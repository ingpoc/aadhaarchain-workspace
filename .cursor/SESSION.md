# Session checkpoint — 2026-07-06 (saved 22:45 IST)

Resume here. Follow **workflow hardening**: manual validate (×2) before simplify/automate.

## Goal

Production-ready AadhaarChain: portfolio stack + local Solana validator + gateway on-chain bridge.

## Hardened lanes (empty-iteration met unless noted)

| Lane | Status | Canonical entry |
|------|--------|-----------------|
| Portfolio API | **Hardened** | `./scripts/verify-portfolio.sh` |
| Portfolio browser (burner) | **Hardened** | `python3 scripts/portfolio_browser.py lane burner seller` |
| First-run setup | **Hardened** | `./scripts/setup.sh` → stack URL bookend |
| Identity onboarding | **Validate 2/2** | Hermes `identity-onboarding` flow (~52s/run) |
| Solana anchor validate | **Validate 2/2** | `validate-onchain.sh` on **fresh ledger** |
| Gateway on-chain E2E | **Validate 2/2** | deploy-only → init config → approve smoke (see below) |

## Not yet hardened

| Lane | Blocker |
|------|---------|
| Solflare SSO | Scaffolded — not validated |
| Elevated commerce | Needs Solflare or burner SSO + verified trust browser pass |

## Wave 3 results (2026-07-06 night)

| Step | Result |
|------|--------|
| On-chain E2E | **Done** — deploy ~27s; init config; 2× approve smokes with `chain_transaction_signature` |
| Seller trust chip | **Fixed** — `useSubject` prefers `auth/me` wallet for `useTrustState` |
| Solflare SSO | Pending |
| Elevated commerce | Pending |

## Validate-phase fixes (on-chain)

1. **`skip_preflight=True`** on localnet sends (`init_identity_registry_config.py`, `solana_bridge.py`) — fixes preflight `BlockhashNotFound`.
2. **Persistent background shells** for validator + on-chain gateway (nohup shells die under load).
3. **Wallet airdrop** required before `create_identity` on localnet (rent).
4. Sign create tx with **`tx.message.recent_blockhash`** immediately after API returns unsigned tx.

## Mutex rules

- **Hermes / Chrome:** one browser agent at a time.
- **`:8899` / `.local-validator`:** one on-chain agent at a time; fresh ledger before full `validate-onchain.sh`.

## Known bugs (open)

1. **Ephemeral burner wallet** — fixture on session wallet after SSO as workaround.
2. **Verify stub** — Aadhaar PDF → `manual_review`; fixture required for verified trust.
3. **Gateway on-chain env** — restart gateway with `SOLANA_ON_CHAIN_ENABLED=true` + `ORACLE_PRIVATE_KEY` (not persisted in `.env` by default).

## Wave 4 (next session, sequential)

1. **Solflare SSO** — `python3 scripts/portfolio_browser.py sso solflare seller|buyer`
2. **Elevated commerce** — buyer checkout + seller catalog with verified trust
3. **Optional:** promote `scripts/verify-solana.sh` after one more manual on-chain bookend

## UX simplification (2026-07-06/07) — shipped

| App | Routes | Status |
|-----|--------|--------|
| AadhaarChain | 7 (`/`, `/home`, `/verify`, `/login`, `/apps`, `/activity`, `/settings`) | Implemented + UI polish |
| ONDC Buyer | 8 (Agent secondary) | Implemented |
| ONDC Seller | 7 (Agent secondary) | Implemented |

- Mockups + ledger: `.cursor/design/ux-validation-ledger.json`
- AadhaarChain polish: title, single home CTA, no Localnet on home, `next.config` redirects, prod build green
- **Next:** Hermes identity-onboarding retarget to `/verify`; elevated commerce checkout E2E (buyer `useSubject` fix landed)

## On-chain E2E bookend (validated)

```bash
# Validator — persistent background shell recommended
cd aadharsolana && rm -rf .local-validator && solana-test-validator --ledger .local-validator

# Deploy-only (no anchor test)
anchor keys sync && anchor build && anchor deploy
cp target/idl/identity_registry.json ../aadharchain/gateway/idl/

# Init config
cd ../aadharchain/gateway
export SOLANA_ON_CHAIN_ENABLED=true SOLANA_RPC_URL=http://127.0.0.1:8899
export ORACLE_PRIVATE_KEY=$(.venv/bin/python -c "import json,base58; print(base58.b58encode(bytes(json.load(open('$HOME/.config/solana/id.json')))).decode())")
.venv/bin/python scripts/init_identity_registry_config.py   # Initialized config at …

# Gateway with on-chain bridge (persistent shell)
env PORT=43101 SOLANA_ON_CHAIN_ENABLED=true SOLANA_RPC_URL=http://127.0.0.1:8899 ORACLE_PRIVATE_KEY="$ORACLE_PRIVATE_KEY" .venv/bin/python main.py

# Smoke: airdrop wallet → POST create identity → sign/send create tx → fixture manual_review → approve review
# Pass signal: verification metadata chain_transaction_signature non-null
```

## Key paths

| Area | Path |
| --- | --- |
| Validation ledger | `.cursor/skills/portfolio-browser/references/validation-ledger.md` |
| Init registry config | `aadharchain/gateway/scripts/init_identity_registry_config.py` |
| Solana bridge | `aadharchain/gateway/app/solana_bridge.py` |
| Seller trust fix | `ondcseller/src/hooks/useSubject.ts` |

## Ports

43100 web · 43101 gateway · 43102 buyer · 43103 seller · 43104/43105 FlatWatch · 8899 validator

## Rule for next agent

Per-lane validate ×2 before simplify/automate. Respect Hermes + `:8899` mutex. Ledger is source of truth.
