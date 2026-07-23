#!/usr/bin/env python3
"""Fail when deployable AgentGuard contract copies drift from the canonical owner."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "shared" / "agentguard-contract"
CONSUMERS = (
    ROOT / "ondcbuyer" / "shared" / "agentguard-contract",
    ROOT / "ondcseller" / "shared" / "agentguard-contract",
)
GATEWAY_FIXTURES = (
    ROOT
    / "aadharchain"
    / "gateway"
    / "tests"
    / "fixtures"
    / "agentguard-contract"
)
PARITY_FILES = (
    "README.md",
    "src/actions.ts",
    "src/canonicalize.ts",
    "src/decisions.ts",
    "src/index.ts",
    "src/reasons.ts",
    "src/types.ts",
    "fixtures/golden-action-request.json",
    "fixtures/golden-decision-v2.json",
)


def main() -> int:
    failures: list[str] = []
    canonical_package = json.loads((CANONICAL / "package.json").read_text())

    for consumer in CONSUMERS:
        consumer_package = json.loads((consumer / "package.json").read_text())
        if consumer_package.get("version") != canonical_package.get("version"):
            failures.append(
                f"{consumer.relative_to(ROOT)} package version "
                f"{consumer_package.get('version')!r} != {canonical_package.get('version')!r}"
            )
        if "./decisions" not in consumer_package.get("exports", {}):
            failures.append(
                f"{consumer.relative_to(ROOT)} does not export ./decisions"
            )

        for relative in PARITY_FILES:
            canonical_path = CANONICAL / relative
            consumer_path = consumer / relative
            if not consumer_path.is_file():
                failures.append(f"{consumer_path.relative_to(ROOT)} is missing")
                continue
            if consumer_path.read_bytes() != canonical_path.read_bytes():
                failures.append(
                    f"{consumer_path.relative_to(ROOT)} differs from canonical "
                    f"{canonical_path.relative_to(ROOT)}"
                )

    for name in (
        "golden-action-request.json",
        "golden-action-request.canonical.txt",
        "golden-decision-v2.json",
    ):
        canonical_path = CANONICAL / "fixtures" / name
        gateway_path = GATEWAY_FIXTURES / name
        if not gateway_path.is_file():
            failures.append(f"{gateway_path.relative_to(ROOT)} is missing")
        elif gateway_path.read_bytes() != canonical_path.read_bytes():
            failures.append(
                f"{gateway_path.relative_to(ROOT)} differs from canonical "
                f"{canonical_path.relative_to(ROOT)}"
            )

    result = {
        "contract": "@aadharchain/agentguard-contract",
        "version": canonical_package["version"],
        "decision_schema_version": "2",
        "consumers": [str(path.relative_to(ROOT)) for path in CONSUMERS],
        "files_checked_per_consumer": len(PARITY_FILES),
        "gateway_fixture_files_checked": 3,
        "ok": not failures,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
