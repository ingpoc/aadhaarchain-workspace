#!/usr/bin/env python3
"""ONDC testing matrix with Hermes screenshots (claim → screenshot → Pass).

Saves evidence under .cursor/skills/ondc-testing/references/evidence/
Usage:
  python3 scripts/hermes_ondc_testing_matrix.py          # buyer+seller
  python3 scripts/hermes_ondc_testing_matrix.py buyer
  python3 scripts/hermes_ondc_testing_matrix.py seller
"""
from __future__ import annotations

import json
import argparse
import pathlib
import shutil
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
SELLER = "http://127.0.0.1:43103"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION = "ondc-testing-matrix"
TS = time.strftime("%Y%m%d-%H%M%S")
TRANSCRIPT_FILE = ROOT / "aadharchain/gateway/data/samantha-transcripts.jsonl"


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="ondc-matrix")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def post_gateway_json(path: str, body: dict) -> dict:
    """Create deterministic local commerce preconditions; operator actions still run through Samantha."""
    request = urllib.request.Request(
        f"{GATEWAY}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": str(body.get("idempotency_key") or f"matrix:{TS}"),
        },
        method="POST",
    )
    payload = json.loads(urllib.request.urlopen(request, timeout=15).read())
    if payload.get("success") is False:
        raise RuntimeError(payload.get("detail") or payload.get("message") or payload)
    return payload.get("data") or {}


def seed_seller_order_fixture() -> list[str]:
    """Seed two paid orders so accept-to-fulfil and reject are repeatable in one source-frozen run."""
    key = f"ondc-matrix:{TS}"
    created = post_gateway_json(
        "/api/demo-commerce/test-fixtures/seller/items",
        {
            "idempotency_key": f"{key}:item:create",
            "title": f"Matrix Order Item {TS[-6:]}",
            "description": "Local Samantha order-lifecycle fixture",
            "price_inr": 80,
            "inventory": 5,
            "seller_id": "demo-seller",
        },
    )
    item_id = str((created.get("item") or {}).get("item_id") or "")
    if not item_id:
        raise RuntimeError(f"Seller fixture item missing: {created}")
    post_gateway_json(
        f"/api/demo-commerce/test-fixtures/seller/items/{urllib.parse.quote(item_id)}/publish",
        {"idempotency_key": f"{key}:item:publish"},
    )
    order_ids = []
    for index in (1, 2):
        ordered = post_gateway_json(
            "/api/demo-commerce/test-fixtures/buyer/orders",
            {
                "idempotency_key": f"{key}:order:{index}",
                "item_id": item_id,
                "quantity": 1,
                "buyer_id": f"matrix-buyer-{index}",
                "payment_mode": "success",
            },
        )
        order_id = str((ordered.get("order") or {}).get("order_id") or "")
        if not order_id:
            raise RuntimeError(f"Seller fixture order missing: {ordered}")
        order_ids.append(order_id)
    return order_ids


def seed_buyer_checkout_fixture() -> tuple[str, str]:
    """Publish fresh low- and over-limit Atta items for exact checkout decisions."""
    key = f"ondc-matrix:{TS}:buyer"

    def publish(label: str, title: str, price_inr: int) -> None:
        created = post_gateway_json(
            "/api/demo-commerce/test-fixtures/seller/items",
            {
                "idempotency_key": f"{key}:{label}:create",
                "title": title,
                "description": "Fresh local Samantha checkout fixture",
                "price_inr": price_inr,
                "inventory": 20,
                "seller_id": "demo-seller",
            },
        )
        item_id = str((created.get("item") or {}).get("item_id") or "")
        if not item_id:
            raise RuntimeError(f"Buyer fixture item missing: {created}")
        post_gateway_json(
            f"/api/demo-commerce/test-fixtures/seller/items/{urllib.parse.quote(item_id)}/publish",
            {"idempotency_key": f"{key}:{label}:publish"},
        )

    checkout_title = f"Matrix Fresh Atta {TS[-6:]}"
    approval_title = f"Matrix Approval Atta {TS[-6:]}"
    publish("checkout", checkout_title, 89)
    publish("approval", approval_title, 25_000)
    return checkout_title, approval_title


def get_gateway_json(path: str) -> dict:
    payload = json.loads(urllib.request.urlopen(f"{GATEWAY}{path}", timeout=15).read())
    if payload.get("success") is False:
        raise RuntimeError(payload.get("detail") or payload.get("message") or payload)
    data = payload.get("data")
    return data if isinstance(data, dict) else payload


def runtime_backend_snapshot(role: str) -> dict:
    request = urllib.request.Request(
        f"{GATEWAY}/api/agent/runtime?app=ondc-{role}",
        headers={"X-User-Id": f"matrix-{role}"},
    )
    return json.loads(urllib.request.urlopen(request, timeout=15).read())


def backend_snapshot(*, runtime_role: str | None = None, catalog_query: str = "atta") -> dict:
    """Read the backend owners immediately after an operator query."""
    try:
        realtime = get_gateway_json("/api/realtime/status")
        ondc = get_gateway_json("/api/ondc/status")
        catalog = get_gateway_json(
            f"/api/demo-commerce/buyer/search?q={urllib.parse.quote_plus(catalog_query)}"
        )
        orders = get_gateway_json("/api/demo-commerce/test-fixtures/seller/orders")
        catalog_items = catalog.get("items") or []
        seller_orders = orders.get("orders") or []
        snapshot = {
            "ok": True,
            "realtime_configured": realtime.get("configured") is True,
            "ondc_enabled": ondc.get("enabled") is True,
            "catalog": [
                {
                    "item_id": item.get("item_id"),
                    "title": item.get("title"),
                    "price_inr": item.get("price_inr"),
                    "status": item.get("status"),
                }
                for item in catalog_items
                if isinstance(item, dict)
            ],
            "orders": [
                {
                    "order_id": order.get("order_id"),
                    "status": order.get("status"),
                    "updated_at": order.get("updated_at"),
                }
                for order in seller_orders
                if isinstance(order, dict)
            ],
            "order_count": len(seller_orders),
        }
        if runtime_role:
            snapshot["runtime"] = runtime_backend_snapshot(runtime_role)
        return snapshot
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def transcript_proof(role: str, ask: str, tools: list[str]) -> tuple[bool, str]:
    """Fail closed unless this exact operator turn reached the authenticated store."""
    for _ in range(5):
        events: list[dict] = []
        if TRANSCRIPT_FILE.exists():
            for line in TRANSCRIPT_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[-500:]:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("role") == role:
                    events.append(event)
        matching_users = [
            event for event in events
            if event.get("event_type") in {"user_text", "user_voice_transcript"}
            and str(event.get("content") or "").strip() == ask.strip()
        ]
        if matching_users:
            session_id = matching_users[-1].get("session_id")
            turn_events = [event for event in events if event.get("session_id") == session_id]
            event_types = {str(event.get("event_type") or "") for event in turn_events}
            tool_results = {
                str((event.get("metadata") or {}).get("tool") or "")
                for event in turn_events
                if event.get("event_type") == "tool_result"
            }
            tools_ok = not tools or set(tools).issubset(tool_results)
            assistant_ok = "assistant_text" in event_types
            ok = tools_ok and assistant_ok
            return ok, (
                f"transcript session={session_id} events={sorted(event_types)} "
                f"tool_results={sorted(tool_results)}"
            )
        time.sleep(0.4)
    return False, f"transcript missing exact {role} ask"


def latest_tool(state: dict, name: str) -> dict:
    tools = state.get("turn_tools") if "turn_tools" in state else state.get("tools")
    for tool in reversed(tools or []):
        if isinstance(tool, dict) and tool.get("name") == name:
            return tool
    return {}


def frontend_origin(state: dict) -> str:
    explicit = str(state.get("frontend_origin") or "")
    if explicit:
        return explicit
    href = str(state.get("href") or "")
    parsed = urllib.parse.urlparse(href)
    return f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else ""


def validate_frontend_claim(state: dict, expected_origin: str) -> tuple[bool, str]:
    actual_origin = frontend_origin(state)
    pathname = str(state.get("pathname") or "")
    ok = actual_origin == expected_origin and pathname.startswith("/")
    return ok, f"origin={actual_origin or 'missing'} expected={expected_origin} path={pathname or 'missing'}"


def validate_checkout_evidence(state: dict, backend: dict) -> tuple[bool, str]:
    tool = latest_tool(state, "checkout_commit")
    if not tool:
        return False, "checkout_commit tool evidence missing"
    data = tool.get("data") if isinstance(tool.get("data"), dict) else {}
    decision = str(tool.get("decision") or "")
    backend_decision = str(data.get("decision") or "")
    amount = tool.get("amount_inr")
    session_id = str(tool.get("session_id") or "")
    backend_response = backend.get("checkout_response") if isinstance(backend.get("checkout_response"), dict) else {}
    if backend_response != data:
        return False, "recorded checkout backend response does not match checkout_commit data"
    if decision not in {"allow", "need_approval", "deny"}:
        return False, f"unexpected checkout decision={decision or 'missing'}"
    if backend_decision != decision:
        return False, f"tool decision={decision} backend response decision={backend_decision or 'missing'}"
    if not isinstance(amount, (int, float)) or amount <= 0 or not session_id:
        return False, f"checkout inputs incomplete amount={amount} session_id_present={bool(session_id)}"

    if decision == "allow":
        receipt_id = str(tool.get("receiptId") or "")
        response_receipt = data.get("receipt") if isinstance(data.get("receipt"), dict) else {}
        response_receipt_id = str(response_receipt.get("receipt_id") or "")
        ok = bool(receipt_id) and response_receipt_id == receipt_id
        return ok, (
            f"decision=allow receipt={receipt_id or 'missing'} "
            f"backend_receipt_match={response_receipt_id == receipt_id}"
        )

    if decision == "need_approval":
        approval = data.get("approval") if isinstance(data.get("approval"), dict) else {}
        approval_id = str(approval.get("approval_id") or "")
        return bool(tool.get("ok") is True and approval_id), (
            f"decision=need_approval approval_id={approval_id or 'missing'} tool_ok={tool.get('ok')}"
        )

    receipt_id = str(tool.get("receiptId") or "")
    return bool(tool.get("ok") is False and not receipt_id), (
        f"decision=deny tool_ok={tool.get('ok')} receipt_absent={not receipt_id}"
    )


def checkout_decision_visible(state: dict, decision: str) -> bool:
    pathname = str(state.get("pathname") or "")
    if decision == "allow":
        return bool(state.get("has_receipt")) and ("/orders/" in pathname or "/checkout" in pathname)
    if decision == "need_approval":
        return bool(state.get("has_approval")) and "/checkout" in pathname
    if decision == "deny":
        return bool(state.get("has_deny")) and "/checkout" in pathname
    return False


def is_internal_agent_path(path: str) -> bool:
    return path == "/agent" or path.startswith("/agent/")


def validate_backend_claim(
    mid: str,
    state: dict,
    backend: dict,
    *,
    baseline_order_count: int | None = None,
    expected_order: tuple[str, str] | None = None,
) -> tuple[bool, str]:
    if not backend.get("ok"):
        return False, f"backend snapshot failed: {backend.get('error')}"
    if not backend.get("realtime_configured"):
        return False, "backend Realtime owner is not configured"

    catalog = backend.get("catalog") or []
    has_atta_backend = any("atta" in str(item.get("title") or "").lower() for item in catalog)
    if mid.startswith(("B-FIND", "B-RESULT", "B-ADD", "B-CLEAR", "B-REMOVE", "B-QUANTITY")):
        if not has_atta_backend:
            return False, "backend catalog has no published atta matching the frontend claim"
    if mid in {
        "B-ADD-ATTA",
        "B-CLEAR-CART",
        "B-ADD-RESTORE-CLEAR",
        "B-QUANTITY",
        "B-REMOVE",
        "B-ADD-RESTORE-REMOVE",
        "B-NAV-CART",
        "B-NAV-CHECKOUT",
        "B-ADD-OVER-FIXTURE",
        "B-REMOVE-OVER-FIXTURE",
    }:
        if baseline_order_count is not None and backend.get("order_count") != baseline_order_count:
            return False, "cart-only query created a backend order before checkout"
        return True, f"local cart owner verified in frontend; backend catalog item exists; order_count={backend.get('order_count')} unchanged"
    if mid in {"B-CHECKOUT-OK", "B-CHECKOUT-OVER"}:
        ok, evidence = validate_checkout_evidence(state, backend)
        decision = latest_tool(state, "checkout_commit").get("decision")
        if mid == "B-CHECKOUT-OVER" and decision not in {"need_approval", "deny"}:
            return False, f"over-limit checkout unexpectedly decided {decision}; {evidence}"
        if mid == "B-CHECKOUT-OVER":
            amount = float(latest_tool(state, "checkout_commit").get("amount_inr") or 0)
            if amount <= 10_000:
                return False, f"over-limit checkout used non-over-limit amount {amount}; {evidence}"
        return ok, evidence
    if mid == "S-PUBLISH":
        published = any("evening ragi flour" in str(item.get("title") or "").lower() for item in catalog)
        return published, f"backend published_item_visible={published}"
    if expected_order:
        order_id, expected_status = expected_order
        actual = next(
            (order.get("status") for order in backend.get("orders") or [] if order.get("order_id") == order_id),
            None,
        )
        return actual == expected_status, f"backend order={order_id} status={actual} expected={expected_status}"
    if mid.startswith("S-REFUND"):
        refund = latest_tool(state, "refund_issue")
        decision = refund.get("decision")
        return bool(decision) and backend.get("order_count", 0) > 0, f"backend AgentGuard decision={decision} orders={backend.get('order_count')}"
    if mid in {"B-LONG-WEEKLY", "S-LONG-TRIAGE"}:
        runtime = backend.get("runtime") if isinstance(backend.get("runtime"), dict) else {}
        handoff = latest_tool(state, "delegate_to_runtime_agent")
        statuses = {
            str(job.get("status") or "")
            for job in state.get("runtime_jobs") or []
            if isinstance(job, dict)
        }
        ok = runtime.get("runtime_available") is True and handoff.get("ok") is True and bool(
            statuses & {"started", "completed"}
        )
        return ok, (
            f"runtime_available={runtime.get('runtime_available')} model={runtime.get('model')} "
            f"handoff_ok={handoff.get('ok')} statuses={sorted(statuses)}"
        )
    return True, f"backend owners reachable; realtime_configured=true; order_count={backend.get('order_count')}"


EVAL = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? panel.innerText : '';
  const statusHint = panel ? (panel.querySelectorAll(':scope > p')[1]?.textContent || '') : '';
  const body = document.body.innerText || '';
  const tools = (window.__samanthaTools || []).slice(-12);
  const runtimeJobs = (window.__samanthaRuntimeJobs || []).slice(-12);
  const recentEvents = (window.__samanthaEvents || []).slice(-30);
  const recentErrors = (window.__samanthaErrors || []).slice(-12);
  const turn = window.__samanthaTurn || {};
  return {
    href: location.href,
    frontend_origin: location.origin,
    pathname: location.pathname,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0,12),
    body_snip: body.slice(0, 1000),
    hint: hint.slice(0, 600),
    status_hint: statusHint.slice(0, 200),
    reply: reply ? reply.innerText.slice(0, 400) : '',
    tools,
    runtime_jobs: runtimeJobs,
    recent_events: recentEvents,
    recent_errors: recentErrors,
    error_count: (window.__samanthaErrors || []).length,
    turn_in_flight: turn.in_flight === true,
    turn_phase: turn.phase || '',
    tool_count: (window.__samanthaTools || []).length,
    has_atta: /atta/i.test(body),
    has_milk: /milk/i.test(body),
    has_organic: /organic/i.test(body),
    has_receipt: /receipt/i.test(body),
    has_approval: /need.?approval|approve|approval/i.test(body),
    has_allow: /\\ballow(ed)?\\b|committed|receipt/i.test(body),
    has_deny: /\\bdeny|denied\\b/i.test(body),
    has_refund: /refund/i.test(body),
    has_catalog: /catalog|sku|listing|product/i.test(body),
    has_mandate: /mandate|agentguard|auto.?approve/i.test(body),
    has_customer_demo_copy: /\b(demo|booth)\b/i.test(body),
  };
})()
"""

def eval_states(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict) and ("href" in val or "pathname" in val or "ok" in val or "mandate_id" in val):
            out.append(val)
    return out


def shot_paths(result: dict) -> list[str]:
    paths = []
    for step in result.get("results", []):
        if step.get("type") == "screenshot" and step.get("screenshot_path"):
            paths.append(step["screenshot_path"])
    return paths


def save_evidence(mid: str, paths: list[str]) -> list[str]:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, p in enumerate(paths):
        src = pathlib.Path(p)
        if not src.exists():
            continue
        dest = EVIDENCE / f"{mid}-{TS}-{i}{src.suffix or '.jpeg'}"
        shutil.copy2(src, dest)
        saved.append(str(dest))
    return saved


def tool_names(state: dict) -> list[str]:
    tools = state.get("turn_tools") if "turn_tools" in state else state.get("tools")
    return [t.get("name") for t in (tools or []) if isinstance(t, dict) and t.get("name")]


def samantha_turn_pending(state: dict) -> bool:
    if state.get("turn_in_flight") is True:
        return True
    text = str(state.get("status_hint") or "").lower()
    return any(marker in text for marker in ("thinking", "connecting", "pulling", "searching"))


def ask_with_shot(handler, message: str, mid: str, wait_ms: int = 18000) -> tuple[dict, list[str]]:
    request = {
        "action": "run",
        "session_name": SESSION,
        "use_selected_tab": False,
        "timeout_seconds": max(90, wait_ms // 1000 + 45),
        "actions": [
            {"type": "evaluate", "expression": EVAL},
            {
                "type": "locator",
                "locator": {"by": "testid", "testId": "samantha-orb-text"},
                "operation": "fill",
                "value": message,
            },
            {
                "type": "locator",
                "locator": {"by": "role", "role": "button", "name": "Send", "exact": True},
                "operation": "click",
            },
            {"type": "wait", "ms": wait_ms},
            {"type": "evaluate", "expression": EVAL},
            {"type": "screenshot", "format": "jpeg", "quality": 70},
            {"type": "page_context"},
        ],
    }
    try:
        result = call(handler, request)
    except RuntimeError as exc:
        if "Locator did not resolve for fill" not in str(exc):
            raise
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 45,
                "actions": [
                    {
                        "type": "locator",
                        "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                        "operation": "click",
                    },
                    {"type": "wait", "ms": 8000},
                ],
            },
        )
        result = call(handler, request)
    states = [e for e in eval_states(result) if "href" in e]
    state = states[-1] if states else {}
    baseline_tool_count = int(states[0].get("tool_count") or 0) if states else 0
    baseline_error_count = int(states[0].get("error_count") or 0) if states else 0
    for attempt in range(1, 4):
        if not samantha_turn_pending(state):
            break
        result = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 50,
                "actions": [
                    {"type": "wait", "ms": 15000},
                    {"type": "evaluate", "expression": EVAL},
                    {"type": "screenshot", "format": "jpeg", "quality": 70},
                    {"type": "page_context"},
                ],
            },
        )
        states = [e for e in eval_states(result) if "href" in e]
        state = states[-1] if states else state
        if samantha_turn_pending(state):
            print(f"[WAIT] {mid}: Samantha still pending after settle attempt {attempt}", flush=True)
    state["turn_settled"] = not samantha_turn_pending(state)
    current_tool_count = int(state.get("tool_count") or 0)
    new_tool_count = max(0, current_tool_count - baseline_tool_count)
    recent_tools = state.get("tools") or []
    state["turn_tool_start"] = baseline_tool_count
    state["turn_tools"] = recent_tools[-new_tool_count:] if new_tool_count else []
    current_error_count = int(state.get("error_count") or 0)
    new_error_count = max(0, current_error_count - baseline_error_count)
    recent_errors = state.get("recent_errors") or []
    state["turn_error_start"] = baseline_error_count
    state["turn_errors"] = recent_errors[-new_error_count:] if new_error_count else []
    saved = save_evidence(mid, shot_paths(result))
    return state, saved


def goto_shot(handler, url: str, mid: str) -> tuple[dict, list[str]]:
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 60,
            "actions": [
                {"type": "goto", "url": url},
                {"type": "wait", "ms": 2000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    states = [e for e in eval_states(result) if "href" in e]
    state = states[-1] if states else {}
    saved = save_evidence(mid, shot_paths(result))
    return state, saved


def signed_out_samantha_gate(handler, app_url: str, mid: str) -> tuple[bool, dict, list[str]]:
    """Prove the app does not render Samantha after the gateway session is revoked."""
    initial = call(
        handler,
        {
            "action": "run", "session_name": SESSION, "use_selected_tab": False,
            "timeout_seconds": 30,
            "actions": [
                {"type": "goto", "url": app_url},
                {"type": "wait", "ms": 1000},
                {"type": "evaluate", "expression": "(() => ({href:location.href,body_snip:(document.body.innerText||'').slice(0,2000)}))()"},
            ],
        },
    )
    initial_states = [entry for entry in eval_states(initial) if "href" in entry]
    initial_state = initial_states[-1] if initial_states else {}
    if "sign out" in str(initial_state.get("body_snip") or "").lower():
        call(
            handler,
            {
                "action": "run", "session_name": SESSION, "use_selected_tab": False,
                "timeout_seconds": 30,
                "actions": [
                    {
                        "type": "locator",
                        "locator": {"by": "role", "role": "button", "name": "Sign out", "exact": True},
                        "operation": "click",
                    },
                    {"type": "wait", "ms": 1000},
                ],
            },
        )
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 45,
            "actions": [
                {"type": "goto", "url": app_url},
                {"type": "wait", "ms": 1400},
                {
                    "type": "evaluate",
                    "expression": "(() => ({href:location.href,orb_count:document.querySelectorAll('[data-testid=\"samantha-orb\"]').length,body_snip:(document.body.innerText||'').slice(0,1000)}))()",
                },
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    states = [entry for entry in eval_states(result) if "href" in entry]
    state = states[-1] if states else {}
    shots = save_evidence(mid, shot_paths(result))
    clean_copy = not bool(__import__("re").search(r"\b(demo|booth)\b", str(state.get("body_snip") or ""), __import__("re").I))
    return bool(shots) and state.get("orb_count") == 0 and clean_copy, state, shots


def merge_turn_with_page_state(turn_state: dict, page_state: dict) -> dict:
    """Keep settled operator-turn evidence while replacing only the visible page state."""
    merged = dict(page_state)
    for key in (
        "tools",
        "turn_tools",
        "turn_tool_start",
        "runtime_jobs",
        "recent_events",
        "recent_errors",
        "turn_errors",
        "turn_error_start",
        "turn_in_flight",
        "turn_phase",
        "turn_settled",
        "hint",
        "status_hint",
        "reply",
    ):
        if key in turn_state:
            merged[key] = turn_state[key]
    merged["turn_frontend_origin"] = frontend_origin(turn_state)
    return merged


def samantha_ready(state: dict) -> bool:
    hint = str(state.get("status_hint") or "").lower()
    return "text mode ready" in hint or "listening + text ready" in hint


def wait_for_samantha_ready(handler, state: dict) -> dict:
    for restart in range(2):
        for _ in range(4):
            if samantha_ready(state):
                return state
            result = call(
                handler,
                {
                    "action": "run",
                    "session_name": SESSION,
                    "use_selected_tab": False,
                    "timeout_seconds": 30,
                    "actions": [
                        {"type": "wait", "ms": 5000},
                        {"type": "evaluate", "expression": EVAL},
                    ],
                },
            )
            states = [entry for entry in eval_states(result) if "href" in entry]
            state = states[-1] if states else state
        if restart == 0:
            call(
                handler,
                {
                    "action": "run",
                    "session_name": SESSION,
                    "use_selected_tab": False,
                    "timeout_seconds": 40,
                    "actions": [
                        {
                            "type": "locator",
                            "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                            "operation": "click",
                        },
                        {"type": "wait", "ms": 800},
                        {
                            "type": "locator",
                            "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                            "operation": "click",
                        },
                        {"type": "wait", "ms": 8000},
                        {"type": "evaluate", "expression": EVAL},
                    ],
                },
            )
    raise RuntimeError(f"Samantha text mode did not become ready: {state.get('status_hint')}")


def boot_buyer(handler) -> dict:
    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {"aud": "ondcbuyer", "return": f"{BUYER}/search", "display_name": "ONDC Matrix Buyer"}
        )
    )
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 100,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2200},
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2200},
                {
                    "type": "locator",
                    "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                    "operation": "click",
                },
                {"type": "wait", "ms": 8000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    save_evidence("B-BOOT", shot_paths(result))
    states = [e for e in eval_states(result) if "href" in e]
    return wait_for_samantha_ready(handler, states[-1] if states else {})


def boot_seller(handler) -> dict:
    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {"aud": "ondcseller", "return": f"{SELLER}/dashboard", "display_name": "ONDC Matrix Seller"}
        )
    )
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 100,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2200},
                {"type": "goto", "url": f"{SELLER}/dashboard"},
                {"type": "wait", "ms": 2200},
                {
                    "type": "locator",
                    "locator": {"by": "role", "role": "button", "name": "Open Samantha", "exact": True},
                    "operation": "click",
                },
                {"type": "wait", "ms": 8000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    save_evidence("S-BOOT", shot_paths(result))
    states = [e for e in eval_states(result) if "href" in e]
    return wait_for_samantha_ready(handler, states[-1] if states else {})


def run_buyer(handler, rows: list) -> None:
    def rec(mid, ask, result, evidence, shots, state):
        backend = backend_snapshot(runtime_role="buyer" if mid == "B-LONG-WEEKLY" else None)
        if mid.startswith("B-CHECKOUT"):
            checkout = latest_tool(state or {}, "checkout_commit")
            backend["checkout_response"] = checkout.get("data") if isinstance(checkout.get("data"), dict) else {}
        backend_ok, backend_evidence = validate_backend_claim(
            mid,
            state or {},
            backend,
            baseline_order_count=baseline_order_count,
        )
        frontend_ok, frontend_evidence = validate_frontend_claim(state or {}, BUYER)
        turn_settled = (state or {}).get("turn_settled") is True
        turn_errors = (state or {}).get("turn_errors") or []
        transcript_ok, transcript_evidence = transcript_proof("buyer", ask, tool_names(state or {}))
        clean_copy = not bool((state or {}).get("has_customer_demo_copy"))
        if result == "Pass" and (
            not shots or not frontend_ok or not backend_ok or not turn_settled or turn_errors
            or not transcript_ok or not clean_copy
        ):
            result = "Fail"
        evidence = (
            f"{evidence}; settled={turn_settled}; turn_errors={len(turn_errors)}; frontend={frontend_evidence}; "
            f"backend={backend_evidence}; {transcript_evidence}; clean_copy={clean_copy}"
        )
        rows.append(
            {
                "id": mid,
                "ask": ask,
                "result": result,
                "evidence": evidence,
                "screenshots": shots,
                "pathname": (state or {}).get("pathname"),
                "frontend_origin": frontend_origin(state or {}),
                "frontend_check": {"ok": frontend_ok, "evidence": frontend_evidence},
                "tools": tool_names(state or {}),
                "reply": ((state or {}).get("reply") or "")[:140],
                "backend": backend,
                "backend_check": {"ok": backend_ok, "evidence": backend_evidence},
                "turn_errors": turn_errors,
                "visual_review": "required",
            }
        )
        print(f"[{result}] {mid}: {evidence} shots={shots}", flush=True)

    print("=== Buyer ===", flush=True)
    baseline_order_count = int(backend_snapshot().get("order_count") or 0)
    gate_ok, gate_state, gate_shots = signed_out_samantha_gate(handler, f"{BUYER}/search", "B-AUTH-GATE")
    rows.append({
        "id": "B-AUTH-GATE", "ask": "signed-out Samantha gate",
        "result": "Pass" if gate_ok else "Fail",
        "evidence": f"orb_count={gate_state.get('orb_count')} clean_copy=true",
        "screenshots": gate_shots, "pathname": urllib.parse.urlparse(str(gate_state.get('href') or '')).path,
        "frontend_origin": frontend_origin(gate_state), "frontend_check": {"ok": gate_ok},
        "tools": [], "reply": "", "backend": {"client_secret_unauth_expected": 401},
        "backend_check": {"ok": True}, "turn_errors": [], "visual_review": "required",
    })
    print(f"[{'Pass' if gate_ok else 'Fail'}] B-AUTH-GATE: orb_count={gate_state.get('orb_count')}", flush=True)
    checkout_item_title, approval_item_title = seed_buyer_checkout_fixture()
    print(
        f"[PRECONDITION] published Buyer checkout items {checkout_item_title!r} and {approval_item_title!r}",
        flush=True,
    )
    boot_buyer(handler)

    greeting = "Hi Samantha, this is my first time here. What can you help me do?"
    st, shots = ask_with_shot(handler, greeting, "B-HI", 12000)
    tools = tool_names(st)
    commerce = {"search_catalog", "add_to_cart", "checkout_commit", "navigate_to"}
    fired = [t for t in tools if t in commerce]
    ok = "/search" in (st.get("pathname") or "") and not fired and bool(shots) and bool(st.get("reply"))
    rec("B-HI", greeting, "Pass" if ok else "Fail", f"path={st.get('pathname')} tools={tools}", shots, st)

    find_ask = f"Please show me {checkout_item_title}. Do not add anything to my cart yet."
    st, shots = ask_with_shot(handler, find_ask, "B-FIND-ATTA", 28000)
    tools = tool_names(st)
    ok = bool(shots) and bool(st.get("has_atta")) and "/results" in (st.get("pathname") or "") and "search_catalog" in tools
    rec(
        "B-FIND-ATTA",
        find_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} atta={st.get('has_atta')} tools={tools}",
        shots,
        st,
    )

    ground_ask = "What atta choices are on this page, and what does the first one cost?"
    st, shots = ask_with_shot(handler, ground_ask, "B-RESULT-GROUND", 16000)
    reply = (st.get("reply") or "").lower()
    ok = bool(shots) and "/results" in (st.get("pathname") or "") and "atta" in reply and any(
        ch.isdigit() for ch in reply
    )
    rec(
        "B-RESULT-GROUND",
        ground_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} grounded_reply={reply[:140]}",
        shots,
        st,
    )

    add_ask = f"Please put one {checkout_item_title} in my cart."
    st, shots = ask_with_shot(handler, add_ask, "B-ADD-ATTA", 28000)
    tools = tool_names(st)
    ok = bool(shots) and bool(st.get("has_atta")) and "/cart" in (st.get("pathname") or "") and "add_to_cart" in tools
    rec(
        "B-ADD-ATTA",
        add_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} atta={st.get('has_atta')} tools={tools}",
        shots,
        st,
    )

    clear_ask = "Please empty my cart so I can start over."
    st, shots = ask_with_shot(handler, clear_ask, "B-CLEAR-CART", 18000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "/cart" in (st.get("pathname") or "")
        and "clear_cart" in tool_names(st)
        and "cart is empty" in blob
    )
    rec(
        "B-CLEAR-CART",
        clear_ask,
        "Pass" if ok else "Fail",
        f"tools={tool_names(st)} empty={'cart is empty' in blob}",
        shots,
        st,
    )

    restore_ask = f"Please put one {checkout_item_title} back in my cart."
    st, shots = ask_with_shot(handler, restore_ask, "B-ADD-RESTORE-CLEAR", 22000)
    ok = (
        bool(shots)
        and "/cart" in (st.get("pathname") or "")
        and "add_to_cart" in tool_names(st)
        and bool(st.get("has_atta"))
    )
    rec(
        "B-ADD-RESTORE-CLEAR",
        restore_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tool_names(st)}",
        shots,
        st,
    )

    quantity_ask = "Make that two packs instead."
    st, shots = ask_with_shot(handler, quantity_ask, "B-QUANTITY", 18000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "/cart" in (st.get("pathname") or "")
        and "set_cart_quantity" in tool_names(st)
        and "2" in blob
    )
    rec(
        "B-QUANTITY",
        quantity_ask,
        "Pass" if ok else "Fail",
        f"tools={tool_names(st)} quantity_visible={'2' in blob}",
        shots,
        st,
    )

    remove_ask = "Remove that atta from my cart."
    st, shots = ask_with_shot(handler, remove_ask, "B-REMOVE", 18000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "/cart" in (st.get("pathname") or "")
        and "remove_from_cart" in tool_names(st)
        and "cart is empty" in blob
    )
    rec(
        "B-REMOVE",
        remove_ask,
        "Pass" if ok else "Fail",
        f"tools={tool_names(st)} empty={'cart is empty' in blob}",
        shots,
        st,
    )

    st, shots = ask_with_shot(handler, restore_ask, "B-ADD-RESTORE-REMOVE", 22000)
    ok = (
        bool(shots)
        and "/cart" in (st.get("pathname") or "")
        and "add_to_cart" in tool_names(st)
        and bool(st.get("has_atta"))
    )
    rec(
        "B-ADD-RESTORE-REMOVE",
        restore_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tool_names(st)}",
        shots,
        st,
    )

    st, shots = ask_with_shot(handler, "take me to my cart", "B-NAV-CART", 16000)
    ok = bool(shots) and "/cart" in (st.get("pathname") or "")
    rec("B-NAV-CART", "take me to cart", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "go to checkout", "B-NAV-CHECKOUT", 16000)
    ok = bool(shots) and "/checkout" in (st.get("pathname") or "")
    rec("B-NAV-CHECKOUT", "go to checkout", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "remember that I prefer organic produce", "B-MEM-ORG", 16000)
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    ok = bool(shots) and ("remember_preference" in tool_names(st) or "organic" in blob)
    rec("B-MEM-ORG", "remember organic", "Pass" if ok else "Fail", f"tools={tool_names(st)}", shots, st)

    st, shots = ask_with_shot(handler, "open config so I can see my mandate and preferences", "B-NAV-CONFIG", 16000)
    ok = bool(shots) and "/config" in (st.get("pathname") or "")
    rec("B-NAV-CONFIG", "open config", "Pass" if ok else "Fail", f"path={st.get('pathname')} organic={st.get('has_organic')}", shots, st)

    find_approval_ask = f"Please show me {approval_item_title}. Do not add it to my cart yet."
    st, shots = ask_with_shot(handler, find_approval_ask, "B-FIND-OVER-FIXTURE", 30000)
    tools = tool_names(st)
    ok = bool(shots) and "/results" in (st.get("pathname") or "") and "search_catalog" in tools
    rec(
        "B-FIND-OVER-FIXTURE",
        find_approval_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tools}",
        shots,
        st,
    )

    add_approval_ask = f"Please add one {approval_item_title} to my cart."
    st, shots = ask_with_shot(handler, add_approval_ask, "B-ADD-OVER-FIXTURE", 30000)
    tools = tool_names(st)
    ok = bool(shots) and "/cart" in (st.get("pathname") or "") and "add_to_cart" in tools
    rec(
        "B-ADD-OVER-FIXTURE",
        add_approval_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tools}",
        shots,
        st,
    )

    # Exercise the over-limit decision against the authoritative live cart total.
    st, shots = ask_with_shot(
        handler,
        "Please checkout and pay for my current cart now.",
        "B-CHECKOUT-OVER",
        24000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    checkout = latest_tool(st, "checkout_commit")
    exact_decision = str(checkout.get("decision") or "")
    if exact_decision in {"need_approval", "deny"}:
        page_state, decision_shots = goto_shot(handler, f"{BUYER}/checkout", "B-CHECKOUT-OVER-UI")
        st = merge_turn_with_page_state(st, page_state)
        shots = decision_shots
        checkout = latest_tool(st, "checkout_commit")
        exact_decision = str(checkout.get("decision") or "")
        blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    decision_visible = checkout_decision_visible(st, exact_decision)
    ok = (
        bool(shots)
        and exact_decision in {"need_approval", "deny"}
        and decision_visible
        and any(k in blob for k in ("need_approval", "approval", "deny", "denied", "limit", "exceed", "25000", "mandate"))
    )
    rec(
        "B-CHECKOUT-OVER",
        "checkout current over-limit cart",
        "Pass" if ok else "Fail",
        f"decision={exact_decision} decision_visible={decision_visible} blob={blob[:120]}",
        shots,
        st,
    )

    remove_approval_ask = f"Please remove {approval_item_title} from my cart."
    st, shots = ask_with_shot(handler, remove_approval_ask, "B-REMOVE-OVER-FIXTURE", 24000)
    tools = tool_names(st)
    ok = bool(shots) and "/cart" in (st.get("pathname") or "") and "remove_from_cart" in tools
    rec(
        "B-REMOVE-OVER-FIXTURE",
        remove_approval_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tools}",
        shots,
        st,
    )

    # Checkout / payment — required after removing the over-limit fixture.
    st, shots = ask_with_shot(
        handler,
        "please checkout and pay for my cart now",
        "B-CHECKOUT-OK",
        28000,
    )
    tools = tool_names(st)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ag_hit = any(
        k in blob
        for k in (
            "allow",
            "receipt",
            "committed",
            "need_approval",
            "need approval",
            "approve",
            "denied",
            "deny",
            "checkout",
        )
    )
    tools_ok = "checkout_commit" in tools
    checkout = latest_tool(st, "checkout_commit")
    exact_decision = str(checkout.get("decision") or "")
    if exact_decision in {"need_approval", "deny"}:
        chk_st, chk_shots = goto_shot(handler, f"{BUYER}/checkout", "B-CHECKOUT-UI")
        shots = shots + chk_shots
        st = merge_turn_with_page_state(st, chk_st)
        blob2 = f"{st.get('body_snip','')} {st.get('hint','')}".lower()
        ag_hit = ag_hit or any(k in blob2 for k in ("approval", "receipt", "mandate", "agentguard", "checkout"))
        checkout = latest_tool(st, "checkout_commit")
        exact_decision = str(checkout.get("decision") or "")
    decision_visible = checkout_decision_visible(st, exact_decision)
    ok = bool(shots) and tools_ok and decision_visible and ag_hit
    rec(
        "B-CHECKOUT-OK",
        "checkout and pay",
        "Pass" if ok else "Fail",
        f"decision={exact_decision} tools={tools} decision_visible={decision_visible} visible={ag_hit}",
        shots,
        st,
    )

    long_ask = "Please plan a practical week of groceries for two people under 2,000 rupees, taking my preferences into account."
    st, shots = ask_with_shot(handler, long_ask, "B-LONG-WEEKLY", 22000)
    path = st.get("pathname") or ""
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    jobs = st.get("runtime_jobs") or []
    statuses = [job.get("status") for job in jobs if isinstance(job, dict)]
    if is_internal_agent_path(path) or "cursor" in blob:
        res, ev = "Fail", f"leaked path={path}"
    elif "delegate_to_runtime_agent" not in tool_names(st):
        res, ev = "Fail", f"runtime tool missing path={path} blob={blob[:120]}"
    elif "completed" in statuses:
        res, ev = "Pass", f"completed inline path={path} runtime_statuses={statuses}"
    elif "started" in statuses:
        res, ev = "Pass", f"handoff accepted path={path} runtime_statuses={statuses}"
    else:
        res, ev = "Fail", f"no clear handoff path={path} blob={blob[:120]}"
    if not shots and res == "Pass":
        res, ev = "Fail", "no screenshot"
    rec("B-LONG-WEEKLY", long_ask, res, ev, shots, st)


def run_seller(handler, rows: list) -> None:
    def rec(mid, ask, result, evidence, shots, state, *, expected_order=None):
        backend = backend_snapshot(
            runtime_role="seller" if mid == "S-LONG-TRIAGE" else None,
            catalog_query="evening ragi flour" if mid == "S-PUBLISH" else "atta",
        )
        backend_ok, backend_evidence = validate_backend_claim(
            mid,
            state or {},
            backend,
            expected_order=expected_order,
        )
        frontend_ok, frontend_evidence = validate_frontend_claim(state or {}, SELLER)
        turn_settled = (state or {}).get("turn_settled") is True
        turn_errors = (state or {}).get("turn_errors") or []
        transcript_ok, transcript_evidence = transcript_proof("seller", ask, tool_names(state or {}))
        clean_copy = not bool((state or {}).get("has_customer_demo_copy"))
        if result == "Pass" and (
            not shots or not frontend_ok or not backend_ok or not turn_settled or turn_errors
            or not transcript_ok or not clean_copy
        ):
            result = "Fail"
        evidence = (
            f"{evidence}; settled={turn_settled}; turn_errors={len(turn_errors)}; frontend={frontend_evidence}; "
            f"backend={backend_evidence}; {transcript_evidence}; clean_copy={clean_copy}"
        )
        rows.append(
            {
                "id": mid,
                "ask": ask,
                "result": result,
                "evidence": evidence,
                "screenshots": shots,
                "pathname": (state or {}).get("pathname"),
                "frontend_origin": frontend_origin(state or {}),
                "frontend_check": {"ok": frontend_ok, "evidence": frontend_evidence},
                "tools": tool_names(state or {}),
                "reply": ((state or {}).get("reply") or "")[:140],
                "backend": backend,
                "backend_check": {"ok": backend_ok, "evidence": backend_evidence},
                "turn_errors": turn_errors,
                "visual_review": "required",
            }
        )
        print(f"[{result}] {mid}: {evidence} shots={shots}", flush=True)

    print("=== Seller ===", flush=True)
    gate_ok, gate_state, gate_shots = signed_out_samantha_gate(handler, f"{SELLER}/dashboard", "S-AUTH-GATE")
    rows.append({
        "id": "S-AUTH-GATE", "ask": "signed-out Samantha gate",
        "result": "Pass" if gate_ok else "Fail",
        "evidence": f"orb_count={gate_state.get('orb_count')} clean_copy=true",
        "screenshots": gate_shots, "pathname": urllib.parse.urlparse(str(gate_state.get('href') or '')).path,
        "frontend_origin": frontend_origin(gate_state), "frontend_check": {"ok": gate_ok},
        "tools": [], "reply": "", "backend": {"client_secret_unauth_expected": 401},
        "backend_check": {"ok": True}, "turn_errors": [], "visual_review": "required",
    })
    print(f"[{'Pass' if gate_ok else 'Fail'}] S-AUTH-GATE: orb_count={gate_state.get('orb_count')}", flush=True)
    boot_seller(handler)

    greeting = "Hi Samantha, I'm new here. What can you help me run in my shop?"
    st, shots = ask_with_shot(handler, greeting, "S-HI", 12000)
    tools = tool_names(st)
    commerce = {"refund_issue", "navigate_to", "catalog_publish"}
    fired = [t for t in tools if t in commerce]
    path = st.get("pathname") or ""
    ok = bool(shots) and not fired and bool(st.get("reply")) and ("dashboard" in path or path.startswith("/"))
    rec("S-HI", greeting, "Pass" if ok else "Fail", f"path={path} tools={tools}", shots, st)

    st, shots = ask_with_shot(handler, "open agentguard so I can review my mandate", "S-NAV-AG", 18000)
    ok = bool(shots) and "/agentguard" in (st.get("pathname") or "")
    rec("S-NAV-AG", "open agentguard", "Pass" if ok else "Fail", f"path={st.get('pathname')}", shots, st)

    st, shots = ask_with_shot(handler, "show me the catalog", "S-NAV-CAT", 18000)
    path = st.get("pathname") or ""
    ok = bool(shots) and (
        "catalog" in path
        or "product" in path
        or "listing" in path
        or (st.get("has_catalog") and "navigate_to" in tool_names(st))
    )
    rec("S-NAV-CAT", "show catalog", "Pass" if ok else "Fail", f"path={path} tools={tool_names(st)}", shots, st)

    publish_ask = f"Please add Evening Ragi Flour {TS[-6:]} to my catalog at 75 rupees for 500 grams, with 7 packs in stock."
    st, shots = ask_with_shot(handler, publish_ask, "S-PUBLISH", 24000)
    tools = tool_names(st)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and "catalog_publish" in tools and "7" in blob and "/catalog" in (st.get("pathname") or "")
    rec("S-PUBLISH", publish_ask, "Pass" if ok else "Fail", f"path={st.get('pathname')} tools={tools} quantity_visible={'7' in blob}", shots, st)

    fixture_orders = seed_seller_order_fixture()
    print(f"[PRECONDITION] seeded Seller orders {fixture_orders}", flush=True)

    st, shots = ask_with_shot(handler, "show me orders", "S-NAV-ORD", 18000)
    path = st.get("pathname") or ""
    ok = bool(shots) and ("order" in path or "order" in (st.get("body_snip") or "").lower())
    rec("S-NAV-ORD", "show orders", "Pass" if ok else "Fail", f"path={path}", shots, st)

    accept_ask = "Please accept the newest paid order."
    st, shots = ask_with_shot(handler, accept_ask, "S-ORDER-ACCEPT", 22000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "accept_order" in tool_names(st)
        and "/orders/" in (st.get("pathname") or "")
        and "accepted" in blob
    )
    rec(
        "S-ORDER-ACCEPT",
        accept_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tool_names(st)} accepted={'accepted' in blob}",
        shots,
        st,
        expected_order=(fixture_orders[-1], "accepted"),
    )

    fulfil_ask = "That accepted order is packed. Mark it fulfilled."
    st, shots = ask_with_shot(handler, fulfil_ask, "S-ORDER-FULFIL", 22000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "mark_order_fulfilled" in tool_names(st)
        and "/orders/" in (st.get("pathname") or "")
        and any(word in blob for word in ("fulfilled", "delivered"))
    )
    rec(
        "S-ORDER-FULFIL",
        fulfil_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tool_names(st)}",
        shots,
        st,
        expected_order=(fixture_orders[-1], "fulfilled"),
    )

    reject_ask = "Reject the newest remaining paid order."
    st, shots = ask_with_shot(handler, reject_ask, "S-ORDER-REJECT", 22000)
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = (
        bool(shots)
        and "reject_order" in tool_names(st)
        and "/orders/" in (st.get("pathname") or "")
        and any(word in blob for word in ("rejected", "cancelled"))
    )
    rec(
        "S-ORDER-REJECT",
        reject_ask,
        "Pass" if ok else "Fail",
        f"path={st.get('pathname')} tools={tool_names(st)}",
        shots,
        st,
        expected_order=(fixture_orders[0], "rejected"),
    )

    st, shots = ask_with_shot(
        handler,
        "Please refund 400 rupees on my most recent order.",
        "S-REFUND-OK",
        26000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and (
        "refund_issue" in tool_names(st)
        or any(k in blob for k in ("allow", "refund", "receipt", "executed", "500"))
    )
    rec("S-REFUND-OK", "refund 400 on most recent order", "Pass" if ok else "Fail", f"tools={tool_names(st)} blob={blob[:140]}", shots, st)

    st, shots = ask_with_shot(
        handler,
        "Please refund 26000 rupees on my most recent order.",
        "S-REFUND-OVER",
        24000,
    )
    blob = f"{st.get('hint','')} {st.get('reply','')} {st.get('body_snip','')}".lower()
    ok = bool(shots) and any(
        k in blob for k in ("need_approval", "approval", "deny", "denied", "limit", "exceed", "26000")
    )
    rec("S-REFUND-OVER", "refund 26000 on most recent order", "Pass" if ok else "Fail", f"blob={blob[:160]}", shots, st)

    st, shots = ask_with_shot(handler, "remember I prefer brief refund confirmations", "S-MEM", 16000)
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    ok = bool(shots) and ("remember_preference" in tool_names(st) or "brief" in blob)
    # Capture agentguard memory UI
    ag_st, ag_shots = goto_shot(handler, f"{SELLER}/agentguard", "S-MEM-UI")
    shots = shots + ag_shots
    rec("S-MEM", "brief refund confirmations", "Pass" if ok else "Fail", f"tools={tool_names(st)} ag_organic={ag_st.get('has_organic')}", shots, st)

    long_ask = "Review my recent orders and give me a short priority list of what I should handle first, including refund risk."
    st, shots = ask_with_shot(handler, long_ask, "S-LONG-TRIAGE", 22000)
    path = st.get("pathname") or ""
    blob = f"{st.get('hint','')} {st.get('reply','')}".lower()
    jobs = st.get("runtime_jobs") or []
    statuses = [job.get("status") for job in jobs if isinstance(job, dict)]
    if is_internal_agent_path(path) or "cursor" in blob:
        res, ev = "Fail", f"leaked path={path}"
    elif "delegate_to_runtime_agent" not in tool_names(st):
        res, ev = "Fail", f"runtime tool missing path={path} blob={blob[:120]}"
    elif "completed" in statuses:
        res, ev = "Pass", f"completed inline path={path} runtime_statuses={statuses}"
    elif "started" in statuses:
        res, ev = "Pass", f"handoff accepted path={path} runtime_statuses={statuses}"
    else:
        res, ev = "Fail", f"no clear handoff path={path} blob={blob[:120]}"
    if not shots and res == "Pass":
        res, ev = "Fail", "no screenshot"
    rec("S-LONG-TRIAGE", long_ask, res, ev, shots, st)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("side", nargs="?", choices=("all", "buyer", "seller"), default="all")
    side = parser.parse_args().side
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    handler = load_handler()
    # WIP Hermes window isolation requires an explicit controllable URL. Keep
    # the lease scoped to this matrix session so a stale focused tab cannot
    # silently become the test target.
    pre = call(
        handler,
        {
            "action": "preflight",
            "session_name": SESSION,
            "url": BUYER if side in ("all", "buyer") else SELLER,
            "timeout_seconds": 20,
        },
    )
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    rows: list[dict] = []
    try:
        if side in ("all", "buyer"):
            run_buyer(handler, rows)
        if side in ("all", "seller"):
            run_seller(handler, rows)
    finally:
        leave = f"{SELLER}/agentguard" if side in ("all", "seller") else f"{BUYER}/checkout"
        try:
            call(
                handler,
                {
                    "action": "run",
                    "session_name": SESSION,
                    "use_selected_tab": False,
                    "timeout_seconds": 30,
                    "actions": [{"type": "goto", "url": leave}, {"type": "wait", "ms": 800}],
                },
            )
        finally:
            call(handler, {"action": "closeout", "timeout_seconds": 20})
            try:
                post_gateway_json("/api/demo-commerce/test-fixtures/cleanup", {})
            except Exception as exc:
                print(f"Warning: local fixture cleanup failed: {exc}", file=sys.stderr)

    passed = sum(1 for x in rows if x["result"] == "Pass")
    failed = sum(1 for x in rows if x["result"] == "Fail")
    skipped = sum(1 for x in rows if x["result"] == "Skip")
    out = {
        "success": failed == 0,
        "counts": {"pass": passed, "fail": failed, "skip": skipped, "total": len(rows)},
        "rows": rows,
        "evidence_dir": str(EVIDENCE),
        "realtime_model": status.get("data", {}).get("model"),
        "ts": TS,
    }
    out_path = EVIDENCE / f"matrix-run-{TS}.json"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))
    print(f"Wrote {out_path}", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
