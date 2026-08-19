#!/usr/bin/env bash
# Local ship gate — run BEFORE committing or dispatching Portfolio Deploy.
# $0 only (Render Free + Vercel Hobby). No Auth0, Chrome, UPI, live ONDC, or AgentMail.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Local ship gate (offline, \$0) ==="
echo "Does not hit Auth0, Chrome, UPI, real ONDC, or AgentMail."
echo "Does not set VITE_COMMERCE_DEMO_MODE."
echo

python3 "$ROOT/scripts/ondc_ci_graders.py" --self-test
python3 "$ROOT/scripts/ondc_ci_graders.py" --offline

if [[ -d "$ROOT/ondcbuyer/shared/agentguard-contract" &&
      -d "$ROOT/ondcseller/shared/agentguard-contract" &&
      -d "$ROOT/aadharchain/gateway/tests/fixtures/agentguard-contract" ]]; then
  echo "→ AgentGuard contract parity"
  python3 "$ROOT/scripts/verify_agentguard_contract_sync.py"
else
  echo "→ AgentGuard contract parity skipped (nested app trees not present)"
fi

cat <<'EOF'

✓ Offline ship gate passed.

Next steps (fail-closed, $0):
  1. In the app repo you changed, run npm test / pytest locally.
  2. Open a PR on that app repo. App CI runs on the PR (cursor/* pushes
     skip app CI until a PR exists — do not "fix" that with paid minutes).
  3. Merge the app PR to main.
  4. Workspace Portfolio CI (this repo, PR → main) is unique jobs only:
     AgentGuard contract parity, Gateway pytest+Postgres, offline graders.
     It does not re-run Buyer/Seller vitest.
  5. After merge: GitHub → Actions → Portfolio Deploy → Run workflow
       confirm_free_tier = true
       surface = all | gateway | buyer | seller
     Git is not connected on Vercel. This CLI workflow is the ship path.
  6. Deploy fails closed unless public FQDN assets/index-*.js matches the
     no-hyphen production alias:
       https://ondcbuyer.vercel.app  ↔  https://ondcbuyer.aadharcha.in
       https://ondcseller.vercel.app ↔  https://ondcseller.aadharcha.in
     HTTP 200 on the FQDN is not enough.

Hyphen trap: projects `ondc-buyer` / `ondc-seller` are NOT the FQDN owners.
VERCEL_PROJECT_ID_BUYER / VERCEL_PROJECT_ID_SELLER must target `ondcbuyer`
and `ondcseller` on Hobby team "ingpoc's projects".

Do not: upgrade Render/Vercel, attach Disk, Connect Git, or flip
VITE_COMMERCE_DEMO_MODE.

Owner: docs/SHIP.md  ·  .cursor/skills/portfolio-deploy/references/ci-cd.md
EOF
