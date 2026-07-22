#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/vercel_archive_deploy.sh <buyer|seller> --confirm-free-tier [--stage-only]

Builds with the linked Vercel Production environment, creates a non-git archive
stage, deploys it to Vercel Hobby, and aliases the canonical FQDN. The explicit
free-tier confirmation is required because Vercel's CLI does not expose the team
plan in project inspection output.
EOF
}

if [[ $# -lt 2 || "$2" != "--confirm-free-tier" ]]; then
  usage >&2
  exit 2
fi

case "$1" in
  buyer)
    app="ondcbuyer"
    domain="ondcbuyer.aadharcha.in"
    ;;
  seller)
    app="ondcseller"
    domain="ondcseller.aadharcha.in"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

stage_only=false
if [[ "${3:-}" == "--stage-only" ]]; then
  stage_only=true
elif [[ $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
app_dir="$root/$app"

command -v jq >/dev/null
command -v vercel >/dev/null
test -f "$app_dir/vercel.json"
test -f "$app_dir/.vercel/project.json"

lock_backup="$(mktemp "/tmp/${app}-package-lock.XXXXXX")"
cp "$app_dir/package-lock.json" "$lock_backup"
restore_lock() {
  cp "$lock_backup" "$app_dir/package-lock.json"
  rm -f "$lock_backup"
}
trap restore_lock EXIT

(
  cd "$app_dir"
  vercel pull --yes --environment=production
  # Vercel's production environment sets NODE_ENV=production. The local
  # TypeScript build still needs dev-only compiler declarations before the
  # already-built dist directory is archived.
  npm ci --include=dev
  NPM_CONFIG_INCLUDE=dev vercel build --prod
)
restore_lock
trap - EXIT

stage="$(mktemp -d "/tmp/${app}-vercel-stage.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/.vercel"
cp -R "$app_dir/dist" "$stage/dist"
cp "$app_dir/.vercel/project.json" "$stage/.vercel/project.json"
jq '. + {buildCommand:"echo skip",installCommand:"echo skip",outputDirectory:"dist"}' \
  "$app_dir/vercel.json" > "$stage/vercel.json"

test -f "$stage/dist/index.html"
test -n "$(find "$stage/dist/assets" -name 'index-*.js' -print -quit)"
test -z "$(find "$stage" -name .git -print -quit)"

if [[ "$stage_only" == true ]]; then
  jq -n --arg app "$app" --arg domain "$domain" \
    '{ok:true, stage_only:true, app:$app, domain:$domain, stage_validated:true}'
  exit 0
fi

deploy_json="$(cd "$stage" && vercel deploy --prod --archive=tgz --yes --format=json)"
deployment_url="$(printf '%s' "$deploy_json" | jq -r '.deployment.url // empty')"
ready_state="$(printf '%s' "$deploy_json" | jq -r '.deployment.readyState // empty')"
test "$ready_state" = "READY"
test -n "$deployment_url"

(cd "$stage" && vercel alias set "$deployment_url" "$domain")

jq -n \
  --arg app "$app" \
  --arg domain "$domain" \
  --arg deployment_url "$deployment_url" \
  '{ok:true, app:$app, domain:$domain, deployment_url:$deployment_url, ready_state:"READY"}'
