#!/usr/bin/env python3
"""Fail-closed owner / CI instruction drift checks (offline, no nested apps, no LLM).

Catches the class of stale status that PR #9 fixed: AGENTS / IMPLEMENTATIONPLAN
claiming outdated PreProd catalog emptiness while `.voice/progress.md` owns
current Gate 1–3 evidence. Also asserts Portfolio CI wiring stays fail-closed
for unique graders and keeps live FQDN probes advisory.

Usage:
  python3 scripts/verify_owner_drift.py
  python3 scripts/verify_owner_drift.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Phrases that were live stale status in AGENTS before the Gate 1–3 reconcile.
# Keep narrow — historical evidence docs may still narrate the empty catalog.
AGENTS_FORBIDDEN = (
    (
        "the Seller had zero published items, so the callback catalog and "
        "Buyer results were empty"
    ),
)

AGENTS_REQUIRED = (
    ".voice/progress.md",
    "Sampoorna Whole Wheat Atta 1kg",
    "current-source FQDN `W-*` remains open",
    "preprod-gate1-search-20260725-213218.json",
)

PROGRESS_REQUIRED = (
    "preprod-gate-3-logistics-conformance",
    "**passed**",
    "Gate 1",
    "Gate 2",
)

IMPL_REQUIRED = (
    ".voice/progress.md",
    "production conformance remain open",
    "PreProd Gates 1–3 passed",
)

CI_REQUIRED_JOB_IDS = (
    "secret-scan",
    "agentguard-contract",
    "gateway",
    "ondc-offline",
    "owner-drift",
    "ci-ok",
)

SOFT_JOB_ID = "ondc-fqdn-soft"


def _read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _job_block(ci_text: str, job_id: str) -> str | None:
    match = re.search(
        rf"(?ms)^  {re.escape(job_id)}:\n(.*?)(?=^  [a-z0-9-]+:|\Z)",
        ci_text,
    )
    return match.group(0) if match else None


def grade_owners(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    agents = root / "AGENTS.md"
    progress = root / ".voice" / "progress.md"
    impl = root / ".voice" / "IMPLEMENTATIONPLAN.md"
    ci = root / ".github" / "workflows" / "ci.yml"
    ship = root / "docs" / "SHIP.md"
    cicd = (
        root
        / ".cursor"
        / "skills"
        / "portfolio-deploy"
        / "references"
        / "ci-cd.md"
    )

    agents_text = _read(agents) if agents.is_file() else ""
    progress_text = _read(progress) if progress.is_file() else ""
    impl_text = _read(impl) if impl.is_file() else ""
    ci_text = _read(ci) if ci.is_file() else ""
    ship_text = _read(ship) if ship.is_file() else ""
    cicd_text = _read(cicd) if cicd.is_file() else ""

    rows.append(
        {
            "id": "owners_present",
            "ok": all(p.is_file() for p in (agents, progress, impl, ci, ship, cicd)),
            "detail": "AGENTS/progress/IMPLEMENTATIONPLAN/ci.yml/SHIP/ci-cd.md",
        }
    )

    stale = [phrase for phrase in AGENTS_FORBIDDEN if phrase in agents_text]
    rows.append(
        {
            "id": "agents_no_stale_empty_catalog_claim",
            "ok": not stale,
            "detail": "ok" if not stale else f"stale={stale!r}",
        }
    )

    missing_agents = [m for m in AGENTS_REQUIRED if m not in agents_text]
    rows.append(
        {
            "id": "agents_gate_markers",
            "ok": not missing_agents,
            "detail": "ok" if not missing_agents else f"missing={missing_agents}",
        }
    )

    missing_progress = [m for m in PROGRESS_REQUIRED if m not in progress_text]
    rows.append(
        {
            "id": "progress_gate_markers",
            "ok": not missing_progress,
            "detail": "ok" if not missing_progress else f"missing={missing_progress}",
        }
    )

    missing_impl = [m for m in IMPL_REQUIRED if m not in impl_text]
    rows.append(
        {
            "id": "implementationplan_m9_open",
            "ok": not missing_impl,
            "detail": "ok" if not missing_impl else f"missing={missing_impl}",
        }
    )

    # Fail if IMPLEMENTATIONPLAN claims M9 complete without the open clause nearby.
    m9_complete = bool(
        re.search(
            r"(?is)9\.\s*ONDC integration.*?\|\s*\*\*Complete\*\*",
            impl_text,
        )
    )
    rows.append(
        {
            "id": "implementationplan_m9_not_complete",
            "ok": not m9_complete,
            "detail": "ok" if not m9_complete else "M9 marked Complete",
        }
    )

    missing_jobs = [job for job in CI_REQUIRED_JOB_IDS if f"  {job}:" not in ci_text]
    rows.append(
        {
            "id": "ci_fail_closed_jobs_present",
            "ok": not missing_jobs,
            "detail": "ok" if not missing_jobs else f"missing={missing_jobs}",
        }
    )

    soft_block = _job_block(ci_text, SOFT_JOB_ID) or ""
    rows.append(
        {
            "id": "ci_soft_fqdn_advisory",
            "ok": bool(soft_block)
            and "continue-on-error: true" in soft_block
            and "--soft" in soft_block,
            "detail": "ondc-fqdn-soft must stay continue-on-error + --soft",
        }
    )

    # Soft job must not be wired into the merge aggregator.
    ci_ok_block = _job_block(ci_text, "ci-ok") or ""
    soft_in_ci_ok = SOFT_JOB_ID in ci_ok_block
    needs_match = re.search(r"needs:\s*\[([^\]]+)\]", ci_ok_block)
    needs = needs_match.group(1) if needs_match else ""
    required_in_needs = all(job in needs for job in CI_REQUIRED_JOB_IDS if job != "ci-ok")
    rows.append(
        {
            "id": "ci_ok_needs_fail_closed_only",
            "ok": required_in_needs and not soft_in_ci_ok,
            "detail": f"needs=[{needs}] soft_in_ci_ok={soft_in_ci_ok}",
        }
    )

    # Offline graders must remain blocking (no continue-on-error on that job).
    offline_block = _job_block(ci_text, "ondc-offline") or ""
    rows.append(
        {
            "id": "ci_offline_fail_closed",
            "ok": bool(offline_block) and "continue-on-error" not in offline_block,
            "detail": "ondc-offline must not continue-on-error",
        }
    )

    owner_block = _job_block(ci_text, "owner-drift") or ""
    rows.append(
        {
            "id": "ci_owner_drift_fail_closed",
            "ok": bool(owner_block)
            and "continue-on-error" not in owner_block
            and "verify_owner_drift.py" in owner_block,
            "detail": "owner-drift job must run verify_owner_drift.py fail-closed",
        }
    )

    rows.append(
        {
            "id": "ship_mentions_unique_graders",
            "ok": "offline graders" in ship_text and "AgentGuard contract" in ship_text,
            "detail": "docs/SHIP.md must keep unique grader list",
        }
    )

    rows.append(
        {
            "id": "cicd_offline_blocks",
            "ok": "ondc_ci_graders.py --offline" in cicd_text
            and "blocks" in cicd_text.casefold(),
            "detail": "ci-cd.md must keep offline as blocking",
        }
    )

    # Soft swallow: `|| true` after live probes hides real script crashes.
    soft_swallows = "|| true" in soft_block
    rows.append(
        {
            "id": "ci_soft_no_true_swallow",
            "ok": bool(soft_block) and not soft_swallows,
            "detail": "soft job must not use `|| true` (use --soft / continue-on-error)",
        }
    )

    return rows


def _self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".voice").mkdir()
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / ".cursor" / "skills" / "portfolio-deploy" / "references").mkdir(
            parents=True
        )

        # Seed a passing tree, then introduce one stale AGENTS claim.
        (root / "AGENTS.md").write_text(
            "\n".join(AGENTS_REQUIRED)
            + "\nthe Seller had zero published items, so the callback catalog and "
            "Buyer results were empty\n",
            encoding="utf-8",
        )
        (root / ".voice" / "progress.md").write_text(
            "\n".join(PROGRESS_REQUIRED) + "\n",
            encoding="utf-8",
        )
        (root / ".voice" / "IMPLEMENTATIONPLAN.md").write_text(
            "\n".join(IMPL_REQUIRED) + "\n",
            encoding="utf-8",
        )
        (root / ".github" / "workflows" / "ci.yml").write_text(
            """
name: Portfolio CI
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - run: true
  agentguard-contract:
    runs-on: ubuntu-latest
    steps:
      - run: true
  gateway:
    runs-on: ubuntu-latest
    steps:
      - run: true
  ondc-offline:
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/ondc_ci_graders.py --offline
  owner-drift:
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/verify_owner_drift.py
  ondc-fqdn-soft:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/ondc_ci_graders.py --live --soft
  ci-ok:
    needs: [secret-scan, agentguard-contract, gateway, ondc-offline, owner-drift]
    runs-on: ubuntu-latest
    steps:
      - run: true
""".lstrip(),
            encoding="utf-8",
        )
        (root / "docs" / "SHIP.md").write_text(
            "AgentGuard contract parity and offline graders\n",
            encoding="utf-8",
        )
        (
            root
            / ".cursor"
            / "skills"
            / "portfolio-deploy"
            / "references"
            / "ci-cd.md"
        ).write_text(
            "ondc_ci_graders.py --offline blocks ci-ok\n",
            encoding="utf-8",
        )

        rows = grade_owners(root)
        by_id = {str(r["id"]): r for r in rows}
        if by_id["agents_no_stale_empty_catalog_claim"]["ok"]:
            print("self-test: expected stale AGENTS claim to fail", file=sys.stderr)
            return 1

        # Fix stale phrase; expect full pass.
        (root / "AGENTS.md").write_text("\n".join(AGENTS_REQUIRED) + "\n", encoding="utf-8")
        rows = grade_owners(root)
        failed = [r for r in rows if not r["ok"]]
        if failed:
            print(f"self-test: expected pass, failed={failed}", file=sys.stderr)
            return 1

        # Soft swallow must fail.
        soft_path = root / ".github" / "workflows" / "ci.yml"
        soft_path.write_text(
            soft_path.read_text(encoding="utf-8").replace(
                "python3 scripts/ondc_ci_graders.py --live --soft",
                "python3 scripts/ondc_preprod_smoke.py --ci || true",
            ),
            encoding="utf-8",
        )
        rows = grade_owners(root)
        by_id = {str(r["id"]): r for r in rows}
        if by_id["ci_soft_no_true_swallow"]["ok"] or by_id["ci_soft_fqdn_advisory"]["ok"]:
            print("self-test: expected soft swallow / missing --soft to fail", file=sys.stderr)
            return 1

    print("verify_owner_drift self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    rows = grade_owners(args.root)
    failed = [r for r in rows if not r["ok"]]
    for row in rows:
        mark = "PASS" if row["ok"] else "FAIL"
        print(f"{mark} {row['id']}: {row['detail']}")
    if failed:
        print(f"owner drift: {len(failed)} check(s) failed", file=sys.stderr)
        return 1
    print("owner drift: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
