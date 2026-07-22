#!/usr/bin/env python3
"""Close all Hermes WIP agent leases/windows (one agent → zero leftover windows)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wip_hermes import closeout_all_sessions, load_handler  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--leave-url",
        default="http://127.0.0.1:43102/search",
        help="Controllable URL used when reclaiming orphan leases",
    )
    args = parser.parse_args()
    handler = load_handler()
    result = closeout_all_sessions(handler, leave_url=args.leave_url)
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
