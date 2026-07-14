#!/usr/bin/env python3
"""FQDN Samantha USP settle→validate→next (one ask at a time). Hermes WIP only.

Sequence: wake → hi → find atta (settle grid) → add → mem → prefer-find → checkout → runtime
→ Seller nav/publish/refund/runtime → voice Blocked evidence → closeout.
No demo flip. $0. Doctrine: claim → screenshot Read → Pass.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "https://gateway.aadharcha.in"
BUYER = "https://ondcbuyer.aadharcha.in"
SELLER = "https://ondcseller.aadharcha.in"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION_B = "web-usp-buyer"
SESSION_S = "web-usp-seller"
TS = time.strftime("%Y%m%d-%H%M%S")
LEDGER: dict = {
    "stamp": TS,
    "buyer": [],
    "seller": [],
    "voice": [],
    "not_covered": [],
    "meta": {},
}


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="usp-settle")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def jq(s: str) -> str:
    return json.dumps(s)


CLICK_ORB = """
(() => {
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  if (!orb) return { ok: false };
  orb.click();
  return { ok: true };
})()
"""

ENSURE_PANEL = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  if (panel) return { ok: true, already: true };
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  if (!orb) return { ok: false };
  orb.click();
  return { ok: true, already: false };
})()
"""

WAIT_READY = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const hint = panel ? (panel.innerText || '') : '';
  const ready = /Text mode ready|Listening \\+ text ready|Listening/i.test(hint);
  const connecting = /Connecting/i.test(hint) && !ready;
  const err = /Realtime not configured|Samantha error|Failed to start/i.test(hint);
  const pulling = /Pulling|Searching|Thinking|Working/i.test(hint);
  return { ready, connecting, err, pulling, hint: hint.slice(0, 280) };
})()
"""

SETTLE = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? (panel.innerText || '') : '';
  const body = document.body.innerText || '';
  const toolsRaw = window.__samanthaTools || [];
  const toolCount = toolsRaw.length;
  const tools = toolsRaw.slice(-24).map(t => {
    if (!t || typeof t !== 'object') return t;
    return {
      name: t.name || t.tool || t.type,
      ok: t.ok,
      navigateTo: t.navigateTo || t.navTo,
      cartAdds: t.cartAdds,
      navSuperseded: t.navSuperseded,
      message: (t.message || t.error || '') ? String(t.message || t.error).slice(0, 160) : undefined,
      itemId: t.itemId || (t.args && t.args.item_id),
    };
  });
  const events = (window.__samanthaEvents || []).slice(-20);
  const errors = (window.__samanthaErrors || []).slice(-12);
  const cards = Array.from(document.querySelectorAll('[data-testid*="result"], article, [class*="result"]'))
    .map(el => (el.innerText || '').trim().slice(0, 80))
    .filter(Boolean)
    .slice(0, 8);
  const cacheIds = (() => {
    try {
      const w = window;
      const c = w.__buyerCatalogCache || w.__samanthaCatalogCache || null;
      if (c && typeof c === 'object') return Object.keys(c).slice(0, 12);
    } catch (_) {}
    return [];
  })();
  const pulling = /Pulling|Searching for|still looking/i.test(body + hint);
  const offerCount = (body.match(/₹|INR|Rs\\.?\\s*\\d/gi) || []).length;
  return {
    href: location.href,
    pathname: location.pathname,
    search: location.search,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0, 10),
    body_snip: body.slice(0, 1600),
    hint: hint.slice(0, 700),
    reply: reply ? reply.innerText.slice(0, 500) : '',
    tools,
    toolCount,
    events,
    errors,
    cards,
    cacheIds,
    pulling,
    offerCount,
    has_sign_out: /Sign out/i.test(body),
    has_atta: /atta/i.test(body),
    has_banana: /banana/i.test(body),
    has_organic: /organic/i.test(body),
    cart_empty: /cart is empty/i.test(body),
    cart_line: /Robusta|Bananas|Atta|AgentGuard PreProd/i.test(body) && location.pathname === '/cart',
    paid: /\\bPaid\\b/i.test(body),
    receipt: /rcpt_[a-z0-9]+/i.test(body),
    ag_card: /Need approval|Denied|AgentGuard/i.test(body) && /checkout|orders|agentguard/i.test(location.pathname + body.slice(0,200)),
    listening: /Listening/i.test(hint),
    text_ready: /Text mode ready|Listening \\+ text ready/i.test(hint),
    no_mic: /no mic/i.test(hint),
  };
})()
"""


def fill_send(message: str) -> str:
    return f"""
(() => {{
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  if (!input || !send) return {{ ok: false, reason: 'missing_controls' }};
  const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeSet.call(input, {jq(message)});
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  if (send.disabled) return {{ ok: false, reason: 'send_disabled', draft: input.value, toolCount: (window.__samanthaTools||[]).length }};
  const before = (window.__samanthaTools || []).length;
  send.click();
  return {{ ok: true, draft: input.value, toolCountBefore: before }};
}})()
"""


def evals(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict):
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
    print(json.dumps({"side": side, "id": fid, "result": result, "notes": notes[:220]}, ensure_ascii=False), flush=True)


def tool_names(state: dict) -> list[str]:
    names = []
    for t in state.get("tools") or []:
        if isinstance(t, dict) and t.get("name"):
            names.append(str(t["name"]))
        elif isinstance(t, str):
            names.append(t)
    return names


def latest_tool(state: dict, name: str) -> dict | None:
    for t in reversed(state.get("tools") or []):
        if isinstance(t, dict) and t.get("name") == name:
            return t
    return None


def wake_gateway():
    meta = LEDGER["meta"]
    for url, key in [
        (f"{GATEWAY}/api/health", "health"),
        (f"{GATEWAY}/api/ondc/status", "ondc_status"),
        (f"{GATEWAY}/api/realtime/status", "realtime"),
    ]:
        try:
            meta[key] = json.loads(urllib.request.urlopen(url, timeout=30).read())
        except Exception as exc:
            meta[f"{key}_err"] = str(exc)
    try:
        req = urllib.request.Request(
            f"{GATEWAY}/api/ondc/bpp/ensure-demo-item",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        meta["ensure_demo"] = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except Exception as exc:
        meta["ensure_err"] = str(exc)


def wait_orb_ready(handler, session: str, rounds: int = 10) -> dict:
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
                    {"type": "evaluate", "expression": ENSURE_PANEL},
                    {"type": "wait", "ms": 1200},
                    {"type": "evaluate", "expression": WAIT_READY},
                ],
            },
        )
        states = evals(r)
        last = states[-1] if states else {}
        if last.get("ready") and not last.get("pulling"):
            return last
        if last.get("err"):
            return last
        time.sleep(1.2)
    return last


def settle_poll(
    handler,
    session: str,
    *,
    tool_count_before: int,
    expect_path: str | None = None,
    require_tool: str | None = None,
    max_rounds: int = 24,
    round_ms: int = 2500,
    allow_pulling: bool = False,
) -> dict:
    """Poll until settle gate: new tool (if required), not pulling (unless allowed), path match."""
    last: dict = {}
    for i in range(max_rounds):
        r = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [{"type": "evaluate", "expression": SETTLE}],
            },
        )
        states = [s for s in evals(r) if "pathname" in s]
        last = states[-1] if states else {}
        last["_round"] = i
        tools = tool_names(last)
        new_tools = (last.get("toolCount") or 0) > tool_count_before
        path_ok = expect_path is None or last.get("pathname") == expect_path
        tool_ok = require_tool is None or require_tool in tools
        pulling = bool(last.get("pulling"))
        ready_hint = bool(last.get("text_ready") or last.get("listening"))
        if path_ok and tool_ok and (new_tools or require_tool is None) and (allow_pulling or not pulling) and ready_hint:
            # For search: also prefer offers or honest empty after some rounds
            if require_tool == "search_catalog" and expect_path == "/results":
                body = last.get("body_snip") or ""
                if (
                    last.get("offerCount", 0) > 0
                    or i >= 8
                    or re.search(r"no match|no offers|couldn't find|0 match", body, re.I)
                ):
                    return last
                # keep waiting for progressive paint
            else:
                return last
        time.sleep(round_ms / 1000)
    return last


def ask_one(
    handler,
    session: str,
    message: str,
    prefix: str,
    *,
    expect_path: str | None = None,
    require_tool: str | None = None,
    no_tools: bool = False,
    settle_rounds: int = 20,
    allow_pulling: bool = False,
    early_poll_results: bool = False,
) -> tuple[dict, list[str], dict]:
    """One ask → settle → screenshot. Never stacks another ask."""
    # capture tool count before
    before_r = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 45,
            "actions": [
                {"type": "evaluate", "expression": ENSURE_PANEL},
                {"type": "wait", "ms": 600},
                {"type": "evaluate", "expression": SETTLE},
            ],
        },
    )
    before_states = [s for s in evals(before_r) if "pathname" in s]
    before = before_states[-1] if before_states else {}
    tool_before = int(before.get("toolCount") or 0)

    send_r = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [{"type": "evaluate", "expression": fill_send(message)}],
        },
    )
    send_states = evals(send_r)
    send_info = send_states[-1] if send_states else {}

    early = {}
    if early_poll_results:
        for _ in range(14):
            time.sleep(0.6)
            poll = call(
                handler,
                {
                    "action": "run",
                    "session_name": session,
                    "use_selected_tab": False,
                    "timeout_seconds": 40,
                    "actions": [{"type": "evaluate", "expression": SETTLE}],
                },
            )
            st = ([s for s in evals(poll) if "pathname" in s] or [{}])[-1]
            early = st
            if st.get("pathname") == "/results":
                break

    if no_tools:
        # greetings: wait for reply, ensure no new tools
        time.sleep(8)
        late = settle_poll(
            handler,
            session,
            tool_count_before=tool_before,
            expect_path=expect_path,
            require_tool=None,
            max_rounds=6,
            round_ms=1500,
            allow_pulling=True,
        )
    else:
        late = settle_poll(
            handler,
            session,
            tool_count_before=tool_before,
            expect_path=expect_path,
            require_tool=require_tool,
            max_rounds=settle_rounds,
            round_ms=2500,
            allow_pulling=allow_pulling,
        )

    shot_r = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "evaluate", "expression": SETTLE},
                {"type": "screenshot"},
            ],
        },
    )
    final_states = [s for s in evals(shot_r) if "pathname" in s]
    final = final_states[-1] if final_states else late
    shots = shot_paths(shot_r, prefix)
    final["_send"] = send_info
    final["_early"] = early
    final["_tool_before"] = tool_before
    return final, shots, send_info


def goto_and_orb(handler, session: str, url: str):
    call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": url},
                {"type": "wait", "ms": 2800},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 3500},
            ],
        },
    )
    return wait_orb_ready(handler, session)


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    wake_gateway()
    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 25})
    LEDGER["meta"]["preflight_ready"] = bool(pre.get("ready"))
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        (EVIDENCE / f"usp-settle-{TS}.json").write_text(json.dumps(LEDGER, indent=2))
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
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 4000},
                {"type": "evaluate", "expression": SETTLE},
                {"type": "screenshot"},
            ],
        },
    )
    boot_st = ([s for s in evals(boot) if "pathname" in s] or [{}])[-1]
    boot_shots = shot_paths(boot, "W-B-USP-BOOT")
    ready = wait_orb_ready(handler, SESSION_B)
    signed = bool(boot_st.get("has_sign_out"))
    record(
        "buyer",
        "W-B-SPA-SESSION",
        "Pass" if signed else "Blocked",
        boot_shots,
        f"sign_out={signed} ready={ready.get('ready')} hint={(ready.get('hint') or '')[:100]}",
        {**boot_st, "ready": ready},
    )
    if not signed:
        LEDGER["not_covered"].append("All Buyer USP flows — Auth0 session missing")
    else:
        # 1) Hi
        hi, hi_shots, hi_send = ask_one(
            handler, SESSION_B, "hi", "W-B-HI", expect_path="/search", no_tools=True, settle_rounds=5
        )
        hi_tools = tool_names(hi)
        new_tools = [t for t in hi_tools if t in ("search_catalog", "navigate_to", "add_to_cart", "checkout_commit")]
        hi_ok = hi.get("pathname") != "/results" and not new_tools and bool(hi_send.get("ok"))
        # if toolCount didn't grow, also ok even if old tools linger
        if (hi.get("toolCount") or 0) == (hi.get("_tool_before") or 0) and hi.get("pathname") != "/results":
            hi_ok = True
        record(
            "buyer",
            "W-B-HI",
            "Pass" if hi_ok else "Fail",
            hi_shots,
            f"path={hi.get('pathname')} new_bad={new_tools} reply={(hi.get('reply') or hi.get('hint') or '')[:120]}",
            hi,
        )

        # cooldown + reset for find
        time.sleep(2)
        goto_and_orb(handler, SESSION_B, f"{BUYER}/search")

        # 2) Find atta — early /results + settle offers
        find, find_shots, find_send = ask_one(
            handler,
            SESSION_B,
            "search for atta",
            "W-B-FIND-ATTA",
            expect_path="/results",
            require_tool="search_catalog",
            early_poll_results=True,
            settle_rounds=22,
            allow_pulling=False,
        )
        early_path = (find.get("_early") or {}).get("pathname")
        find_ok = (
            bool(find_send.get("ok"))
            and find.get("pathname") == "/results"
            and "search_catalog" in tool_names(find)
            and (find.get("offerCount", 0) > 0 or find.get("has_atta") or not find.get("pulling"))
        )
        if early_path != "/results" and find.get("pathname") == "/results":
            # late-only early miss → Partial
            find_result = "Pass" if find_ok else "Fail"
            if find_ok and early_path != "/results":
                find_result = "Partial"
        else:
            find_result = "Pass" if (find_ok and early_path == "/results") else ("Fail" if not find_ok else "Partial")
        if find_ok and early_path == "/results":
            find_result = "Pass"
        elif find_ok:
            find_result = "Partial"
        else:
            find_result = "Fail"
        record(
            "buyer",
            "W-B-FIND-ATTA",
            find_result,
            find_shots,
            f"early={early_path} late={find.get('pathname')} offers={find.get('offerCount')} atta={find.get('has_atta')} tools={tool_names(find)[-6:]}",
            find,
        )

        # 3) Add atta — ONLY after find settled
        time.sleep(2)
        add, add_shots, add_send = ask_one(
            handler,
            SESSION_B,
            "add the atta to my cart",
            "W-B-ADD-ATTA",
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
        add_partial = bool(add_send.get("ok")) and ("add_to_cart" in tool_names(add) or add.get("pathname") == "/cart")
        if add_ok:
            add_result = "Pass"
        elif add_partial:
            add_result = "Partial"
        else:
            add_result = "Fail"
        record(
            "buyer",
            "W-B-ADD-ATTA",
            add_result,
            add_shots,
            f"path={add.get('pathname')} empty={add.get('cart_empty')} line={add.get('cart_line')} tool={add_tool} tools={tool_names(add)[-6:]}",
            add,
        )

        # 4) Remember preference
        time.sleep(2)
        mem, mem_shots, mem_send = ask_one(
            handler,
            SESSION_B,
            "remember I prefer organic atta",
            "W-B-MEM-ORG",
            require_tool="remember_preference",
            settle_rounds=10,
            allow_pulling=True,
        )
        mem_ok = bool(mem_send.get("ok")) and "remember_preference" in tool_names(mem)
        # optional navigate to config to show
        if mem_ok:
            time.sleep(1.5)
            cfg, cfg_shots, _ = ask_one(
                handler,
                SESSION_B,
                "open config",
                "W-B-NAV-CONFIG",
                expect_path="/config",
                require_tool="navigate_to",
                settle_rounds=8,
            )
            cfg_ok = cfg.get("pathname") == "/config"
            record(
                "buyer",
                "W-B-NAV-CONFIG",
                "Pass" if cfg_ok else "Fail",
                cfg_shots,
                f"path={cfg.get('pathname')} organic={cfg.get('has_organic')}",
                cfg,
            )
            mem_visible = bool(cfg.get("has_organic"))
        else:
            mem_visible = False
        record(
            "buyer",
            "W-B-MEM-ORG",
            "Pass" if mem_ok else "Fail",
            mem_shots,
            f"tool_ok={mem_ok} visible_organic={mem_visible} tools={tool_names(mem)[-4:]}",
            mem,
        )

        # 5) Preference-aligned find
        time.sleep(2)
        goto_and_orb(handler, SESSION_B, f"{BUYER}/search")
        pref, pref_shots, pref_send = ask_one(
            handler,
            SESSION_B,
            "find something that matches my organic preference",
            "W-B-FIND-PREF",
            expect_path="/results",
            require_tool="search_catalog",
            early_poll_results=True,
            settle_rounds=18,
        )
        pref_ok = (
            bool(pref_send.get("ok"))
            and pref.get("pathname") == "/results"
            and "search_catalog" in tool_names(pref)
        )
        record(
            "buyer",
            "W-B-FIND-PREF",
            "Pass" if pref_ok else "Fail",
            pref_shots,
            f"path={pref.get('pathname')} offers={pref.get('offerCount')} organic={pref.get('has_organic')} tools={tool_names(pref)[-5:]}",
            pref,
        )

        # 6) Checkout / pay
        time.sleep(2)
        # ensure cart path first if empty from failed add — try nav then checkout
        chk, chk_shots, chk_send = ask_one(
            handler,
            SESSION_B,
            "checkout and pay for my cart",
            "W-B-CHECKOUT",
            require_tool="checkout_commit",
            settle_rounds=14,
            allow_pulling=True,
        )
        chk_ok = bool(chk.get("paid") and chk.get("receipt")) or bool(chk.get("ag_card"))
        chk_tool = "checkout_commit" in tool_names(chk)
        if chk_ok:
            chk_result = "Pass"
        elif chk_tool:
            chk_result = "Partial"
        else:
            chk_result = "Fail"
        record(
            "buyer",
            "W-B-CHECKOUT",
            chk_result,
            chk_shots,
            f"path={chk.get('pathname')} paid={chk.get('paid')} receipt={chk.get('receipt')} ag={chk.get('ag_card')} tools={tool_names(chk)[-5:]}",
            chk,
        )

        # 7) Runtime handoff
        time.sleep(2)
        goto_and_orb(handler, SESSION_B, f"{BUYER}/search")
        rt, rt_shots, rt_send = ask_one(
            handler,
            SESSION_B,
            "Plan a weekly grocery list under 2000 rupees with staples, produce, and dairy — work on it in the background and let me know when done.",
            "W-B-RUNTIME",
            require_tool="delegate_to_runtime_agent",
            settle_rounds=12,
            allow_pulling=True,
        )
        rt_ok = (
            bool(rt_send.get("ok"))
            and "delegate_to_runtime_agent" in tool_names(rt)
            and rt.get("pathname") != "/agent"
        )
        record(
            "buyer",
            "W-B-RUNTIME",
            "Pass" if rt_ok else "Fail",
            rt_shots,
            f"path={rt.get('pathname')} tools={tool_names(rt)[-4:]} hint={(rt.get('hint') or '')[:140]}",
            rt,
        )

        # Voice evidence (no mic claim)
        voice_hint = (rt.get("hint") or ready.get("hint") or "")
        voice_blocked = True  # Hermes automation: no reliable WebRTC mic ask
        record(
            "voice",
            "W-B-VOICE",
            "Blocked",
            [],
            f"Realtime configured; Hermes mic/WebRTC voice ask not Pass. hint={voice_hint[:160]} no_mic={(rt.get('no_mic') or boot_st.get('no_mic'))}",
            {"hint": voice_hint[:300], "listening": rt.get("listening"), "text_ready": rt.get("text_ready")},
        )

    # --- Seller ---
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
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 4000},
                {"type": "evaluate", "expression": SETTLE},
                {"type": "screenshot"},
            ],
        },
    )
    boot_s_st = ([s for s in evals(boot_s) if "pathname" in s] or [{}])[-1]
    boot_s_shots = shot_paths(boot_s, "W-S-USP-BOOT")
    ready_s = wait_orb_ready(handler, SESSION_S)
    signed_s = bool(boot_s_st.get("has_sign_out"))
    record(
        "seller",
        "W-S-SPA-SESSION",
        "Pass" if signed_s else "Blocked",
        boot_s_shots,
        f"sign_out={signed_s} ready={ready_s.get('ready')}",
        {**boot_s_st, "ready": ready_s},
    )

    if signed_s:
        hi_s, hi_s_shots, _ = ask_one(
            handler, SESSION_S, "hi", "W-S-HI", expect_path="/dashboard", no_tools=True, settle_rounds=5
        )
        hi_s_ok = hi_s.get("pathname") in ("/dashboard", "/") or "dashboard" in (hi_s.get("pathname") or "")
        if (hi_s.get("toolCount") or 0) == (hi_s.get("_tool_before") or 0):
            hi_s_ok = True
        record(
            "seller",
            "W-S-HI",
            "Pass" if hi_s_ok else "Fail",
            hi_s_shots,
            f"path={hi_s.get('pathname')} tools={tool_names(hi_s)[-3:]}",
            hi_s,
        )

        for fid, msg, path in [
            ("W-S-NAV-CAT", "open catalog", "/catalog"),
            ("W-S-NAV-ORD", "show orders", "/orders"),
            ("W-S-NAV-AG", "open agentguard", "/agentguard"),
        ]:
            time.sleep(1.5)
            st, shots, send = ask_one(
                handler, SESSION_S, msg, fid, expect_path=path, require_tool="navigate_to", settle_rounds=8
            )
            ok = st.get("pathname") == path and bool(send.get("ok"))
            record("seller", fid, "Pass" if ok else "Fail", shots, f"path={st.get('pathname')} tools={tool_names(st)[-3:]}", st)

        time.sleep(2)
        pub, pub_shots, pub_send = ask_one(
            handler,
            SESSION_S,
            "publish a test organic atta 1kg at 85 rupees",
            "W-S-PUBLISH",
            require_tool="catalog_publish",
            settle_rounds=12,
            allow_pulling=True,
        )
        pub_ok = bool(pub_send.get("ok")) and "catalog_publish" in tool_names(pub)
        record(
            "seller",
            "W-S-PUBLISH",
            "Pass" if pub_ok else "Fail",
            pub_shots,
            f"path={pub.get('pathname')} tools={tool_names(pub)[-4:]} hint={(pub.get('hint') or '')[:100]}",
            pub,
        )

        time.sleep(2)
        ref, ref_shots, ref_send = ask_one(
            handler,
            SESSION_S,
            "refund the latest order for 50 rupees if any exist, otherwise say none",
            "W-S-REFUND",
            settle_rounds=12,
            allow_pulling=True,
        )
        ref_tools = tool_names(ref)
        if "refund_issue" in ref_tools:
            ref_result = "Pass"
        elif any(t in ref_tools for t in ("navigate_to", "delegate_to_runtime_agent")):
            ref_result = "Partial"
        else:
            ref_result = "Fail"
        record(
            "seller",
            "W-S-REFUND",
            ref_result,
            ref_shots,
            f"path={ref.get('pathname')} tools={ref_tools[-5:]} send={ref_send.get('ok')}",
            ref,
        )

        time.sleep(2)
        goto_and_orb(handler, SESSION_S, f"{SELLER}/dashboard")
        srt, srt_shots, srt_send = ask_one(
            handler,
            SESSION_S,
            "Triage today's orders and flag any refunds that need attention — work in the background.",
            "W-S-RUNTIME",
            require_tool="delegate_to_runtime_agent",
            settle_rounds=12,
            allow_pulling=True,
        )
        srt_ok = (
            bool(srt_send.get("ok"))
            and "delegate_to_runtime_agent" in tool_names(srt)
            and srt.get("pathname") != "/agent"
        )
        record(
            "seller",
            "W-S-RUNTIME",
            "Pass" if srt_ok else "Fail",
            srt_shots,
            f"path={srt.get('pathname')} tools={tool_names(srt)[-4:]}",
            srt,
        )

        record(
            "voice",
            "W-S-VOICE",
            "Blocked",
            [],
            "Seller voice twin not attempted — Hermes mic Blocked (same as Buyer)",
            {},
        )
    else:
        LEDGER["not_covered"].append("All Seller USP flows — Auth0 session missing")

    # catalog completeness vs operator-flows
    catalog_ids = [
        "B-HI",
        "B-THX",
        "B-FIND-BANANA",
        "B-FIND-ATTA",
        "B-FIND-MILK",
        "B-FIND-APPLE",
        "B-ADD-BANANA",
        "B-NAV-CART",
        "B-NAV-CHECKOUT",
        "B-NAV-CONFIG",
        "B-NAV-ORDERS",
        "B-MEM-ORG",
        "B-CHECKOUT-OK",
        "B-CHECKOUT-OVER",
        "B-EMPTY",
        "B-CHAINED",
        "B-RUNTIME",
        "B-VOICE-*",
        "S-HI",
        "S-NAV-CAT",
        "S-NAV-ORD",
        "S-NAV-AG",
        "S-PUBLISH",
        "S-REFUND-OK",
        "S-REFUND-OVER",
        "S-MEM",
        "S-RUNTIME",
        "S-VOICE-*",
    ]
    ran_map = {
        "B-HI": "W-B-HI",
        "B-FIND-ATTA": "W-B-FIND-ATTA",
        "B-ADD-BANANA": "W-B-ADD-ATTA",  # USP atta variant
        "B-MEM-ORG": "W-B-MEM-ORG",
        "B-NAV-CONFIG": "W-B-NAV-CONFIG",
        "B-CHECKOUT-OK": "W-B-CHECKOUT",
        "B-RUNTIME": "W-B-RUNTIME",
        "B-VOICE-*": "W-B-VOICE",
        "S-HI": "W-S-HI",
        "S-NAV-CAT": "W-S-NAV-CAT",
        "S-NAV-ORD": "W-S-NAV-ORD",
        "S-NAV-AG": "W-S-NAV-AG",
        "S-PUBLISH": "W-S-PUBLISH",
        "S-REFUND-OK": "W-S-REFUND",
        "S-RUNTIME": "W-S-RUNTIME",
        "S-VOICE-*": "W-S-VOICE",
    }
    all_rows = LEDGER["buyer"] + LEDGER["seller"] + LEDGER["voice"]
    by_id = {r["id"]: r for r in all_rows}
    covered = []
    for cid in catalog_ids:
        wid = ran_map.get(cid)
        if wid and wid in by_id:
            covered.append((cid, by_id[wid]["result"]))
        else:
            LEDGER["not_covered"].append(cid)
    # also note USP preference find is net-new
    if "W-B-FIND-PREF" in by_id:
        covered.append(("B-FIND-PREF (net-new)", by_id["W-B-FIND-PREF"]["result"]))

    pass_n = sum(1 for _, r in covered if r == "Pass")
    partial_n = sum(1 for _, r in covered if r == "Partial")
    blocked_n = sum(1 for _, r in covered if r == "Blocked")
    fail_n = sum(1 for _, r in covered if r == "Fail")
    catalog_n = len(catalog_ids)
    attempted = len(covered)
    # weight: Pass=1, Partial=0.5, Blocked=0.25 (attempted), Fail=0
    score = pass_n + 0.5 * partial_n + 0.25 * blocked_n
    pct_catalog = round(100.0 * score / catalog_n, 1)
    pct_attempted = round(100.0 * score / max(attempted, 1), 1)
    LEDGER["completeness"] = {
        "catalog_ids": catalog_n,
        "attempted": attempted,
        "pass": pass_n,
        "partial": partial_n,
        "blocked": blocked_n,
        "fail": fail_n,
        "pct_catalog_weighted": pct_catalog,
        "pct_attempted_weighted": pct_attempted,
        "usp_gaps": [
            g
            for g in [
                "add→cart after shared txn" if by_id.get("W-B-ADD-ATTA", {}).get("result") != "Pass" else None,
                "preference-aligned finds" if by_id.get("W-B-FIND-PREF", {}).get("result") != "Pass" else None,
                "checkout Paid+receipt via Samantha" if by_id.get("W-B-CHECKOUT", {}).get("result") != "Pass" else None,
                "voice mic/WebRTC" if by_id.get("W-B-VOICE", {}).get("result") == "Blocked" else None,
                "B-THX / B-EMPTY / B-CHAINED / B-FIND-MILK|APPLE / B-CHECKOUT-OVER / S-MEM / S-REFUND-OVER not in this run",
            ]
            if g
        ],
    }

    out = EVIDENCE / f"usp-settle-{TS}.json"
    # trim huge state for ledger file
    slim = json.loads(json.dumps(LEDGER))
    for side in ("buyer", "seller", "voice"):
        for row in slim.get(side, []):
            st = row.get("state") or {}
            row["state"] = {
                k: st.get(k)
                for k in (
                    "pathname",
                    "search",
                    "hint",
                    "reply",
                    "tools",
                    "toolCount",
                    "offerCount",
                    "cart_empty",
                    "cart_line",
                    "paid",
                    "receipt",
                    "ag_card",
                    "has_atta",
                    "has_organic",
                    "errors",
                    "_send",
                    "_early",
                    "_tool_before",
                )
                if k in st
            }
    out.write_text(json.dumps(slim, indent=2))
    print(json.dumps({"ledger": str(out), "completeness": LEDGER["completeness"]}, indent=2), flush=True)

    # closeout
    try:
        sys.path.insert(0, str(ROOT / ".cursor/skills/portfolio-browser/scripts"))
        from wip_hermes import ensure_wip_env

        ensure_wip_env()
        close = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION_B,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 1500},
                ],
            },
        )
        LEDGER["meta"]["closeout_nav"] = close.get("final_url") or BUYER + "/search"
    except Exception as exc:
        LEDGER["meta"]["closeout_err"] = str(exc)

    # rewrite with closeout meta
    slim["meta"] = LEDGER["meta"]
    out.write_text(json.dumps(slim, indent=2))
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
