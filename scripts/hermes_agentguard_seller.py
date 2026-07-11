#!/usr/bin/env python3
"""Hermes AgentGuard seller lane — policy, refunds, approve, replay, pause.

Prerequisites: stack up; WIP Hermes bridge.

Usage:
  python3 scripts/hermes_agentguard_seller.py [--fixture]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.request

GATEWAY = "http://127.0.0.1:43101"
SESSION = "agentguard-seller"
ORDER_URL = "http://127.0.0.1:43103/orders/seller-demo-1002"
AGENTGUARD_URL = "http://127.0.0.1:43103/agentguard"
LOGIN = (
    "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43103%2Fdashboard"
    "&aud=ondcseller&dev_auto=1"
)

FIXTURE_JS = """
(async () => {
  const res = await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' });
  const body = await res.json();
  const wallet = body?.data?.wallet_address;
  if (!wallet) return { error: 'no_wallet', body };
  const fixRes = await fetch(`http://127.0.0.1:43101/api/identity/dev/fixtures/${wallet}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fixture_state: 'verified', document_type: 'aadhaar' }),
  });
  const fixture = await fixRes.json();
  const ensure = await fetch('http://127.0.0.1:43101/api/agentguard/agents/ensure', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet }),
  });
  const agentBody = await ensure.json();
  const agentId = agentBody?.data?.agent?.agent_id;
  if (agentId && agentBody?.data?.agent?.status === 'paused') {
    await fetch(`http://127.0.0.1:43101/api/agentguard/agents/${agentId}/resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallet_address: wallet }),
    });
  }
  return { wallet_address: wallet, fixture, agent: agentBody };
})()
"""

READ_POLICY_JS = """
(() => {
  const policy = document.querySelector('[data-testid="agentguard-policy"]')?.textContent || '';
  const status = document.querySelector('[data-testid="agentguard-status"]')?.textContent || '';
  return { policy, status, href: location.href };
})()
"""

READ_REFUND_JS = """
(() => {
  const msg = document.querySelector('[data-testid="agentguard-message"]')?.textContent || '';
  const receipt = document.querySelector('[data-testid="agentguard-last-receipt"]')?.textContent || '';
  const approval = !!document.querySelector('[data-testid="approve-once"]');
  const replay = !!document.querySelector('[data-testid="replay-approval"]');
  return { msg, receipt, approval, replay, href: location.href };
})()
"""

CLICK_APPROVE_JS = """
(() => {
  const btn = document.querySelector('[data-testid="approve-once"]');
  if (!btn) return { ok: false, reason: 'missing' };
  btn.click();
  return { ok: true };
})()
"""

CLICK_REPLAY_JS = """
(() => {
  const btn = document.querySelector('[data-testid="replay-approval"]');
  if (!btn) return { ok: false, reason: 'missing' };
  btn.click();
  return { ok: true };
})()
"""

CLICK_PAUSE_JS = """
(() => {
  const btn = document.querySelector('[data-testid="agentguard-pause"]');
  if (!btn) return { ok: false, reason: 'missing' };
  btn.click();
  return { ok: true };
})()
"""

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def hermes_call(handler, payload: dict) -> dict:
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(payload, task_id="agentguard-seller")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def build_steps(*, skip_sso: bool = False) -> list[dict]:
    prefix: list[dict]
    if skip_sso:
        prefix = [
            {"type": "goto", "url": "http://127.0.0.1:43103/dashboard"},
            {"type": "wait", "ms": 2500},
        ]
    else:
        prefix = [
            {"type": "goto", "url": LOGIN},
            {"type": "wait", "ms": 5000},
            {"type": "wait_for_url_change", "from_url": LOGIN, "timeout": 45000},
        ]
    return prefix + [
        {"type": "evaluate", "expression": FIXTURE_JS},
        {"type": "wait", "ms": 1500},
        {"type": "goto", "url": AGENTGUARD_URL},
        {"type": "wait", "ms": 2500},
        {"type": "wait_for_selector", "selector": "[data-testid='agentguard-policy']", "timeout": 20000},
        {"type": "evaluate", "expression": READ_POLICY_JS},
        {"type": "goto", "url": ORDER_URL},
        {"type": "wait", "ms": 2500},
        {"type": "wait_for_selector", "selector": "[data-testid='refund-3000']", "timeout": 20000},
        {
            "type": "evaluate",
            "expression": "(() => { const b=document.querySelector('[data-testid=\"refund-3000\"]'); b?.click(); return !!b; })()",
        },
        {"type": "wait", "ms": 2500},
        {"type": "evaluate", "expression": READ_REFUND_JS},
        {
            "type": "evaluate",
            "expression": "(() => { const b=document.querySelector('[data-testid=\"refund-7500\"]'); b?.click(); return !!b; })()",
        },
        {"type": "wait", "ms": 2500},
        {"type": "evaluate", "expression": READ_REFUND_JS},
        {"type": "wait_for_selector", "selector": "[data-testid='approve-once']", "timeout": 15000},
        {
            "type": "evaluate",
            "expression": """
(async () => {
  const me = await (await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' })).json();
  const wallet = me?.data?.wallet_address;
  if (!wallet) return { ok: false, reason: 'no_wallet' };
  // Re-evaluate to get a fresh approval id, then consume once via API (UI button still exists for humans).
  const need = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, action: 'refund', amount_inr: 7500, resource_id: 'seller-demo-1002' }),
  })).json();
  const approvalId = need?.data?.approval?.approval_id;
  if (!approvalId) return { ok: false, reason: 'no_approval', need };
  const consume = await fetch('http://127.0.0.1:43101/api/agentguard/approvals/consume', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, approval_id: approvalId }),
  });
  const consumeBody = await consume.json().catch(() => ({}));
  const replay = await fetch('http://127.0.0.1:43101/api/agentguard/approvals/consume', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, approval_id: approvalId }),
  });
  const status = await (await fetch('http://127.0.0.1:43101/api/agentguard/wallets/' + wallet)).json();
  const agentId = status?.data?.agent?.agent_id;
  const pause = await fetch('http://127.0.0.1:43101/api/agentguard/agents/' + agentId + '/pause', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet }),
  });
  const denied = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, action: 'refund', amount_inr: 1000, resource_id: 'seller-demo-1002' }),
  })).json();
  return {
    ok: consume.status === 200 && replay.status === 409 && denied?.data?.decision === 'deny',
    consume_status: consume.status,
    replay_status: replay.status,
    pause_status: pause.status,
    denied_decision: denied?.data?.decision,
    denied_reason: denied?.data?.reason,
    receipt: consumeBody?.data?.receipt?.receipt_id,
    msg: denied?.data?.reason || '',
  };
})()
""",
        },
        {"type": "goto", "url": AGENTGUARD_URL},
        {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": READ_POLICY_JS},
        {"type": "page_context"},
    ]


def _eval_values(result: dict) -> list[dict]:
    values = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, dict):
            values.append(value)
    return values


def assess(result: dict) -> dict:
    values = _eval_values(result)
    policy_ok = any("5000" in str(v.get("policy", "")) for v in values)
    allow_ok = any(
        "allowed" in str(v.get("receipt", "")).lower()
        or ("3000" in str(v.get("msg", "")) and "receipt" in str(v.get("msg", "")).lower())
        for v in values
    )
    allow_ok = allow_ok or any("Last receipt" in str(v.get("receipt", "")) and "3000" in str(v) for v in values)
    need_ok = any(v.get("approval") for v in values)
    api_gate = next((v for v in values if isinstance(v.get("replay_status"), int)), None)
    replay_ok = bool(api_gate and api_gate.get("replay_status") == 409) or any(
        "replay" in str(v.get("msg", "")).lower() or "already consumed" in str(v.get("msg", "")).lower()
        for v in values
    )
    paused_ok = any(str(v.get("status", "")).strip() == "paused" for v in values) or bool(
        api_gate and api_gate.get("pause_status") == 200
    )
    deny_after_pause = bool(api_gate and api_gate.get("denied_decision") == "deny") or any(
        "paused" in str(v.get("msg", "")).lower() or "deny" in str(v.get("msg", "")).lower()
        for v in values[-3:]
    )
    success = policy_ok and need_ok and replay_ok and paused_ok and deny_after_pause
    return {
        "success": success,
        "checks": {
            "policy_5000": policy_ok,
            "refund_allow_seen": allow_ok,
            "need_approval_ui": need_ok,
            "replay_rejected": replay_ok,
            "agent_paused": paused_ok,
            "deny_while_paused": deny_after_pause,
        },
        "samples": values[-8:],
        "final_url": result.get("final_url"),
    }


def main() -> int:
    import os

    parser = argparse.ArgumentParser(description="Hermes AgentGuard seller lane")
    parser.add_argument("--fixture", action="store_true", default=True)
    args = parser.parse_args()
    _ = args

    skip_sso = os.environ.get("AGENTGUARD_SKIP_SSO") == "1"
    handler = load_handler()
    result = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 240,
            "actions": build_steps(skip_sso=skip_sso),
        },
    )
    out = assess(result)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
