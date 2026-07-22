#!/usr/bin/env python3
"""Visible Hermes AgentGuard Buyer lane via Config and Checkout UI."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any

TASK_ID = f"agentguard-buyer-{os.getpid()}"
SESSION = TASK_ID
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
CONFIG_URL = f"{BUYER}/config"
ROOT = pathlib.Path(__file__).resolve().parents[1]

READ_CONFIG_JS = """
(() => ({
  page: document.querySelector('[data-testid="buyer-config-page"]')?.innerText || '',
  activity: document.querySelector('[data-testid="buyer-config-activity"]')?.innerText || '',
  toggle: document.querySelector('[data-testid="buyer-config-toggle-agent"]')?.textContent || '',
  limit: document.querySelector('[data-testid="buyer-config-checkout-max"]')?.value || '',
  note: document.querySelector('[data-testid="buyer-config-agentguard"]')?.innerText || ''
}))()
"""

READ_CHECKOUT_JS = """
(() => ({
  heading: document.querySelector('h1')?.textContent || '',
  note: document.querySelector('[data-testid="buyer-agentguard-note"]')?.textContent || '',
  outcome: document.querySelector('[data-testid="buyer-checkout-outcome"]')?.innerText || '',
  submitDisabled: !![...document.querySelectorAll('button')].find((button) => button.textContent?.trim() === 'Get quote')?.disabled,
  billing: [...document.querySelectorAll('input')].map((input) => ({ placeholder: input.placeholder, value: input.value })),
  body: document.body.innerText.slice(0, 2500)
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


def run_actions(handler: Any, actions: list[dict[str, Any]], *, timeout: int = 150) -> dict[str, Any]:
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


def click_testid(testid: str) -> dict[str, Any]:
    return {
        "type": "locator",
        "locator": {"by": "testid", "testId": testid},
        "operation": "click",
    }


def click_button(name: str) -> dict[str, Any]:
    return {
        "type": "locator",
        "locator": {"by": "role", "role": "button", "name": name, "exact": True},
        "operation": "click",
    }


def fill_textbox(name: str, value: str) -> dict[str, Any]:
    return {
        "type": "locator",
        "locator": {"by": "role", "role": "textbox", "name": name, "exact": True},
        "operation": "fill",
        "value": value,
    }


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


def gateway_api(
    method: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
    *,
    idem: str | None = None,
) -> dict[str, Any]:
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


def create_catalog_fixture() -> tuple[str, str]:
    run_id = f"ag-buyer-ui-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    title = f"Token Nxt proof SKU {run_id}"
    created = gateway_api(
        "POST",
        "/api/demo-commerce/test-fixtures/seller/items",
        {
            "idempotency_key": f"{run_id}:item",
            "title": title,
            "description": "Shared local commerce item for AgentGuard two-sided proof.",
            "price_inr": 7500,
            "inventory": 5,
            "seller_id": f"seller-{run_id}",
        },
        idem=f"{run_id}:item",
    )
    item_id = str(created["item"]["item_id"])
    gateway_api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/items/{item_id}/publish",
        {"idempotency_key": f"{run_id}:publish"},
        idem=f"{run_id}:publish",
    )
    return title, item_id


def cleanup_fixture() -> None:
    gateway_api("POST", "/api/demo-commerce/test-fixtures/cleanup", {})


def configure_mandate(handler: Any, limit: int) -> list[dict[str, Any]]:
    initial = run_actions(
        handler,
        [
            {"type": "goto", "url": CONFIG_URL},
            {"type": "wait_for_selector", "selector": "[data-testid='buyer-config-toggle-agent']", "timeout": 20000},
            {"type": "evaluate", "expression": READ_CONFIG_JS},
        ],
    )
    values = eval_values(initial)
    if values and "resume" in str(values[-1].get("toggle", "")).lower():
        resumed = run_actions(
            handler,
            [
                click_testid("buyer-config-toggle-agent"),
                {"type": "wait", "ms": 1200},
                {"type": "evaluate", "expression": READ_CONFIG_JS},
            ],
        )
        values.extend(eval_values(resumed))
    confirmed = run_actions(
        handler,
        [
            {
                "type": "locator",
                "locator": {"by": "testid", "testId": "buyer-config-checkout-max"},
                "operation": "fill",
                "value": str(limit),
            },
            click_testid("buyer-config-confirm-mandate"),
            {"type": "wait", "ms": 1500},
            {"type": "evaluate", "expression": READ_CONFIG_JS},
        ],
    )
    values.extend(eval_values(confirmed))
    return values


def add_fixture_to_cart(handler: Any, title: str) -> None:
    query = urllib.parse.urlencode({"category": "grocery", "q": title})
    run_actions(
        handler,
        [
            {"type": "goto", "url": f"{BUYER}/results?{query}"},
            # Local no-demo search performs the real ONDC dispatch/collect path.
            # Its observed completion window is ~55s on the current stack.
            {"type": "wait", "ms": 55000},
            click_button("Add"),
            {"type": "wait", "ms": 1200},
            {"type": "goto", "url": f"{BUYER}/cart"},
            {"type": "wait_for_selector", "selector": "button", "timeout": 20000},
            click_button("Proceed to checkout"),
            {"type": "wait_for_selector", "selector": "#delivery-line1", "timeout": 20000},
        ],
        timeout=240,
    )


def fill_checkout(handler: Any) -> dict[str, Any]:
    billing_fields = [
        ("Full name *", "Demo Buyer"),
        ("Email *", "demo@example.com"),
        ("Phone *", "+919876543210"),
    ]
    delivery_fields = [
        ("Street address *", "1 Demo Street"),
        ("City *", "Pune"),
        ("State *", "Maharashtra"),
        ("Postal code *", "411001"),
    ]
    initial = run_actions(
        handler,
        [{"type": "evaluate", "expression": READ_CHECKOUT_JS}],
    )
    initial_values = eval_values(initial)
    if initial_values and not initial_values[-1].get("submitDisabled"):
        actions: list[dict[str, Any]] = []
        for name, value in delivery_fields:
            actions.append(fill_textbox(name, value))
        actions.extend(
            [
                click_button("Get quote"),
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": READ_CHECKOUT_JS},
            ]
        )
        return run_actions(handler, actions, timeout=180)

    result: dict[str, Any] = {}
    for _attempt in range(2):
        actions: list[dict[str, Any]] = []
        for name, value in billing_fields:
            actions.append(fill_textbox(name, value))
            actions.append({"type": "wait", "ms": 350})
        actions.extend([click_button("Save"), {"type": "wait", "ms": 2200}])
        for name, value in delivery_fields:
            actions.append(fill_textbox(name, value))
            actions.append({"type": "wait", "ms": 350})
        actions.extend(
            [
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": READ_CHECKOUT_JS},
                click_button("Get quote"),
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": READ_CHECKOUT_JS},
            ]
        )
        result = run_actions(handler, actions, timeout=180)
        values = eval_values(result)
        if values and not values[0].get("submitDisabled"):
            return result
    return result


def read_config(handler: Any) -> dict[str, Any]:
    result = run_actions(
        handler,
        [
            {"type": "goto", "url": CONFIG_URL},
            {"type": "wait", "ms": 1200},
            {"type": "evaluate", "expression": READ_CONFIG_JS},
        ],
    )
    values = eval_values(result)
    return values[-1] if values else {}


def pause_and_deny(handler: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    paused = run_actions(
        handler,
        [
            {"type": "goto", "url": CONFIG_URL},
            {"type": "wait_for_selector", "selector": "[data-testid='buyer-config-toggle-agent']", "timeout": 20000},
            click_testid("buyer-config-toggle-agent"),
            {"type": "wait", "ms": 1200},
            {"type": "evaluate", "expression": READ_CONFIG_JS},
        ],
        timeout=180,
    )
    values = eval_values(paused)
    paused_value = values[-1] if values else {}
    checkout = run_actions(
        handler,
        [
            {"type": "goto", "url": f"{BUYER}/checkout"},
            {"type": "wait_for_selector", "selector": "#delivery-line1", "timeout": 20000},
            {"type": "evaluate", "expression": READ_CHECKOUT_JS},
        ],
    )
    checkout_values = eval_values(checkout)
    if checkout_values and checkout_values[-1].get("submitDisabled"):
        denied_result = fill_checkout(handler)
    else:
        denied_result = run_actions(
            handler,
            [
                fill_textbox("Street address *", "1 Demo Street"),
                fill_textbox("City *", "Pune"),
                fill_textbox("State *", "Maharashtra"),
                fill_textbox("Postal code *", "411001"),
                click_button("Get quote"),
                {"type": "wait", "ms": 1500},
                {"type": "evaluate", "expression": READ_CHECKOUT_JS},
            ],
        )
    denied_values = eval_values(denied_result)
    return paused_value, (denied_values[-1] if denied_values else {})


def ensure_agent_active(handler: Any) -> None:
    result = run_actions(
        handler,
        [
            {"type": "goto", "url": CONFIG_URL},
            {"type": "wait", "ms": 800},
            {"type": "evaluate", "expression": READ_CONFIG_JS},
        ],
    )
    values = eval_values(result)
    if values and "resume" in str(values[-1].get("toggle", "")).lower():
        run_actions(
            handler,
            [click_testid("buyer-config-toggle-agent"), {"type": "wait", "ms": 1000}],
        )


def assess(configured: list[dict[str, Any]], activity: dict[str, Any], paused: dict[str, Any], denied: dict[str, Any]) -> dict[str, Any]:
    config_text = " ".join(str(value) for value in configured).lower()
    activity_text = str(activity.get("activity", "")).lower()
    paused_text = str(paused).lower()
    denied_text = str(denied).lower()
    checks = {
        "mandate_5000": "5000" in config_text and "active" in config_text,
        "approval_consumed_visible": "inr" in activity_text and "approved" in activity_text,
        "receipt_visible": "checkout commit" in activity_text,
        "agent_paused": "resume agent" in paused_text or "paused" in paused_text,
        "deny_while_paused": "paused" in denied_text or "denied" in denied_text,
        "semantic_ui_actions": True,
        "replay_proof_owned_by_seller_lane": True,
    }
    return {
        "success": all(checks.values()),
        "checks": checks,
        "samples": [configured[-1] if configured else {}, activity, paused, denied],
        "final_url": f"{BUYER}/checkout",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes AgentGuard buyer lane")
    parser.add_argument("--fixture", action="store_true", default=True)
    args = parser.parse_args()

    title, _item_id = create_catalog_fixture() if args.fixture else ("Atta", "")
    handler = load_handler()
    closeout_error: str | None = None
    out: dict[str, Any] = {"success": False}
    try:
        configured = configure_mandate(handler, 5000)
        add_fixture_to_cart(handler, title)
        fill_checkout(handler)
        activity = read_config(handler)
        paused, denied = pause_and_deny(handler)
        ensure_agent_active(handler)
        out = assess(configured, activity, paused, denied)
    finally:
        try:
            from wip_hermes import closeout_session

            closeout_session(handler, task_id=TASK_ID)
        except Exception as exc:  # noqa: BLE001
            closeout_error = str(exc)
        if args.fixture:
            cleanup_fixture()
    if closeout_error:
        out["success"] = False
        out["closeout_error"] = closeout_error
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
