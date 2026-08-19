# Historical UX simplification package

Retained visual evidence from the July 2026 simplification pass. It is not a
current design or readiness owner. Use `.session/docs/DESIGN.md` for design and the
testing ledger for current acceptance.

Machine-readable validation: [`ux-validation-ledger.json`](ux-validation-ledger.json)

## Mockup index

| App | Count | Directory |
|-----|-------|-----------|
| AadhaarChain | 11 | [`mockups/aadharchain/`](mockups/aadharchain/) |
| ONDC Buyer | 8 | [`mockups/ondcbuyer/`](mockups/ondcbuyer/) |
| ONDC Seller | 7 | [`mockups/ondcseller/`](mockups/ondcseller/) |

## Route targets (v1)

- **AadhaarChain:** `/`, `/home`, `/verify`, `/login`, `/apps`, `/activity`, `/settings`
- **ONDC Buyer:** `/search` (+ 7 commerce routes); Agent secondary
- **ONDC Seller:** `/dashboard` (+ 5 routes); Agent secondary

## Validation

Per-page `pass_signals` and `validation_steps` live in the JSON ledger. Manual runs: `pending` → `1 pass` → `2 pass` before automate.
