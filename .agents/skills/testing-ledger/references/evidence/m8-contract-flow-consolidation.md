# Milestone 8 contract and visible-flow consolidation

Date: 2026-07-16

## Final-source proof

The Buyer and Seller clients now consume the shared AgentGuard contract types
for actions, agents, mandates, approvals, and intent receipts. The displaced
standalone `/agent` routes, navigation entries, page implementations, and staged
handoff storage were removed; the global Samantha orb remains the single visible
assistant surface in each app. Judged Hermes scripts contain no AgentGuard API
shortcut for protected actions.

| Gate | Result |
| --- | --- |
| Buyer deterministic | **Pass** — 21 files / 131 tests; typecheck and production build pass |
| Seller deterministic | **Pass** — 13 files / 162 tests; typecheck and production build pass |
| Gateway deterministic | **Pass** — `./scripts/verify-portfolio.sh --ci`, 86 tests |
| Contract search | **Pass** — `AgentGuardAction` and `IntentReceipt` are shared owners; the remaining Seller local action vocabulary is a dated legacy compatibility adapter |
| Judged-flow shortcut search | **Pass** — no AgentGuard evaluate/consume/pause/mandate API calls in Buyer, Seller, or two-sided Hermes scripts |
| Browser closeout | **Pass** — WIP bridge ready; left at Buyer search |

## Consecutive visible passes

| Run | Server identity | Retained captures |
| --- | --- | --- |
| `m8-contract-final-1784209300-a` | order `order_47aa87015f8f40ec`; transaction `txn_a9607f26c37c4315`; issue `issue_6ff48b295bd64728` | `m8-contract-flow-consolidation/run-a-seller-catalog.jpeg`, `run-a-seller-order.jpeg`, `run-a-buyer-order.jpeg` |
| `m8-contract-final-1784209301-b` | order `order_070f0ce5a9274463`; transaction `txn_8b9c603db3d04b5c`; issue `issue_46a0ee83c93d45d9` | `m8-contract-flow-consolidation/run-b-seller-catalog.jpeg`, `run-b-seller-order.jpeg`, `run-b-buyer-order.jpeg` |

All six captures were opened and visually accepted. Seller catalog, Seller
order, Buyer order, payment, receipt, and support identities agree per run. Both
apps show Samantha as the global orb without a competing standalone agent link.
