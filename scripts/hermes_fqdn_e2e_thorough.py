#!/usr/bin/env python3
"""Thorough ONDC FQDN E2E after SPA session Pass (claim → screenshot → Pass).

Surfaces: ondcbuyer / ondcseller / gateway.aadharcha.in
Bridge: Hermes Chrome WIP only. No demo flip. No secrets in evidence JSON.
"""
from __future__ import annotations

import argparse
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
SESSION_B = "web-e2e-buyer"
SESSION_S = "web-e2e-seller"
TS = time.strftime("%Y%m%d-%H%M%S")
TASK_ID = f"fqdn-e2e-{TS}"
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
    raw = handler._handle_hermes_chrome_browser(args, task_id=TASK_ID)
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


WAIT_READY = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const hint = panel ? (panel.innerText || '') : '';
  const ready = /Text mode ready|Listening \\+ text ready|Listening/i.test(hint);
  const connecting = /Connecting|No mic/i.test(hint) && !ready;
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
  const tools = (window.__samanthaTools || []).slice(-16);
  const events = (window.__samanthaEvents || []).slice(-40);
  const errors = (window.__samanthaErrors || []).slice(-8);
  const btns = Array.from(document.querySelectorAll('button,a'))
    .map(el => (el.textContent || '').trim())
    .filter(Boolean)
    .slice(0, 40);
  return {
    href: location.href,
    pathname: location.pathname,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0,12),
    body_snip: body.slice(0, 1200),
    hint: hint.slice(0, 700),
    reply: reply ? reply.innerText.slice(0, 500) : '',
    tools,
    event_types: events,
    errors,
    has_sign_out: btns.some(t => /^Sign out$/i.test(t)),
    has_sign_in: btns.some(t => /^Sign in$/i.test(t)),
    has_banana: /banana/i.test(body),
    has_atta: /AgentGuard PreProd Atta|Sharbati Atta|Test Atta/i.test(body),
    cart_empty: /Your cart is empty/i.test(body),
    has_cart_item: /\\d+ item(?:s)? ready for trust-aware checkout/i.test(body),
    has_milk: /milk/i.test(body),
    has_organic: /organic/i.test(body),
    has_receipt: /receipt|rcpt_/i.test(body),
    has_paid: /\\bPaid\\b/i.test(body),
    has_approval: /need.?approval|Need approval|Approval required/i.test(body),
    has_deny: /\\bdeny|denied\\b/i.test(body),
    has_refund: /refund/i.test(body),
    has_refund_panel: Boolean(document.querySelector('[data-testid="agentguard-refund-panel"]')),
    has_catalog: /catalog|sku|listing|product/i.test(body),
    has_mandate: /mandate|agentguard|auto.?approve/i.test(body),
    has_handoff: /I've started|I'll let you know|started working/i.test(hint + ' ' + body),
    has_pause_agent: btns.some(t => /^Pause agent$/i.test(t)),
    has_resume_agent: btns.some(t => /^Resume agent$/i.test(t)),
    has_protected_activity: /Protected activity/i.test(body),
    has_verify_receipt: btns.some(t => /^Verify receipt$/i.test(t)),
    has_verified_receipt: /\\bVerified\\b/i.test(body),
    has_replay_rejected: /replay rejected|already consumed/i.test(body),
    durability_disclosed: /Durable production storage is not enabled/i.test(body),
    mic_hint: /Listening \\+ text ready|no mic|Text mode ready/i.test(hint),
    voice_connected: /Listening \\+ text ready/i.test(hint),
    text_ready: /Text mode ready/i.test(hint),
  };
})()
"""

def eval_states(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict):
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
        saved.append(dest.name)
    return saved


def wake_gateway() -> None:
    try:
        urllib.request.urlopen(f"{GATEWAY}/api/health", timeout=20).read()
    except Exception:
        pass


def last_eval(states: list[dict], *keys: str) -> dict:
    for s in reversed(states):
        if any(k in s for k in keys):
            return s
    return states[-1] if states else {}


def record(side: str, mid: str, result: str, shots: list[str], notes: str, state: dict | None = None) -> None:
    entry = {
        "id": mid,
        "result": result,
        "shots": shots,
        "notes": notes,
        "state": {
            k: (state or {}).get(k)
            for k in (
                "pathname",
                "href",
                "hint",
                "reply",
                "tools",
                "has_sign_out",
                "has_banana",
                "has_receipt",
                "has_paid",
                "has_approval",
                "has_handoff",
                "has_pause_agent",
                "has_resume_agent",
                "has_protected_activity",
                "has_verify_receipt",
                "has_verified_receipt",
                "durability_disclosed",
                "voice_connected",
                "text_ready",
                "mandate_id",
                "mandate_status",
                "principal",
                "mic_ok",
            )
            if (state or {}).get(k) is not None
        },
    }
    LEDGER[side].append(entry)
    print(json.dumps({"id": mid, "result": result, "shots": shots, "notes": notes[:200]}, indent=2))


def wait_samantha_ready(handler, session: str, max_rounds: int = 8) -> dict:
    probe = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 30,
            "actions": [{"type": "evaluate", "expression": WAIT_READY}],
        },
    )
    last = last_eval(eval_states(probe), "ready", "hint")
    if last.get("ready") or last.get("err"):
        return last
    if not last.get("hint"):
        call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 30,
                "actions": [
                    {
                        "type": "click_selector",
                        "selector": '[data-testid="samantha-orb"]',
                    },
                    {
                        "type": "wait_for_selector",
                        "selector": '[data-testid="samantha-orb-panel"]',
                        "timeout": 8000,
                    },
                ],
            },
        )
    for _ in range(max_rounds):
        result = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 40,
                "actions": [
                    {"type": "wait", "ms": 2500},
                    {"type": "evaluate", "expression": WAIT_READY},
                ],
            },
        )
        states = eval_states(result)
        last = last_eval(states, "ready", "hint")
        if last.get("ready") or last.get("err"):
            return last
    return last


def ask(handler, session: str, message: str, mid: str, wait_ms: int = 22000) -> tuple[dict, list[str]]:
    ready = wait_samantha_ready(handler, session)
    if ready.get("err"):
        result = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        state = last_eval(eval_states(result), "href")
        state["ready_err"] = ready
        return state, save_evidence(mid, shot_paths(result))

    result = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": max(120, wait_ms // 1000 + 60),
            "actions": [
                {
                    "type": "fill_selector",
                    "selector": '[data-testid="samantha-orb-text"]',
                    "value": message,
                },
                {
                    "type": "click_selector",
                    "selector": '[data-testid="samantha-orb-send"]',
                },
                {"type": "wait", "ms": wait_ms},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    state = last_eval(eval_states(result), "href")
    state["ready_before"] = ready
    return state, save_evidence(mid, shot_paths(result))


def goto_shot(handler, session: str, url: str, mid: str) -> tuple[dict, list[str]]:
    result = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 70,
            "actions": [
                {"type": "goto", "url": url},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    return last_eval(eval_states(result), "href"), save_evidence(mid, shot_paths(result))


def tool_names(state: dict) -> list[str]:
    return [t.get("name") for t in (state.get("tools") or []) if isinstance(t, dict) and t.get("name")]


def run_buyer(handler) -> None:
    wake_gateway()
    # Boot: confirm SPA session + mandate + open orb
    boot = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
                {
                    "type": "click_selector",
                    "selector": '[data-testid="samantha-orb"]',
                },
                {"type": "wait", "ms": 14000},
                {"type": "evaluate", "expression": WAIT_READY},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    states = eval_states(boot)
    page = last_eval([s for s in states if "href" in s], "href")
    spa = {"success": bool(page.get("has_sign_out")), "principal": "session-cookie"}
    mandate = {"mandate_status": "visible" if page.get("has_mandate") else None}
    mic = {
        "mic_ok": bool(page.get("voice_connected")),
        "error": None if page.get("voice_connected") else "browser did not expose voice-connected state",
    }
    ready = last_eval(states, "ready")
    shots = save_evidence("W-B-BOOT", shot_paths(boot))

    signed = bool(page.get("has_sign_out"))
    record(
        "buyer",
        "W-B-SPA-SESSION",
        "Pass" if signed else "Needs sign-in",
        shots,
        f"principal={spa.get('principal')} sign_out={page.get('has_sign_out')} mandate={mandate.get('mandate_status')}",
        {**page, **spa, **mandate},
    )
    record(
        "buyer",
        "W-B-MANDATE",
        "Pass" if mandate.get("mandate_status") else "Blocked",
        shots,
        f"status={mandate.get('mandate_status')} id={mandate.get('mandate_id')} msg={mandate.get('compile_msg')}",
        mandate,
    )
    record(
        "buyer",
        "W-B-VOICE-MIC",
        "Pass" if mic.get("mic_ok") else "Blocked",
        shots,
        f"mic_ok={mic.get('mic_ok')} err={mic.get('error')} ready={ready}",
        mic,
    )

    if not signed:
        signin = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 90,
                "actions": [
                    {"type": "click_text", "text": "Sign in"},
                    {"type": "wait", "ms": 8000},
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 3000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                    {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                    {"type": "wait", "ms": 12000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        states = eval_states(signin)
        page = last_eval([s for s in states if "href" in s], "href")
        shots = save_evidence("W-B-SIGNIN", shot_paths(signin))
        signed = bool(page.get("has_sign_out"))
        record(
            "buyer",
            "W-B-SPA-SESSION",
            "Pass" if signed else "Fail",
            shots,
            f"after Sign in click principal=session-cookie sign_out={page.get('has_sign_out')}",
            {**page, "principal": "session-cookie"},
        )
        if not signed:
            LEDGER["meta"]["buyer_aborted"] = "no SPA session after Sign in"
            return

    # Greeting
    st, sh = ask(handler, SESSION_B, "hi", "W-B-HI", wait_ms=12000)
    tools = tool_names(st)
    record(
        "buyer",
        "W-B-HI",
        "Pass" if "/search" in (st.get("pathname") or "") and not tools else "Fail",
        sh,
        f"path={st.get('pathname')} tools={tools} reply={ (st.get('reply') or '')[:80] }",
        st,
    )

    # Search the exact Seller-published item used by the PreProd network grader.
    st, sh = ask(handler, SESSION_B, "find AgentGuard PreProd Atta", "W-B-FIND-ATTA", wait_ms=28000)
    ok = st.get("has_atta") and "/results" in (st.get("pathname") or "")
    record(
        "buyer",
        "W-B-FIND-ATTA",
        "Pass" if ok else "Fail",
        sh,
        f"path={st.get('pathname')} atta={st.get('has_atta')} tools={tool_names(st)} hint={(st.get('hint') or '')[:120]}",
        st,
    )

    # Add to cart
    st, sh = ask(handler, SESSION_B, "add AgentGuard PreProd Atta to my cart", "W-B-ADD-ATTA", wait_ms=32000)
    cart_st, cart_sh = goto_shot(handler, SESSION_B, f"{BUYER}/cart", "W-B-CART")
    ok = cart_st.get("has_cart_item") and not cart_st.get("cart_empty")
    record(
        "buyer",
        "W-B-ADD-ATTA",
        "Pass" if ok else "Fail",
        sh + cart_sh,
        f"ask_tools={tool_names(st)} cart_item={cart_st.get('has_cart_item')} empty={cart_st.get('cart_empty')} cart_snip={(cart_st.get('body_snip') or '')[:160]}",
        {**st, "cart": cart_st},
    )
    record(
        "buyer",
        "W-B-CART",
        "Pass" if cart_st.get("has_cart_item") and not cart_st.get("cart_empty") else "Fail",
        cart_sh,
        f"path={cart_st.get('pathname')} cart_item={cart_st.get('has_cart_item')} empty={cart_st.get('cart_empty')}",
        cart_st,
    )

    # Navigate tools
    st, sh = ask(handler, SESSION_B, "go to checkout", "W-B-NAV-CHECKOUT", wait_ms=18000)
    record(
        "buyer",
        "W-B-NAV-CHECKOUT",
        "Pass" if "/checkout" in (st.get("pathname") or "") else "Fail",
        sh,
        f"path={st.get('pathname')} tools={tool_names(st)}",
        st,
    )

    st, sh = ask(handler, SESSION_B, "remember I prefer organic", "W-B-MEM-ORG", wait_ms=18000)
    cfg_st, cfg_sh = goto_shot(handler, SESSION_B, f"{BUYER}/config", "W-B-CONFIG")
    record(
        "buyer",
        "W-B-MEM-ORG",
        "Pass" if "remember_preference" in tool_names(st) or cfg_st.get("has_organic") else "Partial",
        sh + cfg_sh,
        f"tools={tool_names(st)} organic_ui={cfg_st.get('has_organic')}",
        st,
    )
    record(
        "buyer",
        "W-B-CONFIG",
        "Pass" if "/config" in (cfg_st.get("pathname") or "") else "Fail",
        cfg_sh,
        f"path={cfg_st.get('pathname')} mandate={cfg_st.get('has_mandate')}",
        cfg_st,
    )

    # Checkout / pay
    wake_gateway()
    # Ensure cart then checkout ask
    goto_shot(handler, SESSION_B, f"{BUYER}/cart", "W-B-CART-PRE")
    # reopen orb after navigation
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 12000},
            ],
        },
    )
    st, sh = ask(handler, SESSION_B, "checkout and pay for my cart", "W-B-CHECKOUT", wait_ms=40000)
    # Follow to orders if navigated, else capture checkout page
    path = st.get("pathname") or ""
    if "/orders" in path or st.get("has_paid") or st.get("has_receipt") or st.get("has_approval"):
        co_st, co_sh = st, sh
    else:
        co_st, co_sh = goto_shot(handler, SESSION_B, f"{BUYER}/checkout", "W-B-CHECKOUT-PAGE")
        co_sh = sh + co_sh
    ok = co_st.get("has_paid") or co_st.get("has_receipt") or co_st.get("has_approval")
    record(
        "buyer",
        "W-B-CHECKOUT",
        "Pass" if ok else "Fail",
        co_sh,
        f"ask_path={path} tools={tool_names(st)} paid={co_st.get('has_paid')} receipt={co_st.get('has_receipt')} approval={co_st.get('has_approval')} snip={(co_st.get('body_snip') or '')[:200]}",
        {**st, "page": co_st},
    )

    # Buyer authority/activity proof: pause, observe paused state, resume, and
    # verify a receipt through visible controls. No in-page mutation/fetch.
    controls = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 70,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/config"},
                {"type": "wait", "ms": 3000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    control_state = last_eval(eval_states(controls), "href")
    control_shots = save_evidence("W-B-AG-CONTROLS", shot_paths(controls))
    if control_state.get("has_pause_agent"):
        paused = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 40,
                "actions": [
                    {"type": "click_selector", "selector": '[data-testid="buyer-config-toggle-agent"]'},
                    {"type": "wait", "ms": 1800},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        paused_state = last_eval(eval_states(paused), "href")
        paused_shots = save_evidence("W-B-AG-PAUSED", shot_paths(paused))
        resumed = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 40,
                "actions": [
                    {"type": "click_selector", "selector": '[data-testid="buyer-config-toggle-agent"]'},
                    {"type": "wait", "ms": 1800},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        resumed_state = last_eval(eval_states(resumed), "href")
        resumed_shots = save_evidence("W-B-AG-RESUMED", shot_paths(resumed))
        record(
            "buyer",
            "W-B-AG-PAUSE-RESUME",
            "Pass" if paused_state.get("has_resume_agent") and resumed_state.get("has_pause_agent") else "Fail",
            control_shots + paused_shots + resumed_shots,
            f"paused={paused_state.get('has_resume_agent')} resumed={resumed_state.get('has_pause_agent')} durability={control_state.get('durability_disclosed')}",
            {**resumed_state, "paused_observed": paused_state.get("has_resume_agent")},
        )
    else:
        record(
            "buyer",
            "W-B-AG-PAUSE-RESUME",
            "Fail",
            control_shots,
            "Pause agent control not visible.",
            control_state,
        )

    if control_state.get("has_verify_receipt"):
        verified = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 40,
                "actions": [
                    {"type": "click_text", "text": "Verify receipt", "exact": True},
                    {"type": "wait", "ms": 1500},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        verified_state = last_eval(eval_states(verified), "href")
        verified_shots = save_evidence("W-B-AG-RECEIPT", shot_paths(verified))
        record(
            "buyer",
            "W-B-AG-RECEIPT",
            "Pass" if verified_state.get("has_verified_receipt") else "Fail",
            verified_shots,
            f"activity={verified_state.get('has_protected_activity')} verified={verified_state.get('has_verified_receipt')}",
            verified_state,
        )
    else:
        record(
            "buyer",
            "W-B-AG-RECEIPT",
            "Blocked",
            control_shots,
            f"activity={control_state.get('has_protected_activity')} no receipt available after checkout",
            control_state,
        )

    # Runtime handoff
    wake_gateway()
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2000},
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 12000},
            ],
        },
    )
    st, sh = ask(
        handler,
        SESSION_B,
        "plan my weekly groceries under 2000 rupees with a shopping list and budget breakdown",
        "W-B-RUNTIME",
        wait_ms=45000,
    )
    # Wait longer for handoff completion notify
    time.sleep(8)
    late = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 50,
            "actions": [
                {"type": "wait", "ms": 15000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    late_st = last_eval(eval_states(late), "href")
    late_sh = save_evidence("W-B-RUNTIME-LATE", shot_paths(late))
    handoff = st.get("has_handoff") or late_st.get("has_handoff") or "delegate_to_runtime_agent" in tool_names(st)
    not_agent = "/agent" not in (st.get("pathname") or "") and "/agent" not in (late_st.get("pathname") or "")
    record(
        "buyer",
        "W-B-RUNTIME",
        "Pass" if handoff and not_agent else ("Partial" if handoff or not_agent else "Fail"),
        sh + late_sh,
        f"handoff={handoff} path={st.get('pathname')} late_path={late_st.get('pathname')} tools={tool_names(st)} hint={(st.get('hint') or '')[:160]}",
        st,
    )

    # Voice pillar: attempt mic reconnect via orb reopen; Pass only if Listening+text
    voice = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_B,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    vst = last_eval(eval_states(voice), "href")
    vsh = save_evidence("W-B-VOICE", shot_paths(voice))
    if vst.get("voice_connected"):
        # try a short voice-path ask still via text if mic connected for session
        ask_st, ask_sh = ask(handler, SESSION_B, "show milk under 100", "W-B-VOICE-ASK", wait_ms=25000)
        record(
            "buyer",
            "W-B-VOICE",
            "Pass" if ask_st.get("has_milk") or tool_names(ask_st) else "Partial",
            vsh + ask_sh,
            f"voice_connected=True tools={tool_names(ask_st)}",
            ask_st,
        )
    else:
        record(
            "buyer",
            "W-B-VOICE",
            "Blocked",
            vsh,
            f"gateway Realtime configured; orb hint text-only (no mic). hint={(vst.get('hint') or '')[:160]}",
            vst,
        )


def run_seller(handler) -> None:
    wake_gateway()
    boot = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
                {
                    "type": "click_selector",
                    "selector": '[data-testid="samantha-orb"]',
                },
                {"type": "wait", "ms": 14000},
                {"type": "evaluate", "expression": WAIT_READY},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    states = eval_states(boot)
    page = last_eval([s for s in states if "href" in s], "href")
    spa = {"success": bool(page.get("has_sign_out")), "principal": "session-cookie"}
    mandate = {"mandate_status": "visible" if page.get("has_mandate") else None}
    shots = save_evidence("W-S-BOOT", shot_paths(boot))
    signed = bool(page.get("has_sign_out"))
    record(
        "seller",
        "W-S-SPA-SESSION",
        "Pass" if signed else "Needs sign-in",
        shots,
        f"principal={spa.get('principal')} sign_out={page.get('has_sign_out')} mandate={mandate.get('mandate_status')}",
        {**page, **spa, **mandate},
    )

    if not signed:
        # Try Sign in click → silent SSO
        signin = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_S,
                "use_selected_tab": False,
                "timeout_seconds": 90,
                "actions": [
                    {"type": "click_text", "text": "Sign in"},
                    {"type": "wait", "ms": 8000},
                    {"type": "goto", "url": f"{SELLER}/dashboard"},
                    {"type": "wait", "ms": 3000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                    {
                        "type": "click_selector",
                        "selector": '[data-testid="samantha-orb"]',
                    },
                    {"type": "wait", "ms": 12000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                ],
            },
        )
        states = eval_states(signin)
        page = last_eval([s for s in states if "href" in s], "href")
        spa = {"success": bool(page.get("has_sign_out")), "principal": "session-cookie"}
        mandate = {"mandate_status": "visible" if page.get("has_mandate") else None}
        shots = save_evidence("W-S-SIGNIN", shot_paths(signin))
        signed = bool(page.get("has_sign_out"))
        record(
            "seller",
            "W-S-SPA-SESSION",
            "Pass" if signed else "Fail",
            shots,
            f"after Sign in click principal={spa.get('principal')} sign_out={page.get('has_sign_out')}",
            {**page, **spa, **mandate},
        )
        if not signed:
            LEDGER["meta"]["seller_aborted"] = "no SPA session"
            # still capture surfaces
            for mid, url in [
                ("W-S-CAT", f"{SELLER}/catalog"),
                ("W-S-ORD", f"{SELLER}/orders"),
                ("W-S-AG", f"{SELLER}/agentguard"),
            ]:
                st, sh = goto_shot(handler, SESSION_S, url, mid)
                expected = {
                    "W-S-CAT": "/catalog",
                    "W-S-ORD": "/orders",
                    "W-S-AG": "/agentguard",
                }[mid]
                record("seller", mid, "Pass" if expected in (st.get("pathname") or "") else "Fail", sh, f"path={st.get('pathname')}", st)
            return

    st, sh = ask(handler, SESSION_S, "hi", "W-S-HI", wait_ms=12000)
    record(
        "seller",
        "W-S-HI",
        "Pass" if not tool_names(st) else "Partial",
        sh,
        f"path={st.get('pathname')} tools={tool_names(st)}",
        st,
    )

    st, sh = ask(handler, SESSION_S, "open catalog", "W-S-NAV-CAT", wait_ms=18000)
    record(
        "seller",
        "W-S-NAV-CAT",
        "Pass" if "/catalog" in (st.get("pathname") or "") else "Fail",
        sh,
        f"path={st.get('pathname')} tools={tool_names(st)}",
        st,
    )

    st, sh = ask(handler, SESSION_S, "show orders", "W-S-NAV-ORD", wait_ms=18000)
    record(
        "seller",
        "W-S-NAV-ORD",
        "Pass" if "/orders" in (st.get("pathname") or "") else "Fail",
        sh,
        f"path={st.get('pathname')} tools={tool_names(st)}",
        st,
    )

    st, sh = ask(handler, SESSION_S, "open agentguard", "W-S-NAV-AG", wait_ms=18000)
    ag_st, ag_sh = goto_shot(handler, SESSION_S, f"{SELLER}/agentguard", "W-S-AG")
    record(
        "seller",
        "W-S-NAV-AG",
        "Pass" if "/agentguard" in (st.get("pathname") or ag_st.get("pathname") or "") else "Fail",
        sh + ag_sh,
        f"path={st.get('pathname')} ag={ag_st.get('pathname')}",
        st,
    )

    # Publish
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/catalog"},
                {"type": "wait", "ms": 2000},
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 12000},
            ],
        },
    )
    st, sh = ask(
        handler,
        SESSION_S,
        "publish a simple grocery item named Test Atta 1kg priced at 80 rupees",
        "W-S-PUBLISH",
        wait_ms=35000,
    )
    cat_st, cat_sh = goto_shot(handler, SESSION_S, f"{SELLER}/catalog", "W-S-CAT-AFTER")
    body = cat_st.get("body_snip") or ""
    ok = "catalog_publish" in tool_names(st) or ("Test Atta" in body) or ("atta" in body.lower())
    record(
        "seller",
        "W-S-PUBLISH",
        "Pass" if ok else "Fail",
        sh + cat_sh,
        f"tools={tool_names(st)} snip={body[:200]}",
        st,
    )

    # Natural latest-order refund. Passing requires an AgentGuard outcome, not
    # merely the word "refund" or a tool invocation.
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/orders"},
                {"type": "wait", "ms": 2000},
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 12000},
            ],
        },
    )
    st, sh = ask(
        handler,
        SESSION_S,
        "issue a refund of 50 rupees for the latest order if any",
        "W-S-REFUND",
        wait_ms=30000,
    )
    if "refund_issue" in tool_names(st) and (st.get("has_receipt") or st.get("has_approval")):
        res = "Pass"
    elif "0 incoming" in (st.get("body_snip") or "") or "no order" in (st.get("hint") or "").lower():
        res = "Blocked"
    else:
        res = "Fail"
    record(
        "seller",
        "W-S-REFUND",
        res,
        sh,
        f"tools={tool_names(st)} hint={(st.get('hint') or '')[:160]} snip={(st.get('body_snip') or '')[:160]}",
        st,
    )

    # Deterministic Seller refund boundary: allow, need-approval, approve once,
    # receipt, and replay rejection are exercised through visible UI controls.
    refund_open = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/orders"},
                {"type": "wait", "ms": 3000},
                {"type": "click_text", "text": "View Details"},
                {"type": "wait", "ms": 3000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    refund_page = last_eval(eval_states(refund_open), "href")
    refund_page_sh = save_evidence("W-S-REFUND-PAGE", shot_paths(refund_open))
    record(
        "seller",
        "W-S-REFUND-PAGE",
        "Pass"
        if "/orders/" in (refund_page.get("pathname") or "") and refund_page.get("has_refund_panel")
        else "Fail",
        refund_page_sh,
        f"path={refund_page.get('pathname')} panel={refund_page.get('has_refund_panel')}",
        refund_page,
    )
    low = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "click_selector", "selector": '[data-testid="refund-3000"]'},
                {"type": "wait", "ms": 3500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    low_st = last_eval(eval_states(low), "href")
    low_sh = save_evidence("W-S-REFUND-ALLOW", shot_paths(low))
    record(
        "seller",
        "W-S-REFUND-ALLOW",
        "Pass" if low_st.get("has_receipt") else "Fail",
        refund_page_sh + low_sh,
        f"page={refund_page.get('pathname')} receipt={low_st.get('has_receipt')}",
        low_st,
    )

    high = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "click_selector", "selector": '[data-testid="refund-7500"]'},
                {"type": "wait", "ms": 3000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    high_st = last_eval(eval_states(high), "href")
    high_sh = save_evidence("W-S-REFUND-APPROVAL", shot_paths(high))
    record(
        "seller",
        "W-S-REFUND-APPROVAL",
        "Pass" if high_st.get("has_approval") else "Fail",
        high_sh,
        f"approval={high_st.get('has_approval')}",
        high_st,
    )

    replay = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 70,
            "actions": [
                {"type": "click_selector", "selector": '[data-testid="approve-once"]'},
                {"type": "wait", "ms": 3500},
                {"type": "click_selector", "selector": '[data-testid="replay-approval"]'},
                {"type": "wait", "ms": 3500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    replay_st = last_eval(eval_states(replay), "href")
    replay_sh = save_evidence("W-S-REFUND-REPLAY", shot_paths(replay))
    record(
        "seller",
        "W-S-REFUND-REPLAY",
        "Pass" if replay_st.get("has_receipt") and replay_st.get("has_replay_rejected") else "Fail",
        replay_sh,
        f"receipt={replay_st.get('has_receipt')} replay_rejected={replay_st.get('has_replay_rejected')}",
        replay_st,
    )

    # Memory
    st, sh = ask(handler, SESSION_S, "remember I prefer brief confirmations", "W-S-MEM", wait_ms=18000)
    record(
        "seller",
        "W-S-MEM",
        "Pass" if "remember_preference" in tool_names(st) else "Partial",
        sh,
        f"tools={tool_names(st)}",
        st,
    )

    # Runtime
    wake_gateway()
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2000},
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 12000},
            ],
        },
    )
    st, sh = ask(
        handler,
        SESSION_S,
        "triage all pending seller orders and refunds for today and summarize actions needed",
        "W-S-RUNTIME",
        wait_ms=45000,
    )
    handoff = st.get("has_handoff") or "delegate_to_runtime_agent" in tool_names(st)
    not_agent = "/agent" not in (st.get("pathname") or "")
    record(
        "seller",
        "W-S-RUNTIME",
        "Pass" if handoff and not_agent else ("Partial" if not_agent else "Fail"),
        sh,
        f"handoff={handoff} path={st.get('pathname')} tools={tool_names(st)} hint={(st.get('hint') or '')[:160]}",
        st,
    )

    # Voice
    vst, vsh = goto_shot(handler, SESSION_S, f"{SELLER}/dashboard", "W-S-VOICE")
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "click_selector", "selector": '[data-testid="samantha-orb"]'},
                {"type": "wait", "ms": 10000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    # reuse last ask state pattern
    voice = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION_S,
            "use_selected_tab": False,
            "timeout_seconds": 40,
            "actions": [
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    vst = last_eval(eval_states(voice), "href")
    vsh = save_evidence("W-S-VOICE", shot_paths(voice))
    record(
        "seller",
        "W-S-VOICE",
        "Pass" if vst.get("voice_connected") else "Blocked",
        vsh,
        f"hint={(vst.get('hint') or '')[:160]}",
        vst,
    )


def close_harness_sessions(handler) -> None:
    try:
        result = call(handler, {"action": "closeout", "timeout_seconds": 20})
        LEDGER["meta"]["sessions_closed"] = [result.get("session_id") or TASK_ID]
    except Exception as exc:  # noqa: BLE001 — persist closeout failure
        LEDGER["meta"].setdefault("closeout_errors", []).append(
            {"session": TASK_ID, "error": str(exc)}
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("side", nargs="?", choices=("buyer", "seller", "both"), default="both")
    args = parser.parse_args(argv)

    handler = None
    exit_code = 0
    try:
        wake_gateway()
        try:
            rt = json.loads(
                urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=20).read()
            )
            LEDGER["meta"]["realtime"] = rt.get("data")
        except Exception as exc:  # noqa: BLE001 — evidence, not a crash
            LEDGER["meta"]["realtime_err"] = str(exc)

        handler = load_handler()
        pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
        if not pre.get("ready"):
            raise RuntimeError(f"bridge not ready: {pre}")
        LEDGER["meta"]["preflight_ready"] = True

        if args.side in ("buyer", "both"):
            run_buyer(handler)
        if args.side in ("seller", "both"):
            run_seller(handler)
    except Exception as exc:  # noqa: BLE001 — persist failure evidence and close tabs
        LEDGER["meta"]["fatal_error"] = str(exc)
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        exit_code = 1
    finally:
        if handler is not None:
            close_harness_sessions(handler)

    validation_failures = [
        entry["id"]
        for side in ("buyer", "seller")
        for entry in LEDGER[side]
        if entry.get("result") == "Fail"
    ]
    if validation_failures:
        LEDGER["meta"]["validation_failures"] = validation_failures
        exit_code = 1

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE / f"web-e2e-thorough-{TS}.json"
    out.write_text(json.dumps(LEDGER, indent=2))
    print(f"LEDGER={out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
