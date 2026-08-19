# PreProd ONDC network matrix (real data — no mock)

**Currency boundary (2026-08-01):** official Workbench session
`PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT` is the latest Gate 3 evidence. After explicit
operator authorization for the synthetic PreProd `accept_bpp_terms=yes` field,
corrected transaction `900b80c1-72a6-430e-8e64-bed93d971a5b` completed all 15
Immediate Delivery steps from `search` through final unsolicited `on_status`.
All 15 Workbench records ACKed with no missed or extra steps, and the public
LBNP gateway signature-verified all 10 callbacks from `workbench.ondc.tech` at
`1.2.5`. Gate 1 remains frozen.
Do not use this matrix to claim production ONDC, live payment, or official
conformance; the current release checkpoint lives in
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
| 2026-07-24 03:24 UTC | **Blocked** after gateway ACK; no callback | [`evidence/preprod-buyer-search-20260724-032417.json`](evidence/preprod-buyer-search-20260724-032417.json) | Local-file persistence; 12 polls found no correlated `on_search` and no network item |
| 2026-07-24 13:56 UTC | **Blocked** after durable delivery and callback; catalog empty | [`evidence/preprod-postgres-search-20260724-135337.json`](evidence/preprod-postgres-search-20260724-135337.json) | Free PostgreSQL and exact commit `5431307` passed persistence proof; signed `atta` search received gateway + Seller ACK, three delivered outbox records, and a correlated `on_search`, but Seller `published_item_count: 0` left Buyer with no network result |
| 2026-07-25 21:32 UTC | **Pass** Gate 1 signed search with approved Seller item | [`evidence/preprod-gate1-search-20260725-213218.json`](evidence/preprod-gate1-search-20260725-213218.json) | Exact live commit `5431307`; protected Seller publish produced `published_item_count: 1`; one signed `atta` search received registry `SUBSCRIBED`, gateway + Seller ACK, three delivered outbox records, and a correlated Seller `on_search` containing the approved atta. Smoke helper exited 6 from a provider-wrapper filter false negative; persisted transaction evidence is non-empty. No later gate ran. |
| 2026-07-26 09:50 UTC | **Pass** Gate 2 dedicated Logistics Buyer/LBNP PreProd registration | [`evidence/preprod-gate2-lbnp-portal-registration-20260726.json`](evidence/preprod-gate2-lbnp-portal-registration-20260726.json) | Portal profile `15462-10220` persisted 1.a Completed; one exact registry lookup returned `SUBSCRIBED` for `ondclbnp.aadharcha.in`, `ONDC:LOG10`, BAP, `/ondc`, all cities, and the deployed portal key ID. Workbench, 1.b, protocol lifecycle, order, payment, production, and later gates did not run. |
| 2026-07-26 10:32 UTC | **Blocked** Gate 3 Logistics PreProd conformance after provider discovery and local implementation | [`evidence/preprod-gate3-logistics-conformance-preflight-20260726.json`](evidence/preprod-gate3-logistics-conformance-preflight-20260726.json) | Official registry and one signed LOG10 search proved `ondc.bringg.space` as a current SUBSCRIBED BPP advertising `1.2.5`, Immediate Delivery, P2P, and one forward quote. The new dedicated LBNP lifecycle/signature-verification path passes all local gateway tests but is uncommitted and undeployed, so the correlated callbacks are discovery evidence, not signed conformance proof. Exact-commit deployment authorization is next; portal 1.b remains an untouched operator attestation. |
| 2026-07-26 11:33 UTC | **Blocked** Gate 3 after exact deploy and signed `search/init` proof | [`evidence/preprod-gate3-logistics-conformance-20260726.json`](evidence/preprod-gate3-logistics-conformance-20260726.json) | Exact commit `cde2242` is live on Render Free. DNS/TLS/status/site/challenge passed. Search ACKed and three `on_search` callbacks verified against current registry keys. Pramaan mock and TapTap each ACKed `init` and returned signature-verified `on_init`, but neither supplied mandatory `rider_check/inline_check_for_rider=yes`; fail-closed before `confirm`. Workbench remains behind untouched operator task 1.b. |
| 2026-07-31 19:35 UTC | **Blocked** Gate 3 official Workbench entry | [portal ledger](../../../../.cursor/skills/apisetu-partner-onboarding/references/ondc-portal-ledger.md) | Operator-completed 1.b persisted. Verify-build 2.d opened official Workbench with BAP and PRE-PRODUCTION preselected; subscriber URL was entered. Chrome control timed out during `ONDC:LOG10` selection before version/use-case selection or Submit, so no Workbench session, report, token, or protocol call exists. |
| 2026-07-31 20:24 UTC | **Blocked** Gate 3 Workbench at confirm legal boundary | [`evidence/preprod-gate3-workbench-20260731.json`](evidence/preprod-gate3-workbench-20260731.json) | Session `PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT`, `ONDC:LOG10` `1.2.5`, Logistics (P2P), BAP, PRE-PRODUCTION. Corrected transaction `900b80c1-72a6-430e-8e64-bed93d971a5b` has four Workbench ACK records through `on_init`; inbox `8668`/`8669` independently prove both callbacks were registry-matched and signature-verified. Confirm requires `accept_bpp_terms=yes`, so no confirm/update/status/track, payment, shipment, production, or legal action ran. |
| 2026-08-01 04:25 UTC | **Pass** Gate 3 Workbench Immediate Delivery forward lifecycle | [`evidence/preprod-gate3-workbench-20260731.json`](evidence/preprod-gate3-workbench-20260731.json) | Explicit authorization resolved the confirm boundary. The same frozen transaction completed all 15 expected steps; every Workbench record ACKed, all 10 public callbacks were signature-verified at `1.2.5`, and missed/extra steps are empty. Exact holiday-guard commit `63df7ca` is live as Render Free deploy `dep-d9mna2942hec73e3eq40`; DNS/TLS/status/site/challenge and public 422 regression proof passed. No Gate 1 rerun, real payment, real shipment, production, report, or later gate. |

## Last verified deployed protocol status (latest row 2026-08-01)

| Step | Status |
| --- | --- |
| search / on_search | **Gate 1 passed** — latest signed callback was correlated and contained the approved Seller atta |
| select / init / confirm (+ on_*) | **Wired** gateway ≥`067ec32` — boot ensure + API ACK path proven |
| `VITE_COMMERCE_DEMO_MODE` | **false** on Vercel Hobby; loopback `.env.local` bake guarded at runtime |
| Production ONDC / live UPI | **Out of scope** |

- Auth header / uk_id mismatch
- bap_uri callback not reachable (Vercel rewrite)
- City code / domain empty catalogs
- Gateway NACK schema
- Free cold-start timeout before on_search
