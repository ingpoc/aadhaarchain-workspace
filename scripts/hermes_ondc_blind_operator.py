#!/usr/bin/env python3
"""Black-box ONDC Buyer/Seller acceptance through only visible UI and natural asks.

The actor does not seed fixtures or inspect tools/backend state while deciding
what to do. Diagnostic transcript/tool evidence is collected only after each
visible journey is frozen.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hermes_ondc_testing_matrix import call, eval_states, load_handler, shot_paths  # noqa: E402

BUYER = "http://127.0.0.1:43102"
SELLER = "http://127.0.0.1:43103"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
TRANSCRIPTS = ROOT / "aadharchain/gateway/data/samantha-transcripts.jsonl"
TS = time.strftime("%Y%m%d-%H%M%S")

VISIBLE = r"""
(() => {
  const body = document.body.innerText || '';
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  return {
    href: location.href,
    origin: location.origin,
    pathname: location.pathname,
    body: body.slice(0, 6000),
    panel: panel ? panel.innerText.slice(0, 1200) : '',
    reply: reply ? reply.innerText.slice(0, 1200) : '',
    orb_count: document.querySelectorAll('[data-testid="samantha-orb"]').length,
    signed_in: /\bSign out\b/i.test(body),
    sign_in_visible: /\bSign in\b/i.test(body),
  };
})()
"""


def run(handler, session: str, actions: list[dict], timeout: int = 60) -> dict:
    return call(handler, {
        "action": "run", "session_name": session, "use_selected_tab": False,
        "timeout_seconds": timeout, "actions": actions,
    })


def state(result: dict) -> dict:
    values = [item for item in eval_states(result) if "href" in item]
    return values[-1] if values else {}


def freeze(result: dict, label: str) -> tuple[dict, list[str]]:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for index, path in enumerate(shot_paths(result)):
        source = pathlib.Path(path)
        if source.exists():
            target = EVIDENCE / f"BLIND-{label}-{TS}-{index}{source.suffix or '.jpeg'}"
            shutil.copy2(source, target)
            saved.append(str(target))
    return state(result), saved


def visible_probe(handler, session: str, label: str, wait_ms: int = 800) -> tuple[dict, list[str]]:
    result = run(handler, session, [
        {"type": "wait", "ms": wait_ms},
        {"type": "evaluate", "expression": VISIBLE},
        {"type": "screenshot", "format": "jpeg", "quality": 75},
    ])
    return freeze(result, label)


def ensure_signed_out(handler, session: str, url: str, label: str) -> tuple[bool, dict, list[str]]:
    first = run(handler, session, [
        {"type": "goto", "url": url}, {"type": "wait", "ms": 1200},
        {"type": "evaluate", "expression": VISIBLE},
    ])
    current = state(first)
    if current.get("signed_in"):
        run(handler, session, [{
            "type": "locator",
            "locator": {"by": "role", "role": "button", "name": "Sign out", "exact": True},
            "operation": "click",
        }, {"type": "wait", "ms": 1200}], 30)
    current, shots = visible_probe(handler, session, label, 1200)
    clean = not re.search(r"\b(demo|booth)\b", str(current.get("body") or ""), re.I)
    return current.get("orb_count") == 0 and current.get("sign_in_visible") and clean, current, shots


def sign_in_like_operator(handler, session: str, app_origin: str, label: str) -> tuple[bool, dict, list[str]]:
    run(handler, session, [{
        "type": "locator",
        "locator": {"by": "role", "role": "button", "name": "Sign in", "exact": True},
        "operation": "click",
    }, {"type": "wait", "ms": 9000}], 45)
    current, shots = visible_probe(handler, session, label, 1000)
    return current.get("origin") == app_origin and current.get("signed_in") is True, current, shots


def open_samantha(handler, session: str) -> dict:
    run(handler, session, [{
        "type": "locator",
        "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
        "operation": "click",
    }, {"type": "wait", "ms": 8000}], 45)
    return visible_probe(handler, session, "SAMANTHA-READY", 500)[0]


def ask(handler, session: str, message: str, label: str, wait_ms: int = 18000) -> tuple[dict, list[str]]:
    result = run(handler, session, [
        {
            "type": "locator",
            "locator": {"by": "role", "role": "textbox", "name": "Ask Samantha", "exact": True},
            "operation": "fill", "value": message,
        },
        {
            "type": "locator",
            "locator": {"by": "role", "role": "button", "name": "Send", "exact": True},
            "operation": "click",
        },
        {"type": "wait", "ms": wait_ms},
        {"type": "evaluate", "expression": VISIBLE},
        {"type": "screenshot", "format": "jpeg", "quality": 75},
    ], max(60, wait_ms // 1000 + 40))
    return freeze(result, label)


def transcript_diagnostics(role: str, asks: list[str]) -> dict:
    events: list[dict] = []
    if TRANSCRIPTS.exists():
        for line in TRANSCRIPTS.read_text(encoding="utf-8", errors="replace").splitlines()[-1000:]:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("role") == role:
                events.append(event)
    found = {ask: any(event.get("event_type") == "user_text" and event.get("content") == ask for event in events) for ask in asks}
    sessions = {event.get("session_id") for event in events if event.get("content") in asks}
    relevant = [event for event in events if event.get("session_id") in sessions]
    return {
        "all_asks_persisted": all(found.values()),
        "asks": found,
        "event_types": sorted({str(event.get("event_type") or "") for event in relevant}),
        "tool_results": [
            (event.get("metadata") or {}).get("tool") for event in relevant
            if event.get("event_type") == "tool_result"
        ],
        "errors": [event.get("content") for event in relevant if event.get("event_type") == "error"],
    }


def record(rows: list[dict], row_id: str, ok: bool, visible: dict, shots: list[str], evidence: str) -> None:
    rows.append({
        "id": row_id, "result": "Pass" if ok else "Fail", "evidence": evidence,
        "pathname": visible.get("pathname"), "reply": visible.get("reply"), "screenshots": shots,
    })
    print(f"[{'Pass' if ok else 'Fail'}] {row_id}: {evidence}", flush=True)


def buyer_journey(handler, rows: list[dict]) -> list[str]:
    session = "ondc-blind-buyer"
    gate, visible, shots = ensure_signed_out(handler, session, f"{BUYER}/search", "B-AUTH-GATE")
    record(rows, "B-AUTH-GATE", gate, visible, shots, f"orb={visible.get('orb_count')} sign_in={visible.get('sign_in_visible')}")
    signed_in, visible, shots = sign_in_like_operator(handler, session, BUYER, "B-SIGN-IN")
    record(rows, "B-SIGN-IN", signed_in, visible, shots, f"origin={visible.get('origin')} signed_in={visible.get('signed_in')}")
    if not signed_in:
        return []
    ready = open_samantha(handler, session)
    asks = [
        "Hi Samantha, can you help me with my shopping?",
        "Before we start, please empty my cart.",
        "I need atta.",
        "Add one atta to my cart.",
        "Please empty my cart.",
        "Find atta again and add one pack to my cart.",
        "Checkout and pay for my cart.",
    ]
    checks = [
        lambda s: bool(s.get("reply")),
        lambda s: "your cart is empty" in str(s.get("body") or "").lower(),
        lambda s: s.get("pathname") == "/results" and "atta" in str(s.get("body") or "").lower(),
        lambda s: s.get("pathname") == "/cart" and bool(re.search(r"×\s*1\b", str(s.get("body") or ""))) and not re.search(r"×\s*2\b", str(s.get("body") or "")),
        lambda s: "your cart is empty" in str(s.get("body") or "").lower(),
        lambda s: s.get("pathname") == "/cart" and bool(re.search(r"×\s*1\b", str(s.get("body") or ""))),
        lambda s: "/orders/" in str(s.get("pathname") or "") and bool(re.search(r"paid|receipt", str(s.get("body") or ""), re.I)),
    ]
    labels = ["B-HI", "B-CLEAR-BASE", "B-FIND", "B-ADD-ONE", "B-CLEAR", "B-REFILL", "B-CHECKOUT"]
    for prompt, check, label in zip(asks, checks, labels):
        visible, shots = ask(handler, session, prompt, label, 24000 if label in {"B-FIND", "B-REFILL", "B-CHECKOUT"} else 18000)
        clean = not re.search(r"\b(demo|booth)\b", str(visible.get("body") or ""), re.I)
        record(rows, label, bool(check(visible)) and clean, visible, shots, f"path={visible.get('pathname')} clean_copy={clean}")
    return asks


def seller_journey(handler, rows: list[dict]) -> list[str]:
    session = "ondc-blind-seller"
    call(handler, {"action": "preflight", "session_name": session, "url": f"{SELLER}/dashboard", "timeout_seconds": 20})
    gate, visible, shots = ensure_signed_out(handler, session, f"{SELLER}/dashboard", "S-AUTH-GATE")
    record(rows, "S-AUTH-GATE", gate, visible, shots, f"orb={visible.get('orb_count')} sign_in={visible.get('sign_in_visible')}")
    signed_in, visible, shots = sign_in_like_operator(handler, session, SELLER, "S-SIGN-IN")
    record(rows, "S-SIGN-IN", signed_in, visible, shots, f"origin={visible.get('origin')} signed_in={visible.get('signed_in')}")
    if not signed_in:
        return []
    open_samantha(handler, session)
    product = f"Sunrise Whole Wheat Flour {TS[-4:]}"
    asks = [
        "Hi Samantha, what can you help me manage?",
        "Show me the products I am selling.",
        f"Add {product}, one kilogram, at 120 rupees with 10 packs in stock.",
        "Show me my orders.",
    ]
    checks = [
        lambda s: bool(s.get("reply")),
        lambda s: s.get("pathname") == "/catalog" and "catalog" in str(s.get("body") or "").lower(),
        lambda s: s.get("pathname") == "/catalog" and product.lower() in str(s.get("body") or "").lower(),
        lambda s: s.get("pathname") == "/orders" and "orders" in str(s.get("body") or "").lower(),
    ]
    labels = ["S-HI", "S-CATALOG", "S-PUBLISH", "S-ORDERS"]
    for prompt, check, label in zip(asks, checks, labels):
        visible, shots = ask(handler, session, prompt, label, 24000 if label == "S-PUBLISH" else 18000)
        clean = not re.search(r"\b(demo|booth)\b", str(visible.get("body") or ""), re.I)
        record(rows, label, bool(check(visible)) and clean, visible, shots, f"path={visible.get('pathname')} clean_copy={clean}")
    return asks


def main() -> int:
    handler = load_handler()
    pre = call(handler, {"action": "preflight", "session_name": "ondc-blind-buyer", "url": f"{BUYER}/search", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"success": False, "error": "browser bridge not ready", "preflight": pre}, indent=2))
        return 1
    rows: list[dict] = []
    buyer_asks: list[str] = []
    seller_asks: list[str] = []
    try:
        buyer_asks = buyer_journey(handler, rows)
        seller_asks = seller_journey(handler, rows)
    finally:
        try:
            call(handler, {"action": "closeout", "timeout_seconds": 20})
        except Exception:
            pass
    diagnostics = {
        "buyer": transcript_diagnostics("buyer", buyer_asks),
        "seller": transcript_diagnostics("seller", seller_asks),
    }
    diagnostics_ok = all(
        not asks or (
            diagnostics[role]["all_asks_persisted"]
            and "assistant_text" in diagnostics[role]["event_types"]
            and "tool_call" in diagnostics[role]["event_types"]
            and "tool_result" in diagnostics[role]["event_types"]
            and not diagnostics[role]["errors"]
        )
        for role, asks in (("buyer", buyer_asks), ("seller", seller_asks))
    )
    failed = [row for row in rows if row["result"] != "Pass"]
    output = {
        "success": not failed and diagnostics_ok,
        "mode": "blinded-visible-operator-first",
        "rows": rows,
        "diagnostics_after_visible_journey": diagnostics,
        "diagnostics_ok": diagnostics_ok,
        "ts": TS,
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / f"blind-operator-{TS}.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"Wrote {path}")
    return 0 if output["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
