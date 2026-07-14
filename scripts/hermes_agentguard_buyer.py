#!/usr/bin/env python3
"""Hermes AgentGuard buyer lane — checkout allow, approval, replay, pause."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

SESSION = "agentguard-buyer"
BUYER_URL = "http://127.0.0.1:43102/search"
LOGIN = (
    "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43102%2Fsearch"
    "&aud=ondcbuyer&dev_auto=1"
)

ROOT = pathlib.Path(__file__).resolve().parents[1]

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
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, role: 'buyer' }),
  });
  const agentBody = await ensure.json();
  const agentId = agentBody?.data?.agent?.agent_id;
  if (agentId && agentBody?.data?.agent?.status === 'paused') {
    await fetch(`http://127.0.0.1:43101/api/agentguard/agents/${agentId}/resume`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallet_address: wallet }),
    });
  }
  return { wallet_address: wallet, fixture, agent: agentBody };
})()
"""

BUYER_GATE_JS = """
(async () => {
  const me = await (await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' })).json();
  const wallet = me?.data?.wallet_address;
  if (!wallet) return { ok: false, reason: 'no_wallet', me };

  const allow = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 3000,
      resource_id: 'buyer-checkout-allow'
    }),
  })).json();

  const need = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 15000,
      resource_id: 'buyer-checkout-approval'
    }),
  })).json();
  const approvalId = need?.data?.approval?.approval_id;
  if (!approvalId) return { ok: false, reason: 'no_approval', allow, need };

  const consume = await fetch('http://127.0.0.1:43101/api/agentguard/approvals/consume', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, approval_id: approvalId }),
  });
  const consumeBody = await consume.json().catch(() => ({}));
  const replay = await fetch('http://127.0.0.1:43101/api/agentguard/approvals/consume', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet, approval_id: approvalId }),
  });

  const status = await (await fetch('http://127.0.0.1:43101/api/agentguard/agents/current?role=buyer&wallet_address=' + wallet, {
    credentials: 'include'
  })).json();
  const agentId = status?.data?.agent?.agent_id;
  const pause = await fetch('http://127.0.0.1:43101/api/agentguard/agents/' + agentId + '/pause', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet }),
  });
  const denied = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 1000,
      resource_id: 'buyer-checkout-paused'
    }),
  })).json();

  return {
    ok: allow?.data?.decision === 'allow'
      && need?.data?.decision === 'need_approval'
      && consume.status === 200
      && replay.status === 409
      && pause.status === 200
      && denied?.data?.decision === 'deny',
    wallet_address: wallet,
    allow_decision: allow?.data?.decision,
    need_decision: need?.data?.decision,
    consume_status: consume.status,
    replay_status: replay.status,
    pause_status: pause.status,
    denied_decision: denied?.data?.decision,
    denied_reason: denied?.data?.reason,
    receipt: consumeBody?.data?.receipt?.receipt_id,
  };
})()
"""


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
    raw = handler._handle_hermes_chrome_browser(payload, task_id="agentguard-buyer")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def build_steps(*, skip_sso: bool = False) -> list[dict]:
    prefix = [
        {"type": "goto", "url": BUYER_URL},
        {"type": "wait", "ms": 2500},
    ] if skip_sso else [
        {"type": "goto", "url": LOGIN},
        {"type": "wait", "ms": 5000},
        {"type": "wait_for_url_change", "from_url": LOGIN, "timeout": 45000},
    ]
    return prefix + [
        {"type": "evaluate", "expression": FIXTURE_JS},
        {"type": "wait", "ms": 1000},
        {"type": "goto", "url": "http://127.0.0.1:43102/checkout"},
        {"type": "wait", "ms": 1500},
        {"type": "evaluate", "expression": BUYER_GATE_JS},
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
    gate = next((value for value in values if "allow_decision" in value), {})
    success = bool(gate.get("ok"))
    return {
        "success": success,
        "checks": {
            "checkout_allow": gate.get("allow_decision") == "allow",
            "approval_required": gate.get("need_decision") == "need_approval",
            "approval_consumed": gate.get("consume_status") == 200,
            "replay_rejected": gate.get("replay_status") == 409,
            "agent_paused": gate.get("pause_status") == 200,
            "deny_while_paused": gate.get("denied_decision") == "deny",
        },
        "samples": values[-6:],
        "final_url": result.get("final_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes AgentGuard buyer lane")
    parser.add_argument("--fixture", action="store_true", default=True)
    args = parser.parse_args()
    _ = args

    handler = load_handler()
    result = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 180,
            "actions": build_steps(skip_sso=os.environ.get("AGENTGUARD_SKIP_SSO") == "1"),
        },
    )
    out = assess(result)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
