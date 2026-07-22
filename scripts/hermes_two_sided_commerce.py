#!/usr/bin/env python3
"""Two-sided AgentGuard commerce proof via the local demo-commerce API."""
from __future__ import annotations

import argparse
import atexit
import json
import pathlib
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GATEWAY = "http://127.0.0.1:43101"
ROOT = pathlib.Path(__file__).resolve().parents[1]
SESSION = "two-sided-commerce"


def _browser_proof(*, title: str, order_id: str, transaction_id: str, issue_id: str) -> dict[str, Any]:
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import closeout_session, load_handler, run_with_session_preflight

    handler = load_handler()

    def capture(name: str, app: str, url: str) -> dict[str, Any]:
        audience = "ondcbuyer" if app == "buyer" else "ondcseller"
        login = (
            f"{GATEWAY}/api/auth/demo-continue?aud={audience}"
            f"&return={urllib.parse.quote(url, safe='')}&display_name=Demo+User"
        )
        return run_with_session_preflight(
            handler,
            {
                "action": "run",
                "session_name": f"{SESSION}-{name}",
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "goto", "url": login},
                    {"type": "wait", "ms": 1200},
                    {"type": "goto", "url": url},
                    {"type": "wait", "ms": 1800},
                    {"type": "text"},
                    {"type": "screenshot", "format": "jpeg", "quality": 75},
                    {"type": "page_context"},
                ],
            },
            task_id="two-sided-commerce",
        )

    try:
        seller_catalog = capture("seller-catalog", "seller", "http://127.0.0.1:43103/catalog")
        seller_order = capture("seller-order", "seller", f"http://127.0.0.1:43103/orders/{order_id}")
        buyer_order = capture("buyer-order", "buyer", f"http://127.0.0.1:43102/orders/{order_id}")
    finally:
        closeout_session(handler, task_id="two-sided-commerce")

    def visible_text(result: dict[str, Any]) -> str:
        return "\n".join(
            str(step.get("text") or "")
            for step in result.get("results", [])
            if step.get("type") == "text"
        )

    def screenshots(result: dict[str, Any]) -> list[str]:
        return [
            str(step["screenshot_path"])
            for step in result.get("results", [])
            if step.get("type") == "screenshot" and step.get("screenshot_path")
        ]

    catalog_text = visible_text(seller_catalog)
    seller_text = visible_text(seller_order)
    buyer_text = visible_text(buyer_order)
    checks = {
        "seller_catalog_visible": title in catalog_text,
        "seller_order_visible": order_id in seller_text and transaction_id in seller_text,
        "buyer_order_visible": order_id in buyer_text and transaction_id in buyer_text,
        "buyer_issue_visible": issue_id in buyer_text,
    }
    return {
        "success": all(checks.values()),
        "checks": checks,
        "screenshots": screenshots(seller_catalog) + screenshots(seller_order) + screenshots(buyer_order),
        "final_urls": {
            "seller_catalog": seller_catalog.get("final_url"),
            "seller_order": seller_order.get("final_url"),
            "buyer_order": buyer_order.get("final_url"),
        },
    }


def api(method: str, endpoint: str, payload: dict[str, Any] | None = None, *, idem: str | None = None) -> dict[str, Any]:
    body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if idem:
        headers["Idempotency-Key"] = idem
    req = urllib.request.Request(f"{GATEWAY}{endpoint}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            parsed = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {endpoint} failed: {exc.code} {detail}") from exc
    if not parsed.get("success", True):
        raise RuntimeError(f"{method} {endpoint} failed: {parsed}")
    return parsed["data"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Two-sided local commerce proof")
    parser.add_argument("--fixture", action="store_true", default=True)
    parser.add_argument("--api-only", action="store_true", help="Skip the judged WIP browser proof")
    parser.add_argument(
        "--run-id",
        default="",
        help="Unique run id (default: ag-<unix>-<6hex> to avoid same-second collisions)",
    )
    args = parser.parse_args()

    run_id = args.run_id or f"ag-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    seller_id = f"seller-{run_id}"
    buyer_id = f"buyer-{run_id}"
    title = f"Token Nxt proof SKU {run_id}"

    created = api(
        "POST",
        "/api/demo-commerce/test-fixtures/seller/items",
        {
          "idempotency_key": f"{run_id}:item:create",
          "title": title,
          "description": "Shared local commerce item for AgentGuard two-sided proof.",
          "price_inr": 1200,
          "inventory": 4,
          "seller_id": seller_id,
        },
        idem=f"{run_id}:item:create",
    )
    item_id = created["item"]["item_id"]
    cleanup_registered = True

    def cleanup() -> None:
        nonlocal cleanup_registered
        if not cleanup_registered:
            return
        cleanup_registered = False
        try:
            api("POST", "/api/demo-commerce/test-fixtures/cleanup", {})
        except Exception:
            pass

    atexit.register(cleanup)

    published = api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/items/{item_id}/publish",
        {"idempotency_key": f"{run_id}:item:publish"},
        idem=f"{run_id}:item:publish",
    )

    query = urllib.parse.urlencode({"q": title})
    search = api("GET", f"/api/demo-commerce/buyer/search?{query}")
    found = next((item for item in search["items"] if item["item_id"] == item_id), None)
    if not found:
        raise RuntimeError(f"Published item {item_id} was not discoverable in buyer search")

    order = api(
        "POST",
        "/api/demo-commerce/test-fixtures/buyer/orders",
        {
          "idempotency_key": f"{run_id}:order:create",
          "item_id": item_id,
          "quantity": 2,
          "buyer_id": buyer_id,
          "payment_mode": "success",
        },
        idem=f"{run_id}:order:create",
    )
    order_id = order["order"]["order_id"]
    transaction_id = order["transaction_id"]

    seller_orders = api("GET", f"/api/demo-commerce/test-fixtures/seller/orders?{urllib.parse.urlencode({'seller_id': seller_id})}")
    seller_order = next((entry for entry in seller_orders["orders"] if entry["order_id"] == order_id), None)
    if not seller_order:
        raise RuntimeError(f"Order {order_id} was not visible in seller orders")

    accepted = api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/orders/{order_id}/transition",
        {"idempotency_key": f"{run_id}:order:accept", "status": "accepted"},
        idem=f"{run_id}:order:accept",
    )

    issue = api(
        "POST",
        f"/api/demo-commerce/test-fixtures/buyer/orders/{order_id}/issues",
        {
          "idempotency_key": f"{run_id}:issue:create",
          "reason": "demo_quality",
          "description": "Buyer issue created for two-sided AgentGuard proof.",
        },
        idem=f"{run_id}:issue:create",
    )
    issue_id = issue["issue"]["issue_id"]

    issues = api("GET", "/api/demo-commerce/test-fixtures/seller/issues")
    seller_issue = next((entry for entry in issues["issues"] if entry["issue_id"] == issue_id), None)
    if not seller_issue:
        raise RuntimeError(f"Issue {issue_id} was not visible in seller issues")

    response = api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/issues/{issue_id}/respond",
        {"response": "Seller acknowledged the simulated issue."},
    )
    remedy = api(
        "POST",
        f"/api/demo-commerce/test-fixtures/seller/issues/{issue_id}/remedy",
        {
          "idempotency_key": f"{run_id}:issue:remedy",
          "data": {"type": "refund", "amount_inr": 300},
        },
        idem=f"{run_id}:issue:remedy",
    )

    out = {
        "success": True,
        "run_id": run_id,
        "item_id": item_id,
        "order_id": order_id,
        "transaction_id": transaction_id,
        "issue_id": issue_id,
        "checks": {
            "seller_published_item": published["item"]["status"] == "published",
            "buyer_search_found_item": found["item_id"] == item_id,
            "buyer_checkout_created_order": order["order"]["order_id"] == order_id,
            "seller_saw_order": seller_order["transaction_id"] == transaction_id,
            "seller_transitioned_order": accepted["order"]["status"] == "accepted",
            "seller_saw_issue": seller_issue["order_id"] == order_id,
            "seller_responded": response["issue"]["status"] == "responded",
            "seller_promised_remedy": remedy["remedy"]["order_id"] == order_id,
        },
    }
    if not args.api_only:
        out["browser"] = _browser_proof(
            title=title,
            order_id=order_id,
            transaction_id=transaction_id,
            issue_id=issue_id,
        )
        out["checks"]["visible_two_sided_identity"] = out["browser"]["success"]
    out["success"] = all(out["checks"].values())
    cleanup()
    print(json.dumps(out, indent=2))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
