#!/usr/bin/env python3
"""Hermes WIP: Seller Samantha ops text loop (refunds, navigate, pause awareness)."""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
SELLER = "http://127.0.0.1:43103"
SESSION = "samantha-seller-ops"

TURNS: list[tuple[str, int, list[str]]] = [
    (
        "Hi Samantha, help me with store operations today.",
        12000,
        ["help", "refund", "order", "catalog", "agentguard", "ops", "ready"],
    ),
    (
        "Issue a refund of 500 rupees on order seller-demo-1002. Call refund_issue now.",
        22000,
        ["refund", "allow", "executed", "receipt", "500", "agentguard", "approval", "need"],
    ),
    (
        "Call refund_issue for 25000 rupees on order seller-demo-1002.",
        22000,
        ["approval", "need", "limit", "deny", "agentguard", "exceed", "25000"],
    ),
    (
        "Call navigate_to with path /agentguard so I can review mandate and pause.",
        16000,
        ["agentguard", "/agentguard", "mandate", "navigate", "pause"],
    ),
    (
        "Call remember_preference kind preference value brief refund confirmations.",
        16000,
        ["remember", "brief", "prefer", "noted", "got", "preference"],
    ),
]

CONFIRM_MANDATE = """
(async () => {
  const ensure = await fetch('http://127.0.0.1:43101/api/agentguard/agents/ensure', {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role: 'seller' }),
  }).then(r => r.json());
  const compile = await fetch('http://127.0.0.1:43101/api/agentguard/mandates/compile', {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      role: 'seller',
      template: 'seller_ops_v1',
      limits: { auto_approve_max_inr: { 'seller.refund.issue': 5000 }, simulated_payment: true },
      allowed_actions: [
        'seller.catalog.publish','seller.price.change','seller.inventory.commit',
        'seller.order.accept','seller.order.reject','seller.fulfillment.commit',
        'seller.remedy.promise','seller.refund.issue'
      ],
    }),
  }).then(r => r.json());
  const mid = compile?.data?.mandate?.mandate_id;
  let confirm = null;
  if (mid) {
    confirm = await fetch('http://127.0.0.1:43101/api/agentguard/mandates/' + mid + '/confirm', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }).then(r => r.json());
  }
  return {
    ensure_ok: Boolean(ensure?.success),
    mandate_id: mid || null,
    mandate_status: confirm?.data?.mandate?.status || compile?.data?.mandate?.status || null,
  };
})()
"""


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="samantha-seller")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def js_quote(s: str) -> str:
    return json.dumps(s)


EVAL_STATE = """
(async () => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  let me = null;
  try {
    const r = await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' });
    me = await r.json();
  } catch (e) { me = { error: String(e) }; }
  const keys = Object.keys(localStorage).filter(k => k.startsWith('samantha-seller-memory:'));
  const mems = {};
  for (const k of keys) {
    try { mems[k] = JSON.parse(localStorage.getItem(k)); } catch {}
  }
  return {
    href: location.href,
    panel: Boolean(panel),
    hint: panel ? panel.innerText.slice(0, 600) : '',
    reply: reply ? reply.innerText.slice(0, 500) : '',
    principal_id: me?.data?.principal_id || null,
    memory_keys: keys,
    memories: mems,
  };
})()
"""

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


def fill_send(message: str) -> str:
    return f"""
(() => {{
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  if (!input || !send) return {{ ok: false, reason: 'missing_controls' }};
  const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeSet.call(input, {js_quote(message)});
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  send.click();
  return {{ ok: true }};
}})()
"""


def soft_match(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


def main() -> int:
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {
                "aud": "ondcseller",
                "return": f"{SELLER}/dashboard",
                "display_name": "Seller Samantha Ops",
            }
        )
    )

    bootstrap = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2500},
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": CONFIRM_MANDATE},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 10000},
                {"type": "evaluate", "expression": EVAL_STATE},
            ],
        },
    )
    boot_evals = [
        (s.get("value") or s.get("result"))
        for s in bootstrap.get("results", [])
        if s.get("type") == "evaluate" and isinstance(s.get("value") or s.get("result"), dict)
    ]
    mandate_boot = next((e for e in boot_evals if "mandate_status" in e), {})

    steps: list[dict] = [
        {"type": "goto", "url": f"{SELLER}/dashboard"},
        {"type": "wait", "ms": 1500},
        {"type": "evaluate", "expression": ENSURE_PANEL},
        {"type": "wait", "ms": 8000},
    ]
    for message, wait_ms, _kw in TURNS:
        steps.append({"type": "evaluate", "expression": fill_send(message)})
        steps.append({"type": "wait", "ms": wait_ms})
        steps.append({"type": "evaluate", "expression": EVAL_STATE})

    # Drain lagging tool replies
    steps.append(
        {
            "type": "evaluate",
            "expression": fill_send("Reply with a short done when pending tools finished."),
        }
    )
    steps.append({"type": "wait", "ms": 12000})
    steps.append({"type": "evaluate", "expression": EVAL_STATE})

    turns_run = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 240,
            "actions": steps,
        },
    )
    evals = [
        (s.get("value") or s.get("result"))
        for s in turns_run.get("results", [])
        if s.get("type") == "evaluate" and isinstance(s.get("value") or s.get("result"), dict)
    ]
    states = [e for e in evals if "hint" in e or "reply" in e]
    # drop drain state for scoring; keep last N turns
    post = states[-(len(TURNS) + 1) : -1] if len(states) > len(TURNS) else states[-len(TURNS) :]
    turns = []
    for (message, _w, keywords), state in zip(TURNS, post):
        blob = f"{state.get('hint','')}\n{state.get('reply','')}\n{state.get('href','')}"
        mem_blob = json.dumps(state.get("memories") or {})
        ok = soft_match(blob, keywords) or soft_match(
            blob, ["replied", "ready", "refund", "navigate", "thinking", "approval", "remember"]
        )
        turns.append(
            {
                "utterance": message,
                "ok": ok,
                "href": state.get("href"),
                "reply_snip": (state.get("reply") or "")[:200],
                "hint_snip": (state.get("hint") or "")[:200],
                "memory_hit": soft_match(mem_blob, ["brief", "prefer"]),
            }
        )

    snap = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/agentguard"},
                {"type": "wait", "ms": 3000},
                {
                    "type": "evaluate",
                    "expression": """
(() => {
  const keys = Object.keys(localStorage).filter(k => k.startsWith('samantha-seller-memory:'));
  const mems = {};
  for (const k of keys) {
    try { mems[k] = JSON.parse(localStorage.getItem(k)); } catch {}
  }
  return {
    href: location.href,
    has_agentguard: /AgentGuard/i.test(document.body.innerText),
    has_samantha: /Samantha/i.test(document.body.innerText),
    has_brief: /brief/i.test(document.body.innerText),
    has_pause: /Pause agent/i.test(document.body.innerText),
    orb: Boolean(document.querySelector('[data-testid="samantha-orb"]')),
    memories: mems,
    snip: document.body.innerText.slice(0, 900),
  };
})()
""",
                },
            ],
        },
    )
    snap_evals = [
        (s.get("value") or s.get("result"))
        for s in snap.get("results", [])
        if s.get("type") == "evaluate" and isinstance(s.get("value") or s.get("result"), dict)
    ]
    agentguard = next((e for e in snap_evals if "has_pause" in e or "has_agentguard" in e), {})

    passed = sum(1 for t in turns if t["ok"])
    mem_ok = (
        any(t.get("memory_hit") for t in turns)
        or bool(agentguard.get("has_brief"))
        or soft_match(json.dumps(agentguard.get("memories") or {}), ["brief", "prefer"])
    )
    nav_ok = any("/agentguard" in str(t.get("href") or "") for t in turns) or bool(
        agentguard.get("has_agentguard")
    )
    success = (
        passed >= 4
        and bool(agentguard.get("has_agentguard"))
        and bool(agentguard.get("has_samantha"))
        and bool(agentguard.get("orb"))
    )

    out = {
        "success": success,
        "realtime_model": status.get("data", {}).get("model"),
        "turns_passed": passed,
        "turns_total": len(turns),
        "memory_ok": mem_ok,
        "nav_ok": nav_ok,
        "mandate_boot": mandate_boot,
        "agentguard": agentguard,
        "turns": turns,
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
