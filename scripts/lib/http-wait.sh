#!/usr/bin/env bash
# Shared HTTP readiness helpers for portfolio scripts.
# Source from other bash scripts: source "$(dirname "$0")/lib/http-wait.sh"

wait_http() {
  local url="$1"
  local label="${2:-$url}"
  local attempts="${3:-45}"
  local i=1
  while [[ "$i" -le "$attempts" ]]; do
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$url" 2>/dev/null || echo "000")
    if [[ "$code" =~ ^2 ]]; then
      printf "✓ %s %s\n" "$label" "$url"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  printf "✗ %s %s (not ready after %ss)\n" "$label" "$url" "$attempts"
  return 1
}
