#!/usr/bin/env bash
# Portfolio browser preflight — WIP Hermes only (never ~/.codex or ~/.hermes live).
# Exit 0 only when HTTP + WIP bridge are healthy (ready: true).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
# shellcheck source=../../../../scripts/lib/http-wait.sh
source "$ROOT/scripts/lib/http-wait.sh"

WIP_ROOT="${HERMES_CHROME_WIP_ROOT:-/Users/gurusharan/plugins/hermes-chrome-cursor-wip}"
export HERMES_CHROME_BRIDGE_SOCKET="${HERMES_CHROME_BRIDGE_SOCKET:-$WIP_ROOT/run/chrome-bridge.sock}"
WIP_SYNC="$WIP_ROOT/scripts/sync-wip.sh"
BRIDGE_PY="$ROOT/.cursor/skills/portfolio-browser/scripts/hermes_bridge.py"

fail=0

cleanup_orphan_wip_hosts() {
  # Do not kill live WIP native hosts — they are owned by the browser extension.
  # Only remove a stale socket file when the bridge is unreachable.
  if [[ -S "$HERMES_CHROME_BRIDGE_SOCKET" ]] && ! bridge_ready 2>/dev/null; then
    echo "→ Stale WIP socket (bridge not ready) — removing $HERMES_CHROME_BRIDGE_SOCKET"
    rm -f "$HERMES_CHROME_BRIDGE_SOCKET"
  fi
}

bridge_ready() {
  python3 "$BRIDGE_PY" status 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('ready') else 1)"
}

portfolio_stack_ready() {
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 \
    "http://127.0.0.1:43101/api/health" 2>/dev/null || echo "000")
  [[ "$code" =~ ^2 ]]
}

ensure_portfolio_stack() {
  if portfolio_stack_ready; then
    return 0
  fi
  echo "→ Portfolio stack not ready — starting ./scripts/start-dev.sh"
  "$ROOT/scripts/start-dev.sh"
}

check_http() {
  local name="$1" url="$2"
  if ! wait_http "$url" "$name" 30; then
    fail=1
  fi
}

check_validator_rpc() {
  if ! grep -q 'NEXT_PUBLIC_DEV_BURNER_WALLET=true' "$ROOT/aadharchain/frontend/.env.local" 2>/dev/null; then
    return 0
  fi
  # Deterministic ensure (getHealth). Do not pkill / rm ledger for browser lanes.
  if bash "$ROOT/aadharsolana/scripts/ensure-validator.sh"; then
    return 0
  fi
  echo "✗ Solana validator :8899 not healthy — required for burner SSO"
  echo "  Fix: ./aadharsolana/scripts/ensure-validator.sh"
  echo "  Probe: curl -s http://127.0.0.1:8899 -X POST -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getHealth\"}'"
  echo "  Do not pkill or rm aadharsolana/.local-validator for portfolio browser (on-chain tests only use --reset)"
  fail=1
}

echo "→ WIP Hermes paths"
echo "  root:   $WIP_ROOT"
echo "  socket: $HERMES_CHROME_BRIDGE_SOCKET"

echo "→ Native host hygiene (WIP only)"
cleanup_orphan_wip_hosts

echo "→ Hermes Chrome WIP bridge"
if ! bridge_ready 2>/dev/null; then
  if [[ -x "$WIP_SYNC" ]]; then
    echo "→ Bridge down — running sync-wip.sh..."
    bash "$WIP_SYNC" 2>&1 | tail -20 || true
  fi
  # Wake: status ping after short wait (extension must be loaded in Comet/Chrome)
  sleep 2
  if ! bridge_ready 2>/dev/null; then
    echo "✗ WIP bridge not ready"
    echo "  1. Load unpacked: $WIP_ROOT/deploy/extension"
    echo "  2. Confirm native host parent is that browser (Comet or Chrome)"
    echo "  3. export HERMES_CHROME_BRIDGE_SOCKET=$HERMES_CHROME_BRIDGE_SOCKET"
    echo "  4. Re-run preflight"
    fail=1
  fi
else
  echo "✓ WIP bridge ready"
fi

if ! bridge_ready 2>/dev/null; then
  echo "✗ Bridge status not ready (EMPTY_RESPONSE or socket down)"
  fail=1
fi

echo "→ Portfolio HTTP"
ensure_portfolio_stack
check_http "AadhaarChain web" "http://127.0.0.1:43100/login"
check_http "Gateway"        "http://127.0.0.1:43101/api/health"
check_http "ONDC Buyer"     "http://127.0.0.1:43102/search"
check_http "ONDC Seller"    "http://127.0.0.1:43103/dashboard"

echo "→ Browser desktop visibility (Chrome or Comet)"
visible=0
if osascript -e 'tell application "Google Chrome" to get name of every window' 2>/dev/null | grep -qE 'AadhaarChain|ONDC|Identity Agent|Solflare|127\.0\.0\.1'; then
  visible=1
  echo "✓ Google Chrome portfolio windows visible"
fi
if osascript -e 'tell application "Comet" to get name of every window' 2>/dev/null | grep -qE 'AadhaarChain|ONDC|Identity Agent|Solflare|127\.0\.0\.1|Example'; then
  visible=1
  echo "✓ Comet portfolio/windows visible"
fi
if [[ "$visible" -eq 0 ]]; then
  echo "⚠ No Chrome/Comet portfolio tabs visible on this macOS Space"
  echo "  Move the WIP host browser to the same desktop as Cursor, then re-run"
  # Soft warn only — WIP may still drive background windows
fi

echo "→ Dev burner wallet"
if grep -q 'NEXT_PUBLIC_DEV_BURNER_WALLET=true' "$ROOT/aadharchain/frontend/.env.local" 2>/dev/null; then
  echo "✓ Burner wallet enabled — Hermes SSO uses dev_auto=1"
  check_validator_rpc
else
  echo "○ Burner off — Hermes SSO requires Phantom in Chrome wallet modal"
fi

if [[ "$fail" -eq 0 ]]; then
  echo "✓ Portfolio preflight passed — tier: hermes-wip"
  python3 "$BRIDGE_PY" urls >/dev/null
fi

exit "$fail"
