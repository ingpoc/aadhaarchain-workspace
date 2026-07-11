#!/usr/bin/env bash
# AUTOMATION CANDIDATE — do not treat as canonical until on-chain E2E is manually verified.
# Manual lane: validator → validate-onchain.sh → init config → approve path on-chain.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOLANA_DIR="$ROOT/aadharsolana"
GATEWAY_DIR="$ROOT/aadharchain/gateway"

usage() {
  cat <<'EOF'
Usage: ./scripts/verify-solana.sh [options]

Options:
  --init-config   Run gateway identity-registry initialize_config after deploy
  --skip-deploy   Run anchor test only (validator + programs must already match IDL)
  -h, --help      Show help

Flow: validator up → anchor keys sync/build/deploy/test → gateway solana_bridge tests
EOF
}

INIT_CONFIG=0
SKIP_DEPLOY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --init-config) INIT_CONFIG=1; shift ;;
    --skip-deploy) SKIP_DEPLOY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

echo "=== Solana verify ==="

if ! solana cluster-version --url localhost >/dev/null 2>&1; then
  echo "→ Starting local validator"
  "$SOLANA_DIR/scripts/start-validator.sh"
  sleep 2
fi

if [[ "$SKIP_DEPLOY" == "0" ]]; then
  echo "→ Anchor build/deploy/test"
  "$SOLANA_DIR/scripts/validate-onchain.sh"
else
  echo "→ Anchor test (skip deploy)"
  cd "$SOLANA_DIR"
  anchor test --skip-local-validator
fi

echo "→ Sync IDL into gateway"
cp "$SOLANA_DIR/target/idl/identity_registry.json" "$GATEWAY_DIR/idl/identity_registry.json"

echo "→ Gateway solana bridge tests"
cd "$GATEWAY_DIR"
.venv/bin/python -m pytest tests/test_solana_bridge.py -q

if [[ "$INIT_CONFIG" == "1" ]]; then
  echo "→ Initialize identity-registry config"
  .venv/bin/python scripts/init_identity_registry_config.py
fi

echo "✓ Solana verify passed"
