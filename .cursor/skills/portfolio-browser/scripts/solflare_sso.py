#!/usr/bin/env python3
"""Deterministic Solflare SSO: Hermes (page) + CUA/cliclick (sign popup).

Usage:
  python3 .cursor/skills/portfolio-browser/scripts/solflare_sso.py seller
  python3 .cursor/skills/portfolio-browser/scripts/solflare_sso.py buyer
  python3 .cursor/skills/portfolio-browser/scripts/solflare_sso.py --approve-only
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

APPS = {
    "seller": ("ondcseller", "http://127.0.0.1:43103/dashboard"),
    "buyer": ("ondcbuyer", "http://127.0.0.1:43102/search"),
}
SESSION = "solflare-sso"
CUA_SCRIPT = Path.home() / ".agents/skills/macos-cua/scripts/macos-cua.py"
AX_MAX_ELEMENTS = 80
POPUP_POLL_S = 12
POPUP_POLL_INTERVAL = 0.5


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hermes_run(handler, actions: list[dict], *, timeout: int = 60, selected: bool = False) -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": selected,
            "timeout_seconds": timeout,
            "actions": actions,
        },
        task_id="solflare-sso",
    )
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def login_url(app: str) -> str:
    aud, ret = APPS[app]
    from urllib.parse import quote

    return f"http://127.0.0.1:43100/login?return={quote(ret, safe='')}&aud={aud}"


def focus_solflare_window() -> None:
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Google Chrome" to activate',
            "-e",
            '''tell application "Google Chrome"
  repeat with w in windows
    if name of w is "Solflare" then set index of w to 1
  end repeat
end tell''',
        ],
        check=False,
    )


def find_solflare_window() -> tuple[int, int] | None:
    """Return (pid, window_id) for Chrome window titled Solflare."""
    try:
        from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionOnScreenOnly
    except ImportError:
        return None
    for w in CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID):
        if w.get("kCGWindowName") == "Solflare" and w.get("kCGWindowOwnerName") == "Google Chrome":
            pid = w.get("kCGWindowOwnerPID")
            wid = w.get("kCGWindowNumber")
            if pid and wid:
                return int(pid), int(wid)
    return None


def approve_cua(cua, pid: int, wid: int) -> bool:
    focus_solflare_window()
    time.sleep(0.35)
    snap = cua.snapshot(pid, wid, max_elements=AX_MAX_ELEMENTS, mode="ax")
    if "error" in snap:
        return False
    idx = cua.find_clickable_index(snap, "Approve")
    if idx is None:
        return False
    cua.click_with_retry(pid, wid, idx)
    return True


def approve_cliclick() -> bool:
    script = Path(__file__).resolve().parent / "approve_solflare.py"
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    return proc.returncode == 0


def wait_and_approve(cua) -> str:
    """Poll for Solflare popup; approve via CUA then cliclick fallback."""
    deadline = time.time() + POPUP_POLL_S
    while time.time() < deadline:
        found = find_solflare_window()
        if found:
            pid, wid = found
            if approve_cua(cua, pid, wid):
                return "cua"
            if approve_cliclick():
                return "cliclick"
            raise RuntimeError("Solflare popup found but Approve click failed")
        time.sleep(POPUP_POLL_INTERVAL)
    raise RuntimeError(f"Solflare sign popup did not appear within {POPUP_POLL_S}s")


def verify_signed_in(handler, app: str) -> dict:
    _, ret = APPS[app]
    data = hermes_run(
        handler,
        [
            {"type": "goto", "url": ret},
            {"type": "wait", "ms": 2000},
            {"type": "page_context"},
        ],
        selected=True,
    )
    ctx = data["results"][-1]
    buttons = ctx.get("buttons") or []
    if "Sign out" not in buttons:
        raise RuntimeError(f"SSO verify failed at {ctx.get('url')}; buttons={buttons[:6]}")
    return {"url": ctx.get("url"), "signed_in": True, "buttons": buttons[:6]}


def run_sso(app: str) -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from wip_hermes import load_handler

    handler = load_handler()
    cua = load_module("cua", CUA_SCRIPT)
    login = login_url(app)

    hermes_run(
        handler,
        [
            {"type": "goto", "url": login},
            {"type": "wait", "ms": 3000},
            {"type": "page_context"},
        ],
        selected=False,
    )

    ctx = hermes_run(handler, [{"type": "page_context"}], selected=True)["results"][-1]
    wallet_btn = next((b for b in (ctx.get("buttons") or []) if ".." in b), None)

    if wallet_btn:
        hermes_run(
            handler,
            [
                {"type": "click_text", "text": wallet_btn},
                {"type": "wait", "ms": 800},
                {"type": "click_text", "text": "Change wallet"},
                {"type": "wait", "ms": 1200},
                {"type": "click_text", "text": "Solflare"},
                {"type": "wait", "ms": 2000},
            ],
            selected=True,
        )
    else:
        hermes_run(
            handler,
            [
                {"type": "click_text", "text": "Select Wallet"},
                {"type": "wait", "ms": 1200},
                {"type": "click_text", "text": "Solflare"},
                {"type": "wait", "ms": 2000},
            ],
            selected=True,
        )

    hermes_run(
        handler,
        [{"type": "click_text", "text": "Sign in and continue"}, {"type": "wait", "ms": 500}],
        selected=True,
    )

    approve_method = wait_and_approve(cua)
    time.sleep(1.5)

    try:
        hermes_run(
            handler,
            [
                {"type": "wait_for_url_change", "from_url": login, "timeout": 15000},
                {"type": "page_context"},
            ],
            selected=True,
            timeout=25,
        )
    except RuntimeError:
        pass

    verify = verify_signed_in(handler, app)
    return {"app": app, "approve_method": approve_method, **verify}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Solflare SSO")
    parser.add_argument("app", nargs="?", choices=["seller", "buyer"], help="Portfolio app")
    parser.add_argument("--approve-only", action="store_true", help="Only approve open Solflare popup")
    args = parser.parse_args()

    if args.approve_only:
        cua = load_module("cua", CUA_SCRIPT)
        method = wait_and_approve(cua)
        print(json.dumps({"approve_method": method}))
        return 0

    if not args.app:
        parser.error("app required (seller|buyer) unless --approve-only")
    try:
        result = run_sso(args.app)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
