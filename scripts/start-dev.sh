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
  local env_file=""
  local -a env_args=("PORT=$port")

  lsof -ti:"$port" | xargs kill -9 2>/dev/null || true

  cd "$dir"
  if [ -x .venv/bin/python ]; then
    PYTHON_BIN=".venv/bin/python"
  fi

  # Load service .env into the process (uvicorn does not auto-load dotenv).
  if [ -f .env ]; then
    env_file=".env"
  elif [ -f .env.local ]; then
    env_file=".env.local"
  fi
  if [ -n "$env_file" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        ''|\#*) continue ;;
      esac
      if [[ "$line" == *=* ]]; then
        env_args+=("$line")
      fi
    done <"$env_file"
  fi

  nohup env "${env_args[@]}" "$PYTHON_BIN" -m uvicorn "$module" --host 127.0.0.1 --port "$port" \
    >"$LOG_DIR/$name.log" 2>&1 &
  echo $! >"$LOG_DIR/$name.pid"
  echo "Started $name on :$port (pid $(cat "$LOG_DIR/$name.pid"))"
}

start_node() {
  local name="$1"
  local dir="$2"
  local port="$3"
  local env_file=""

  lsof -ti:"$port" | xargs kill -9 2>/dev/null || true

  cd "$dir"

  # Vite prefers process env over .env.local. Shell/FQDN VITE_* leaks
  # (e.g. gateway.aadharcha.in) break local booth Realtime/AgentGuard.
  # Prefer .env.local, else .env; strip inherited VITE_* then apply file.
  # Start in a new process group so Cursor Shell teardown cannot SIGKILL Vite.
  if [ -f .env.local ]; then
    env_file=".env.local"
  elif [ -f .env ]; then
    env_file=".env"
  fi

  ROOT_DIR="$(cd "$ROOT" && pwd)"
  APP_DIR="$(pwd)"
  LOG_FILE="$LOG_DIR/$name.log"
  PID_FILE="$LOG_DIR/$name.pid"
  python3 - "$APP_DIR" "$LOG_FILE" "$PID_FILE" "$env_file" <<'PY'
import os, subprocess, sys
from pathlib import Path
app, log_path, pid_path, env_file = sys.argv[1:5]
env = os.environ.copy()
for k in list(env):
    if k.startswith("VITE_"):
        del env[k]
ef = Path(app) / env_file if env_file else None
if ef and ef.is_file():
    for line in ef.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("VITE_") or line.startswith("PORT="):
            key, _, val = line.partition("=")
            env[key] = val
logf = open(log_path, "w")
proc = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=app,
    env=env,
    stdout=logf,
    stderr=subprocess.STDOUT,
    start_new_session=True,
)
Path(pid_path).write_text(str(proc.pid), encoding="utf-8")
print(proc.pid)
PY
  echo "Started $name on :$port (pid $(cat "$LOG_DIR/$name.pid"))${env_file:+ [env=$env_file,detached]}"
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
