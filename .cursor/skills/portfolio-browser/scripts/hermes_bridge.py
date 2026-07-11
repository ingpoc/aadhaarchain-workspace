#!/usr/bin/env python3
"""Thin Hermes Chrome bridge wrapper for portfolio browser skill (WIP only)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
import urllib.parse

# Same directory import when run as script
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wip_hermes import ensure_wip_env, load_handler  # noqa: E402


def call(handler, args: dict) -> dict:
    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(args, task_id="portfolio-browser")
    return json.loads(raw) if isinstance(raw, str) else raw


LOGIN_TARGETS = {
    "buyer": ("ondcbuyer", "http://127.0.0.1:43102/search"),
    "seller": ("ondcseller", "http://127.0.0.1:43103/dashboard"),
}


def login_url(app: str, *, dev_auto: bool = False) -> str:
    aud, return_url = LOGIN_TARGETS[app]
    encoded = urllib.parse.quote(return_url, safe="")
    url = f"http://127.0.0.1:43100/login?return={encoded}&aud={aud}"
    if dev_auto:
        url += "&dev_auto=1"
    return url


def cmd_status(_: argparse.Namespace) -> int:
    handler = load_handler()
    data = call(handler, {"action": "status", "timeout_seconds": 10})
    print(json.dumps(data, indent=2))
    return 0 if data.get("ready") else 1


def cmd_run(args: argparse.Namespace) -> int:
    handler = load_handler()
    actions = json.loads(args.actions_json) if args.actions_json else [{"type": "page_context"}]
    diag_path = pathlib.Path(__file__).with_name("page_diag.py")
    spec = importlib.util.spec_from_file_location("portfolio_page_diag", diag_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {diag_path}")
    page_diag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(page_diag)
    actions = page_diag.wrap_actions(actions)
    payload = {
        "action": "run",
        "session_name": args.session or "portfolio-browser",
        "use_selected_tab": args.use_selected_tab,
        "timeout_seconds": args.timeout,
        "actions": actions,
    }
    if args.url:
        payload["url"] = args.url
    data = call(handler, payload)
    if not data.get("success"):
        print(json.dumps(data, indent=2), file=sys.stderr)
        return 1
    data["page_diag"] = page_diag.extract_diag(data)
    print(json.dumps(data, indent=2, default=str))
    return 0 if data["page_diag"].get("ok", True) else 2


def cmd_urls(args: argparse.Namespace) -> int:
    apps = ["buyer", "seller"] if args.app == "all" else [args.app]
    out = {}
    for app in apps:
        out[app] = {
            "smoke": LOGIN_TARGETS[app][1],
            "sso_phantom": login_url(app, dev_auto=False),
            "sso_dev_auto": login_url(app, dev_auto=True),
        }
    print(json.dumps(out, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Portfolio Hermes bridge helper (WIP only)")
    parser.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Bridge health")
    p_status.set_defaults(func=cmd_status)

    p_urls = sub.add_parser("urls", help="Canonical portfolio URLs")
    p_urls.add_argument("app", choices=["buyer", "seller", "all"], nargs="?", default="all")
    p_urls.set_defaults(func=cmd_urls)

    p_run = sub.add_parser("run", help="Run batched Hermes actions")
    p_run.add_argument("--url")
    p_run.add_argument("--session", default="portfolio-browser")
    p_run.add_argument("--timeout", type=int, default=60)
    p_run.add_argument("--use-selected-tab", action="store_true", default=False)
    p_run.add_argument(
        "actions_json",
        nargs="?",
        help='JSON array of actions, e.g. \'[{"type":"page_context"}]\'',
    )
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
