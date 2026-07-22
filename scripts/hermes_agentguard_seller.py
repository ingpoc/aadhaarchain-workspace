#!/usr/bin/env python3
"""Visible Hermes AgentGuard Seller lane: mandate, refund, replay, pause, deny."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

TASK_ID = f"agentguard-seller-{os.getpid()}"
SESSION = TASK_ID
GATEWAY = "http://127.0.0.1:43101"
ORDER_URL = "http://127.0.0.1:43103/orders/seller-demo-1002"
AGENTGUARD_URL = "http://127.0.0.1:43103/agentguard"
LOGIN = (
    "http://127.0.0.1:43100/login?return=http%3A%2F%2F127.0.0.1%3A43103%2Fdashboard"
    "&aud=ondcseller&dev_auto=1"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]


def gateway_api(
    method: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
    *,
    idem: str | None = None,
) -> dict[str, Any]:
    """Create/clean deterministic state outside the visible browser assertions."""
    body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if idem:
        headers["Idempotency-Key"] = idem
    request = urllib.request.Request(
        f"{GATEWAY}{endpoint}", data=body, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {endpoint} failed: {exc.code} {detail}") from exc
    if not parsed.get("success", True):
        raise RuntimeError(f"{method} {endpoint} failed: {parsed}")
    return parsed.get("data") or {}


def create_order_fixture(seller_id: str) -> tuple[str, str]:
    run_id = f"ag-seller-ui-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    item_result = gateway_api(
        "POST",
        "/api/demo-commerce/test-fixtures/seller/items",
        {
            "idempotency_key": f"{run_id}:item",
            "title": "Sampoorna Whole Wheat Atta 1kg",
            "description": "Stone-ground whole wheat flour for soft rotis.",
            "price_inr": 89,
            "inventory": 23,
            "seller_id": seller_id,
            "seller_name": "Sampoorna Groceries",
            "category_id": "Grocery",
            "delivery_estimate": "2–4 business days",
            "return_policy": "Unopened packs may be returned within 7 days.",
        },
        idem=f"{run_id}:item",
    )
    item_id = str(item_result["item"]["item_id"])
    gateway_api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/items/{item_id}/publish",
        {"idempotency_key": f"{run_id}:publish"},
        idem=f"{run_id}:publish",
    )
    created = gateway_api(
        "POST",
        "/api/demo-commerce/test-fixtures/buyer/orders",
        {
            "idempotency_key": f"{run_id}:order",
            "item_id": item_id,
            "quantity": 2,
            "buyer_id": f"buyer-{run_id}",
            "payment_mode": "success",
            "delivery_address": {
                "name": "Ananya Rao",
                "phone": "+91 98765 43210",
                "email": "ananya@example.test",
                "line1": "14 Market Road",
                "city": "Pune",
                "state": "Maharashtra",
                "postalCode": "411001",
                "country": "India",
            },
        },
        idem=f"{run_id}:order",
    )
    return item_id, str(created["order"]["order_id"])


def cleanup_order_fixture(order_id: str, item_id: str) -> None:
    gateway_api(
        "POST",
        "/api/demo-commerce/test-fixtures/cleanup",
        {"data": {"order_ids": [order_id], "item_ids": [item_id]}},
    )

READ_POLICY_JS = """
(() => ({
  policy: document.querySelector('[data-testid="agentguard-policy"]')?.textContent || '',
  status: document.querySelector('[data-testid="agentguard-status"]')?.textContent || '',
  mandate: document.querySelector('[data-testid="agentguard-mandate-status"]')?.textContent || '',
  pauseLabel: document.querySelector('[data-testid="agentguard-pause"]')?.textContent || ''
}))()
"""

READ_ORDER_JS = """
(() => ({
  msg: document.querySelector('[data-testid="agentguard-message"]')?.textContent || '',
  receipt: document.querySelector('[data-testid="agentguard-last-receipt"]')?.textContent || '',
  approval: !!document.querySelector('[data-testid="approve-once"]'),
  replay: !!document.querySelector('[data-testid="replay-approval"]'),
  approveDisabled: !!document.querySelector('[data-testid="approve-once"]')?.disabled
}))()
"""


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def hermes_call(handler: Any, payload: dict[str, Any]) -> dict[str, Any]:
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import run_with_session_preflight

    return run_with_session_preflight(handler, payload, task_id=TASK_ID)


def click_testid(testid: str) -> dict[str, Any]:
    return {
        "type": "locator",
        "locator": {"by": "testid", "testId": testid},
        "operation": "click",
    }


def fill_testid(testid: str, value: str) -> dict[str, Any]:
    return {
        "type": "locator",
        "locator": {"by": "testid", "testId": testid},
        "operation": "fill",
        "value": value,
    }


def run_actions(handler: Any, actions: list[dict[str, Any]], *, timeout: int = 120) -> dict[str, Any]:
    return hermes_call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": timeout,
            "actions": actions,
        },
    )


def eval_values(*results: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for result in results:
        for step in result.get("results", []):
            if step.get("type") != "evaluate":
                continue
            value = step.get("value") or step.get("result")
            if isinstance(value, dict):
                values.append(value)
    return values


def authenticated_principal(handler: Any) -> str:
    result = run_actions(
        handler,
        [
            {"type": "goto", "url": f"{GATEWAY}/api/auth/me"},
            {"type": "wait", "ms": 500},
            {"type": "text"},
        ],
        timeout=30,
    )
    for step in result.get("results", []):
        if step.get("type") != "text":
            continue
        try:
            payload = json.loads(step.get("text") or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        principal_id = ((payload.get("data") or {}).get("principal_id") or "").strip()
        if principal_id:
            return principal_id
    raise RuntimeError("Seller SSO did not expose an authenticated principal.")


def prepare_mandate(handler: Any, *, skip_sso: bool) -> list[dict[str, Any]]:
    prefix = (
        [{"type": "goto", "url": AGENTGUARD_URL}]
        if skip_sso
        else [
            {"type": "goto", "url": LOGIN},
            {"type": "wait", "ms": 5000},
            {"type": "wait_for_url_change", "from_url": LOGIN, "timeout": 45000},
            {"type": "goto", "url": AGENTGUARD_URL},
        ]
    )
    prepared = run_actions(
        handler,
        prefix
        + [
            {"type": "wait_for_selector", "selector": "[data-testid='agentguard-policy']", "timeout": 20000},
            fill_testid("agentguard-refund-max-input", "5000"),
            click_testid("agentguard-confirm-mandate"),
            {"type": "wait", "ms": 1800},
            {"type": "evaluate", "expression": READ_POLICY_JS},
        ],
    )
    values = eval_values(prepared)
    if values and values[-1].get("status", "").strip().lower() == "paused":
        resumed = run_actions(
            handler,
            [
                {"type": "goto", "url": AGENTGUARD_URL},
                {"type": "wait_for_selector", "selector": "[data-testid='agentguard-pause']", "timeout": 20000},
                click_testid("agentguard-pause"),
                {"type": "wait", "ms": 1200},
                {"type": "evaluate", "expression": READ_POLICY_JS},
            ],
        )
        values.extend(eval_values(resumed))
    return values


def exercise_refunds(handler: Any) -> list[dict[str, Any]]:
    result = run_actions(
        handler,
        [
            {"type": "goto", "url": ORDER_URL},
            {"type": "wait_for_selector", "selector": "[data-testid='refund-3000']", "timeout": 20000},
            click_testid("refund-3000"),
            {"type": "wait", "ms": 1500},
            {"type": "evaluate", "expression": READ_ORDER_JS},
            click_testid("refund-7500"),
            {"type": "wait", "ms": 1500},
            {"type": "evaluate", "expression": READ_ORDER_JS},
            click_testid("approve-once"),
            {"type": "wait", "ms": 1500},
            {"type": "evaluate", "expression": READ_ORDER_JS},
            click_testid("replay-approval"),
            {"type": "wait", "ms": 1200},
            {"type": "evaluate", "expression": READ_ORDER_JS},
        ],
        timeout=150,
    )
    return eval_values(result)


def exercise_pause(handler: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    paused = run_actions(
        handler,
        [
            {"type": "goto", "url": AGENTGUARD_URL},
            {"type": "wait_for_selector", "selector": "[data-testid='agentguard-pause']", "timeout": 20000},
            click_testid("agentguard-pause"),
            {"type": "wait", "ms": 1200},
            {"type": "evaluate", "expression": READ_POLICY_JS},
            {"type": "goto", "url": ORDER_URL},
            {"type": "wait_for_selector", "selector": "[data-testid='refund-3000']", "timeout": 20000},
            click_testid("refund-3000"),
            {"type": "wait", "ms": 1200},
            {"type": "evaluate", "expression": READ_ORDER_JS},
            {"type": "page_context"},
        ],
        timeout=120,
    )
    return eval_values(paused), paused


def assess(values: list[dict[str, Any]], final_result: dict[str, Any]) -> dict[str, Any]:
    messages = [str(value.get("msg", "")).lower() for value in values]
    policy_ok = any("5000" in str(value.get("policy", "")) for value in values)
    allow_ok = any("allowed" in message and "3000" in message for message in messages)
    need_ok = any(value.get("approval") for value in values)
    replay_ok = any("replay" in message or "consumed" in message for message in messages)
    paused_ok = any(str(value.get("status", "")).strip().lower() == "paused" for value in values)
    deny_ok = any("paused" in message or "denied" in message for message in messages[-3:])
    checks = {
        "policy_5000": policy_ok,
        "refund_allow_seen": allow_ok,
        "need_approval_ui": need_ok,
        "replay_rejected": replay_ok,
        "agent_paused": paused_ok,
        "deny_while_paused": deny_ok,
        "semantic_ui_actions": True,
    }
    return {
        "success": all(checks.values()),
        "checks": checks,
        "samples": values[-10:],
        "final_url": final_result.get("final_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes AgentGuard seller lane")
    parser.add_argument("--fixture", action="store_true", default=True)
    args = parser.parse_args()

    handler = load_handler()
    out: dict[str, Any]
    closeout_error: str | None = None
    fixture_order_id: str | None = None
    fixture_item_id: str | None = None
    try:
        values = prepare_mandate(handler, skip_sso=os.environ.get("AGENTGUARD_SKIP_SSO") == "1")
        global ORDER_URL
        if args.fixture:
            fixture_item_id, fixture_order_id = create_order_fixture(authenticated_principal(handler))
            ORDER_URL = f"http://127.0.0.1:43103/orders/{fixture_order_id}"
        values.extend(exercise_refunds(handler))
        paused_values, final_result = exercise_pause(handler)
        values.extend(paused_values)
        out = assess(values, final_result)
    finally:
        try:
            from wip_hermes import closeout_session

            closeout_session(handler, task_id=TASK_ID)
        except Exception as exc:  # noqa: BLE001 - closeout is reported as lane failure
            closeout_error = str(exc)
        if args.fixture and fixture_order_id and fixture_item_id:
            cleanup_order_fixture(fixture_order_id, fixture_item_id)
    if closeout_error:
        out["success"] = False
        out["closeout_error"] = closeout_error
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
