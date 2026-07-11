# AadhaarChain Portfolio — Agent Control Surface

Read this file first. Repo-local `AGENTS.md` files add app-specific detail only.

**Product hierarchy:** AadhaarChain trust substrate → AgentGuard (flagship) → ONDC Seller first → Buyer / FlatWatch. Thesis: [`PRODUCTIDEA.md`](PRODUCTIDEA.md). Per-app owners: `*/GOAL.md`.

## Workflow hardening gate (read before changing scripts)

```
1. Make it work   — one manual end-to-end success
2. Validate       — repeat manually; write preconditions + pass signals
3. Simplify       — ONLY NOW remove duplicate entry points / prose
4. Optimize       — bookends, retries, timings (from failed/slow manual runs)
5. Automate       — wrapper scripts last
```

**Do not simplify or remove steps until phase 2 is done** (two consecutive manual passes, documented in `validation-ledger.md`). Fixes discovered during manual runs (wrong URL, missing wait) are validate-phase fixes — not simplification.

**Friction closeout:** improvised recovery during verify/browser ⇒ encode before done (`~/.codex/AGENTS.md` AFTER + `workflow-hardening`). Example: `:8899` → `ensure-validator.sh`.

## First commands (manual lanes)

```bash
# 0. First-run setup (fresh clone or missing deps)
./scripts/setup.sh   # then ./scripts/start-dev.sh only if :43100–43105 are not all 2xx

# 1. Portfolio API lane (stack if needed + gateway pytest)
./scripts/verify-portfolio.sh

# Manual split: ./scripts/start-dev.sh then cd aadharchain/gateway && .venv/bin/python -m pytest tests/ -q

# 2. Optional: local Solana validator (on-chain lane only)
./aadharsolana/scripts/start-validator.sh
cd aadharsolana && ./scripts/validate-onchain.sh
```

Restart ONDC buyer/seller dev servers after changing `.env.local` (Vite reads env at startup).

## Portfolio browser (validated lane)

Bookends + pass signals — see `.cursor/skills/portfolio-browser/SKILL.md`.

```bash
# Full lane — preflight auto-starts stack; one preflight for smoke+sso+closeout
python3 scripts/portfolio_browser.py lane burner seller

# Or API + browser wrapper
./scripts/verify-portfolio.sh --browser

# Parallel multi-app smoke (WIP Hermes only — 0-token scout)
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
python3 scripts/parallel_smoke_wip.py
```

**Trigger:** parallel apps / cheaper scouts / console triage → skill **Multi-app orchestration** (script scout → mini fixer; SSO stays mutex). Portfolio browser uses **WIP Hermes only** (never `~/.codex` / `~/.hermes` live).

**Validated fixes (from manual runs):** preflight auto-starts `start-dev.sh` when stack is down; HTTP retries 30s; burner SSO auto-`ensure-validator.sh` (`getHealth` on `:8899` — do not improvise `pkill`/ledger wipe); `lane` avoids triple preflight.

Validation ledger: `.cursor/skills/portfolio-browser/references/validation-ledger.md` (includes scaffolded lanes: onboarding, Solflare SSO, first-run setup, elevated commerce).

## Ports (local)

| Service | URL |
| --- | --- |
| AadhaarChain web | http://127.0.0.1:43100 |
| AadhaarChain gateway | http://127.0.0.1:43101 |
| ONDC Buyer | http://127.0.0.1:43102 |
| ONDC Seller | http://127.0.0.1:43103 |
| FlatWatch API | http://127.0.0.1:43104 |
| FlatWatch web | http://127.0.0.1:43105 |
| Solana validator (optional) | http://127.0.0.1:8899 |

## What is real vs stubbed (2026-07)

| Subsystem | Status |
| --- | --- |
| Identity anchor + verification state | **Real** — file-backed `aadharchain/gateway/data/gateway-state.json` |
| Trust read API | **Real** — `GET /api/identity/{wallet}/trust` |
| Aadhaar eKYC | **Active:** local demo + Setu.co sandbox (`SETU_EKYC_*`). **Paused:** MeitY API Setu / DigiLocker (skill `apisetu-partner-onboarding`). See `PRODUCTION-READINESS.md` |
| Portfolio SSO | **Real** — proof-token `sso_login` → `aadharcha_session` cookie → `/api/auth/me` |
| Login page | **Real** — `http://127.0.0.1:43100/login?return=…&aud=ondcbuyer\|ondcseller` |
| On-chain identity writes from gateway | **Flagged** — `SOLANA_ON_CHAIN_ENABLED=true` + oracle key; see `./scripts/verify-solana.sh` |
| ONDC commerce (search/cart/orders) | **Stubbed** — `VITE_COMMERCE_DEMO_MODE=true`; protocol scaffold in `ondcbuyer/src/lib/ondc/` |
| Like-minded app SSO | **Out of scope** — not in this workspace |
| `aadharsolana` programs | **Separate stack** — not wired to portfolio gateway yet |

## SSO flow (ONDC buyer + seller only)

1. App header **Login with AadhaarChain** → `:43100/login?return=<app-url>&aud=ondcbuyer|ondcseller`
2. Connect wallet → issue proof-token (`purpose: sso_login`) → **Phantom signMessage** (manual)
3. Verify with `credentials: include` → gateway sets cookie on `:43101`
4. Redirect back → app calls `GET :43101/api/auth/me` with credentials

Local dev requires `VITE_IDENTITY_AUTH_ENABLED=true` in `ondcbuyer/.env.local` and `ondcseller/.env.local`.

Elevated actions (checkout, catalog publish) still need **verified** trust + separate proof-token (`buyer_checkout_identity_proof`, etc.) — not the SSO cookie alone.

## Portfolio browser test order

Validated lane (agents):

```bash
python3 scripts/portfolio_browser.py lane burner seller
```

Extended manual order (onboarding + trust):

1. **Lane** — `lane burner seller` (or step through preflight → smoke → sso → closeout)
2. **Onboarding** — `:43100/verify` (anchor → upload → status wizard)
3. **Trust shortcut** — `POST :43101/api/identity/dev/fixtures/{wallet}` with `{"fixture_state":"verified","document_type":"aadhaar"}`
4. **Post-login** — trust chip, demo cart/catalog

Record results in `validation-ledger.md`.

## Do not route agents to

- `../docs/workflow/*` — not present in this workspace; use this file instead
- Port `3002` / `3000` for ONDC apps — use `43102` / `43103`
- Production URLs (`aadharcha.in`) when testing locally — use loopback env vars
- Building new auth endpoints — SSO reuses existing proof-token issue/verify + cookie

## Agent runtime (Cursor SDK only)

Portfolio AI runs through the **Cursor SDK** (`cursor-sdk`) using your Cursor subscription API key.

| App | Runtime host | Env |
| --- | --- | --- |
| AadhaarChain gateway agents | `:43101` | `CURSOR_API_KEY`, `CURSOR_AGENT_MODEL=composer-2.5` |
| FlatWatch chat + ONDC agent pages | `:43104` | `CURSOR_API_KEY`, `CURSOR_AGENT_MODEL=composer-2.5` |

Create `CURSOR_API_KEY` at [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations). Set it in `aadharchain/gateway/.env` and `flatwatch/backend/.env`, then restart `./scripts/start-dev.sh`.

ONDC buyer/seller proxy `/api/agent/*` → FlatWatch `:43104`. Keep `VITE_AGENT_RUNTIME_ENABLED=true` in ONDC `.env.local`.

Shared module: `shared/cursor_agent_runtime/`.

## Shared package

`shared/trust-client/` — trust reads and identity proof helpers for ONDC buyer/seller.

`shared/cursor_agent_runtime/` — Cursor SDK policy, streaming, and one-shot prompt helpers for gateway + FlatWatch control plane.
