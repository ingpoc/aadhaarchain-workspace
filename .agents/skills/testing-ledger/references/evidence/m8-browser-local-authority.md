# Milestone 8 browser-local authority proof — 2026-07-16

## Failed diagnostic run

- `m8-visible-1784208100-a`: API lifecycle and Seller UI passed; Buyer UI failed because Seller demo SSO replaced the Buyer audience cookie and the running gateway had not loaded the new Buyer issues route. The lane was fixed to authenticate immediately before each app capture, then the stack was restarted through `scripts/start-dev.sh`.

## Accepted runs

| Run | Item | Order | Transaction | Issue | Result |
| --- | --- | --- | --- | --- | --- |
| `m8-visible-1784208200-a` | `item_db254a79fda946c4` | `order_046194d8c55b46e5` | `txn_7c370c1c44094790` | `issue_b2b3839a03174e14` | Pass |
| `m8-visible-1784208201-b` | `item_80808eab073b43ad` | `order_e5539c89c77b4593` | `txn_26866a2a067a46a0` | `issue_6ec0143760424ab3` | Pass |

Both runs passed Seller publication, Buyer search/checkout, Seller order visibility and acceptance, Buyer issue creation, Seller issue response/remedy, and visible Buyer/Seller identity checks. Every screenshot below was opened and visually accepted.

### Run A screenshots

- `m8-browser-local-authority/m8-visible-1784208200-a-seller-catalog.jpeg`
- `m8-browser-local-authority/m8-visible-1784208200-a-seller-order.jpeg`
- `m8-browser-local-authority/m8-visible-1784208200-a-buyer-order.jpeg`

### Run B screenshots

- `m8-browser-local-authority/m8-visible-1784208201-b-seller-catalog.jpeg`
- `m8-browser-local-authority/m8-visible-1784208201-b-seller-order.jpeg`
- `m8-browser-local-authority/m8-visible-1784208201-b-buyer-order.jpeg`

## Deterministic proof

- `./scripts/verify-portfolio.sh`: 86 gateway tests passed.
- Gateway targeted commerce + AgentGuard: 15 tests passed.
- Buyer: 23 files / 143 tests passed; production build passed.
- Seller: 13 files / 162 tests passed; production build passed.

No deployment, spend, Milestone 9 work, or physical microphone claim was made.
