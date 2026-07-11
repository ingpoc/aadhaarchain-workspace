# AadhaarChain Portfolio Workspace

Local workspace for the portfolio apps. Product thesis: **AadhaarChain AgentGuard** — see [`PRODUCTIDEA.md`](PRODUCTIDEA.md). Per-app goals: [`aadharchain/GOAL.md`](aadharchain/GOAL.md), [`ondcseller/GOAL.md`](ondcseller/GOAL.md), [`ondcbuyer/GOAL.md`](ondcbuyer/GOAL.md), [`flatwatch/GOAL.md`](flatwatch/GOAL.md).

| App | Directory | Local URL |
| --- | --- | --- |
| AadhaarChain | `aadharchain/` | http://127.0.0.1:43100 |
| ONDC Buyer | `ondcbuyer/` | http://127.0.0.1:43102 |
| ONDC Seller | `ondcseller/` | http://127.0.0.1:43103 |
| FlatWatch | `flatwatch/` | http://127.0.0.1:43105 |
| Aadhar Solana | `aadharsolana/` | Solana/Anchor monorepo (bridge target; not portfolio SoT) |

AadhaarChain gateway (trust producer) runs at http://127.0.0.1:43101. FlatWatch backend runs at http://127.0.0.1:43104.

## Quick start

```bash
chmod +x scripts/setup.sh scripts/start-dev.sh
./scripts/setup.sh
./scripts/start-dev.sh
```

## Repos cloned from ingpoc

- https://github.com/ingpoc/aadhaar-chain → `aadharchain/`
- https://github.com/ingpoc/ondc-buyer → `ondcbuyer/`
- https://github.com/ingpoc/ondc-seller → `ondcseller/`
- https://github.com/ingpoc/flatwatch → `flatwatch/`
- https://github.com/ingpoc/aadhar-solana → `aadharsolana/`

## Shared package

`shared/trust-client/` is the local workspace package used by the ONDC buyer and seller apps for AadhaarChain trust reads and identity proof signing.

## For agents

Read [`AGENTS.md`](AGENTS.md) before browser testing, SSO work, or trust/onboarding changes. It is the current control surface for ports, real vs stubbed behavior, and portfolio test order.

## Local env

Local `.env.local` / `.env` files point all apps at the loopback ports above with `VITE_COMMERCE_DEMO_MODE=true` for buyer and seller. ONDC apps also set `VITE_IDENTITY_AUTH_ENABLED=true` for portfolio SSO in local dev.
