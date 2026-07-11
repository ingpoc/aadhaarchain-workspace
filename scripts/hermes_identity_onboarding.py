#!/usr/bin/env python3
"""Hermes identity onboarding — unified /verify wizard (UX v1).

Usage:
  python3 scripts/hermes_identity_onboarding.py
  python3 scripts/hermes_identity_onboarding.py --fixture
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_URL = "http://127.0.0.1:43100/verify"
GATEWAY = "http://127.0.0.1:43101"
SESSION = "identity-onboarding"
PAGE_DIAG = ROOT / ".cursor/skills/portfolio-browser/scripts/page_diag.py"


def load_page_diag():
    spec = importlib.util.spec_from_file_location("portfolio_page_diag", PAGE_DIAG)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PAGE_DIAG}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

FILE_UPLOAD_JS = """
(() => {
  const input = document.querySelector('#aadhaar-file');
  if (!input) throw new Error('Missing #aadhaar-file');
  const pdf = '%PDF-1.4\\ntest stub aadhaar';
  const file = new File([pdf], 'aadhaar.pdf', { type: 'application/pdf' });
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));
  return { files: input.files.length, name: input.files[0]?.name || null };
})()
"""

WALLET_JS = """
(async () => {
  try {
    const res = await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' });
    if (res.ok) {
      const body = await res.json();
      if (body?.data?.wallet_address) return body.data.wallet_address;
    }
  } catch (_) {}
  try {
    const pk = window?.solana?.publicKey?.toBase58?.()
      || window?.phantom?.solana?.publicKey?.toBase58?.();
    if (pk) return pk;
  } catch (_) {}
  const btn = document.querySelector('.wallet-adapter-button');
  const label = btn?.textContent?.trim() || '';
  // Never return truncated button labels as wallet addresses.
  return { label, href: location.href, wallet: null };
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
    raw = handler._handle_hermes_chrome_browser(payload, task_id="identity-onboarding")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def onboarding_steps() -> list[dict]:
    return [
        {"type": "goto", "url": "http://127.0.0.1:43100/home"},
        {"type": "wait", "ms": 2500},
        {
            "type": "evaluate",
            "expression": """
(() => {
  const btn = document.querySelector('.wallet-adapter-button, .wallet-adapter-button-trigger');
  if (!btn) return { status: 'no-wallet-button' };
  const label = btn.textContent?.trim() || '';
  if (/Select Wallet/i.test(label)) {
    btn.click();
    return { status: 'opened-wallet-modal' };
  }
  return { status: 'wallet-already-connected', label };
})()
""",
        },
        {"type": "wait", "ms": 1200},
        {
            "type": "evaluate",
            "expression": """
(() => {
  const items = [...document.querySelectorAll('.wallet-adapter-modal-list .wallet-adapter-button, .wallet-adapter-modal-list button, .wallet-adapter-modal li button')];
  const burner = items.find((el) => /burner/i.test(el.textContent || ''));
  if (burner) {
    burner.click();
    return { status: 'clicked-burner' };
  }
  const connected = document.querySelector('.wallet-adapter-button, .wallet-adapter-button-trigger');
  return connected
    ? { status: 'already-connected', label: (connected.textContent || '').trim() }
    : { status: 'no-wallet' };
})()
""",
        },
        {"type": "wait", "ms": 2500},
        {"type": "goto", "url": VERIFY_URL},
        {"type": "wait", "ms": 2500},
        {"type": "click_text", "text": "Continue"},
        {"type": "wait", "ms": 8000},
        {
            "type": "evaluate",
            "expression": """
(() => {
  const buttons = [...document.querySelectorAll('button')];
  const cont = buttons.find((b) => /continue|anchor/i.test((b.textContent || '').trim()) && !b.disabled);
  if (cont && !document.querySelector('#aadhaar-file')) {
    cont.click();
    return 'clicked-continue-again';
  }
  return {
    hasFile: !!document.querySelector('#aadhaar-file'),
    buttons: buttons.map((b) => (b.textContent || '').trim()).filter(Boolean).slice(0, 8),
  };
})()
""",
        },
        {"type": "wait", "ms": 5000},
        {"type": "page_context"},
        {"type": "wait_for_selector", "selector": "#aadhaar-file", "timeout": 20000},
        {"type": "evaluate", "expression": FILE_UPLOAD_JS},
        {"type": "wait", "ms": 800},
        {"type": "click_text", "text": "Continue"},
        {"type": "wait", "ms": 1200},
        {"type": "fill_selector", "selector": "#aadhaar-number", "value": "123456789012"},
        {"type": "fill_selector", "selector": "#full-name", "value": "Portfolio Test User"},
        {"type": "fill_selector", "selector": "#dob", "value": "1990-01-01"},
        {
            "type": "evaluate",
            "expression": "(() => { const c = document.querySelector('input[type=checkbox]'); if (c && !c.checked) c.click(); return !!c?.checked; })()",
        },
        {"type": "click_text", "text": "Submit for verification"},
        {"type": "wait", "ms": 8000},
        {"type": "text"},
        {"type": "evaluate", "expression": WALLET_JS},
        {"type": "page_context"},
    ]


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


def extract_wallet(result: dict) -> str | None:
    def looks_like_wallet(token: str) -> bool:
        if not (32 <= len(token) <= 44 and token.isalnum()):
            return False
        # Reject truncated UI labels and status prefixes.
        if ".." in token or ":" in token or token.startswith("wallet"):
            return False
        return True

    for step in reversed(result.get("results", [])):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, str) and looks_like_wallet(value):
            return value
        if isinstance(value, dict):
            for key in ("wallet", "wallet_address"):
                candidate = value.get(key)
                if isinstance(candidate, str) and looks_like_wallet(candidate):
                    return candidate
    for step in reversed(result.get("results", [])):
        if step.get("type") == "text":
            text = step.get("text") or ""
            for token in text.split():
                if looks_like_wallet(token):
                    return token
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes /verify onboarding lane")
    parser.add_argument("--fixture", action="store_true", help="Apply verified trust fixture after wizard")
    parser.add_argument("--wallet", help="Fixture this wallet instead of parsing Hermes output")
    args = parser.parse_args()

    handler = load_handler()
    preflight = hermes_call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not preflight.get("ready"):
        print(json.dumps({"error": "Hermes not ready", "preflight": preflight}, indent=2), file=sys.stderr)
        return 1

    result = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": load_page_diag().wrap_actions(onboarding_steps()),
        },
    )
    page_diag = load_page_diag().extract_diag(result)

    page_text = ""
    for step in result.get("results", []):
        if step.get("type") == "text":
            page_text = step.get("text") or page_text

    signals = {
        "manual_review": "manual review" in page_text.lower(),
        "verification_complete": "verification complete" in page_text.lower(),
        "anchor_step_done": "#aadhaar-file" in json.dumps(result.get("results", [])),
    }

    wallet = args.wallet or extract_wallet(result)
    fixture_result = None
    if args.fixture and wallet:
        try:
            fixture_result = apply_fixture(wallet)
        except urllib.error.HTTPError as exc:
            fixture_result = {"error": exc.read().decode()}

    out = {
        "success": signals["manual_review"] or signals["verification_complete"] or signals["anchor_step_done"],
        "session": SESSION,
        "verify_url": VERIFY_URL,
        "wallet_address": wallet,
        "signals": signals,
        "fixture": fixture_result,
        "page_diag": page_diag,
        "final_url": result.get("final_url"),
    }
    print(json.dumps(out, indent=2, default=str))
    if not out["success"]:
        return 1
    return 0 if page_diag.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
