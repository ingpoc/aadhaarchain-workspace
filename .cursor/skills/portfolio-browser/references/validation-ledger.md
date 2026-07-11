# Validation ledger

Track **manual** runs before simplifying or automating. Update after each full-path iteration.

Phase order: make it work → **validate (this file)** → simplify → optimize → automate.

**Lane status:** Portfolio API + browser (burner) + first-run setup + identity onboarding + on-chain anchor validate + **gateway on-chain E2E** validated. Solflare/commerce scaffolded; **AgentGuard seller** validated (2026-07-11) — see [AgentGuard seller lane](#agentguard-seller-lane).

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
| `agentguard seller --fixture` | Stack up; WIP Hermes; gateway AgentGuard routes | JSON `"success": true`; checks policy/need/replay/paused/deny | **2 pass** (2026-07-11) | `python3 scripts/portfolio_browser.py agentguard seller --fixture` (SSO then Hermes script) |
| Gateway pytest | gateway `.venv` | `tests/test_agentguard.py` pass | API | Does not replace Hermes lane |

**Validated bookend (2026-07-11):** two consecutive `AGENTGUARD_SKIP_SSO=1` Hermes script passes after burner SSO — UI refunds + API consume/replay/pause/deny.

**Parallel with other lanes?** No — Hermes mutex with `lane` / SSO / commerce / onboarding.

**Hermes / Chrome?** Yes.

**Validator `:8899`?** No.

**Blocked by:** Fixture verified trust + seller SSO (`dev_auto` in script).

## AgentGuard buyer lane

ONDC Buyer checkout consume (`ondcbuyer/GOAL.md` phase-one): allow ≤ INR 10k → need approval over → consume once → replay 409 → pause → deny. UI checkout lands `/orders/…` with AgentGuard note.

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| `agentguard buyer --fixture` | Stack up; WIP Hermes; seller lane green | JSON `"success": true`; order + gate checks | **1 pass** (2026-07-11) | SSO then `AGENTGUARD_SKIP_SSO=1`; note may clear after `/orders` redirect |
| Gateway pytest | gateway `.venv` | checkout cases in `test_agentguard.py` | API | — |

**Manual bookend (2026-07-11):** checkout → `/orders/…` + API allow/need/consume/replay/pause/deny.

**Parallel with other lanes?** No — Hermes mutex.

**Hermes / Chrome?** Yes.

**Validator `:8899`?** Burner SSO only (preflight).

## AgentGuard FlatWatch lane

FlatWatch dual-control (`flatwatch/GOAL.md`): create payment/correction proposal → 2-of-2 approve → replay reject (409).

| Step | Preconditions | Pass signal | Manual runs | Notes |
| --- | --- | --- | --- | --- |
| `agentguard flatwatch` | Stack up; FlatWatch `:43104`/`:43105` | JSON `"success": true`; approved + replay 409 | **1 pass** (2026-07-11) | API in-process (CORS); Hermes page evidence on `:43105` |
| FlatWatch pytest | backend `.venv` | `tests/test_dual_control.py` pass | API | — |

**Manual bookend (2026-07-11):** dual-control 2-of-2 + replay 409 + FlatWatch home title.

**Parallel with other lanes?** No — Hermes mutex.

**Hermes / Chrome?** Yes (page context on `:43105`; API on `:43104`).

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