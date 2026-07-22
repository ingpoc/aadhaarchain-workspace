# PreProd ONDC network matrix (real data — no mock)

**Currency boundary (2026-07-22):** the latest deployed PreProd evidence in
this ledger is the 2026-07-16 row. The CF1 PostgreSQL source validated locally
on 2026-07-22 was not deployed or revalidated through FQDN/Auth0. Do not use
this matrix to claim current-source production ONDC, live payment, or official
conformance; current local customer evidence lives in
[`matrix-status.md`](matrix-status.md).

**Policy:** `ONDC_ENABLED` may be true on gateway. Flip `VITE_COMMERCE_DEMO_MODE` only with [`commerce_demo_mode_gate.py`](../../../../scripts/commerce_demo_mode_gate.py) evidence (unlocked 2026-07-12 evening — see ledger).

**Smoke:**
```bash
python3 scripts/ondc_preprod_smoke.py --base https://gateway.aadharcha.in --search atta --order
# Free wake: POST /api/ondc/bpp/ensure-demo-item (also runs on gateway lifespan when ONDC_ENABLED)
```

| ID | Check | Pass signal |
| --- | --- | --- |
| P-STATUS | `GET /api/ondc/status` | `enabled:true` `configured:true` signing_key_present |
| P-LOOKUP | `POST /api/ondc/lookup` Buyer `ondcbuyer.aadharcha.in` | HTTP from registry with signed auth (not `1020` auth missing) |
| P-LOOKUP-S | Lookup Seller `ondcseller.aadharcha.in` | Same |
| P-SEARCH | `POST /api/ondc/search` query Atta/marker `ONDC:RET10` city `std:080` | Dispatched; ack ACK or documented NACK body |
| P-ONSEARCH | Poll `GET /api/ondc/catalogs?transaction_id=` (prefer `ondcseller.aadharcha.in`) | ≥1 network item **or** empty with gap note (timeout/city/domain/fanout) |
| P-REWRITE | `POST https://ondcbuyer.aadharcha.in/ondc/on_search` | Reaches gateway ACK JSON — not SPA HTML |
| P-UI | Buyer `search_catalog` with adapter ready | `source: ondc-network` — never `mock` |

## Session ledger

| Date | Result | Evidence | Gaps |
| --- | --- | --- | --- |
| 2026-07-12 | **Pass** P-STATUS/LOOKUP/SEARCH/ONSEARCH/REWRITE | [`evidence/preprod-network-20260712.json`](evidence/preprod-network-20260712.json) | (superseded by evening flip) |
| 2026-07-12 | **Pass** Seller BPP + Buyer sees us on network | [`evidence/preprod-seller-bpp-20260712.json`](evidence/preprod-seller-bpp-20260712.json) | Fanout variance on some queries (banana) |
| 2026-07-12 evening | **Pass** demo mode off + select→init→confirm | [`evidence/commerce-demo-mode-gate-20260712.json`](evidence/commerce-demo-mode-gate-20260712.json) + [`evidence/demo-mode-off-select-confirm-20260712.json`](evidence/demo-mode-off-select-confirm-20260712.json) | PreProd only; payment simulated (not live UPI); UI checkout thin vs API proof; network Atta fanout still variable |
| 2026-07-12 night | **Pass** boot ensure `067ec32` + console harden | [`evidence/console-inventory-before-20260712-200618.json`](evidence/console-inventory-before-20260712-200618.json) → [`evidence/console-inventory-after-20260712-201123.json`](evidence/console-inventory-after-20260712-201123.json); [`evidence/prove-atta-select-confirm-retry-20260712.json`](evidence/prove-atta-select-confirm-retry-20260712.json); [`evidence/seller-catalog-diag-20260712-201242.json`](evidence/seller-catalog-diag-20260712-201242.json) | Buyer results UI may still be loading at 5s (poll ≤20s); Free 503 mid-poll intermittent; no live UPI |
| 2026-07-16 | **Pass** fail-closed public search + item/provider/quantity/quote-consistent select→init→confirm on gateway `099a93d` | [`evidence/preprod-order-consistency-20260716.json`](evidence/preprod-order-consistency-20260716.json) | PreProd only; payment state simulated, not live UPI |

## Historical deployed protocol status (2026-07-12 night; latest row 2026-07-16)

| Step | Status |
| --- | --- |
| search / on_search | **Live** PreProd |
| select / init / confirm (+ on_*) | **Wired** gateway ≥`067ec32` — boot ensure + API ACK path proven |
| `VITE_COMMERCE_DEMO_MODE` | **false** on Vercel Hobby; loopback `.env.local` bake guarded at runtime |
| Production ONDC / live UPI | **Out of scope** |

- Auth header / uk_id mismatch
- bap_uri callback not reachable (Vercel rewrite)
- City code / domain empty catalogs
- Gateway NACK schema
- Free cold-start timeout before on_search
