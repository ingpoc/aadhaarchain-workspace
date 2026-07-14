#!/usr/bin/env python3
"""Demo principal SSO via gateway /api/auth/demo-continue (no wallet).

Usage:
  python3 scripts/hermes_demo_sso.py seller
  python3 scripts/hermes_demo_sso.py buyer
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
PAGE_DIAG = ROOT / ".cursor/skills/portfolio-browser/scripts/page_diag.py"
GATEWAY = "http://127.0.0.1:43101"


def load_page_diag():
    spec = importlib.util.spec_from_file_location("portfolio_page_diag", PAGE_DIAG)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PAGE_DIAG}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="portfolio-demo-sso")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def demo_login_url(app: str) -> str:
    aud, return_url = AUDIENCE[app]
    encoded = urllib.parse.quote(return_url, safe="")
    return f"{GATEWAY}/api/auth/demo-continue?aud={aud}&return={encoded}&display_name=Demo+User"


def main() -> int:
    app = (sys.argv[1] if len(sys.argv) > 1 else "seller").lower()
    if app not in AUDIENCE:
        print(f"Unknown app {app!r}. Use: buyer | seller", file=sys.stderr)
        return 2

    login = demo_login_url(app)
    session = f"agentguard-demo-sso-{app}"
    _, expect_return = AUDIENCE[app]
    steps = [
        {"type": "goto", "url": login},
        {"type": "wait", "ms": 2500},
        {"type": "wait_for_url_change", "from_url": login, "timeout": 20000},
        {"type": "page_context"},
        # Hermes evaluation is intentionally read-only; verify the cookie-bound
        # principal by visiting the session endpoint rather than calling fetch
        # inside a debug expression.
        {"type": "goto", "url": f"{GATEWAY}/api/auth/me"},
        {"type": "wait", "ms": 500},
        {"type": "text"},
        {"type": "goto", "url": expect_return},
        {"type": "wait", "ms": 800},
        {"type": "page_context"},
    ]

    handler = load_handler()
    # Bridge preflight inspects the *active* tab. chrome:// / error pages fail
    # injection checks even when WIP sock is healthy. Recover via session goto;
    # do not re-preflight the stuck active tab — SSO run uses use_selected_tab=False.
    try:
        preflight = call(handler, {"action": "preflight", "timeout_seconds": 15})
        if not preflight.get("ready"):
            print(json.dumps({"bridge_ready": False, "preflight": preflight}, indent=2), file=sys.stderr)
            return 1
    except RuntimeError as exc:
        msg = str(exc)
        if "error page" in msg.lower() or "does not allow content-script" in msg.lower():
            print(json.dumps({"bridge_preflight_skip": msg}), file=sys.stderr)
            call(
                handler,
                {
                    "action": "run",
                    "session_name": session,
                    "use_selected_tab": False,
                    "timeout_seconds": 30,
                    "actions": [{"type": "goto", "url": expect_return}, {"type": "wait", "ms": 800}],
                },
            )
        else:
            raise

    try:
        result = call(
            handler,
            {
                "action": "run",
                "session_name": session,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": load_page_diag().wrap_actions(steps),
            },
        )
    finally:
        try:
            call(handler, {"action": "closeout", "timeout_seconds": 20, "keep_open": True})
        except RuntimeError:
            pass
    page_diag = load_page_diag().extract_diag(result)
    final_url = result.get("final_url") or ""

    me_ok = any(
        "principal_id" in (step.get("text") or "")
        and "principal:demo:" in (step.get("text") or "")
        for step in result.get("results", [])
        if step.get("type") == "text"
    )
    if not me_ok or expect_return.split("/")[2] not in final_url and expect_return not in final_url:
        # Host check: path presence is enough (43102/search etc.)
        landed = expect_return.rstrip("/") in final_url.rstrip("/") or any(
            part in final_url for part in ("43102", "43103") if str(AUDIENCE[app][1]).find(part) >= 0
        )
        if not me_ok or not landed:
            print(
                json.dumps(
                    {
                        "error": "Demo SSO did not establish principal session",
                        "final_url": final_url,
                        "me_ok": me_ok,
                        "page_diag": page_diag,
                    },
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 1

    print(
        json.dumps(
            {
                "bridge_ready": True,
                "app": app,
                "auth_mode": "demo_continue",
                "login_url": login,
                "final_url": final_url,
                "page_diag": page_diag,
            },
            indent=2,
            default=str,
        )
    )
    return 0 if page_diag.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
