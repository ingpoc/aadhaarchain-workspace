#!/usr/bin/env python3
"""P5 gate: refuse flipping VITE_COMMERCE_DEMO_MODE=false without conformance evidence.

Usage:
  python3 scripts/commerce_demo_mode_gate.py --check
  python3 scripts/commerce_demo_mode_gate.py --allow-with-evidence path/to/evidence.json

Evidence JSON must include:
  { "ondc_conformance": true, "subscriber_id": "...", "environment": "staging"|"production",
    "attested_at": "ISO-8601", "notes": "..." }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED = ("ondc_conformance", "subscriber_id", "environment", "attested_at")


def validate_evidence(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"evidence file missing: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    for key in REQUIRED:
        if key not in data:
            errors.append(f"missing field: {key}")
    if data.get("ondc_conformance") is not True:
        errors.append("ondc_conformance must be true")
    env = data.get("environment")
    if env not in ("staging", "production", "preprod", "pre-production"):
        errors.append("environment must be staging/preprod/production")
    if not str(data.get("subscriber_id") or "").strip():
        errors.append("subscriber_id must be non-empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Print gate status")
    parser.add_argument(
        "--allow-with-evidence",
        type=Path,
        help="Validate evidence file that unlocks VITE_COMMERCE_DEMO_MODE=false",
    )
    args = parser.parse_args()

    if args.allow_with_evidence:
        errs = validate_evidence(args.allow_with_evidence)
        if errs:
            print(json.dumps({"ok": False, "errors": errs}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "ok": True,
                    "message": (
                        "Evidence accepted. You may set VITE_COMMERCE_DEMO_MODE=false "
                        "and point VITE_ONDC_* at public discovery URLs. "
                        "Signing keys remain on the gateway only."
                    ),
                    "evidence": str(args.allow_with_evidence),
                },
                indent=2,
            )
        )
        return 0

    print(
        json.dumps(
            {
                "ok": True,
                "commerce_demo_mode_required": True,
                "message": (
                    "Do not set VITE_COMMERCE_DEMO_MODE=false until ONDC portal A5–A8, "
                    "staging conformance, and evidence JSON pass --allow-with-evidence."
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
