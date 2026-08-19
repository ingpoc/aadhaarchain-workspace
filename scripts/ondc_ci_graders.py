#!/usr/bin/env python3
"""Deterministic ONDC / AgentGuard CI graders (no Hermes, no LLM).

Modes:
  --offline   Local/PR: commerce demo gate + 2026-08-19 P0 test scanners (blocks CI)
  --live      Read-only FQDN/gateway JSON + rewrite + bundle probes
  --protocol-search  With --live: explicitly dispatch bounded PreProd searches
  --bundle-parity  Compare assets/index-*.js on vercel.app vs public FQDN
  --vercel-project-identity  Fail if pulled project is ondc-buyer/ondc-seller
  --soft      With --live: network/cold-start failures → warn exit 0
              With --bundle-parity: advisory only (deploy must omit --soft)
  --hard      With --live: any fail → non-zero (post-deploy optional)

Examples:
  python3 scripts/ondc_ci_graders.py --offline
  python3 scripts/ondc_ci_graders.py --live --soft
  python3 scripts/ondc_ci_graders.py --live --hard \\
    --gateway https://gateway.aadharcha.in \\
    --buyer https://ondcbuyer.aadharcha.in \\
    --seller https://ondcseller.aadharcha.in
  python3 scripts/ondc_ci_graders.py --bundle-parity
  python3 scripts/ondc_ci_graders.py --vercel-project-identity buyer \\
    --project-json .vercel/project.json

No secrets. Does not flip VITE_COMMERCE_DEMO_MODE. No UPI/prod order claims.
Bundle parity is fail-closed on Portfolio Deploy: HTTP 200 on the FQDN is not
enough if the custom domain still serves a different index-*.js than production.
"""
from __future__ import annotations

import argparse
import inspect
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _git_worktree_roots(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        return []
    return [
        Path(line.removeprefix("worktree "))
        for line in completed.stdout.splitlines()
        if line.startswith("worktree ")
    ]


def _gateway_tests(root: Path, worktrees: list[Path] | None = None) -> tuple[Path, str]:
    roots = [root, *(worktrees if worktrees is not None else _git_worktree_roots(root))]
    for candidate_root in dict.fromkeys(path.resolve() for path in roots):
        tests = candidate_root / "aadharchain" / "gateway" / "tests"
        if tests.is_dir() and any(tests.glob("test_*.py")):
            return tests, "current" if candidate_root == root.resolve() else "git-worktree"
    return root / "aadharchain" / "gateway" / "tests", "missing"


def _nested_app_root(
    root: Path,
    name: str,
    *,
    marker: str,
    worktrees: list[Path] | None = None,
) -> tuple[Path, str]:
    roots = [root, *(worktrees if worktrees is not None else _git_worktree_roots(root))]
    for candidate_root in dict.fromkeys(path.resolve() for path in roots):
        app = candidate_root / name
        if (app / marker).exists():
            return app, "current" if candidate_root == root.resolve() else "git-worktree"
    return root / name, "missing"


def _iter_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    skip_parts = {"node_modules", ".git", "dist", "build", "__pycache__"}
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path for path in root.rglob(pattern) if path.is_file())
    return sorted({path for path in files if not skip_parts.intersection(path.parts)})


def _tree_text(root: Path, patterns: tuple[str, ...]) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in _iter_files(root, patterns)
    )


def _missing_needles(text: str, needles: tuple[str, ...]) -> list[str]:
    return [needle for needle in needles if needle not in text]


# Landed 2026-08-19 P0 regression names/assertions. Emptying or deleting these
# tests must fail the offline grader. Buyer: ondc-buyer#8. Seller: ondc-seller#8.
# Gateway: aadhaar-chain#7 (fail closed until that tree is on main).
BUYER_P0_TEST_GLOBS = ("*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx")
SELLER_P0_TEST_GLOBS = BUYER_P0_TEST_GLOBS
GATEWAY_P0_TEST_GLOBS = ("test_*.py",)

BUYER_P0_NEEDLES = (
    "does not ensure or resume a paused agent when reading status",
    "does not resume AgentGuard authority just by opening chat",
    "stays paused across opening Samantha and verifying an Intent Receipt",
    "Resume shopping agent",
    "/ensure",
    "/resume",
    "does not silently drop a guest add",
    "shows a sign-in notice instead of a silent no-op",
    "Sign in to check out.",
    "collapses a duplicated state value instead of showing KarnatakaKarnataka",
    "does not navigate away for guests or after items were already present",
    "opens the Agent Guard tab from /config?tab=agent-guard",
    "KarnatakaKarnataka",
    "shouldRedirectEmptyCheckout",
)

SELLER_P0_NEEDLES = (
    "keeps store setup editable when the store record is not found",
    "does not treat a 404 from the store API as a fatal setup block",
    "Store setup unavailable",
    "refund_issue reports AgentGuard need_approval",
    "approved and executed",
    "refund_issue does not execute or celebrate a missing order",
    "refund_issue reports AgentGuard deny while paused",
    "stays on /dashboard instead of auto-redirecting to store setup",
    "asks a signed-out deep link to sign in and keeps the return-to path",
    "signin-return-to",
)

GATEWAY_P0_NEEDLES = (
    "test_order_short_id_is_a_hex_prefix_not_a_uuid",
    "test_seller_store_get_empty_is_200_not_404",
    "test_seller_refund_over_limit_needs_approval_and_missing_order_is_not_executed",
    "test_postgres_seller_store_get_empty_is_200_not_404",
    "test_same_principal_buyer_checkout_lists_on_seller_and_short_id",
    "test_seller_refund_over_limit_and_missing_order_are_server_enforced",
    "7BA6FE24",
    "_order_hex_prefix",
    '_order_hex_prefix("order_missing") is None',
    "need_approval",
    "resource_not_found",
    "/api/demo-commerce/seller/store",
    "display_id",
    "/api/demo-commerce/seller/orders/{display_id}",
)

GATEWAY_P0_HINT = (
    "gateway_p0_regression_tests_missing - need aadharchain tests from "
    "https://github.com/ingpoc/aadhaar-chain/pull/7"
)
BUYER_P0_HINT = (
    "buyer_p0_regression_tests_missing - need ondcbuyer tests from "
    "https://github.com/ingpoc/ondc-buyer/pull/8"
)
SELLER_P0_HINT = (
    "seller_p0_regression_tests_missing - need ondcseller tests from "
    "https://github.com/ingpoc/ondc-seller/pull/8"
)


def _p0_scan_row(
    *,
    tree: Path,
    source: str,
    present_id: str,
    missing_id: str,
    needles: tuple[str, ...],
    patterns: tuple[str, ...],
    hint: str,
    required: bool,
) -> dict[str, Any]:
    if source == "missing" or not tree.exists():
        return {
            "id": missing_id if required else present_id,
            "ok": not required,
            "detail": hint if required else f"skipped: {tree.name} tree not present",
        }
    text = _tree_text(tree, patterns)
    missing = _missing_needles(text, needles)
    if missing:
        shown = missing if len(missing) <= 8 else [*missing[:8], f"...+{len(missing) - 8}"]
        return {
            "id": missing_id,
            "ok": False,
            "detail": f"source={source} missing={shown} {hint}",
        }
    return {
        "id": present_id,
        "ok": True,
        "detail": f"source={source} files={len(_iter_files(tree, patterns))}",
    }


def grade_p0_regression(
    root: Path,
    *,
    worktrees: list[Path] | None = None,
    require_app_trees: bool = False,
) -> list[dict[str, Any]]:
    """Fail closed if 2026-08-19 Buyer/Seller/Gateway P0 tests were deleted or emptied."""
    buyer_root, buyer_source = _nested_app_root(
        root, "ondcbuyer", marker="package.json", worktrees=worktrees
    )
    seller_root, seller_source = _nested_app_root(
        root, "ondcseller", marker="package.json", worktrees=worktrees
    )
    gateway_tests, gateway_source = _gateway_tests(root, worktrees)
    return [
        _p0_scan_row(
            tree=buyer_root,
            source=buyer_source,
            present_id="buyer_p0_regression_tests",
            missing_id="buyer_p0_regression_tests_missing",
            needles=BUYER_P0_NEEDLES,
            patterns=BUYER_P0_TEST_GLOBS,
            hint=BUYER_P0_HINT,
            required=require_app_trees,
        ),
        _p0_scan_row(
            tree=seller_root,
            source=seller_source,
            present_id="seller_p0_regression_tests",
            missing_id="seller_p0_regression_tests_missing",
            needles=SELLER_P0_NEEDLES,
            patterns=SELLER_P0_TEST_GLOBS,
            hint=SELLER_P0_HINT,
            required=require_app_trees,
        ),
        _p0_scan_row(
            tree=gateway_tests,
            source=gateway_source,
            present_id="gateway_p0_regression_tests",
            missing_id="gateway_p0_regression_tests_missing",
            needles=GATEWAY_P0_NEEDLES,
            patterns=GATEWAY_P0_TEST_GLOBS,
            hint=GATEWAY_P0_HINT,
            required=True,
        ),
    ]


def _write_needles(path: Path, needles: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(needles) + "\n", encoding="utf-8")


def _self_test_p0() -> None:
    with tempfile.TemporaryDirectory(prefix="ondc-ci-p0-") as directory:
        base = Path(directory)
        empty = base / "empty"
        empty.mkdir()
        missing_rows = grade_p0_regression(
            empty, worktrees=[], require_app_trees=True
        )
        missing_ids = {row["id"] for row in missing_rows if not row["ok"]}
        assert missing_ids == {
            "buyer_p0_regression_tests_missing",
            "seller_p0_regression_tests_missing",
            "gateway_p0_regression_tests_missing",
        }, missing_ids
        skipped = grade_p0_regression(empty, worktrees=[], require_app_trees=False)
        assert all(
            row["ok"]
            for row in skipped
            if row["id"] in {"buyer_p0_regression_tests", "seller_p0_regression_tests"}
        )
        assert any(
            row["id"] == "gateway_p0_regression_tests_missing" and not row["ok"]
            for row in skipped
        )

        weak = base / "weak"
        weak_gateway = weak / "aadharchain" / "gateway" / "tests" / "test_placeholder.py"
        weak_gateway.parent.mkdir(parents=True)
        weak_gateway.write_text("def test_placeholder(): pass\n", encoding="utf-8")
        _write_needles(weak / "ondcbuyer" / "package.json", ('{"name":"ondc-buyer"}',))
        _write_needles(
            weak / "ondcbuyer" / "src" / "pages" / "CheckoutPage.test.tsx",
            ("it('unrelated') {}",),
        )
        _write_needles(weak / "ondcseller" / "package.json", ('{"name":"ondc-seller"}',))
        _write_needles(
            weak / "ondcseller" / "src" / "pages" / "BusinessPage.test.tsx",
            ("it('unrelated') {}",),
        )
        weak_rows = grade_p0_regression(weak, worktrees=[], require_app_trees=True)
        assert {row["id"] for row in weak_rows if not row["ok"]} == {
            "buyer_p0_regression_tests_missing",
            "seller_p0_regression_tests_missing",
            "gateway_p0_regression_tests_missing",
        }

        good = base / "good"
        _write_needles(good / "ondcbuyer" / "package.json", ('{"name":"ondc-buyer"}',))
        _write_needles(
            good / "ondcbuyer" / "src" / "pages" / "BuyerP0.test.tsx",
            BUYER_P0_NEEDLES,
        )
        _write_needles(good / "ondcseller" / "package.json", ('{"name":"ondc-seller"}',))
        _write_needles(
            good / "ondcseller" / "src" / "pages" / "SellerP0.test.tsx",
            SELLER_P0_NEEDLES,
        )
        _write_needles(
            good / "aadharchain" / "gateway" / "tests" / "test_p0_regressions.py",
            GATEWAY_P0_NEEDLES,
        )
        good_rows = grade_p0_regression(good, worktrees=[], require_app_trees=True)
        assert all(row["ok"] for row in good_rows), good_rows
        assert {row["id"] for row in good_rows} == {
            "buyer_p0_regression_tests",
            "seller_p0_regression_tests",
            "gateway_p0_regression_tests",
        }


def _self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="ondc-ci-graders-") as directory:
        base = Path(directory)
        current = base / "current"
        primary = base / "primary"
        current.mkdir()
        test_file = primary / "aadharchain" / "gateway" / "tests" / "test_ondc.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def test_placeholder(): pass\n", encoding="utf-8")
        resolved, source = _gateway_tests(current, [current, primary])
        assert resolved == test_file.parent.resolve() and source == "git-worktree"
        local_test = current / "aadharchain" / "gateway" / "tests" / "test_local.py"
        local_test.parent.mkdir(parents=True)
        local_test.write_text("def test_placeholder(): pass\n", encoding="utf-8")
        resolved, source = _gateway_tests(current, [primary])
        assert resolved == local_test.parent.resolve() and source == "current"
    _self_test_p0()
    _self_test_bundle_parity()
    signature = inspect.signature(grade_live)
    assert signature.parameters["protocol_search"].default is False
    live_source = inspect.getsource(grade_live)
    assert "_post_json(" not in live_source and "if protocol_search:" in live_source
    print(json.dumps({"ok": True, "self_test": "gateway-worktree-p0-live-readonly-bundle-parity"}))
    return 0


def _self_test_bundle_parity() -> None:
    html_new = '<script type="module" src="/assets/index-BNEIAZ9p.js"></script>'
    html_old = '<script type="module" src="/assets/index-XX7NQ1aR.js"></script>'
    assert extract_index_bundle(html_new) == "index-BNEIAZ9p.js"
    assert extract_index_bundle(html_old) == "index-XX7NQ1aR.js"
    assert extract_index_bundle("<html></html>") is None
    assert (
        deployment_url_from_vercel_json({"url": "ondcbuyer-abc.vercel.app"})
        == "https://ondcbuyer-abc.vercel.app"
    )
    assert (
        deployment_url_from_vercel_json({"url": "https://ondcbuyer.vercel.app/"})
        == "https://ondcbuyer.vercel.app"
    )
    assert (
        deployment_url_from_vercel_json(
            {"deployment": {"url": "https://ondcseller-xyz.vercel.app"}}
        )
        == "https://ondcseller-xyz.vercel.app"
    )
    assert (
        deployment_url_from_vercel_output(
            'hint\n{"url":"https://ondcbuyer-abc.vercel.app","readyState":"READY"}\n'
        )
        == "https://ondcbuyer-abc.vercel.app"
    )
    with tempfile.TemporaryDirectory(prefix="ondc-ci-parity-") as directory:
        path = Path(directory) / "project.json"
        path.write_text(json.dumps({"projectName": "ondcbuyer"}), encoding="utf-8")
        assert grade_vercel_project_identity(path, "buyer")["ok"]
        path.write_text(json.dumps({"projectName": "ondc-buyer"}), encoding="utf-8")
        hyphen = grade_vercel_project_identity(path, "buyer")
        assert not hyphen["ok"] and "ondcbuyer" in hyphen["detail"]
        path.write_text(json.dumps({"name": "ondcseller"}), encoding="utf-8")
        assert grade_vercel_project_identity(path, "seller")["ok"]
        path.write_text(json.dumps({"projectName": "ondc-seller"}), encoding="utf-8")
        assert not grade_vercel_project_identity(path, "seller")["ok"]
        missing = grade_vercel_project_identity(path.parent / "missing.json", "buyer")
        assert not missing["ok"]


def _fetch(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    data: bytes | None = None,
    timeout: float = 45,
    retries: int | None = None,
) -> tuple[int, str, str]:
    if retries is None:
        retries = 11 if method.upper() == "GET" else 1
    attempts = max(1, retries)
    transient = {0, 429, 502, 503, 504}
    result: tuple[int, str, str] = (0, "request not attempted", "")
    for attempt in range(attempts):
        req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                ctype = resp.headers.get("Content-Type", "")
                result = (resp.status, body, ctype)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
            result = (exc.code, body, ctype)
        except Exception as exc:  # noqa: BLE001 — grader surface
            result = (0, str(exc), "")
        if result[0] not in transient or attempt == attempts - 1:
            return result
        time.sleep(3)
    return result


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


INDEX_ASSET_RE = re.compile(r"assets/(index-[^\"']+\.js)")
NO_CACHE_HEADERS = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
CANONICAL_VERCEL_APP = {
    "buyer": "https://ondcbuyer.vercel.app",
    "seller": "https://ondcseller.vercel.app",
}
CANONICAL_PUBLIC_FQDN = {
    "buyer": "https://ondcbuyer.aadharcha.in",
    "seller": "https://ondcseller.aadharcha.in",
}
EXPECTED_VERCEL_PROJECT = {
    "buyer": "ondcbuyer",
    "seller": "ondcseller",
}
HYPHEN_VERCEL_PROJECT = {
    "buyer": "ondc-buyer",
    "seller": "ondc-seller",
}
BUNDLE_PARITY_HINT = (
    "custom domain is not serving this production; 2026-08-19 trap: FQDNs must "
    "live on Vercel projects ondcbuyer/ondcseller (no hyphen), not "
    "ondc-buyer/ondc-seller"
)


def extract_index_bundle(html: str) -> str | None:
    match = INDEX_ASSET_RE.search(html or "")
    return match.group(1) if match else None


def normalize_http_url(url: str) -> str:
    text = (url or "").strip()
    if not text:
        return ""
    if text.startswith("//"):
        text = "https:" + text
    elif not text.startswith(("http://", "https://")):
        text = "https://" + text
    return text.rstrip("/")


def deployment_url_from_vercel_json(payload: Any) -> str:
    data = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(data, dict):
        return ""
    url = data.get("url")
    deployment = data.get("deployment")
    if not url and isinstance(deployment, dict):
        url = deployment.get("url")
    return normalize_http_url(str(url or ""))


def deployment_url_from_vercel_output(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    try:
        return deployment_url_from_vercel_json(json.loads(raw))
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            return ""
        try:
            return deployment_url_from_vercel_json(json.loads(raw[start : end + 1]))
        except json.JSONDecodeError:
            return ""


def grade_vercel_project_identity(project_json: Path, role: str) -> dict[str, Any]:
    expected = EXPECTED_VERCEL_PROJECT[role]
    forbidden = HYPHEN_VERCEL_PROJECT[role]
    check_id = f"{role}_vercel_project_identity"
    if not project_json.is_file():
        return {
            "id": check_id,
            "ok": False,
            "detail": f"missing {project_json} — vercel pull must create project.json",
        }
    try:
        data = json.loads(project_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"id": check_id, "ok": False, "detail": f"invalid JSON: {exc}"}
    if not isinstance(data, dict):
        return {"id": check_id, "ok": False, "detail": "project.json is not an object"}
    name = str(data.get("projectName") or data.get("name") or "").strip()
    if name == expected:
        return {"id": check_id, "ok": True, "detail": f"projectName={name}"}
    if name == forbidden:
        return {
            "id": check_id,
            "ok": False,
            "detail": (
                f"projectName={name} is the hyphen twin; VERCEL_PROJECT_ID_"
                f"{role.upper()} must target Hobby project {expected} on "
                "ingpoc's projects. Git is not connected; CLI --prod only."
            ),
        }
    return {
        "id": check_id,
        "ok": False,
        "detail": f"projectName={name!r} expected {expected} (not {forbidden})",
    }


def grade_index_bundle_parity(
    check_id: str,
    left_url: str,
    right_url: str,
    *,
    attempts: int = 8,
    sleep_seconds: float = 8,
) -> dict[str, Any]:
    left = normalize_http_url(left_url)
    right = normalize_http_url(right_url)
    last_detail = "parity not attempted"
    for attempt in range(attempts):
        left_code, left_html, _ = _fetch(
            left, headers=NO_CACHE_HEADERS, timeout=30, retries=2
        )
        right_code, right_html, _ = _fetch(
            right, headers=NO_CACHE_HEADERS, timeout=30, retries=2
        )
        left_bundle = extract_index_bundle(left_html)
        right_bundle = extract_index_bundle(right_html)
        matched = (
            left_code == 200
            and right_code == 200
            and bool(left_bundle)
            and left_bundle == right_bundle
        )
        last_detail = (
            f"left={left} http={left_code} bundle={left_bundle} "
            f"right={right} http={right_code} bundle={right_bundle} "
            f"attempts={attempt + 1}"
        )
        if matched:
            return {"id": check_id, "ok": True, "detail": last_detail}
        if attempt < attempts - 1:
            time.sleep(sleep_seconds)
    return {
        "id": check_id,
        "ok": False,
        "detail": f"{last_detail} {BUNDLE_PARITY_HINT}",
    }


def grade_bundle_parity_pairs(
    pairs: list[tuple[str, str, str]],
) -> list[dict[str, Any]]:
    return [
        grade_index_bundle_parity(check_id, left_url, right_url)
        for check_id, left_url, right_url in pairs
    ]


def grade_protocol_search(gw: str, by: str, sl: str) -> list[dict[str, Any]]:
    """Dispatch bounded PreProd searches only after explicit authorization."""
    rows: list[dict[str, Any]] = []
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
                "item": {"descriptor": {"name": "Sampoorna Whole Wheat Atta"}},
            }
        },
    }
    seller_code = 0
    seller_body = ""
    seller_ctype = ""
    seller_attempts = 0
    for attempt in range(10):
        seller_attempts = attempt + 1
        seller_code, seller_body, seller_ctype = _post_json(
            f"{sl}/ondc/search", direct_payload
        )
        if seller_code == 200:
            break
        if attempt < 9:
            time.sleep(3)
    seller_json = _try_json(seller_body)
    seller_ack = (
        seller_json.get("message", {}).get("ack", {}).get("status")
        if isinstance(seller_json, dict)
        else None
    )
    rows.append(
        {
            "id": "seller_fqdn_bpp_search_json_ack",
            "ok": seller_code == 200
            and seller_ack == "ACK"
            and not _is_spa_html(seller_body, seller_ctype),
            "detail": (
                f"http={seller_code} ack={seller_ack} "
                f"spa={_is_spa_html(seller_body, seller_ctype)} attempts={seller_attempts}"
            ),
        }
    )

    exact_items: list[dict[str, Any]] = []
    catalog_code = 0
    for attempt in range(8):
        if attempt:
            time.sleep(3)
        catalog_code, catalog_body, _ = _fetch(
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
            and "Sampoorna Whole Wheat Atta" in str(item.get("name") or "")
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

    code, body, ctype = _post_json(
        f"{gw}/api/ondc/search",
        {
            "query": "Sampoorna Whole Wheat Atta",
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
    return rows


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

    # CI checks out the ignored nested gateway into ROOT; local Git worktrees
    # reuse the primary worktree's independent nested checkout.
    ag_tests, ag_tests_source = _gateway_tests(ROOT)
    has_ag = ag_tests.is_dir() and any(ag_tests.glob("test_*.py"))
    rows.append(
        {
            "id": "gateway_tests_present",
            "ok": has_ag,
            "detail": (
                f"tests_dir={ag_tests.is_dir()} sample={has_ag} "
                f"source={ag_tests_source}"
            ),
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

    # 2026-08-19 P0: fail if Buyer/Seller/Gateway regression tests were deleted
    # or emptied. Nested apps are gitignored locally; CI checks them out.
    rows.extend(
        grade_p0_regression(
            ROOT,
            require_app_trees=os.environ.get("GITHUB_ACTIONS") == "true",
        )
    )
    return rows


def grade_live(
    gateway: str,
    buyer: str,
    seller: str,
    protocol_search: bool = False,
) -> list[dict[str, Any]]:
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

    if protocol_search:
        rows.extend(grade_protocol_search(gw, by, sl))

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
    for name, url, expected_codes in (
        ("buyer_api_agent_runtime", f"{by}/api/agent/runtime?app=ondc-buyer", {200}),
        ("seller_api_agent_runtime", f"{sl}/api/agent/runtime?app=ondc-seller", {200}),
        ("seller_commerce_orders_auth_boundary", f"{sl}/api/demo-commerce/seller/orders", {401, 403}),
        ("seller_commerce_store_auth_boundary", f"{sl}/api/demo-commerce/seller/store", {401, 403}),
        ("buyer_ondc_path", f"{by}/ondc/status", {200}),
        ("seller_ondc_path", f"{sl}/ondc/status", {200}),
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
                "ok": code in expected_codes and not spa and isinstance(parsed, dict),
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
    p.add_argument(
        "--protocol-search",
        action="store_true",
        help="With --live, explicitly dispatch bounded PreProd search checks",
    )
    p.add_argument(
        "--bundle-parity",
        action="store_true",
        help="Compare assets/index-*.js between vercel.app production and public FQDN",
    )
    p.add_argument(
        "--vercel-project-identity",
        choices=sorted(EXPECTED_VERCEL_PROJECT),
        help="Fail closed if .vercel/project.json is the hyphen twin project",
    )
    p.add_argument("--project-json", type=Path, help="Path to .vercel/project.json")
    p.add_argument(
        "--print-deploy-url",
        type=Path,
        help="Read Vercel CLI --format=json output and print the deployment URL",
    )
    p.add_argument("--parity-from", help="Left URL for a single index-*.js comparison")
    p.add_argument("--parity-to", help="Right URL for a single index-*.js comparison")
    p.add_argument("--parity-id", default="index_bundle_parity")
    p.add_argument(
        "--buyer-production",
        default="",
        help="Buyer vercel.app or unique --prod deployment URL",
    )
    p.add_argument(
        "--seller-production",
        default="",
        help="Seller vercel.app or unique --prod deployment URL",
    )
    p.add_argument("--self-test", action="store_true", help="Run deterministic grader checks")
    p.add_argument("--soft", action="store_true", help="Live/parity: warn-only on fail (exit 0)")
    p.add_argument("--hard", action="store_true", help="Live: fail closed")
    p.add_argument("--gateway", default="https://gateway.aadharcha.in")
    p.add_argument("--buyer", default=CANONICAL_PUBLIC_FQDN["buyer"])
    p.add_argument("--seller", default=CANONICAL_PUBLIC_FQDN["seller"])
    args = p.parse_args()

    if args.protocol_search and not args.live:
        p.error("--protocol-search requires --live")
    if args.vercel_project_identity and not args.project_json:
        p.error("--vercel-project-identity requires --project-json")
    if (args.parity_from or args.parity_to) and not (args.parity_from and args.parity_to):
        p.error("--parity-from and --parity-to are required together")
    if (args.parity_from or args.parity_to) and not args.bundle_parity:
        p.error("--parity-from/--parity-to require --bundle-parity")
    if (args.buyer_production or args.seller_production) and not args.bundle_parity:
        p.error("--buyer-production/--seller-production require --bundle-parity")
    if args.self_test:
        return _self_test()
    if args.print_deploy_url:
        url = deployment_url_from_vercel_output(
            args.print_deploy_url.read_text(encoding="utf-8")
        )
        if not url:
            print("Vercel deploy JSON missing url", file=sys.stderr)
            return 1
        print(url)
        return 0

    identity_or_parity = bool(args.vercel_project_identity or args.bundle_parity)
    if not args.offline and not args.live and not identity_or_parity:
        args.offline = True

    report: dict[str, Any] = {"checks": []}
    if args.vercel_project_identity:
        report["checks"].append(
            grade_vercel_project_identity(args.project_json, args.vercel_project_identity)
        )
    if args.offline:
        report["checks"].extend(grade_offline())
    live_ids: set[str] = set()
    if args.live:
        live_rows = grade_live(
            args.gateway,
            args.buyer,
            args.seller,
            protocol_search=args.protocol_search,
        )
        live_ids = {row["id"] for row in live_rows}
        report["checks"].extend(live_rows)
    parity_ids: set[str] = set()
    if args.bundle_parity:
        pairs: list[tuple[str, str, str]] = []
        if args.parity_from and args.parity_to:
            pairs.append((args.parity_id, args.parity_from, args.parity_to))
        if args.buyer_production:
            pairs.append(
                ("buyer_index_bundle_parity", args.buyer_production, args.buyer)
            )
        if args.seller_production:
            pairs.append(
                ("seller_index_bundle_parity", args.seller_production, args.seller)
            )
        if not pairs:
            pairs = [
                (
                    "buyer_index_bundle_parity",
                    CANONICAL_VERCEL_APP["buyer"],
                    args.buyer,
                ),
                (
                    "seller_index_bundle_parity",
                    CANONICAL_VERCEL_APP["seller"],
                    args.seller,
                ),
            ]
        parity_rows = grade_bundle_parity_pairs(pairs)
        parity_ids = {row["id"] for row in parity_rows}
        report["checks"].extend(parity_rows)

    failed = [c for c in report["checks"] if not c.get("ok")]
    report["ok"] = len(failed) == 0
    report["failed"] = [c["id"] for c in failed]
    print(json.dumps(report, indent=2))

    if report["ok"]:
        return 0

    live_soft = args.live and not args.hard
    parity_soft = args.bundle_parity and args.soft and not args.hard
    blocking: list[str] = []
    advisory: list[str] = []
    for check in failed:
        cid = str(check.get("id", ""))
        if cid.endswith("_vercel_project_identity"):
            blocking.append(cid)
        elif cid in parity_ids:
            (advisory if parity_soft else blocking).append(cid)
        elif cid in live_ids:
            (advisory if live_soft else blocking).append(cid)
        else:
            blocking.append(cid)
    if advisory and not blocking:
        print(
            f"SOFT: advisory failures {advisory} → exit 0",
            file=sys.stderr,
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
