#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/http-wait.sh
source "$ROOT/scripts/lib/http-wait.sh"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "python3 is required" >&2
  exit 1
fi
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"
REQUESTED_SERVICES=" ${*:-all} "

want_service() {
  local service="$1"
  [[ "$REQUESTED_SERVICES" == *" all "* || "$REQUESTED_SERVICES" == *" $service "* ]]
}

for service in "$@"; do
  case "$service" in
    gateway|host|buyer|seller|flatwatch-api|flatwatch-web|checklist) ;;
    *)
      echo "Unknown service '$service'. Use: gateway host buyer seller flatwatch-api flatwatch-web checklist" >&2
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

  # Local gateway: caller DATABASE_URL wins over gateway/.env (which may hold a
  # Render URL). Refuse Render/remote Postgres unless ALLOW_REMOTE_DATABASE_URL=1.
  # Never migrate / CF3 schema-work against Render from start-dev.
  if [[ "$name" == "aadhaar-gateway" ]]; then
    local parent_database_url="${DATABASE_URL-}"
    local filtered_env_args=()
    local arg
    for arg in "${env_args[@]}"; do
      if [[ -n "$parent_database_url" && "$arg" == DATABASE_URL=* ]]; then
        continue
      fi
      filtered_env_args+=("$arg")
    done
    env_args=("${filtered_env_args[@]}")
    if [[ -n "$parent_database_url" ]]; then
      env_args+=("DATABASE_URL=$parent_database_url")
    fi

    local effective_database_url="$parent_database_url"
    if [[ -z "$effective_database_url" ]]; then
      for arg in "${env_args[@]}"; do
        if [[ "$arg" == DATABASE_URL=* ]]; then
          effective_database_url="${arg#DATABASE_URL=}"
          break
        fi
      done
    fi
    if [[ -n "$effective_database_url" && "${ALLOW_REMOTE_DATABASE_URL:-}" != "1" ]]; then
      case "$effective_database_url" in
        *onrender.com*|*render.com*|*.postgres.render.com*|*dpg-*.oregon-postgres*|*dpg-*.virginia-postgres*|*dpg-*.ohio-postgres*|*dpg-*.frankfurt-postgres*)
          echo "Refusing local gateway with Render/remote DATABASE_URL (from .env or env)." >&2
          echo "Export local DATABASE_URL=postgresql://gurusharan@127.0.0.1:5432/postgres (caller env overrides .env)," >&2
          echo "or set ALLOW_REMOTE_DATABASE_URL=1 only for intentional remote work." >&2
          exit 1
          ;;
      esac
    fi
  fi

  # Codex/agent shell teardown kills the caller's process group even when a
  # child uses nohup. Launch Python services in a new session (setsid double-fork
  # below). Plain nohup dies when the agent shell exits — do not "fix" detach
  # with nohup alone.
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
  if [[ -z "$PACKAGE_RUNNER" || ( "$RUNNER_MODE" == "vite" && ! -f "$APP_DIR/node_modules/vite/bin/vite.js" ) ]]; then
    echo "No package runner is available for $name" >&2
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

# Durable static serve for product-lead checklist HTML. Same setsid double-fork
# as gateway — plain nohup dies when the agent shell exits. Generate stays a
# separate command; this only regenerates when checklist.html is missing.
# Port: CHECKLIST_PORT or 8030, then 8031… when busy (cap +20). Never kill
# foreign listeners — other repos may hold lower ports in parallel.
checklist_port_in_range() {
  local port="$1"
  local preferred="$2"
  local max_offset="$3"
  [[ "$port" =~ ^[0-9]+$ ]] || return 1
  (( port >= preferred && port <= preferred + max_offset ))
}

checklist_ours_healthy() {
  local port="$1"
  local pid_file="$2"
  local saved_pid listen_pids

  [[ -f "$pid_file" ]] || return 1
  saved_pid="$(tr -d '[:space:]' <"$pid_file")"
  [[ -n "$saved_pid" ]] || return 1
  listen_pids="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)"
  [[ -n "$listen_pids" ]] || return 1
  printf '%s\n' "$listen_pids" | grep -qx "$saved_pid" || return 1
  curl -sf -o /dev/null "http://127.0.0.1:${port}/checklist.html"
}

start_checklist_html() {
  local name="checklist-html"
  local preferred="${CHECKLIST_PORT:-8030}"
  local max_offset=20
  local html_dir="$ROOT/.session/html"
  local html_file="$html_dir/checklist.html"
  local session_log_dir="$ROOT/.session/logs"
  local log_file="$session_log_dir/$name.log"
  local pid_file="$session_log_dir/$name.pid"
  local port_file="$session_log_dir/$name.port"
  local port="" recorded="" listen_pids="" chosen=""

  if [[ ! "$preferred" =~ ^[0-9]+$ ]]; then
    echo "WARN: CHECKLIST_PORT='$preferred' is not numeric; using 8030" >&2
    preferred=8030
  fi

  mkdir -p "$html_dir" "$session_log_dir"

  if [[ ! -f "$html_file" ]]; then
    echo "checklist.html missing; running generate_checklist.py once..."
    if ! (cd "$ROOT" && "$PYTHON_BIN" scripts/generate_checklist.py); then
      echo "WARN: generate_checklist.py failed; refusing to serve without $html_file" >&2
      return 1
    fi
  fi
  if [[ ! -f "$html_file" ]]; then
    echo "WARN: $html_file still missing after generate; skip checklist serve" >&2
    return 1
  fi

  if [[ -f "$port_file" ]]; then
    recorded="$(tr -d '[:space:]' <"$port_file")"
    if checklist_port_in_range "$recorded" "$preferred" "$max_offset" \
      && checklist_ours_healthy "$recorded" "$pid_file"; then
      echo "$recorded" >"$port_file"
      echo "Checklist HTML already healthy on :$recorded — leaving running (pid $(cat "$pid_file"))"
      echo "  → http://127.0.0.1:${recorded}/checklist.html"
      return 0
    fi
  fi

  for ((port = preferred; port <= preferred + max_offset; port++)); do
    if checklist_ours_healthy "$port" "$pid_file"; then
      echo "$port" >"$port_file"
      echo "Checklist HTML already healthy on :$port — leaving running (pid $(cat "$pid_file"))"
      echo "  → http://127.0.0.1:${port}/checklist.html"
      return 0
    fi
  done

  for ((port = preferred; port <= preferred + max_offset; port++)); do
    listen_pids="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)"
    if [[ -z "$listen_pids" ]]; then
      chosen="$port"
      break
    fi
    echo "Port $port busy (not this repo's checklist); trying next..."
  done

  if [[ -z "$chosen" ]]; then
    echo "WARN: no free checklist port in ${preferred}-$((preferred + max_offset))" >&2
    return 1
  fi
  port="$chosen"

  python3 - "$html_dir" "$log_file" "$pid_file" "$PYTHON_BIN" "$port" <<'PY'
import os
import sys
from pathlib import Path

service_dir, log_path, pid_path, python_bin, port = sys.argv[1:]
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
    [python_bin, "-m", "http.server", port, "--bind", "127.0.0.1"],
    os.environ,
)
PY
  echo "$port" >"$port_file"
  echo "Started $name on :$port (pid $(cat "$pid_file")) → http://127.0.0.1:${port}/checklist.html"
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
if want_service checklist; then
  start_checklist_html || fail_checklist=1
fi

echo ""
echo "Waiting for health checks..."
fail=0
fail_checklist="${fail_checklist:-0}"
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
if want_service checklist; then
  checklist_port="$(tr -d '[:space:]' <"$ROOT/.session/logs/checklist-html.port" 2>/dev/null || true)"
  checklist_port="${checklist_port:-8030}"
  wait_http "http://127.0.0.1:${checklist_port}/checklist.html" "Checklist HTML" 15 || fail=1
fi

if [[ "$fail" -ne 0 || "$fail_checklist" -ne 0 ]]; then
  echo ""
  echo "✗ One or more services failed to become ready. Check logs in $LOG_DIR"
  if want_service checklist; then
    echo "  Checklist log: $ROOT/.session/logs/checklist-html.log"
  fi
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
if want_service checklist; then
  checklist_port="$(tr -d '[:space:]' <"$ROOT/.session/logs/checklist-html.port" 2>/dev/null || true)"
  checklist_port="${checklist_port:-8030}"
  echo "  Checklist     http://127.0.0.1:${checklist_port}/checklist.html"
fi
