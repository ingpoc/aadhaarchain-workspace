#!/usr/bin/env python3
"""Two-sided AgentGuard commerce proof via the local demo-commerce API."""
from __future__ import annotations

import argparse
import json
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GATEWAY = "http://127.0.0.1:43101"


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
        "/api/demo-commerce/seller/items",
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

    published = api(
        "POST",
        f"/api/demo-commerce/seller/items/{item_id}/publish",
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
        "/api/demo-commerce/buyer/orders",
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

    seller_orders = api("GET", f"/api/demo-commerce/seller/orders?{urllib.parse.urlencode({'seller_id': seller_id})}")
    seller_order = next((entry for entry in seller_orders["orders"] if entry["order_id"] == order_id), None)
    if not seller_order:
        raise RuntimeError(f"Order {order_id} was not visible in seller orders")

    accepted = api(
        "POST",
        f"/api/demo-commerce/seller/orders/{order_id}/transition",
        {"idempotency_key": f"{run_id}:order:accept", "status": "accepted"},
        idem=f"{run_id}:order:accept",
    )

    issue = api(
        "POST",
        f"/api/demo-commerce/buyer/orders/{order_id}/issues",
        {
          "idempotency_key": f"{run_id}:issue:create",
          "reason": "demo_quality",
          "description": "Buyer issue created for two-sided AgentGuard proof.",
        },
        idem=f"{run_id}:issue:create",
    )
    issue_id = issue["issue"]["issue_id"]

    issues = api("GET", "/api/demo-commerce/seller/issues")
    seller_issue = next((entry for entry in issues["issues"] if entry["issue_id"] == issue_id), None)
    if not seller_issue:
        raise RuntimeError(f"Issue {issue_id} was not visible in seller issues")

    response = api(
        "POST",
        f"/api/demo-commerce/seller/issues/{issue_id}/respond",
        {"response": "Seller acknowledged the simulated issue."},
    )
    remedy = api(
        "POST",
        f"/api/demo-commerce/seller/issues/{issue_id}/remedy",
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
    out["success"] = all(out["checks"].values())
    print(json.dumps(out, indent=2))
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
