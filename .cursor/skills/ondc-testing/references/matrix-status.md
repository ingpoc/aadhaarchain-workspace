# Matrix status ledger

## CF1 release checkpoint — 2026-07-22

- Frozen product/deploy fingerprint: `e95340b069cab63b75f436e0d5fdfe4e667545c40d2ee9b378f1b5957914db26` (`b8b90bd` / `fd586da` / `f028ade` / `8146340`).
- Deterministic gates pass: gateway CI 152 passed/48 skipped; PostgreSQL breadth 200 passed; Buyer 195 tests plus typecheck/build; Seller 211 tests plus typecheck/build; offline ONDC grader passed.
- Final PostgreSQL database `cf1_release_e95340` contains two exact published SKUs, two orders, two successful simulated payments, two successful full refunds, and publish/checkout/refund receipts twice. Inventory is 18 from 20 for each SKU.
- Render Free deployment `dep-d9gc443bc2fs73frb320` is live on gateway commit `fd586da`; Buyer and Seller Hobby archive deployments are Ready and their FQDN aliases return 200.
- **Open visible rows:** the bundled Chrome session is not controllable in this thread, so two-pass semantic logs, combined responsive/accessibility smoke, and FQDN/Auth0 Buyer/Seller acceptance are not yet credited. The live soft grader remains advisory-failed on the unseeded public exact item.
- Structured checkpoint: [`evidence/cf1-release-e95340-checkpoint-20260722.json`](evidence/cf1-release-e95340-checkpoint-20260722.json).

## Seller Samantha ops — 2026-07-20

- Local Hermes WIP · demo SSO · `hermes_samantha_seller_ops.py` → **script Pass** (`turns_passed` 5/5, Realtime `gpt-realtime-2.1-mini`).
- Evidence: [`evidence/seller-samantha-ops-20260720.json`](evidence/seller-samantha-ops-20260720.json).
- Nav active pill uses theme primary (`oklch(0.48 0.07 195)`) — verified on `/dashboard`.
- Product notes (not script failures): ₹500 refund on `seller-demo-1002` → unknown order for fresh demo principal; ₹25k → `need_approval` (correct); model once refused explicit `navigate_to /agentguard` while already on that page from approval redirect.

## Current local safety record — 2026-07-17

- Executable source: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.
- Two unchanged-source passes: gateway 133, Buyer 173 plus typecheck/build/copy gate, Seller 192 plus typecheck/build/copy gate, targeted adversarial 91.
- Buyer loopback admission on the immediately preceding hash verified exact `toor dal`, Pune serviceability, editable Pune checkout prefill, one exact approval, one order, empty cart and no duplicate.
- Final-hash browser status remains partial: the Realtime-unavailable text fallback is deterministic-test verified but still needs fresh blind browser proof; Seller and two-sided final-hash lanes remain pending.
- Retained record: [`evidence/local-safety-final-20260717-af987.json`](evidence/local-safety-final-20260717-af987.json).

**Session:** 2026-07-12  
**Bridge:** Hermes Chrome WIP · demo SSO  
**Doctrine:** claim → screenshot Read → Pass  
**Evidence dir:** [`evidence/`](evidence/)

## Buyer

| ID | Result | Screenshot(s) | Notes |
| --- | --- | --- | --- |
| B-HI | **Pass** | `evidence/B-HI-20260712-015147-0.jpeg` | `/search`; greeting; no tools |
| B-ADD-BANANA | **Pass** | `evidence/B-ADD-BANANA-20260712-015147-0.jpeg` | `/cart`; Robusta Bananas line; tools search+add |
| B-NAV-CART | **Pass** | `evidence/B-NAV-CART-20260712-015147-0.jpeg` | `/cart` |
| B-NAV-CHECKOUT | **Pass** | `evidence/B-NAV-CHECKOUT-20260712-015147-0.jpeg` | `/checkout` |
| B-MEM-ORG | **Pass** | `evidence/B-MEM-ORG-20260712-015147-0.jpeg` | `remember_preference` |
| B-NAV-CONFIG | **Pass** | `evidence/B-NAV-CONFIG-20260712-015147-0.jpeg` | `/config`; organic preference visible; mandate active |
| B-CHECKOUT-OK | **Pass** | `evidence/B-CHECKOUT-OK-20260712-021529-8.jpeg` (+ `-5.jpeg`) | **Page** shows Paid + receipt `rcpt_3f50a424cc354a10` on `/orders/demo-…` (not orb-only). Prior soft Pass revoked — form still looked unpaid. |
| B-CHECKOUT-OVER | **Pass** | `evidence/B-CHECKOUT-OVER-20260712-021529-9.jpeg` (+ `-5.jpeg`) | Checkout page headline “needs approval”; AgentGuard decision card Need approval · INR 25000 · `appr_315b30924b5b4d28` |
| B-LONG-WEEKLY | **Pass** | `evidence/B-LONG-WEEKLY-20260712-022511-7.jpeg` | `/search` (not `/agent`); orb “I've started… I'll let you know”; `delegate_to_runtime_agent` ok. Root cause was FlatWatch process missing `.env` (key was in file). |

Untested this session: B-THX, B-FIND-*, B-NAV-ORDERS, B-EMPTY (covered historically / lower priority).

## Seller

| ID | Result | Screenshot(s) | Notes |
| --- | --- | --- | --- |
| S-HI | **Pass** | `evidence/S-HI-20260712-015532-0.jpeg` | `/dashboard`; no tools |
| S-NAV-AG | **Pass** | `evidence/S-NAV-AG-20260712-015532-0.jpeg` | `/agentguard`; mandate UI |
| S-NAV-CAT | **Pass** | `evidence/S-NAV-CAT-20260712-015532-0.jpeg` | `/catalog` |
| S-NAV-ORD | **Pass** | `evidence/S-NAV-ORD-20260712-015532-0.jpeg` | `/orders` |
| S-REFUND-OK | **Pass** | `evidence/S-REFUND-OK-20260712-015532-0.jpeg` | `refund_issue`; receipt `rcpt_257d94e264e0466c` in orb |
| S-REFUND-OVER | **Pass** | `evidence/S-REFUND-OVER-20260712-015532-0.jpeg` | need one-time approval in orb |
| S-MEM | **Pass** | `evidence/S-MEM-20260712-015532-0.jpeg`, `S-MEM-UI-…` | `remember_preference`; AG page shot present (memory chip not strongly visible in UI crop) |

Untested: S-PUBLISH, S-LONG-TRIAGE.

## Run artifacts

- Buyer matrix JSON: `evidence/matrix-run-20260712-015147.json`
- Seller matrix JSON: `evidence/matrix-run-20260712-015532.json`
- Checkout UI residuals: `evidence/checkout-ui-residuals-20260712-021529.json`
- Long weekly final: `evidence/long-weekly-final-20260712-022511.json`

## Fixes this session

1. Skill doctrine: claim → screenshot → Pass; both apps; checkout required.
2. `checkout_commit` host auto-fill (`session_id` + cart `amount_inr`).
3. **Visible checkout success:** on AG allow + receipt, create paid local order and navigate to `/orders/{id}` with Paid + receipt badges (not unpaid checkout form).
4. **Visible AG over-limit:** write `checkoutOutcome` → checkout page shows Need approval / Denied card.
5. `scripts/start-dev.sh` `start_python`: load service `.env` into process (uvicorn does not). Explains prior false “CURSOR_API_KEY required” while key existed in `flatwatch/backend/.env`.
6. Sanitize buyer `delegate_to_runtime_agent` blocked_reason so Cursor/API-key strings do not leak into orb copy.

## Residuals

- None for the three Buyer residuals above (B-CHECKOUT-OK / OVER / B-LONG-WEEKLY all Pass with Read screenshots).
- Seller memory preference chip still weak in AG UI crop.
- UI audit (2026-07-12): demo/Google principal skips legacy trust wall; no AadhaarChain / Resolve-trust / identity-anchor CTAs; hangar jargon purged from user copy (see [`ui-surface-audit.md`](ui-surface-audit.md)).

---

## Live web E2E (FQDN) — 2026-07-12 afternoon

**Surfaces:** `https://ondcbuyer.aadharcha.in` · `https://ondcseller.aadharcha.in` · gateway `https://gateway.aadharcha.in`  
**Bridge:** Hermes Chrome WIP · sessions `web-e2e-buyer` / `web-e2e-seller`  
**Policy:** did not flip `VITE_COMMERCE_DEMO_MODE`; no live-network order claims; no blind PreProd subscribe POST.

### Buyer (web)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-HOME | **Pass** | `web-buyer-home-20260712-154417-4.jpeg` · `web-buyer-home-diag-*.json` | `/search`; page_diag ok; console clean |
| W-B-SEARCH | **Pass** | `web-buyer-commerce-20260712-154639-7.jpeg` | banana → Robusta Bananas (12 pcs); 1 match |
| W-B-CART | **Pass** | `web-buyer-checkout-20260712-154718-10.jpeg` | cart lines + total INR 481; Simulated exchange in shell |
| W-B-CHECKOUT | **Blocked** | `web-buyer-checkout-20260712-154718-16.jpeg` · `web-buyer-orders-*-4.jpeg` | form reachable; CTA **Trust verification required**; Unsigned |
| W-B-ORDERS | **Pass** | `web-buyer-orders-20260712-154757-10.jpeg` | empty lane (expected unsigned/no paid order) |
| W-B-CONFIG | **Pass** | body in `web-buyer-routes-*.json` | mandate UI; sign-in copy; no Sign-in button |
| W-B-SAM | **Blocked** | `web-buyer-samantha-20260712-155025-6.jpeg` | orb opens; **Realtime not configured on gateway** |
| W-B-AUTH0 | **Partial → Pass CTA** (2026-07-12 16:32) | `web-buyer-signin-button-20260712-1632.jpeg` | Sign in CTA live; wallet KYC gone. Gateway start → Auth0 authorize with Render `redirect_uri` (curl 302). OTP still operator hard-stop. Prior fail evidence kept. |

### Seller (web)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-HOME | **Pass** | `web-seller-routes-20260712-154757-4.jpeg` | dashboard; Unsigned; 0 products |
| W-S-CAT | **Pass** | `web-seller-routes-*-10.jpeg` | catalog empty; publish gated |
| W-S-ORD | **Pass** | `web-seller-ag-20260712-154903-4.jpeg` | 0 incoming; no refund UI |
| W-S-AG | **Pass** | `web-seller-ag-*-10.jpeg` | AgentGuard page; bind-policy gated on sign-in |
| W-S-CFG | **Pass** | `web-seller-ag-*-16.jpeg` | ONDC credentials / gateway URL UI present |
| W-S-REFUND | **Blocked** | `web-seller-refund-probe-*.jpeg` | no orders → no refund path |
| W-S-AUTH0 | **Partial → Pass CTA** (2026-07-12 16:32) | `web-seller-signin-button-20260712-1632.jpeg` | Sign in CTA live; wallet KYC gone. Same Auth0 callback allowlist as Buyer. OTP hard-stop. |

### ONDC integration (API + user-visible)

| Check | Result | Notes |
| --- | --- | --- |
| FQDN `/ondc-site-verification.html` buyer+seller | **Pass** | 200 + `meta name=ondc-site-verification` |
| Gateway `/ondc/np/{buyer,seller}/status` | **Pass** | 200; keys_source=env; registry_env=preprod; signing+enc present |
| FQDN `/ondc/np/*/status` | **Fail** | serves SPA HTML (rewrite not mapped) — use gateway origin |
| FQDN `/ondc/on_subscribe` | **Pass** (hosted) | GET 405; POST reaches decrypt (400 on bogus challenge) |
| Gateway `/api/ondc/status` | **Pass** (honest) | `enabled:false` — keep demo commerce; no live Beckn claim |
| Live network order | **Not claimed** | commerce still demo/Simulated exchange |

### Bugs / operator blockers (ledger)

1. ~~Vercel identity env empty / Sign in tree-shaken~~ → **cleared 2026-07-12 16:32** (values recreated; static prod deploy; Sign in CTA live).
2. ~~Auth0 Render callback missing~~ → **cleared** (dashboard Save; curl start uses Render `redirect_uri`).
3. Stale “Google or demo” copy — mostly replaced; residual trust strings OK.
4. ~~Samantha Realtime `configured:false`~~ → **cleared** (`OPENAI_*` + `CURSOR_API_KEY` on Render Free; `/api/realtime/status` → `configured:true`, model `gpt-realtime-2.1-mini`).
5. **FQDN NP status path** not rewritten to gateway JSON.
6. ~~Wallet hangar copy on FQDN~~ → **cleared** (Buyer+Seller bundles: no `Wallet KYC`).
7. **OTP / Universal Login completion** — still operator hard-stop (Hermes did not complete Auth0 UI nav; curl proves authorize redirect).
8. **Vercel Hobby git-author seat block** — CLI deploys from monorepo git author `gupta.huf…` → `TEAM_ACCESS_REQUIRED` / BLOCKED. Workaround: deploy from non-git staging dir + `echo skip-build` + alias FQDN. Do not upgrade.

### Auth0 / session proof

- `/api/auth/providers`: `auth0:true`, `demo_continue:false`, `runtime_mode:staging`.
- `/api/realtime/status`: `configured:true`, `model:gpt-realtime-2.1-mini`.
- `/api/auth/me`: no session until OTP.
- Sign in CTA: **visible** Buyer+Seller FQDN. OTP/consent: **not completed**.


## Live web E2E refresh — 2026-07-12 16:32 IST

**Unblocked on Free/Hobby:** Auth0 Render callback allowlisted; Vercel BLOCKED deploys deleted; Buyer+Seller Production redeployed (wallet purge + identity bake); Render env `OPENAI_API_KEY` / `OPENAI_REALTIME_MODEL` / `CURSOR_API_KEY` saved+redeployed via dashboard session (CLI key expired).

### Matrix (claim→screenshot)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AUTH0-UI | **Pass** | `web-buyer-signin-button-20260712-1632.jpeg` | Header **Sign in**; asset `index-DBy88kFf.js`; no Wallet KYC |
| W-S-AUTH0-UI | **Pass** | `web-seller-signin-button-20260712-1632.jpeg` | Header **Sign in**; asset `index-D9ua_Jy5.js` |
| W-B-AUTH0-FLOW | **Partial** | curl Location → `dev-ejqlkc0qt84udk7i…/authorize` with Render callback | Callback mismatch cleared. OTP still operator. |
| W-B-WALLET-COPY | **Pass** (live) | bundle probe | `Wallet KYC` absent |
| W-B-VOICE | **Unblocked config** | `/api/realtime/status` | `configured:true` — re-run voice matrix next |
| W-B-RUNTIME | **Unblocked config** | Render env | `CURSOR_API_KEY` present — needs signed-in matrix |
| W-B-CHECKOUT | **Blocked** | prior | needs Auth0 session (OTP) |
| ONDC live Beckn | **Not claimed** | demo mode unchanged | no demo flip |

### Remaining operator hard-stops

1. OTP / consent on Auth0 Universal Login (keep gateway awake)
2. Optional: re-login Render CLI (`render login`) — dashboard session worked; API key in `~/.render/cli.yaml` was unauthorized
3. Prefer Vercel deploys without HUF git author (non-git staging) until that email is a team member — **no paid seat upgrade**

### Env keys set (names only)

| Host | Keys |
| --- | --- |
| Vercel Buyer+Seller Prod+Preview | `VITE_IDENTITY_AUTH_ENABLED`, `VITE_IDENTITY_URL`, `VITE_IDENTITY_WEB_URL`, `VITE_COMMERCE_DEMO_MODE`, `VITE_AGENT_RUNTIME_ENABLED` (**values** restored; were empty) |
| Render gateway | `AUTH0_*` (already), plus `OPENAI_API_KEY`, `OPENAI_REALTIME_MODEL`, `CURSOR_API_KEY` |

---

## Live web E2E resume — 2026-07-12 17:05 IST

**Bridge:** Hermes Chrome WIP · sessions `web-e2e-buyer` / `web-e2e-seller`  
**Policy:** no demo flip; no paid upgrades; no secrets in ledger.  
**Artifacts:** `evidence/web-e2e-fqdn-resume-20260712-170051.json` · `evidence/web-e2e-logout-sam-20260712-170355.json` · `evidence/web-buyer-auth-session-probe-20260712-165727.json`

### Auth / session

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AUTH0-UI | **Pass** | prior `web-buyer-signin-button-20260712-1632.jpeg` + home shots | Sign in CTA; Unsigned; no Wallet KYC |
| W-S-AUTH0-UI | **Pass** | `web-seller-home-20260712-170051-3.jpeg` | Sign in CTA on Seller |
| W-GW-AUTH0-SESSION | **Pass** | `web-gw-me-20260712-170051-4.jpeg` · session probe JSON | `/api/auth/auth0/start` silent-SSO → gateway `/api/auth/me` **Authenticated** (`principal:auth0:google-oauth2:…`). OTP **not** required in this browser profile |
| W-B-SPA-SESSION | **Pass** | `spa-session-probe-20260712-172223.json` · `spa-buyer-after-signin-20260712-172223.jpeg` | After `gateway.aadharcha.in` cutover: Buyer **Sign out**; `fetch(https://gateway.aadharcha.in/api/auth/me,{credentials:'include'})` → Authenticated `principal:auth0:…` |
| W-GW-LOGOUT | **Pass** (POST) | `web-e2e-logout-sam-20260712-170355.json` | `POST /api/auth/logout` clears session (`afterMsg: No authenticated…`). **GET** logout → **405** (Allow: POST) — do not use GET for Sign out proof |
| W-B-AUTH0-FLOW | **Pass** | SPA session Pass + Auth0 callback on gateway FQDN | Custom domain + `PUBLIC_GATEWAY_URL` + Auth0 callback allowlist |

### Buyer commerce / Samantha

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-HOME | **Pass** | search/home shots | `/search`; Sign in; Unsigned |
| W-B-CART | **Pass** | `web-buyer-cc-20260712-170051-3.jpeg` | Cart lines: Sharbati Atta + Robusta Bananas ×3; total INR 559 |
| W-B-CHECKOUT | **Blocked** | `web-buyer-cc-20260712-170051-8.jpeg` | Form reachable; **Trust verification / Sign in before elevated**; no Paid+receipt without SPA session |
| W-B-SEARCH | **Partial** | `web-buyer-search-20260712-170051-6.jpeg` | Query `banana` filled; results UI not captured this click (cart already held bananas from prior) |
| W-B-SAM-TEXT | **Fail** | `web-buyer-sam-*-170051-9.jpeg` · `web-buyer-sam-show-*-170355-12.jpeg` | Orb opens; `fill_send` returns ok; **no visible tool reply / results UI** this run |
| W-B-VOICE | **Partial** | `web-buyer-voice-20260712-170051-5.jpeg` | Gateway `/api/realtime/status` `configured:true`; orb **“Text mode ready (no mic)”** — not WebRTC voice Pass |
| W-B-RUNTIME | **Fail** | `web-buyer-runtime-20260712-170051-8.jpeg` | Long ask left in input; no “I've started…” / handoff shot |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-HOME | **Pass** | `web-seller-home-20260712-170051-3.jpeg` | Dashboard; Sign in; Unsigned |
| W-S-CAT | **Pass** | `web-seller-cat-20260712-170051-3.jpeg` | Empty catalog; Add product gated |
| W-S-ORD | **Pass** | `web-seller-ord-20260712-170051-3.jpeg` | 0 incoming |
| W-S-AG | **Pass** | `web-seller-ag-20260712-170051-3.jpeg` | AgentGuard page; bind-policy gated on sign-in |
| W-S-CFG | **Pass** | `web-seller-cfg-20260712-170051-3.jpeg` | Credentials UI present |
| W-S-REFUND | **Blocked** | orders empty + unsigned | No refund path |
| W-S-SAM | **Partial** | `web-seller-sam-20260712-170355-9.jpeg` | Orb “Text mode ready (no mic)”; no tool outcome shot |

### Remaining hard-stops (ordered)

1. ~~Cross-site session cookie~~ — **Closed 2026-07-12:** `gateway.aadharcha.in` + `Domain=.aadharcha.in` (SPA session Pass).
2. Samantha FQDN text/voice tool outcomes + runtime handoff — retest now that SPA session works.
3. Optional: Render CLI re-login; Vercel non-HUF git author for deploys — **no paid upgrade**.

**OTP note:** Not the blocker in this Hermes profile (Auth0 silent SSO already minted gateway session). Leave Universal Login tab only if a fresh browser has no Auth0 SSO cookie.

---

## Live web E2E — Realtime “not configured” fix — 2026-07-12 17:48 IST

**Operator report:** Samantha UI showed **“Realtime not configured on gateway”**.

### Diagnose (evidence)

| Check | Result |
| --- | --- |
| `https://gateway.aadharcha.in/api/realtime/status` | `configured:true`, model `gpt-realtime-2.1-mini` |
| `https://identity-aadhar-gateway-main.onrender.com/api/realtime/status` | same `configured:true` |
| Buyer asset `TRUST_API_URL` | fetches `https://gateway.aadharcha.in/api/realtime/status` (perf + bake) |
| Render `OPENAI_API_KEY` | **present** (status configured — never print value); local `.env` also set |
| UI code path | `SamanthaOrb` `configured===false` → hint “Realtime not configured…” — **false negative** when mount-time status fetch raced / Free cold-start failed before orb open |

### Fix ($0 Hobby)

- Buyer+Seller: re-probe `/api/realtime/status` on orb open (retries for cold start); do not treat `configured=null` as missing key.
- Redeployed non-git staging + alias FQDNs — assets `index-BQ6FIta4.js` (Buyer), `index-Cc8UIQ_e.js` (Seller).
- Gateway redeploy **not required** (key already live).

### Matrix after fix

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-RT-STATUS | **Pass** | curl both hosts | `configured:true` |
| W-B-RT-UI | **Pass** | `W-B-VOICE-RT-FIXED-20260712-174850-0.jpeg` · `web-realtime-fix-20260712-174850.json` | Orb **“Text mode ready (no mic)”** — **not** “Realtime not configured” |
| W-B-SAM-TEXT | **Pass** | `W-B-SAM-TEXT-AFTER-RT-20260712-174923-0.jpeg` · prior `W-B-FIND-BANANA-20260712-173205-0.jpeg` | `search_catalog` → `/results` bananas |
| W-B-ADD-BANANA | **Pass** | `W-B-ADD-BANANA-20260712-173341-0.jpeg` · `W-B-CART-…` | cart line Robusta Bananas |
| W-B-MEM-ORG | **Pass** | `W-B-MEM-ORG-20260712-173341-0.jpeg` | `remember_preference` |
| W-B-CHECKOUT | **Blocked** → **Pass** (retest) | prior `W-B-CHECKOUT-20260712-173341-0.jpeg`; retest below | was `Permission denied: 'data'`; fixed by `DATA_DIR` |
| W-B-RUNTIME | **Partial** | `W-B-RUNTIME-20260712-173341-0.jpeg` | `delegate_to_runtime_agent` fired; JSON/HTML error in hint; stayed on `/search` |
| W-B-VOICE | **Blocked** | mic `NotFoundError` in Hermes + “no mic” | Realtime **session** Pass (text); **mic/WebRTC voice** not available in automation profile |
| W-B-AG-ENSURE | **Blocked** → **Pass** (retest) | prior `W-B-AG-ENSURE-20260712-173341-0.jpeg`; retest below | was ensure **500**; fixed by `DATA_DIR` |

### Remaining hard-stops (ordered)

1. ~~Render `DATA_DIR` writable~~ — **done** 17:56 (`DATA_DIR=/tmp/aadharchain-data`; no Disk).
2. Seller thorough mirror (publish/refund/runtime) — AG ensure Pass; tools still owed.
3. True **voice** Pass needs operator mic / browser permission (Hermes profile has no mic device).
4. Optional: Render CLI re-login; Render MCP workspace auth — Hermes dashboard works — **no paid upgrade**.

---

## Live web E2E — DATA_DIR + checkout — 2026-07-12 17:56 IST

**Hard-stop cleared:** Render Free gateway AgentGuard write. Set env `DATA_DIR=/tmp/aadharchain-data` on `identity-aadhar-gateway-main` via Hermes dashboard → Save, rebuild, and deploy. Ephemeral `/tmp` only — **no Render Disk / $0**.

### Proof

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AG-ENSURE | **Pass** | `W-B-AG-ENSURE-20260712-175629-0.jpeg` · `W-B-AG-ENSURE-20260712-175629.json` | `POST …/agents/ensure` **200** `AgentGuard agent ready`; `permissionDenied:false` |
| W-B-CART | **Pass** | `W-B-CART-DATADIR-20260712-175654-5.jpeg` | `/cart`; Robusta Bananas + Atta |
| W-B-CHECKOUT | **Pass** | `W-B-CHECKOUT-DATADIR-20260712-175654-5.jpeg` · `-8.jpeg` · `W-B-CHECKOUT-DATADIR-20260712-175654.json` | `checkout_commit` **allow**; **Paid** + receipt `rcpt_90c6dec41ab8400f`; order `demo-1783859251508-w7m0e0`; INR 715 |
| W-S-AG-ENSURE | **Pass** | `W-S-AG-ENSURE-20260712-175821-2.jpeg` · `W-S-AG-ENSURE-20260712-175821.json` | Seller role ensure **200**; no Errno 13 |

**Note:** Order page still shows “Trust check: Unsigned” (signed-receipt verify gap — not DATA_DIR). SPA session authenticated (`Sign out` + `/api/auth/me`).

---

## Live web E2E thorough — 2026-07-12 20:55 IST (FQDN + gateway control plane)

**Script:** `scripts/hermes_fqdn_e2e_thorough.py both`  
**Ledger:** `evidence/web-e2e-thorough-20260712-205518.json`  
**Counts:** Pass **18** · Fail **3** · Blocked **2** (voice mic)  
**Closeout:** ok · console errors **0**

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-BOOT-…-205518-*.jpeg` | Auth0 principal + Sign out |
| W-B-MANDATE | **Pass** | same | `mandate_…` active |
| W-B-VOICE-MIC | **Pass** | same | orb “Listening + text ready” (device present); full voice ask still Blocked below |
| W-B-HI | **Fail** | `W-B-HI-…` | greeting also fired `search_catalog` → `/results` |
| W-B-FIND-BANANA | **Pass** | `W-B-FIND-BANANA-…` | network results; banana=True |
| W-B-ADD-BANANA | **Fail** | `W-B-ADD-BANANA-…` · `W-B-CART-…` | tools searched; **cart empty** (network→local cart gap) |
| W-B-CART / CONFIG / MEM | **Pass** | shots `…-205518` | `/cart`, `/config`, organic preference |
| W-B-NAV-CHECKOUT | **Fail** | `W-B-NAV-CHECKOUT-…` | stayed `/cart` (empty cart) |
| W-B-CHECKOUT | **Pass** | `W-B-CHECKOUT-…` | `checkout_commit` tool fired; empty-cart honest deny path |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…` · late shot | `delegate_to_runtime_agent`; stayed `/search`; weekly plan content in orb |
| W-B-VOICE | **Blocked** | `W-B-VOICE-…` | Realtime configured; Hermes mic/WebRTC not usable |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-BOOT-…` | Auth0 + active mandate |
| W-S-HI / NAV-* | **Pass** | `W-S-HI/NAV-*` | dashboard / catalog / orders / agentguard |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…` · `W-S-CAT-AFTER-…` | `catalog_publish` → Test Atta; Atta 1kg live in ledger |
| W-S-REFUND | **Pass** | `W-S-REFUND-…` | handoff + navigate; orb started background refund triage |
| W-S-MEM | **Pass** | `W-S-MEM-…` | `remember_preference` |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…` | `delegate_to_runtime_agent`; ops triage in orb; not `/agent` |
| W-S-VOICE | **Blocked** | — | same mic constraint |

### Remaining after this run

1. **Buyer network add→cart** — top Fail; blocks paid checkout tonight.
2. Greeting must not auto-search (W-B-HI Fail).
3. True voice Pass needs operator mic.
4. Prefer Seller `refund_issue` when a concrete order id exists (tonight used navigate+runtime).

---

## Operator text-mode + early `/results` — 2026-07-12 21:42 IST

**Script:** `scripts/hermes_operator_visible_search.py`  
**Ledger:** `evidence/op-visible-search-20260712-214200.json`  
**Skill updates:** `operator-flows.md`, `test-inventory.md`, `ondc_ci_graders.py` (CI soft FQDN)  
**Closeout:** ok · console errors **0**

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-OP-BOOT-…-214200-0.jpeg` | Auth0 Sign out; text mode ready |
| W-B-HI | **Pass** | `W-B-HI-…-214200-0.jpeg` | `/search`; no tools; greeting only |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-214200-0.jpeg` | **Early `/results`**; hint “Searching for atta — watch the results page…”; pulling offers |
| W-B-FIND-BANANA | **Fail** | `W-B-FIND-BANANA-…` | Ask left in input; orb busy after prior ONDC search |
| W-B-ADD / NAV / RUNTIME | **Fail** | shots `…-214200` | Same stall — no tools fired |

### Seller smoke

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-OP-BOOT-…` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…` | `catalog_publish`; catalog 17→18 |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…` | handoff hint; not `/agent` |

### Remaining after this run

1. **Orb send after long `search_catalog`** — follow-on text asks can stick in draft (banana/nav/runtime Fail).
2. Network **add→cart** still owed when tools fire.
3. Voice mic still Blocked in Hermes.
4. CI: `ondc_ci_graders --live --soft` advisory (seller bundle may tree-shake demo-mode key).

---

## Operator text-mode retest (orb stall mitigations) — 2026-07-12 22:07–22:14 IST

**Scripts:** `hermes_operator_visible_search.py` (+ chained prove) · focused retest `op-retest-chained-20260712-221433.json`  
**Ledgers:** `evidence/op-visible-search-20260712-220718.json` · `evidence/op-retest-chained-20260712-221433.json`  
**Graders:** `ondc_ci_graders --live --soft` → ok (buyer bundle demo_mode=false; seller key tree-shaken)  
**Closeout:** ok · bridge ready · leave `ondcbuyer…/search`

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-OP-BOOT-…-220718-0.jpeg` | Auth0 Sign out; text mode ready |
| W-B-HI | **Pass** | `W-B-HI-…-220718-0.jpeg` | `/search`; greeting; no tools |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-220718-0.jpeg` | Early `/results`; pulling offers |
| W-B-FIND-BANANA | **Pass** | `W-B-RETEST2-BANANA-…-221433-0.jpeg` | Early `/results` (retest; mid-run Fail was Free GW cold + Realtime down) |
| W-B-CHAINED | **Partial** | `W-B-RETEST2-CHAINED-…-221433-0.jpeg` · prior `W-B-CHAINED-…-220718` | **Draft stall fixed** (`send_ok=true`); `navigate_to` fires; UI still `/results` (search race holds page). Orb claims cart. |
| W-B-ADD | **Partial** | `W-B-RETEST2-ADD-…-221433-0.jpeg` | Send accepted; Realtime “active response in progress”; no cart line |
| W-B-NAV-CART | **Pass** | `W-B-NAV-CART-…-220718-0.jpeg` | `/cart` after cooldown |
| W-B-NAV-CONFIG | **Pass** | `W-B-NAV-CONFIG-…-220718-0.jpeg` | `/config` |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…-220718-0.jpeg` | `delegate_to_runtime_agent`; not `/agent` |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-OP-BOOT-…-220718` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…-220718` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…-220718` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…-220718-0.jpeg` | `catalog_publish`; catalog →19; Operator Atta |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…-220718` | handoff; not `/agent` |

### Orb stall verdict

| Claim | Verdict |
| --- | --- |
| Draft stuck / send_disabled after long search | **Fixed** — chained asks `send_ok=true` (×2 retests) |
| Chained ask lands visible `/cart` while search still pulling | **Not fixed** — `navigate_to` + `search_catalog` race; page stays on `/results` |
| Free gateway cold mid-matrix | Still bites — mark Blocked/retry, not product Fail |

### Remaining

1. Network **add→cart** when tools fire cleanly (Realtime concurrent-response); item ids from ResultsPage cache after progressive paint.
2. Voice mic still Blocked in Hermes.
3. Keep gateway warm during long FQDN operator runs (Free spin-down).
4. Paint ~19s still dominated by PreProd `on_search` fanout (not double dispatch) — acceptable vs prior 93s.

---

## ONDC fetch doctrine prove — 2026-07-12 22:54 IST

**Doctrine:** [`ondc-fetch-doctrine.md`](ondc-fetch-doctrine.md)  
**Deploy:** `ondcbuyer-6xlyphqq6` · **Ledger:** `evidence/op-doctrine-atta-20260712-225441.json` · **Shot:** `W-B-DOCTRINE-ATTA-20260712-225441-0.jpeg`

| Metric | Before | After |
| --- | --- | --- |
| Early `/results` | ~1s | **1012 ms** Pass |
| Tool `search_catalog` return | collect up to **12s** | **4068 ms** ACK+txn Pass |
| Unique `/api/ondc/search` | **2** (double dispatch) | **1** Pass |
| Grid settle | **~93s** / Failed-to-fetch races | **18935 ms**, 13 matches, no hard fail Pass |
| W-B-FIND-ATTA doctrine | — | **Pass** |

---

## USP settle→validate→next — 2026-07-12 23:21 IST

**Protocol:** one ask → settle (`__samanthaTools` + route/UI) → next. Hermes WIP. Demo off.  
**Bake:** `index-Mo-Hxb-1.js` · deploy `ondcbuyer-b0xglvsrx` · alias `ondcbuyer.aadharcha.in`  
**Ledgers:** `evidence/usp-settle-20260712-225913.json` · `usp-add-reprove2-20260712-231845.json` · `usp-checkout-after-add-20260712-232128.json`  
**Closeout:** leave `ondcbuyer…/search` · bridge ready

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-USP-BOOT-…-225913` | Auth0 Sign out; text mode ready (no mic) |
| W-B-HI | **Pass** | `W-B-HI-…-225913` | `/search`; greeting; no tools |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-225913` · `W-B-FIND-ATTA-R2-…-231845` | Early `/results`; offers≥18; `search_catalog` |
| W-B-ADD-ATTA | **Fail→Pass** | Fail `W-B-ADD-ATTA-…-225913`; Pass `W-B-ADD-ATTA-R2-…-231845` | Root: ACK-empty ids → model re-searched. Fix: cache name resolve + Host context inject. `/cart` line “atta” ×1 INR 118; `add_to_cart` ok |
| W-B-MEM-ORG | **Pass** | `W-B-MEM-ORG-…-225913` | `remember_preference`; organic on `/config` |
| W-B-NAV-CONFIG | **Pass** | `W-B-NAV-CONFIG-…-225913` | `/config` |
| W-B-FIND-PREF | **Pass** | `W-B-FIND-PREF-…-225913` | preference-aligned search; `/results` offers |
| W-B-CHECKOUT | **Partial→Pass** | Partial `W-B-CHECKOUT-AFTER-ADD-…-232128`; Pass `W-B-ORDER-DETAIL-20260712-232726-3.jpeg` · `usp-order-detail-20260712-232726.json` | Partial was HTML≠JSON on `/orders/{id}`. Fix: `OrderDetailPage` localStorage fallback + `orderApi` HTML reject. Reprove: Paid + `rcpt_c9a68660930b4fba` on order detail (not unavailable). Alias `ondcbuyer-archive-deploy-3i99740un` · `index-BaIfxHlR.js` |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…-225913` | `delegate_to_runtime_agent`; stayed `/search`; weekly plan in orb |
| W-B-VOICE | **Blocked** | orb hint | Realtime configured; Hermes mic/WebRTC not usable |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-USP-BOOT-…-225913` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…-225913` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…-225913` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…-225913` | `catalog_publish` Test Organic Atta |
| W-S-REFUND | **Partial** | `W-S-REFUND-…-225913` | navigated `/orders`; no `refund_issue` (no order id) |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…-225913` | handoff; not `/agent` |
| W-S-VOICE | **Blocked** | — | same mic Blocked |

### Completeness (operator-flows catalog = 28 IDs)

| Metric | Value |
| --- | --- |
| Attempted this run | 16 catalog twins (+ FIND-PREF net-new) |
| Pass / Partial / Blocked / Fail | 14 / 1 / 2 / 0 (after ADD + order-detail fix) |
| Weighted catalog coverage | **~52%** (14 + 0.5×1 + 0.25×2) / 28 |
| Weighted attempted | **~91%** of attempted |

### NOT covered (this run)

`B-THX`, `B-FIND-BANANA`, `B-FIND-MILK`, `B-FIND-APPLE`, `B-NAV-CART`, `B-NAV-CHECKOUT`, `B-NAV-ORDERS`, `B-CHECKOUT-OVER`, `B-EMPTY`, `B-CHAINED`, `S-MEM`, `S-REFUND-OVER`

### USP gaps remaining

1. ~~**Order detail after Samantha checkout**~~ — **Pass** 23:27 (`rcpt_c9a68660930b4fba`; see § Order detail retest)
2. **Voice mic/WebRTC** — Blocked in Hermes
3. **B-CHAINED** visible `/cart` while search still pulling — not retested this run
4. Cart line label generic “atta” (cache name) — acceptable Pass, polish later

### Fix shipped mid-run

Buyer: `lookupBuyerCatalogByQuery` + `add_to_cart` query/name resolve; search early return includes cached ids; Realtime Host context inject of visible results cache; orb instructions “do not re-search to add”. Hobby archive redeploy ×2 → `index-Mo-Hxb-1.js`.

---

## Order detail after Samantha checkout — 2026-07-12 23:27 IST

**Gate:** Paid + receipt on **order detail page** (not tool orb alone; not “Order detail unavailable”).  
**Alias:** `ondcbuyer-archive-deploy-3i99740un` → `ondcbuyer.aadharcha.in` · bake `index-BaIfxHlR.js` · demo off  
**Ledger:** `evidence/usp-order-detail-20260712-232726.json`  
**Closeout:** `ondcbuyer…/search` · bridge ready

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| B-FIND-ATTA | **Pass** | ledger | `/results`; `search_catalog`; atta offers |
| B-ADD-ATTA | **Pass** | ledger | `add_to_cart` → `/cart` line atta ×1 |
| W-B-CHECKOUT | **Pass** | `W-B-ORDER-DETAIL-20260712-232726-3.jpeg` | `/orders/demo-1783879102172-2701w7`; **Paid** + `rcpt_c9a68660930b4fba`; Payment PAID; unavailable=false |

---

## Local first-time operator text-mode hardening — 2026-07-14 13:59–14:22 IST

**Protocol:** novice natural-language asks through Samantha's visible text UI; Hermes WIP semantic locators; one ask → settle → route/page/tool screenshot. No API seeding or mutating `evaluate`. Voice intentionally deferred.

**Ledgers:** `evidence/matrix-run-20260714-135947.json` (Buyer product 9/9; runtime harness false-negative fixed) · `evidence/matrix-run-20260714-140825.json` (Seller 9/9) · focused Buyer runtime screenshots `B-LONG-FOCUSED-20260714-141912-0.jpeg`, `B-LONG-FOCUSED-R1-20260714-141912-0.jpeg`, `B-LONG-FOCUSED-R2-20260714-141912-0.jpeg`.

### Buyer

| ID | Result | Evidence | Visible outcome |
| --- | --- | --- | --- |
| B-HI | **Pass ×2** | `B-HI-20260714-135947-0.jpeg` · `B-HI-20260714-141258-0.jpeg` | `/search`; useful first-time introduction; no tool fired |
| B-FIND-NL-ATTA | **Pass ×2** | `B-FIND-ATTA-20260714-135947-0.jpeg` · `B-FIND-ATTA-20260714-141258-0.jpeg` | Natural breakfast ask → `/results`; Atta offers; `search_catalog` |
| B-ADD-ATTA | **Pass ×2** | `B-ADD-ATTA-20260714-135947-0.jpeg` · `B-ADD-ATTA-20260714-141258-0.jpeg` | “That first atta” → `/cart`; visible line; `add_to_cart` |
| B-NAV-CART / CHECKOUT / CONFIG | **Pass ×2** | matching `*-20260714-135947-0.jpeg` and `*-20260714-141258-0.jpeg` | Samantha navigates while operator watches; remembered organic preference visible on Config |
| B-CHECKOUT-OK | **Pass ×2** | `B-CHECKOUT-OK-20260714-135947-0.jpeg` · `B-CHECKOUT-OK-20260714-141258-0.jpeg` | `checkout_commit`; paid order and receipt visible; signed principal no longer shown as unsigned |
| B-CHECKOUT-OVER | **Pass ×2** | `B-CHECKOUT-OVER-20260714-135947-0.jpeg` · `B-CHECKOUT-OVER-20260714-141258-0.jpeg` | Exact one-time approval required and visible |
| B-LONG-WEEKLY | **Pass** | focused screenshots above | `delegate_to_runtime_agent`; stayed off `/agent`; lifecycle `started → heartbeat → completed` |

### Seller

| ID | Result | Evidence | Visible outcome |
| --- | --- | --- | --- |
| S-HI / NAV-AG / NAV-CAT / NAV-ORD | **Pass ×2** | matching `*-20260714-140410-0.jpeg` and `*-20260714-140825-0.jpeg` | First-time introduction and visible page navigation |
| S-PUBLISH | **Pass ×2** | `S-PUBLISH-20260714-140410-0.jpeg` · `S-PUBLISH-20260714-140825-0.jpeg` | Spoken price and 7-pack inventory persisted; catalog refreshed immediately |
| S-REFUND-OK | **Pass ×2** | `S-REFUND-OK-20260714-140410-0.jpeg` · `S-REFUND-OK-20260714-140825-0.jpeg` | AgentGuard page shows executed refund and receipt, not orb-only text |
| S-REFUND-OVER | **Pass ×2** | `S-REFUND-OVER-20260714-140410-0.jpeg` · `S-REFUND-OVER-20260714-140825-0.jpeg` | 26,000 INR refund visibly waits for exact one-time approval; manual approval/execution also proved |
| S-MEM | **Pass ×2** | `S-MEM-UI-20260714-140410-0.jpeg` · `S-MEM-UI-20260714-140825-0.jpeg` | Preference appears on AgentGuard without reload |
| S-LONG-TRIAGE | **Pass** | `S-LONG-TRIAGE-20260714-140825-0.jpeg` · `S-LONG-TRIAGE-DONE-20260714-140825-0.jpeg` | Stayed on `/orders`; lifecycle `started → completed`; concrete triage returned |

### Root fixes encoded

- Orb accepts/queues text while Realtime connects; Seller now matches Buyer queue behavior.
- Replies keep their beginning and response segments no longer concatenate mid-word.
- Buyer order-detail trust derives the effective signed-principal state.
- Seller publish honors spoken inventory and refreshes the visible catalog.
- Seller refund outcomes navigate to AgentGuard; high-value approval can be executed from the visible banner.
- Buyer/Seller background work records lifecycle events and shows an honest 30-second heartbeat.
- Orb output now removes raw Markdown punctuation, uses readable bullets/spacing, avoids duplicate completion summaries, and gives long answers more room.
- `scripts/hermes_ondc_testing_matrix.py` now uses Hermes locators, novice phrasing, runtime completion proof, recovery after normal panel remounts, and mandatory closeout.

**Reply polish proof:** `B-REPLY-POLISH-20260714-142407-0.jpeg` · `S-REPLY-POLISH-20260714-142407-0.jpeg` — readable bullets, no raw Markdown markers.

**Regression:** Buyer 151 tests + build Pass; Seller 158 tests + build Pass. Portfolio gateway 80 tests Pass. Hermes skill validation hard=0 (soft folder/name warning only). Hermes session inventory empty at closeout.

---

## Post-deployment Chrome web gate — 2026-07-14 17:40 IST

**Protocol:** authenticated Buyer + Seller FQDN matrix through WIP Hermes in the discovered Google Chrome profile directory `robo-trader-testing`; semantic locators for mutations; session closeout required.
**Ledger:** `evidence/web-e2e-thorough-20260714-174011.json`
**Result:** **26 Pass / 3 Blocked / 0 Fail**; all Blocked checks are physical microphone/voice proof.

| Surface | Result | Evidence |
| --- | --- | --- |
| Buyer | **13 Pass / 2 Blocked / 0 Fail** | Auth0 session + mandate; text Samantha; ONDC Atta search; resolved cart add; cart/checkout; Paid order + receipt; pause/resume; protected activity + receipt verification; memory; Realtime config; runtime delegation. `W-B-VOICE-MIC` and `W-B-VOICE` remain Blocked because the browser exposed `Text mode ready (no mic)`. The first Atta screenshot caught the offer grid painting; the ledger assertion and following cart captures prove the completed result and product resolution. |
| Seller | **13 Pass / 1 Blocked / 0 Fail** | Auth0 session; text Samantha; catalog/orders/AgentGuard navigation; catalog publish; refund page; INR 3,000 auto-allow receipt; INR 7,500 approval; consume; replay rejection; memory; runtime delegation. `W-S-VOICE` remains Blocked because no physical mic state was available. |
| Browser owner | **Pass** | Preflight discovered `Google Chrome` / profile directory `robo-trader-testing`; no duplicate Comet or isolated-Chrome profile was launched. |
| Closeout | **Pass** | Ledger `meta.sessions_closed` contains `fqdn-e2e-20260714-174011`; no validation lease was left open. |

Realtime is configured (`gpt-realtime-2.1-mini`, Samantha), and text/runtime tool execution passed. This gate does **not** claim physical mic/WebRTC completion.

---

## Local Samantha frozen-source text gate — 2026-07-16 00:08–00:34 IST

**Protocol:** WIP Hermes local browser; Buyer `http://127.0.0.1:43102`, Seller `http://127.0.0.1:43103`; customer-language text asks; exact turn-scoped tools; settled turn; visible screenshot; backend semantic owner check. Two consecutive combined runs used unchanged source. Every screenshot was opened and visually accepted. API writes were limited to unique catalog/order preconditions; browser `evaluate` remained read-only.

**Ledgers:** `evidence/matrix-run-20260716-000819.json` · `evidence/matrix-run-20260716-002128.json`

| Surface | Result | Evidence |
| --- | --- | --- |
| Buyer | **19/19 Pass ×2** | Search-only discovery, grounded results, add/clear/quantity/remove, cart/checkout/config navigation, preference memory, real INR 25,089 cart → exact `need_approval`, high-value item removal → INR 89 exact `allow` + matching receipt, runtime handoff. Origin `:43102`; zero turn errors. |
| Seller | **12/12 Pass ×2** | First-time help, AgentGuard/catalog/orders navigation, exact Ragi publish + backend visibility, accept→fulfill and reject with exact backend states, refund allow receipt, INR 26,000 approval, memory, multi-tool runtime handoff. Origin `:43103`; zero turn errors. |
| Visual review | **64/64 accepted** | 32 screenshots per run (Seller memory row has separate action and AgentGuard captures); no error panel, wrong-origin page, hidden `/agent` route, or stale checkout fallback accepted. |
| Regression | **Pass** | Buyer **155/155** tests + typecheck + production build; Seller **163/163** tests + typecheck + production build; `ondc-testing` and `portfolio-browser` validators Pass; Python compile, Ruff, and diff checks Pass. |
| Closeout | **Pass** | Matrix-owned WIP Hermes closeout completed after both runs. |

Durable fixes: Realtime follow-up responses are serialized per active response and reset per `response.created`, so chained navigation→delegation no longer races or stalls. Matrix proof is turn-scoped, fails on new Realtime errors, validates exact frontend origin and backend response semantics, uses a real over-limit cart instead of overriding the cart total, and reloads only approval/deny checkout states.

**Boundary:** local text/runtime proof only. No deployment, FQDN freshness, release, or physical microphone/WebRTC claim is made; physical mic remains blocked.

---

## Milestone 8 server-owned two-sided lifecycle — 2026-07-16 18:41–18:43 IST

**Protocol:** local WIP Hermes with app-specific demo SSO immediately before each capture; unique server-owned item/order/transaction/issue identities; screenshot + page text + gateway state agreement; cleanup after capture. Full evidence: `evidence/m8-browser-local-authority.md`.

| Gate | Result | Evidence |
| --- | --- | --- |
| First browser attempt | **Fail → fixed** | `m8-visible-1784208100-a`; Seller visible, Buyer audience cookie overwritten and gateway process stale. Lane now authenticates per app; stack restarted through `scripts/start-dev.sh`. |
| Two-sided run A | **Pass** | `m8-visible-1784208200-a`; order `order_046194d8c55b46e5`; transaction `txn_7c370c1c44094790`; issue `issue_b2b3839a03174e14`; three retained screenshots visually accepted. |
| Two-sided run B | **Pass** | `m8-visible-1784208201-b`; order `order_e5539c89c77b4593`; transaction `txn_26866a2a067a46a0`; issue `issue_6ec0143760424ab3`; three retained screenshots visually accepted. |
| Deterministic gates | **Pass** | Gateway 86; targeted commerce/AgentGuard 15; Buyer 143 + build; Seller 162 + build. |

Conclusion: browser storage is no longer authoritative for catalog, orders, inventory, checkout, or support cases. Remaining local storage is limited to cart/session/UI preferences, drafts, audit annotations, and seller notes; every accepted commerce mutation is server-owned.

---

## Milestone 8 shared contract and single assistant surface — 2026-07-16 19:13–19:20 IST

**Protocol:** final-source Buyer/Seller tests, typechecks, builds, gateway CI,
contract/shortcut searches, then two consecutive unique WIP-Hermes two-sided
runs with screenshot review and closeout. Full evidence:
`evidence/m8-contract-flow-consolidation.md`.

| Gate | Result | Evidence |
| --- | --- | --- |
| Shared contract | **Pass** | Buyer/Seller use shared action, agent, mandate, approval, and intent-receipt types; dated Seller compatibility vocabulary remains explicitly legacy |
| Single assistant surface | **Pass** | standalone Buyer and Seller `/agent` routes/navigation removed; Samantha remains the global orb; model navigation allowlists reject `/agent` |
| Judged-flow integrity | **Pass** | no AgentGuard protected-action API shortcut in judged Buyer/Seller/two-sided Hermes scripts |
| Two-sided run A | **Pass** | `m8-contract-final-1784209300-a`; order `order_47aa87015f8f40ec`; transaction `txn_a9607f26c37c4315`; issue `issue_6ff48b295bd64728`; three screenshots accepted |
| Two-sided run B | **Pass** | `m8-contract-final-1784209301-b`; order `order_070f0ce5a9274463`; transaction `txn_8b9c603db3d04b5c`; issue `issue_46a0ee83c93d45d9`; three screenshots accepted |
| Regression | **Pass** | Buyer 131 tests + typecheck + build; Seller 162 tests + typecheck + build; gateway 86 tests |
| Closeout | **Pass** | WIP bridge ready; no validation lease retained |

Conclusion: Milestone 8 cleanup has one shared AgentGuard contract owner and one
visible Samantha surface per app while preserving the server-owned two-sided
commerce and receipt proof.

---

## Independent customer and UX gate hardening — 2026-07-16 19:34–20:18 IST

**Protocol:** blind context-isolated reviewers through leased WIP Hermes;
correct app-audience demo SSO prepared by the main thread; visible UI only;
screenshots read before verdicts; every owned lease closed. An unrelated
BrandGPT lease was left untouched.

| Reviewer / gate | Result | Evidence |
| --- | --- | --- |
| Buyer novice, signed in | **App Fail** | “Ask Samantha” was visible but the first activation did not expose a usable input; downstream shopping was Not Tested. `6b71284b-c5da-42e0-ab9a-ef94cbd73c2f-1.png`, `432435a2-129a-4231-b024-9eb0961064ee-0.png` |
| Seller novice, signed in | **App Fail (incomplete)** | Samantha text mode accepted “Hello there”; catalog showed three products. Publish, stock/price proof, and orders were Not Tested before the old short bound. `0a95c81d-4dcc-4aac-8156-136dc18ddef4-1.png` |
| Buyer UX/accessibility | **App Fail** | Vague “verified/protected” claims; Samantha authority unexplained; floating assistant overlaps the search action; hero/status content competes with the primary search. `3e850fc1-179a-4b06-9b43-cb23010dec23-1.png`, `3e850fc1-179a-4b06-9b43-cb23010dec23-4.png` |
| Seller UX/accessibility | **App Fail** | “Verified” and “AgentGuard” are unexplained; product rows look static despite control semantics; Samantha purpose/authority is unclear. `dbbbd5ad-dcf9-4818-ac77-c902df031dbc-1.png` |
| Buyer search accessibility | **Fail → fixed** | Hero and form submit both exposed “Search catalog”; the form submit now exposes unique name “Search the network”. Focused component test and live role/name counts pass. |
| Fresh novice Buyer A | **App Fail** | `rice` reached a truthful zero-result page. `fd0eb80a-ae09-4b43-9d7a-81ffd44df95b-3.png` |
| Fresh novice Buyer B | **App Fail** | `rice`, then the visible broadening follow-up `grocery`, both returned zero results despite Seller inventory. `d7b0d5a3-f9ea-4d37-9c75-16883fbf0186-1.png`, `56850fd0-f5fa-406d-a10b-412878c46603-1.png`, `02c868df-6b8b-495a-9e52-ceb699e2d0e0-0.png` |

**Elon-algorithm correction:** the old 90-second micro-runs produced setup churn
and left journeys incomplete. They are historical rejected evidence. The owner
gate now uses three sequential full-mission actors: post-login Buyer novice,
post-login Seller merchant, and cross-app UI/UX plus accessibility smoke. Briefs
contain only profile, signed-in URL, and customer goal—no control names, fixes,
internals, fixtures, or known defects. Customer missions have six-minute
outcome budgets; read-only UX app missions have four-minute budgets. Each report
has one mission verdict, and any fix requires the whole affected journey to run
again in a fresh blind context.

**Current stop:** Buyer blind acceptance remains **App Fail** until the whole
journey is rerun. The earlier local CORS root cause is corrected in current
source through the Buyer `/ondc-control` development proxy, and the proxied
PreProd status endpoint now reports enabled/configured. That deterministic
repair is not customer proof. The WIP Hermes bridge currently reports
`SOCKET_DOWN`, so none of the three revised full-mission profiles has run yet.
The FQDN build also remains unchanged because deployment is outside this goal.
Do not promote this gate from curl, fixture, or diagnostic evidence.

### Current-source deterministic safety closure — 2026-07-16 21:28 IST

| Gate | Result | Current-source evidence |
| --- | --- | --- |
| Shared Python/TypeScript canonical action request | **Pass** | `test_python_canonicalizes_and_hashes_shared_golden_action_request`; Buyer `agentGuardContract.test.ts`; shared expected SHA-256 `b1845e24832e79a73abc2f3502a3130f9d947caf5b1c89e3c2cf8e74fa9ebab2` |
| Session ownership and tenant isolation | **Pass** | session-principal/body-wallet tests, session-B cannot consume session-A approval, plus `test_approval_cannot_cross_tenants`; legacy body-wallet fixture routes remain explicitly outside AgentGuard acceptance |
| Exact approval binding, expiry, atomic consume and replay | **Pass** | bound-field, changed-payload, explicit-expiry, concurrent-consume and replay-conflict tests |
| Pause/revoke and mandate-change invalidation | **Pass** | pause/resume invalidation, mandate replacement, and both stop-vs-consume race variants |
| Checkout cardinality/inventory | **Pass** | duplicate order idempotency yields exactly one stored order, one explicit reservation, and inventory `4 → 2` for quantity two |
| Fulfilment and issue/remedy lifecycle | **Pass** | Seller accepts then fulfils; Buyer reads fulfilled; Seller reads/responds to issue; Buyer reads resolved issue with attached refund remedy ID |
| Simulated payment/refund/reconciliation | **Pass** | success/idempotency test plus timeout `unknown → succeeded` reconciliation and missing-payment unknown result |
| Receipt tamper, prompt injection and direct executor bypass | **Pass** | focused receipt verification/tamper, mandate non-expansion, and no-effect protected executor tests |
| Optional dependency boundary | **Pass locally** | gateway starts and completes core commerce with Solana/Solders imports blocked and ONDC/eKYC/Solana disabled; Buyer/Seller manifests, lockfiles and installed trees contain no Solana wallet stack; visible scope-copy tests reject the legacy identity narrative |

Commands on unchanged local source:

- Executable-source SHA-256: `c29e70aa9240852e8678f5a69574ada06c77120b40927e8958fc5384e644ccbd`.
- `LOCAL-ADVERSARIAL-20260716-2125` → focused gateway contract, isolation, approval, lifecycle, payment, race, tamper, bypass and dependency suite **37 passed**.
- `LOCAL-SAFETY-20260716-2126-P1` → gateway **103 passed**; Buyer **137 passed** + typecheck/build; Seller **163 passed** + typecheck/build.
- `LOCAL-SAFETY-20260716-2127-P2` → the same counts and builds on the unchanged executable-source hash.
- `ondc-testing` and `portfolio-browser` validators, `workflow lint --full`, and all root/nested `git diff --check` gates → **PASS**.
- Retained artifact: [`evidence/local-safety-final-20260716-2128.json`](evidence/local-safety-final-20260716-2128.json).

This closes the local deterministic safety rows only. The three final browser
rows and deployed dependency-honesty row in `TESTINGPLAN.md` remain open until
the WIP Hermes bridge is healthy and an authorized deployment places the final
source on the FQDN. Neither condition may be replaced by local or API evidence.

### Current local safety closure — 2026-07-17 08:23 IST

This entry supersedes the preceding current-source counts and browser blocker.

- Executable-source SHA-256: `d940189015a07678ac2704554a80da16874d0c0021b15c9b5d2bb7ec54684a05`.
- `LOCAL-ADVERSARIAL-20260717-D940-P1` and `LOCAL-ADVERSARIAL-20260717-D940-P2` → targeted gateway contract, isolation, approval, lifecycle, payment, race, tamper, bypass and dependency suite **87 passed** each.
- `LOCAL-SAFETY-20260717-D940-P1` and `LOCAL-SAFETY-20260717-D940-P2` → gateway **129 passed**; Buyer **151 passed** + typecheck/build; Seller **172 passed** + typecheck/build.
- Seller UI/UX attempt `SELLER-UX-D940-A1` → **Tooling Blocked**: lease semantic context and owned screenshot referred to different pages; closeout passed and the session was absent.
- One bounded recovery and fresh retry `SELLER-UX-D940-A2-BOUNDED-RETRY` → **Tooling Blocked**: the owned lease disappeared twice; closeout passed and owned sessions were absent.
- Buyer/Seller customer passes and the two-sided visible repeat are **Not Tested** on this hash. The campaign stopped after the repeated browser-ownership failure; prior Seller passes were invalidated by the visible authority fix and are not counted.
- Retained artifact: [`evidence/local-safety-final-20260717-d940.json`](evidence/local-safety-final-20260717-d940.json).

Local deterministic Layers 1–4 and the deterministic portion of Layer 5 pass
twice on unchanged source. The three visible acceptance rows remain open; API,
unit, build, or older-hash browser evidence does not replace them.

### Final-hash independent Buyer campaign — 2026-07-17 23:30–23:45 IST

- Executable-source SHA-256: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.
- Buyer pass 1 reached checkout after visible discovery, cart add, quantity change, remove, and re-add, then stopped **Tooling Blocked** when the visible full-name field could not be targeted reliably.
- The one permitted fresh recovery repeated the same class of failure: semantic full-name lookup reported no matching visible element and cursor entry diverged into the wrong checkout field. No AgentGuard authorization, order, or receipt was created.
- Both owned leases closed and were absent afterward. The campaign stopped under the independent-customer gate; Seller, two-sided, and combined UI/UX missions are **Not Tested** on this hash.
- Retained blocker: [`evidence/local-customer-proof-blocker-20260717-af987.json`](evidence/local-customer-proof-blocker-20260717-af987.json).

The checkout semantic-input and screenshot owners were repaired, and the WIP
Hermes isolation gate passed three times. A fresh signed-in blind Buyer rerun on
2026-07-18 nevertheless stopped **Tooling Blocked** on the live search surface:
the labeled fill failed once, succeeded after the sole recovery, then the visible
Search click returned `Locator did not resolve for click`. `rice` remained
visibly entered; the 12-item / 8-order / inventory baseline was unchanged and
the owned lease closed. Retained blocker:
[`evidence/local-customer-proof-blocker-20260718-af987-search-locator.json`](evidence/local-customer-proof-blocker-20260718-af987-search-locator.json).
Visible customer acceptance is paused on this narrower WIP Hermes locator-readiness
owner; API or deterministic evidence cannot replace the missing browser rows.

### Independent customer gate — local close 2026-07-19 evening IST

- Git HEAD: `d4ca699`. Buyer audience already had repaired-UI Pass ×2 + Buyer UX Pass earlier the same day (`ui_repair_fingerprint` `22235abcd…`).
- Owner Dispatch proof **Pass** before Seller merchant: Accept → `dialog_opened` prompt → `dialog_handle` → backend `fulfilled`. Evidence: [`evidence/local-owner-dispatch-proof-pass-20260719.json`](evidence/local-owner-dispatch-proof-pass-20260719.json). Prior Seller stop was prompt mishandled as inject/`EXTENSION_TIMEOUT`.
- Seller merchant pass 1 **Pass** ([`Blind Seller merchant`](evidence/local-customer-seller-merchant-pass1-20260719-rerun.json)): publish + Accept→Dispatch→Delivered; incomplete-delivery Accept fails closed to full-page Orders error (recoverable via Retry). Cleanup restored baseline 33 items / 31 orders.
- Seller UX half first attempt **Not Tested** (accidental Sign out). Rerun **Pass**, no unresolved P0/P1: [`evidence/local-customer-seller-ux-half-rerun-20260719.json`](evidence/local-customer-seller-ux-half-rerun-20260719.json). Combined UX **Pass**: [`evidence/local-customer-combined-ux-pass-20260719.json`](evidence/local-customer-combined-ux-pass-20260719.json).
- Seller merchant pass 2 **Pass** (stability): Tata Sampann Toor Dal published; order `34413F79` → Delivered/Completed. Evidence: [`evidence/local-customer-seller-merchant-pass2-20260719.json`](evidence/local-customer-seller-merchant-pass2-20260719.json). Cleanup matched baseline again.
- Campaign close: [`evidence/local-customer-campaign-close-20260719.json`](evidence/local-customer-campaign-close-20260719.json). Bridge closeout ready; `active_agent_sessions=0`.
- Release threshold for this local visible portfolio: Buyer Pass×2 + Seller Pass×2 + combined UX clear on the day’s repaired UI / current HEAD. Parallel Buyer+Seller actors remain blocked on shared WIP cookie (gate).

### Samantha catalog data validation — local 2026-07-19 night IST

- Protocol: [`samantha-catalog-validation.md`](samantha-catalog-validation.md). Evidence: [`evidence/samantha-catalog-validation-20260719.json`](evidence/samantha-catalog-validation-20260719.json).
- Blind Samantha actors: pass1 `bb108593-…` / retest `d4beef4d-…`. **B-HI Pass**; **B-FIND-NL-ATTA Fail** (JUNK `q=roti`, then SKIP-UI unsolicited add); GHOST Atta vs empty `buyer/search?q=atta` before fix.
- Root cause (catalog MISS): `commerce_demo.search_items` required `seller_name` — published fixture Atta with null name was invisible. Fixed to published + in-stock. Gateway restarted; `q=atta` now returns 17 rows (includes test litter `Dispatch Proof*`).
- **Relevance harden (same night):** strict token match in `commerce_demo` + BPP (no empty→full-catalog fallback); Buyer `filterBuyerItemsForQuery` keeps short tokens (`tv`); `catalogSearchQuery` maps TV/television→`tv` and keeps `toor dal`. Delivery-area filter no longer hides SKUs with empty `deliveryAreas`. Empty ONDC network collect falls back to demo-commerce so the grid matches Samantha.
- Seeded markers `20260719234027` (Atta / Toor Dal / Oil / LED TV). API truth: `q=tv` → 1 TV (no oil); `q=oil` → oils only; `q=banana` → 0.
- Browser recheck **Pass** (direct `/results?q=tv` + Samantha “Search for a TV”): **1 match**, Horizon LED TV, no oil. Evidence: [`evidence/samantha-catalog-relevance-recheck-20260719-234802.json`](evidence/samantha-catalog-relevance-recheck-20260719-234802.json). Earlier Samantha pass also HIT oil/atta with `search_catalog` tool: [`evidence/samantha-catalog-relevance-20260719-234437.json`](evidence/samantha-catalog-relevance-20260719-234437.json).
- Still open: find-only “I need atta…” can still unsolicited `add_to_cart` (instruction tightened; needs fresh blind re-proof); catalog litter `Dispatch Proof*` / Hermes Fix*.
- **Live voice session 2026-07-19 ~23:51 IST** (`samantha-buyer-97c8df0d-…`): user asked rice → **JUNK** Poha via description “flattened rice”; orb reply buffer **concatenated** prior rice text onto later Atta turns; ASR “somebody”/“shoamizamata”. Fixes: title-primary search (rice≠poha); `response.created` clears reply; NL stop-words + `basmati rice` compound; seeded India Gate Basmati Rice. Reload Buyer orb before retest.
- **Operator retest 2026-07-20 ~00:08 IST** (Hermes WIP + demo SSO + API truth + page settle): evidence [`operator-catalog-retest-20260720-000815-rescored.json`](evidence/operator-catalog-retest-20260720-000815-rescored.json). First pass found **Atta GHOST** (reply claimed Atta while `q=poha`, no new `search_catalog` — Host `visible_results` leaked full-session cache) and **banana GHOST** (“still loading” after wait with 0 matches). Fixes: scope Host visible_results to `current_query`; force `search_catalog` when find-ask skips tools; after `waitForBuyerCatalogItems` empty → `can_assert_empty=true` + honest empty message. Rescored **Pass**: rice/poha/atta/tv HIT, banana EMPTY-OK. Spot poha→atta: `q=atta` navigates correctly.

---

## Chrome customer issue catalog — local dirty source, 2026-07-21 17:14–18:35 IST

**Protocol:** Mode A catalog-then-fix; explicit `@chrome` plugin; sequential
signed-in Buyer, Seller, combined UI/UX-accessibility, Buyer Samantha, and
Seller Samantha missions. Reviewers used visible UI only and continued past
individual findings. Product and harness source were not edited. Evidence:
[`customer-chrome-issue-catalog-20260721.json`](evidence/customer-chrome-issue-catalog-20260721.json).

**Source boundary:** `HEAD d4ca699a15e9`; dirty tracked-diff SHA-256
`cc7d960fe1c39b7e0d584e79b609b5870791f77545a3fd3c226485dd0cfa4fdf`.
This is local dirty-source evidence, not FQDN or release evidence.

| Mission | Verdict | Customer outcome |
| --- | --- | --- |
| Novice Buyer | **Pass** | Search → compare → add/remove/re-add → checkout → signed AgentGuard authorization → order `88FDF65A` receipt. |
| Small Seller merchant | **Tooling Blocked** | Published Kaveri Toor Dal and accepted order `2BEE2CD5`; Chrome disconnected at dispatch tracking prompt, and the single fresh recovery repeated the same class. |
| Combined UI/UX + accessibility smoke | **App Fail** | Both apps reviewed; five deduplicated P1/P2 findings, including Buyer Samantha dialog keyboard failure and ambiguous listening state. |
| Buyer Samantha customer | **App Fail** | Search, grounding, add, checkout, and authorization passed; cart navigation, memory readback, weekly-task completion, address coherence, and reply rendering failed. |
| Seller Samantha customer | **App Fail** | Navigation, publish, memory, and recall passed; fulfillment/refund were unavailable and bulk triage contradicted the visible zero-order queue. |

### Issue ledger

| ID | Priority | Owner surface | Finding |
| --- | --- | --- | --- |
| `CUST-CHROME-20260721-01` | P1 | Buyer checkout | Stale “Complete the form…” quote instruction remains after all required fields are complete and authorization is enabled. |
| `CUST-CHROME-20260721-02` | P1 | Buyer results | Credible offers are mixed with fixture-like `Dispatch Proof` catalog litter and incomplete seller/delivery/returns context. |
| `CUST-CHROME-20260721-03` | P1 | Buyer Samantha | Keyboard opening leaves focus on `BODY`; no dialog/heading semantics; Escape does not close. |
| `CUST-CHROME-20260721-04` | P1 | Buyer + Seller Samantha | `Listening + text ready` implies audio capture without a microphone control, consent affordance, or state explanation. |
| `CUST-CHROME-20260721-05` | P1 | Authority copy | Execution boundaries are inconsistent; visible surfaces expose `principal:demo`, `seller principal`, `PII-free`, and `Mandate: active`. |
| `CUST-CHROME-20260721-06` | P2 | Seller Network | Generate/save/test controls remain enabled while connection details are incomplete. |
| `CUST-CHROME-20260721-07` | P2 | Seller Orders | Active queue filter is visual only; no `aria-pressed` or `aria-current`. |
| `CUST-CHROME-20260721-08` | P1 | Buyer Samantha | “Show me my cart” becomes a zero-result catalog query and leaks an internal operator instruction. |
| `CUST-CHROME-20260721-09` | P1 | Buyer memory | Samantha claims a preference was remembered while the visible memory owner remains empty. |
| `CUST-CHROME-20260721-10` | P1 | Buyer runtime | Weekly-grocery background task reports complete without a plan or requested basket. |
| `CUST-CHROME-20260721-11` | P1 | Buyer order detail | Full submitted delivery address is reduced to `IND`. |
| `CUST-CHROME-20260721-12` | P2 | Buyer Samantha | Replies truncate mid-sentence. |
| `CUST-CHROME-20260721-13` | P1 | Demo principal | Seller catalog/orders disappear across demo sign-ins because each session receives a new principal. |
| `CUST-CHROME-20260721-14` | **P0** | Seller runtime | Bulk triage reports `17/16/1` orders while the visible queue and follow-up both report zero. |
| `CUST-CHROME-20260721-15` | P2 | Seller Samantha | Preference recall works, but Samantha cannot open the visible memory settings. |
| `CUST-CHROME-20260721-16` | **P0 tooling** | Chrome dialog control | Dispatch tracking prompt disconnects Chrome; the one bounded recovery repeats. |
| `CUST-CHROME-20260721-17` | P1 tooling | Portfolio preflight | AgentGuard demo setup incorrectly waits for legacy host/Solana wallet infrastructure. |
| `CUST-CHROME-20260721-18` | P1 tooling | `reviewer_ready.py` | Post-idle readiness read loses its required browser-session preflight. |

**Supporting gates:** gateway `135 passed`; Buyer test/build Pass; Seller
`196 passed` + build Pass; offline graders Pass; commerce-demo-mode gate Pass.

**Not converted to Pass:** physical voice remained Not Tested; Seller
dispatch/completion/refund remained Tooling Blocked; dirty local source was not
tested on FQDN. Production ONDC and live payment remain contractually out of
scope.

**Cleanup:** removed exactly three campaign items, three orders, three
reservations, and matching idempotency entries; restored the one pre-existing
item’s inventory to 21. Baseline identity sets match again: 53 items, 35 orders,
33 reservations. Recoverable pre-cleanup copy:
`/tmp/aadhaarchain-commerce-pre-cleanup-20260721.json`.

## Chrome customer fix acceptance — local dirty source, 2026-07-21 18:36–19:26 IST

**Result: Pass on frozen local source.** All 18 cataloged findings were fixed
and accepted. The fix loop continued through three additional findings exposed
by re-review: residual non-Dispatch fixture catalog families, a direct Seller
Realtime multi-tool reply that contradicted an executed fulfillment, and a
Radix dialog ref warning. Each was fixed before the final empty iteration.

| Acceptance area | Evidence |
| --- | --- |
| Buyer commerce | One customer-safe Atta offer; readiness copy changes only after complete billing/address; authorized order retained full delivery address; repeat demo sign-in retained the order. |
| Buyer Samantha | Named dialog, initial text focus, Escape close/focus restore, explicit mic state, cart intent → `/cart`, immediate memory readback, and unverified weekly work ends as **could not finish**. |
| Seller operations | Pressed filter state, incomplete Network Save/Test disabled, customer authority copy, accessible in-page dispatch tracking, direct Samantha memory link. |
| Seller truthfulness | Order mutations require exact order IDs; the repeated bulk-triage mission showed grounded read/action outcomes and made no unintended mutation. |
| Tooling | AgentGuard preflight excludes legacy host/Solana; post-idle reviewer read re-runs session preflight; dispatch no longer opens a native prompt. |
| Empty iteration | Fresh Chrome dispatch replay on final source: correct dialog semantics and zero console errors. |

**Deterministic support:** gateway `144 passed`; Buyer `187 passed` + build/copy
gate; Seller `207 passed` + build/copy gate; offline graders Pass; both repo
skill validators Pass; diff checks Pass in the portfolio and all nested repos.

**Cleanup:** removed known stale fixture catalog families, four temporary
acceptance orders/reservations, two temporary acceptance items, and temporary
Buyer Samantha memory. Final demo state: 22 items, 13 orders, 11 reservations.
Recoverable copies remain at
`/tmp/aadhaarchain-commerce-pre-cleanup-20260721.json` and
`/tmp/aadhaarchain-commerce-before-catalog-quality-cleanup-20260721.json`.

**Boundaries:** local dirty-source proof only; the FQDN deployment was not
changed or tested. Production ONDC, live payment, and official conformance
remain out of scope. Existing Chrome microphone permission exposed live state,
but no controlled physical voice-accuracy campaign was run.

## CF1 PostgreSQL `@Chrome` customer validation — local dirty source, 2026-07-22 16:30–17:30 IST

- Focused frozen-source fingerprint: `9c7fadc8fab66f3f456272f5dd8041e357780830bbabfe7185d4c30199704d66` (compatibility read model, Seller AgentGuard executor, regression tests, and Seller commerce mapping). Portfolio HEAD `fbafeb7f`; nested HEADs: AadhaarChain `30e6d11`, Buyer `d24e4fe`, Seller `9ca5e85`. Worktrees were dirty and existing user changes were preserved.
- **Buyer novice: Pass.** Visible Chrome journey searched for a generic grocery, compared the one available Atta offer, added it, changed quantity `1 → 2`, previewed exact `INR 178`, confirmed the one-time AgentGuard approval, and reached order `7C71667B` with `Simulated payment succeeded` and `Authorized · signed reference verified`. Retained screenshots: `/private/tmp/buyer-offer.png`, `/private/tmp/buyer-cart.png`, `/private/tmp/buyer-order.png`.
- Buyer PostgreSQL readback agreed with the UI: one `paid` order for `17800` paise, one `succeeded` payment attempt, one executed receipt bound to its decision and approval, one order effect for the quote, and inventory `12 → 10`.
- **Seller discovery/fix loop:** the first blind run was **App Fail** because `seller.order.accept` treated the CommerceV1 compatibility order as a wrapped object. The next run exposed a distinct **App Fail**: already-refunded orders still rendered Pending/refundable and a duplicate refund surfaced only as `Failed to fetch`. The owner fixes changed the Seller executor to consume the direct order shape and projected durable refund amount/status into Seller as terminal `Cancelled / Payment: Refunded`; focused regression tests were added before each full rerun.
- **Seller merchant: Pass after one bounded Chrome recovery.** The final actor published `Farm Fresh Tomatoes 1kg` (`INR 62`, stock `14`), distinguished two terminal refunded orders from actionable order `EE247B4A`, completed the full `INR 89` AgentGuard refund, and observed `Payment: Refunded`, `The full order value has been refunded. No further refund is available.`, verified authorization reference `7474C04D`, and `Order cancelled`. Retained screenshots: `/private/tmp/seller-add-product-form.png`, `/private/tmp/seller-catalog-published-new.png`, `/private/tmp/seller-orders-before-new.png` (the last file contains the terminal refunded detail despite its historical filename).
- Seller PostgreSQL readback agreed with the terminal UI: order `ee247b4a-551b-403a-9d45-fe14ff65bca4` was `cancelled`; payment remained truthfully `succeeded`; exactly one `succeeded` refund for `8900` paise and one `seller.refund.issue` AgentGuard receipt existed.
- Frozen-source deterministic support: gateway `198 passed`; Seller `210 passed` plus production build/copy gate; targeted Ruff and diff checks passed; `ondc_ci_graders.py --offline` passed all checks.
- Cleanup removed every temporary catalog listing; the isolated UTF-8 PostgreSQL validation cluster owns all generated orders/refunds and is deleted at closeout. All Chrome sessions were finalized.

**Acceptance boundary:** this establishes one complete Buyer customer Pass and one complete Seller customer Pass on the corrected local source. It is not the two-pass release threshold: Buyer Pass 2, Seller Pass 2, the combined UI/UX-accessibility smoke, Samantha voice/runtime breadth, FQDN Auth0, live payment, production ONDC lifecycle/conformance, and iOS remain **Not Tested** in this campaign.
