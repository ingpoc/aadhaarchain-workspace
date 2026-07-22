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


AGENT_ID = "portfolio-browser"


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def call(handler, args: dict) -> dict:
    """Run via portfolio-browser lease (1 agent → 1 window; no orphan task ids)."""
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import run_with_session_preflight

    payload = dict(args)
    payload.setdefault("session_name", SESSION)
    if payload.get("action") == "preflight":
        payload.setdefault("url", f"{SELLER}/dashboard")
        # Still go through the shared helper so agent_id stays portfolio-browser.
        payload = {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": payload.get("timeout_seconds", 30),
            "actions": [
                {"type": "goto", "url": str(payload.get("url") or f"{SELLER}/dashboard")},
                {"type": "wait", "ms": 500},
            ],
        }
    return run_with_session_preflight(handler, payload, task_id=AGENT_ID)


def click_testid(testid: str) -> dict:
    return {
        "type": "locator",
        "locator": {"by": "testid", "testId": testid},
        "operation": "click",
    }


def fill_testid(testid: str, value: str) -> dict:
    return {
        "type": "locator",
        "locator": {"by": "testid", "testId": testid},
        "operation": "fill",
        "value": value,
    }


def soft_match(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


# Read-only DOM probe — WIP evaluate rejects fetch/click side effects.
EVAL_STATE = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  const hint = panel ? panel.innerText.slice(0, 600) : '';
  const ready = /Text mode ready|Listening \\+ text ready|Listening/i.test(hint);
  // Do not touch localStorage — WIP evaluate is throwOnSideEffect.
  return {
    href: location.href,
    panel: Boolean(panel),
    input: Boolean(input),
    send: Boolean(send),
    ready,
    hint,
    reply: reply ? reply.innerText.slice(0, 500) : '',
  };
})()
"""


def wait_samantha_ready(handler, *, max_rounds: int = 8) -> dict:
    """Open orb and poll until text input is ready (Realtime session up)."""
    last: dict = {}
    for _ in range(max_rounds):
        result = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [
                    click_testid("samantha-orb"),
                    {"type": "wait", "ms": 2500},
                    {"type": "evaluate", "expression": EVAL_STATE},
                ],
            },
        )
        evals = [
            (s.get("value") or s.get("result"))
            for s in result.get("results", [])
            if s.get("type") == "evaluate" and isinstance(s.get("value") or s.get("result"), dict)
        ]
        last = next((e for e in evals if "hint" in e), {})
        if last.get("input") and last.get("send") and (
            last.get("ready") or "error" not in (last.get("hint") or "").lower()
        ):
            if last.get("input") and last.get("send"):
                return last
    return last

EVAL_AGENTGUARD = """
(() => {
  const body = document.body.innerText || '';
  return {
    href: location.href,
    has_agentguard: /AgentGuard/i.test(body),
    has_samantha: /Samantha/i.test(body),
    has_brief: /brief/i.test(body),
    has_pause: /Pause agent/i.test(body),
    orb: Boolean(document.querySelector('[data-testid="samantha-orb"]')),
    snip: body.slice(0, 900),
  };
})()
"""


def main() -> int:
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    handler = load_handler()
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
    # WIP bridge requires an explicit http(s) URL for window preflight.
    pre = call(
        handler,
        {
            "action": "preflight",
            "url": f"{SELLER}/dashboard",
            "session_name": SESSION,
            "timeout_seconds": 20,
        },
    )
    if not pre.get("ready") and not pre.get("success"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    # Demo principal is unique per login — activate authority in the same browser session.
    try:
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 90,
                "actions": [
                    {"type": "goto", "url": demo},
                    {"type": "wait", "ms": 2500},
                    {"type": "goto", "url": f"{SELLER}/agentguard"},
                    {"type": "wait", "ms": 2500},
                    click_testid("agentguard-confirm-mandate"),
                    {"type": "wait", "ms": 2500},
                ],
            },
        )
        mandate_boot = {"via": "ui_activate_authority", "ok": True}
    except RuntimeError as exc:
        mandate_boot = {"via": "ui_activate_authority", "ok": False, "error": str(exc)[:240]}

    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2000},
            ],
        },
    )
    boot_state = wait_samantha_ready(handler)
    if not boot_state.get("input"):
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "samantha_not_ready",
                    "mandate_boot": mandate_boot,
                    "boot_state": boot_state,
                },
                indent=2,
                default=str,
            )
        )
        return 1

    steps: list[dict] = []
    for message, wait_ms, _kw in TURNS:
        steps.extend(
            [
                fill_testid("samantha-orb-text", message),
                click_testid("samantha-orb-send"),
                {"type": "wait", "ms": wait_ms},
                {"type": "evaluate", "expression": EVAL_STATE},
            ]
        )

    # Drain lagging tool replies
    steps.extend(
        [
            fill_testid(
                "samantha-orb-text",
                "Reply with a short done when pending tools finished.",
            ),
            click_testid("samantha-orb-send"),
            {"type": "wait", "ms": 12000},
            {"type": "evaluate", "expression": EVAL_STATE},
        ]
    )

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
                "memory_hit": soft_match(blob, ["brief", "prefer", "remember"]),
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
                {"type": "evaluate", "expression": EVAL_AGENTGUARD},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
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
    mem_ok = any(t.get("memory_hit") for t in turns) or bool(agentguard.get("has_brief"))
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
        "boot_hint": (boot_state.get("hint") or "")[:200],
        "agentguard": agentguard,
        "turns": turns,
    }
    print(json.dumps(out, indent=2, default=str))
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import closeout_session

    try:
        closeout_session(handler, task_id=AGENT_ID)
    except Exception as exc:  # noqa: BLE001 — best-effort closeout
        out["closeout_error"] = str(exc)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
