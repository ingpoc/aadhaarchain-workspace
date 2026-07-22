# Validation ledger

Track **manual** runs before simplifying or automating. Update after each full-path iteration.

Phase order: make it work → **validate (this file)** → simplify → optimize → automate.

**Lane status:** Portfolio API + browser (burner) + first-run setup + identity onboarding + on-chain lanes validated historically. **AgentGuard seller Hermes** pass 2026-07-11 evening (WIP bridge recovered). **AgentGuard buyer Hermes** first judged pass 2026-07-11 evening; re-pass 15:54Z. **Buyer `/config` + Samantha** operator path 1× pass 15:55Z; **full Buyer journey** re-pass 16:10Z (UI search apples + tool cart + AG + orb; live mic env-dependent). **Buyer Samantha operator-long** 11/11 + cart/memory re-pass 2026-07-11 night. **Seller Samantha ops** (`hermes_samantha_seller_ops.py`) 5/5 + memory on `/agentguard` same night. **Two-sided** consecutive unique run_ids pass. FlatWatch AgentGuard remains **deferred**.

## Milestone 0 baseline (IMPLEMENTATIONPLAN)

| Command | Result | When |
| --- | --- | --- |
| `aadharchain/gateway`: `.venv/bin/python -m pytest tests/ -q` | exit 0; **56** passed | 2026-07-11 |
| `ondcbuyer`: `npm test` + `npm run build` | 117 passed; build OK | 2026-07-11 |
| `ondcseller`: `npm test` + `npm run build` | 150 passed; build OK | 2026-07-11 |
| `agentguard seller --fixture` | **2 pass** (2026-07-11) + **2 pass** night | same; demo principal UI path |

Known old seller `tsc` errors are resolved in this workspace. `refundedAmount` compiled as numeric in the installed shared order type; nested `refund.amount` remains a price object.



## Milestone 8 cleanup (validated 2026-07-11T14:51Z)

| Change | Result |
| --- | --- |
| Delete dead `agentCommerceState.ts`, `sellerBackendEnforcement*` | Done |
| Seller Hermes approve/replay/pause/deny via UI (no consume API in judged path) | **Pass** — compressed ≤20 Hermes actions (`MAX_ACTIONS=20` silent truncate was the abort) |
| Unique `run_id` for `two-sided` / `hermes_two_sided_commerce.py` | Done (auto in `portfolio_browser.py two-sided`) |
| Fixture resumes paused agent before judged path | Done (`FIXTURE_JS` wallet re-read + resume) |
| Remaining | Buyer Hermes still API-gated for consume/replay/pause; local* commerce fixtures still authoritative fallbacks |

| Gate | Result |
| --- | --- |
| Gateway pytest | **56 passed** (2026-07-11T14:48Z) |
| `agentguard seller --fixture` UI path | **Pass** checks all true (incl. `ui_clicks_ok`); consecutive skip-sso + `portfolio_browser` SSO→Hermes |
| `agentguard buyer --fixture` | **Pass** all checks true (API-gated judged path) |
| Two-sided unique runs | **2 pass** `ag-1783781283-36e172`, `ag-1783781283-db290e` |
| Seller UI sample (judged) | allow `rcpt_7a2140b63d3846db` → approve `rcpt_bd3a041283194f80` → msg `Approval already consumed (replay rejected).` → status `paused` → deny `Agent is paused.` |


## Portfolio API lane

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| `start-dev.sh` | `setup.sh` done once | All :43100–43105 URLs 2xx | 2 pass | Fixed: wait all portfolio URLs; FlatWatch `/api/health` |
| `pytest tests/` | gateway `.venv` | 43 passed | 2 pass | — |

**Validated bookend (2026-07-06):** `./scripts/verify-portfolio.sh` (default, no `--browser`) — two consecutive exit 0; 43 passed each.

**Hardening (phase 3–4, 2026-07-06):**
- `./scripts/verify-portfolio.sh` promoted as canonical API-only entry (gateway health → auto `start-dev.sh` if down)

**Required:** gateway + ONDC frontends for SSO/browser. FlatWatch required for full stack start only.

**Inefficient (fixed after manual):** single-shot HTTP curl in preflight; start-dev only waited on gateway.

**Not yet manually verified:** full on-chain create → verify → bitmap E2E.

## Portfolio browser lane

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| preflight | stack up, Chrome same Space, Hermes | exit 0, `tier: hermes` | 2 pass | Chain with `start-dev.sh`; HTTP retries 30s |
| smoke | preflight green | JSON `"success": true` | 2 pass | Asserts ONDC titles |
| sso burner | `NEXT_PUBLIC_DEV_BURNER_WALLET=true` | Sign out visible | 2 pass | Validator :8899 must be up for RPC |
| closeout | after browser work | bridge `ready=True` | 2 pass | — |

**Validated bookend (2026-07-06):** `python3 scripts/portfolio_browser.py lane burner seller` — two consecutive exit 0.

**Hardening (phase 3–4, 2026-07-06):**
- `lane` subcommand — single preflight for smoke + SSO + closeout
- Preflight auto-starts `start-dev.sh` when stack down
- Preflight checks validator `:8899` when burner enabled
- `verify-portfolio.sh --browser` promoted to canonical wrapper

## Solana on-chain lane

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| validator | Solana CLI; port `:8899` free or already healthy | `solana cluster-version --url localhost` prints version (e.g. `2.1.5`) | 2 pass | `start-validator.sh` uses `aadharsolana/.local-validator` |
| anchor validate | validator up; **fresh ledger** (see below); `anchor keys sync` | `validate-onchain.sh` exit 0; **58 passing** (~49–54s tests) | **2 pass** (fresh ledger each) | Stale re-run without reset: 41 pass / 17 fail (~129–135s). Fresh passes: ~139–144s wall (2026-07-06 night agent) |
| init config | deploy-only on fresh ledger; `ORACLE_PRIVATE_KEY` (env or `.env`); deploy wallet funded | script prints `Initialized config at …` | **2 pass** | `skip_preflight=True` validate-phase fix for localnet `BlockhashNotFound` (~1s, 2026-07-06 night) |
| gateway bridge | init config done; IDL synced; identity on-chain | `submit_approved_verification` returns tx signature; metadata `chain_transaction_signature` set | **2 pass** | API smoke: airdrop → create → fixture → approve (~2s/run, 2026-07-06 night) |

**Fresh ledger (required when anchor tests fail with stale state):**

```bash
# Fresh ledger for on-chain tests only (mutex — not for portfolio browser)
kill $(lsof -ti:8899) 2>/dev/null
aadharsolana/scripts/start-validator.sh --reset   # background; Agave 2.2 has no admin.rpc
aadharsolana/scripts/validate-onchain.sh
```

Pass signals for stale ledger: `account … already in use` on `initialize`; `ConstraintHasOne` admin mismatch (Left/Right pubkeys differ); assertion drift (e.g. `schemaCount` 9 vs 1); late `ECONNREFUSED :8899` if validator dies under bad state.

**Root cause (2026-07-06 evening):** persistent `aadharsolana/.local-validator` retained config PDAs from prior runs. Anchor integration tests generate **ephemeral** admin/oracle keypairs each run but reuse deterministic PDAs (`[b"config"]`). Re-running tests without resetting the ledger leaves on-chain admin ≠ test signer → `ConstraintHasOne` and related failures. Example from failed run: on-chain admin `FKpwbJHDUcqewNRiYSK6aDsCTHfcePUfSRNULzenHud7` vs test signer `DrW1yhspaGGyfQcenmLr41Q1cvfUji6Fmsv1RBb7gB1n`. Program IDs in `Anchor.toml` matched deploy keypairs after `anchor keys sync`; not a keys-sync issue.

**Fix:** `kill $(lsof -ti:8899)` → `aadharsolana/scripts/start-validator.sh --reset` → `validate-onchain.sh`. Fresh run: **58 passing**, exit 0 (~139s wall including build/deploy).

**Parallel-agent hazard (2026-07-06 night):** Multiple subagents resetting/restarting `:8899` concurrently caused partial deploys (`account data too small`, `invalid account data`) and validator death. **Treat validator + ledger as mutex** — one on-chain agent at a time, exclusive fresh-ledger reset before validate.

**Validated anchor bookend (2/2):** evening pass + exclusive night pass (58/58 each, ~148s wall on pass 2).
**Validate session (2026-07-06 night agent):**
- Run 0 (stale ledger, no reset): **fail** — 41 pass / 17 fail, ~135s, `ConstraintHasOne` on verification-oracle config.
- Run 1 (fresh ledger): **pass** — 58/58, exit 0, ~144s wall.
- Run 2 (consecutive, polluted ledger, validator restarted): **fail** — 41/17, ~129s (confirms stale-ledger precondition).
- Run 3 (fresh ledger): **pass** — 58/58, exit 0, ~139s wall.
- **Precondition:** reset `aadharsolana/.local-validator` before each full `validate-onchain.sh`; back-to-back validate without reset is expected to fail.

**Gateway E2E attempt (deploy-only path, same night):**
- `anchor keys sync && anchor build && anchor deploy` (no test): **pass** (~40–43s) when validator exclusive.
- IDL copy to gateway: done during attempts.
- `init_identity_registry_config.py`: **fail** — `RPCException` preflight `BlockhashNotFound` (observed with validator process alive). Validate-phase patch: `_coerce_blockhash` + `last_valid_block_height` on confirm (still failing preflight).
- **Infra:** parallel agents `pkill -f solana-test-validator` / ledger reset → `ECONNREFUSED :8899` mid-lane; treat `:8899` as mutex.


**Gateway E2E order (not yet manually run):** fresh ledger → `anchor build && anchor deploy` (no tests) → set `ORACLE_PRIVATE_KEY` + `SOLANA_ON_CHAIN_ENABLED=true` in gateway `.env` → `init_identity_registry_config.py` → approve verification via gateway. Running `validate-onchain.sh` first initializes identity-registry config with **test** oracle; `init_identity_registry_config.py` then no-ops (`Config already initialized`) — gateway oracle will not match.

**Blockers (init config + gateway bridge):**
- **Mutex:** only one agent may own `:8899` + ledger reset (parallel pkill/deploy caused validator death and partial deploy errors).
- Init config: `BlockhashNotFound` on `send_transaction` preflight — debug with exclusive validator (`solana transfer` sanity, then `send_raw_transaction` + `skip_preflight` if needed).
- `ORACLE_PRIVATE_KEY` unset in `aadharchain/gateway/.env` — export at runtime from deploy wallet or set locally (do not commit).
- Programmatic bridge smoke (create identity + `submit_approved_verification`) blocked until init succeeds.
- Full HTTP E2E: restart gateway with `SOLANA_ON_CHAIN_ENABLED=true` + oracle key → wallet-signed create on `:43100` → verify/approve → metadata `chain_transaction_signature`.

**Next manual steps (init config + gateway bridge):**
1. Reset ledger again (same fresh-ledger block above).
2. `cd aadharsolana && anchor keys sync && anchor build && anchor deploy` — **do not** run `anchor test`.
3. Copy IDL: `cp aadharsolana/target/idl/identity_registry.json aadharchain/gateway/idl/`.
4. Gateway `.env`: `SOLANA_ON_CHAIN_ENABLED=true`, `SOLANA_RPC_URL=http://127.0.0.1:8899`, `ORACLE_PRIVATE_KEY=<base58>` (key must match funded deploy wallet or separate oracle key registered in config).
5. `cd aadharchain/gateway && .venv/bin/python scripts/init_identity_registry_config.py` — expect `Initialized config at …` (not “already initialized”).
6. Restart gateway; create identity (wallet signs) → verify aadhaar → approve path → confirm on-chain tx signature in verification metadata / bitmap.

**Do not automate wrapper** (`verify-solana.sh`) until init config + one approve path manually confirmed on-chain.

## UX simplification lanes (2026-07-06)

Source of truth: `.cursor/design/ux-validation-ledger.json` (26 mockups, 25 page entries).

| Lane | Scope | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| AadhaarChain UX | `ac-*` ids; routes `/`, `/home`, `/verify`, `/login`, `/apps`, `/activity`, `/settings` | All routes HTTP 200; `/dashboard` → `/home`; `/verify/pan` → `/home`; nav 4 items; builds pass | 2 pass (routes) | Home state variants + verify wizard Hermes: **1 pass** |
| Buyer UX | `buy-*` ids; `/` → `/search`; Agent secondary footer | No buyer proof card; `useSubject` prefers SSO wallet; smoke `signed_in` + Sign out | 2 pass (routes + smoke) | Full checkout E2E: **1 pass** (trust wallet fix landed) |
| Seller UX | `sell-*` ids; `/` → `/dashboard`; Agent secondary footer | No seller proof card on dashboard; smoke seller dashboard | 2 pass (routes + smoke) | Catalog publish Hermes: **1 pass** |
| Portfolio regression | `lane burner seller` + `smoke` | Buyer `:43102/search`; seller `:43103/dashboard`; SSO session visible | 2 pass smoke | Full `lane` SSO URL wait timeout once; final URL + Sign out OK |

**Validated bookend (2026-07-06 night):** Two consecutive HTTP passes on all canonical routes; `portfolio_browser.py smoke` ×2 success; gateway pytest 43 passed; buyer/seller builds green; AadhaarChain frontend build green.

**UI polish (2026-07-07):** Page title → AadhaarChain; home duplicate CTA removed; Localnet hidden on home wallet card; redirects moved to `next.config.ts` (production build green); login layout metadata; dev server restart required after config changes.

**Redirects confirmed:** `GET /dashboard` → `/home`; `GET /verify/pan` → `/home`; buyer `/` serves SPA (client `Navigate` → `/search`); seller `/` → `/dashboard` (client).

**Removed in v1:** GSAP landing; PAN route; buyer/seller proof cards; orphan `LoginPage.tsx`; primary nav Agent/usecase (footer secondary).

## Identity onboarding lane

Full path: `:43100/verify` (wizard: anchor → upload → status) → trust fixture → post-login on ONDC app.

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| verify wizard | Stack up (`:43100`, `:43101`); burner via wallet modal; Hermes session `identity-onboarding`; `form.requestSubmit()` | `gateway-state.json` new identity; redirect `/home` | 1 pass | Route merged from `/identity/create` + `/verify/aadhaar` |
| trust fixture | Wallet known; gateway dev route enabled | `POST …/dev/fixtures/{wallet}` → `trust_state: verified`; `high_trust_eligible: true` | 2 pass | Fixture create wallet + session wallet after SSO |
| post-login | SSO **Sign in and continue** (same Hermes session); `:43103` | `auth/me` signed in; `GET …/trust` → `verified`; **Sign out** on seller | 2 pass | ~16s; API pass; UI chip still **No identity** (blocker) |

**Validated bookend (2026-07-06 evening):** Two consecutive Hermes runs (~52s each); API trust verified + Sign out.

**Preconditions:** Stack up; Hermes `ready: true`; `NEXT_PUBLIC_DEV_BURNER_WALLET=true`; session `identity-onboarding`; omit `close_tab` (causes `about:blank#blocked`).

**Pass signals (runs 6–7):** create → new pubkey in `gateway-state.json`; verify → `Manual review required`; fixture → `trust_state: "verified"`; post-login → browser `fetch` `auth/me` + `…/trust` both `verified`, **Sign out** visible.

**Root causes fixed in phase 1:** use `form.requestSubmit()` for create; `evaluate`+`DataTransfer` for file upload; open burner via `click_selector` on `wallet-adapter-button`; single Hermes session (no `close_tab`).

**Blockers (open):** (1) `UnsafeBurnerWalletAdapter` ephemeral keypair — create wallet ≠ SSO session wallet; workaround: fixture session wallet after sign-in. (2) ~~Seller `useTrustState(walletAddress)` uses wallet adapter pubkey~~ **fixed 2026-07-06** — `useSubject` prefers `auth/me` wallet. (3) Stub PDF verify stops at `manual_review`; fixture required for verified trust.

**Parallel with other lanes?** No — shares Hermes/Chrome with browser lanes (mutex). API fixture step is serial per wallet after create/verify.

**Hermes / Chrome?** Yes — create, verify, and post-login UI.

**Validator `:8899`?** No — identity state is file-backed unless `SOLANA_ON_CHAIN_ENABLED` (out of scope for this lane).

**Blocks:** Elevated commerce (needs verified trust). **Blocked by:** First-run setup + `start-dev.sh`.

## Solflare SSO lane

Command: `python3 scripts/portfolio_browser.py sso solflare [seller|buyer]` (preflight → SSO → optional closeout).

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| preflight | Stack up; Solflare extension; Hermes + Chrome same Space | exit 0, `tier: hermes` | pending | Same bookend as burner lane |
| sso solflare seller | Preflight green; `VITE_IDENTITY_AUTH_ENABLED=true` in `ondcseller/.env.local` | JSON `"signed_in": true`; **Sign out** on `:43103/dashboard` | pending | Solflare `signMessage` + approve popup |
| sso solflare buyer | Preflight green; `VITE_IDENTITY_AUTH_ENABLED=true` in `ondcbuyer/.env.local` | JSON `"signed_in": true`; **Sign out** on `:43102/search` | pending | Run seller then buyer or vice versa in one session |
| closeout | After SSO work | bridge `ready=True` | pending | Closes `solflare-sso` Hermes session |

**Parallel with other lanes?** No — Hermes mutex with identity onboarding, elevated commerce, and burner `lane`.

**Hermes / Chrome?** Yes — required (`solflare_sso.py`, extension popup).

**Validator `:8899`?** No — unlike burner SSO.

**Blocks:** Post-login checks that assume Solflare wallet (not dev burner).

## First-run setup lane

Path: `./scripts/setup.sh` → `./scripts/start-dev.sh` (once per clone or after dep drift).

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| setup.sh | Clean or stale clone; `PYTHON_BIN` valid; network for `pip`/`npm` | Exit 0; `.venv` in gateway + FlatWatch backend; `node_modules` in frontends | 2 pass | Idempotent; ~42s first / ~17s re-run (2026-07-06) |
| start-dev.sh | `setup.sh` done at least once | All `:43100`–`:43105` URLs 2xx (FlatWatch `/api/health`) | 2 pass | Validate: **verify-only** when stack already healthy — do not restart; also Portfolio API lane |

**Validated bookend (2026-07-06):** `./scripts/setup.sh` → stack pass signals on `:43100`–`:43105` (run `./scripts/start-dev.sh` only when URLs not all 2xx). Two consecutive full iterations, exit 0.

**Hardening (phase 3–4, 2026-07-06):**
- Canonical bootstrap: `setup.sh` then conditional `start-dev.sh` (healthy stack = curl bookend only)
- Pass signals: gateway + FlatWatch `.venv`; four frontend `node_modules` dirs

**Parallel with other lanes?** Yes **after** `setup.sh` completes — `start-dev.sh` can overlap with API-only `pytest`. Do **not** parallel two `start-dev.sh` invocations.

**Hermes / Chrome?** No.

**Validator `:8899`?** No.

**Blocks:** All browser and API lanes that need the portfolio stack.

**Validated bookend (2026-07-06 night):** `./scripts/setup.sh` ×2 exit 0 → verify portfolio URLs ×2 (stack already up).

## Elevated commerce lane

Verified trust + SSO cookie + purpose-bound identity proof (not SSO alone). Demo mode: `VITE_COMMERCE_DEMO_MODE=true`.

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| buyer checkout action | Verified trust via `useSubject` SSO wallet | Cart → checkout completes in demo mode without proof card | **2 pass** (2026-07-10) | `FILL_DELIVERY_JS` (not `fill_selector`); lands `/orders/demo-…` |
| seller catalog proof | — | — | removed | Dashboard proof card removed in UX v1 |
| seller catalog publish | Signed in on `:43103`; verified trust | Create/edit catalog item on `/catalog/new` succeeds in demo mode | **2 pass** (2026-07-10) | `--fixture` + burner SSO; final `/catalog` |

**Parallel with other lanes?** No — Hermes mutex. Buyer and seller sub-steps are sequential in one browser session (shared gateway cookie domain).

**Hermes / Chrome?** Yes — proof signing uses wallet `signMessage` in app UI.

**Validator `:8899`?** No.

**Blocked by:** Identity onboarding (or fixture) for verified trust; SSO lane (burner or Solflare) for session.

## AgentGuard seller lane

ONDC Seller AgentGuard vertical slice (PRODUCTIDEA / `ondcseller/GOAL.md`): policy ≤ INR 5k → refund 3k allow → 7.5k need approval → approve once → replay reject → pause → deny.

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| `agentguard seller --fixture` | Stack up; WIP Hermes; gateway AgentGuard routes | JSON `"success": true`; checks policy/need/replay/paused/deny | **2+2 pass** (day + night demo principal) | `python3 scripts/portfolio_browser.py agentguard seller --fixture` (demo SSO then Hermes) |
| Gateway pytest | gateway `.venv` | `tests/test_agentguard.py` pass | API | Does not replace Hermes lane |

**Validated bookend (2026-07-11):** two consecutive `AGENTGUARD_SKIP_SSO=1` Hermes script passes after burner SSO — UI refunds + UI approve/replay/pause/deny (M8; Hermes `MAX_ACTIONS=20`).

**Re-validated (2026-07-11T14:51Z):** `portfolio_browser.py agentguard seller --fixture` → all checks true (UI judged path).

**Re-validated (2026-07-11 night, demo principal):** two consecutive `portfolio_browser.py agentguard seller --fixture` → all checks true (`policy_5000`, allow, need approval, replay rejected, paused, deny while paused, `ui_clicks_ok`). Fix: order refund UI + Hermes fixture use cookie `principal_id` (not wallet).

2026-07-11 API proof after client/shared-commerce wiring: Seller refund INR 3,000 allowed; INR 7,500 required approval; consume 200; replay 409; pause 200; next refund denied with `Agent is paused.` Receipt `rcpt_ce7d8c1de73643ab`. Same-day Hermes rerun was blocked by WIP bridge/session readiness, not by the AgentGuard API checks.

**Parallel with other lanes?** No — Hermes mutex with `lane` / SSO / commerce / onboarding.

**Hermes / Chrome?** Yes.

**Validator `:8899`?** No.

**Blocked by:** Demo principal SSO (`sso demo seller`); stack + WIP Hermes.

## AgentGuard buyer lane

**Validated (2026-07-11 evening):** `python3 scripts/portfolio_browser.py agentguard buyer --fixture` →
`"success": true` (checkout_allow, approval_required, approval_consumed, replay_rejected, agent_paused, deny_while_paused). Receipt `rcpt_c1503c4cd116494d`.

```bash
python3 scripts/portfolio_browser.py agentguard buyer --fixture
```

Earlier same-day API proof (pre-Hermes recovery): Buyer checkout INR 3,000 allowed; INR 15,000 required approval; consume 200; replay 409; pause 200; next checkout denied. Receipt `rcpt_0e66b0e999b345f3`.

**Re-run (2026-07-11T15:54Z, commit `6907ce3` WT):** `agentguard buyer --fixture` → `"success": true` all checks; receipt `rcpt_f5a78757a06547c4`; SSO **Sign out**; orb button **S** on `/search`. Gateway pytest via `verify-portfolio.sh`: **57 passed**.

## Buyer Config + Samantha (M10/M12 operator path)

Operator proof for `/config` mandate editor + Realtime orb (not a `portfolio_browser` subcommand yet). WIP Hermes only.

| Step | Pass signal | Result (2026-07-11T15:55Z) |
| --- | --- | --- |
| Stack / realtime status | `GET :43101/api/realtime/status` → `configured:true`, model `gpt-realtime-2.1-mini`, `agent_name:Samantha` | **Pass** |
| Client-secret mint | `POST :43101/api/realtime/client-secret` HTTP 200; ephemeral `ek_…` secret; no long-lived key in browser | **Pass** (secret_len 35, expires_at set) |
| Buyer SSO | burner `dev_auto`; **Sign out** on `:43102` | **Pass** |
| `/config` UI | H1 `AgentGuard & Samantha`; cards AgentGuard mandate + Samantha memory; Confirm mandate | **Pass** — note `Mandate confirmed.`; memory Likes/Dislikes/Preferences/Notes |
| Mandate confirm API | compile + `POST …/mandates/{id}/confirm` → 200, status `active` | **Pass** — `mandate_8a6e0f1bb7344c1a` |
| Samantha orb | bottom-right **S**; hint; link Preferences & AgentGuard | **Pass** — hint `Connecting Samantha…`; link visible |
| Mic / WebRTC listen | mic connected; no NotFoundError | **Blocked (automation)** — `permissions mic=prompt`; console `Requested device not found` / `NotFoundError` after orb click (no host mic device). Product gates above still pass. |

**Commands used:** `./scripts/verify-portfolio.sh` → `./scripts/start-dev.sh` (preflight auto-restart) → `portfolio_browser.py preflight` → `agentguard buyer --fixture` → ad-hoc Hermes session `samantha-config-op` on `/config` → `closeout`.

**TESTINGPLAN gap:** M10–M12 Layer 5 are prose-only (no `portfolio_browser` lane for `/config` or Samantha). Baseline § still says buyer AgentGuard is unimplemented — stale vs this ledger. Encode a scripted config/orb lane only after a second consecutive manual pass of this path.

**Ops note:** gateway `:43101` dropped between verify and immediate follow-up curls; preflight/`start-dev.sh` recovered. Treat stack as verify-ready only after a fresh health check.

### Full Buyer journey re-pass (2026-07-11T16:10Z, Hermes WIP `buyer-full-journey`)

Utterance-style intents replayed as operator (not live mic): “looking for apple / Shimla Apples”, preferences (organic / noise-cancelling / hate bright colors), cheapest under budget, checkout over mandate max, unknown product, duplicate add, orb start/stop.

| Journey step | Result |
| --- | --- |
| Land `/search` + nav (Search/Cart/Orders/Config) + orb **S** | **Pass** |
| Burner SSO sticky (**Sign out**) | **Pass** |
| UI search `apple` → results (was 0 matches) | **Pass** after fix — mock fallback + grocery includes fruits |
| UI Add → `/cart` shows Shimla | **Pass** |
| Tool path `runBuyerTool` search→add→localCart; empty/unknown reject; memory | **Pass** |
| `/config` mandate confirm max=100; memory likes/dislikes/prefs visible | **Pass** |
| AG evaluate under=allow / over=`need_approval` | **Pass** |
| `/product/fresh-apples-1kg`, `/orders`, `/agent` (no VoiceShoppingPanel) | **Pass** |
| Orb start/stop + Preferences link; stop-during-connect no longer throws | **Pass** (listening on this host; mic still env-dependent) |
| Cart title uses `name` when descriptor missing; qty +/- | **Pass** |

**Fixes this pass:** `useApi.ts` empty demo search → mock; `mockSearch.ts` grocery∋fruits; `SamanthaOrb.tsx` abort-safe WebRTC + mic errors; `CartComponents.tsx` title fallback; `agentTools.ts` skip spaced-id commerce 404 + label cartAdds.

**Still limited:** live spoken Realtime mic path depends on host mic; no `portfolio_browser` subcommand for full Buyer journey yet (2nd consecutive pass of this path still needed before automating).

## AgentGuard FlatWatch lane

**Deferred — out of Token Nxt scope.** Hermes `agentguard flatwatch` deleted. Do not rebuild until FlatWatch reactivation gate in `flatwatch/GOAL.md`.

## Two-sided commerce lane

**Validated (2026-07-11 evening):** consecutive unique run_ids after WIP bridge recovery.

```bash
python3 scripts/hermes_two_sided_commerce.py --fixture --run-id "ag-$(date +%s)-a"
python3 scripts/hermes_two_sided_commerce.py --fixture --run-id "ag-$(date +%s)-b"
# or: python3 scripts/portfolio_browser.py two-sided --fixture  (use unique run-ids for consecutive proofs)
```

Passes: `ag-1783781283-36e172`, `ag-1783781283-db290e` (earlier: `ag-hermes-1783779577-a`, `ag-hermes-1783779578-b`, API `ag-1783778465`). Checks: seller publish → buyer search → checkout → seller order/issue/remedy.

**Cleared 2026-07-11 evening:** WIP bridge recovered. **Re-validated 2026-07-11T14:51Z:** judged seller UI + buyer + two consecutive two-sided + gateway 56 pytest.

## Subagent orchestration

Hermes WIP + host browser = **one agent at a time** for **SSO / onboarding / commerce / `lane`**. `start-dev.sh` = **one stack starter at a time**.

**Exception (2026-07-10):** deterministic **WIP** parallel smoke (`scripts/parallel_smoke_wip.py`) may open multiple leased windows — smoke/console only, **no SSO**. Do not run that in parallel with `lane` / Solflare / onboarding. All portfolio browser paths use **WIP Hermes only** (not Codex live).

| Wave | Lane(s) | Parallel? | Depends on |
| --- | --- | --- | --- |
| 0 | First-run setup (`setup.sh` → `start-dev.sh`) | Internal sequential only | — |
| 1 | Portfolio API (`pytest`) | Parallel with wave 0 after `setup.sh` | Wave 0 `setup.sh` |
| 1b | Solana on-chain (`validate-onchain.sh`) | **Mutex** on `:8899` / ledger | Exclusive agent; no parallel ledger reset |
| 2 | Portfolio browser burner (`lane burner seller`) | **Mutex** — already validated | Wave 0 `start-dev.sh` |
| 3 | Identity onboarding | **Mutex** | Wave 0; prefer before wave 4–5 |
| 4 | Solflare SSO (`sso solflare seller\|buyer`) | **Mutex** | Wave 0; independent of burner wallet |
| 5 | Elevated commerce (buyer → seller) | **Mutex**; buyer then seller sequential | Wave 3 verified trust + wave 2 or 4 SSO |

**Recommended agent assignment**

| Agent | Lanes | Run when |
| --- | --- | --- |
| **bootstrap** | First-run setup | Fresh clone or missing deps only |
| **api** | `pytest tests/` | After `setup.sh`; parallel with `start-dev` if stack already up |
| **browser-onboarding** | Identity onboarding | After stack up; before commerce |
| **browser-sso-solflare** | Solflare SSO | After stack up; not concurrent with other browser agents |
| **browser-commerce** | Elevated commerce | After verified trust + SSO session |

**Do not** run `browser-onboarding`, `browser-sso-solflare`, `browser-commerce`, or `lane` in parallel — they contend for WIP Hermes sessions, host-browser Space, and SSO popup focus.

**Do** use `parallel_smoke_wip.py` for parallel web/buyer/seller smoke on the **WIP** bridge (separate from live Hermes). Still do not overlap it with SSO/`lane`.

**Do not** run multiple on-chain subagents in parallel — they contend for `:8899` and `.local-validator` (same mutex class as Hermes).

## Simplify backlog

- [x] Single `verify-portfolio.sh --browser` entry (lane command)
- [x] `lane` command in `portfolio_browser.py`
- [x] Single `verify-portfolio.sh` API entry (default, no browser)
- [ ] Trim duplicate prose in AGENTS.md vs SKILL.md (partial — AGENTS points to SKILL)
- [ ] Single `verify-solana.sh` entry (if on-chain E2E stable)

## Empty-iteration stop

**API lane: met** (2026-07-06) — two consecutive `./scripts/verify-portfolio.sh` (no browser), exit 0, 43 passed.
**Browser lane (burner): met** (2026-07-06) — two post-hardening `lane burner seller` runs, exit 0, no new failures/inefficiency.
**Identity onboarding: met (phase 2, 2026-07-06 evening)** — two consecutive runs (~52s); API trust verified + Sign out; seller UI trust chip mismatch documented.
**Solflare SSO: not met** (scaffolded).
**First-run setup: met** (2026-07-06) — two consecutive `setup.sh` exit 0 + stack URL bookend (verify-only; stack already up).
**Elevated commerce: met** (2026-07-10) — seller `--fixture` → `/catalog`; buyer checkout → `/orders/demo-…` (evaluate fill; WIP `fill_selector` Detach).
**On-chain anchor validate: met** (2/2, 58/58 each). **Gateway init config + bridge E2E: met** (2026-07-06 night) — deploy-only ~27s; init config with `skip_preflight`; approve path writes `chain_transaction_signature` (2 consecutive API smokes). `verify-solana.sh` remains automation candidate (phase 5).

## Samantha operator-long text (2026-07-11)

Command: `python3 scripts/hermes_samantha_operator_long.py`

| Signal | Result |
| --- | --- |
| 11/11 operator utterances replied | **Pass** |
| Cart has Shimla/Organic apples | **Pass** |
| Preference recall in dialogue | **Pass** |
| Empty catalog (unicorn cereal) | **Pass** |
| Config memory UI | Partial before merge fix |
| Milk under 100 in cart | Miss this run |
| checkout_commit / navigate_to | Soft model refuse — instructions tightened |

## Samantha Buyer re-pass + Seller ops (2026-07-11 night)

| Lane | Command | Result |
| --- | --- | --- |
| Buyer operator-long | `python3 scripts/hermes_samantha_operator_long.py` | **Pass** — 11/11, `cart_ok`, `/config` shows AgentGuard + Samantha memory (organic / bright / noise-cancelling) |
| Buyer unit | `ondcbuyer` `agentTools` + `mockSearch` | **Pass** — milk under 100, navigate_to, subjectId memory, checkout_commit AG path |
| Seller Samantha ops | `python3 scripts/hermes_samantha_seller_ops.py` | **Pass** — 5/5, mandate boot active, `/agentguard` orb + Samantha memory (`brief refund confirmations`), `memory_ok` + `nav_ok` |
| Seller unit | `ondcseller` `agentTools.test.ts` | **Pass** — navigate / remember / refund need_approval |
| AgentGuard seller fixture | `portfolio_browser.py agentguard seller --fixture` | **Pass ×2** (2026-07-11 night) — all checks true under demo principal SSO; root cause was refund UI gating on `walletAddress` (buttons disabled) + fixture `no_wallet`, not Hermes `MAX_ACTIONS` |

**Demo gate (Token Nxt local):** Buyer Samantha operator-long **11/11** · Seller Samantha ops **5/5** · Seller AG fixture **Pass ×2** (principal UI approve/replay/pause/deny).

**Fixes this pass:** mock milk + dairy under grocery; mock search “under N” price filter; commerce/mock search conflict fallback; Buyer/Seller Samantha instructions; Seller `SamanthaOrb` + seller memory; gateway realtime `role:seller`; AgentGuard page principal (`subjectId`) + memory card; deterministic `remember_preference` / `navigate_to` text cmds for Hermes; Seller order refunds bind `subjectId` (demo principal) instead of wallet; Hermes fixture ensure/resume via cookie principal.

**Residual non-goals:** live ONDC/NPCI; live mic host-dependent; Google OAuth credentials optional (demo principal sufficient); milk-in-cart still soft under model lag (unit + catalog covered).

## Samantha banana visible journey (2026-07-12)

| Gate | Result |
| --- | --- |
| Ask “add banana to my cart” (text orb) | **Pass** — `search_catalog` → `add_to_cart` (`banana-robusta-dozen`); URL `/cart`; body shows **Robusta Bananas (12 pcs)** |
| “hi” spot-check | **Pass** — stayed `/search`, no cart tools |
| Closeout | **Pass** — `http://127.0.0.1:43102/cart`, bridge ready |

**Root cause:** `session.update` used invalid `output_modalities: ['audio','text']` (API allows one) → session error; silent mic track left VAD on → ghost turns; model talked without tools. Also hardened `extractRealtimeToolCalls` for GA nested `item` shape.

**Fixes:** `SamanthaOrb.tsx` modalities + `turn_detection: null` in text mode; wait for `session.updated`; `agentTools` search/cart `navigateTo`; `realtimeToolCalls.ts` nested item extraction.

## Final deployed AgentGuard FQDN gate (2026-07-14)

Final surfaces: `gateway.aadharcha.in`, `ondcbuyer.aadharcha.in`,
`ondcseller.aadharcha.in`. Vercel Hobby and Render Free were confirmed before
deploy; no billing/plan changes were made.

| Gate | Command / evidence | Result |
| --- | --- | --- |
| Gateway deterministic | `./scripts/verify-portfolio.sh --ci` | **Pass** — gateway **80/80** |
| Buyer deterministic | `npm test`, lint, build | **Pass** — **151/151** |
| Seller deterministic | `npm test`, lint, build | **Pass** — **158/158** |
| Live hard grader | `python3 scripts/ondc_ci_graders.py --live --hard` | **Pass ×2** — gateway ACK + configured Seller ACK; exact Atta callback; rewrites/runtime/Realtime/bundles |
| Buyer FQDN pass 1 | `web-e2e-thorough-20260714-030751.json` | **Pass** — session/mandate, exact Atta, cart, paid checkout+receipt, pause/resume, activity, verify, runtime; mic Blocked |
| Seller FQDN pass 1 | `web-e2e-thorough-20260714-023601.json` | **Pass** — publish, latest-order refund, detail, allow receipt, approval, consume, replay rejection, memory/runtime; mic Blocked |
| Final combined pass 2 | `web-e2e-thorough-20260714-031443.json` | **Pass** — all strict Buyer + Seller assertions repeated; no `Fail`; session closeout clean |
| Chrome post-deploy full gate | `web-e2e-thorough-20260714-174011.json` | **Pass with explicit boundary** — **26 Pass / 3 Blocked / 0 Fail**; Buyer and Seller functional, AgentGuard, memory, and runtime paths passed; physical mic/voice is the only Blocked surface; WIP owner was Google Chrome profile directory `robo-trader-testing` |
| Browser lease audit | WIP Hermes `sessions` | **Pass** — empty inventory |

Delivered corrections: semantic ONDC ACK/payment intent, signed configured-BPP
search beside normal PreProd fanout, exact Buyer query normalization, scoped
principal storage, Seller route/runtime tests, latest-order refund, shared-order
detail, server-principal approval, per-attempt idempotency, replay proof, Buyer
pause/activity/receipt verification, strict non-mutating FQDN grader, and guarded
archive deploy script.

Open boundaries (not release blockers for the PreProd demo claim):

- Physical microphone proof remains **Blocked** in Hermes; do not claim the M12
  mic exit criterion. Realtime configuration, text tools, and runtime passed.
- Render Free state is file-backed under `/tmp` and may reset on restart/redeploy;
  the Buyer UI now discloses this. Durable production storage remains open.
- Install audit remains **120 Buyer / 125 Seller advisories** (five critical
  each); production-only audit is **111 Buyer / 117 Seller** (two critical
  each). No unsafe `npm audit fix --force` was run.
- A removed Voyage key remains in git history and must be revoked/rotated outside
  this repo. Current tracked files no longer contain it.

---

## Local Samantha frozen-source browser gate — 2026-07-16 00:08–00:34 IST

| Gate | Command / evidence | Result |
| --- | --- | --- |
| Combined local pass 1 | `matrix-run-20260716-000819.json` | **31/31 Pass** — Buyer 19, Seller 12; 32/32 screenshots visually accepted; zero turn errors; matrix closeout clean |
| Combined local pass 2 | `matrix-run-20260716-002128.json` | **31/31 Pass** — unchanged source; 32/32 screenshots visually accepted; zero turn errors; matrix closeout clean |
| Buyer checkout semantics | exact tool/backend evidence + screenshots | **Pass ×2** — real INR 25,089 cart → `need_approval`; expensive item removed; INR 89 cart → `allow`, paid order, matching receipt |
| Seller lifecycle semantics | exact tool/backend evidence + screenshots | **Pass ×2** — publish visibility; accept→fulfill; reject; refund allow + INR 26,000 approval; runtime handoff |
| Deterministic gates | tests, typecheck, builds, validators, Ruff/diff | **Pass** — Buyer 155 tests; Seller 163 tests; both production builds; `portfolio-browser` and `ondc-testing` validators |

This is local text/runtime browser proof only. It does not refresh deployed FQDN evidence and does not claim physical microphone/WebRTC completion.

---

## Milestone 8 AgentGuard sole-owner cleanup — 2026-07-16 17:46–18:12 IST

| Gate | Command / evidence | Result |
| --- | --- | --- |
| Seller visible authority | `PORTFOLIO_SKIP_PREFLIGHT=1 python3 scripts/portfolio_browser.py agentguard seller --fixture` | **Pass** — INR 3,000 allowed; INR 7,500 required one-time approval; replay rejected; pause visible; next refund denied; receipts visible |
| Buyer visible authority | `PORTFOLIO_SKIP_PREFLIGHT=1 python3 scripts/portfolio_browser.py agentguard buyer --fixture` | **Pass** — mandate INR 5,000; unique published INR 7,500 SKU found through the real ONDC collect path; approval and receipt visible in Config; pause visible; next checkout denied; agent restored active during closeout |
| Buyer deterministic | `npm test && npm run typecheck && npm run build` | **Pass** — 25 files / 148 tests; typecheck clean; production build clean apart from existing chunk and browser `node:crypto` warnings |
| Seller deterministic | `npm test && npm run typecheck && npm run build` | **Pass** — 14 files / 164 tests; typecheck clean; production build clean apart from existing chunk and browser `node:crypto` warnings |
| Gateway deterministic | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/pytest -q tests/test_agentguard.py tests/test_commerce_demo.py` + Ruff | **Pass** — 15 tests; Ruff clean |
| Browser owner validation | `.cursor/skills/portfolio-browser/scripts/validate.sh` + Python compile/Ruff | **Pass** — process-local WIP lease preflight/closeout and semantic lanes validate cleanly |

Changed-source conclusion: AgentGuard is the sole authorization owner for the
consequential Buyer/Seller mutation paths changed in this goal. The remaining
Seller policy/runtime and Buyer Netlify surfaces are explicitly legacy
compatibility callers with a deletion date after 2026-08-01; they are not used
by the current Vercel/Render protected-write path. Replay proof is Seller-owned;
Buyer proves the complementary approval receipt and paused-checkout outcome.

### Milestone 8 two-sided visible identity repair — 2026-07-16

`scripts/hermes_two_sided_commerce.py` previously exercised only the API despite being the declared visible lane. It now captures Seller catalog, Seller order, and Buyer order through WIP Hermes, authenticates the correct app audience immediately before each capture, retains screenshot paths, and fails unless the same order/transaction plus Buyer issue are visible.

- Diagnostic Fail: `m8-visible-1784208100-a` exposed overwritten Buyer SSO and a stale gateway process; neither was counted as acceptance.
- Pass A: `m8-visible-1784208200-a` — `order_046194d8c55b46e5` / `txn_7c370c1c44094790`.
- Pass B: `m8-visible-1784208201-b` — `order_e5539c89c77b4593` / `txn_26866a2a067a46a0`.
- Retained evidence: `.cursor/skills/ondc-testing/references/evidence/m8-browser-local-authority.md` and six JPEG captures under its sibling `m8-browser-local-authority/` directory.
- Closeout: `python3 scripts/portfolio_browser.py closeout http://127.0.0.1:43102/search` passed; WIP bridge remained ready.

### Milestone 8 contract and visible-flow consolidation — 2026-07-16

Buyer and Seller now consume the shared AgentGuard action, agent, mandate,
approval, and intent-receipt types. Both displaced standalone `/agent` routes
and their navigation entries were deleted; the global Samantha orb remains the
single visible assistant surface. The judged Buyer, Seller, and two-sided Hermes
scripts contain no AgentGuard evaluate/consume/pause/mandate API shortcuts.

| Gate | Result |
| --- | --- |
| Buyer deterministic | **Pass** — 21 files / 131 tests; typecheck + production build |
| Seller deterministic | **Pass** — 13 files / 162 tests; typecheck + production build |
| Gateway deterministic | **Pass** — `./scripts/verify-portfolio.sh --ci`, 86 tests |
| Final visible run A | **Pass** — `m8-contract-final-1784209300-a`; `order_47aa87015f8f40ec` / `txn_a9607f26c37c4315` / `issue_6ff48b295bd64728` |
| Final visible run B | **Pass** — `m8-contract-final-1784209301-b`; `order_070f0ce5a9274463` / `txn_8b9c603db3d04b5c` / `issue_46a0ee83c93d45d9` |
| Visual review | **Pass** — six retained screenshots opened and accepted; no competing standalone agent link; global Samantha orb visible |
| Closeout | **Pass** — WIP bridge ready; Buyer search leave URL requested |

Retained evidence: `.cursor/skills/ondc-testing/references/evidence/m8-contract-flow-consolidation.md`
and six JPEGs in its sibling `m8-contract-flow-consolidation/` directory.

## AgentGuard final local safety candidate — 2026-07-17

Source SHA-256: `d940189015a07678ac2704554a80da16874d0c0021b15c9b5d2bb7ec54684a05`.

| Gate | Run IDs | Result |
| --- | --- | --- |
| Targeted adversarial | `LOCAL-ADVERSARIAL-20260717-D940-P1`, `LOCAL-ADVERSARIAL-20260717-D940-P2` | **Pass ×2** — 87/87 each |
| Portfolio verifier | `LOCAL-SAFETY-20260717-D940-P1`, `LOCAL-SAFETY-20260717-D940-P2` | **Pass ×2** — gateway 129/129 each |
| Buyer deterministic | same run IDs | **Pass ×2** — 151/151, typecheck, build, copy gate |
| Seller deterministic | same run IDs | **Pass ×2** — 172/172, typecheck, build, copy gate |
| Seller UI/UX | `SELLER-UX-D940-A1` | **Tooling Blocked** — semantic page and owned screenshot diverged; lease closed and absent |
| Seller UI/UX bounded retry | `SELLER-UX-D940-A2-BOUNDED-RETRY` | **Tooling Blocked** — owned lease disappeared twice; closeout confirmed owned sessions absent |
| Buyer/Seller customer passes | — | **Not Tested** on this hash; browser campaign stopped after repeated ownership failure |

Retained evidence: `.cursor/skills/ondc-testing/references/evidence/local-safety-final-20260717-d940.json`.
Prior Seller customer passes were on an invalidated source hash and are not
counted. Deterministic evidence does not replace the three open visible rows.

## Final-hash independent Buyer proof blocker — 2026-07-17

Source SHA-256: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.

| Gate | Result |
| --- | --- |
| Buyer blind pass 1 | **Tooling Blocked** — visible search/cart journey reached `/checkout`; semantic input lookup failed and cursor entry persisted only a partial name |
| One bounded recovery | **Tooling Blocked** — the same checkout input-targeting class repeated; phone entry appeared in postal-code readback; no authorization submitted |
| Closeout | **Pass** — both owned session ids absent; no order or receipt created |
| Remaining customer campaign | **Not Tested** — stopped before Seller, two-sided, or combined UI/UX dispatch |

Retained evidence: `.cursor/skills/ondc-testing/references/evidence/local-customer-proof-blocker-20260717-af987.json`.
Resume only after the WIP Hermes semantic input path is repaired and independently checked; rerun the entire Buyer mission from a fresh principal.

## Final-hash Buyer proof resumed after Hermes repair — 2026-07-18

Source SHA-256: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.

| Gate | Result |
| --- | --- |
| Hermes semantic remount regression | **Pass** — late-mounted/remounted Full name target received text; postal decoy remained empty |
| Concurrent capture stress | **Pass** — three repeated A/B rounds returned the correct lease-specific pixels with bounded readback recovery and quota pacing |
| Full isolation admission | **Pass ×3** — two consecutive owner-gate passes plus the checkpoint execute-once pass; every lease closed |
| Buyer audience setup | **Pass** — fresh demo principal, visibly empty cart, `reviewer_ready`, two byte-identical signed-in screenshots |
| Fresh blind Buyer mission | **Tooling Blocked** — labeled search fill first failed; after the one allowed recovery it visibly contained `rice`, then the visible Search click failed with `Locator did not resolve for click` |
| Data hygiene / closeout | **Pass** — 12 item ids, 8 order ids, and inventory unchanged; no cart/order delta; owned session absent and inventory empty |

Retained evidence: `.cursor/skills/ondc-testing/references/evidence/local-customer-proof-blocker-20260718-af987-search-locator.json`.
The browser campaign stopped before cart mutation. Seller, two-sided, and combined
UI/UX remain **Not Tested** on this hash; deterministic or fixture evidence does
not replace the fresh blind rerun after the locator owner is repaired.

## CF1 release candidate checkpoint — 2026-07-22

Source fingerprint: `e95340b069cab63b75f436e0d5fdfe4e667545c40d2ee9b378f1b5957914db26`.

| Gate | Result |
| --- | --- |
| Source identity | **Pass** — portfolio `b8b90bd`, gateway `fd586da`, Buyer `f028ade`, Seller `8146340`; all tracked worktrees clean on `main`/`origin/main`. The separate untracked `portfolio-site/` repository is outside this manifest. |
| Deterministic matrix | **Pass** — gateway CI 152/48 skipped and PostgreSQL 200; Buyer 195 plus typecheck/build; Seller 211 plus typecheck/build; offline ONDC grader passed. |
| PostgreSQL two-cycle readback | **Pass** — two SKUs, orders, successful simulated payments and full refunds; inventory 20→18 twice; six signed receipts grouped as publish/checkout/refund ×2. |
| Deployment | **Pass** — Render Free deployment `dep-d9gc443bc2fs73frb320` live at gateway commit `fd586da`; Buyer/Seller Vercel Hobby deployments Ready and FQDN verification probes 200. |
| Buyer Chrome Pass 1+2 | **Pass** — unchanged source and database `cf1_release_e95340`: `CF1 e953 A Atta 1kg` produced order `CAC1D3A8`, simulated payment `CFD9BD5C`, and verified signed receipt; `CF1 e953 B Atta 1kg` produced order `EC116D90`, simulated payment `945F12AE`, and verified signed receipt. Both runs used exact one-time approval and ended with zero browser console errors. |
| Seller Chrome Pass 1+2 | **Pass** — each Buyer order was discovered and fully refunded in the same unchanged-source campaign. The terminal UI showed Cancelled/Refunded with verified authorization references `DC4D0FC9` and `F3601E3D`; PostgreSQL agreed with exactly two successful full refunds and no duplicate effect. |
| Combined responsive/accessibility smoke | **Pass** — Buyer and Seller desktop shells at 1920×902 each exposed one main, one navigation and one banner, no duplicate IDs, and no horizontal overflow. At 390×844 both navigation dialogs had accessible names/headings, closed with Escape, returned focus to their triggers, and had no horizontal overflow or console errors. Temporary viewport overrides were reset. |
| FQDN/Auth0 Buyer/Seller | **Pass** — deployed Buyer returned from Auth0 to a verified AgentGuard session, exposed protected navigation/account state, and completed an `atta` search to the truthful zero-match state. Deployed Seller returned from Auth0 to a verified identity, then loaded protected dashboard, catalog and incoming-orders surfaces. Both FQDN journeys had zero console errors. The public ONDC live-search soft grader remains advisory: the public catalog is intentionally unseeded and the first Free-tier calls briefly returned 503 while the service settled. |

Final evidence: `.cursor/skills/ondc-testing/references/evidence/cf1-release-e95340-checkpoint-20260722.json`.

Remaining exclusions are unchanged: real payments, production ONDC conformance,
native voice, iOS, multi-seller checkout, and broad redesign.
