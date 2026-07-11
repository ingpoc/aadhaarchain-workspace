#!/usr/bin/env python3
"""Portfolio SSO browser test via Hermes Chrome.

Uses dev_auto burner when NEXT_PUBLIC_DEV_BURNER_WALLET=true (local default),
otherwise Phantom wallet connect in real Chrome.

Usage:
  python3 scripts/hermes_portfolio_sso.py seller
  python3 scripts/hermes_portfolio_sso.py buyer
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import urllib.parse

AUDIENCE = {
    "buyer": ("ondcbuyer", "http://127.0.0.1:43102/search"),
    "seller": ("ondcseller", "http://127.0.0.1:43103/dashboard"),
}

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_LOCAL = ROOT / "aadharchain" / "frontend" / ".env.local"
PAGE_DIAG = ROOT / ".cursor/skills/portfolio-browser/scripts/page_diag.py"


def load_page_diag():
    spec = importlib.util.spec_from_file_location("portfolio_page_diag", PAGE_DIAG)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PAGE_DIAG}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def burner_enabled() -> bool:
    if not ENV_LOCAL.exists():
        return False
    return "NEXT_PUBLIC_DEV_BURNER_WALLET=true" in ENV_LOCAL.read_text()


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="portfolio-sso")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def login_url(app: str, *, dev_auto: bool) -> str:
    aud, return_url = AUDIENCE[app]
    encoded = urllib.parse.quote(return_url, safe="")
    url = f"http://127.0.0.1:43100/login?return={encoded}&aud={aud}"
    if dev_auto:
        url += "&dev_auto=1"
    return url


def dev_auto_steps(login: str, session: str) -> list[dict]:
    # WIP leased sessions forbid close_tab — goto replaces the tab URL instead.
    # 5s covers burner auto-connect when :8899 is healthy (ensure-validator in preflight).
    return [
        {"type": "goto", "url": login},
        {"type": "wait", "ms": 5000},
        {"type": "wait_for_url_change", "from_url": login, "timeout": 30000},
        {"type": "page_context"},
    ]


def phantom_steps(login: str, session: str) -> list[dict]:
    return [
        {"type": "goto", "url": login},
        {"type": "wait", "ms": 2000},
        {"type": "page_context"},
        {"type": "click_text", "text": "Select Wallet"},
        {"type": "wait", "ms": 1500},
        {"type": "click_text", "text": "Phantom"},
        {"type": "wait", "ms": 2500},
        {"type": "click_text", "text": "Sign in and continue"},
        {"type": "wait_for_url_change", "from_url": login, "timeout": 30000},
        {"type": "page_context"},
    ]


def buyer_checkout_only_steps() -> list[dict]:
    """Post-SSO buyer checkout tail (single Hermes session)."""
    commerce = importlib.util.spec_from_file_location(
        "hermes_elevated_commerce",
        ROOT / "scripts" / "hermes_elevated_commerce.py",
    )
    if commerce is None or commerce.loader is None:
        raise RuntimeError("Cannot load hermes_elevated_commerce.py")
    module = importlib.util.module_from_spec(commerce)
    commerce.loader.exec_module(module)
    fixture_js = module.FIXTURE_JS
    seed_cart_js = module.SEED_CART_JS

    return [
        {"type": "evaluate", "expression": fixture_js},
        {"type": "wait", "ms": 1500},
        {"type": "evaluate", "expression": seed_cart_js},
        {"type": "wait", "ms": 500},
        {"type": "goto", "url": "http://127.0.0.1:43102/checkout"},
        {"type": "wait", "ms": 6000},
        {"type": "evaluate", "expression": module.FILL_DELIVERY_JS},
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
    ]


def main() -> int:
    argv = [a for a in sys.argv[1:] if a != "--checkout"]
    with_checkout = "--checkout" in sys.argv[1:]
    app = (argv[0] if argv else "seller").lower()
    if app not in AUDIENCE:
        print(f"Unknown app {app!r}. Use: buyer | seller", file=sys.stderr)
        return 2

    use_burner = burner_enabled()
    login = login_url(app, dev_auto=use_burner)
    session = f"aadhaarchain-sso-{app}"
    if with_checkout and app == "buyer":
        steps = [
            {"type": "goto", "url": login},
            {"type": "wait", "ms": 5000},
        ]
        steps.extend(buyer_checkout_only_steps())
    else:
        steps = dev_auto_steps(login, session) if use_burner else phantom_steps(login, session)

    handler = load_handler()
    preflight = call(handler, {"action": "preflight", "timeout_seconds": 15})
    if not preflight.get("ready"):
        print(
            json.dumps(
                {
                    "bridge_ready": False,
                    "preflight": preflight,
                    "fix": "bash .cursor/skills/portfolio-browser/scripts/preflight.sh",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    result = call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 180 if with_checkout else 90,
            "actions": load_page_diag().wrap_actions(steps),
        },
    )
    page_diag = load_page_diag().extract_diag(result)

    final_url = result.get("final_url") or ""
    _, expect_return = AUDIENCE[app]
    if with_checkout and app == "buyer":
        order_ok = any(
            (step.get("value") or step.get("result") or {}).get("ok")
            for step in result.get("results", [])
            if step.get("type") == "evaluate"
            and isinstance(step.get("value") or step.get("result"), dict)
        )
        if not order_ok and "/orders/" not in final_url:
            print(json.dumps({"error": "Buyer checkout did not land on order", "final_url": final_url, "page_diag": page_diag}, indent=2), file=sys.stderr)
            return 1
    elif expect_return not in final_url:
        print(json.dumps({"error": "SSO did not land on expected app", "final_url": final_url, "page_diag": page_diag}, indent=2), file=sys.stderr)
        return 1

    out = {
        "bridge_ready": True,
        "app": app,
        "wallet_mode": "dev_burner" if use_burner else "phantom",
        "login_url": login,
        "final_url": final_url,
        "page_diag": page_diag,
        "results": result.get("results", [])[-2:],
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if page_diag.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
