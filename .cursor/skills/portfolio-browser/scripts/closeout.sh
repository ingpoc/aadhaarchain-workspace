#!/usr/bin/env bash
# Portfolio browser closeout — leave Chrome + bridge in stable state.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
BRIDGE_PY="$ROOT/.cursor/skills/portfolio-browser/scripts/hermes_bridge.py"
LEAVE_URL="${1:-http://127.0.0.1:43102/search}"

SESSIONS='portfolio-browser aadhaarchain-sso-seller aadhaarchain-sso-buyer solflare-sso'
close_json='['
first=1
for s in $SESSIONS; do
  [[ $first -eq 1 ]] || close_json+=','
  close_json+="{\"type\":\"close_tab\",\"sessionName\":\"$s\"}"
  first=0
done
close_json+=']'

echo "→ Bridge status"
if ! python3 "$BRIDGE_PY" status 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('ready:', d.get('ready')); sys.exit(0 if d.get('ready') else 1)"; then
  echo "✗ Bridge not ready at closeout — run preflight before next session"
  exit 1
fi

echo "→ Closing agent-opened tabs"
python3 "$BRIDGE_PY" run --use-selected-tab --timeout 30 "$close_json" 2>/dev/null || true

echo "→ Leaving Chrome at $LEAVE_URL"
python3 "$BRIDGE_PY" run --timeout 20 \
  "[{\"type\":\"goto\",\"url\":\"$LEAVE_URL\"},{\"type\":\"wait_for_selector\",\"selector\":\"h1,h2\",\"timeout\":8000},{\"type\":\"page_context\"}]" \
  2>/dev/null || true

echo "→ Final bridge check"
python3 "$BRIDGE_PY" status 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
tab=d.get('active_tab') or {}
print(f\"✓ Closeout complete — Chrome at {tab.get('url','?')}, bridge ready={d.get('ready')}\")
sys.exit(0 if d.get('ready') else 1)
"
