# AadhaarChain Portfolio Workspace

**Product:** [AgentGuard](PRODUCTIDEA.md) — humans authorize AI agents for
intent-limited commerce with one-time approval, replay rejection, pause, and
verifiable Intent Receipts.

**Token Nxt local demo:** AgentGuard across **ONDC Buyer + ONDC Seller** (shared
mandate/approval/receipt contract; simulated ONDC exchange and payment until
Milestone 9).

| App | Role | Local URL |
| --- | --- | --- |
| AadhaarChain | Legacy host; AgentGuard gateway lives here | http://127.0.0.1:43100 / `:43101` |
| ONDC Buyer | **Active demo** — shopping agent + guarded checkout | http://127.0.0.1:43102 |
| ONDC Seller | **Active demo** — ops agent + guarded refund/catalog | http://127.0.0.1:43103 |
| FlatWatch | Deferred hangar | http://127.0.0.1:43105 |
| Aadhar Solana | Deferred research; not AgentGuard acceptance | local validator `:8899` |

## Owner docs

| Doc | Owns |
| --- | --- |
| [`PRODUCTIDEA.md`](PRODUCTIDEA.md) | Product thesis |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Shared contracts / protocol |
| [`IMPLEMENTATIONPLAN.md`](IMPLEMENTATIONPLAN.md) | Build milestones |
| [`TESTINGPLAN.md`](TESTINGPLAN.md) | Verification gates |
| [`ondcbuyer/GOAL.md`](ondcbuyer/GOAL.md) / [`ondcseller/GOAL.md`](ondcseller/GOAL.md) | App outcomes |
| [`aadharchain/GOAL.md`](aadharchain/GOAL.md) | Gateway decomposition |
| [`AGENTS.md`](AGENTS.md) | Agent routing / first commands |
| [`PRODUCTION-READINESS.md`](PRODUCTION-READINESS.md) | Ops / KYC / live ONDC later |

## Quick start

```bash
./scripts/setup.sh
./scripts/start-dev.sh
./scripts/verify-portfolio.sh
python3 scripts/portfolio_browser.py agentguard seller --fixture
```

Current validated browser lane is **Seller AgentGuard**. Buyer and two-sided lanes
are required by TESTINGPLAN and not implemented yet.

## Repos

- https://github.com/ingpoc/aadhaar-chain → `aadharchain/`
- https://github.com/ingpoc/ondc-seller → `ondcseller/`
- https://github.com/ingpoc/ondc-buyer → `ondcbuyer/`
- https://github.com/ingpoc/flatwatch → `flatwatch/`
- https://github.com/ingpoc/aadhar-solana → `aadharsolana/`
- https://github.com/ingpoc/aadhaarchain-workspace → workspace scripts / ledger

## For agents

Read [`AGENTS.md`](AGENTS.md) first, then IMPLEMENTATIONPLAN before structural edits.
