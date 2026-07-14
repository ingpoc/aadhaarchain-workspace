# Pre-deploy checklist (copy per run)

Gate: **all boxes before** `render` / `vercel --prod` / MCP deploy mutate.

```
Pre-deploy
- [ ] $0 ONLY: Render instance = Free; workspace = Hobby; Vercel = Hobby;
      abort upgrade/billing/paid Disk/Pro/Password Protection
- [ ] Maximize free features (see free-tier.md): DATA_DIR=/tmp/aadharchain-data;
      health check /health; Preview+Prod Vercel envs; FQDN aliases; Analytics on;
      Speed Insights Buyer-only; ≤2 Render custom domains; no card-overage trap
- [ ] Charge-risk watchlist scanned (Disk, Starter, Postgres day-30, domain #3,
      bandwidth near limit + payment method, Vercel Plus add-ons)
- [ ] CI graders green (Portfolio CI or local): gitleaks; verify-portfolio --ci;
      Buyer/Seller npm test + build — see references/ci-cd.md
- [ ] Local verify: ./scripts/verify-portfolio.sh (or agreed subset) if stack up
- [ ] Gateway local: GET :43101/api/health 200
- [ ] Onboard local (if shipping ONDC): GET :43101/ondc/np/buyer/status + seller/status ≠ 404
- [ ] Auth (if shipping Auth0): GET :43101/api/auth/providers → auth0 true; demo_continue policy matches AADHAAR_CHAIN_ENV
- [ ] Buyer/Seller build green if frontend changed: npm test && npm run build
- [ ] Secrets listed for Render (values in Dashboard/CLI only — not git):
      AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET
      SESSION_SECRET (or equivalent session HMAC secret)
      PUBLIC_GATEWAY_URL=https://gateway.aadharcha.in
      DATA_DIR=/tmp/aadharchain-data
      CORS_ORIGINS includes FQDNs + local ports
      ONDC subscriber ids + key material (env/dir strategy for ephemeral FS)
- [ ] No PEM / keys.json / .env staged for commit
- [ ] Auth0 Allowed Callback URLs include local + Render gateway callback
- [ ] Auth0 Logout + Web Origins include ondcbuyer/ondcseller FQDNs + local
- [ ] vercel.json rewrites point at gateway.aadharcha.in
      (buyer → /ondc/np/buyer/…; seller → /ondc/np/seller/…)
- [ ] VITE_IDENTITY_URL / VITE_IDENTITY_AUTH_ENABLED set for Vercel if auth UI shipping
      (Production **and** Preview)
- [ ] VITE_COMMERCE_DEMO_MODE not flipped without evidence gate
- [ ] WIP/Hermes not blocking — deploy does not need browser bridge
- [ ] Free-tier hard gate: cold start OK; no Disk for PEMs; zero cents / abort paid paths
- [ ] If using Actions deploy: GH secrets RENDER_* / VERCEL_* set (names in ci-cd.md)

Deploy order
- [ ] Prefer workflow_dispatch Portfolio Deploy (confirm_free_tier=true) OR:
- [ ] Redeploy Render gateway
- [ ] Wake + probe /api/health (allow ~60s cold start)
- [ ] Redeploy Vercel ondcbuyer
- [ ] Redeploy Vercel ondcseller

Post-deploy
- [ ] /api/auth/providers on Render
- [ ] /ondc/np/{buyer,seller}/status on Render
- [ ] FQDN /ondc-site-verification.html buyer + seller
- [ ] Optional: on_subscribe challenge fixture
- [ ] Hand off to partner-onboarding ladder for registry lookup/subscribe
```

## Secrets inventory (names only)

| Secret | Where |
| --- | --- |
| `AUTH0_*` | Render env; never Vite |
| `SESSION_SECRET` | Render env (session cookie HMAC) |
| `PUBLIC_GATEWAY_URL` | Render → public gateway origin |
| `CORS_ORIGINS` | Render — must list SPA FQDNs |
| ONDC PEMs / `ONDC_*_KEYS_DIR` | Render env or secret files rematerialized each deploy |
| `VITE_IDENTITY_URL` | Vercel build env (public gateway URL only) |

## Ephemeral FS strategy

1. Prefer encoding key paths that read from **env-provided PEM strings** or a **deploy hook** that writes PEMs from secrets into a tmp dir at boot.
2. On Render Free set **`DATA_DIR=/tmp/aadharchain-data`** (Dockerfile default) — never `./data` (Permission denied as `appuser`) and **never Disk**.
3. Do not SSH-copy PEMs onto Free instances and expect persistence.
4. After portal key rotation: update secrets → **redeploy** gateway → re-probe verification.

## Run stamp — 2026-07-12 FQDN redeploy ($0)

- [x] Render Free confirmed; gateway commit **`933cadf`** live; onboard status + providers 200
- [x] Key material via Render env `ONDC_{BUYER,SELLER}_*_PEM_B64` (ephemeral FS; no Disk)
- [x] Vercel Hobby; deployed to `ondc-buyer` / `ondc-seller` (FQDN owners `ondcbuyer` / `ondcseller.aadharcha.in`)
- [x] Post-deploy probes: GW health/providers/buyer+seller status **200**; FQDN `/ondc-site-verification.html` **200** + meta; `POST /ondc/on_subscribe` decrypt path live (400 on junk)
- [x] Aborted Pro Password Protection; no Disk / paid instance
- [x] PreProd lookup: auth required — no subscribe POST
- Detail twin: [`../../apisetu-partner-onboarding/references/ondc-sandbox-integration-ladder.md`](../../apisetu-partner-onboarding/references/ondc-sandbox-integration-ladder.md) Deploy stamp

## Run stamp — 2026-07-12 DATA_DIR AgentGuard write ($0)

- [x] Render Free env `DATA_DIR=/tmp/aadharchain-data` (Hermes dashboard Save+rebuild; no Disk)
- [x] Buyer FQDN: ensure **200**; checkout **Paid** + `rcpt_90c6dec41ab8400f` (ondc-testing matrix 17:56)
- [x] Seller FQDN: ensure **200** (no Errno 13)
- [x] SPA Auth0 session still authenticated via `gateway.aadharcha.in` cookie Domain
- [x] No paid upgrades; demo mode not flipped

## Run stamp — 2026-07-12 free-tier maximize applied live ($0)

- [x] `DATA_DIR` reconfirmed (AgentGuard ensure **200**); gateway redeploy skipped (env already live)
- [x] Vercel Hobby archive redeploy Buyer+Seller (`@vercel/analytics`; Buyer Speed Insights); FQDN aliases set
- [x] Post-probes: GW `/health`+`/api/health`/providers/ondc status **200**; SPA + verification **200**; insights script **200**
- [x] Render Settings health-check path `/api/health` (confirmed Free; evidence `references/evidence/render-health-path-edit-view-20260712.jpeg`)
- [x] Vercel Analytics **Enable** Hobby-included on `ondc-buyer` + `ondc-seller` (not Pro)
- [x] No Disk / Pro / paid add-ons

## Run stamp — 2026-07-12 evening demo-mode off + select/confirm ($0)

- [x] Gate: `commerce_demo_mode_gate.py --allow-with-evidence` → [`../ondc-testing/references/evidence/commerce-demo-mode-gate-20260712.json`](../ondc-testing/references/evidence/commerce-demo-mode-gate-20260712.json)
- [x] Gateway nested push **`1ba0a0c`** (select/init/confirm BAP+BPP); live note shows select/init/confirm; API ACK path proven
- [x] Vercel Hobby: `VITE_COMMERCE_DEMO_MODE=false` Prod+Preview Buyer+Seller; archive deploys `dpl_6ynH5M49…` / `dpl_J5rZDKoH…` + FQDN aliases
- [x] Proof: [`../ondc-testing/references/evidence/demo-mode-off-select-confirm-20260712.json`](../ondc-testing/references/evidence/demo-mode-off-select-confirm-20260712.json)
- [x] No Disk / Pro / paid add-ons; **not** production ONDC; payment still simulated

## Run stamp — 2026-07-12 web identity env ($0)

- [x] Vercel Hobby `ondcbuyer` + `ondcseller`: set Production+Preview `VITE_IDENTITY_*`, `VITE_COMMERCE_DEMO_MODE`, `VITE_AGENT_RUNTIME_ENABLED` (were empty — caused missing Sign in)
- [ ] Redeploy both after wallet-copy purge (WalletProvider stub; no Phantom/Solflare adapters)
- [ ] Render Free: `render login` required — CLI unauthorized; set `OPENAI_API_KEY`, `OPENAI_REALTIME_MODEL`, `CURSOR_API_KEY` from gateway `.env` (names only; never commit)
- [ ] Auth0: add Render callback URL (operator dashboard)
- [x] No paid upgrades; demo mode not flipped

### Vercel UNKNOWN queue / pnpm trap (2026-07-12)

- Stale `pnpm-lock.yaml` made Vercel use frozen `pnpm install` → fail; force `"installCommand": "npm install"` in app `vercel.json`; rename/remove stale pnpm lock.
- Vendor `@aadharchain/agentguard-contract` under `ondcbuyer|ondcseller/shared/` (`file:./shared/...`) so CLI uploads resolve.
- Multiple Production deploys stuck **UNKNOWN** with empty builds — cancel stuck deploys in dashboard; retry one at a time on Hobby ($0).

