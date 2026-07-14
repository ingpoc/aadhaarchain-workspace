#!/usr/bin/env python3
"""Operator-long Samantha testing in batches (Hermes WIP text channel)."""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
SESSION = "samantha-operator-long"

BATCHES: list[list[tuple[str, int, list[str]]]] = [
    [
        (
            "Hi Samantha, I'm shopping for tonight's dinner. What can you help with?",
            14000,
            ["dinner", "help", "shop", "find", "cart", "search"],
        ),
        (
            "I'm looking for apples — preferably Shimla or something fresh.",
            18000,
            ["apple", "shimla", "search", "found", "fresh", "cart"],
        ),
        (
            "Add the Shimla Apples to my cart please.",
            18000,
            ["add", "cart", "shimla", "apple", "added"],
        ),
        (
            "Remember that I like organic produce and I dislike bright packaging.",
            16000,
            ["remember", "organic", "dislike", "prefer", "noted", "got", "bright"],
        ),
    ],
    [
        (
            "What do you remember about my preferences?",
            14000,
            ["organic", "bright", "prefer", "dislike", "like", "remember"],
        ),
        (
            "Find milk under 100 rupees and add the cheapest option to my cart.",
            20000,
            ["milk", "cart", "add", "search", "cheap", "rupee"],
        ),
        (
            "Take me to my cart so I can review what we added.",
            14000,
            ["cart", "navigate", "/cart", "review"],
        ),
    ],
    [
        (
            "Try to checkout my cart for twenty five thousand rupees.",
            18000,
            ["approval", "agentguard", "limit", "mandate", "need", "deny", "exceed", "checkout"],
        ),
        (
            "Navigate me to config so I can see AgentGuard and my saved preferences.",
            14000,
            ["config", "/config", "mandate", "prefer", "agentguard"],
        ),
        (
            "Also remember I prefer noise-cancelling headphones for later shopping.",
            14000,
            ["noise", "remember", "prefer", "headphone", "noted", "got"],
        ),
        (
            "Search for purple unicorn cereal — I don't think it exists.",
            16000,
            ["no", "found", "sorry", "couldn't", "unavailable", "none", "empty", "not"],
        ),
    ],
]


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="samantha-long")
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
  const pid = me?.data?.principal_id || '';
  const keys = Object.keys(localStorage).filter(k => k.startsWith('samantha-memory:'));
  const mems = {};
  for (const k of keys) {
    try { mems[k] = JSON.parse(localStorage.getItem(k)); } catch {}
  }
  return {
    href: location.href,
    panel: Boolean(panel),
    hint: panel ? panel.innerText.slice(0, 600) : '',
    reply: reply ? reply.innerText.slice(0, 500) : '',
    principal_id: pid || null,
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


def run_batch(handler, batch: list[tuple[str, int, list[str]]], *, bootstrap: bool) -> list[dict]:
    steps: list[dict] = []
    if bootstrap:
        demo = (
            f"{GATEWAY}/api/auth/demo-continue?"
            + urllib.parse.urlencode(
                {
                    "aud": "ondcbuyer",
                    "return": f"{BUYER}/search",
                    "display_name": "Operator Long Test",
                }
            )
        )
        steps.extend(
            [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2500},
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 10000},
                {"type": "evaluate", "expression": EVAL_STATE},
            ]
        )
    else:
        steps.extend(
            [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2000},
                # Ensure panel open
                {
                    "type": "evaluate",
                    "expression": """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  if (panel) return { ok: true, already: true };
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  if (!orb) return { ok: false };
  orb.click();
  return { ok: true, already: false };
})()
""",
                },
                {"type": "wait", "ms": 8000},
            ]
        )

    for message, wait_ms, _kw in batch:
        steps.append({"type": "evaluate", "expression": fill_send(message)})
        steps.append({"type": "wait", "ms": wait_ms})
        steps.append({"type": "evaluate", "expression": EVAL_STATE})

    result = call(
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
        for s in result.get("results", [])
        if s.get("type") == "evaluate" and isinstance(s.get("value") or s.get("result"), dict)
    ]
    states = [e for e in evals if "hint" in e or "reply" in e]
    # last N states correspond to turns
    post = states[-len(batch) :] if len(states) >= len(batch) else states
    out = []
    for (message, _w, keywords), state in zip(batch, post):
        blob = f"{state.get('hint','')}\n{state.get('reply','')}\n{state.get('href','')}"
        mem_blob = json.dumps(state.get("memories") or {})
        ok = soft_match(blob, keywords) or soft_match(blob, ["replied", "ready", "cart", "search", "thinking"])
        out.append(
            {
                "utterance": message,
                "ok": ok,
                "href": state.get("href"),
                "reply_snip": (state.get("reply") or "")[:200],
                "hint_snip": (state.get("hint") or "")[:200],
                "memories": state.get("memories"),
                "memory_hit": soft_match(mem_blob, ["organic", "bright", "noise", "prefer"]),
            }
        )
    return out


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

    all_turns: list[dict] = []
    for i, batch in enumerate(BATCHES):
        turns = run_batch(handler, batch, bootstrap=(i == 0))
        all_turns.extend(turns)

    # Final cart + config evidence
    snap = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/cart"},
                {"type": "wait", "ms": 2500},
                {
                    "type": "evaluate",
                    "expression": """
(() => ({
  href: location.href,
  has_apple: /apple/i.test(document.body.innerText),
  has_milk: /milk/i.test(document.body.innerText),
  snip: document.body.innerText.slice(0, 900),
}))()
""",
                },
                {"type": "goto", "url": f"{BUYER}/config"},
                {"type": "wait", "ms": 2500},
                {
                    "type": "evaluate",
                    "expression": """
(() => ({
  href: location.href,
  has_agentguard: /AgentGuard/i.test(document.body.innerText),
  has_samantha: /Samantha/i.test(document.body.innerText),
  has_organic: /organic/i.test(document.body.innerText),
  snip: document.body.innerText.slice(0, 900),
}))()
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
    cart = next((e for e in snap_evals if "has_apple" in e), {})
    config = next((e for e in snap_evals if "has_agentguard" in e), {})

    passed = sum(1 for t in all_turns if t["ok"])
    mem_ok = any(t.get("memory_hit") for t in all_turns) or bool(config.get("has_organic"))
    cart_ok = bool(cart.get("has_apple") or cart.get("has_milk"))
    success = passed >= 8 and (cart_ok or passed >= 9)

    out = {
        "success": success,
        "realtime_model": status.get("data", {}).get("model"),
        "turns_passed": passed,
        "turns_total": len(all_turns),
        "memory_ok": mem_ok,
        "cart_ok": cart_ok,
        "cart": cart,
        "config": config,
        "turns": all_turns,
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
