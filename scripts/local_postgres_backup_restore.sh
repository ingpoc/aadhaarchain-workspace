#!/usr/bin/env bash
# Local PostgreSQL backup / restore exercise for A6 / O2 checklist prep.
# Refuses non-local DATABASE_URL hosts (never targets Render/production).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${ROOT}/.session/evidence/backups"
EVIDENCE_TEMPLATE="${ROOT}/.session/docs/local-postgres-backup-restore-template.json"

usage() {
  cat <<'EOF'
Usage: local_postgres_backup_restore.sh <command> [options]

Commands:
  backup          pg_dump custom-format backup to .session/evidence/backups/
  verify-restore  restore backup into temporary local DB and run integrity counts
  restore         restore backup file into TARGET_DATABASE_URL (local only)

Environment:
  DATABASE_URL            Source database (default: gateway .env or local postgres)
  TARGET_DATABASE_URL     Target for restore (verify-restore sets automatically)
  BACKUP_FILE             Explicit backup path for restore / verify-restore

Examples:
  DATABASE_URL='postgresql://user@127.0.0.1:5432/postgres' ./scripts/local_postgres_backup_restore.sh backup
  ./scripts/local_postgres_backup_restore.sh verify-restore
EOF
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

assert_local_database_url() {
  local url="$1"
  local label="${2:-DATABASE_URL}"
  python3 - "$url" "$label" <<'PY'
import sys
from urllib.parse import urlparse

url, label = sys.argv[1], sys.argv[2]
parsed = urlparse(url)
host = (parsed.hostname or "").lower()
allowed = {"127.0.0.1", "localhost", "::1"}
if host not in allowed:
    print(f"Refusing non-local {label} host {host!r}. Use 127.0.0.1/localhost only.", file=sys.stderr)
    sys.exit(1)
if parsed.scheme not in {"postgresql", "postgres"}:
    print(f"Refusing non-PostgreSQL {label}: {parsed.scheme}", file=sys.stderr)
    sys.exit(1)
PY
}

resolve_database_url() {
  if [[ -n "${DATABASE_URL:-}" ]]; then
    echo "$DATABASE_URL"
    return
  fi
  local env_file="${ROOT}/aadharchain/gateway/.env"
  if [[ -f "$env_file" ]]; then
    local line
    line="$(grep -E '^DATABASE_URL=' "$env_file" | tail -1 || true)"
    if [[ -n "$line" ]]; then
      echo "${line#DATABASE_URL=}" | tr -d '"' | tr -d "'"
      return
    fi
  fi
  echo "postgresql://${USER}@127.0.0.1:5432/postgres"
}

admin_database_url() {
  python3 - "$1" <<'PY'
import sys
from urllib.parse import urlparse, urlunparse

parsed = urlparse(sys.argv[1])
admin = parsed._replace(path="/postgres")
print(urlunparse(admin))
PY
}

latest_backup() {
  ls -1t "${BACKUP_DIR}"/local-postgres-*.dump 2>/dev/null | head -1 || true
}

cmd_backup() {
  require_cmd pg_dump
  local url
  url="$(resolve_database_url)"
  assert_local_database_url "$url" "DATABASE_URL"
  mkdir -p "$BACKUP_DIR"
  local stamp file
  stamp="$(date +%Y%m%d-%H%M%S)"
  file="${BACKUP_DIR}/local-postgres-${stamp}.dump"
  echo "Backing up local database to ${file}"
  pg_dump "$url" --format=custom --no-owner --no-acl --file="$file"
  python3 - "$file" "$url" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

backup, url = Path(sys.argv[1]), sys.argv[2]
record = {
    "schema_version": "local-postgres-backup.v1",
    "recorded_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    "command": "backup",
    "database_host": urlparse(url).hostname,
    "backup_file": str(backup.relative_to(backup.parents[2])),
    "backup_bytes": backup.stat().st_size,
    "note": "Local-only backup. Production encrypted backup remains operator-owned (A6/O2).",
}
sidecar = backup.with_suffix(".json")
sidecar.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(sidecar)
PY
}

integrity_counts() {
  local url="$1"
  psql "$url" -v ON_ERROR_STOP=1 -At <<'SQL'
SELECT 'agentguard_mandate_versions' AS table_name, count(*)::text FROM agentguard_mandate_versions
UNION ALL SELECT 'commerce_orders', count(*)::text FROM commerce_orders
UNION ALL SELECT 'commerce_ledger_entries', count(*)::text FROM commerce_ledger_entries
UNION ALL SELECT 'ondc_inbox', count(*)::text FROM ondc_inbox
UNION ALL SELECT 'agentguard_receipts', count(*)::text FROM agentguard_receipts;
SQL
}

cmd_verify_restore() {
  require_cmd pg_dump
  require_cmd pg_restore
  require_cmd psql
  require_cmd createdb
  require_cmd dropdb

  local source_url backup target_db target_url admin_url stamp
  source_url="$(resolve_database_url)"
  assert_local_database_url "$source_url" "DATABASE_URL"
  backup="${BACKUP_FILE:-$(latest_backup)}"
  if [[ -z "$backup" || ! -f "$backup" ]]; then
    echo "No backup found. Run backup first or set BACKUP_FILE." >&2
    exit 1
  fi

  stamp="$(date +%Y%m%d%H%M%S)"
  target_db="agentguard_restore_${stamp}"
  admin_url="$(admin_database_url "$source_url")"
  assert_local_database_url "$admin_url" "admin URL"

  echo "Creating temporary database ${target_db}"
  createdb --maintenance-db="$admin_url" "$target_db"

  target_url="$(python3 - "$source_url" "$target_db" <<'PY'
import sys
from urllib.parse import urlparse, urlunparse
parsed = urlparse(sys.argv[1])
print(urlunparse(parsed._replace(path=f"/{sys.argv[2]}")))
PY
)"
  assert_local_database_url "$target_url" "TARGET_DATABASE_URL"

  cleanup() {
    dropdb --maintenance-db="$admin_url" --if-exists "$target_db" >/dev/null 2>&1 || true
  }
  trap cleanup EXIT

  echo "Restoring ${backup} -> ${target_db}"
  pg_restore --no-owner --no-acl --dbname="$target_url" "$backup"

  echo "Integrity counts on restored database:"
  integrity_counts "$target_url" | while IFS='|' read -r table count; do
    printf "  %-28s %s\n" "$table" "$count"
  done

  python3 - "$backup" "$target_db" "$EVIDENCE_TEMPLATE" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

backup, target_db, template = sys.argv[1], sys.argv[2], Path(sys.argv[3])
payload = {
    "schema_version": "local-postgres-backup-restore.v1",
    "exercise_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    "backup_file": backup,
    "restore_target_db": target_db,
    "host_policy": "local-only (127.0.0.1/localhost/::1)",
    "integrity_checks": "agentguard_mandate_versions, commerce_orders, commerce_ledger_entries, ondc_inbox, agentguard_receipts",
    "operator_next": [
        "Approve RTO/RPO placeholders in .session/docs/PRODUCTION-READINESS.md",
        "Configure encrypted production backups on Render/Neon",
        "Run isolated production restore drill (not this script)",
    ],
    "status": "local_verify_restore_passed",
}
out = template.with_name(f"local-postgres-backup-restore-{datetime.now().strftime('%Y%m%d')}.json")
out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(out)
PY
}

cmd_restore() {
  require_cmd pg_restore
  local backup target_url
  backup="${BACKUP_FILE:-$(latest_backup)}"
  target_url="${TARGET_DATABASE_URL:-$(resolve_database_url)}"
  if [[ -z "$backup" || ! -f "$backup" ]]; then
    echo "No backup found. Set BACKUP_FILE." >&2
    exit 1
  fi
  assert_local_database_url "$target_url" "TARGET_DATABASE_URL"
  echo "Restoring ${backup} into ${target_url}"
  pg_restore --clean --if-exists --no-owner --no-acl --dbname="$target_url" "$backup"
  echo "Restore complete. Run integrity checks manually if needed."
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    backup) cmd_backup ;;
    verify-restore) cmd_verify_restore ;;
    restore) cmd_restore ;;
    -h|--help|help|"") usage ;;
    *)
      echo "Unknown command: $cmd" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
