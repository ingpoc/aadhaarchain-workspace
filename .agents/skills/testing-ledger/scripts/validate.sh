#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
python3 "$repo_root/scripts/generate_testing_ledger.py" --check
python3 "$repo_root/scripts/generate_checklist.py" --check-current
exec python3 "$repo_root/scripts/validate_cursor_skill.py" testing-ledger
