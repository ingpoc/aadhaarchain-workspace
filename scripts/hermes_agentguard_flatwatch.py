#!/usr/bin/env python3
"""Hermes AgentGuard FlatWatch lane — dual-control 2-of-2 + replay reject.

API asserts run in-process (avoids Vite CORS). Hermes loads FlatWatch web for UI evidence.

Prerequisites: stack up; WIP Hermes bridge; FlatWatch :43104/:43105.

Usage:
  python3 scripts/hermes_agentguard_flatwatch.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.error
import urllib.request

SESSION = "agentguard-flatwatch"
FLATWATCH_WEB = "http://127.0.0.1:43105/"
FLATWATCH_API = "http://127.0.0.1:43104"

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _json_request(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode() if exc.fp else ""
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError:
            payload = {"detail": raw}
        return exc.code, payload


def dual_control_api() -> dict:
    create_status, created = _json_request(
        "POST",
        f"{FLATWATCH_API}/api/dual-control/proposals",
        {
            "action": "payment_correction",
            "resource_id": "fw-agentguard-demo",
            "created_by": "ops-a",
            "amount_inr": 2500,
            "note": "Portfolio dual-control validation (PII-free)",
        },
    )
    proposal_id = (created.get("proposal") or {}).get("proposal_id")
    if not proposal_id:
        return {"ok": False, "reason": "no_proposal", "create_status": create_status, "created": created}

    first_status, first_body = _json_request(
        "POST",
        f"{FLATWATCH_API}/api/dual-control/proposals/{proposal_id}/approve",
        {"approver": "approver-1"},
    )
    second_status, second_body = _json_request(
        "POST",
        f"{FLATWATCH_API}/api/dual-control/proposals/{proposal_id}/approve",
        {"approver": "approver-2"},
    )
    replay_status, _ = _json_request(
        "POST",
        f"{FLATWATCH_API}/api/dual-control/proposals/{proposal_id}/approve",
        {"approver": "approver-1"},
    )
    get_status, get_body = _json_request(
        "GET",
        f"{FLATWATCH_API}/api/dual-control/proposals/{proposal_id}",
    )
    proposal = get_body.get("proposal") or {}
    ok = (
        create_status == 200
        and first_status == 200
        and second_status == 200
        and replay_status == 409
        and proposal.get("status") == "approved"
        and len(proposal.get("approvals") or []) >= 2
    )
    return {
        "ok": ok,
        "create_status": create_status,
        "first_status": first_status,
        "first_approvals": len((first_body.get("proposal") or {}).get("approvals") or []),
        "second_status": second_status,
        "second_status_label": (second_body.get("proposal") or {}).get("status"),
        "replay_status": replay_status,
        "get_status": get_status,
        "final_status": proposal.get("status"),
        "approvals": proposal.get("approvals"),
        "proposal_id": proposal_id,
    }


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
    raw = handler._handle_hermes_chrome_browser(payload, task_id="agentguard-flatwatch")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def build_steps() -> list[dict]:
    return [
        {"type": "goto", "url": FLATWATCH_WEB},
        {"type": "wait", "ms": 3000},
        {
            "type": "evaluate",
            "expression": "({ href: location.href, title: document.title, ready: document.readyState })",
        },
        {"type": "page_context"},
    ]


def assess(*, api: dict, hermes: dict) -> dict:
    page = None
    for step in hermes.get("results", []):
        if step.get("type") != "evaluate":
            continue
        value = step.get("value") or step.get("result")
        if isinstance(value, dict) and value.get("href"):
            page = value
            break
    page_ok = bool(page and "43105" in str(page.get("href", "")))
    success = bool(api.get("ok") and page_ok)
    return {
        "success": success,
        "checks": {
            "proposal_created": api.get("create_status") == 200,
            "two_approvers": api.get("final_status") == "approved",
            "replay_rejected": api.get("replay_status") == 409,
            "flatwatch_page": page_ok,
        },
        "api": api,
        "page": page,
        "final_url": hermes.get("final_url"),
    }


def main() -> int:
    api = dual_control_api()
    handler = load_handler()
    hermes = hermes_call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": build_steps(),
        },
    )
    out = assess(api=api, hermes=hermes)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
