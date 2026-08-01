# AadhaarChain Portfolio — Agent Control Surface

Read this file first. Repo-local app `GOAL.md` files add outcome detail only.

**Product:** [AgentGuard](PRODUCTIDEA.md) — safe agentic commerce authority. Token Nxt demo is **ONDC Buyer + ONDC Seller** under one control contract. `aadharchain/` hosts the gateway only (legacy checkout, not the product). FlatWatch / Solana are deferred hangars.

## Owner map (do not invent parallel contracts)

| Concern | Owner |
| --- | --- |
| Product thesis / non-goals | [`PRODUCTIDEA.md`](PRODUCTIDEA.md) |
| Product design / UX / design acceptance | [`.voice/DESIGN.md`](.voice/DESIGN.md) |
| Shared contracts / protocol | [`.voice/ARCHITECTURE.md`](.voice/ARCHITECTURE.md) |
| Build order / milestones | [`.voice/IMPLEMENTATIONPLAN.md`](.voice/IMPLEMENTATIONPLAN.md) |
| Verification gates / evidence | [`.agents/skills/testing-ledger/SKILL.md`](.agents/skills/testing-ledger/SKILL.md) |
| Buyer outcome | [`ondcbuyer/GOAL.md`](ondcbuyer/GOAL.md) |
| Seller outcome | [`ondcseller/GOAL.md`](ondcseller/GOAL.md) |
| Gateway decomposition | [`aadharchain/GOAL.md`](aadharchain/GOAL.md) |
| FlatWatch (deferred) | [`flatwatch/GOAL.md`](flatwatch/GOAL.md) |
| Ops / KYC / ONDC portal later | [`PRODUCTION-READINESS.md`](PRODUCTION-READINESS.md) |
| Current execution state / evidence gates | [`.voice/progress.md`](.voice/progress.md) |

Work in IMPLEMENTATIONPLAN milestone order. PreProd-ready Token Nxt demo =
milestones 0–7 + TESTINGPLAN demo gate + FQDN `W-*`. **Agent-as-executor** =
milestones 10–12 (mandate editor, Cursor tool runner, Buyer Realtime voice).
Live ONDC = milestone 9 only. AgentGuard remains the sole authorization owner;
do not invent parallel auth contracts.

`.voice/IMPLEMENTATIONPLAN.md` owns long-term milestones and sequencing; `.voice/progress.md`
owns current execution state and evidence gates. Update the relevant owner when
work changes.

## Active ONDC participant-host gate

Every agent adding an ONDC participant FQDN must use this fail-closed order:
reuse the existing gateway with isolated identity/keys → deploy the exact
verified commit → attach and verify the existing Render target → add only the
approved GoDaddy DNS record → prove public DNS, TLS, site verification, and
`/ondc/on_subscribe` → only then resume portal access. GoDaddy is DNS only;
Render is the application runtime. Never reuse Retail keys/mappers, create a
parallel gateway/service, publish DNS before the runtime target is known, or
advance a portal/protocol gate from partial evidence. A reproducible defect
fixed on this path must leave one deterministic regression check in its owner.
If `Raise Request` generates a modal keypair, that latest pair supersedes the
outer draft pair: reconcile key ID/fingerprints and re-prove the public endpoint
before Submit. Protocol Workbench replaces Pramaan only for later verification;
1.a completion does not authorize 1.b, protocol, conformance, or production.
For an authorized Workbench run, keep exactly one flow active, satisfy its
visible input schema, send the signed action before the five-minute expectation
expires, and derive every later identifier from signed callback/readback. An
`activeFlow` label alone is not proof that an expectation exists. Treat
`accept_bpp_terms` and any other legal-semantic field as an operator boundary,
and preserve the exact Workbench/portal tabs when stopping there. Validate tags
per outbound action instead of copying callback tags blindly, and advance an
`INPUT-REQUIRED` step with an empty schema exactly once using empty inputs.

## Workflow hardening gate (read before changing scripts)

```
1. Make it work   — one manual end-to-end success
2. Validate       — repeat manually; write preconditions + pass signals
3. Simplify       — ONLY NOW remove duplicate entry points / prose
4. Optimize       — bookends, retries, timings (from failed/slow manual runs)
5. Automate       — wrapper scripts last
```

**Do not simplify or remove steps until phase 2 is done** (two consecutive manual passes in `validation-ledger.md`). Improvised recovery during verify/browser ⇒ encode before done.

## First commands

```bash
# 0. Fresh clone / missing deps
./scripts/setup.sh   # then ./scripts/start-dev.sh if :43100–43105 are not all 2xx

# 1. Testing-ledger baseline
./scripts/verify-portfolio.sh
cd ondcbuyer && npm test && npm run build
cd ../ondcseller && npm test && npm run build

# 2. Legacy deterministic browser harness (explicit fallback/diagnosis only)
python3 scripts/portfolio_browser.py agentguard seller --fixture

# 3. Legacy harness demo-principal SSO helper (no wallet)
python3 scripts/portfolio_browser.py sso demo buyer
```

Restart ONDC buyer/seller after changing `.env.local`. Solana `:8899` is **not** part of AgentGuard acceptance.

## Portfolio browser

Bookends: `.cursor/skills/portfolio-browser/SKILL.md`. Ledger: `.cursor/skills/portfolio-browser/references/validation-ledger.md`. Samantha / ONDC customer gate: `.agents/skills/testing-ledger/SKILL.md` (doctrine → `~/.agents/skills/testing-framework`). Auth / Auth0 / sessions: `.cursor/skills/authentication/SKILL.md`. Public Render/Vercel deploy + **CI/CD** (graders, `ci.yml` / `deploy.yml`, Free/Hobby): `.cursor/skills/portfolio-deploy/SKILL.md` (`references/ci-cd.md`).

| Lane | Status |
| --- | --- |
| Current local Buyer `@Chrome` | **Pass 1 + Pass 2** (2026-07-25, frozen source, PostgreSQL): two mandate-governed orders, simulated payments, signed authorization, and reload persistence |
| Current local Seller `@Chrome` | **Pass** (2026-07-25): both orders completed full lifecycle/refund; targeted protected archive rerun passed and cleanup returned the catalog to zero products |
| Current FQDN/Auth0 checkpoint | **Pass 1 + Pass 2** (2026-07-23, unchanged source, PostgreSQL) for Buyer and Seller plus combined responsive/accessibility smoke |
| Prior CF1 release checkpoint | **Historical pass** (2026-07-22); retained in the validation ledger and superseded as current acceptance by the CF0 contract-closure checkpoint |
| Legacy `agentguard buyer/seller --fixture` | Historical deterministic/Hermes proof: Seller ×2 (2026-07-11); Buyer API/Hermes and FQDN ×2 (2026-07-14). Historical only; current CF0 acceptance is owned by the bundled Chrome checkpoint |
| Legacy `two-sided --fixture` | Historical unique-run proof (2026-07-11); historical only, not the owner of current local or FQDN acceptance |
| Mandate editor / agent tools / Realtime | M10 code present; M11 text tools/runtime historically FQDN validated; M12 Realtime configured + text validated. Current-source runtime breadth and physical microphone proof remain open |
| FlatWatch AgentGuard | **Deferred** — out of scope |

Default interactive UI control is bundled `@chrome` for browser pages and bundled `@Computer` for native Mac UI. The WIP Hermes portfolio harness is legacy deterministic replay/diagnosis only; use it only when explicitly requested or after the operator approves fallback from an unavailable bundled route. SSO stays mutex.

**Legacy harness history:** preflight auto-starts `start-dev.sh`; HTTP retries 30s; AG lanes use **demo principal SSO** (no Solana); legacy burner SSO auto-`ensure-validator.sh` only for hangar wallet lanes; `lane` avoids triple preflight; WIP `SOCKET_DOWN` — evidence first: **SW Inactive** (primary 2026-07-12) vs classic path trap (`native_host.py` → `~/.hermes/run`); preflight `ensure-wip-native-host.sh` must keep `native_host_wip.sh`; wake/Reload in Comet — do not `launch-wip-chrome` to fix Comet.

## Ports (local)

| Service | URL |
| --- | --- |
| AadhaarChain web (legacy host UI) | http://127.0.0.1:43100 |
| Gateway + AgentGuard | http://127.0.0.1:43101 |
| ONDC Buyer | http://127.0.0.1:43102 |
| ONDC Seller | http://127.0.0.1:43103 |
| FlatWatch API / web | http://127.0.0.1:43104 / `:43105` |
| Solana validator (optional, not AG) | http://127.0.0.1:8899 |

## What is real vs stubbed (reconciled 2026-07-25)

| Subsystem | Status |
| --- | --- |
| AgentGuard domain (evaluate / consume / pause / receipts) | **Real** — principal-scoped PostgreSQL mandates, decisions, approvals, execution intents and receipts when `DATABASE_URL` selects CF1 persistence; local-file mode is the exclusive development fallback, not a concurrent owner |
| ONDC Seller AgentGuard UI | **Real** — refund demo + `/agentguard` |
| Buyer AgentGuard checkout | **Real locally on CF1 PostgreSQL** — exact landed cost, saved mandate, mutation rejection, two simulated-payment order effects and signed authorization; current-source FQDN/Auth0 Buyer acceptance passed. Public checkout/payment was not claimed |
| CommerceV1 + compatibility exchange | **Real CF1 foundation, partial product lifecycle** — PostgreSQL carts, quotes, inventory, orders, payment attempts, balanced ledger and two full lifecycle/refund cycles; `/api/demo-commerce` is a compatibility adapter, not an independent file store. Multi-seller checkout and settlement remain open |
| Signed receipt verify | **Real locally** — issue/verify and tamper tests plus current-source Buyer/Seller UI verification. FQDN/Auth0 app acceptance passed; receipt verification itself was not re-exercised on FQDN |
| Authenticated principal on AG APIs | **Real** — session cookie principal; body wallet cannot override social/demo session |
| ONDC commerce UI labels | **Demo mode off** — `VITE_COMMERCE_DEMO_MODE=false` (gate evidence 2026-07-12); label **ONDC network**; payment still simulated (not live UPI) |
| Host identity | **Auth0** (FQDN PreProd) + local `AUTH_DEMO_CONTINUE` (Hermes only) |
| ONDC PreProd Beckn (BAP+BPP) | **Real, partial** — the 2026-07-24 PostgreSQL retest proved signed search delivery and correlated signed `on_search`; the Seller had zero published items, so the callback catalog and Buyer results were empty. Historical **select→init→confirm** ACK + `on_*` stubs remain protocol foundation, not current lifecycle acceptance. Production onboarding and official conformance remain open. Matrix: `.agents/skills/testing-ledger/references/preprod-network-matrix.md` |
| Buyer mock grocery fallback | **Removed** when ONDC adapter ready |
| Trust / demo KYC | **Deferred hangar** — not AgentGuard acceptance |
| MeitY DigiLocker / **prod** ONDC / NPCI agent UPI | **Out of scope** — PRODUCTION-READINESS; UPI Circle AI = CUG only |
| FlatWatch AgentGuard / reputation / land | **Non-goal** for Token Nxt |
| Solana / burner wallet for AG | **Non-goal** — hangar only; AG lanes use `sso demo` |

## Host identity (AgentGuard principal adapter)

Buyer/Seller bind AgentGuard to a **server session principal**, not a wallet:

1. **Sign in (Auth0)** → `:43101/api/auth/auth0/start` → cookie `aadharcha_session` with `principal:auth0:…` ([Auth0 Authorization Code Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow))
2. **Optional Google** (legacy direct) → `:43101/api/auth/google/start` → `principal:google:…` (prefer Google as an Auth0 connection)
3. **Demo continue** (local only) → `:43101/api/auth/demo-continue` → `principal:demo:…` — forced off in staging/production unless `AUTH_DEMO_CONTINUE_FORCE=true`
4. App → `GET :43101/api/auth/me` with credentials → `{ principal_id, identity_provider, … }`
5. AgentGuard routes derive principal from the cookie; body `wallet_address` is legacy-only and rejected when it would override a social/demo session

`VITE_IDENTITY_AUTH_ENABLED=true` in both ONDC `.env.local`. Set `AUTH0_DOMAIN` / `AUTH0_CLIENT_ID` / `AUTH0_CLIENT_SECRET` on the gateway for PreProd/prod; `AUTH_DEMO_CONTINUE=true` for local Hermes automation only.

Wallet burner / Solflare SSO remains available for legacy host regression only — **not** AgentGuard acceptance.

## Do not route agents to

- Expanding AadhaarChain as an identity product — see `aadharchain/GOAL.md`
- **Production** ONDC / NPCI claims before milestone 9 + official evidence (PreProd Beckn search ≠ prod)
- Port `3002` / `3000` for ONDC — use `43102` / `43103`
- Production URLs when testing locally
- New parallel auth contracts — evolve `/api/agentguard` per IMPLEMENTATIONPLAN
- FlatWatch AgentGuard or Solana for Token Nxt acceptance
- `../docs/workflow/*` — not in this workspace

## Agent runtime (executor hosts)

Runtime agents **execute app tools** under AgentGuard (IMPLEMENTATIONPLAN M11+).
Chat-only is insufficient for the PreProd executor story.

| Host | Env | Role |
| --- | --- | --- |
| Cursor SDK (text) | Gateway: `CURSOR_API_KEY`, `CURSOR_AGENT_MODEL=composer-2.5`; FQDN `/api/agent/*` on `gateway.aadharcha.in` (Buyer/Seller Vercel rewrite) | Long `delegate_to_runtime_agent` handoff |
| OpenAI Realtime `gpt-realtime-2.1` | Gateway: `OPENAI_API_KEY` (server); ephemeral client secrets for browser | Buyer voice (M12) |
| FlatWatch `:43104` | Local vite proxy only (optional) | Local Cursor SSE when gateway not used |

Set Cursor key in `aadharchain/gateway/.env` (and `flatwatch/backend/.env` for local FlatWatch); restart
`start-dev.sh`. Keep `VITE_AGENT_RUNTIME_ENABLED=true` in ONDC `.env.local`. Leave
`VITE_AGENT_CONTROL_PLANE_URL` empty on FQDN so `/api/agent/*` uses same-origin rewrites → **gateway** (not FlatWatch — FQDN FlatWatch 401s portfolio `X-User-Id`). Loopback `.env.local` bake guarded by `loopback.ts`.
Do **not** force-migrate to OpenAI Agents SDK before the shared tool runner works.
CI: `ondc_ci_graders.py --offline` blocks PR; FQDN soft graders are advisory (`continue-on-error`) — detail in portfolio-deploy `ci-cd.md`.

Shared: `shared/cursor_agent_runtime/`, `shared/trust-client/` (host assurance helpers during migration).
AgentGuard APIs on `:43101` remain the sole authorization boundary.
