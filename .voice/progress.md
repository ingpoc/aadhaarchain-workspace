# Current execution ledger

## Scope

Final local visible Buyer, Seller, two-sided, and combined UX acceptance; the
bounded PreProd Gate 1 search closure and Gate 2 logistics decision; and the
dedicated public LBNP onboarding endpoint, PreProd registration, and bounded
Gate 3 official Workbench Immediate Delivery forward lifecycle. One synthetic
PreProd mock order completed inside Workbench; no real logistics order,
production-money, physical shipment, physical-microphone, pilot, spend,
report-generation, later-gate, or Milestone 9 certification claim is added.

## Current milestone

`preprod-gate-3-logistics-conformance`: **passed**. Gate 1 and Gate 2 remain
frozen. Official Workbench session
`PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT` is configured as `ONDC:LOG10` `1.2.5`,
Logistics (P2P), BAP, PRE-PRODUCTION. Corrected transaction
`900b80c1-72a6-430e-8e64-bed93d971a5b` completed all 15 expected steps through
the final unsolicited `on_status`. All 15 Workbench records ACKed, missed and
extra steps are empty, and the public LBNP gateway signature-verified all 10
callbacks from `workbench.ondc.tech` at `1.2.5`.

## Current evidence

- PostgreSQL access was restored without exposing the credential; the gateway
  is healthy with `persistence_backend: postgres`.
- Frozen source `bf4c7cee...` completed two bundled-Chrome Buyer passes on the
  same temporary INR 89 listing. Quantity controls proved `1 -> 2 -> 1`; both
  exact quotes used the saved INR 10000 shopping mandate:
  - order `83A97020`, authorization `2F48D8C7`;
  - order `709D9B9E`, authorization `C1C66BCF`.
- Both orders showed simulated payment success and verified signed Buyer
  authorization. Seller then drove each order through Pending -> Accepted -> In
  progress -> Dispatched -> Delivered -> Cancelled and Paid -> Refunded.
  Refund references `AB167E21` and `4DA37A95` plus signed receipt IDs survived
  reload. The final queue showed exactly two Cancelled/Refunded orders.
- Combined Buyer/Seller visible review has no unresolved P0/P1. Evidence is in
  `.session/evidence/local-visible-bf4c7cee473643d3f035884a172610beb29e716387d273e26d5ce22fc170d680/`.
- Cleanup exposed one isolated PostgreSQL response-shape defect in protected
  catalog archive. Candidate `923e1113...` repairs the direct-versus-wrapped
  item shape and adds a live PostgreSQL publish/archive regression. Under the
  session-orchestrate targeted-rerun rule, the unaffected two-pass order/refund
  evidence is retained and only the affected archive lane was rerun.
- On `923e1113...`, the protected Chrome archive returned 200; after reload the
  Seller catalog shows zero visible products, BPP reports
  `published_item_count: 0`, and campaign reservations are `held: 0`,
  `consumed: 2`, `released: 2`.
- On live gateway commit `5431307...`, the deployed Seller catalog's protected
  AgentGuard publish created the approved `Sampoorna Whole Wheat Atta 1kg`
  listing; BPP status reported `published_item_count: 1`.
- Exactly one signed `atta` search, transaction
  `00fda29f-947d-4e42-89b9-b98b38c96ad6`, received registry `SUBSCRIBED`,
  gateway + Seller ACK, three delivered outbox records, and a correlated
  Seller `on_search` containing the approved item. Gate 1 passed. Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate1-search-20260725-213218.json`.
- Gate 2 source reconnaissance found only Retail `ONDC:RET10`/`1.2.0`; no
  Logistics domain or public logistics mutation route exists. The official
  B2C Logistics contract is `ONDC:LOG10`/`1.2.5`, with the Retail Seller NP as
  LBNP/BAP and the external LSP as BPP. The bounded role, version, scope, and
  ownership decision passed without an external call. Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate2-logistics-decision-20260726.json`.
- Gateway commit `b3e81b2e...` adds only the third onboarding identity:
  `ondclbnp.aadharcha.in`, callback
  `https://ondclbnp.aadharcha.in/ondc`, `ONDC:LOG10`, target `1.2.5`, and the
  advertised-only `1.2.0` response rule. No Retail Buyer/Seller app source,
  keys, catalog, or callback changed.
- A distinct gitignored LBNP Ed25519/X25519 pair exists. The generator's
  reproducible `0644` private-PEM defect is fixed at its owner with a `0600`
  postcondition; both new private files now read `0600`. Gateway tests passed
  `233 / 50 skipped`; portfolio CI and Buyer/Seller test+build passed. Local
  status/site verification returned 200, and a valid deterministic
  `on_subscribe` challenge returned 200.
- Exact deploy `dep-d9itdcjeo5us73ag2v30` is live on the existing Render Free
  gateway. Its second included custom domain is verified; GoDaddy owns the
  `ondclbnp` CNAME to the existing Render target. Public DNS and TLS pass.
- Public LBNP status, site verification, and a valid challenge/answer callback
  each returned 200. Status read back the isolated env-backed LBNP keys and
  exact LOG10 contract. Existing Retail Buyer/Seller status and site
  verification remained 200; Gate 1 was not rerun. Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate2-lbnp-endpoint-migration-20260726.json`.
- Portal profile `15462-10220` visibly reads Logistics (B2C), API v1.2, Buyer
  NP. The latest operator-generated modal pair and key ID
  `9e7388f4-c68e-4006-ac5a-e7517382999f` were securely materialized and deployed.
  Public status/site verification/challenge and Retail non-regression passed.
  The operator submitted the 1.a modal; reload persisted `Completed` at
  03:15 PM. Although the portal's List of Requests remained empty, one exact
  registry lookup returned HTTP 200 and `SUBSCRIBED` with matching identity,
  key ID, callback, domain, role, city wildcard, and public keys. The visible
  Workbench banner applies to later protocol/conformance work, not this gate.
  Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate2-lbnp-portal-registration-20260726.json`.
- The current ONDC Logistics v1.2.5 contract makes `ONDC:LOG10` the P2P
  domain and Immediate Delivery the bounded baseline. One signed PreProd search
  (`332b7622-458f-4855-8197-d1c331da4dfe`) received seven correlated
  `on_search` callbacks. The selected registered BPP `ondc.bringg.space`
  advertised `1.2.5`, Immediate Delivery, P2P, one INR 59 forward quote, and
  no enhanced feature list. The currently deployed callback owner did not
  verify or record the inbound signature, so this is discovery evidence only.
- Gateway commit `69bf9ad` now exposes only the dedicated LBNP
  `search/init/confirm/update/status/track` path, reuses the durable
  inbox/outbox, rejects Retail `select` and non-Immediate scope, verifies LOG10
  callback signatures against current registry keys, and enforces the
  advertised-only 1.2.0 rule. The third-party lookup caller-key contamination
  defect also has a regression. Gateway tests passed `236 / 50 skipped`;
  focused ONDC tests passed `12 / 15 skipped`. PostgreSQL role-aware test
  doubles were corrected in `cde2242`; the exact nested CI and full deployment
  grader gate passed. Render Free deploy `dep-d9iun27aqgkc73an2cpg` is live,
  and DNS/TLS/status/site/challenge re-proof passed.
- Signed transaction `AA79565B-3815-4D2E-A63A-D8CA8F9E70C5` received three
  signature-verified `on_search` callbacks. Pramaan mock and TapTap both ACKed
  `init` and returned signature-verified `on_init`, but neither included the
  current contract's mandatory inline rider check. The flow stopped before
  `confirm`; no CommerceV1 fulfilment, payment, shipment, or later action was
  mutated. Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate3-logistics-conformance-20260726.json`.
- On 2026-07-31 the operator completed portal 1.b. Portal readback showed the
  four verification tasks, and 2.d opened the official ONDC Workbench with BAP
  and PRE-PRODUCTION preselected. The subscriber URL was entered, but bundled
  Chrome control repeatedly timed out while selecting `ONDC:LOG10`; no
  Workbench session, report, observability token, or protocol call was created.
- The recovered official Workbench session started one Immediate Delivery
  flow. Its first signed search exposed mandatory non-empty future-dated
  `provider.time.schedule.holidays`; the gateway owner now rejects missing,
  empty, malformed, and past-only values. After explicit operator authorization
  for the synthetic `accept_bpp_terms=yes` field, the same frozen transaction
  completed `confirm/on_confirm`, ready-to-ship `update/on_update`, five
  unsolicited `on_status` callbacks, and `track/on_track`. All 15 Workbench
  records ACKed with no missed or extra steps; public inbox rows `8668` through
  `8868` contain 10 callbacks from `workbench.ondc.tech`, all at `1.2.5` with
  `signature_verified: true`. Evidence:
  `.agents/skills/testing-ledger/references/evidence/preprod-gate3-workbench-20260731.json`.
- Exact gateway commit `63df7ca73faa6096961d9cf1333bc9e2387f5770`
  contains only the holiday validator and its deterministic regression. Gateway
  tests passed `236 / 50 skipped`, Buyer tests passed `201` plus build, Seller
  tests/build and portfolio CI passed, and Ruff passed. Render Free deploy
  `dep-d9mna2942hec73e3eq40` is live. GoDaddy CNAME, TLS, dedicated LBNP status,
  site verification, valid/invalid `on_subscribe`, and public empty/past holiday
  422 checks all passed without rerunning Gate 1.
- The testing-ledger validator's `gateway_tests_present` check no longer reports
  a false failure in Codex worktrees where the intentionally ignored nested
  gateway is absent. The existing grader now prefers the current checkout and
  falls back only to another declared Git worktree; its deterministic self-test,
  offline grader, and full testing-ledger validator pass.

## Current blocker

None within Gate 3. Production onboarding, real shipment/payment, Workbench
report generation, and every later gate remain outside this authorization.

## Single next action

Stop this gate and preserve its evidence. Any Workbench report or later gate
requires a separately owned scope; do not repeat the completed transaction or
Gate 1 search.
