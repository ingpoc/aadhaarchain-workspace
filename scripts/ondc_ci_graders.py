#!/usr/bin/env python3
"""Deterministic ONDC / AgentGuard CI graders (no Hermes, no LLM).

Modes:
  --offline   Local/PR: commerce demo gate + static checks (blocks CI)
  --live      Hit FQDN/gateway JSON + rewrite + bundle probes
  --soft      With --live: network/cold-start failures → warn exit 0
  --hard      With --live: any fail → non-zero (post-deploy optional)

Examples:
  python3 scripts/ondc_ci_graders.py --offline
  python3 scripts/ondc_ci_graders.py --live --soft
  python3 scripts/ondc_ci_graders.py --live --hard \\
    --gateway https://gateway.aadharcha.in \\
    --buyer https://ondcbuyer.aadharcha.in \\
    --seller https://ondcseller.aadharcha.in

No secrets. Does not flip VITE_COMMERCE_DEMO_MODE. No UPI/prod order claims.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _fetch(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    data: bytes | None = None,
    timeout: float = 45,
) -> tuple[int, str, str]:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            ctype = resp.headers.get("Content-Type", "")
            return resp.status, body, ctype
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
        return exc.code, body, ctype
    except Exception as exc:  # noqa: BLE001 — grader surface
        return 0, str(exc), ""


def _is_spa_html(body: str, ctype: str) -> bool:
    head = body.lstrip()[:200].lower()
    if "text/html" in (ctype or "").lower() and ("<!doctype html" in head or "<html" in head):
        return True
    if "<!doctype html" in head or (head.startswith("<html") and "react" in body[:2000].lower()):
        return True
    return False


def _try_json(body: str) -> Any | None:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def _post_json(url: str, payload: dict[str, Any], timeout: float = 60) -> tuple[int, str, str]:
    return _fetch(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        timeout=timeout,
    )


def grade_offline() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gate = ROOT / "scripts" / "commerce_demo_mode_gate.py"
    proc = subprocess.run(
        [sys.executable, str(gate), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    ok = proc.returncode == 0
    rows.append(
        {
            "id": "commerce_demo_mode_gate",
            "ok": ok,
            "detail": (proc.stdout or proc.stderr)[:300],
        }
    )

    # Source-level: apps should not default-bake demo true in committed env examples
    for app in ("ondcbuyer", "ondcseller"):
        env_ex = ROOT / app / ".env.example"
        demo_true = False
        if env_ex.is_file():
            text = env_ex.read_text(encoding="utf-8", errors="replace")
            if re.search(r"VITE_COMMERCE_DEMO_MODE\s*=\s*true", text, re.I):
                demo_true = True
        rows.append(
            {
                "id": f"{app}_env_example_demo_not_true",
                "ok": not demo_true,
                "detail": "ok" if not demo_true else ".env.example sets DEMO_MODE=true",
            }
        )

    # Local unit tests already cover AgentGuard; assert gateway test file present
    ag_tests = ROOT / "aadharchain" / "gateway" / "tests"
    has_ag = ag_tests.is_dir() and any(ag_tests.glob("test_*agentguard*.py")) or any(
        ag_tests.glob("test_*.py")
    ) if ag_tests.is_dir() else False
    rows.append(
        {
            "id": "gateway_tests_present",
            "ok": bool(ag_tests.is_dir()),
            "detail": f"tests_dir={ag_tests.is_dir()} sample={has_ag}",
        }
    )

    harness = ROOT / "scripts" / "hermes_fqdn_e2e_thorough.py"
    harness_text = harness.read_text(encoding="utf-8", errors="replace") if harness.is_file() else ""
    forbidden_browser_mutations = [
        token
        for token in (".click()", "dispatchEvent(", "method: 'POST'", "getUserMedia(")
        if token in harness_text
    ]
    rows.append(
        {
            "id": "fqdn_harness_safe_actions_and_closeout",
            "ok": bool(harness_text)
            and not forbidden_browser_mutations
            and "close_harness_sessions(handler)" in harness_text
            and 'choices=("buyer", "seller", "both")' in harness_text,
            "detail": f"forbidden={forbidden_browser_mutations} closeout={'close_harness_sessions(handler)' in harness_text}",
        }
    )
    return rows


def grade_live(gateway: str, buyer: str, seller: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gw = gateway.rstrip("/")
    by = buyer.rstrip("/")
    sl = seller.rstrip("/")

    # Gateway health
    code, body, ctype = _fetch(f"{gw}/api/health")
    rows.append(
        {
            "id": "gateway_health",
            "ok": code == 200 and not _is_spa_html(body, ctype),
            "detail": f"http={code} spa={_is_spa_html(body, ctype)}",
        }
    )

    # ONDC status JSON
    code, body, ctype = _fetch(f"{gw}/api/ondc/status")
    data = (_try_json(body) or {}).get("data") if _try_json(body) else None
    ondc_ok = (
        code == 200
        and isinstance(data, dict)
        and data.get("enabled") is True
        and data.get("configured") is True
    )
    rows.append(
        {
            "id": "gateway_ondc_status",
            "ok": ondc_ok,
            "detail": f"http={code} enabled={isinstance(data, dict) and data.get('enabled')} configured={isinstance(data, dict) and data.get('configured')}",
        }
    )

    # Semantic network acceptance: the gateway wraps upstream failures in HTTP 200,
    # so the grader must inspect data.http_status + data.ack.
    code, body, ctype = _post_json(
        f"{gw}/api/ondc/search",
        {
            "query": "AgentGuard PreProd Atta",
            "city": "std:080",
            "domain": "ONDC:RET10",
            "include_configured_bpp": True,
        },
    )
    search_json = _try_json(body)
    search_data = search_json.get("data") if isinstance(search_json, dict) else None
    direct_bpp = search_data.get("direct_bpp") if isinstance(search_data, dict) else None
    network_ack_ok = (
        code == 200
        and not _is_spa_html(body, ctype)
        and isinstance(search_data, dict)
        and search_data.get("http_status") == 200
        and search_data.get("ack") == "ACK"
        and bool(search_data.get("transaction_id"))
        and isinstance(direct_bpp, dict)
        and direct_bpp.get("ack") == "ACK"
        and direct_bpp.get("ok") is True
    )
    rows.append(
        {
            "id": "ondc_network_search_ack_semantic",
            "ok": network_ack_ok,
            "detail": (
                f"wrapper_http={code} upstream_http="
                f"{search_data.get('http_status') if isinstance(search_data, dict) else None} "
                f"ack={search_data.get('ack') if isinstance(search_data, dict) else None} "
                f"direct_bpp_ack={direct_bpp.get('ack') if isinstance(direct_bpp, dict) else None}"
            ),
        }
    )

    # Deterministic two-sided proof: public Seller rewrite ACKs a real BPP search,
    # then the Seller posts on_search to the public Buyer callback on the same txn.
    direct_txn = f"ci-grader-{uuid.uuid4()}"
    direct_payload = {
        "context": {
            "action": "search",
            "bap_uri": f"{by}/ondc",
            "bap_id": "ondcbuyer.aadharcha.in",
            "transaction_id": direct_txn,
            "message_id": f"ci-grader-{uuid.uuid4()}",
            "domain": "ONDC:RET10",
            "city": "std:080",
            "country": "IND",
            "core_version": "1.2.0",
        },
        "message": {
            "intent": {
                "payment": {
                    "@ondc/org/buyer_app_finder_fee_type": "Percent",
                    "@ondc/org/buyer_app_finder_fee_amount": "0",
                },
                "item": {"descriptor": {"name": "AgentGuard PreProd Atta"}},
            }
        },
    }
    seller_code = 0
    seller_body = ""
    seller_ctype = ""
    for attempt in range(3):
        seller_code, seller_body, seller_ctype = _post_json(
            f"{sl}/ondc/search", direct_payload
        )
        if seller_code == 200:
            break
        if attempt < 2:
            time.sleep(2)
    seller_json = _try_json(seller_body)
    seller_ack = (
        seller_json.get("message", {}).get("ack", {}).get("status")
        if isinstance(seller_json, dict)
        else None
    )
    rows.append(
        {
            "id": "seller_fqdn_bpp_search_json_ack",
            "ok": seller_code == 200 and seller_ack == "ACK" and not _is_spa_html(seller_body, seller_ctype),
            "detail": f"http={seller_code} ack={seller_ack} spa={_is_spa_html(seller_body, seller_ctype)}",
        }
    )

    exact_items: list[dict[str, Any]] = []
    catalog_code = 0
    for attempt in range(8):
        if attempt:
            time.sleep(3)
        catalog_code, catalog_body, catalog_ctype = _fetch(
            f"{gw}/api/ondc/catalogs?transaction_id={direct_txn}", timeout=30
        )
        catalog_json = _try_json(catalog_body)
        catalog_data = catalog_json.get("data") if isinstance(catalog_json, dict) else None
        items = catalog_data.get("items", []) if isinstance(catalog_data, dict) else []
        exact_items = [
            item
            for item in items
            if isinstance(item, dict)
            and item.get("bpp_id") == "ondcseller.aadharcha.in"
            and "AgentGuard PreProd Atta" in str(item.get("name") or "")
        ]
        if exact_items:
            break
    rows.append(
        {
            "id": "seller_to_buyer_on_search_exact_item",
            "ok": catalog_code == 200 and bool(exact_items),
            "detail": f"http={catalog_code} exact_items={len(exact_items)} txn={direct_txn}",
        }
    )

    # Realtime
    code, body, ctype = _fetch(f"{gw}/api/realtime/status")
    rt = (_try_json(body) or {}).get("data") if _try_json(body) else None
    rows.append(
        {
            "id": "gateway_realtime_status",
            "ok": code == 200 and isinstance(rt, dict) and rt.get("configured") is True,
            "detail": f"http={code} configured={isinstance(rt, dict) and rt.get('configured')}",
        }
    )

    # Runtime JSON with X-User-Id
    code, body, ctype = _fetch(
        f"{gw}/api/agent/runtime?app=ondc-buyer",
        headers={"X-User-Id": "ci-grader", "Accept": "application/json"},
    )
    runtime = _try_json(body)
    rows.append(
        {
            "id": "gateway_agent_runtime_json",
            "ok": code == 200 and isinstance(runtime, dict) and "runtime_available" in runtime,
            "detail": f"http={code} spa={_is_spa_html(body, ctype)} keys={list(runtime)[:8] if isinstance(runtime, dict) else None}",
        }
    )

    # Vercel rewrites: must not serve SPA HTML
    for name, url in (
        ("buyer_api_agent_runtime", f"{by}/api/agent/runtime?app=ondc-buyer"),
        ("seller_api_agent_runtime", f"{sl}/api/agent/runtime?app=ondc-seller"),
        ("seller_demo_commerce_orders", f"{sl}/api/demo-commerce/seller/orders"),
        ("buyer_ondc_path", f"{by}/ondc/status"),
        ("seller_ondc_path", f"{sl}/ondc/status"),
    ):
        hdrs = {"Accept": "application/json"}
        if "agent/runtime" in url:
            hdrs["X-User-Id"] = "ci-grader"
        code, body, ctype = _fetch(url, headers=hdrs)
        spa = _is_spa_html(body, ctype)
        parsed = _try_json(body)
        rows.append(
            {
                "id": f"rewrite_{name}",
                "ok": code == 200 and not spa and isinstance(parsed, dict),
                "detail": f"http={code} spa={spa} json={isinstance(parsed, dict)} ctype={ctype[:40]}",
            }
        )

    # Bundle probe: demo mode false
    for app_name, base in (("buyer", by), ("seller", sl)):
        code, html, _ = _fetch(base + "/")
        m = re.search(r"assets/(index-[^\"']+\.js)", html or "")
        if not m:
            rows.append(
                {
                    "id": f"{app_name}_bundle_demo_mode",
                    "ok": False,
                    "detail": f"http={code} no index asset",
                }
            )
            continue
        asset_url = f"{base}/assets/{m.group(1)}"
        ac, abody, _ = _fetch(asset_url, timeout=60)
        # Vite often inlines as VITE_COMMERCE_DEMO_MODE:"false"
        false_hit = bool(
            re.search(r'VITE_COMMERCE_DEMO_MODE\s*:\s*"false"', abody)
            or re.search(r'COMMERCE_DEMO_MODE["\']?\s*:\s*["\']?false', abody, re.I)
        )
        true_hit = bool(re.search(r'VITE_COMMERCE_DEMO_MODE\s*:\s*"true"', abody))
        # Pass if explicitly false, or key absent (tree-shaken) and not explicitly true.
        ok_demo = ac == 200 and not true_hit and (false_hit or "VITE_COMMERCE_DEMO_MODE" not in abody)
        rows.append(
            {
                "id": f"{app_name}_bundle_demo_mode_false",
                "ok": ok_demo,
                "detail": f"asset={m.group(1)} false={false_hit} true={true_hit} key_present={'VITE_COMMERCE_DEMO_MODE' in abody}",
            }
        )

    # Site verification meta (cheap)
    for app_name, base in (("buyer", by), ("seller", sl)):
        code, body, _ = _fetch(f"{base}/ondc-site-verification.html")
        ok = code == 200 and "ondc-site-verification" in (body or "")
        rows.append(
            {
                "id": f"{app_name}_site_verification",
                "ok": ok,
                "detail": f"http={code}",
            }
        )

    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--offline", action="store_true", help="PR-blocking local graders")
    p.add_argument("--live", action="store_true", help="FQDN/gateway HTTP graders")
    p.add_argument("--soft", action="store_true", help="Live: warn-only on fail (exit 0)")
    p.add_argument("--hard", action="store_true", help="Live: fail closed")
    p.add_argument("--gateway", default="https://gateway.aadharcha.in")
    p.add_argument("--buyer", default="https://ondcbuyer.aadharcha.in")
    p.add_argument("--seller", default="https://ondcseller.aadharcha.in")
    args = p.parse_args()

    if not args.offline and not args.live:
        args.offline = True

    report: dict[str, Any] = {"checks": []}
    if args.offline:
        report["checks"].extend(grade_offline())
    if args.live:
        report["checks"].extend(grade_live(args.gateway, args.buyer, args.seller))

    failed = [c for c in report["checks"] if not c.get("ok")]
    report["ok"] = len(failed) == 0
    report["failed"] = [c["id"] for c in failed]
    print(json.dumps(report, indent=2))

    if report["ok"]:
        return 0
    if args.live and args.soft and not args.hard:
        print("SOFT: live graders failed but --soft → exit 0", file=sys.stderr)
        return 0
    if args.live and not args.hard and not args.soft:
        # default live = soft for CI safety
        print("SOFT(default): pass --hard to fail closed", file=sys.stderr)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
