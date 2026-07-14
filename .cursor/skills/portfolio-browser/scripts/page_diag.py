#!/usr/bin/env python3
"""Compact page diagnostics for Hermes portfolio browser work.

Merges three signals agents need on every page:
  1. UI — page_context (url/title/headings/buttons)
  2. Console/network — native Hermes DevTools diagnostics
  3. Backend — recent error lines from portfolio service logs

Usage:
  python3 .cursor/skills/portfolio-browser/scripts/page_diag.py
  python3 .cursor/skills/portfolio-browser/scripts/page_diag.py --url http://127.0.0.1:43100/verify
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[4]
LOG_DIR = ROOT / "logs"
LOG_FILES = (
    "aadhaar-gateway.log",
    "aadhaar-frontend.log",
    "ondc-buyer.log",
    "ondc-seller.log",
    "flatwatch-backend.log",
)

ERROR_LINE = re.compile(
    r"(error|exception|traceback|failed|ECONNREFUSED|TypeError|ReferenceError|Unhandled)",
    re.I,
)

IGNORED_BROWSER_WARNINGS = (
    "MaxListenersExceededWarning",
    'ObjectMultiplex - orphaned data for stream "app-init-liveness"',
    'ObjectMultiplex - orphaned data for stream "background-liveness"',
)


def load_handler():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from wip_hermes import load_handler as _load

    return _load()


def hermes_call(handler, payload: dict) -> dict:
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(payload, task_id="portfolio-page-diag")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def install_actions() -> list[dict[str, Any]]:
    """Enable native network capture without mutating application globals."""
    return [{"type": "network_watch", "clear": True}]


def dump_actions() -> list[dict[str, Any]]:
    return [
        {"type": "page_context"},
        {"type": "console_tail", "levels": ["error", "warn"], "limit": 12},
        {"type": "network_summary"},
    ]


def wrap_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Capture native diagnostics around navigation and dump them at the end."""
    out: list[dict[str, Any]] = []
    for action in actions:
        if action.get("type") == "goto":
            out.extend(install_actions())
        out.append(action)
        if action.get("type") == "goto":
            # Give page scripts a beat so early errors land in native buffers.
            out.append({"type": "wait", "ms": 400})
    out.extend(dump_actions())
    return out


def backend_errors(*, max_per_file: int = 4, max_total: int = 12) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for name in LOG_FILES:
        path = LOG_DIR / name
        if not path.exists():
            continue
        try:
            lines = path.read_text(errors="replace").splitlines()[-80:]
        except OSError:
            continue
        file_hits = []
        for line in lines:
            if ERROR_LINE.search(line) and not re.search(r"\b200 OK\b", line):
                file_hits.append(line.strip()[:240])
        for line in file_hits[-max_per_file:]:
            hits.append({"log": name, "line": line})
            if len(hits) >= max_total:
                return hits
    return hits


def extract_diag(result: dict) -> dict[str, Any]:
    ui: dict[str, Any] = {}
    console: dict[str, Any] = {"installed": True, "errors": [], "warns": [], "total": 0}
    network: dict[str, Any] = {}
    for step in result.get("results", []):
        if step.get("type") == "page_context":
            ui = {
                "url": step.get("url"),
                "title": step.get("title"),
                "headings": [h.get("text") for h in (step.get("headings") or [])[:5]],
                "buttons": (step.get("buttons") or [])[:10],
            }
        if step.get("type") == "console_tail":
            entries = step.get("entries") or step.get("messages") or step.get("result") or []
            if isinstance(entries, dict):
                entries = entries.get("entries") or entries.get("messages") or []
            if not isinstance(entries, list):
                entries = []
            errors: list[str] = []
            warns: list[str] = []
            for entry in entries:
                if isinstance(entry, str):
                    errors.append(entry)
                    continue
                if not isinstance(entry, dict):
                    continue
                level = str(entry.get("level") or entry.get("type") or "error").lower()
                message = str(entry.get("message") or entry.get("text") or entry.get("value") or entry)[:500]
                if any(ignored in message for ignored in IGNORED_BROWSER_WARNINGS):
                    continue
                (warns if level == "warn" else errors).append(message)
            console = {"installed": True, "errors": errors, "warns": warns, "total": len(entries)}
        if step.get("type") == "network_summary":
            value = step.get("result") if "result" in step else step.get("value")
            network = value if isinstance(value, dict) else step
    backend = backend_errors()
    issues = []
    for msg in console.get("errors") or []:
        issues.append({"source": "console", "level": "error", "msg": msg})
    for msg in console.get("warns") or []:
        issues.append({"source": "console", "level": "warn", "msg": msg})
    network_errors = int(network.get("error_count") or network.get("errors") or 0)
    if network_errors:
        issues.append(
            {
                "source": "network",
                "level": "error",
                "msg": str(network.get("last_error") or f"{network_errors} request errors"),
            }
        )
    # The log tail can contain failures from an earlier run. Keep it available
    # for diagnosis, but let current browser console/network evidence own the
    # pass/fail result.
    for hit in backend:
        issues.append({"source": "backend", "level": "context", "msg": f"{hit['log']}: {hit['line']}"})
    return {
        "ok": not any(i["level"] == "error" for i in issues),
        "ui": ui,
        "console": {
            "installed": bool(console.get("installed")),
            "total": console.get("total", 0),
            "errors": (console.get("errors") or [])[:8],
            "warns": (console.get("warns") or [])[:4],
        },
        "network": network,
        "backend": backend[:8],
        "issues": issues[:16],
        "final_url": result.get("final_url"),
    }


def collect(*, url: str | None = None, session: str = "portfolio-page-diag") -> dict[str, Any]:
    handler = load_handler()
    actions: list[dict[str, Any]] = []
    if url:
        actions.append({"type": "goto", "url": url})
        actions.append({"type": "wait", "ms": 1200})
    if not url:
        actions.extend(install_actions())
    actions.append({"type": "wait", "ms": 800})
    actions.extend(dump_actions())
    result = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": 45,
            "actions": actions,
        },
    )
    return extract_diag(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact Hermes page diagnostics")
    parser.add_argument("--url", help="Navigate here before collecting diag")
    parser.add_argument("--session", default="portfolio-page-diag")
    args = parser.parse_args()
    try:
        out = collect(url=args.url, session=args.session)
    except Exception as exc:  # noqa: BLE001 — surface bridge failures compactly
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
