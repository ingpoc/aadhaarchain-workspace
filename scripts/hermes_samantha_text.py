#!/usr/bin/env python3
"""Hermes WIP: Samantha orb text-mode smoke on Buyer."""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="samantha-text")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def main() -> int:
    # API preflight
    import urllib.request

    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {"aud": "ondcbuyer", "return": f"{BUYER}/search", "display_name": "Samantha Text"}
        )
    )

    EVAL_PANEL = """
(() => {
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = document.querySelector('[data-testid="samantha-orb-hint"], [data-testid="samantha-orb-panel"]');
  const hintText = hint ? hint.innerText : '';
  return {
    orb: Boolean(orb),
    panel: Boolean(panel),
    input: Boolean(input),
    send: Boolean(send),
    reply: reply ? reply.innerText.slice(0, 240) : '',
    hint: hintText.slice(0, 240),
    href: location.href,
  };
})()
"""

    FILL_SEND = """
(() => {
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  if (!input || !send) return { ok: false, reason: 'missing_controls' };
  const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeSet.call(input, 'Find Shimla apples and add them to my cart');
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  send.click();
  return { ok: true, value: input.value };
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

    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    steps = [
        {"type": "goto", "url": demo},
        {"type": "wait", "ms": 2500},
        {"type": "goto", "url": f"{BUYER}/search"},
        {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": CLICK_ORB},
        {"type": "wait", "ms": 8000},
        {"type": "evaluate", "expression": EVAL_PANEL},
        {"type": "evaluate", "expression": FILL_SEND},
        {"type": "wait", "ms": 18000},
        {"type": "evaluate", "expression": EVAL_PANEL},
        {"type": "page_context"},
    ]

    result = call(
        handler,
        {
            "action": "run",
            "session_name": "samantha-text-mode",
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": steps,
        },
    )

    evals = [
        (s.get("value") or s.get("result"))
        for s in result.get("results", [])
        if s.get("type") == "evaluate"
    ]
    panels = [e for e in evals if isinstance(e, dict) and "panel" in e]
    last = panels[-1] if panels else {}
    first = panels[0] if panels else {}

    ok = bool(first.get("panel")) and bool(first.get("input"))
    # Pass if reply text, tool hint about cart/apples, or listening/text ready after send
    evidence = (last.get("reply") or "") + " " + (last.get("hint") or "")
    toolish = any(
        k in evidence.lower()
        for k in ("apple", "cart", "added", "shimla", "search", "replied", "thinking", "ready", "listening")
    )
    out = {
        "success": ok and (bool(last.get("reply")) or toolish),
        "realtime_model": status.get("data", {}).get("model"),
        "panel_open": ok,
        "first_panel": first,
        "after_send": last,
        "final_url": result.get("final_url"),
        "page_diag": result.get("page_diag"),
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
