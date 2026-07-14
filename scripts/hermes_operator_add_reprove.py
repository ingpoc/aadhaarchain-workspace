#!/usr/bin/env python3
"""Re-prove W-B-FIND-ATTA → W-B-ADD-ATTA after cache-resolve fix. Hermes WIP."""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
# reuse helpers by importing the usp module pieces inline
from hermes_operator_usp_settle import (  # type: ignore
    BUYER,
    CLICK_ORB,
    EVIDENCE,
    GATEWAY,
    SETTLE,
    ask_one,
    call,
    evals,
    goto_and_orb,
    load_handler,
    latest_tool,
    record,
    shot_paths,
    tool_names,
    wait_orb_ready,
    wake_gateway,
    LEDGER,
)

SESSION = "web-usp-add-reprove"
TS = time.strftime("%Y%m%d-%H%M%S")
# rebind stamp in shared ledger
LEDGER["stamp"] = TS
LEDGER["buyer"] = []
LEDGER["seller"] = []
LEDGER["voice"] = []
LEDGER["not_covered"] = []
LEDGER["meta"] = {"purpose": "add-reprove-after-cache-fix"}


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    wake_gateway()
    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 25})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    boot = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 3000},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 4000},
                {"type": "evaluate", "expression": SETTLE},
                {"type": "screenshot"},
            ],
        },
    )
    boot_st = ([s for s in evals(boot) if "pathname" in s] or [{}])[-1]
    ready = wait_orb_ready(handler, SESSION)
    signed = bool(boot_st.get("has_sign_out"))
    record(
        "buyer",
        "W-B-SPA-SESSION",
        "Pass" if signed else "Blocked",
        shot_paths(boot, "W-B-ADD-REPROVE-BOOT"),
        f"sign_out={signed} ready={ready.get('ready')} asset_hint=index-g-MK17OV",
        boot_st,
    )
    if not signed:
        out = EVIDENCE / f"usp-add-reprove-{TS}.json"
        out.write_text(json.dumps(LEDGER, indent=2))
        print(json.dumps({"ledger": str(out)}, indent=2))
        return 1

    find, find_shots, find_send = ask_one(
        handler,
        SESSION,
        "search for atta",
        "W-B-FIND-ATTA-REPROVE",
        expect_path="/results",
        require_tool="search_catalog",
        early_poll_results=True,
        settle_rounds=22,
    )
    find_ok = (
        bool(find_send.get("ok"))
        and find.get("pathname") == "/results"
        and "search_catalog" in tool_names(find)
        and (find.get("offerCount", 0) > 0 or find.get("has_atta"))
    )
    record(
        "buyer",
        "W-B-FIND-ATTA",
        "Pass" if find_ok else "Fail",
        find_shots,
        f"path={find.get('pathname')} offers={find.get('offerCount')} atta={find.get('has_atta')} tools={tool_names(find)[-4:]}",
        find,
    )
    if not find_ok:
        out = EVIDENCE / f"usp-add-reprove-{TS}.json"
        out.write_text(json.dumps(LEDGER, indent=2, default=str))
        print(json.dumps({"ledger": str(out), "stopped": "find_failed"}, indent=2))
        return 1

    time.sleep(3)  # let ResultsPage finish remembering cache
    # force a settle snapshot so cache has time
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [{"type": "wait", "ms": 5000}, {"type": "evaluate", "expression": SETTLE}],
        },
    )

    add, add_shots, add_send = ask_one(
        handler,
        SESSION,
        "add the atta to my cart",
        "W-B-ADD-ATTA-REPROVE",
        expect_path="/cart",
        require_tool="add_to_cart",
        settle_rounds=16,
    )
    add_tool = latest_tool(add, "add_to_cart")
    add_ok = (
        bool(add_send.get("ok"))
        and add.get("pathname") == "/cart"
        and not add.get("cart_empty")
        and (add.get("cart_line") or (add_tool and add_tool.get("ok") and add_tool.get("cartAdds")))
    )
    # Partial if add_to_cart fired ok even if path race
    if add_ok:
        add_result = "Pass"
    elif "add_to_cart" in tool_names(add) and add_tool and add_tool.get("ok"):
        add_result = "Partial"
    else:
        add_result = "Fail"
    record(
        "buyer",
        "W-B-ADD-ATTA",
        add_result,
        add_shots,
        f"path={add.get('pathname')} empty={add.get('cart_empty')} line={add.get('cart_line')} tool={add_tool} tools={tool_names(add)[-6:]} hint={(add.get('hint') or '')[:160]}",
        add,
    )

    # slim state
    slim = json.loads(json.dumps(LEDGER, default=str))
    for row in slim["buyer"]:
        st = row.get("state") or {}
        row["state"] = {
            k: st.get(k)
            for k in (
                "pathname",
                "search",
                "hint",
                "reply",
                "tools",
                "offerCount",
                "cart_empty",
                "cart_line",
                "_send",
                "_early",
            )
            if k in st
        }
    out = EVIDENCE / f"usp-add-reprove-{TS}.json"
    out.write_text(json.dumps(slim, indent=2))
    print(json.dumps({"ledger": str(out), "rows": [{k: r[k] for k in ('id','result','notes')} for r in slim['buyer']]}, indent=2))

    # leave on search
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 45,
            "actions": [{"type": "goto", "url": f"{BUYER}/search"}, {"type": "wait", "ms": 1000}],
        },
    )
    return 0 if add_result == "Pass" else 1


if __name__ == "__main__":
    # patch record to use new TS prefixes — already via ask_one prefixes
    raise SystemExit(main())
