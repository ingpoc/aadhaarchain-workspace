#!/usr/bin/env python3
"""Export deterministic CF0 state-machine and mutation-inventory evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATEWAY = ROOT / "aadharchain" / "gateway"
sys.path.insert(0, str(GATEWAY))

from app.domain_state_machines import transition_manifest  # noqa: E402
from app.mutation_inventory import inventory_manifest  # noqa: E402
from main import app  # noqa: E402


def main() -> int:
    payload = {
        "state_contract": transition_manifest(),
        "mutation_inventory": inventory_manifest(app.routes),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
