"""AadhaarChain portfolio → Hermes Chrome **WIP only** (never Codex live).

Window policy (operator-facing):
- One agent / one conversation → one leased Chrome window (`portfolio-browser`).
- Two concurrent agents → set distinct `HERMES_AGENT_ID` (or `PORTFOLIO_HERMES_MULTI_AGENT=1`
  with distinct task ids) → two windows.
- Do not invent a new session/task id per script step; that opens orphan windows.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
from typing import Any

WIP_ROOT = pathlib.Path(
    os.environ.get(
        "HERMES_CHROME_WIP_ROOT",
        "/Users/gurusharan/plugins/hermes-chrome-cursor-wip",
    )
)
WIP_TOOLS = WIP_ROOT / "plugin" / "hermes_chrome" / "tools.py"
WIP_SOCKET = WIP_ROOT / "run" / "chrome-bridge.sock"
WIP_SYNC = WIP_ROOT / "scripts" / "sync-wip.sh"

# Stable single-agent lease identity for this portfolio skill.
DEFAULT_PORTFOLIO_AGENT_ID = "portfolio-browser"


def ensure_wip_env() -> pathlib.Path:
    """Force WIP socket before importing tools.py (module reads env at import)."""
    if not WIP_TOOLS.is_file():
        raise RuntimeError(f"WIP Hermes tools missing: {WIP_TOOLS}")
    os.environ["HERMES_CHROME_BRIDGE_SOCKET"] = str(WIP_SOCKET)
    os.environ["HERMES_CHROME_WIP_ROOT"] = str(WIP_ROOT)
    return WIP_SOCKET


def load_handler():
    """Load WIP plugin/hermes_chrome/tools.py with WIP socket env set."""
    ensure_wip_env()
    spec = importlib.util.spec_from_file_location("hermes_chrome_wip_tools", WIP_TOOLS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load WIP Hermes plugin at {WIP_TOOLS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_agent_id(task_id: str | None, payload: dict[str, Any] | None = None) -> str:
    """Map portfolio calls onto one window unless multi-agent is explicit."""
    payload = payload or {}
    for key in ("session_id", "agent_id"):
        value = str(payload.get(key) or "").strip()
        if value:
            return value
    env = (
        os.environ.get("HERMES_AGENT_ID")
        or os.environ.get("PORTFOLIO_HERMES_AGENT_ID")
        or ""
    ).strip()
    if env:
        return env
    # Opt-in: each unique task_id gets its own window (true multi-agent).
    if os.environ.get("PORTFOLIO_HERMES_MULTI_AGENT", "").strip() == "1":
        raw = str(task_id or payload.get("session_name") or "").strip()
        return raw or DEFAULT_PORTFOLIO_AGENT_ID
    return DEFAULT_PORTFOLIO_AGENT_ID


def _parse(raw: Any) -> dict[str, Any]:
    data = json.loads(raw) if isinstance(raw, str) else raw
    return data if isinstance(data, dict) else {"success": False, "error": data}


def _has_lease(handler: Any, agent_id: str) -> bool:
    tokens = getattr(handler, "_LEASE_TOKENS", None)
    return isinstance(tokens, dict) and bool(tokens.get(agent_id))


def run_with_session_preflight(handler: Any, payload: dict[str, Any], *, task_id: str) -> dict[str, Any]:
    """Acquire/reuse the process-local Hermes lease, then run.

    Reuses the existing lease when this process already holds it — does not open
    a second window for the same agent id.
    """
    ensure_wip_env()
    agent_id = resolve_agent_id(task_id, payload)
    run_payload = dict(payload)
    run_payload.setdefault("session_name", agent_id)
    # Keep Hermes identity stable even when callers pass decorative session labels.
    run_payload["session_id"] = agent_id
    run_payload["agent_id"] = agent_id

    preflight_url = str(run_payload.get("url") or "").strip()
    if not preflight_url:
        preflight_url = next(
            (
                str(action.get("url") or "").strip()
                for action in run_payload.get("actions", [])
                if action.get("type") == "goto" and action.get("url")
            ),
            "",
        )

    if not _has_lease(handler, agent_id):
        if not preflight_url:
            preflight_url = "http://127.0.0.1:43102/search"
        preflight = _parse(
            handler._handle_hermes_chrome_browser(
                {
                    "action": "preflight",
                    "session_id": agent_id,
                    "agent_id": agent_id,
                    "session_name": str(run_payload.get("session_name") or agent_id),
                    "timeout_seconds": run_payload.get("timeout_seconds", 60),
                    "url": preflight_url,
                },
                task_id=agent_id,
            )
        )
        if not preflight.get("success"):
            raise RuntimeError(preflight.get("error") or preflight)

    data = _parse(handler._handle_hermes_chrome_browser(run_payload, task_id=agent_id))
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def closeout_session(handler: Any, *, task_id: str | None = None, agent_id: str | None = None) -> dict[str, Any]:
    """Release one lease while its process-local token is still available."""
    ensure_wip_env()
    resolved = (agent_id or resolve_agent_id(task_id, {})).strip() or DEFAULT_PORTFOLIO_AGENT_ID
    data = _parse(
        handler._handle_hermes_chrome_browser(
            {
                "action": "closeout",
                "session_id": resolved,
                "agent_id": resolved,
                "timeout_seconds": 20,
            },
            task_id=resolved,
        )
    )
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def list_sessions(handler: Any) -> list[dict[str, Any]]:
    ensure_wip_env()
    data = _parse(
        handler._handle_hermes_chrome_browser(
            {"action": "sessions", "timeout_seconds": 20},
            task_id=DEFAULT_PORTFOLIO_AGENT_ID,
        )
    )
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    sessions = data.get("sessions") or []
    return sessions if isinstance(sessions, list) else []


def closeout_all_sessions(
    handler: Any,
    *,
    leave_url: str = "http://127.0.0.1:43102/search",
) -> dict[str, Any]:
    """Close every active agent lease/window, reclaiming orphans when possible.

    Same-process tokens close immediately. Foreign/orphan leases are reclaimed via
    preflight (Hermes idle/stale reclaim) then closeout.
    """
    ensure_wip_env()
    closed: list[str] = []
    failed: list[dict[str, str]] = []
    sessions = list_sessions(handler)
    # Prefer closing leases this process owns first.
    tokens = getattr(handler, "_LEASE_TOKENS", {}) or {}
    owned_ids = [str(k) for k in tokens.keys()]
    other_ids = [
        str(s.get("session_id") or s.get("agent_id") or "")
        for s in sessions
        if str(s.get("session_id") or s.get("agent_id") or "")
        and str(s.get("session_id") or s.get("agent_id") or "") not in owned_ids
    ]

    for sid in owned_ids + other_ids:
        if not sid:
            continue
        try:
            if sid not in tokens:
                # Reclaim stale/orphan lease for this id, then close with new token.
                pre = _parse(
                    handler._handle_hermes_chrome_browser(
                        {
                            "action": "preflight",
                            "session_id": sid,
                            "agent_id": sid,
                            "session_name": sid,
                            "url": leave_url,
                            "timeout_seconds": 45,
                        },
                        task_id=sid,
                    )
                )
                if not pre.get("success"):
                    failed.append({"session_id": sid, "error": str(pre.get("error") or pre)})
                    continue
            out = closeout_session(handler, agent_id=sid)
            if out.get("success"):
                closed.append(sid)
            else:
                failed.append({"session_id": sid, "error": str(out.get("error") or out)})
        except Exception as exc:  # noqa: BLE001 — closeout must be best-effort
            failed.append({"session_id": sid, "error": str(exc)})

    remaining = []
    try:
        remaining = [
            str(s.get("session_id") or s.get("agent_id") or "")
            for s in list_sessions(handler)
            if s.get("session_id") or s.get("agent_id")
        ]
    except Exception as exc:  # noqa: BLE001
        failed.append({"session_id": "*", "error": f"relist failed: {exc}"})

    return {
        "success": len(remaining) == 0,
        "closed": closed,
        "failed": failed,
        "remaining": remaining,
        "leave_url": leave_url,
    }
