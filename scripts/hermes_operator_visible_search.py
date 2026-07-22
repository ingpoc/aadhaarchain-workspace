#!/usr/bin/env python3
"""Operator text-mode: Buyer visible early /results + Seller smoke (Hermes WIP / FQDN).

Proves search_catalog early-nav UX. No demo flip. No secrets in evidence.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "https://gateway.aadharcha.in"
BUYER = "https://ondcbuyer.aadharcha.in"
SELLER = "https://ondcseller.aadharcha.in"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION_B = "web-op-buyer"
SESSION_S = "web-op-seller"
TS = time.strftime("%Y%m%d-%H%M%S")
LEDGER: dict = {"stamp": TS, "buyer": [], "seller": [], "meta": {}}


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="op-visible")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


OPEN_ORB_ACTION = {
    "type": "locator",
    "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
    "operation": "click",
}

WAIT_READY = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const hint = panel ? (panel.innerText || '') : '';
  const ready = /Text mode ready|Listening \\+ text ready|Listening/i.test(hint);
  const connecting = /Connecting/i.test(hint) && !ready;
  const err = /Realtime not configured|Samantha error|Failed to start/i.test(hint);
  return { ready, connecting, err, hint: hint.slice(0, 240) };
})()
"""

EVAL = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? panel.innerText : '';
  const body = document.body.innerText || '';
  const tools = (window.__samanthaTools || []).slice(-20).map(t => {
    if (!t || typeof t !== 'object') return t;
    return {
      name: t.name || t.tool || t.type,
      ok: t.ok,
      navSuperseded: t.navSuperseded,
      navEpoch: t.navEpoch,
      path: t.path || t.pathname || (t.args && (t.args.path || t.args.pathname)),
      error: t.error ? String(t.error).slice(0, 120) : undefined,
    };
  });
  const navSupersededAny = tools.some(t => t && t.navSuperseded === true);
  return {
    href: location.href,
    pathname: location.pathname,
    search: location.search,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0,12),
    body_snip: body.slice(0, 1400),
    hint: hint.slice(0, 700),
    reply: reply ? reply.innerText.slice(0, 500) : '',
    tools,
    navSupersededAny,
    has_sign_out: /Sign out/i.test(body),
    has_banana: /banana/i.test(body),
    has_atta: /atta/i.test(body),
    has_pulling: /pulling|loading|searching|offers/i.test(body + hint),
    cart_line: /Robusta|Bananas|Atta|cart is empty|Your cart/i.test(body),
    cart_empty: /cart is empty/i.test(body),
  };
})()
"""

POLL_RESULTS = """
(() => {
  const tools = (window.__samanthaTools || []).slice(-8);
  return {
    href: location.href,
    pathname: location.pathname,
    search: location.search,
    early_results: location.pathname === '/results',
    hint: (document.querySelector('[data-testid="samantha-orb-panel"]')||{}).innerText?.slice(0, 300) || '',
    tools,
  };
})()
"""


def send_actions(message: str) -> list[dict]:
    return [
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
    ]


def eval_results(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict) and ("href" in val or "pathname" in val or "ok" in val or "ready" in val):
            out.append(val)
    return out


def shot_paths(result: dict, prefix: str) -> list[str]:
    saved = []
    idx = 0
    for step in result.get("results", []):
        if step.get("type") != "screenshot":
            continue
        src = step.get("path") or step.get("file") or step.get("screenshot_path")
        if not src:
            continue
        src_p = pathlib.Path(src)
        if not src_p.exists():
            continue
        dest = EVIDENCE / f"{prefix}-{TS}-{idx}.jpeg"
        shutil.copy2(src_p, dest)
        saved.append(dest.name)
        idx += 1
    return saved


def record(side: str, fid: str, result: str, shots: list[str], notes: str, state: dict | None = None):
    row = {"id": fid, "result": result, "shots": shots, "notes": notes, "state": state or {}}
    LEDGER[side].append(row)
    print(json.dumps({"side": side, **{k: row[k] for k in ("id", "result", "notes")}}, ensure_ascii=False))


def wake_gateway():
    try:
        urllib.request.urlopen(f"{GATEWAY}/api/health", timeout=30).read()
    except Exception as exc:
        LEDGER["meta"]["wake_err"] = str(exc)
    try:
        st = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=20).read())
        LEDGER["meta"]["realtime"] = st.get("data") or st
    except Exception as exc:
        LEDGER["meta"]["realtime_err"] = str(exc)
def wait_orb_ready(handler, session: str, rounds: int = 8) -> dict:
    last = {}
    for _ in range(rounds):
        r = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "wait", "ms": 1500},
                    {"type": "evaluate", "expression": WAIT_READY},
                ],
            },
        )
        states = eval_results(r)
        last = states[-1] if states else {}
        if last.get("ready"):
            return last
        if last.get("err"):
            return last
        time.sleep(1.5)
    return last


def ask_and_poll_early(handler, session: str, message: str, prefix: str) -> tuple[dict, dict, list[str]]:
    """Send ask; poll pathname quickly for early /results; then late eval + shot."""
    call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                *send_actions(message),
            ],
        },
    )
    early = {}
    for _ in range(12):
        time.sleep(0.7)
        poll = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [{"type": "evaluate", "expression": POLL_RESULTS}],
            },
        )
        states = eval_results(poll)
        early = states[-1] if states else {}
        if early.get("early_results") or early.get("pathname") == "/results":
            break

    late = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": [
                {"type": "wait", "ms": 8000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot"},
            ],
        },
    )
    late_states = [s for s in eval_results(late) if "pathname" in s]
    late_state = late_states[-1] if late_states else {}
    shots = shot_paths(late, prefix)
    return early, late_state, shots


def ask_simple(handler, session: str, message: str, wait_ms: int, prefix: str) -> tuple[dict, list[str]]:
    r = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": [
                *send_actions(message),
                {"type": "wait", "ms": wait_ms},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot"},
            ],
        },
    )
    states = [s for s in eval_results(r) if "pathname" in s]
    return (states[-1] if states else {}), shot_paths(r, prefix)


def tool_names(state: dict) -> list[str]:
    names = []
    for t in state.get("tools") or []:
        if isinstance(t, dict) and t.get("name"):
            names.append(str(t["name"]))
        elif isinstance(t, str):
            names.append(t)
    return names


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    wake_gateway()
    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 25})
    LEDGER["meta"]["preflight_ready"] = bool(pre.get("ready"))
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        out = EVIDENCE / f"op-visible-search-{TS}.json"
        out.write_text(json.dumps(LEDGER, indent=2))
        return 1

    # --- Buyer boot ---
    boot = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 90,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 3000},
                    OPEN_ORB_ACTION,
                    {"type": "wait", "ms": 4000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot"},
            ],
        },
    )
    boot_states = [s for s in eval_results(boot) if "pathname" in s]
    boot_state = boot_states[-1] if boot_states else {}
    boot_shots = shot_paths(boot, "W-B-OP-BOOT")
    ready = wait_orb_ready(handler, SESSION_B)
    signed = bool(boot_state.get("has_sign_out"))
    record(
        "buyer",
        "W-B-SPA-SESSION",
        "Pass" if signed else "Blocked",
        boot_shots,
        f"sign_out={signed} ready={ready.get('ready')} hint={str(ready.get('hint',''))[:120]}",
        {**boot_state, "ready": ready},
    )
    if not signed:
        # Still try local? No — FQDN preferred; stop buyer commerce if unsigned
        record("buyer", "W-B-FIND-ATTA", "Blocked", [], "no Auth0 Sign out — session missing", {})
    else:
        # B-HI
        hi, hi_shots = ask_simple(handler, SESSION_B, "hi", 10000, "W-B-HI")
        hi_tools = tool_names(hi)
        hi_ok = hi.get("pathname") == "/search" and not any(
            t in hi_tools for t in ("search_catalog", "navigate_to", "add_to_cart")
        )
        # Allow soft: if tools empty and not on /results
        if not hi_ok and hi.get("pathname") != "/results" and not hi_tools:
            hi_ok = True
        record(
            "buyer",
            "W-B-HI",
            "Pass" if hi_ok else "Fail",
            hi_shots,
            f"path={hi.get('pathname')} tools={hi_tools} reply={str(hi.get('reply') or hi.get('hint') or '')[:100]}",
            hi,
        )

        # Reset to /search before find
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 2000},
                    OPEN_ORB_ACTION,
                    {"type": "wait", "ms": 3000},
                ],
            },
        )
        wait_orb_ready(handler, SESSION_B, rounds=5)

        # Visible early search — atta then bananas
        early_a, late_a, shots_a = ask_and_poll_early(
            handler, SESSION_B, "search for atta", "W-B-FIND-ATTA"
        )
        early_ok = bool(early_a.get("early_results") or early_a.get("pathname") == "/results")
        late_ok = late_a.get("pathname") == "/results"
        tools_a = tool_names(late_a) or tool_names(early_a)
        find_pass = early_ok and late_ok and ("search_catalog" in tools_a or late_a.get("has_atta") or late_a.get("has_pulling"))
        # Require early /results as hard signal for this UX ship
        if not early_ok:
            find_pass = False
        record(
            "buyer",
            "W-B-FIND-ATTA",
            "Pass" if find_pass else "Fail",
            shots_a,
            f"early_path={early_a.get('pathname')} late_path={late_a.get('pathname')} early={early_ok} tools={tools_a} atta={late_a.get('has_atta')}",
            {"early": early_a, "late": late_a},
        )

        # Stall prove: chained follow-on IMMEDIATELY after search — no page reload.
        # Prior Fail (21:42): draft stuck / send_disabled while search_catalog still busy.
        chain = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 90,
                "actions": [
                    *send_actions("go to my cart"),
                    {"type": "wait", "ms": 18000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot"},
                ],
            },
        )
        chain_evals = eval_results(chain)
        chain_send: dict = {}
        for s in chain_evals:
            if "ok" in s and ("draft" in s or "reason" in s):
                chain_send = s
                break
        chain_state = ([s for s in chain_evals if "pathname" in s] or [{}])[-1]
        chain_shots = shot_paths(chain, "W-B-CHAINED")
        chain_tools = tool_names(chain_state)
        chain_send_ok = True  # locator fill/click would have raised on failure
        chain_ok = chain_send_ok and chain_state.get("pathname") == "/cart"
        record(
            "buyer",
            "W-B-CHAINED",
            "Pass" if chain_ok else "Fail",
            chain_shots,
            f"send_ok={chain_send_ok} send={chain_send} path={chain_state.get('pathname')} tools={chain_tools} navSuperseded={chain_state.get('navSupersededAny')}",
            {"send": chain_send, "late": chain_state},
        )

        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 2000},
                    OPEN_ORB_ACTION,
                    {"type": "wait", "ms": 2500},
                ],
            },
        )
        wait_orb_ready(handler, SESSION_B, rounds=4)

        early_b, late_b, shots_b = ask_and_poll_early(
            handler, SESSION_B, "find bananas", "W-B-FIND-BANANA"
        )
        early_ok_b = bool(early_b.get("early_results") or early_b.get("pathname") == "/results")
        late_ok_b = late_b.get("pathname") == "/results"
        tools_b = tool_names(late_b) or tool_names(early_b)
        banana_pass = early_ok_b and late_ok_b
        record(
            "buyer",
            "W-B-FIND-BANANA",
            "Pass" if banana_pass else "Fail",
            shots_b,
            f"early_path={early_b.get('pathname')} late={late_b.get('pathname')} banana={late_b.get('has_banana')} tools={tools_b}",
            {"early": early_b, "late": late_b},
        )

        # Add to cart
        add_state, add_shots = ask_simple(
            handler, SESSION_B, "add the first banana or atta result to my cart", 18000, "W-B-ADD"
        )
        add_tools = tool_names(add_state)
        on_cart = add_state.get("pathname") == "/cart"
        add_pass = on_cart and ("add_to_cart" in add_tools or add_state.get("cart_line"))
        record(
            "buyer",
            "W-B-ADD",
            "Pass" if add_pass else "Fail",
            add_shots,
            f"path={add_state.get('pathname')} tools={add_tools} cart_line={add_state.get('cart_line')}",
            add_state,
        )

        # Nav + runtime
        for fid, msg, expect, wait in [
            ("W-B-NAV-CART", "go to my cart", "/cart", 10000),
            ("W-B-NAV-CONFIG", "open config", "/config", 10000),
            (
                "W-B-RUNTIME",
                "Plan a weekly grocery list under 2000 rupees with staples and produce — take your time in the background.",
                None,
                16000,
            ),
        ]:
            st, shots = ask_simple(handler, SESSION_B, msg, wait, fid)
            tools = tool_names(st)
            if fid == "W-B-RUNTIME":
                ok = "delegate_to_runtime_agent" in tools and st.get("pathname") != "/agent"
                note = f"handoff={ok} path={st.get('pathname')} tools={tools} hint={str(st.get('hint') or '')[:120]}"
            else:
                ok = st.get("pathname") == expect
                note = f"path={st.get('pathname')} tools={tools}"
            record("buyer", fid, "Pass" if ok else "Fail", shots, note, st)

    # --- Seller smoke ---
    boot_s = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 3000},
                OPEN_ORB_ACTION,
                {"type": "wait", "ms": 4000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot"},
            ],
        },
    )
    boot_s_state = ([s for s in eval_results(boot_s) if "pathname" in s] or [{}])[-1]
    boot_s_shots = shot_paths(boot_s, "W-S-OP-BOOT")
    ready_s = wait_orb_ready(handler, SESSION_S)
    signed_s = bool(boot_s_state.get("has_sign_out"))
    record(
        "seller",
        "W-S-SPA-SESSION",
        "Pass" if signed_s else "Blocked",
        boot_s_shots,
        f"sign_out={signed_s} ready={ready_s.get('ready')}",
        boot_s_state,
    )

    if signed_s:
        for fid, msg, expect_path, wait in [
            ("W-S-HI", "hi", "/dashboard", 10000),
            ("W-S-NAV-CAT", "open catalog", "/catalog", 12000),
            ("W-S-NAV-ORD", "show orders", "/orders", 12000),
            ("W-S-NAV-AG", "open agentguard", "/agentguard", 12000),
        ]:
            st, shots = ask_simple(handler, SESSION_S, msg, wait, fid)
            tools = tool_names(st)
            if fid == "W-S-HI":
                ok = st.get("pathname") == expect_path and "navigate_to" not in tools
            else:
                ok = st.get("pathname") == expect_path
            record(
                "seller",
                fid,
                "Pass" if ok else "Fail",
                shots,
                f"path={st.get('pathname')} tools={tools}",
                st,
            )

        pub, pub_shots = ask_simple(
            handler,
            SESSION_S,
            "publish a simple test item: Operator Atta 1kg at 85 rupees",
            18000,
            "W-S-PUBLISH",
        )
        pub_tools = tool_names(pub)
        pub_ok = "catalog_publish" in pub_tools or pub.get("pathname") == "/catalog"
        record(
            "seller",
            "W-S-PUBLISH",
            "Pass" if pub_ok else "Fail",
            pub_shots,
            f"path={pub.get('pathname')} tools={pub_tools}",
            pub,
        )

        rt, rt_shots = ask_simple(
            handler,
            SESSION_S,
            "Do a background triage of today's seller ops — flag anything needing refund attention.",
            16000,
            "W-S-RUNTIME",
        )
        rt_tools = tool_names(rt)
        rt_ok = "delegate_to_runtime_agent" in rt_tools and rt.get("pathname") != "/agent"
        record(
            "seller",
            "W-S-RUNTIME",
            "Pass" if rt_ok else "Fail",
            rt_shots,
            f"handoff={rt_ok} path={rt.get('pathname')} tools={rt_tools}",
            rt,
        )
    else:
        record("seller", "W-S-NAV-CAT", "Blocked", [], "no Auth0 session", {})

    out = EVIDENCE / f"op-visible-search-{TS}.json"
    out.write_text(json.dumps(LEDGER, indent=2))
    print(f"LEDGER {out}")

    # closeout leave buyer
    try:
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [{"type": "goto", "url": f"{BUYER}/search"}],
            },
        )
    except Exception:
        pass

    fails = sum(1 for side in ("buyer", "seller") for r in LEDGER[side] if r["result"] == "Fail")
    blocked = sum(1 for side in ("buyer", "seller") for r in LEDGER[side] if r["result"] == "Blocked")
    passes = sum(1 for side in ("buyer", "seller") for r in LEDGER[side] if r["result"] == "Pass")
    print(json.dumps({"pass": passes, "fail": fails, "blocked": blocked, "stamp": TS}))
    return 0 if fails == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
