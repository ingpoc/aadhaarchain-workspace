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
  const principal = body?.data?.principal_id;
  const wallet = body?.data?.wallet_address;
  if (!principal && !wallet) return { error: 'no_principal', body };

  // Identity fixture is hangar-only (wallet KYC). Demo/Google principal skips it.
  let fixture = null;
  if (wallet) {
    const fixRes = await fetch(`http://127.0.0.1:43101/api/identity/dev/fixtures/${wallet}`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fixture_state: 'verified', document_type: 'aadhaar' }),
    });
    fixture = await fixRes.json();
  }

  const ensureBody = wallet
    ? { wallet_address: wallet, role: 'seller' }
    : { role: 'seller' };
  const ensure = await fetch('http://127.0.0.1:43101/api/agentguard/agents/ensure', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ensureBody),
  });
  const agentBody = await ensure.json();
  let agentId = agentBody?.data?.agent?.agent_id;
  let status = agentBody?.data?.agent?.status;

  // Re-read current agent — ensure may return stale while pause file still applies.
  const statusUrl = wallet
    ? `http://127.0.0.1:43101/api/agentguard/wallets/${wallet}`
    : 'http://127.0.0.1:43101/api/agentguard/agents/current?role=seller';
  const st = await (await fetch(statusUrl, { credentials: 'include' })).json();
  agentId = st?.data?.agent?.agent_id || agentId;
  status = st?.data?.agent?.status || status;

  let resumed = null;
  if (agentId && status === 'paused') {
    const resumePayload = wallet ? { wallet_address: wallet } : {};
    const r = await fetch(`http://127.0.0.1:43101/api/agentguard/agents/${agentId}/resume`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(resumePayload),
    });
    resumed = { http: r.status, body: await r.json().catch(() => ({})) };
    const st2 = await (await fetch(statusUrl, { credentials: 'include' })).json();
    status = st2?.data?.agent?.status || status;
  }
  return {
    principal_id: principal || null,
    wallet_address: wallet || null,
    fixture,
    agent: agentBody,
    status,
    resumed,
  };
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
  const err = document.querySelector('.text-destructive')?.textContent || '';
  const approval = !!document.querySelector('[data-testid="approve-once"]');
  const replay = !!document.querySelector('[data-testid="replay-approval"]');
  const approveDisabled = !!document.querySelector('[data-testid="approve-once"][disabled]');
  return { msg, err, receipt, approval, replay, approveDisabled, href: location.href };
})()
"""


# Compact judged UI flow — Hermes MAX_ACTIONS=20 silently truncates longer lists.
JUDGED_ORDER_JS = """
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const read = () => ({
    msg: document.querySelector('[data-testid="agentguard-message"]')?.textContent || '',
    err: '',  // avoid destructive Button label false positives
    receipt: document.querySelector('[data-testid="agentguard-last-receipt"]')?.textContent || '',
    approval: !!document.querySelector('[data-testid="approve-once"]'),
    replay: !!document.querySelector('[data-testid="replay-approval"]'),
  });
  const click = (sel) => {
    const btn = document.querySelector(sel);
    if (!btn) return { ok: false, reason: 'missing', sel };
    if (btn.disabled) return { ok: false, reason: 'disabled', sel, disabled: true };
    btn.click();
    return { ok: true, sel };
  };
  const waitFor = async (sel, timeoutMs, { enabled = false } = {}) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      const el = document.querySelector(sel);
      if (el && (!enabled || !el.disabled)) return true;
      await sleep(200);
    }
    return false;
  };
  const waitMsg = async (pred, timeoutMs) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (pred(read())) return true;
      await sleep(200);
    }
    return false;
  };

  if (!(await waitFor('[data-testid="refund-3000"]', 20000, { enabled: true }))) {
    const btn = document.querySelector('[data-testid="refund-3000"]');
    return {
      ok: false,
      reason: 'no_refund_3000',
      present: !!btn,
      disabled: !!btn?.disabled,
      subjectHint: document.body?.innerText?.includes('Sign in') || false,
    };
  }
  click('[data-testid="refund-3000"]');
  await waitMsg((s) => !!s.msg || !!s.receipt, 8000);
  const after3000 = read();

  click('[data-testid="refund-7500"]');
  await waitMsg((s) => s.approval || /approv/i.test(s.msg), 8000);
  const after7500 = read();
  if (!after7500.approval) {
    return { ok: false, reason: 'no_approve_btn', after3000, after7500 };
  }

  const approve = click('[data-testid="approve-once"]');
  await waitMsg((s) => s.replay && !s.approval, 10000);
  // Approve clears pending button; replay remains via lastApprovalId.
  const afterApprove = read();
  if (!afterApprove.replay) {
    return { ok: false, reason: 'no_replay_btn', approve, after3000, after7500, afterApprove };
  }

  const replay = click('[data-testid="replay-approval"]');
  await waitMsg((s) => /replay|consumed|already/i.test(s.msg), 8000);
  const afterReplay = read();

  return {
    ok: approve.ok && replay.ok,
    action: 'order_judged',
    after3000,
    after7500,
    afterApprove,
    afterReplay,
    approve,
    replay,
  };
})()
"""

PAUSE_AND_DENY_JS = """
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const waitFor = async (sel, timeoutMs) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (document.querySelector(sel)) return true;
      await sleep(200);
    }
    return false;
  };
  if (!(await waitFor('[data-testid="agentguard-pause"]', 20000))) {
    return { ok: false, reason: 'no_pause_btn' };
  }
  const before = {
    policy: document.querySelector('[data-testid="agentguard-policy"]')?.textContent || '',
    status: document.querySelector('[data-testid="agentguard-status"]')?.textContent || '',
  };
  const btn = document.querySelector('[data-testid="agentguard-pause"]');
  const label = (btn?.textContent || '').trim();
  if (/resume/i.test(label)) {
    return { ok: false, reason: 'already_paused', label, before };
  }
  btn.click();
  await sleep(4000);
  const afterPause = {
    policy: document.querySelector('[data-testid="agentguard-policy"]')?.textContent || '',
    status: document.querySelector('[data-testid="agentguard-status"]')?.textContent || '',
  };
  // Navigate to order and attempt refund while paused (caller does goto; this only pauses).
  return { ok: true, action: 'pause', before, afterPause, label };
})()
"""

DENY_WHILE_PAUSED_JS = """
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const waitFor = async (sel, timeoutMs, { enabled = false } = {}) => {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      const el = document.querySelector(sel);
      if (el && (!enabled || !el.disabled)) return true;
      await sleep(200);
    }
    return false;
  };
  if (!(await waitFor('[data-testid="refund-3000"]', 20000, { enabled: true }))) {
    const btn = document.querySelector('[data-testid="refund-3000"]');
    return {
      ok: false,
      reason: btn?.disabled ? 'refund_blocked' : 'no_refund_btn',
      present: !!btn,
      disabled: !!btn?.disabled,
    };
  }
  const btn = document.querySelector('[data-testid="refund-3000"]');
  btn.click();
  const start = Date.now();
  let msg = '';
  let receipt = '';
  while (Date.now() - start < 8000) {
    msg = document.querySelector('[data-testid="agentguard-message"]')?.textContent || '';
    receipt = document.querySelector('[data-testid="agentguard-last-receipt"]')?.textContent || '';
    if (/paus|deny/i.test(msg) || /paus/i.test(receipt)) break;
    await sleep(200);
  }
  return { ok: true, action: 'deny_refund', msg, receipt };
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
    """Keep <=20 Hermes actions (plugin MAX_ACTIONS=20 truncates silently)."""
    prefix: list[dict]
    if skip_sso:
        prefix = [
            {"type": "goto", "url": "http://127.0.0.1:43103/dashboard"},
            {"type": "wait", "ms": 2000},
        ]
    else:
        prefix = [
            {"type": "goto", "url": LOGIN},
            {"type": "wait", "ms": 5000},
            {"type": "wait_for_url_change", "from_url": LOGIN, "timeout": 45000},
        ]
    # 2–3 prefix + 12 judged = <=15 (SSO prefix uses 3 → 15 total)
    return prefix + [
        {"type": "evaluate", "expression": FIXTURE_JS},
        {"type": "goto", "url": AGENTGUARD_URL},
        {"type": "wait", "ms": 2500},
        {"type": "wait_for_selector", "selector": "[data-testid='agentguard-policy']", "timeout": 20000},
        {"type": "evaluate", "expression": READ_POLICY_JS},
        {"type": "goto", "url": ORDER_URL},
        {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": JUDGED_ORDER_JS},
        {"type": "goto", "url": AGENTGUARD_URL},
        {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": PAUSE_AND_DENY_JS},
        {"type": "goto", "url": ORDER_URL},
        {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": DENY_WHILE_PAUSED_JS},
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

    def flatten(v: dict) -> list[dict]:
        out = [v]
        for key in ("after3000", "after7500", "afterApprove", "afterReplay", "before", "afterPause"):
            nested = v.get(key)
            if isinstance(nested, dict):
                out.append(nested)
        return out

    flat: list[dict] = []
    for v in values:
        flat.extend(flatten(v))

    clicks = [
        v
        for v in values
        if isinstance(v.get("action"), str)
        or v.get("reason")
        in {
            "missing_or_disabled",
            "missing",
            "disabled",
            "no_refund_3000",
            "no_approve_btn",
            "no_replay_btn",
            "no_pause_btn",
            "already_paused",
            "no_refund_btn",
            "refund_blocked",
            "no_principal",
            "no_wallet",
        }
    ]
    policy_ok = any("5000" in str(v.get("policy", "")) for v in flat)
    allow_ok = any(
        "allowed" in str(v.get("msg", "")).lower()
        or ("3000" in str(v.get("msg", "")) and "receipt" in str(v.get("msg", "")).lower())
        or ("Last receipt" in str(v.get("receipt", "")) and "3000" in str(v))
        for v in flat
    )
    need_ok = any(v.get("approval") for v in flat)
    def _msg(v: dict) -> str:
        return str(v.get("msg", "")).lower()
    replay_ok = any(
        "replay" in _msg(v) or "already consumed" in _msg(v) or "consumed" in _msg(v)
        for v in flat
    )
    paused_ok = any(str(v.get("status", "")).strip().lower() == "paused" for v in flat)
    deny_after_pause = any("paused" in _msg(v) or "deny" in _msg(v) for v in flat[-6:])
    click_ok = all(v.get("ok") for v in clicks) if clicks else False
    success = policy_ok and need_ok and replay_ok and paused_ok and deny_after_pause and click_ok
    return {
        "success": success,
        "checks": {
            "policy_5000": policy_ok,
            "refund_allow_seen": allow_ok,
            "need_approval_ui": need_ok,
            "replay_rejected": replay_ok,
            "agent_paused": paused_ok,
            "deny_while_paused": deny_after_pause,
            "ui_clicks_ok": click_ok,
        },
        "samples": values[-8:],
        "final_url": result.get("final_url"),
        "action_count_note": "hermes MAX_ACTIONS=20; build_steps must stay <=20",
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
            "timeout_seconds": 300,
            "actions": build_steps(skip_sso=skip_sso),
        },
    )
    out = assess(result)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
