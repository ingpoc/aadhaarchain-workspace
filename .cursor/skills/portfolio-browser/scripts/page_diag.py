#!/usr/bin/env python3
"""Compact page diagnostics for Hermes portfolio browser work.

Merges three signals agents need on every page:
  1. UI — page_context (url/title/headings/buttons)
  2. Console — injected console + failed fetch capture
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

# Install as early as possible after each goto. Survives same-document work;
# re-run after every navigation.
INSTALL_CONSOLE_JS = """
(() => {
  if (window.__acDiag && window.__acDiag.v === 2) {
    return { already: true, count: window.__acDiag.events.length };
  }
  const events = [];
  const push = (level, args) => {
    try {
      const msg = args.map((a) => {
        if (typeof a === 'string') return a;
        if (a instanceof Error) return a.stack || a.message;
        try { return JSON.stringify(a); } catch (_) { return String(a); }
      }).join(' ').slice(0, 500);
      events.push({ t: Date.now(), level, msg });
      if (events.length > 80) events.shift();
    } catch (_) {}
  };
  ['error', 'warn'].forEach((level) => {
    const orig = console[level].bind(console);
    console[level] = (...args) => { push(level, args); orig(...args); };
  });
  window.addEventListener('error', (e) => {
    push('error', [e.message || 'window.error', e.filename || '', e.lineno || '']);
  });
  window.addEventListener('unhandledrejection', (e) => {
    const r = e.reason;
    push('error', ['unhandledrejection', r && (r.stack || r.message || String(r))]);
  });
  const wrapFetch = (orig) => async (...args) => {
    const input = args[0];
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    try {
      const res = await orig(...args);
      if (!res.ok) push('error', [`fetch ${res.status}`, url.slice(0, 180)]);
      return res;
    } catch (err) {
      push('error', ['fetch failed', url.slice(0, 180), err && err.message]);
      throw err;
    }
  };
  if (window.fetch) window.fetch = wrapFetch(window.fetch.bind(window));
  window.__acDiag = { v: 2, events };
  return { installed: true, count: 0 };
})()
"""

DUMP_CONSOLE_JS = """
(() => {
  const d = window.__acDiag;
  if (!d) return { installed: false, errors: [], warns: [], total: 0 };
  const errors = d.events.filter((e) => e.level === 'error').slice(-12);
  const warns = d.events.filter((e) => e.level === 'warn').slice(-6);
  return {
    installed: true,
    total: d.events.length,
    errors: errors.map((e) => e.msg),
    warns: warns.map((e) => e.msg),
  };
})()
"""

ERROR_LINE = re.compile(
    r"(error|exception|traceback|failed|ECONNREFUSED|TypeError|ReferenceError|Unhandled)",
    re.I,
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
    return [{"type": "evaluate", "expression": INSTALL_CONSOLE_JS}]


def dump_actions() -> list[dict[str, Any]]:
    return [
        {"type": "page_context"},
        {"type": "evaluate", "expression": DUMP_CONSOLE_JS},
    ]


def wrap_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Inject console install after every goto; dump UI+console at end."""
    out: list[dict[str, Any]] = []
    for action in actions:
        out.append(action)
        if action.get("type") == "goto":
            out.extend(install_actions())
            # Give page scripts a beat so early errors land in the buffer.
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
            lines = path.read_text(errors="replace").splitlines()[-200:]
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
    console: dict[str, Any] = {"installed": False, "errors": [], "warns": [], "total": 0}
    for step in result.get("results", []):
        if step.get("type") == "page_context":
            ui = {
                "url": step.get("url"),
                "title": step.get("title"),
                "headings": [h.get("text") for h in (step.get("headings") or [])[:5]],
                "buttons": (step.get("buttons") or [])[:10],
            }
        if step.get("type") == "evaluate":
            value = step.get("result") if "result" in step else step.get("value")
            if isinstance(value, dict) and ("errors" in value or "installed" in value):
                if "errors" in value or "warns" in value:
                    console = value
    backend = backend_errors()
    issues = []
    for msg in console.get("errors") or []:
        issues.append({"source": "console", "level": "error", "msg": msg})
    for msg in console.get("warns") or []:
        issues.append({"source": "console", "level": "warn", "msg": msg})
    for hit in backend:
        issues.append({"source": "backend", "level": "error", "msg": f"{hit['log']}: {hit['line']}"})
    return {
        "ok": len([i for i in issues if i["level"] == "error"]) == 0,
        "ui": ui,
        "console": {
            "installed": bool(console.get("installed")),
            "total": console.get("total", 0),
            "errors": (console.get("errors") or [])[:8],
            "warns": (console.get("warns") or [])[:4],
        },
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
    actions.extend(install_actions())
    actions.append({"type": "wait", "ms": 800})
    # Nudge a known failing pattern into the buffer if page already errored earlier:
    # re-read auth/me so fetch failures show up.
    actions.append(
        {
            "type": "evaluate",
            "expression": """
(async () => {
  try {
    const r = await fetch('http://127.0.0.1:43101/api/auth/me', { credentials: 'include' });
    return { status: r.status };
  } catch (e) {
    return { error: String(e && e.message || e) };
  }
})()
""",
        }
    )
    actions.append({"type": "wait", "ms": 300})
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
