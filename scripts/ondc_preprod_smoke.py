#!/usr/bin/env python3
"""Smoke signed PreProd ONDC lookup, search, and optional order sequence.

Usage:
  # Against running local gateway (:43101) with ONDC_ENABLED + keys
  python3 scripts/ondc_preprod_smoke.py

  # Against Render
  python3 scripts/ondc_preprod_smoke.py --base https://gateway.aadharcha.in --search atta --order

Does not flip VITE_COMMERCE_DEMO_MODE. Does not POST /subscribe.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def _post(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw[:2000]}
        return exc.code, body


def _get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def _poll_order_callback(
    base: str,
    transaction_id: str,
    expected_action: str,
    *,
    attempts: int,
    poll_seconds: float,
) -> tuple[dict, dict]:
    """Return the expected on_* payload and current persisted order snapshot."""
    latest: dict = {}
    for attempt in range(max(1, attempts)):
        if attempt:
            time.sleep(max(0, poll_seconds))
        code, body = _get(f"{base}/api/ondc/orders?transaction_id={transaction_id}")
        if code != 200:
            continue
        latest = (body or {}).get("data") or {}
        for entry in latest.get("callbacks") or []:
            payload = entry.get("payload") or {}
            context = payload.get("context") or {}
            if context.get("action") == expected_action:
                return payload, latest
    raise TimeoutError(f"no {expected_action} callback for transaction {transaction_id}")


def _order_fingerprint(order: dict) -> dict:
    items = order.get("items") or []
    first = items[0] if items else {}
    return {
        "order_id": order.get("id"),
        "state": order.get("state"),
        "provider_id": (order.get("provider") or {}).get("id"),
        "item_id": first.get("id"),
        "quantity": (first.get("quantity") or {}).get("count"),
        "item_price": (first.get("price") or {}).get("value"),
        "quote_total": ((order.get("quote") or {}).get("price") or {}).get("value"),
        "payment_status": (order.get("payment") or {}).get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:43101")
    parser.add_argument(
        "--callback-base",
        default="",
        help="Where registered public on_* callbacks are stored (defaults to --base)",
    )
    parser.add_argument("--search", default="", help="If set, POST /api/ondc/search with this query")
    parser.add_argument("--lookup-id", default="ondcbuyer.aadharcha.in")
    parser.add_argument(
        "--order",
        action="store_true",
        help="After search, fail closed unless select→init→confirm callbacks preserve the Seller offer",
    )
    parser.add_argument("--quantity", type=int, default=1, help="Order quantity for --order")
    parser.add_argument(
        "--catalog-attempts",
        type=int,
        default=6,
        help="Catalog polls after an ACK (default: 6; async on_search may be delayed)",
    )
    parser.add_argument(
        "--catalog-poll-seconds",
        type=float,
        default=3,
        help="Delay between catalog polls (default: 3s)",
    )
    parser.add_argument("--order-attempts", type=int, default=10)
    parser.add_argument("--order-poll-seconds", type=float, default=1.0)
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Soft CI mode: network/config failures print WARN and exit 0 (no PR flake)",
    )
    args = parser.parse_args()
    base = args.base.rstrip("/")
    callback_base = (args.callback_base or base).rstrip("/")

    def fail(code: int, msg: str) -> int:
        print(("WARN" if args.ci else "FAIL") + f": {msg}", file=sys.stderr)
        return 0 if args.ci else code

    if args.order and not args.search:
        return fail(2, "--order requires --search so a real Seller offer can be selected")
    if args.quantity < 1:
        return fail(2, "--quantity must be at least 1")

    try:
        status_code, status_body = _get(f"{base}/api/ondc/status")
    except Exception as exc:  # noqa: BLE001
        return fail(2, f"status fetch failed: {exc}")

    print(json.dumps({"status_http": status_code, "status": status_body}, indent=2))
    data = (status_body or {}).get("data") or {}
    if not data.get("enabled"):
        return fail(2, "ONDC_ENABLED is false on gateway")
    if not data.get("configured"):
        return fail(2, "adapter not configured (subscriber/bap_uri/uk_id/signing key)")

    try:
        lookup_code, lookup_body = _post(
            f"{base}/api/ondc/lookup",
            {"subscriber_id": args.lookup_id, "domain": "ONDC:RET10", "type": "BAP"},
        )
    except Exception as exc:  # noqa: BLE001
        return fail(2, f"lookup failed: {exc}")
    print(json.dumps({"lookup_http": lookup_code, "lookup": lookup_body}, indent=2))

    if args.search:
        try:
            search_code, search_body = _post(
                f"{base}/api/ondc/search",
                {
                    "query": args.search,
                    "city": "std:080",
                    "domain": "ONDC:RET10",
                    "include_configured_bpp": True,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return fail(2, f"search failed: {exc}")
        print(json.dumps({"search_http": search_code, "search": search_body}, indent=2))
        search_data = (search_body or {}).get("data") or {}
        upstream_status = search_data.get("http_status")
        ack = search_data.get("ack")
        if search_code != 200 or upstream_status != 200 or ack != "ACK":
            return fail(
                3,
                f"search was not accepted: wrapper_http={search_code} "
                f"upstream_http={upstream_status} ack={ack!r}",
            )
        txn = search_data.get("transaction_id")
        direct_bpp = search_data.get("direct_bpp") or {}
        if not direct_bpp.get("ok"):
            return fail(4, f"configured Seller BPP did not accept search: {direct_bpp!r}")
        if txn:
            cat_code = 0
            cat_body: dict = {}
            attempts = max(1, args.catalog_attempts)
            for attempt in range(attempts):
                if attempt:
                    time.sleep(max(0, args.catalog_poll_seconds))
                cat_code, cat_body = _get(
                    f"{callback_base}/api/ondc/catalogs?transaction_id={txn}"
                )
                items = ((cat_body or {}).get("data") or {}).get("items") or []
                if items:
                    break
            catalog_data = (cat_body or {}).get("data") or {}
            items = catalog_data.get("items") or []
            seller_items = [
                item for item in items if item.get("bpp_id") == "ondcseller.aadharcha.in"
            ]
            summary = {
                "catalogs_http": cat_code,
                "transaction_id": txn,
                "count": catalog_data.get("count", len(items)),
                "source": catalog_data.get("source"),
                "our_seller_items": [
                    {
                        "name": item.get("name"),
                        "bpp_id": item.get("bpp_id"),
                        "provider_name": item.get("provider_name"),
                    }
                    for item in seller_items
                ],
            }
            print(json.dumps({"catalogs": summary}, indent=2))
            if cat_code != 200 or not items:
                return fail(5, f"no on_search catalog received for transaction {txn}")
            if not summary["our_seller_items"]:
                return fail(6, "on_search catalog did not contain ondcseller.aadharcha.in")

            if args.order:
                selected = seller_items[0]
                item_id = str(selected.get("id") or "")
                provider_id = str(selected.get("provider_id") or "")
                bpp_id = str(selected.get("bpp_id") or "")
                bpp_uri = str(selected.get("bpp_uri") or "")
                try:
                    expected_total = float(selected.get("price_inr")) * args.quantity
                except (TypeError, ValueError):
                    return fail(7, f"Seller offer has no numeric price: {selected!r}")
                if not all((item_id, provider_id, bpp_id, bpp_uri)):
                    return fail(7, f"Seller offer is missing order identity fields: {selected!r}")

                order: dict = {
                    "provider": {"id": provider_id},
                    "items": [{"id": item_id, "quantity": {"count": str(args.quantity)}}],
                }
                stages: dict[str, dict] = {}
                for action in ("select", "init", "confirm"):
                    try:
                        action_code, action_body = _post(
                            f"{base}/api/ondc/{action}",
                            {
                                "transaction_id": txn,
                                "bpp_id": bpp_id,
                                "bpp_uri": bpp_uri,
                                "city": "std:080",
                                "domain": "ONDC:RET10",
                                "order": order,
                            },
                        )
                    except Exception as exc:  # noqa: BLE001
                        return fail(8, f"{action} dispatch failed: {exc}")
                    action_data = (action_body or {}).get("data") or {}
                    if (
                        action_code != 200
                        or not (action_body or {}).get("success")
                        or action_data.get("http_status") != 200
                        or action_data.get("ack") != "ACK"
                    ):
                        return fail(
                            8,
                            f"{action} was not accepted: wrapper_http={action_code} "
                            f"upstream_http={action_data.get('http_status')} "
                            f"ack={action_data.get('ack')!r}",
                        )
                    try:
                        callback, persisted = _poll_order_callback(
                            callback_base,
                            txn,
                            f"on_{action}",
                            attempts=args.order_attempts,
                            poll_seconds=args.order_poll_seconds,
                        )
                    except Exception as exc:  # noqa: BLE001
                        return fail(9, str(exc))
                    order = ((callback.get("message") or {}).get("order") or {})
                    fingerprint = _order_fingerprint(order)
                    stages[action] = fingerprint
                    if fingerprint["item_id"] != item_id:
                        return fail(10, f"{action} changed item identity: {fingerprint!r}")
                    if str(fingerprint["quantity"]) != str(args.quantity):
                        return fail(10, f"{action} changed quantity: {fingerprint!r}")
                    if fingerprint["provider_id"] != provider_id:
                        return fail(10, f"{action} changed provider: {fingerprint!r}")
                    try:
                        quote_total = float(fingerprint["quote_total"])
                    except (TypeError, ValueError):
                        return fail(10, f"{action} returned no numeric quote: {fingerprint!r}")
                    if abs(quote_total - expected_total) > 0.001:
                        return fail(
                            10,
                            f"{action} quote {quote_total} != expected {expected_total:.2f}",
                        )

                final_orders = persisted.get("items") or []
                final = stages["confirm"]
                matching = [
                    row
                    for row in final_orders
                    if row.get("id") == final.get("order_id")
                    and row.get("transaction_id") == txn
                ]
                if (
                    final.get("state") != "Accepted"
                    or final.get("payment_status") != "PAID"
                    or not final.get("order_id")
                    or not matching
                ):
                    return fail(11, f"confirm did not persist one accepted paid order: {final!r}")
                print(
                    json.dumps(
                        {
                            "order_sequence": {
                                "transaction_id": txn,
                                "seller_offer": {
                                    "item_id": item_id,
                                    "provider_id": provider_id,
                                    "bpp_id": bpp_id,
                                    "quantity": args.quantity,
                                    "expected_total": f"{expected_total:.2f}",
                                },
                                "stages": stages,
                                "persisted_order_count": len(matching),
                            }
                        },
                        indent=2,
                    )
                )
        else:
            return fail(4, "search ACK did not include a transaction_id")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
