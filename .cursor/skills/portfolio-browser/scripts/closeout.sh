#!/usr/bin/env bash
# Portfolio browser closeout — release every Hermes WIP agent window/lease.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
BRIDGE_PY="$SCRIPTS/hermes_bridge.py"
LEAVE_URL="${1:-http://127.0.0.1:43102/search}"

echo "→ Bridge status"
if ! python3 "$BRIDGE_PY" status 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('ready:', d.get('ready')); sys.exit(0 if d.get('ready') else 1)"; then
  echo "✗ Bridge not ready at closeout — run preflight before next session"
  exit 1
fi

echo "→ Closing all Hermes WIP agent leases/windows"
if ! python3 "$SCRIPTS/closeout_leases.py" --leave-url "$LEAVE_URL"; then
  echo "✗ One or more agent leases could not be closed (see JSON above)"
  exit 1
fi

echo "→ Final bridge check"
python3 "$BRIDGE_PY" status 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"✓ Closeout complete — active_agent_sessions={d.get('active_agent_sessions', '?')}, bridge ready={d.get('ready')}\")
sys.exit(0 if d.get('ready') else 1)
"
