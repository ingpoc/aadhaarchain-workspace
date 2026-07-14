#!/usr/bin/env bash
# Portfolio verify — API lane + optional browser lane (validated 2026-07-06).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/http-wait.sh
source "$ROOT/scripts/lib/http-wait.sh"

RUN_BROWSER=0
RUN_SSO=0
CI_MODE=0
SSO_WALLET="burner"
SSO_APP="seller"
LEAVE_URL="http://127.0.0.1:43102/search"

usage() {
  cat <<'EOF'
Usage: ./scripts/verify-portfolio.sh [options]

Options:
  --ci                   API-only CI lane: gateway pytest, no stack start, no Hermes
  --browser              Full browser lane: smoke + SSO + closeout (single preflight)
  --sso WALLET [APP]     Browser lane with SSO only (burner|solflare, seller|buyer|all)
  --leave-url URL        Closeout page (default :43102/search)
  -h, --help

Default: ensure dev stack → gateway pytest (no browser)

Browser lane uses: python3 scripts/portfolio_browser.py lane [wallet] [app]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ci) CI_MODE=1; shift ;;
    --browser) RUN_BROWSER=1; shift ;;
    --sso)
      RUN_SSO=1
      SSO_WALLET="${2:-burner}"
      SSO_APP="${3:-seller}"
      shift $(( $# >= 3 ? 3 : $# ))
      ;;
    --leave-url)
      LEAVE_URL="${2:-$LEAVE_URL}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$CI_MODE" == "1" && ( "$RUN_BROWSER" == "1" || "$RUN_SSO" == "1" ) ]]; then
  echo "error: --ci cannot combine with --browser/--sso (Hermes not available in CI)" >&2
  exit 2
fi

echo "=== Portfolio verify ==="

run_gateway_pytest() {
  echo "→ Gateway tests"
  cd "$ROOT/aadharchain/gateway"
  # Disable setuptools plugin autoload (avoids host pollution e.g. broken
  # anchorpy/pytest_xprocess) but still load pytest-asyncio for async tests.
  local pytest_args=(tests/ -q -p asyncio)
  if [[ -x .venv/bin/python ]]; then
    PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}" \
      .venv/bin/python -m pytest "${pytest_args[@]}"
  else
    PY="${PYTHON:-}"
    if [[ -z "$PY" ]]; then
      if command -v python >/dev/null 2>&1; then PY=python
      else PY=python3
      fi
    fi
    PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}" \
      "$PY" -m pytest "${pytest_args[@]}"
  fi
}

if [[ "$CI_MODE" == "1" ]]; then
  echo "→ CI mode (API-only; skip stack + Hermes)"
  run_gateway_pytest
  echo "✓ Portfolio verify passed (CI)"
  exit 0
fi

if ! wait_http "http://127.0.0.1:43101/health" "Gateway" 3 2>/dev/null; then
  echo "→ Dev stack not ready — starting ./scripts/start-dev.sh"
  "$ROOT/scripts/start-dev.sh"
fi

run_gateway_pytest

if [[ "$RUN_BROWSER" == "1" ]]; then
  echo "→ Browser lane (smoke + SSO + closeout)"
  python3 "$ROOT/scripts/portfolio_browser.py" lane "$SSO_WALLET" "$SSO_APP"
elif [[ "$RUN_SSO" == "1" ]]; then
  echo "→ Browser lane (SSO + closeout)"
  python3 "$ROOT/scripts/portfolio_browser.py" preflight
  PORTFOLIO_SKIP_PREFLIGHT=1 python3 "$ROOT/scripts/portfolio_browser.py" sso "$SSO_WALLET" "$SSO_APP"
  python3 "$ROOT/scripts/portfolio_browser.py" closeout "$LEAVE_URL"
fi

echo "✓ Portfolio verify passed"
