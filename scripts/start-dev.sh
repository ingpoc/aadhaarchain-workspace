#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/http-wait.sh
source "$ROOT/scripts/lib/http-wait.sh"
PYTHON_BIN="${PYTHON_BIN:-/Users/gurusharan/.pyenv/versions/3.12.0/bin/python3}"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

start_python() {
  local name="$1"
  local dir="$2"
  local port="$3"
  local module="$4"

  lsof -ti:"$port" | xargs kill -9 2>/dev/null || true

  cd "$dir"
  if [ -x .venv/bin/python ]; then
    PYTHON_BIN=".venv/bin/python"
  fi

  nohup env PORT="$port" "$PYTHON_BIN" -m uvicorn "$module" --host 127.0.0.1 --port "$port" \
    >"$LOG_DIR/$name.log" 2>&1 &
  echo $! >"$LOG_DIR/$name.pid"
  echo "Started $name on :$port (pid $(cat "$LOG_DIR/$name.pid"))"
}

start_node() {
  local name="$1"
  local dir="$2"
  local port="$3"

  lsof -ti:"$port" | xargs kill -9 2>/dev/null || true

  cd "$dir"
  nohup npm run dev >"$LOG_DIR/$name.log" 2>&1 &
  echo $! >"$LOG_DIR/$name.pid"
  echo "Started $name on :$port (pid $(cat "$LOG_DIR/$name.pid"))"
}

echo "=== Starting AadhaarChain portfolio dev stack ==="

lsof -ti:43101 | xargs kill -9 2>/dev/null || true
cd "$ROOT/aadharchain/gateway"
nohup env PORT=43101 .venv/bin/python main.py >"$LOG_DIR/aadhaar-gateway.log" 2>&1 &
echo $! >"$LOG_DIR/aadhaar-gateway.pid"
echo "Started aadhaar-gateway on :43101 (pid $(cat "$LOG_DIR/aadhaar-gateway.pid"))"
start_node "aadhaar-frontend" "$ROOT/aadharchain/frontend" 43100
start_node "ondc-buyer" "$ROOT/ondcbuyer" 43102
start_node "ondc-seller" "$ROOT/ondcseller" 43103
start_python "flatwatch-backend" "$ROOT/flatwatch/backend" 43104 "app.main:app"
start_node "flatwatch-frontend" "$ROOT/flatwatch/frontend" 43105

echo ""
echo "Waiting for health checks..."
fail=0
wait_http "http://127.0.0.1:43101/health" "Gateway" || fail=1
wait_http "http://127.0.0.1:43101/api/health" "Gateway API" || fail=1
wait_http "http://127.0.0.1:43100/login" "AadhaarChain web" || fail=1
wait_http "http://127.0.0.1:43102/search" "ONDC Buyer" || fail=1
wait_http "http://127.0.0.1:43103/dashboard" "ONDC Seller" || fail=1
wait_http "http://127.0.0.1:43104/api/health" "FlatWatch API" || fail=1
wait_http "http://127.0.0.1:43105" "FlatWatch web" 30 || fail=1

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "✗ One or more services failed to become ready. Check logs in $LOG_DIR"
  exit 1
fi

echo ""
echo "Portfolio dev stack running. Logs: $LOG_DIR"
echo "  AadhaarChain  http://127.0.0.1:43100"
echo "  Gateway       http://127.0.0.1:43101"
echo "  ONDC Buyer    http://127.0.0.1:43102"
echo "  ONDC Seller   http://127.0.0.1:43103"
echo "  FlatWatch API http://127.0.0.1:43104"
echo "  FlatWatch UI  http://127.0.0.1:43105"
