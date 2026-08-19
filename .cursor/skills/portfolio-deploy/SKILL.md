---
name: portfolio-deploy
description: >-
  Pre-deploy checklist, CI graders, Render gateway + Vercel participant-edge deploy,
  post-deploy probes, and free-tier maintenance for AadhaarChainWorkspace. Sole
  CI/CD owner (ci.yml + deploy.yml + references/ci-cd.md) — do not create a
  separate CI skill; Create PRs is Cursor built-in. Use when deploying,
  redeploying, waking cold starts, setting Render/Vercel env, Auth0 callbacks
  for FQDNs, ONDC onboard routes on public hosts, CI/CD lifecycle, or checking
  identity-aadhar-gateway-main.onrender.com / ondcbuyer.aadharcha.in /
  ondcseller.aadharcha.in / ondclbnp.aadharcha.in. HARD POLICY: always free tier
  — $0 spend; abort any upgrade/billing/paid add-on; cold starts OK; no
  Render Disk for PEMs; confirm Free/Hobby before deploy. Does not own partner portal rails
  (apisetu-partner-onboarding) or Auth0 app design (authentication).
---

# Portfolio deploy

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory. Validation is read-only/offline and never deploys.

> **HARD POLICY — $0 ONLY.** Always stay on free tier. Do **not** mistakenly
> spend even one cent. **Abort** any upgrade, billing change, or paid add-on
> (Render paid instance, Disk, paid Postgres, Vercel Pro, etc.). Cold starts
> are OK. No Render Disk for PEMs — env/secrets only. **Confirm Free (Render)
> / Hobby (Vercel) before every deploy.** Details:
> [`references/free-tier.md`](references/free-tier.md).

Owns **pre-deploy gate → CI graders → operator deploy → probe → maintain** for the public portfolio stack.
**Sole CI/CD owner** for this workspace — do **not** create a separate CI skill; Create PRs stays Cursor built-in.
Do **not** duplicate Render Blueprint authorship or Auth0 product rules — link out.

**Standing rule:** append durable findings here + [`references/ci-cd.md`](references/ci-cd.md) / checklist stamps; **no secrets** in markdown (names only).

| Surface | Host | Platform |
| --- | --- | --- |
| Gateway + AgentGuard + ONDC onboard | `https://gateway.aadharcha.in` (also `identity-aadhar-gateway-main.onrender.com`) | Render **Free only** |
| ONDC Buyer SPA | `https://ondcbuyer.aadharcha.in` | Vercel **Hobby only** |
| ONDC Seller SPA | `https://ondcseller.aadharcha.in` | Vercel **Hobby only** |
| ONDC Logistics Buyer endpoint | `https://ondclbnp.aadharcha.in` | Second custom domain on the existing Render **Free** gateway; GoDaddy DNS only, no Vercel project or new service |

Local ports remain `:43101` / `:43102` / `:43103` — see repo [`AGENTS.md`](../../../AGENTS.md).

## CI/CD lifecycle (dev → graders → deploy)

```text
local-ship-gate.sh → app npm test/pytest → app PR CI → merge main →
Portfolio CI (unique jobs) → workflow_dispatch Portfolio Deploy
(confirm Free/Hobby) → fail-closed FQDN vs vercel.app index-*.js
```

| Piece | Path |
| --- | --- |
| Graders + lifecycle detail | [`references/ci-cd.md`](references/ci-cd.md) |
| Portfolio CI | `.github/workflows/ci.yml` |
| Operator deploy (no auto prod on push) | `.github/workflows/deploy.yml` |
| Local/CI API lane | `./scripts/verify-portfolio.sh --ci` |

**CI graders (fail closed):** gitleaks → AgentGuard contract parity → gateway pytest+Postgres via `verify-portfolio.sh --ci --skip-contract` → `ondc_ci_graders.py --offline`. Buyer/Seller vitest stays in **app CI** (`ingpoc/ondc-buyer`, `ingpoc/ondc-seller`). Browser UI lanes are out of CI. No rumdl/ruff unless already adopted. **Never** flip `VITE_COMMERCE_DEMO_MODE` in CI/deploy.

**Live probes are read-only by default.** CI/deploy must never pass
`--protocol-search`; that flag requires a separately authorized ONDC search gate.
FQDN functional journeys stay `--soft`. **Bundle parity** (`assets/index-*.js` on
`*.vercel.app` vs `*.aadharcha.in`) is fail-closed on Portfolio Deploy — HTTP 200
is not enough. Vercel projects must be `ondcbuyer` / `ondcseller` (no hyphen), not
`ondc-buyer` / `ondc-seller`. Git is not connected; CLI `--prod` only.

**Gateway pytest green path (2026-07-12):** always
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` + `-p asyncio` (or
`./scripts/verify-portfolio.sh --ci`). Bare pytest autoload breaks (anchorpy).
Auth0 monkeypatch + local `DATABASE_URL` fail-closed:
[`references/ci-cd.md`](references/ci-cd.md).

**Deploy:** `workflow_dispatch` only; requires `confirm_free_tier=true` (**$0 abort** otherwise); re-runs unique graders by default (not Buyer/Seller vitest); then Render gateway and/or required Vercel edges; then FQDN probes **plus fail-closed index-*.js parity**. Secrets names only in [`references/ci-cd.md`](references/ci-cd.md).

**Last frozen Retail deployment stamp (2026-07-23, Free/Hobby):** exact-commit
Render deployment `dep-d9gqfcjtqb8s73e0l940` is live at gateway
`5431307bf36bb8c906600b3ceea859efb34f9d44`; Buyer and Seller Hobby archive
deployments were Ready and their health/identity/NP/site probes passed.
Current protocol/catalog state is owned by the
[PreProd network matrix](../../../.agents/skills/testing-ledger/references/preprod-network-matrix.md),
not this deploy skill. Run history: [`references/checklist.md`](references/checklist.md).

**Dedicated LBNP deployment stamp (2026-07-26, Render Free):** exact gateway
commit `b3e81b2ebb29fd10d1a22ecb694d8b2c3953fbee` is live as deploy
`dep-d9irpocm0tmc73a0st7g`. The existing service owns its second included
custom domain, `ondclbnp.aadharcha.in`; GoDaddy CNAME, public TLS, dedicated
status, site verification, and valid challenge/answer readback passed. This is
endpoint readiness only, not portal subscription or a logistics protocol call.

**Gate 3 LBNP deployment stamp (2026-07-26, Render Free):** exact gateway
commit `cde2242cb49fb6429766e253ef613f7ff5c083ae` is live as deploy
`dep-d9iun27aqgkc73an2cpg`. The full workflow grader gate passed; absent Render
secret names blocked only the workflow deploy step, so the authenticated Render
CLI deployed the same exact commit to the already verified Free service.
DNS/TLS/status/site/challenge re-proof passed. This is PreProd protocol
readiness, not conformance or production.

**Gate 3 holiday-validator deployment stamp (2026-08-01, Render Free):** exact
gateway commit `63df7ca73faa6096961d9cf1333bc9e2387f5770` is live as deploy
`dep-d9mna2942hec73e3eq40` on the existing service. The commit contains only
the LOG10 future-holiday guard and its regression. Gateway, Buyer, Seller, and
portfolio CI gates passed; GoDaddy CNAME, TLS, LBNP status, site verification,
valid/invalid challenge readback, and public empty/past holiday 422 checks
passed. No new service, domain, paid resource, Retail change, or production
claim was introduced.

**A4 exact-commit deployment stamp (2026-08-17, Render Free):** gateway
commit `7beab582d141c6f3f1e089c356ce0df6852a318c` is live as deploy
`dep-da1boulbedkc73cieceg` on existing `identity-aadhar-gateway-main`.
Auto-deploy stayed off. Health 200; Buyer/Seller/LBNP site-verification 200;
junk `/ondc/on_subscribe` 400 decrypt-fail. PreProd PEMs unchanged. No new
service, domain, paid resource, DNS change, or production claim.

## When to use

- Operator/agent asked to **deploy / redeploy / wake** gateway or Buyer/Seller/LBNP FQDNs
- PreProd/staging needs **live** `/ondc-site-verification.html` or `/ondc/on_subscribe`
- Auth0 / CORS / `PUBLIC_GATEWAY_URL` / Vercel rewrites for public hosts
- Free-tier cold start, logs, or key/env refresh on Render

**Not this skill:** browser acceptance (`testing-ledger`), portal GST/ONDC UI
(`apisetu-partner-onboarding`), Auth0 application design (`authentication`).

## Free-tier policy (operator hard gate — $0)

**Always free. Zero spend.** Abort if a UI/CLI path offers upgrade, billing, or paid add-on. Cold starts OK. Never claim prod HA on free.

**Before deploy:** verify Render **instance** = **Free**, Render **workspace** = **Hobby**, Vercel projects = **Hobby**. If not free → **stop**. Then run the **maximize free features** checklist below (inventory + charge watchlist live in [`references/free-tier.md`](references/free-tier.md)).

| Do | Do not |
| --- | --- |
| Keep Render gateway on **Free** instance | Upgrade web service, add billing, or accept paid “reliability” |
| Prefer **no payment method** (or pipeline spend limit **$0**) | Add a card “just in case” — overages then **bill** |
| Env-injected secrets + `DATA_DIR=/tmp/aadharchain-data` | Attach **Render Disk** or write under `./data` on Render |
| Accept ~15 min spin-down + ~30–60s wake | Promise always-on / zero cold start on Free |
| Avoid Free Postgres (expires **30 days**) | Put AgentGuard/ONDC keys in Free Postgres |
| Keep Vercel **Hobby**; Analytics OK; Speed Insights on **one** project | Pro, Password Protection, Analytics Plus |
| Stay ≤ **2** Render custom domains (new Hobby) | Add a 3rd Render custom domain ($0.25/mo after Aug 2026 plan) |
| Abort any paid path immediately | “Just this once” spend of even **one cent** |

### Maximize free features (before every deploy)

1. Confirm Free/Hobby + charge-risk watchlist in [`references/free-tier.md`](references/free-tier.md) (Disk, Starter, card+overage, domain #3, Postgres day-30, Vercel Pro/Password Protection).
2. Render: custom domain TLS; env PEMs; **`DATA_DIR=/tmp/aadharchain-data`**; HTTP health check `/health` or `/api/health`; wake probe before demos.
3. Render: **skip** Disk, Free Postgres/KV, paid instance, auto-upgrade prompts. Auto-deploy-on-push stays **off** (Actions `confirm_free_tier` owns prod).
4. Vercel: Production **and** Preview `VITE_*` envs; FQDN aliases; rewrites → `gateway.aadharcha.in`; Web Analytics enabled; Speed Insights on **Buyer only** (Hobby = 1 project).
5. Vercel: **abort** Password Protection / Pro / Plus add-ons. HUF git-author block → archive deploy workaround (CLI cheat sheet).

Details: [`references/free-tier.md`](references/free-tier.md). Platform docs: [Render free](https://render.com/docs/free) · [new workspace plans](https://render.com/docs/new-workspace-plans) · [Vercel Hobby](https://vercel.com/docs/plans/hobby) · generic Render deploy: `~/.agents/skills/render-deploy/SKILL.md` · Cursor Render plugin skills — **link, do not copy**.

## Related skills / ladders

| Doc | Role |
| --- | --- |
| [`../authentication/SKILL.md`](../authentication/SKILL.md) | Auth0 callbacks, `AUTH0_*` / `VITE_IDENTITY_*`, cookie Domain, providers probe, CORS |
| [`../apisetu-partner-onboarding/SKILL.md`](../apisetu-partner-onboarding/SKILL.md) | Portal / keys / PreProd / FQDN policy |
| [`../apisetu-partner-onboarding/references/ondc-sandbox-integration-ladder.md`](../apisetu-partner-onboarding/references/ondc-sandbox-integration-ladder.md) | Code → local smoke → **deploy** → FQDN proof |
| [`../apisetu-partner-onboarding/references/ondc-sandbox-keys.md`](../apisetu-partner-onboarding/references/ondc-sandbox-keys.md) | Portal PEM materialization |
| [`../../../.agents/skills/testing-ledger/SKILL.md`](../../../.agents/skills/testing-ledger/SKILL.md) | Post-deploy Buyer/Seller UX matrix (claim→screenshot) |

## Pre-deploy checklist (gate)

**Do not run CLI deploy / Actions deploy until every item passes.** Full copy: [`references/checklist.md`](references/checklist.md). CI/CD: [`references/ci-cd.md`](references/ci-cd.md).

0. **$0 plan confirm** — Render instance = **Free**; workspace = **Hobby**; Vercel = **Hobby**. Abort upgrade/billing/Disk. Run **maximize free features** (above) + charge-risk watchlist in [`references/free-tier.md`](references/free-tier.md).
1. **CI graders green** — Portfolio CI (or `./scripts/local-ship-gate.sh`): gitleaks; AgentGuard contract parity; `./scripts/verify-portfolio.sh --ci --skip-contract`; `ondc_ci_graders.py --offline`. Buyer/Seller `npm test && npm run build` stay in **app CI**. Browser acceptance runs after deploy.
2. **Local smoke** — `./scripts/verify-portfolio.sh` if stack available; gateway onboard status OK on `:43101`; if shipping auth, `GET /api/auth/providers` shows expected providers.
3. **Secrets inventory** — `AUTH0_*`, `SESSION_SECRET` (or gateway session secret env), `CORS_ORIGINS`, `PUBLIC_GATEWAY_URL`, ONDC portal PEMs / `ONDC_*_KEYS_DIR` or equivalent env — **env on host only, never git**.
4. **Ephemeral FS** — Render Free loses local files on spin-down/redeploy. Set **`DATA_DIR=/tmp/aadharchain-data`** (and `ONDC_ENV_KEYS_DIR=/tmp/ondc-env`). PEMs via env; **never** Disk / SSH-copied persistence.
5. **CORS + Auth0** — Callbacks on **gateway** FQDN + local; Logout/Web Origins include Buyer/Seller FQDNs + local. See authentication skill.
6. **Vercel rewrites** — `ondcbuyer`/`ondcseller` `vercel.json` → `gateway.aadharcha.in` `/ondc/np/{buyer|seller}/…` (redeploy required after change).
7. **LBNP isolation** — `ondclbnp` `/ondc/:path*` must route to its
   dedicated gateway namespace and keys, never the Retail Buyer/Seller mapper.
   Verify the exact edge target before adding GoDaddy DNS; keep `ondcseller`
   untouched.
8. **Demo mode** — `VITE_COMMERCE_DEMO_MODE=false` only after `commerce_demo_mode_gate.py` evidence (done 2026-07-12 PreProd). Keep payment labels honest (simulated ≠ live UPI).

## During deploy

Order: **graders green → Render gateway first → attach/verify its exact custom
domain target → GoDaddy DNS → public DNS/TLS/endpoint readback**. Add a Vercel
edge only for an existing SPA that requires one; LBNP routes directly to
Render. Prefer Actions
**Portfolio Deploy** (`workflow_dispatch`) when secrets are configured; else
CLI below.

### 1. Render gateway

```bash
# CLI (preferred when installed + logged in)
render --version
# Dashboard or CLI redeploy of service identity-aadhar-gateway-main
# Ensure root/Dockerfile = aadharchain/gateway (binds 0.0.0.0:$PORT)

# Env on Render (minimum for staging sandbox)
# PUBLIC_GATEWAY_URL=https://gateway.aadharcha.in
# DATA_DIR=/tmp/aadharchain-data   # required on Free — default ./data is not writable
# Custom domain: gateway.aadharcha.in CNAME → identity-aadhar-gateway-main.onrender.com (GoDaddy)
# AADHAAR_CHAIN_ENV=staging
# AUTH0_DOMAIN / AUTH0_CLIENT_ID / AUTH0_CLIENT_SECRET
# SESSION_SECRET=<strong random>
# CORS_ORIGINS=...include https://ondcbuyer.aadharcha.in,https://ondcseller.aadharcha.in...
# ONDC_* subscriber ids + keys (PEM paths or dirs that exist in the image/env strategy)
# AUTH_DEMO_CONTINUE omitted/false on staging
```

MCP fallback: Render plugin `list_services` → `get_service` / deploy helpers — use when CLI missing; do not invent Blueprint ownership here (`render-deploy` skill).

### 2. Vercel participant edges

```bash
vercel --version
# CLI --prod only. Git is not connected on these Hobby projects.
# VERCEL_PROJECT_ID_* must be no-hyphen `ondcbuyer` / `ondcseller`
# (not `ondc-buyer` / `ondc-seller`). After --prod, FQDN index-*.js
# must match ondcbuyer.vercel.app / ondcseller.vercel.app.
cd ondcbuyer && vercel --prod   # project linked to ondcbuyer.aadharcha.in
cd ../ondcseller && vercel --prod
# Env: VITE_IDENTITY_AUTH_ENABLED=true
#      VITE_IDENTITY_URL=https://gateway.aadharcha.in
#      VITE_IDENTITY_WEB_URL=https://gateway.aadharcha.in
```

### 3. Probe then operator smoke

Run post-deploy probes below. On failure: fix env/code, redeploy same surface; **never** upgrade tier / add Disk / open billing as a fix — stay $0.

**After Buyer/Seller archive deploy+alias:** hand to
[`testing-ledger`](../../../.agents/skills/testing-ledger/SKILL.md) for UI acceptance. For onboarding-only
hosts such as LBNP, hand to partner onboarding after endpoint readback.

### Rollback notes

- **Render:** Dashboard → previous successful deploy → **Rollback** (or redeploy last known-good commit).
- **Vercel:** Promote prior deployment in project Deployments, or `vercel rollback` when available for the linked project.
- Keep Auth0 URLs additive (local + Render) so local demo automation still works after public deploy.

## Post-deploy probes

Allow cold start (~60s) on first Render hit after idle.

| Probe | Expect |
| --- | --- |
| `GET https://gateway.aadharcha.in/api/health` | 200 |
| `GET https://gateway.aadharcha.in/api/auth/providers` | JSON; `auth0: true` if Auth0 shipped |
| `GET …/ondc/np/buyer/status` and `…/seller/status` | 200 + key/onboard fields (not 404) |
| `GET …/ondc/np/lbnp/status` when shipping LOG10 | 200 + dedicated subscriber/key source; not Buyer/Seller identity |
| `GET https://ondcbuyer.aadharcha.in/ondc-site-verification.html` | 200 + meta `ondc-site-verification` |
| `GET https://ondcseller.aadharcha.in/ondc-site-verification.html` | same for seller |
| `GET https://ondclbnp.aadharcha.in/ondc-site-verification.html` | 200 + LBNP-specific verification after DNS/TLS |
| `POST` FQDN `/ondc/on_subscribe` (challenge fixture) | `{ "answer": "…" }` after gateway live |
| SPA shells | Buyer/Seller FQDN 200 Vite app **and** `assets/index-*.js` equals `*.vercel.app` |
| Auth SPA session | Buyer Sign out + `fetch(gateway/api/auth/me,{credentials:'include'})` authenticated |
| Auth SPA session | Buyer Sign out + `fetch(gateway/api/auth/me,{credentials:'include'})` authenticated |

Then hand back to partner-onboarding ladder (lookup / subscribe only if needed).

## Maintenance

| Event | Action |
| --- | --- |
| Cold start / 502 on first hit | `curl` `/api/health` and wait; retry once after 60s |
| Spin-down after ~15 min idle | Expected on Free — wake via health probe before demos |
| Auth0 / CORS mismatch | Fix dashboard URLs + `CORS_ORIGINS`; no code change needed |
| Portal key rotation | Update Render secrets / key dirs; **redeploy** (ephemeral FS) |
| Onboard 404 after code merge | Redeploy Render from commit that includes `ondc_onboard_routes.py` |
| Logs | `render logs` / Dashboard logs; Vercel project logs for rewrite 502s |
| Free Postgres nearing 30d | Migrate or delete — do not treat as durable |

## Ops stamps (2026-07-12 evening, $0 Free/Hobby)

| Item | Status |
| --- | --- |
| Render Free gateway | Custom domain `gateway.aadharcha.in` Verified + TLS; `PUBLIC_GATEWAY_URL` cut over; onrender subdomain kept |
| GoDaddy DNS | CNAME `gateway` → `identity-aadhar-gateway-main.onrender.com` (2026-07-12) |
| LBNP endpoint | Second included Render domain `ondclbnp.aadharcha.in`; GoDaddy CNAME → existing gateway; DNS/TLS/status/site/challenge passed 2026-07-26 |
| Realtime probe | `/api/realtime/status` → `configured:true` (via gateway FQDN **and** onrender) |
| Vercel Hobby | Buyer+Seller redeployed non-git bake; `VITE_IDENTITY_*=https://gateway.aadharcha.in`; alias FQDNs |
| Auth0 | Callback includes `gateway.aadharcha.in`; SPA session **PASS** (auth skill evidence) |
| Samantha “not configured” false negative | Fixed 17:48 — orb re-probes status; UI shows Text mode ready (evidence in testing-ledger matrix) |
| AgentGuard write on Free | Fix via **`DATA_DIR=/tmp/aadharchain-data`** (Dockerfile default + env); **no Disk** |
| Free-tier maximize | **Done** 2026-07-12 evening — `free-tier.md` stamp; health `/api/health`; Hobby Analytics Enable Buyer+Seller; $0 |
| PreProd ONDC enable | `ONDC_ENABLED=true` + BAP (`ONDC_SUBSCRIBER_ID`/`BAP_URI`/`UNIQUE_KEY_ID`) + BPP (`ONDC_BPP_ID`/`BPP_URI`/`ONDC_SELLER_UNIQUE_KEY_ID`); keep `*_PEM_B64` + `DATA_DIR=/tmp/aadharchain-data` |
| Vercel ONDC rewrites | **Both** apps need `/ondc/:path*` → `gateway…/ondc/np/{buyer\|seller}/:path*` (not only `on_subscribe`) — else `on_search`/`search` → SPA/405 |
| Nested git deploy | Gateway lives in **`aadharchain/`** nested repo (`ingpoc/aadhaar-chain`); workspace root gitignores it — workspace HEAD is not the gateway SHA. Exact-commit deploy that nested SHA to existing Free `identity-aadhar-gateway-main`; auto-deploy stays **off**. |
| GitHub multi-account | Before pushing `ingpoc/*`, run `gh auth status`; if another account is active, use `gh auth switch --hostname github.com --user ingpoc` + `gh auth setup-git --hostname github.com` |
| HUF git-author | Vercel monorepo git deploy → `TEAM_ACCESS_REQUIRED` — **always** non-git stage + `--archive=tgz` + alias FQDN |
| Hobby Vite bake | `.env.local` loopback must not win on FQDN — `loopback.ts` + empty commerce/`VITE_AGENT_CONTROL_PLANE_URL`; `/api/agent` → **gateway** (FlatWatch FQDN 401s portfolio `X-User-Id`) |

## CLI cheat sheet

```bash
# Render
render login   # if whoami → unauthorized
render services          # or Dashboard: identity-aadhar-gateway-main
render deploys create --service <service-id>
render logs --service <service-id>

# Vercel (Hobby: avoid HUF git-author block; fail-fast non-git stage + alias)
vercel login
./scripts/local-ship-gate.sh
./scripts/vercel_archive_deploy.sh buyer --confirm-free-tier
./scripts/vercel_archive_deploy.sh seller --confirm-free-tier
# Inspect the stage without deploying:
./scripts/vercel_archive_deploy.sh buyer --confirm-free-tier --stage-only
# Fail-closed public hash vs vercel.app (optional live probe):
python3 scripts/ondc_ci_graders.py --bundle-parity

# Probes (after wake)
curl -sS https://gateway.aadharcha.in/api/health
curl -sS https://gateway.aadharcha.in/api/ondc/status
curl -sS https://gateway.aadharcha.in/api/ondc/bpp/status
curl -sS -o /dev/null -w "%{http_code}\n" https://ondcbuyer.aadharcha.in/ondc-site-verification.html
curl -sS -o /dev/null -w "%{http_code}\n" https://ondcseller.aadharcha.in/ondc-site-verification.html
```

MCP: Cursor **Render** server when CLI unavailable — authenticate + **select
workspace** first; prefer read before mutating. Dashboard fallback uses bundled
`@chrome`.

## Do not

- Spend **any** money — abort upgrade / billing / paid add-on (Disk, paid instance, Pro)
- Attach Render Disk for PEMs (use env/secrets; Free has no Disk)
- Deploy without confirming Free (Render) / Hobby (Vercel)
- Auto-deploy production on every push — use **Portfolio Deploy** `workflow_dispatch` (or explicit CLI) after green graders
- Commit `.env`, portal `keys.json`, or PEMs
- Create a parallel gateway/service, reuse Retail keys, or publish DNS before the exact edge target is verified
- Claim **production** ONDC or flip commerce demo mode from this skill (PreProd Beckn ≠ prod)
- Make a legacy browser bridge a deploy precondition
