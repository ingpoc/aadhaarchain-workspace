#!/usr/bin/env python3
"""Smoke signed PreProd ONDC lookup (+ optional search) via local or live gateway.

Usage:
  # Against running local gateway (:43101) with ONDC_ENABLED + keys
  python3 scripts/ondc_preprod_smoke.py

  # Against Render
  python3 scripts/ondc_preprod_smoke.py --base https://gateway.aadharcha.in --search banana

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:43101")
    parser.add_argument("--search", default="", help="If set, POST /api/ondc/search with this query")
    parser.add_argument("--lookup-id", default="ondcbuyer.aadharcha.in")
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
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Soft CI mode: network/config failures print WARN and exit 0 (no PR flake)",
    )
    args = parser.parse_args()
    base = args.base.rstrip("/")

    def fail(code: int, msg: str) -> int:
        print(("WARN" if args.ci else "FAIL") + f": {msg}", file=sys.stderr)
        return 0 if args.ci else code

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
                {"query": args.search, "city": "std:080", "domain": "ONDC:RET10"},
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
        if txn:
            cat_code = 0
            cat_body: dict = {}
            attempts = max(1, args.catalog_attempts)
            for attempt in range(attempts):
                if attempt:
                    time.sleep(max(0, args.catalog_poll_seconds))
                cat_code, cat_body = _get(
                    f"{base}/api/ondc/catalogs?transaction_id={txn}"
                )
                items = ((cat_body or {}).get("data") or {}).get("items") or []
                if items:
                    break
            catalog_data = (cat_body or {}).get("data") or {}
            items = catalog_data.get("items") or []
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
                    for item in items
                    if item.get("bpp_id") == "ondcseller.aadharcha.in"
                ],
            }
            print(json.dumps({"catalogs": summary}, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
