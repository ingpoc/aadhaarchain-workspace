#!/usr/bin/env python3
"""Hermes AgentGuard buyer lane — checkout allow / need / consume / replay / pause.

Prerequisites: stack up; WIP Hermes bridge.

Usage:
  python3 scripts/hermes_agentguard_buyer.py [--fixture]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

SESSION = "agentguard-buyer"
LOGIN = (
    "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43102%2Fsearch"
    "&aud=ondcbuyer&dev_auto=1"
)

SEED_CART_JS = """
(() => {
  const STORAGE_KEY = 'ondc-session-id';
  const LOCAL_CART_STORAGE_KEY = 'ondc-local-cart-session';
  let sessionId = localStorage.getItem(STORAGE_KEY);
  if (!sessionId) {
    sessionId = `session-${Date.now()}-agentguard`;
    localStorage.setItem(STORAGE_KEY, sessionId);
  }
  const item = {
    id: 'basmati-rice-5kg',
    descriptor: { name: 'Basmati Rice 5kg', short_desc: 'AgentGuard buyer validation' },
    name: 'Basmati Rice 5kg',
    price: { currency: 'INR', value: '640.00' },
    images: [],
  };
  const now = new Date().toISOString();
  const session = {
    id: sessionId,
    status: 'active',
    createdAt: now,
    updatedAt: now,
    items: [{ id: 'line-basmati-rice-5kg', item, quantity: 1, addedAt: now }],
    buyer: {
      name: 'Portfolio Test User',
      email: 'portfolio@test.local',
      phone: '+919876543210',
      contact: { email: 'portfolio@test.local', phone: '+919876543210' },
      country: 'IND',
    },
  };
  const store = JSON.parse(localStorage.getItem(LOCAL_CART_STORAGE_KEY) || '{}');
  store[sessionId] = session;
  localStorage.setItem(LOCAL_CART_STORAGE_KEY, JSON.stringify(store));
  return { sessionId, itemCount: session.items.length };
})()
"""

FILL_DELIVERY_JS = """
(() => {
  const set = (sel, val) => {
    const el = document.querySelector(sel);
    if (!el) return false;
    const proto = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
    proto.set.call(el, val);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  };
  return {
    line1: set('#delivery-line1', '12 Test Lane'),
    city: set('#delivery-city', 'Bengaluru'),
    state: set('#delivery-state', 'Karnataka'),
    pin: set('#delivery-postal-code', '560001'),
  };
})()
"""

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

CHECKOUT_GATE_JS = """
(async () => {
  const me = await (await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' })).json();
  const wallet = me?.data?.wallet_address;
  if (!wallet) return { ok: false, reason: 'no_wallet' };
  const allow = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 3000,
      resource_id: 'buyer-agentguard-allow',
    }),
  })).json();
  const need = await (await fetch('http://127.0.0.1:43101/api/agentguard/actions/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 15000,
      resource_id: 'buyer-agentguard-need',
    }),
  })).json();
  const approvalId = need?.data?.approval?.approval_id;
  if (!approvalId) return { ok: false, reason: 'no_approval', allow, need };
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
    body: JSON.stringify({
      wallet_address: wallet,
      action: 'checkout',
      amount_inr: 500,
      resource_id: 'buyer-agentguard-paused',
    }),
  })).json();
  return {
    ok:
      allow?.data?.decision === 'allow' &&
      need?.data?.decision === 'need_approval' &&
      consume.status === 200 &&
      replay.status === 409 &&
      denied?.data?.decision === 'deny',
    allow_decision: allow?.data?.decision,
    need_decision: need?.data?.decision,
    need_reason: need?.data?.reason,
    consume_status: consume.status,
    replay_status: replay.status,
    pause_status: pause.status,
    denied_decision: denied?.data?.decision,
    receipt: consumeBody?.data?.receipt?.receipt_id,
  };
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
    raw = handler._handle_hermes_chrome_browser(payload, task_id="agentguard-buyer")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def build_steps(*, skip_sso: bool = False) -> list[dict]:
    if skip_sso:
        prefix = [
            {"type": "goto", "url": "http://127.0.0.1:43102/search"},
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
        {"type": "evaluate", "expression": SEED_CART_JS},
        {"type": "wait", "ms": 500},
        {
            "type": "evaluate",
            "expression": "(() => { location.href = 'http://127.0.0.1:43102/checkout'; return location.href; })()",
        },
        {"type": "wait", "ms": 5000},
        {"type": "evaluate", "expression": FILL_DELIVERY_JS},
        {"type": "wait", "ms": 500},
        {"type": "click_text", "text": "Get quote"},
        {"type": "wait", "ms": 3500},
        {"type": "click_text", "text": "Place order"},
        {"type": "wait", "ms": 5000},
        {
            "type": "evaluate",
            "expression": """
(() => {
  const note = document.querySelector('[data-testid="buyer-agentguard-note"]')?.textContent || '';
  return {
    href: location.href,
    order_ok: location.pathname.includes('/orders/'),
    note,
  };
})()
""",
        },
        {"type": "evaluate", "expression": CHECKOUT_GATE_JS},
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
    ui = next((v for v in values if "order_ok" in v), None)
    gate = next((v for v in values if "replay_status" in v), None)
    order_ok = bool(ui and ui.get("order_ok"))
    note_ok = bool(ui and ("allowed" in str(ui.get("note", "")).lower() or "receipt" in str(ui.get("note", "")).lower()))
    gate_ok = bool(gate and gate.get("ok"))
    success = order_ok and gate_ok
    return {
        "success": success,
        "checks": {
            "checkout_order": order_ok,
            "agentguard_note": note_ok,
            "allow_checkout": bool(gate and gate.get("allow_decision") == "allow"),
            "need_approval": bool(gate and gate.get("need_decision") == "need_approval"),
            "replay_rejected": bool(gate and gate.get("replay_status") == 409),
            "deny_while_paused": bool(gate and gate.get("denied_decision") == "deny"),
        },
        "samples": values[-6:],
        "final_url": result.get("final_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes AgentGuard buyer lane")
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
