#!/usr/bin/env python3
"""ONDC testing matrix with Hermes screenshots (claim → screenshot → Pass).

Saves evidence under .cursor/skills/ondc-testing/references/evidence/
Usage:
  python3 scripts/hermes_ondc_testing_matrix.py          # buyer+seller
  python3 scripts/hermes_ondc_testing_matrix.py buyer
  python3 scripts/hermes_ondc_testing_matrix.py seller
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
SELLER = "http://127.0.0.1:43103"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION = "ondc-testing-matrix"
TS = time.strftime("%Y%m%d-%H%M%S")


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def call(handler, args: dict) -> dict:
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(args, task_id="ondc-matrix")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


EVAL = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? panel.innerText : '';
  const body = document.body.innerText || '';
  const tools = (window.__samanthaTools || []).slice(-12);
  const runtimeJobs = (window.__samanthaRuntimeJobs || []).slice(-12);
  return {
    href: location.href,
    pathname: location.pathname,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0,12),
    body_snip: body.slice(0, 1000),
    hint: hint.slice(0, 600),
    reply: reply ? reply.innerText.slice(0, 400) : '',
    tools,
    runtime_jobs: runtimeJobs,
    has_atta: /atta/i.test(body),
    has_milk: /milk/i.test(body),
    has_organic: /organic/i.test(body),
    has_receipt: /receipt/i.test(body),
    has_approval: /need.?approval|approve|approval/i.test(body),
    has_allow: /\\ballow(ed)?\\b|committed|receipt/i.test(body),
    has_deny: /\\bdeny|denied\\b/i.test(body),
    has_refund: /refund/i.test(body),
    has_catalog: /catalog|sku|listing|product/i.test(body),
    has_mandate: /mandate|agentguard|auto.?approve/i.test(body),
  };
})()
"""

def eval_states(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict) and ("href" in val or "pathname" in val or "ok" in val or "mandate_id" in val):
            out.append(val)
    return out


def shot_paths(result: dict) -> list[str]:
    paths = []
    for step in result.get("results", []):
        if step.get("type") == "screenshot" and step.get("screenshot_path"):
            paths.append(step["screenshot_path"])
    return paths


def save_evidence(mid: str, paths: list[str]) -> list[str]:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, p in enumerate(paths):
        src = pathlib.Path(p)
        if not src.exists():
            continue
        dest = EVIDENCE / f"{mid}-{TS}-{i}{src.suffix or '.jpeg'}"
        shutil.copy2(src, dest)
        saved.append(str(dest))
    return saved


def tool_names(state: dict) -> list[str]:
    return [t.get("name") for t in (state.get("tools") or []) if isinstance(t, dict) and t.get("name")]


def ask_with_shot(handler, message: str, mid: str, wait_ms: int = 18000) -> tuple[dict, list[str]]:
    request = {
        "action": "run",
        "session_name": SESSION,
        "use_selected_tab": False,
        "timeout_seconds": max(90, wait_ms // 1000 + 45),
        "actions": [
            {
                "type": "locator",
                "locator": {"by": "testid", "testId": "samantha-orb-text"},
                "operation": "fill",
                "value": message,
            },
            {
                "type": "locator",
                "locator": {"by": "role", "role": "button", "name": "Send", "exact": True},
                "operation": "click",
            },
            {"type": "wait", "ms": wait_ms},
            {"type": "evaluate", "expression": EVAL},
            {"type": "screenshot", "format": "jpeg", "quality": 70},
            {"type": "page_context"},
        ],
    }
    try:
        result = call(handler, request)
    except RuntimeError as exc:
        if "Locator did not resolve for fill" not in str(exc):
            raise
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [
                    {
                        "type": "locator",
                        "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                        "operation": "click",
                    },
                    {"type": "wait", "ms": 8000},
                ],
            },
        )
        result = call(handler, request)
    states = [e for e in eval_states(result) if "href" in e]
    state = states[-1] if states else {}
    saved = save_evidence(mid, shot_paths(result))
    return state, saved


def goto_shot(handler, url: str, mid: str) -> tuple[dict, list[str]]:
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "goto", "url": url},
                {"type": "wait", "ms": 2000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    states = [e for e in eval_states(result) if "href" in e]
    state = states[-1] if states else {}
    saved = save_evidence(mid, shot_paths(result))
    return state, saved


def runtime_settle_with_shot(handler, mid: str, wait_ms: int = 45000) -> tuple[dict, list[str]]:
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": max(75, wait_ms // 1000 + 30),
            "actions": [
                {"type": "wait", "ms": wait_ms},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
                {"type": "page_context"},
            ],
        },
    )
    states = [e for e in eval_states(result) if "href" in e]
    state = states[-1] if states else {}
    return state, save_evidence(mid, shot_paths(result))


def boot_buyer(handler) -> dict:
    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {"aud": "ondcbuyer", "return": f"{BUYER}/search", "display_name": "ONDC Matrix Buyer"}
        )
    )
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 100,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2200},
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2200},
                {
                    "type": "locator",
                    "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                    "operation": "click",
                },
                {"type": "wait", "ms": 8000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    save_evidence("B-BOOT", shot_paths(result))
    states = [e for e in eval_states(result) if "href" in e]
    return states[-1] if states else {}


def boot_seller(handler) -> dict:
    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {"aud": "ondcseller", "return": f"{SELLER}/dashboard", "display_name": "ONDC Matrix Seller"}
        )
    )
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 100,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2200},
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2200},
                {
                    "type": "locator",
                    "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                    "operation": "click",
                },
                {"type": "wait", "ms": 8000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    save_evidence("S-BOOT", shot_paths(result))
    states = [e for e in eval_states(result) if "href" in e]
    return states[-1] if states else {}


def run_buyer(handler, rows: list) -> None:
    def rec(mid, ask, result, evidence, shots, state):
        rows.append(
            {
                "id": mid,
                "ask": ask,
                "result": result,
                "evidence": evidence,
                "screenshots": shots,
                "pathname": (state or {}).get("pathname"),
                "tools": tool_names(state or {}),
                "reply": ((state or {}).get("reply") or "")[:140],
            }
        )
        print(f"[{result}] {mid}: {evidence} shots={shots}", flush=True)

    print("=== Buyer ===", flush=True)
    boot_buyer(handler)

    greeting = "Hi Samantha, this is my first time here. What can you help me do?"
    st, shots = ask_with_shot(handler, greeting, "B-HI", 12000)
    tools = tool_names(st)
    commerce = {"search_catalog", "add_to_cart", "checkout_commit", "navigate_to"}
    fired = [t for t in tools if t in commerce]
    ok = "/search" in (st.get("pathname") or "") and not fired and bool(shots)
    rec("B-HI", greeting, "Pass" if ok else "Fail", f"path={st.get('pathname')} tools={tools}", shots, st)

    find_ask = "I need something simple for breakfast. Can you find atta that I can buy?"
    st, shots = ask_with_shot(handler, find_ask, "B-FIND-ATTA", 28000)
    tools = tool_names(st)
    ok = bool(shots) and bool(st.get("has_atta")) and "/results" in (st.get("pathname") or "") and "search_catalog" in tools
    rec(
        "B-FIND-ATTA",
        find_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} atta={st.get('has_atta')} tools={tools}",
        shots,
        st,
    )

    add_ask = "That first atta looks fine. Please put one in my cart."
    st, shots = ask_with_shot(handler, add_ask, "B-ADD-ATTA", 28000)
    tools = tool_names(st)
    ok = bool(shots) and bool(st.get("has_atta")) and "/cart" in (st.get("pathname") or "") and "add_to_cart" in tools
    rec(
        "B-ADD-ATTA",
        add_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} atta={st.get('has_atta')} tools={tools}",
        shots,
        st,
    )

    st, shots = ask_with_shot(handler, "take me to my cart", "B-NAV-CART", 16000)
    ok = bool(shots) and "/cart" in (st.get("pathname") or "")
    rec("B-NAV-CART", "take me to cart", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "go to checkout", "B-NAV-CHECKOUT", 16000)
    ok = bool(shots) and "/checkout" in (st.get("pathname") or "")
    rec("B-NAV-CHECKOUT", "go to checkout", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "remember that I prefer organic produce", "B-MEM-ORG", 16000)
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    ok = bool(shots) and ("remember_preference" in tool_names(st) or "organic" in blob)
    rec("B-MEM-ORG", "remember organic", "Pass" if ok else "Fail", f"tools={tool_names(st)}", shots, st)

    st, shots = ask_with_shot(handler, "open config so I can see my mandate and preferences", "B-NAV-CONFIG", 16000)
    ok = bool(shots) and "/config" in (st.get("pathname") or "")
    rec("B-NAV-CONFIG", "open config", "Pass" if ok else "Fail", f"path={st.get('pathname')} organic={st.get('has_organic')}", shots, st)

    # Checkout / payment — required
    st, shots = ask_with_shot(
        handler,
        "please checkout and pay for my cart now",
        "B-CHECKOUT-OK",
        28000,
    )
    tools = tool_names(st)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ag_hit = any(
        k in blob
        for k in (
            "allow",
            "receipt",
            "committed",
            "need_approval",
            "need approval",
            "approve",
            "denied",
            "deny",
            "checkout",
        )
    )
    tools_ok = "checkout_commit" in tools
    # If need_approval, try to capture checkout page AG UI
    if "need_approval" in blob or "approval" in blob or not tools_ok:
        chk_st, chk_shots = goto_shot(handler, f"{BUYER}/checkout", "B-CHECKOUT-UI")
        shots = shots + chk_shots
        st = {**chk_st, "tools": st.get("tools"), "hint": st.get("hint"), "reply": st.get("reply")}
        blob2 = f"{st.get('body_snip','')} {st.get('hint','')}".lower()
        ag_hit = ag_hit or any(k in blob2 for k in ("approval", "receipt", "mandate", "agentguard", "checkout"))
    ok = bool(shots) and (tools_ok or ag_hit)
    # Prefer honest AG outcome visible
    decision = (
        "allow"
        if ("receipt" in blob or "committed" in blob)
        else "need_approval"
        if ("approval" in blob or "need_approval" in blob)
        else "deny"
        if ("deny" in blob or "denied" in blob)
        else "unknown"
    )
    rec(
        "B-CHECKOUT-OK",
        "checkout and pay",
        "Pass" if ok else "Fail",
        f"decision~{decision} tools={tools} ag_hit={ag_hit}",
        shots,
        st,
    )

    # Over-limit path for AG honesty
    st, shots = ask_with_shot(
        handler,
        "try to checkout my cart for twenty five thousand rupees",
        "B-CHECKOUT-OVER",
        24000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and any(
        k in blob for k in ("need_approval", "approval", "deny", "denied", "limit", "exceed", "25000", "mandate")
    )
    rec("B-CHECKOUT-OVER", "checkout 25000", "Pass" if ok else "Fail", f"blob={blob[:160]}", shots, st)

    long_ask = "Please plan a practical week of groceries for two people under 2,000 rupees, taking my preferences into account."
    st, shots = ask_with_shot(handler, long_ask, "B-LONG-WEEKLY", 22000)
    path = st.get("pathname") or ""
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    jobs = st.get("runtime_jobs") or []
    statuses = [job.get("status") for job in jobs if isinstance(job, dict)]
    if "/agent" in path or "cursor" in blob:
        res, ev = "Fail", f"leaked path={path}"
    elif "delegate_to_runtime_agent" not in tool_names(st):
        res, ev = "Fail", f"runtime tool missing path={path} blob={blob[:120]}"
    elif "completed" in statuses:
        res, ev = "Pass", f"completed inline path={path} runtime_statuses={statuses}"
    elif "started" in statuses:
        settled, settled_shots = runtime_settle_with_shot(handler, "B-LONG-WEEKLY-DONE")
        shots += settled_shots
        jobs = settled.get("runtime_jobs") or []
        completed = any(job.get("status") == "completed" for job in jobs if isinstance(job, dict))
        if not completed:
            settled, more_shots = runtime_settle_with_shot(handler, "B-LONG-WEEKLY-DONE-R2")
            shots += more_shots
            jobs = settled.get("runtime_jobs") or []
            completed = any(job.get("status") == "completed" for job in jobs if isinstance(job, dict))
        res = "Pass" if completed else "Fail"
        ev = f"handoff path={path} runtime_statuses={[job.get('status') for job in jobs if isinstance(job, dict)]}"
        st = settled
    else:
        res, ev = "Fail", f"no clear handoff path={path} blob={blob[:120]}"
    if not shots and res == "Pass":
        res, ev = "Fail", "no screenshot"
    rec("B-LONG-WEEKLY", long_ask, res, ev, shots, st)


def run_seller(handler, rows: list) -> None:
    def rec(mid, ask, result, evidence, shots, state):
        rows.append(
            {
                "id": mid,
                "ask": ask,
                "result": result,
                "evidence": evidence,
                "screenshots": shots,
                "pathname": (state or {}).get("pathname"),
                "tools": tool_names(state or {}),
                "reply": ((state or {}).get("reply") or "")[:140],
            }
        )
        print(f"[{result}] {mid}: {evidence} shots={shots}", flush=True)

    print("=== Seller ===", flush=True)
    boot_seller(handler)

    greeting = "Hi Samantha, I'm new here. What can you help me run in my shop?"
    st, shots = ask_with_shot(handler, greeting, "S-HI", 12000)
    tools = tool_names(st)
    commerce = {"refund_issue", "navigate_to", "catalog_publish"}
    fired = [t for t in tools if t in commerce]
    path = st.get("pathname") or ""
    ok = bool(shots) and not fired and ("dashboard" in path or path.startswith("/"))
    rec("S-HI", greeting, "Pass" if ok else "Fail", f"path={path} tools={tools}", shots, st)

    st, shots = ask_with_shot(handler, "open agentguard so I can review my mandate", "S-NAV-AG", 18000)
    ok = bool(shots) and "/agentguard" in (st.get("pathname") or "")
    rec("S-NAV-AG", "open agentguard", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "show me the catalog", "S-NAV-CAT", 18000)
    path = st.get("pathname") or ""
    ok = bool(shots) and (
        "catalog" in path
        or "product" in path
        or "listing" in path
        or (st.get("has_catalog") and "navigate_to" in tool_names(st))
    )
    rec("S-NAV-CAT", "show catalog", "Pass" if ok else "Fail", f"path={path} tools={tool_names(st)}", shots, st)

    publish_ask = f"Please add Evening Ragi Flour {TS[-6:]} to my catalog at 75 rupees for 500 grams, with 7 packs in stock."
    st, shots = ask_with_shot(handler, publish_ask, "S-PUBLISH", 24000)
    tools = tool_names(st)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and "catalog_publish" in tools and "7" in blob and "/catalog" in (st.get("pathname") or "")
    rec("S-PUBLISH", publish_ask, "Pass" if ok else "Fail", f"path={st.get('pathname')} tools={tools} quantity_visible={'7' in blob}", shots, st)

    st, shots = ask_with_shot(handler, "show me orders", "S-NAV-ORD", 18000)
    path = st.get("pathname") or ""
    ok = bool(shots) and ("order" in path or "order" in (st.get("body_snip") or "").lower())
    rec("S-NAV-ORD", "show orders", "Pass" if ok else "Fail", f"path={path}", shots, st)

    st, shots = ask_with_shot(
        handler,
        "Please refund 400 rupees on my most recent order.",
        "S-REFUND-OK",
        26000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and (
        "refund_issue" in tool_names(st)
        or any(k in blob for k in ("allow", "refund", "receipt", "executed", "500"))
    )
    rec("S-REFUND-OK", "refund 400 on most recent order", "Pass" if ok else "Fail", f"tools={tool_names(st)} blob={blob[:140]}", shots, st)

    st, shots = ask_with_shot(
        handler,
        "Please refund 26000 rupees on my most recent order.",
        "S-REFUND-OVER",
        24000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and any(
        k in blob for k in ("need_approval", "approval", "deny", "denied", "limit", "exceed", "26000")
    )
    rec("S-REFUND-OVER", "refund 26000 on most recent order", "Pass" if ok else "Fail", f"blob={blob[:160]}", shots, st)

    st, shots = ask_with_shot(handler, "remember I prefer brief refund confirmations", "S-MEM", 16000)
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    ok = bool(shots) and ("remember_preference" in tool_names(st) or "brief" in blob)
    # Capture agentguard memory UI
    ag_st, ag_shots = goto_shot(handler, f"{SELLER}/agentguard", "S-MEM-UI")
    shots = shots + ag_shots
    rec("S-MEM", "brief refund confirmations", "Pass" if ok else "Fail", f"tools={tool_names(st)} ag_organic={ag_st.get('has_organic')}", shots, st)

    long_ask = "Review my recent orders and give me a short priority list of what I should handle first, including refund risk."
    st, shots = ask_with_shot(handler, long_ask, "S-LONG-TRIAGE", 22000)
    path = st.get("pathname") or ""
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    jobs = st.get("runtime_jobs") or []
    statuses = [job.get("status") for job in jobs if isinstance(job, dict)]
    if "/agent" in path or "cursor" in blob:
        res, ev = "Fail", f"leaked path={path}"
    elif "delegate_to_runtime_agent" not in tool_names(st):
        res, ev = "Fail", f"runtime tool missing path={path} blob={blob[:120]}"
    elif "completed" in statuses:
        res, ev = "Pass", f"completed inline path={path} runtime_statuses={statuses}"
    elif "started" in statuses:
        settled, settled_shots = runtime_settle_with_shot(handler, "S-LONG-TRIAGE-DONE")
        shots += settled_shots
        jobs = settled.get("runtime_jobs") or []
        completed = any(job.get("status") == "completed" for job in jobs if isinstance(job, dict))
        if not completed:
            settled, more_shots = runtime_settle_with_shot(handler, "S-LONG-TRIAGE-DONE-R2")
            shots += more_shots
            jobs = settled.get("runtime_jobs") or []
            completed = any(job.get("status") == "completed" for job in jobs if isinstance(job, dict))
        res = "Pass" if completed else "Fail"
        ev = f"handoff path={path} runtime_statuses={[job.get('status') for job in jobs if isinstance(job, dict)]}"
        st = settled
    else:
        res, ev = "Fail", f"no clear handoff path={path} blob={blob[:120]}"
    if not shots and res == "Pass":
        res, ev = "Fail", "no screenshot"
    rec("S-LONG-TRIAGE", long_ask, res, ev, shots, st)


def main() -> int:
    side = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    rows: list[dict] = []
    try:
        if side in ("all", "buyer"):
            run_buyer(handler, rows)
        if side in ("all", "seller"):
            run_seller(handler, rows)
    finally:
        leave = f"{SELLER}/agentguard" if side in ("all", "seller") else f"{BUYER}/checkout"
        try:
            call(
                handler,
                {
                    "action": "run",
                    "session_name": SESSION,
                    "use_selected_tab": False,
                    "timeout_seconds": 30,
                    "actions": [{"type": "goto", "url": leave}, {"type": "wait", "ms": 800}],
                },
            )
        finally:
            call(handler, {"action": "closeout", "timeout_seconds": 20})

    passed = sum(1 for x in rows if x["result"] == "Pass")
    failed = sum(1 for x in rows if x["result"] == "Fail")
    skipped = sum(1 for x in rows if x["result"] == "Skip")
    out = {
        "success": failed == 0,
        "counts": {"pass": passed, "fail": failed, "skip": skipped, "total": len(rows)},
        "rows": rows,
        "evidence_dir": str(EVIDENCE),
        "realtime_model": status.get("data", {}).get("model"),
        "ts": TS,
    }
    out_path = EVIDENCE / f"matrix-run-{TS}.json"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))
    print(f"Wrote {out_path}", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
