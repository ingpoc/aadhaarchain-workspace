# Current execution ledger

## Scope

Milestone 9 P3: durable PreProd Buyer search/callback proof before lifecycle work.

## Current milestone

Milestone 9, P3 BAP adapter.

## Ordered gates

| Order | Owner | Gate | Required evidence |
| --- | --- | --- | --- |
| 1 | User / Render | Configure a genuinely free PostgreSQL `DATABASE_URL` for `identity-aadhar-gateway-main`. | No paid plan, card, trial, or budgeted resource; deployed status reports `postgres`. |
| 2 | Gateway / verification | Redeploy or restart; prove transaction-filtered persistence across the defined boundary. | Durable outbox and inbox records remain queryable. |
| 3 | Buyer / gateway | Run one frozen-source, low-risk Buyer search. | ACK, outbox, callback window, correlated `on_search`, and Buyer `ondc-network` provenance. |
| 4 | User / Workbench | Use Workbench only through an authenticated user-provided session. | Retail search/`on_search` scenario result, kept distinct from deployed proof. |
| 5 | ONDC PreProd | Diagnose delivery if the callback remains absent. | Gateway fanout/delivery diagnostic for the correlated transaction. |
| 6 | Architecture | Decide P3a logistics domain scope, protocol version, and Buyer/BPP/Logistics Provider roles. | Decision recorded in the protocol owner before P4 lifecycle contracts. |

## Current blocker

The deployed gateway uses local-file persistence; no genuinely free PostgreSQL binding is configured.

## Single next action

User configures the free PostgreSQL binding; then verify deployed PostgreSQL persistence before sending a search.
