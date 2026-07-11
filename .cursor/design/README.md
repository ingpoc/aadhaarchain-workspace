# UX simplification design package

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
