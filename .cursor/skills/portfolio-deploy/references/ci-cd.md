# CI/CD lifecycle (portfolio — $0)

> **HARD POLICY — $0 ONLY.** CI uses GitHub Actions free minutes. Deploy stays
> Render **Free** + Vercel **Hobby**. Abort any upgrade/billing path. Full free
> inventory + charge watchlist: [`free-tier.md`](free-tier.md).

Apps are **separate public repos** (local dirs gitignored in the workspace).
Portfolio CI checks them out when a unique job needs the tree; app repos keep
their own CI (Buyer/Seller vitest). Do not invent a second test stack — graders
call the same scripts as local/TESTINGPLAN.

Public ship path: [`docs/SHIP.md`](../../../../docs/SHIP.md).

## Lifecycle

```text
dev (local)
  → ./scripts/local-ship-gate.sh (offline graders; $0)
  → app repo npm test / pytest + app PR CI
  → merge app main
  → Portfolio CI unique jobs (PR / push main / workflow_dispatch)
  → green required
  → Portfolio Deploy (workflow_dispatch only; confirm Free/Hobby)
  → fail-closed FQDN vs vercel.app index-*.js
  → maintain (cold start OK)
```

| Stage | Owner | Auto? |
| --- | --- | --- |
| Local ship gate | `./scripts/local-ship-gate.sh` | Operator / agent before commit |
| App unit tests | `ondcbuyer` / `ondcseller` / `aadharchain` CI | On app PR (`cursor/*` skips until PR) |
| Portfolio graders | `.github/workflows/ci.yml` | On PR + push `main` |
| Deploy | `.github/workflows/deploy.yml` | **No** — `workflow_dispatch` only |
| Post-probe | Deploy workflow final job | After deploy jobs; hash parity fail-closed |

Hermes / WIP browser lanes are **out of CI** (`verify-portfolio.sh --ci` skips them).

## Vercel project identity (fail-closed)

Hobby team **ingpoc's projects**. Git is **not** connected. CLI `--prod` via
Portfolio Deploy only.

| Secret | Must target project | Production alias | Public FQDN | Forbidden twin |
| --- | --- | --- | --- | --- |
| `VERCEL_PROJECT_ID_BUYER` | `ondcbuyer` | `https://ondcbuyer.vercel.app` | `https://ondcbuyer.aadharcha.in` | `ondc-buyer` |
| `VERCEL_PROJECT_ID_SELLER` | `ondcseller` | `https://ondcseller.vercel.app` | `https://ondcseller.aadharcha.in` | `ondc-seller` |

**2026-08-19:** Portfolio Deploy run 6 succeeded and landed new production on
the no-hyphen `*.vercel.app` aliases (`index-BNEIAZ9p.js` / `index-XX7NQ1aR.js`)
while `*.aadharcha.in` stayed on the hyphen projects for hours. Soft HTTP 200
probes did not notice. After each Buyer/Seller `--prod`, extract
`assets/index-*.js` from both URLs and **fail the job** if they differ.

## CI graders (fail = non-zero exit)

| Grader | Command / job | Notes |
| --- | --- | --- |
| Secret scan | `gitleaks detect --source … --no-git --config .gitleaks.toml --exit-code 1` | Current release tree; the config narrowly allows public ONDC registry UUIDs in evidence; historical credential rotation is tracked separately; free CLI, no Codecov/paid SaaS |
| AgentGuard contract | `python3 scripts/verify_agentguard_contract_sync.py` | Unique job; canonical vs Buyer/Seller/gateway fixtures |
| Gateway pytest+Postgres | `./scripts/verify-portfolio.sh --ci --skip-contract` | No `start-dev`; TestClient only — see green path below |
| ONDC offline | `python3 scripts/ondc_ci_graders.py --offline` | Demo-mode gate + 2026-08-19 Buyer/Seller/Gateway P0 test scanners; **blocks** `ci-ok`. Job checks out `aadharchain/`, `ondcbuyer/`, `ondcseller/`. Missing/emptied Gateway P0 tests fail closed (`gateway_p0_regression_tests_missing`; aadhaar-chain#7 is on main). |
| ONDC FQDN soft | `ondc_ci_graders.py --live --soft` (+ optional `ondc_preprod_smoke.py --ci`) + `--bundle-parity --soft` | `continue-on-error: true` — Free cold start; advisory. Hash mismatch does **not** block the PR. |
| Aggregator | job `ci-ok` | Needs secret-scan + agentguard-contract + gateway + ondc-offline. **Not** Buyer/Seller npm. |

**Inventory / gradeability map:** [`.agents/skills/testing-ledger/references/test-inventory.md`](../../../../.agents/skills/testing-ledger/references/test-inventory.md). Hermes browser = Ops only (not CI).

### Block PR vs soft

| Blocks merge | Soft / advisory |
| --- | --- |
| gitleaks, AgentGuard contract, gateway pytest+Postgres, `ondc_ci_graders --offline` | `ondc_ci_graders --live --soft`, `--bundle-parity --soft` on PR, `ondc_preprod_smoke --ci` |

Buyer/Seller `npm test` **blocks the app PR**, not this workspace PR.

Post-deploy: live functional graders stay `--soft`; **bundle parity is fail-closed**.

### Gateway pytest green path (2026-07-12)

`verify-portfolio.sh --ci` / CI job `gateway` (contract parity is a separate job):

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1  # avoid host plugin pollution
pytest tests/ -q -p asyncio       # async tests need explicit -p asyncio when autoload off
```

Auth0 isolation: `tests/test_social_auth.py` **monkeypatches** `settings.auth0_domain` / `client_id` / `client_secret` to `None` where the suite asserts demo-only providers — so a developer machine with real `AUTH0_*` in `.env` does not break CI-equivalent local runs. Cookie Domain tests similarly monkeypatch `public_gateway_url` (host-only on `*.onrender.com`).

**Not in CI:** rumdl/ruff (not used in this portfolio), Hermes, Solana validator, FlatWatch AgentGuard.

App-repo CI (extend, don’t duplicate):

| Repo | Workflow | Graders |
| --- | --- | --- |
| `ingpoc/aadhaar-chain` | `.github/workflows/ci.yml` | gitleaks + gateway pytest + frontend build |
| `ingpoc/ondc-buyer` | `.github/workflows/ci.yml` | gitleaks + npm lint/typecheck/test/build |
| `ingpoc/ondc-seller` | `.github/workflows/ci.yml` | gitleaks + npm lint/typecheck/test/build |
| `ingpoc/aadhaarchain-workspace` | `.github/workflows/ci.yml` | portfolio orchestration above |

## Deploy gate

1. Operator runs **Actions → Portfolio Deploy → Run workflow**.
2. Must set `confirm_free_tier=true` (else abort — $0 hard stop).
3. Default re-runs unique graders (contract + gateway pytest+Postgres + offline); `skip_graders` is emergency-only. Does **not** re-run Buyer/Seller vitest.
4. Surfaces: `all` | `gateway` | `buyer` | `seller`.
5. Gateway checkout resolves the selected ref to a commit and sends that exact
   commit to Render. Do not rely on the service's configured branch.
6. On failure: fix code/env and re-dispatch — **never** upgrade plan / add Disk / open billing.

Disable platform auto-deploy-on-push if you want this dispatch to be the sole prod path; otherwise keep branch protection + green CI on the Render/Vercel-connected repos.

## GitHub secrets (names only — never commit values)

| Secret | Used by |
| --- | --- |
| `RENDER_API_KEY` | Gateway deploy (Render API) |
| `RENDER_GATEWAY_SERVICE_ID` | Gateway service id |
| `VERCEL_TOKEN` | Buyer + Seller deploy |
| `VERCEL_ORG_ID` | Vercel CLI scope |
| `VERCEL_PROJECT_ID_BUYER` | Buyer Hobby project **`ondcbuyer`** (no hyphen; not `ondc-buyer`) |
| `VERCEL_PROJECT_ID_SELLER` | Seller Hobby project **`ondcseller`** (no hyphen; not `ondc-seller`) |

Optional **Actions variables** (not secrets): `AADHAAR_CHAIN_REPO`, `ONDC_BUYER_REPO`, `ONDC_SELLER_REPO`, `AADHAAR_CHAIN_REF`, `ONDC_BUYER_REF`, `ONDC_SELLER_REF` (defaults: `ingpoc/*` @ `main`).

**Do not** put in GitHub Actions secrets as deploy inputs for SPA builds: Auth0 client secrets, ONDC PEMs, `SESSION_SECRET` — those stay on **Render/Vercel project env** (see [`checklist.md`](checklist.md)).

## Local equivalents

```bash
# Same unique graders Portfolio CI uses (API-only; no Buyer/Seller vitest)
./scripts/local-ship-gate.sh
./scripts/verify-portfolio.sh --ci --skip-contract

# App-repo tests (own CI on PR)
cd ondcbuyer && npm test && npm run build
cd ../ondcseller && npm test && npm run build

# Optional live hash probe (fail-closed; not part of local-ship-gate)
python3 scripts/ondc_ci_graders.py --bundle-parity
./scripts/verify-portfolio.sh --bundle-parity

# Full local (may start stack; optional Hermes)
./scripts/verify-portfolio.sh
./scripts/verify-portfolio.sh --browser
```

## $0 abort (deploy workflow)

`deploy.yml` requires `confirm_free_tier=true`. Any upgrade / billing / paid Disk / Pro path → **abort**; stay Render **Free** + Vercel **Hobby**. See [`free-tier.md`](free-tier.md).

## Ownership

This file + [`../SKILL.md`](../SKILL.md) own portfolio CI/CD. Do not invent a parallel “ci” skill. Create PRs = Cursor built-in (not duplicated here). Auth design → [`../../authentication/SKILL.md`](../../authentication/SKILL.md). Browser proof → [`../../portfolio-browser/SKILL.md`](../../portfolio-browser/SKILL.md) / [`../../ondc-testing/SKILL.md`](../../ondc-testing/SKILL.md).
