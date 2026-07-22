#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/http-wait.sh
source "$ROOT/scripts/lib/http-wait.sh"
PYTHON_BIN="${PYTHON_BIN:-/Users/gurusharan/.pyenv/versions/3.12.0/bin/python3}"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
REQUESTED_SERVICES=" ${*:-all} "

want_service() {
  local service="$1"
  [[ "$REQUESTED_SERVICES" == *" all "* || "$REQUESTED_SERVICES" == *" $service "* ]]
}

for service in "$@"; do
  case "$service" in
    gateway|host|buyer|seller|flatwatch-api|flatwatch-web) ;;
    *)
      echo "Unknown service '$service'. Use: gateway host buyer seller flatwatch-api flatwatch-web" >&2
      exit 2
      ;;
  esac
done

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

  # Codex/agent shell teardown kills the caller's process group even when a
  # child uses nohup. Launch Python services in a new session, matching the
  # detached Vite contract below, so a passing health check stays valid after
  # this script exits.
  env "${env_args[@]}" python3 - "$dir" "$LOG_DIR/$name.log" "$LOG_DIR/$name.pid" "$PYTHON_BIN" "$module" "$port" <<'PY'
import os
import sys
from pathlib import Path

service_dir, log_path, pid_path, python_bin, module, port = sys.argv[1:]
first = os.fork()
if first:
    os.waitpid(first, 0)
    print(Path(pid_path).read_text(encoding="utf-8").strip())
    raise SystemExit(0)

os.setsid()
second = os.fork()
if second:
    Path(pid_path).write_text(str(second), encoding="utf-8")
    os._exit(0)

os.chdir(service_dir)
logf = open(log_path, "w")
os.dup2(logf.fileno(), 1)
os.dup2(logf.fileno(), 2)
os.execvpe(
    python_bin,
    [python_bin, "-m", "uvicorn", module, "--host", "127.0.0.1", "--port", port],
    os.environ,
)
PY
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
  PACKAGE_RUNNER="$(command -v npm || true)"
  RUNNER_MODE="npm"
  if [[ -z "$PACKAGE_RUNNER" ]]; then
    PACKAGE_RUNNER="${NODE_BIN:-$(command -v node || true)}"
    if [[ -z "$PACKAGE_RUNNER" && -x "/Users/gurusharan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node" ]]; then
      PACKAGE_RUNNER="/Users/gurusharan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    fi
    RUNNER_MODE="vite"
  fi
  if [[ -z "$PACKAGE_RUNNER" || ! -f "$APP_DIR/node_modules/vite/bin/vite.js" ]]; then
    echo "No npm or installed local Vite runtime is available for $name" >&2
    return 1
  fi
  python3 - "$APP_DIR" "$LOG_FILE" "$PID_FILE" "$env_file" "$PACKAGE_RUNNER" "$RUNNER_MODE" <<'PY'
import os, subprocess, sys
from pathlib import Path
app, log_path, pid_path, env_file, package_runner, runner_mode = sys.argv[1:7]
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
command = (
    [package_runner, "run", "dev"]
    if runner_mode == "npm"
    else [package_runner, str(Path(app) / "node_modules/vite/bin/vite.js")]
)
proc = subprocess.Popen(
    command,
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

if want_service gateway; then
  start_python "aadhaar-gateway" "$ROOT/aadharchain/gateway" 43101 "main:app"
fi
if want_service host; then
  start_node "aadhaar-frontend" "$ROOT/aadharchain/frontend" 43100
fi
if want_service buyer; then
  start_node "ondc-buyer" "$ROOT/ondcbuyer" 43102
fi
if want_service seller; then
  start_node "ondc-seller" "$ROOT/ondcseller" 43103
fi
if want_service flatwatch-api; then
  start_python "flatwatch-backend" "$ROOT/flatwatch/backend" 43104 "app.main:app"
fi
if want_service flatwatch-web; then
  start_node "flatwatch-frontend" "$ROOT/flatwatch/frontend" 43105
fi

echo ""
echo "Waiting for health checks..."
fail=0
if want_service gateway; then
  wait_http "http://127.0.0.1:43101/health" "Gateway" || fail=1
  wait_http "http://127.0.0.1:43101/api/health" "Gateway API" || fail=1
fi
if want_service host; then
  wait_http "http://127.0.0.1:43100/login" "AadhaarChain web" || fail=1
fi
if want_service buyer; then
  wait_http "http://127.0.0.1:43102/search" "ONDC Buyer" || fail=1
fi
if want_service seller; then
  wait_http "http://127.0.0.1:43103/dashboard" "ONDC Seller" || fail=1
fi
if want_service flatwatch-api; then
  wait_http "http://127.0.0.1:43104/api/health" "FlatWatch API" || fail=1
fi
if want_service flatwatch-web; then
  wait_http "http://127.0.0.1:43105" "FlatWatch web" 30 || fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo ""
  echo "✗ One or more services failed to become ready. Check logs in $LOG_DIR"
  exit 1
fi

echo ""
echo "Requested services running. Logs: $LOG_DIR"
if want_service host; then echo "  AadhaarChain  http://127.0.0.1:43100"; fi
if want_service gateway; then echo "  Gateway       http://127.0.0.1:43101"; fi
if want_service buyer; then echo "  ONDC Buyer    http://127.0.0.1:43102"; fi
if want_service seller; then echo "  ONDC Seller   http://127.0.0.1:43103"; fi
if want_service flatwatch-api; then echo "  FlatWatch API http://127.0.0.1:43104"; fi
if want_service flatwatch-web; then echo "  FlatWatch UI  http://127.0.0.1:43105"; fi
