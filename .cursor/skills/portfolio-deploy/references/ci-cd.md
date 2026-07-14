# CI/CD lifecycle (portfolio — $0)

> **HARD POLICY — $0 ONLY.** CI uses GitHub Actions free minutes. Deploy stays
> Render **Free** + Vercel **Hobby**. Abort any upgrade/billing path. Full free
> inventory + charge watchlist: [`free-tier.md`](free-tier.md).

Apps are **separate public repos** (local dirs gitignored in the workspace).
Portfolio CI checks them out; app repos keep their own CI. Do not invent a
second test stack — graders call the same scripts as local/TESTINGPLAN.

## Lifecycle

```text
dev (local)
  → Portfolio CI graders (PR / push / workflow_dispatch)
  → green required
  → Portfolio Deploy (workflow_dispatch only; confirm Free/Hobby)
  → post-deploy probes
  → maintain (cold start OK)
```

| Stage | Owner | Auto? |
| --- | --- | --- |
| Local smoke | `./scripts/verify-portfolio.sh` + buyer/seller `npm test`/`build` | Operator / agent |
| Graders | `.github/workflows/ci.yml` | On PR + push `main` |
| Deploy | `.github/workflows/deploy.yml` | **No** — `workflow_dispatch` only |
| Post-probe | Deploy workflow final job | After deploy jobs |

Hermes / WIP browser lanes are **out of CI** (`verify-portfolio.sh --ci` skips them).

## CI graders (fail = non-zero exit)

| Grader | Command / job | Notes |
| --- | --- | --- |
| Secret scan | `gitleaks detect --source … --exit-code 1` | Free CLI; no Codecov/paid SaaS |
| Gateway pytest | `./scripts/verify-portfolio.sh --ci` | No `start-dev`; TestClient only — see green path below |
| ONDC Buyer | `npm ci && npm run lint && npm run typecheck && npm test && npm run build` | Does **not** set `VITE_COMMERCE_DEMO_MODE` |
| ONDC Seller | same npm chain | — |
| ONDC offline | `python3 scripts/ondc_ci_graders.py --offline` | Demo-mode gate + static; **blocks** `ci-ok` |
| ONDC FQDN soft | `ondc_ci_graders.py --live --soft` (+ optional `ondc_preprod_smoke.py --ci`) | `continue-on-error: true` — Free cold start; advisory |
| Aggregator | job `ci-ok` | Needs secret-scan + gateway + buyer + seller + ondc-offline |

**Inventory / gradeability map:** [`.cursor/skills/ondc-testing/references/test-inventory.md`](../../ondc-testing/references/test-inventory.md). Hermes browser = Ops only (not CI).

### Block PR vs soft

| Blocks merge | Soft / advisory |
| --- | --- |
| gitleaks, gateway pytest, buyer/seller npm, `ondc_ci_graders --offline` | `ondc_ci_graders --live --soft`, `ondc_preprod_smoke --ci` |

Post-deploy job runs the same live soft graders after wake.

### Gateway pytest green path (2026-07-12)

`verify-portfolio.sh --ci` / CI job `gateway`:

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
3. Default re-runs graders; `skip_graders` is emergency-only.
4. Surfaces: `all` | `gateway` | `buyer` | `seller`.
5. On failure: fix code/env and re-dispatch — **never** upgrade plan / add Disk / open billing.

Disable platform auto-deploy-on-push if you want this dispatch to be the sole prod path; otherwise keep branch protection + green CI on the Render/Vercel-connected repos.

## GitHub secrets (names only — never commit values)

| Secret | Used by |
| --- | --- |
| `RENDER_API_KEY` | Gateway deploy (Render API) |
| `RENDER_GATEWAY_SERVICE_ID` | Gateway service id |
| `VERCEL_TOKEN` | Buyer + Seller deploy |
| `VERCEL_ORG_ID` | Vercel CLI scope |
| `VERCEL_PROJECT_ID_BUYER` | Buyer project |
| `VERCEL_PROJECT_ID_SELLER` | Seller project |

Optional **Actions variables** (not secrets): `AADHAAR_CHAIN_REPO`, `ONDC_BUYER_REPO`, `ONDC_SELLER_REPO`, `AADHAAR_CHAIN_REF`, `ONDC_BUYER_REF`, `ONDC_SELLER_REF` (defaults: `ingpoc/*` @ `main`).

**Do not** put in GitHub Actions secrets as deploy inputs for SPA builds: Auth0 client secrets, ONDC PEMs, `SESSION_SECRET` — those stay on **Render/Vercel project env** (see [`checklist.md`](checklist.md)).

## Local equivalents

```bash
# Same graders CI uses (API-only)
./scripts/verify-portfolio.sh --ci
cd ondcbuyer && npm test && npm run build
cd ../ondcseller && npm test && npm run build

# Full local (may start stack; optional Hermes)
./scripts/verify-portfolio.sh
./scripts/verify-portfolio.sh --browser
```

## $0 abort (deploy workflow)

`deploy.yml` requires `confirm_free_tier=true`. Any upgrade / billing / paid Disk / Pro path → **abort**; stay Render **Free** + Vercel **Hobby**. See [`free-tier.md`](free-tier.md).

## Ownership

This file + [`../SKILL.md`](../SKILL.md) own portfolio CI/CD. Do not invent a parallel “ci” skill. Create PRs = Cursor built-in (not duplicated here). Auth design → [`../../authentication/SKILL.md`](../../authentication/SKILL.md). Browser proof → [`../../portfolio-browser/SKILL.md`](../../portfolio-browser/SKILL.md) / [`../../ondc-testing/SKILL.md`](../../ondc-testing/SKILL.md).
