#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/Users/gurusharan/.pyenv/versions/3.12.0/bin/python3}"

echo "=== AadhaarChain Portfolio Setup ==="

setup_python() {
  local dir="$1"
  echo ""
  echo "Setting up Python env in $dir"
  cd "$dir"
  if [ ! -d .venv ]; then
    "$PYTHON_BIN" -m venv .venv
  fi
  .venv/bin/pip install -q -r requirements.txt
}

setup_node() {
  local dir="$1"
  echo ""
  echo "Installing npm deps in $dir"
  cd "$dir"
  npm install
}

setup_python "$ROOT/aadharchain/gateway"
setup_python "$ROOT/flatwatch/backend"
cd "$ROOT/flatwatch/backend" && .venv/bin/pip install -q -r requirements-dev.txt
setup_node "$ROOT/aadharchain/frontend"
setup_node "$ROOT/ondcbuyer"
setup_node "$ROOT/ondcseller"
setup_node "$ROOT/flatwatch/frontend"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Start all services:"
echo "  $ROOT/scripts/start-dev.sh"
echo ""
echo "Local ports:"
echo "  AadhaarChain frontend  http://127.0.0.1:43100"
echo "  AadhaarChain gateway   http://127.0.0.1:43101"
echo "  ONDC buyer             http://127.0.0.1:43102"
echo "  ONDC seller            http://127.0.0.1:43103"
echo "  FlatWatch backend      http://127.0.0.1:43104"
echo "  FlatWatch frontend     http://127.0.0.1:43105"
