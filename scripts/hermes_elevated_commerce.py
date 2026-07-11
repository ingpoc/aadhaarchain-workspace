#!/usr/bin/env python3
"""Hermes elevated commerce — seller catalog publish + buyer checkout (demo mode).

Prerequisites: SSO session + verified trust fixture on session wallet.

Usage:
  python3 scripts/hermes_elevated_commerce.py seller
  python3 scripts/hermes_elevated_commerce.py buyer
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import sys
import time
import urllib.request

GATEWAY = "http://127.0.0.1:43101"
SESSION = "elevated-commerce"

APP_HOME = {
    "seller": "http://127.0.0.1:43103/dashboard",
    "buyer": "http://127.0.0.1:43102/search",
}

SEED_CART_JS = """
(() => {
  const STORAGE_KEY = 'ondc-session-id';
  const LOCAL_CART_STORAGE_KEY = 'ondc-local-cart-session';
  let sessionId = localStorage.getItem(STORAGE_KEY);
  if (!sessionId) {
    sessionId = `session-${Date.now()}-validate`;
    localStorage.setItem(STORAGE_KEY, sessionId);
  }
  const item = {
    id: 'basmati-rice-5kg',
    descriptor: { name: 'Basmati Rice 5kg', short_desc: 'Portfolio validation item' },
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

# WIP fill_selector can Detach mid-chain; set React-controlled inputs via evaluate.
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
  return { wallet_address: wallet, fixture };
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
    raw = handler._handle_hermes_chrome_browser(payload, task_id="elevated-commerce")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def apply_fixture(wallet_address: str) -> dict:
    body = json.dumps({"fixture_state": "verified", "document_type": "aadhaar"}).encode()
    req = urllib.request.Request(
        f"{GATEWAY}/api/identity/dev/fixtures/{wallet_address}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def seller_steps() -> list[dict]:
    sku = f"sku-ux-{int(time.time())}"
    session = "portfolio-commerce-seller"
    return [
        {"type": "goto", "url": "http://127.0.0.1:43103/catalog/new"},
        {"type": "wait", "ms": 3500},
        {"type": "wait_for_selector", "selector": "#product-id", "timeout": 30000},
        {"type": "fill_selector", "selector": "#product-id", "value": sku},
        {"type": "fill_selector", "selector": "#product-name", "value": "UX Validation Rice"},
        {"type": "fill_selector", "selector": "#product-description", "value": "Portfolio commerce validation item"},
        {"type": "fill_selector", "selector": "#product-price", "value": "99"},
        {
            "type": "evaluate",
            "expression": """
(() => {
  const cat = document.querySelector('#product-category');
  if (cat instanceof HTMLSelectElement) {
    cat.value = 'cat-1';
    cat.dispatchEvent(new Event('change', { bubbles: true }));
    return 'select';
  }
  const trigger = document.querySelector('#product-category, [id="product-category"] button, [aria-labelledby="product-category"]');
  if (trigger) {
    trigger.click();
    const option = [...document.querySelectorAll('[role="option"], li, button')].find((el) => /grocery/i.test(el.textContent || ''));
    option?.click();
    return 'dropdown';
  }
  return 'no-category-control';
})()
""",
        },
        {"type": "wait", "ms": 500},
        {
            "type": "evaluate",
            "expression": "(() => { const f = document.querySelector('form'); if (f?.requestSubmit) f.requestSubmit(); else f?.submit?.(); return !!f; })()",
        },
        {"type": "wait_for_url_change", "from_url": "http://127.0.0.1:43103/catalog/new", "timeout": 20000},
        {"type": "page_context"},
    ]


def buyer_steps(*, skip_sso: bool = False) -> list[dict]:
    login = "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43102%2Fsearch&aud=ondcbuyer&dev_auto=1"
    steps: list[dict] = []
    if skip_sso:
        steps.extend([
            {"type": "goto", "url": "http://127.0.0.1:43102/search"},
            {"type": "wait", "ms": 2000},
        ])
    else:
        # WIP leased sessions forbid close_tab — goto replaces the tab URL.
        steps.extend([
            {"type": "goto", "url": login},
            {"type": "wait", "ms": 5000},
            {"type": "wait_for_url_change", "from_url": login, "timeout": 30000},
        ])
    steps.extend([
        {"type": "evaluate", "expression": FIXTURE_JS},
        {"type": "wait", "ms": 1500},
        {"type": "evaluate", "expression": SEED_CART_JS},
        {"type": "wait", "ms": 500},
        {
            "type": "evaluate",
            "expression": "(() => { location.href = 'http://127.0.0.1:43102/checkout'; return location.href; })()",
        },
        {"type": "wait", "ms": 6000},
        {"type": "evaluate", "expression": FILL_DELIVERY_JS},
        {"type": "wait", "ms": 500},
        {"type": "click_text", "text": "Get quote"},
        {"type": "wait", "ms": 3500},
        {"type": "click_text", "text": "Place order"},
        {"type": "wait", "ms": 5000},
        {
            "type": "evaluate",
            "expression": "({ href: location.href, ok: location.pathname.includes('/orders/') })",
        },
        {"type": "page_context"},
    ])
    return steps


def parse_auth_me(result: dict) -> dict | None:
    for step in reversed(result.get("results", [])):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, dict) and value.get("wallet_address"):
            return value
        if isinstance(value, dict) and value.get("fixture"):
            wallet = value.get("wallet_address")
            if wallet:
                return {"wallet_address": wallet}
    return None


def parse_fixture(result: dict) -> dict | None:
    for step in reversed(result.get("results", [])):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, dict) and value.get("fixture"):
            return value.get("fixture")
    return None


def build_steps(app: str, *, with_fixture: bool, skip_sso: bool = False) -> list[dict]:
    if app == "buyer":
        return buyer_steps(skip_sso=skip_sso)
    prefix: list[dict] = []
    if with_fixture:
        prefix = [
            {"type": "goto", "url": "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43103%2Fdashboard&aud=ondcseller&dev_auto=1"},
            {"type": "wait", "ms": 4000},
            {"type": "evaluate", "expression": FIXTURE_JS},
            {"type": "wait", "ms": 1500},
        ]
    return prefix + seller_steps()


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes elevated commerce lane")
    parser.add_argument("app", choices=["seller", "buyer"])
    parser.add_argument("--fixture", action="store_true", help="Apply verified fixture for SSO wallet")
    args = parser.parse_args()

    handler = load_handler()
    skip_sso = os.environ.get("COMMERCE_SKIP_SSO") == "1"
    session = f"elevated-commerce-{args.app}"
    result = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 180,
            "actions": build_steps(args.app, with_fixture=args.fixture, skip_sso=skip_sso),
        },
    )

    auth = parse_auth_me(result)
    fixture = parse_fixture(result)

    final_url = result.get("final_url") or ""
    order_ok = False
    for step in reversed(result.get("results", [])):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, dict) and value.get("ok"):
            order_ok = True
            final_url = value.get("href") or final_url
            break

    if args.app == "seller":
        ok = "/catalog" in final_url and "/catalog/new" not in final_url
    else:
        ok = order_ok or "/orders/" in final_url

    out = {
        "success": ok,
        "app": args.app,
        "auth_me": auth,
        "fixture": fixture,
        "final_url": final_url,
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
