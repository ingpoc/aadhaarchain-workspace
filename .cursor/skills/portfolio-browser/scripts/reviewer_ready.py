#!/usr/bin/env python3
"""Prove a Hermes WIP lease can sustain a realistic blind-review handoff."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import tempfile
import time
import uuid
from collections.abc import Callable
from typing import Any

from wip_hermes import closeout_session, load_handler, run_with_session_preflight


class ToolingBlocked(RuntimeError):
    """Reviewer readiness failed before customer work should begin."""

    def __init__(self, message: str, diagnostics: dict[str, Any] | None = None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


def _decode(raw: Any) -> dict[str, Any]:
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(data, dict):
        raise ToolingBlocked("Hermes returned a non-object response")
    return data


def _call(handler: Any, payload: dict[str, Any], *, task_id: str) -> dict[str, Any]:
    return _decode(handler._handle_hermes_chrome_browser(payload, task_id=task_id))


def _screenshots(run: dict[str, Any]) -> list[str]:
    paths = [
        str(step.get("screenshot_path"))
        for step in run.get("results", [])
        if step.get("type") == "screenshot" and step.get("screenshot_path")
    ]
    missing = [path for path in paths if not pathlib.Path(path).is_file() or pathlib.Path(path).stat().st_size == 0]
    if not paths or missing:
        raise ToolingBlocked(
            "Hermes did not retain a non-empty screenshot for reviewer readiness",
            {"screenshots": paths, "missing_or_empty": missing},
        )
    return paths


def _validate_run(
    run: dict[str, Any],
    *,
    label: str,
    expected_url_prefix: str,
    expected_marker: str,
) -> dict[str, Any]:
    if not run.get("success"):
        raise ToolingBlocked(
            f"{label} Hermes call failed: {run.get('error') or 'unknown error'}",
            {"run": label, "error_code": run.get("error_code")},
        )
    identity = {key: run.get(key) for key in ("session_id", "window_id", "tab_id")}
    if any(value in (None, "") for value in identity.values()):
        raise ToolingBlocked(f"{label} did not return complete lease identity", identity)
    final_url = str(run.get("final_url") or "")
    if not final_url.startswith(expected_url_prefix):
        raise ToolingBlocked(
            f"{label} left the expected reviewer surface",
            {"expected_url_prefix": expected_url_prefix, "final_url": final_url},
        )
    semantic = json.dumps(run.get("results", []), ensure_ascii=False).lower()
    if expected_marker and expected_marker.lower() not in semantic:
        raise ToolingBlocked(
            f"{label} did not expose the expected signed-in marker",
            {"expected_marker": expected_marker, "final_url": final_url},
        )
    return {
        "identity": identity,
        "final_url": final_url,
        "screenshots": _screenshots(run),
    }


def _inventory(handler: Any, *, task_id: str) -> dict[str, Any]:
    return _call(
        handler,
        {"action": "sessions", "session_id": task_id, "timeout_seconds": 20},
        task_id=task_id,
    )


def probe_reviewer_readiness(
    handler: Any,
    *,
    url: str,
    expected_url_prefix: str,
    expected_marker: str,
    idle_seconds: float,
    timeout_seconds: int,
    task_id: str,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Run two bound visual reads across an idle interval and prove closeout."""
    first: dict[str, Any] | None = None
    second: dict[str, Any] | None = None
    inventory_before_closeout: dict[str, Any] = {}
    inventory_after_closeout: dict[str, Any] = {}
    closeout: dict[str, Any] = {}
    failure: ToolingBlocked | None = None

    try:
        initial = run_with_session_preflight(
            handler,
            {
                "action": "run",
                "session_name": task_id,
                "url": url,
                "timeout_seconds": timeout_seconds,
                "actions": [
                    {"type": "wait_for_selector", "selector": "main", "timeout": 10_000},
                    {"type": "page_context"},
                    {"type": "screenshot", "format": "png"},
                ],
            },
            task_id=task_id,
        )
        first = _validate_run(
            initial,
            label="initial read",
            expected_url_prefix=expected_url_prefix,
            expected_marker=expected_marker,
        )

        sleep_fn(idle_seconds)
        follow_up = run_with_session_preflight(
            handler,
            {
                "action": "run",
                "session_name": task_id,
                "timeout_seconds": timeout_seconds,
                "actions": [
                    {"type": "page_context"},
                    {"type": "screenshot", "format": "png"},
                ],
            },
            task_id=task_id,
        )
        second = _validate_run(
            follow_up,
            label="post-idle read",
            expected_url_prefix=expected_url_prefix,
            expected_marker=expected_marker,
        )
        if first["identity"] != second["identity"]:
            raise ToolingBlocked(
                "Hermes changed reviewer lease identity between calls",
                {"initial": first["identity"], "post_idle": second["identity"]},
            )
        inventory_before_closeout = _inventory(handler, task_id=task_id)
        owned = inventory_before_closeout.get("sessions") or []
        if not any(session.get("session_id") == task_id for session in owned):
            raise ToolingBlocked(
                "Owned reviewer lease is absent before closeout",
                {"inventory": inventory_before_closeout},
            )
    except ToolingBlocked as exc:
        failure = exc
    except Exception as exc:  # normalize helper/bridge failures
        failure = ToolingBlocked(str(exc))
    finally:
        try:
            closeout = closeout_session(handler, task_id=task_id)
        except Exception as exc:
            closeout = {"success": False, "error": str(exc)}
        try:
            inventory_after_closeout = _inventory(handler, task_id=task_id)
        except Exception as exc:
            inventory_after_closeout = {"success": False, "error": str(exc)}

    if not closeout.get("success"):
        failure = failure or ToolingBlocked("Reviewer lease closeout failed", {"closeout": closeout})
    remaining = inventory_after_closeout.get("sessions") or []
    if any(session.get("session_id") == task_id for session in remaining):
        failure = failure or ToolingBlocked(
            "Owned reviewer lease remains after closeout",
            {"inventory": inventory_after_closeout},
        )
    if failure:
        diagnostics = {
            **failure.diagnostics,
            "task_id": task_id,
            "closeout": closeout,
            "inventory_after_closeout": inventory_after_closeout,
        }
        removals = inventory_after_closeout.get("removals")
        if removals:
            diagnostics["lease_removals"] = removals
        raise ToolingBlocked(str(failure), diagnostics)

    return {
        "success": True,
        "status": "reviewer_ready",
        "task_id": task_id,
        "idle_seconds": idle_seconds,
        "identity": first["identity"] if first else None,
        "final_url": second["final_url"] if second else None,
        "screenshots": (first["screenshots"] if first else []) + (second["screenshots"] if second else []),
        "signed_in_marker": expected_marker,
        "closeout": closeout,
        "session_absent_after_closeout": True,
    }


class _FakeHandler:
    def __init__(self, screenshots: list[str], *, change_identity: bool = False):
        self.screenshots = screenshots
        self.change_identity = change_identity
        self.run_count = 0
        self.closed = False
        self.session_preflight_ready = False

    def _handle_hermes_chrome_browser(self, payload: dict[str, Any], *, task_id: str) -> str:
        action = payload.get("action")
        if action == "preflight":
            self.session_preflight_ready = True
            return json.dumps({"success": True, "session": {"lease_token": "private"}})
        if action == "run":
            if not self.session_preflight_ready:
                return json.dumps(
                    {
                        "success": False,
                        "error_code": "SESSION_PREFLIGHT_REQUIRED",
                        "error": "run requires preflight for this session",
                    }
                )
            self.session_preflight_ready = False
            self.run_count += 1
            return json.dumps(
                {
                    "success": True,
                    "session_id": task_id,
                    "window_id": 10,
                    "tab_id": 12 if self.change_identity and self.run_count == 2 else 11,
                    "final_url": "http://127.0.0.1:43103/dashboard",
                    "results": [
                        {"type": "page_context", "buttons": ["Sign out"]},
                        {"type": "screenshot", "screenshot_path": self.screenshots[self.run_count - 1]},
                    ],
                }
            )
        if action == "closeout":
            self.closed = True
            return json.dumps({"success": True, "session_id": task_id, "windows_closed": 1})
        if action == "sessions":
            sessions = [] if self.closed else [{"session_id": task_id, "window_id": 10, "tab_id": 11}]
            return json.dumps({"success": True, "sessions": sessions, "reaped": [], "removals": []})
        raise AssertionError(f"Unexpected fake action: {action}")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        paths = [str(pathlib.Path(directory) / f"shot-{index}.png") for index in (1, 2)]
        for path in paths:
            pathlib.Path(path).write_bytes(b"png")
        result = probe_reviewer_readiness(
            _FakeHandler(paths),
            url="http://127.0.0.1:43103/dashboard",
            expected_url_prefix="http://127.0.0.1:43103/dashboard",
            expected_marker="Sign out",
            idle_seconds=0,
            timeout_seconds=10,
            task_id="reviewer-ready-self-test",
            sleep_fn=lambda _seconds: None,
        )
        assert result["success"] is True
        assert result["session_absent_after_closeout"] is True

        failing_handler = _FakeHandler(paths, change_identity=True)
        try:
            probe_reviewer_readiness(
                failing_handler,
                url="http://127.0.0.1:43103/dashboard",
                expected_url_prefix="http://127.0.0.1:43103/dashboard",
                expected_marker="Sign out",
                idle_seconds=0,
                timeout_seconds=10,
                task_id="reviewer-ready-negative-self-test",
                sleep_fn=lambda _seconds: None,
            )
        except ToolingBlocked as exc:
            assert "changed reviewer lease identity" in str(exc)
            assert failing_handler.closed is True
        else:
            raise AssertionError("Identity change did not fail reviewer readiness")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Already-authenticated reviewer landing URL")
    parser.add_argument("--expected-url-prefix", help="Allowed final URL prefix; defaults to --url")
    parser.add_argument("--expected-marker", default="Sign out", help="Semantic signed-in marker")
    parser.add_argument("--idle-seconds", type=float, default=35.0, help="Idle interval between bound reads")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print(json.dumps({"success": True, "self_test": "passed"}))
        return 0
    if not args.url:
        raise SystemExit("--url is required unless --self-test is used")
    task_id = args.task_id or f"reviewer-ready-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    try:
        result = probe_reviewer_readiness(
            load_handler(),
            url=args.url,
            expected_url_prefix=args.expected_url_prefix or args.url,
            expected_marker=args.expected_marker,
            idle_seconds=max(0.0, args.idle_seconds),
            timeout_seconds=max(5, args.timeout_seconds),
            task_id=task_id,
        )
    except ToolingBlocked as exc:
        print(
            json.dumps(
                {
                    "success": False,
                    "status": "tooling_blocked",
                    "error": str(exc),
                    "diagnostics": exc.diagnostics,
                },
                indent=2,
            )
        )
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
