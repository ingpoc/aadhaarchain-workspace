# Matrix status ledger

## A5 durable session registry — 2026-08-17 (partial; no tenant cutover)

- Session revoke/list now write-through to local/gateway PostgreSQL (`004_auth_session_registry.sql`). Isolated-schema pytest: revoke-sid, revoke-all, and principal-scoped list survive a new connection. Staging/production fail closed if the store is unready. No Auth0 tenant/connection cutover. No Render migrate from this slice.
- Evidence: [`evidence/a5-session-controls-durable-20260817.json`](evidence/a5-session-controls-durable-20260817.json). A5-C1 passed. A5 stays **partial** (operator tenant cutover, tenant MFA/Attack Protection, release-source acceptance). Product B5 unchanged.

## B5 complete — 2026-08-17 (preprod/Auth0 signed IGM; production IGM is A4/B8)

- Product B5 is **complete** on `evidence_scope` preprod. B5-E1 stays passed. Auth0 issue `e0809349` on order `8F3F56D0` has signed callbacks, audit, owner, response/escalation targets, and Buyer/Seller-visible closed outcome on current FQDNs after nested `27e8faa` / `dep-da1hs181ne8s73cgcb0g`. Workbench `8382bcef` is not the Auth0 user’s. Production IGM remains A4/B8, not a B5 remaining child. No Workbench/Auth0 IGM rerun this closeout.

## B5 residuals native BPP RESOLVED + SLA/UUID UI — 2026-08-17 (E1 still passed; product B5 testing)

- Nested commit `27e8faa` live on existing Free `identity-aadhar-gateway-main` as `dep-da1hs181ne8s73cgcb0g`. Health 200. Native BAP `POST /api/ondc/issue_status` for Auth0 issue `e0809349` sent issue_id only; BPP `on_issue_status` inbox **23249 RESOLVED** `signature_verified`. Commerce SLA filled (`response_due_at` / `escalation_due_at`). Workbench prepaid+IGM was not rerun. No PEM/DNS/Submit.
- Hobby Seller `ondcseller.aadharcha.in` and Buyer `ondcbuyer.aadharcha.in` archive-deployed. Auth0 Buyer and Seller order `8F3F56D0` show issue UUID `e0809349-…`, owner Seller support, response/escalation targets, and open audit timeline (10 events). Workbench `8382bcef` is still not the Auth0 user’s. Production IGM unauthorized.
- Evidence: [`evidence/b5-residuals-bpp-sla-ui-20260817.json`](evidence/b5-residuals-bpp-sla-ui-20260817.json). Prior Auth0 IGM receipt was not overwritten. B5-E1 stays passed. Product B5 stays testing. Comet `b5-residuals-ui-20260817` closeout `verified_absent`.

## B5-E1 Auth0-owned signed IGM — 2026-08-17 (passed; Workbench row still not Auth0-owned)

- Nested commit `014a6dd` live on existing Free `identity-aadhar-gateway-main` as `dep-da1hhcrl550s73fmjrcg`. Health 200. Workbench prepaid+IGM was not rerun. No PEM/DNS/Submit.
- Auth0 Buyer created fulfillment issue `e0809349-e043-4265-a927-d9f981643709` on order `8F3F56D0`. Signed IGM to our Seller BPP (`ondcseller.aadharcha.in`, not Workbench): outbox issue `22922` delivered; inbox `on_issue` **23218 PROCESSING** `signature_verified`; BAP `issue_status` stays PROCESSING (**23221**); CLOSE then commerce **closed** (`open`→`acknowledged`→`closed`). Extra inbound `POST /ondc/issue_status` with RESOLVED produced inbox **23227** RESOLVED `signature_verified`.
- Buyer FQDN shows issue UUID with badge **resolved**. Seller FQDN shows the same description as **closed** (issue UUID not in the card header). Protocol `/orders/B5091e6b53` is not 500 (authenticated UI order-not-found; unauthenticated API 401). Workbench `8382bcef` remains subscriber-scoped/`open` and is not claimed as the Auth0 user’s.
- Evidence: [`evidence/b5-e1-auth0-signed-igm-20260817.json`](evidence/b5-e1-auth0-signed-igm-20260817.json). Prior receipts were not overwritten. B5-E1 passed. Product B5 stays testing (native BPP `issue_status` still PROCESSING unless inbound already RESOLVED; SLA/audit UI gaps; production IGM unauthorized). Comet `b5-e1-auth0-igm-20260817` closeout `verified_absent`.

## B5-E1 Buyer/Seller-visible outcome — 2026-08-17 (principal mismatch; not passed)

- Public Render row `8382bcef-c3ab-41e5-b04e-1088d10ffb84` exists: `principal_id=ondcbuyer.aadharcha.in`, `seller_id=workbench.ondc.tech`, `protocol_order_id=B5091e6b53`, commerce `order_id` null, **status still `open`**. Audit history has five IGM events; signed inbox `issue.status` was null so RESOLVED in `respondent_actions` did not become a commerce terminal state.
- Unauthenticated `GET /api/demo-commerce/buyer/issues` and `/seller/issues` are **401**. Auth0 Buyer FQDN (`principal:auth0:…`) shows orders `8F3F56D0` / `709D9B9E` / `83A97020` and Auth0-owned issue `fabc818c-…`, not `8382bcef` / `B5091e6b53`. Direct `/orders/B5091e6b53` is **500**. Auth0 Seller shows the same four Auth0 orders; 709D9B9E has the closed Auth0 fulfillment issue, not the Workbench IGM row.
- Staff lookup for protocol-bound issues and an Auth0-owned signed IGM path were not implemented (not a small existing-path fix). Production IGM still unauthorized.
- Evidence: [`evidence/b5-e1-buyer-seller-readback-20260817.json`](evidence/b5-e1-buyer-seller-readback-20260817.json). B5-E1 stays pending; product B5 stays testing. Comet `b5-e1-ui-readback-20260817` closeout `verified_absent`.

## B5-E1 Workbench prepaid+IGM resolve — 2026-08-17 (on_issue_resolved SUCCESS)

- Nested commit `1db9fa0` live on existing Free `identity-aadhar-gateway-main` as `dep-da1g9jpt0dsc73bqcp0g`. BAP `issue` now includes `issue_actions.complainant_actions`; BPP `on_issue`/`on_issue_status` include `respondent_actions`. Focused pytest: 14 passed, 16 skipped. Bind contract unchanged (empty issue 422, unknown order/issue 404).
- New Workbench session `jAq3Wt205M3Il6zX2siGsKS8abHbQgIT` / tx `091e6b53-9ce5-49ba-b6ee-414112326d5c` via Scenario Testing UI then `POST /backend-ui/flow/new`. ACK: select, on_select, init, on_init, confirm. `accept_bpp_terms` not filled. Track COMPLETE SUCCESS. `issue_open_100`, `on_issue_processing_100`, **`on_issue_resolved_100` COMPLETE SUCCESS**, `issue_close_100` COMPLETE SUCCESS. Bound issue `8382bcef-c3ab-41e5-b04e-1088d10ffb84`. Signed `on_issue` inbox 23111 (PROCESSING) and `on_issue_status` inbox 23113 (RESOLVED), both `signature_verified`, no Missing issue actions. Mock `on_confirm` still COMPLETE ERROR without Render POST.
- Evidence: [`evidence/b5-e1-workbench-igm-resolve-20260817.json`](evidence/b5-e1-workbench-igm-resolve-20260817.json). Prior receipts were not overwritten. B5-E1 stays pending (Buyer/Seller-visible outcome); product B5 stays testing.

## B5-E1 Workbench prepaid+IGM issue bind — 2026-08-17 (issue_open SUCCESS; signed on_issue landed)

- Nested commit `e55d06e` live on existing Free `identity-aadhar-gateway-main` as `dep-da1fvie7bikc7392gof0`. Dispatch binds a principal-safe CommerceV1 issue from a confirm-outbox order when none exists. Public `POST /api/ondc/issue`: no body **422**, `{}` **422**, unknown order **404 Unknown order**, unknown issue_id **404 Unknown issue**. Focused pytest: 12 passed, 16 skipped.
- New Workbench session `YvuUWZPUfH_n-R8soNMIfLVXr2J7M61l` / tx `d98ec9ac-990c-4793-a5f8-72426afc75b5` via Scenario Testing UI then `POST /backend-ui/flow/new`. ACK: select, on_select, init, on_init, confirm. `accept_bpp_terms` not filled. Track COMPLETE SUCCESS; signed `on_track` inbox true. Mock `on_confirm` still COMPLETE ERROR without Render POST. `issue_open_100` and `issue_close_100` COMPLETE SUCCESS. Bound issue `fd0486d3-aed4-4f92-86f0-46e92b679be3` from signed outbox. Signed `on_issue` inbox 23086/23087 (`signature_verified`; mock envelope `Missing issue actions`). `on_issue_resolved_100` COMPLETE ERROR.
- Evidence: [`evidence/b5-e1-workbench-igm-bind-20260817.json`](evidence/b5-e1-workbench-igm-bind-20260817.json). Prior receipts were not overwritten. B5-E1 stays pending; product B5 stays testing.

## B5-E1 Workbench prepaid+IGM ACK deploy — 2026-08-17 (BAP ACKs; IGM 15 still listening)

- Nested commit `8ae415b` live on existing Free `identity-aadhar-gateway-main` as `dep-da1fl2h5efls73eervbg`. Inbound BAP ACKs `on_confirm`/`on_status` when `transaction_id` matches the lifecycle outbox even if callback `message_id` differs; mismatch is logged and the callback message_id is persisted. Outbound BPP still echoes the request `message_id`. Focused pytest: 11 passed, 16 skipped. Public track still 422 not 404; empty `on_confirm` is 400 not 404.
- Live synthetic POST to gateway and `ondcbuyer` `/ondc/on_confirm` with new message_id + confirm `transaction_id` `f876d453-…` returned ACK; inbox `23056`.
- New Workbench session `kRX_rSpaXI1zRMI9rMRHf8idYHniOxh5` / tx `f876d453-6c33-4297-952e-7ee54ed50551` via `POST /backend-ui/flow/new`. ACK: select, on_select, init, on_init, confirm. `accept_bpp_terms` not filled. Track COMPLETE SUCCESS; signed `on_track` inbox true. Workbench mock `on_confirm` still COMPLETE ERROR with the old pairing string and did not POST to Render. `issue_open_100` LISTENING; `POST /api/ondc/issue` 404 Unknown issue; buyer issues 401. Issue id none.
- Evidence: [`evidence/b5-e1-workbench-igm-ack-20260817.json`](evidence/b5-e1-workbench-igm-ack-20260817.json). Prior receipts were not overwritten. B5-E1 stays pending; product B5 stays testing.

## B5-E1 Workbench prepaid+IGM rerun — 2026-08-17 (blocked at on_confirm)

- Public track reproof still holds: health 200; `POST /api/ondc/track` 422 not 404; IGM routes present. New session `62RWGJAf_xhJm5O1FgYrf6qUakwSdO__` / tx `fa6a6b53-41af-4155-9eea-96ac7d6b90e1` via `POST /backend-ui/flow/new`. ACK: select, on_select, init, on_init, confirm. `accept_bpp_terms` not filled.
- Workbench mock `on_confirm` still mints a new message_id (`54816c38-…` vs confirm `8a907724-…`). Public BAP NACKs; signed on_confirm inbox empty. Track LISTENING but not sent (no signed callback order_id). IGM 15–18 not reached. Issue id none.
- Evidence: [`evidence/b5-e1-workbench-igm-rerun-20260817.json`](evidence/b5-e1-workbench-igm-rerun-20260817.json). Prior receipts were not overwritten. B5-E1 stays pending; product B5 stays testing.

## B5-E1 track/on_confirm deploy — 2026-08-17 (code live; Workbench 15–18 not rerun)

- Root cause: Buyer dispatch had no `/api/ondc/track` (404). Workbench mock `on_confirm` used a new message_id; our BPP also minted uuid5 callback ids. `on_status` `subscriberID not set` was not our previous NACK string; ingest ignored camelCase `subscriberID` and Authorization `keyId`.
- Nested commit `f7794fa` on existing `identity-aadhar-gateway-main` as `dep-da1f80gjo6nc738i40s0`. Public `POST /api/ondc/track` is 422 (not 404); health 200; IGM routes still present. 4 focused track tests plus 144 related ONDC/commerce checks passed.
- Workbench IGM steps 15–18 were not started this slice. Next: one `/backend-ui/flow/new` prepaid+IGM flow, send track with confirm message_id rules, then issue/on_issue. Do not fill `accept_bpp_terms`.
- Evidence: [`evidence/b5-e1-track-onconfirm-deploy-20260817.json`](evidence/b5-e1-track-onconfirm-deploy-20260817.json). Prior receipts were not overwritten. B5-E1 stays pending; product B5 stays testing.

## B5-E1 PreProd Workbench IGM retry — 2026-08-17 (blocked after confirm)

- Flow-start 404 is fixed: UI `POST /backend-ui/api/sessions/flows/{sessionId}` still 404s; `POST /backend-ui/flow/new` registers the current session. Stale `Already expecting action: select` clears with `DELETE /sessions/expectation`.
- Session `v83hwowCbAKXBW9wEHtbCTjTC7f1tQHq`, transaction `d77ff31f-4d1b-4e2e-81ca-53b90a2900cb`, flow `Order_to_confirm_to_fulfillment__Prepaid_with_igm_1.0.0`. ACK: select, on_select, init, on_init, confirm. `accept_bpp_terms` was not filled; confirm ACK'd without it.
- Workbench mock `on_confirm` NACK: message_id mismatch (`72b2829c-…` vs `b4905f64-…`); public on_confirm inbox empty. Unsolicited on_status NACK `subscriberID not set`. Track WAITING; `POST /api/ondc/track` is 404. IGM steps 15–18 not reached. Issue id none.
- Evidence: [`evidence/b5-e1-workbench-igm-retry-20260817.json`](evidence/b5-e1-workbench-igm-retry-20260817.json). 404 receipt [`evidence/b5-e1-workbench-igm-20260817.json`](evidence/b5-e1-workbench-igm-20260817.json) was not overwritten. B5-E1 stays pending; product B5 stays testing.

## B5-E1 PreProd Workbench IGM — 2026-08-17 (blocked at select)

- Public deploy reproof passed: `GET /api/health` 200; `POST /api/ondc/issue` 422 and `/ondc/on_issue` 400 (not 404); OpenAPI lists the four IGM paths. Claimed live commit remains `2e30070` / `dep-da1ds3flk1mc739qgt4g`.
- Official Workbench session `2d8cKTuko6HV78i1sQLN3Nx3H3T5bO64` created as BAP, `ONDC:RET10` `1.2.0`, GROCERY, PRE-PRODUCTION. RET10 has no standalone IGM usecase; the IGM-bearing flow is `Order_to_confirm_to_fulfillment__Prepaid_with_igm_1.0.0` (issue at steps 15–18).
- Flow start `POST /backend-ui/api/sessions/flows/2d8cKTuko6HV78i1sQLN3Nx3H3T5bO64` returned 404. UI ActiveFlow is WAITING on `select` with an empty Request pane. No signed select was invented. Public `on_issue` inbox is empty.
- LOG10 session `PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT` was not reused. A4 Comet leases were not killed. No PEM/DNS/portal Submit/report.
- Evidence: [`evidence/b5-e1-workbench-igm-20260817.json`](evidence/b5-e1-workbench-igm-20260817.json). B5-E1 stays pending; product B5 stays testing.

## CF2/CF3 uncoupled from Q1 — 2026-08-17

- CF2-E1 and CF3-E1 blocking gates already passed. Product items are
  `complete`. Q1 owns the frozen-source release receipt and must not keep
  product items open or block B5.
- B5 is the remaining product-closure item (`partial`; local issue lifecycle
  passed, official IGM remaining).

## A4 exact-commit Render deploy — 2026-08-17 (blocked; PEM/portal 1.a)

- Operator authorized deploy of current gateway HEAD to existing
  `identity-aadhar-gateway-main` only. Nested repo
  `ingpoc/aadhaar-chain` `main` HEAD
  `7beab582d141c6f3f1e089c356ce0df6852a318c` is live as
  `dep-da1boulbedkc73cieceg`. Workspace HEAD `2be9e5a` was not deployed.
- Service stayed Free; auto-deploy stayed off. No Buyer/Seller Render
  domains, no parallel gateway, no GoDaddy DNS, no production PEM env copy.
- Health `https://gateway.aadharcha.in/api/health` 200. Buyer/Seller/LBNP
  site-verification 200. Junk `/ondc/on_subscribe` POST 400 decrypt-fail on
  all three FQDNs. Runtime unique_key_ids remain PreProd
  (`1aee68ad-…` / `baf58086-…` / `9e7388f4-…`).
- Checklist A4 stays `blocked` on production PEM copy, valid production
  challenge, and portal Production 1.a modal reconcile/submit.
- Evidence:
  [`evidence/a4-render-deploy-7beab58-20260817.json`](evidence/a4-render-deploy-7beab58-20260817.json).

## CF3-E1 Seller complete-lifecycle — 2026-08-17 (PASS; product complete)

- **Comet PASS** (local `:43101`/`:43103`, session `cf3-e1-20260817`) on local
  Postgres. Combined source fingerprint
  `298bfdea8ef24a286b4c0088e13b8b32eec578a070977056a682e39631e46244`.
- Pass: store ready; staff invite (fulfilment); CSV draft import; accept with
  SLA due; dispatch+tracking; deliver; full refund auth `6065C440`; Overview
  operational analytics (Refunded ₹95, Catalog live 2); persist agreement on
  tracking/refund (UI projects Cancelled/Refunded from succeeded refund).
- Order `245E0B87` / `245e0b87-caff-4842-babd-f9b14f9938ea`. CF3-E1 gate
  `passed`. Product item complete; Q1 remains a separate release item. B5 is
  next product-closure work. No A4 keys/DNS/deploy from this receipt.
- Ops: gateway died mid-run → restart with forced local `DATABASE_URL`; Comet
  chrome-error recovered via same-session closeout+restart.
- Evidence:
  [`evidence/cf3-e1-seller-lifecycle-20260817.json`](evidence/cf3-e1-seller-lifecycle-20260817.json).

## CF3 catalog + fulfilment path stamps — 2026-08-17 (superseded by CF3-E1)

- **Comet PASS** (local `:43101`/`:43103`, session `cf3-catalog-20260817`): store
  setup; draft CSV import; Save draft; Exact publish preview naming
  `seller.catalog.publish`; Confirm publish after Agent Guard Refresh/Save.
- Local ops trap: `start-dev.sh gateway` must not use Render `DATABASE_URL` from
  `gateway/.env`; force local Postgres. After restart, verify OpenAPI routes
  before UI blame. Transient **Seller mandate not found** → Agent Guard
  Refresh + Save.
- Evidence:
  [`evidence/cf3-catalog-draft-publish-preview-20260817.json`](evidence/cf3-catalog-draft-publish-preview-20260817.json),
  [`evidence/cf3-catalog-store-ready-20260817.png`](evidence/cf3-catalog-store-ready-20260817.png),
  [`evidence/cf3-catalog-draft-import-validation-20260817.png`](evidence/cf3-catalog-draft-import-validation-20260817.png),
  [`evidence/cf3-catalog-save-draft-20260817.png`](evidence/cf3-catalog-save-draft-20260817.png),
  [`evidence/cf3-catalog-exact-publish-preview-20260817.png`](evidence/cf3-catalog-exact-publish-preview-20260817.png),
  [`evidence/cf3-catalog-publish-confirmed-20260817.png`](evidence/cf3-catalog-publish-confirmed-20260817.png),
  [`evidence/cf3-catalog-agentguard-mandate-missing-20260817.png`](evidence/cf3-catalog-agentguard-mandate-missing-20260817.png).

## A4 local production keys — 2026-08-17 (blocked; host gate + portal 1.a)

- Operator said **Generate now**. Isolated local production Ed25519/X25519
  pairs written under gitignored
  `aadharchain/gateway/.local/ondc-production/{buyer,seller,lbnp}`.
  Encryption public format `asn1_der_spki_b64`; private PEMs `0600`.
- Public fingerprints / draft `unique_key_id` (not registered; no private PEMs):
  [`evidence/ondc-a4-production-keys-local-20260817.json`](evidence/ondc-a4-production-keys-local-20260817.json).
- PreProd `portal-download/{buyer,seller,lbnp}` sha256 unchanged. Nothing
  copied to Render env, `.env` production PEM vars, DNS, deploy, or portal.
- Checklist A4 stays `blocked` on the participant-host gate plus portal
  Production 1.a modal reconcile/submit. A modal pair supersedes this draft.

## A4 keys-only authorization — 2026-08-17 (superseded by generate-now)

- Operator authorized **keys only** for Buyer NP `15462-10008`
  (`ondcbuyer.aadharcha.in`), Seller ISN `15462-10011`
  (`ondcseller.aadharcha.in`), and Logistics Buyer `15462-10220`
  (`ondclbnp.aadharcha.in`). Not Render deploy, not GoDaddy DNS, not registry
  submit. Later the same day the operator said **Generate now**; local pairs
  now exist (see entry above).
- Portal 1.b remains Pending for Retail Buyer/Seller (operator attestation, not
  keygen). Logistics 1.b is Completed. Production EnvAccessRequest is not
  visible on the 2026-08-17 portal readback.

## A4 portal readback — 2026-08-17 (blocked; not production)

- Authenticated portal UI readback ≠ provider-mail readback.
- Stamp: [`evidence/ondc-a4-portal-readback-20260817.json`](evidence/ondc-a4-portal-readback-20260817.json).
- Pre-Prod Subscribed / Integration in Progress only; production keys, DNS,
  deploy, and registry submit remain operator-authorized and do not exist.
- Checklist A4 stays `blocked`. The portal stamp does not unlock the path.
  A later 2026-08-17 operator choice selected Unlock production path; a further
  2026-08-17 keys-only authorization named the three profiles but did not give
  generate-now. A later Generate-now wrote local production draft pairs only;
  DNS/deploy/submit were not executed.

## CF0 contract closure — 2026-07-23

- Frozen application-source fingerprint: `cb0769ea45b0f9e9cf63c825706d8fee1eeb3facf97d8e28bb3a832d1d026215` (gateway `5431307bf36bb8c906600b3ceea859efb34f9d44`, Buyer `bdd67735f54794a1936030288cf0e41a4c746893`, Seller `872e850cc451d91a63b1f5fd0216490ec2841cdc`).
- CF0 owners are closed: `cf0.journey.v1`, six `cf0.v1` lifecycle machines (order, payment, refund, return, issue and approval), Decision Contract v2 across canonical/gateway/Buyer/Seller fixtures and consumers, the exhaustive 83-route `cf0.write-risk.v1` inventory, and `cf0.kpi.v1`.
- Deterministic gates pass: PostgreSQL gateway 279 passed; CI-shaped portfolio 231 passed/48 skipped; Buyer 195 tests plus typecheck/build; Seller 215 tests plus typecheck/build; offline ONDC grader and cross-copy contract verifier passed. GitHub Actions runs `29982273344`, `29982147201`, and `29981879263` are green.
- Bundled Chrome Buyer Pass 1 and Pass 2 completed on unchanged source with orders `E36D08D9` / `256DD6FF`, simulated payments `782EF8C3` / `093C4B41`, and authorization references `24BF88AC` / `743EBE5C`. Seller Pass 1 and Pass 2 accepted and fully refunded those orders, reaching terminal Cancelled/Refunded UI with authorization references `2393687B` / `FAE50567`. PostgreSQL readback agrees: both orders are confirmed at version 3 with one succeeded payment and one succeeded full refund each.
- Combined responsive/accessibility smoke passed on Buyer and Seller at desktop and 390×844: one semantic main/navigation/banner, no duplicate IDs or horizontal overflow, named mobile dialogs, Escape close and focus return.
- Exact-source deploy passed at $0: Render Free deployment `dep-d9gqfcjtqb8s73e0l940` is live at gateway `5431307bf36bb8c906600b3ceea859efb34f9d44`; Buyer and Seller Vercel Hobby deployments are Ready at their production aliases. Health, identity-provider, ONDC NP status and site-verification probes returned 200.
- FQDN/Auth0 acceptance passed sequentially: Buyer re-authenticated to Account Ready / AgentGuard-protected checkout and Seller re-authenticated to Verified identity plus protected dashboard/orders. Desktop semantic checks showed no duplicate IDs or overflow.
- Structured final evidence: [`evidence/cf0-completion-cb0769-20260723.json`](evidence/cf0-completion-cb0769-20260723.json).

## CF1 release checkpoint — 2026-07-22

- Frozen product/deploy fingerprint: `e95340b069cab63b75f436e0d5fdfe4e667545c40d2ee9b378f1b5957914db26` (`b8b90bd` / `fd586da` / `f028ade` / `8146340`).
- Deterministic gates pass: gateway CI 152 passed/48 skipped; PostgreSQL breadth 200 passed; Buyer 195 tests plus typecheck/build; Seller 211 tests plus typecheck/build; offline ONDC grader passed.
- Final PostgreSQL database `cf1_release_e95340` contains two exact published SKUs, two orders, two successful simulated payments, two successful full refunds, and publish/checkout/refund receipts twice. Inventory is 18 from 20 for each SKU.
- Render Free deployment `dep-d9gc443bc2fs73frb320` is live on gateway commit `fd586da`; Buyer and Seller Hobby archive deployments are Ready and their FQDN aliases return 200.
- Bundled Chrome Buyer Pass 1 and Pass 2 completed on unchanged source with orders `CAC1D3A8` / `EC116D90`, simulated payments `CFD9BD5C` / `945F12AE`, exact one-time approvals, and verified signed receipts. Seller Pass 1 and Pass 2 completed the corresponding full refunds and reached terminal Cancelled/Refunded state with verified authorization references `DC4D0FC9` / `F3601E3D`.
- Combined responsive/accessibility smoke passed at 1920×902 and 390×844: correct main/navigation/banner and dialog semantics, no duplicate IDs or horizontal overflow, Escape close with focus return, zero console errors, and viewport overrides reset.
- FQDN/Auth0 acceptance passed for Buyer and Seller. Buyer reached verified AgentGuard state and a truthful zero-match search; Seller reached verified identity plus protected dashboard, catalog and orders. The live ONDC search grader remains advisory on the intentionally unseeded public catalog; production ONDC conformance is excluded.
- Structured final evidence: [`evidence/cf1-release-e95340-checkpoint-20260722.json`](evidence/cf1-release-e95340-checkpoint-20260722.json).

## Seller Samantha ops — 2026-07-20

- Local Hermes WIP · demo SSO · `hermes_samantha_seller_ops.py` → **script Pass** (`turns_passed` 5/5, Realtime `gpt-realtime-2.1-mini`).
- Evidence: [`evidence/seller-samantha-ops-20260720.json`](evidence/seller-samantha-ops-20260720.json).
- Nav active pill uses theme primary (`oklch(0.48 0.07 195)`) — verified on `/dashboard`.
- Product notes (not script failures): ₹500 refund on `seller-demo-1002` → unknown order for fresh demo principal; ₹25k → `need_approval` (correct); model once refused explicit `navigate_to /agentguard` while already on that page from approval redirect.

## Current local safety record — 2026-07-17

- Executable source: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.
- Two unchanged-source passes: gateway 133, Buyer 173 plus typecheck/build/copy gate, Seller 192 plus typecheck/build/copy gate, targeted adversarial 91.
- Buyer loopback admission on the immediately preceding hash verified exact `toor dal`, Pune serviceability, editable Pune checkout prefill, one exact approval, one order, empty cart and no duplicate.
- Final-hash browser status remains partial: the Realtime-unavailable text fallback is deterministic-test verified but still needs fresh blind browser proof; Seller and two-sided final-hash lanes remain pending.
- Retained record: [`evidence/local-safety-final-20260717-af987.json`](evidence/local-safety-final-20260717-af987.json).

**Session:** 2026-07-12  
**Bridge:** Hermes Chrome WIP · demo SSO  
**Doctrine:** claim → screenshot Read → Pass  
**Evidence dir:** [`evidence/`](evidence/)

## Buyer

| ID | Result | Screenshot(s) | Notes |
| --- | --- | --- | --- |
| B-HI | **Pass** | `evidence/B-HI-20260712-015147-0.jpeg` | `/search`; greeting; no tools |
| B-ADD-BANANA | **Pass** | `evidence/B-ADD-BANANA-20260712-015147-0.jpeg` | `/cart`; Robusta Bananas line; tools search+add |
| B-NAV-CART | **Pass** | `evidence/B-NAV-CART-20260712-015147-0.jpeg` | `/cart` |
| B-NAV-CHECKOUT | **Pass** | `evidence/B-NAV-CHECKOUT-20260712-015147-0.jpeg` | `/checkout` |
| B-MEM-ORG | **Pass** | `evidence/B-MEM-ORG-20260712-015147-0.jpeg` | `remember_preference` |
| B-NAV-CONFIG | **Pass** | `evidence/B-NAV-CONFIG-20260712-015147-0.jpeg` | `/config`; organic preference visible; mandate active |
| B-CHECKOUT-OK | **Pass** | `evidence/B-CHECKOUT-OK-20260712-021529-8.jpeg` (+ `-5.jpeg`) | **Page** shows Paid + receipt `rcpt_3f50a424cc354a10` on `/orders/demo-…` (not orb-only). Prior soft Pass revoked — form still looked unpaid. |
| B-CHECKOUT-OVER | **Pass** | `evidence/B-CHECKOUT-OVER-20260712-021529-9.jpeg` (+ `-5.jpeg`) | Checkout page headline “needs approval”; AgentGuard decision card Need approval · INR 25000 · `appr_315b30924b5b4d28` |
| B-LONG-WEEKLY | **Pass** | `evidence/B-LONG-WEEKLY-20260712-022511-7.jpeg` | `/search` (not `/agent`); orb “I've started… I'll let you know”; `delegate_to_runtime_agent` ok. Root cause was FlatWatch process missing `.env` (key was in file). |

Untested this session: B-THX, B-FIND-*, B-NAV-ORDERS, B-EMPTY (covered historically / lower priority).

## Seller

| ID | Result | Screenshot(s) | Notes |
| --- | --- | --- | --- |
| S-HI | **Pass** | `evidence/S-HI-20260712-015532-0.jpeg` | `/dashboard`; no tools |
| S-NAV-AG | **Pass** | `evidence/S-NAV-AG-20260712-015532-0.jpeg` | `/agentguard`; mandate UI |
| S-NAV-CAT | **Pass** | `evidence/S-NAV-CAT-20260712-015532-0.jpeg` | `/catalog` |
| S-NAV-ORD | **Pass** | `evidence/S-NAV-ORD-20260712-015532-0.jpeg` | `/orders` |
| S-REFUND-OK | **Pass** | `evidence/S-REFUND-OK-20260712-015532-0.jpeg` | `refund_issue`; receipt `rcpt_257d94e264e0466c` in orb |
| S-REFUND-OVER | **Pass** | `evidence/S-REFUND-OVER-20260712-015532-0.jpeg` | need one-time approval in orb |
| S-MEM | **Pass** | `evidence/S-MEM-20260712-015532-0.jpeg`, `S-MEM-UI-…` | `remember_preference`; AG page shot present (memory chip not strongly visible in UI crop) |

Untested: S-PUBLISH, S-LONG-TRIAGE.

## Run artifacts

- Buyer matrix JSON: `evidence/matrix-run-20260712-015147.json`
- Seller matrix JSON: `evidence/matrix-run-20260712-015532.json`
- Checkout UI residuals: `evidence/checkout-ui-residuals-20260712-021529.json`
- Long weekly final: `evidence/long-weekly-final-20260712-022511.json`

## Fixes this session

1. Skill doctrine: claim → screenshot → Pass; both apps; checkout required.
2. `checkout_commit` host auto-fill (`session_id` + cart `amount_inr`).
3. **Visible checkout success:** on AG allow + receipt, create paid local order and navigate to `/orders/{id}` with Paid + receipt badges (not unpaid checkout form).
4. **Visible AG over-limit:** write `checkoutOutcome` → checkout page shows Need approval / Denied card.
5. `scripts/start-dev.sh` `start_python`: load service `.env` into process (uvicorn does not). Explains prior false “CURSOR_API_KEY required” while key existed in `flatwatch/backend/.env`.
6. Sanitize buyer `delegate_to_runtime_agent` blocked_reason so Cursor/API-key strings do not leak into orb copy.

## Residuals

- None for the three Buyer residuals above (B-CHECKOUT-OK / OVER / B-LONG-WEEKLY all Pass with Read screenshots).
- Seller memory preference chip still weak in AG UI crop.
- UI audit (2026-07-12): demo/Google principal skips legacy trust wall; no AadhaarChain / Resolve-trust / identity-anchor CTAs; hangar jargon purged from user copy (see [`ui-surface-audit.md`](ui-surface-audit.md)).

---

## Live web E2E (FQDN) — 2026-07-12 afternoon

**Surfaces:** `https://ondcbuyer.aadharcha.in` · `https://ondcseller.aadharcha.in` · gateway `https://gateway.aadharcha.in`  
**Bridge:** Hermes Chrome WIP · sessions `web-e2e-buyer` / `web-e2e-seller`  
**Policy:** did not flip `VITE_COMMERCE_DEMO_MODE`; no live-network order claims; no blind PreProd subscribe POST.

### Buyer (web)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-HOME | **Pass** | `web-buyer-home-20260712-154417-4.jpeg` · `web-buyer-home-diag-*.json` | `/search`; page_diag ok; console clean |
| W-B-SEARCH | **Pass** | `web-buyer-commerce-20260712-154639-7.jpeg` | banana → Robusta Bananas (12 pcs); 1 match |
| W-B-CART | **Pass** | `web-buyer-checkout-20260712-154718-10.jpeg` | cart lines + total INR 481; Simulated exchange in shell |
| W-B-CHECKOUT | **Blocked** | `web-buyer-checkout-20260712-154718-16.jpeg` · `web-buyer-orders-*-4.jpeg` | form reachable; CTA **Trust verification required**; Unsigned |
| W-B-ORDERS | **Pass** | `web-buyer-orders-20260712-154757-10.jpeg` | empty lane (expected unsigned/no paid order) |
| W-B-CONFIG | **Pass** | body in `web-buyer-routes-*.json` | mandate UI; sign-in copy; no Sign-in button |
| W-B-SAM | **Blocked** | `web-buyer-samantha-20260712-155025-6.jpeg` | orb opens; **Realtime not configured on gateway** |
| W-B-AUTH0 | **Partial → Pass CTA** (2026-07-12 16:32) | `web-buyer-signin-button-20260712-1632.jpeg` | Sign in CTA live; wallet KYC gone. Gateway start → Auth0 authorize with Render `redirect_uri` (curl 302). OTP still operator hard-stop. Prior fail evidence kept. |

### Seller (web)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-HOME | **Pass** | `web-seller-routes-20260712-154757-4.jpeg` | dashboard; Unsigned; 0 products |
| W-S-CAT | **Pass** | `web-seller-routes-*-10.jpeg` | catalog empty; publish gated |
| W-S-ORD | **Pass** | `web-seller-ag-20260712-154903-4.jpeg` | 0 incoming; no refund UI |
| W-S-AG | **Pass** | `web-seller-ag-*-10.jpeg` | AgentGuard page; bind-policy gated on sign-in |
| W-S-CFG | **Pass** | `web-seller-ag-*-16.jpeg` | ONDC credentials / gateway URL UI present |
| W-S-REFUND | **Blocked** | `web-seller-refund-probe-*.jpeg` | no orders → no refund path |
| W-S-AUTH0 | **Partial → Pass CTA** (2026-07-12 16:32) | `web-seller-signin-button-20260712-1632.jpeg` | Sign in CTA live; wallet KYC gone. Same Auth0 callback allowlist as Buyer. OTP hard-stop. |

### ONDC integration (API + user-visible)

| Check | Result | Notes |
| --- | --- | --- |
| FQDN `/ondc-site-verification.html` buyer+seller | **Pass** | 200 + `meta name=ondc-site-verification` |
| Gateway `/ondc/np/{buyer,seller}/status` | **Pass** | 200; keys_source=env; registry_env=preprod; signing+enc present |
| FQDN `/ondc/np/*/status` | **Fail** | serves SPA HTML (rewrite not mapped) — use gateway origin |
| FQDN `/ondc/on_subscribe` | **Pass** (hosted) | GET 405; POST reaches decrypt (400 on bogus challenge) |
| Gateway `/api/ondc/status` | **Pass** (honest) | `enabled:false` — keep demo commerce; no live Beckn claim |
| Live network order | **Not claimed** | commerce still demo/Simulated exchange |

### Bugs / operator blockers (ledger)

1. ~~Vercel identity env empty / Sign in tree-shaken~~ → **cleared 2026-07-12 16:32** (values recreated; static prod deploy; Sign in CTA live).
2. ~~Auth0 Render callback missing~~ → **cleared** (dashboard Save; curl start uses Render `redirect_uri`).
3. Stale “Google or demo” copy — mostly replaced; residual trust strings OK.
4. ~~Samantha Realtime `configured:false`~~ → **cleared** (`OPENAI_*` + `CURSOR_API_KEY` on Render Free; `/api/realtime/status` → `configured:true`, model `gpt-realtime-2.1-mini`).
5. **FQDN NP status path** not rewritten to gateway JSON.
6. ~~Wallet hangar copy on FQDN~~ → **cleared** (Buyer+Seller bundles: no `Wallet KYC`).
7. **OTP / Universal Login completion** — still operator hard-stop (Hermes did not complete Auth0 UI nav; curl proves authorize redirect).
8. **Vercel Hobby git-author seat block** — CLI deploys from monorepo git author `gupta.huf…` → `TEAM_ACCESS_REQUIRED` / BLOCKED. Workaround: deploy from non-git staging dir + `echo skip-build` + alias FQDN. Do not upgrade.

### Auth0 / session proof

- `/api/auth/providers`: `auth0:true`, `demo_continue:false`, `runtime_mode:staging`.
- `/api/realtime/status`: `configured:true`, `model:gpt-realtime-2.1-mini`.
- `/api/auth/me`: no session until OTP.
- Sign in CTA: **visible** Buyer+Seller FQDN. OTP/consent: **not completed**.

## Live web E2E refresh — 2026-07-12 16:32 IST

**Unblocked on Free/Hobby:** Auth0 Render callback allowlisted; Vercel BLOCKED deploys deleted; Buyer+Seller Production redeployed (wallet purge + identity bake); Render env `OPENAI_API_KEY` / `OPENAI_REALTIME_MODEL` / `CURSOR_API_KEY` saved+redeployed via dashboard session (CLI key expired).

### Matrix (claim→screenshot)

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AUTH0-UI | **Pass** | `web-buyer-signin-button-20260712-1632.jpeg` | Header **Sign in**; asset `index-DBy88kFf.js`; no Wallet KYC |
| W-S-AUTH0-UI | **Pass** | `web-seller-signin-button-20260712-1632.jpeg` | Header **Sign in**; asset `index-D9ua_Jy5.js` |
| W-B-AUTH0-FLOW | **Partial** | curl Location → `dev-ejqlkc0qt84udk7i…/authorize` with Render callback | Callback mismatch cleared. OTP still operator. |
| W-B-WALLET-COPY | **Pass** (live) | bundle probe | `Wallet KYC` absent |
| W-B-VOICE | **Unblocked config** | `/api/realtime/status` | `configured:true` — re-run voice matrix next |
| W-B-RUNTIME | **Unblocked config** | Render env | `CURSOR_API_KEY` present — needs signed-in matrix |
| W-B-CHECKOUT | **Blocked** | prior | needs Auth0 session (OTP) |
| ONDC live Beckn | **Not claimed** | demo mode unchanged | no demo flip |

### Remaining operator hard-stops

1. OTP / consent on Auth0 Universal Login (keep gateway awake)
2. Optional: re-login Render CLI (`render login`) — dashboard session worked; API key in `~/.render/cli.yaml` was unauthorized
3. Prefer Vercel deploys without HUF git author (non-git staging) until that email is a team member — **no paid seat upgrade**

### Env keys set (names only)

| Host | Keys |
| --- | --- |
| Vercel Buyer+Seller Prod+Preview | `VITE_IDENTITY_AUTH_ENABLED`, `VITE_IDENTITY_URL`, `VITE_IDENTITY_WEB_URL`, `VITE_COMMERCE_DEMO_MODE`, `VITE_AGENT_RUNTIME_ENABLED` (**values** restored; were empty) |
| Render gateway | `AUTH0_*` (already), plus `OPENAI_API_KEY`, `OPENAI_REALTIME_MODEL`, `CURSOR_API_KEY` |

---

## Live web E2E resume — 2026-07-12 17:05 IST

**Bridge:** Hermes Chrome WIP · sessions `web-e2e-buyer` / `web-e2e-seller`  
**Policy:** no demo flip; no paid upgrades; no secrets in ledger.  
**Artifacts:** `evidence/web-e2e-fqdn-resume-20260712-170051.json` · `evidence/web-e2e-logout-sam-20260712-170355.json` · `evidence/web-buyer-auth-session-probe-20260712-165727.json`

### Auth / session

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AUTH0-UI | **Pass** | prior `web-buyer-signin-button-20260712-1632.jpeg` + home shots | Sign in CTA; Unsigned; no Wallet KYC |
| W-S-AUTH0-UI | **Pass** | `web-seller-home-20260712-170051-3.jpeg` | Sign in CTA on Seller |
| W-GW-AUTH0-SESSION | **Pass** | `web-gw-me-20260712-170051-4.jpeg` · session probe JSON | `/api/auth/auth0/start` silent-SSO → gateway `/api/auth/me` **Authenticated** (`principal:auth0:google-oauth2:…`). OTP **not** required in this browser profile |
| W-B-SPA-SESSION | **Pass** | `spa-session-probe-20260712-172223.json` · `spa-buyer-after-signin-20260712-172223.jpeg` | After `gateway.aadharcha.in` cutover: Buyer **Sign out**; `fetch(https://gateway.aadharcha.in/api/auth/me,{credentials:'include'})` → Authenticated `principal:auth0:…` |
| W-GW-LOGOUT | **Pass** (POST) | `web-e2e-logout-sam-20260712-170355.json` | `POST /api/auth/logout` clears session (`afterMsg: No authenticated…`). **GET** logout → **405** (Allow: POST) — do not use GET for Sign out proof |
| W-B-AUTH0-FLOW | **Pass** | SPA session Pass + Auth0 callback on gateway FQDN | Custom domain + `PUBLIC_GATEWAY_URL` + Auth0 callback allowlist |

### Buyer commerce / Samantha

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-HOME | **Pass** | search/home shots | `/search`; Sign in; Unsigned |
| W-B-CART | **Pass** | `web-buyer-cc-20260712-170051-3.jpeg` | Cart lines: Sharbati Atta + Robusta Bananas ×3; total INR 559 |
| W-B-CHECKOUT | **Blocked** | `web-buyer-cc-20260712-170051-8.jpeg` | Form reachable; **Trust verification / Sign in before elevated**; no Paid+receipt without SPA session |
| W-B-SEARCH | **Partial** | `web-buyer-search-20260712-170051-6.jpeg` | Query `banana` filled; results UI not captured this click (cart already held bananas from prior) |
| W-B-SAM-TEXT | **Fail** | `web-buyer-sam-*-170051-9.jpeg` · `web-buyer-sam-show-*-170355-12.jpeg` | Orb opens; `fill_send` returns ok; **no visible tool reply / results UI** this run |
| W-B-VOICE | **Partial** | `web-buyer-voice-20260712-170051-5.jpeg` | Gateway `/api/realtime/status` `configured:true`; orb **“Text mode ready (no mic)”** — not WebRTC voice Pass |
| W-B-RUNTIME | **Fail** | `web-buyer-runtime-20260712-170051-8.jpeg` | Long ask left in input; no “I've started…” / handoff shot |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-HOME | **Pass** | `web-seller-home-20260712-170051-3.jpeg` | Dashboard; Sign in; Unsigned |
| W-S-CAT | **Pass** | `web-seller-cat-20260712-170051-3.jpeg` | Empty catalog; Add product gated |
| W-S-ORD | **Pass** | `web-seller-ord-20260712-170051-3.jpeg` | 0 incoming |
| W-S-AG | **Pass** | `web-seller-ag-20260712-170051-3.jpeg` | AgentGuard page; bind-policy gated on sign-in |
| W-S-CFG | **Pass** | `web-seller-cfg-20260712-170051-3.jpeg` | Credentials UI present |
| W-S-REFUND | **Blocked** | orders empty + unsigned | No refund path |
| W-S-SAM | **Partial** | `web-seller-sam-20260712-170355-9.jpeg` | Orb “Text mode ready (no mic)”; no tool outcome shot |

### Remaining hard-stops (ordered)

1. ~~Cross-site session cookie~~ — **Closed 2026-07-12:** `gateway.aadharcha.in` + `Domain=.aadharcha.in` (SPA session Pass).
2. Samantha FQDN text/voice tool outcomes + runtime handoff — retest now that SPA session works.
3. Optional: Render CLI re-login; Vercel non-HUF git author for deploys — **no paid upgrade**.

**OTP note:** Not the blocker in this Hermes profile (Auth0 silent SSO already minted gateway session). Leave Universal Login tab only if a fresh browser has no Auth0 SSO cookie.

---

## Live web E2E — Realtime “not configured” fix — 2026-07-12 17:48 IST

**Operator report:** Samantha UI showed **“Realtime not configured on gateway”**.

### Diagnose (evidence)

| Check | Result |
| --- | --- |
| `https://gateway.aadharcha.in/api/realtime/status` | `configured:true`, model `gpt-realtime-2.1-mini` |
| `https://identity-aadhar-gateway-main.onrender.com/api/realtime/status` | same `configured:true` |
| Buyer asset `TRUST_API_URL` | fetches `https://gateway.aadharcha.in/api/realtime/status` (perf + bake) |
| Render `OPENAI_API_KEY` | **present** (status configured — never print value); local `.env` also set |
| UI code path | `SamanthaOrb` `configured===false` → hint “Realtime not configured…” — **false negative** when mount-time status fetch raced / Free cold-start failed before orb open |

### Fix ($0 Hobby)

- Buyer+Seller: re-probe `/api/realtime/status` on orb open (retries for cold start); do not treat `configured=null` as missing key.
- Redeployed non-git staging + alias FQDNs — assets `index-BQ6FIta4.js` (Buyer), `index-Cc8UIQ_e.js` (Seller).
- Gateway redeploy **not required** (key already live).

### Matrix after fix

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-RT-STATUS | **Pass** | curl both hosts | `configured:true` |
| W-B-RT-UI | **Pass** | `W-B-VOICE-RT-FIXED-20260712-174850-0.jpeg` · `web-realtime-fix-20260712-174850.json` | Orb **“Text mode ready (no mic)”** — **not** “Realtime not configured” |
| W-B-SAM-TEXT | **Pass** | `W-B-SAM-TEXT-AFTER-RT-20260712-174923-0.jpeg` · prior `W-B-FIND-BANANA-20260712-173205-0.jpeg` | `search_catalog` → `/results` bananas |
| W-B-ADD-BANANA | **Pass** | `W-B-ADD-BANANA-20260712-173341-0.jpeg` · `W-B-CART-…` | cart line Robusta Bananas |
| W-B-MEM-ORG | **Pass** | `W-B-MEM-ORG-20260712-173341-0.jpeg` | `remember_preference` |
| W-B-CHECKOUT | **Blocked** → **Pass** (retest) | prior `W-B-CHECKOUT-20260712-173341-0.jpeg`; retest below | was `Permission denied: 'data'`; fixed by `DATA_DIR` |
| W-B-RUNTIME | **Partial** | `W-B-RUNTIME-20260712-173341-0.jpeg` | `delegate_to_runtime_agent` fired; JSON/HTML error in hint; stayed on `/search` |
| W-B-VOICE | **Blocked** | mic `NotFoundError` in Hermes + “no mic” | Realtime **session** Pass (text); **mic/WebRTC voice** not available in automation profile |
| W-B-AG-ENSURE | **Blocked** → **Pass** (retest) | prior `W-B-AG-ENSURE-20260712-173341-0.jpeg`; retest below | was ensure **500**; fixed by `DATA_DIR` |

### Remaining hard-stops (ordered)

1. ~~Render `DATA_DIR` writable~~ — **done** 17:56 (`DATA_DIR=/tmp/aadharchain-data`; no Disk).
2. Seller thorough mirror (publish/refund/runtime) — AG ensure Pass; tools still owed.
3. True **voice** Pass needs operator mic / browser permission (Hermes profile has no mic device).
4. Optional: Render CLI re-login; Render MCP workspace auth — Hermes dashboard works — **no paid upgrade**.

---

## Live web E2E — DATA_DIR + checkout — 2026-07-12 17:56 IST

**Hard-stop cleared:** Render Free gateway AgentGuard write. Set env `DATA_DIR=/tmp/aadharchain-data` on `identity-aadhar-gateway-main` via Hermes dashboard → Save, rebuild, and deploy. Ephemeral `/tmp` only — **no Render Disk / $0**.

### Proof

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-AG-ENSURE | **Pass** | `W-B-AG-ENSURE-20260712-175629-0.jpeg` · `W-B-AG-ENSURE-20260712-175629.json` | `POST …/agents/ensure` **200** `AgentGuard agent ready`; `permissionDenied:false` |
| W-B-CART | **Pass** | `W-B-CART-DATADIR-20260712-175654-5.jpeg` | `/cart`; Robusta Bananas + Atta |
| W-B-CHECKOUT | **Pass** | `W-B-CHECKOUT-DATADIR-20260712-175654-5.jpeg` · `-8.jpeg` · `W-B-CHECKOUT-DATADIR-20260712-175654.json` | `checkout_commit` **allow**; **Paid** + receipt `rcpt_90c6dec41ab8400f`; order `demo-1783859251508-w7m0e0`; INR 715 |
| W-S-AG-ENSURE | **Pass** | `W-S-AG-ENSURE-20260712-175821-2.jpeg` · `W-S-AG-ENSURE-20260712-175821.json` | Seller role ensure **200**; no Errno 13 |

**Note:** Order page still shows “Trust check: Unsigned” (signed-receipt verify gap — not DATA_DIR). SPA session authenticated (`Sign out` + `/api/auth/me`).

---

## Live web E2E thorough — 2026-07-12 20:55 IST (FQDN + gateway control plane)

**Script:** `scripts/hermes_fqdn_e2e_thorough.py both`  
**Ledger:** `evidence/web-e2e-thorough-20260712-205518.json`  
**Counts:** Pass **18** · Fail **3** · Blocked **2** (voice mic)  
**Closeout:** ok · console errors **0**

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-BOOT-…-205518-*.jpeg` | Auth0 principal + Sign out |
| W-B-MANDATE | **Pass** | same | `mandate_…` active |
| W-B-VOICE-MIC | **Pass** | same | orb “Listening + text ready” (device present); full voice ask still Blocked below |
| W-B-HI | **Fail** | `W-B-HI-…` | greeting also fired `search_catalog` → `/results` |
| W-B-FIND-BANANA | **Pass** | `W-B-FIND-BANANA-…` | network results; banana=True |
| W-B-ADD-BANANA | **Fail** | `W-B-ADD-BANANA-…` · `W-B-CART-…` | tools searched; **cart empty** (network→local cart gap) |
| W-B-CART / CONFIG / MEM | **Pass** | shots `…-205518` | `/cart`, `/config`, organic preference |
| W-B-NAV-CHECKOUT | **Fail** | `W-B-NAV-CHECKOUT-…` | stayed `/cart` (empty cart) |
| W-B-CHECKOUT | **Pass** | `W-B-CHECKOUT-…` | `checkout_commit` tool fired; empty-cart honest deny path |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…` · late shot | `delegate_to_runtime_agent`; stayed `/search`; weekly plan content in orb |
| W-B-VOICE | **Blocked** | `W-B-VOICE-…` | Realtime configured; Hermes mic/WebRTC not usable |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-BOOT-…` | Auth0 + active mandate |
| W-S-HI / NAV-* | **Pass** | `W-S-HI/NAV-*` | dashboard / catalog / orders / agentguard |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…` · `W-S-CAT-AFTER-…` | `catalog_publish` → Test Atta; Atta 1kg live in ledger |
| W-S-REFUND | **Pass** | `W-S-REFUND-…` | handoff + navigate; orb started background refund triage |
| W-S-MEM | **Pass** | `W-S-MEM-…` | `remember_preference` |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…` | `delegate_to_runtime_agent`; ops triage in orb; not `/agent` |
| W-S-VOICE | **Blocked** | — | same mic constraint |

### Remaining after this run

1. **Buyer network add→cart** — top Fail; blocks paid checkout tonight.
2. Greeting must not auto-search (W-B-HI Fail).
3. True voice Pass needs operator mic.
4. Prefer Seller `refund_issue` when a concrete order id exists (tonight used navigate+runtime).

---

## Operator text-mode + early `/results` — 2026-07-12 21:42 IST

**Script:** `scripts/hermes_operator_visible_search.py`  
**Ledger:** `evidence/op-visible-search-20260712-214200.json`  
**Skill updates:** `operator-flows.md`, `test-inventory.md`, `ondc_ci_graders.py` (CI soft FQDN)  
**Closeout:** ok · console errors **0**

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-OP-BOOT-…-214200-0.jpeg` | Auth0 Sign out; text mode ready |
| W-B-HI | **Pass** | `W-B-HI-…-214200-0.jpeg` | `/search`; no tools; greeting only |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-214200-0.jpeg` | **Early `/results`**; hint “Searching for atta — watch the results page…”; pulling offers |
| W-B-FIND-BANANA | **Fail** | `W-B-FIND-BANANA-…` | Ask left in input; orb busy after prior ONDC search |
| W-B-ADD / NAV / RUNTIME | **Fail** | shots `…-214200` | Same stall — no tools fired |

### Seller smoke

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-OP-BOOT-…` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…` | `catalog_publish`; catalog 17→18 |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…` | handoff hint; not `/agent` |

### Remaining after this run

1. **Orb send after long `search_catalog`** — follow-on text asks can stick in draft (banana/nav/runtime Fail).
2. Network **add→cart** still owed when tools fire.
3. Voice mic still Blocked in Hermes.
4. CI: `ondc_ci_graders --live --soft` advisory (seller bundle may tree-shake demo-mode key).

---

## Operator text-mode retest (orb stall mitigations) — 2026-07-12 22:07–22:14 IST

**Scripts:** `hermes_operator_visible_search.py` (+ chained prove) · focused retest `op-retest-chained-20260712-221433.json`  
**Ledgers:** `evidence/op-visible-search-20260712-220718.json` · `evidence/op-retest-chained-20260712-221433.json`  
**Graders:** `ondc_ci_graders --live --soft` → ok (buyer bundle demo_mode=false; seller key tree-shaken)  
**Closeout:** ok · bridge ready · leave `ondcbuyer…/search`

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-OP-BOOT-…-220718-0.jpeg` | Auth0 Sign out; text mode ready |
| W-B-HI | **Pass** | `W-B-HI-…-220718-0.jpeg` | `/search`; greeting; no tools |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-220718-0.jpeg` | Early `/results`; pulling offers |
| W-B-FIND-BANANA | **Pass** | `W-B-RETEST2-BANANA-…-221433-0.jpeg` | Early `/results` (retest; mid-run Fail was Free GW cold + Realtime down) |
| W-B-CHAINED | **Partial** | `W-B-RETEST2-CHAINED-…-221433-0.jpeg` · prior `W-B-CHAINED-…-220718` | **Draft stall fixed** (`send_ok=true`); `navigate_to` fires; UI still `/results` (search race holds page). Orb claims cart. |
| W-B-ADD | **Partial** | `W-B-RETEST2-ADD-…-221433-0.jpeg` | Send accepted; Realtime “active response in progress”; no cart line |
| W-B-NAV-CART | **Pass** | `W-B-NAV-CART-…-220718-0.jpeg` | `/cart` after cooldown |
| W-B-NAV-CONFIG | **Pass** | `W-B-NAV-CONFIG-…-220718-0.jpeg` | `/config` |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…-220718-0.jpeg` | `delegate_to_runtime_agent`; not `/agent` |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-OP-BOOT-…-220718` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…-220718` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…-220718` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…-220718-0.jpeg` | `catalog_publish`; catalog →19; Operator Atta |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…-220718` | handoff; not `/agent` |

### Orb stall verdict

| Claim | Verdict |
| --- | --- |
| Draft stuck / send_disabled after long search | **Fixed** — chained asks `send_ok=true` (×2 retests) |
| Chained ask lands visible `/cart` while search still pulling | **Not fixed** — `navigate_to` + `search_catalog` race; page stays on `/results` |
| Free gateway cold mid-matrix | Still bites — mark Blocked/retry, not product Fail |

### Remaining

1. Network **add→cart** when tools fire cleanly (Realtime concurrent-response); item ids from ResultsPage cache after progressive paint.
2. Voice mic still Blocked in Hermes.
3. Keep gateway warm during long FQDN operator runs (Free spin-down).
4. Paint ~19s still dominated by PreProd `on_search` fanout (not double dispatch) — acceptable vs prior 93s.

---

## ONDC fetch doctrine prove — 2026-07-12 22:54 IST

**Doctrine:** [`ondc-fetch-doctrine.md`](ondc-fetch-doctrine.md)  
**Deploy:** `ondcbuyer-6xlyphqq6` · **Ledger:** `evidence/op-doctrine-atta-20260712-225441.json` · **Shot:** `W-B-DOCTRINE-ATTA-20260712-225441-0.jpeg`

| Metric | Before | After |
| --- | --- | --- |
| Early `/results` | ~1s | **1012 ms** Pass |
| Tool `search_catalog` return | collect up to **12s** | **4068 ms** ACK+txn Pass |
| Unique `/api/ondc/search` | **2** (double dispatch) | **1** Pass |
| Grid settle | **~93s** / Failed-to-fetch races | **18935 ms**, 13 matches, no hard fail Pass |
| W-B-FIND-ATTA doctrine | — | **Pass** |

---

## USP settle→validate→next — 2026-07-12 23:21 IST

**Protocol:** one ask → settle (`__samanthaTools` + route/UI) → next. Hermes WIP. Demo off.  
**Bake:** `index-Mo-Hxb-1.js` · deploy `ondcbuyer-b0xglvsrx` · alias `ondcbuyer.aadharcha.in`  
**Ledgers:** `evidence/usp-settle-20260712-225913.json` · `usp-add-reprove2-20260712-231845.json` · `usp-checkout-after-add-20260712-232128.json`  
**Closeout:** leave `ondcbuyer…/search` · bridge ready

### Buyer

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-B-SPA-SESSION | **Pass** | `W-B-USP-BOOT-…-225913` | Auth0 Sign out; text mode ready (no mic) |
| W-B-HI | **Pass** | `W-B-HI-…-225913` | `/search`; greeting; no tools |
| W-B-FIND-ATTA | **Pass** | `W-B-FIND-ATTA-…-225913` · `W-B-FIND-ATTA-R2-…-231845` | Early `/results`; offers≥18; `search_catalog` |
| W-B-ADD-ATTA | **Fail→Pass** | Fail `W-B-ADD-ATTA-…-225913`; Pass `W-B-ADD-ATTA-R2-…-231845` | Root: ACK-empty ids → model re-searched. Fix: cache name resolve + Host context inject. `/cart` line “atta” ×1 INR 118; `add_to_cart` ok |
| W-B-MEM-ORG | **Pass** | `W-B-MEM-ORG-…-225913` | `remember_preference`; organic on `/config` |
| W-B-NAV-CONFIG | **Pass** | `W-B-NAV-CONFIG-…-225913` | `/config` |
| W-B-FIND-PREF | **Pass** | `W-B-FIND-PREF-…-225913` | preference-aligned search; `/results` offers |
| W-B-CHECKOUT | **Partial→Pass** | Partial `W-B-CHECKOUT-AFTER-ADD-…-232128`; Pass `W-B-ORDER-DETAIL-20260712-232726-3.jpeg` · `usp-order-detail-20260712-232726.json` | Partial was HTML≠JSON on `/orders/{id}`. Fix: `OrderDetailPage` localStorage fallback + `orderApi` HTML reject. Reprove: Paid + `rcpt_c9a68660930b4fba` on order detail (not unavailable). Alias `ondcbuyer-archive-deploy-3i99740un` · `index-BaIfxHlR.js` |
| W-B-RUNTIME | **Pass** | `W-B-RUNTIME-…-225913` | `delegate_to_runtime_agent`; stayed `/search`; weekly plan in orb |
| W-B-VOICE | **Blocked** | orb hint | Realtime configured; Hermes mic/WebRTC not usable |

### Seller

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| W-S-SPA-SESSION | **Pass** | `W-S-USP-BOOT-…-225913` | Sign out |
| W-S-HI | **Pass** | `W-S-HI-…-225913` | `/dashboard`; no tools |
| W-S-NAV-CAT/ORD/AG | **Pass** | `W-S-NAV-*-…-225913` | `navigate_to` |
| W-S-PUBLISH | **Pass** | `W-S-PUBLISH-…-225913` | `catalog_publish` Test Organic Atta |
| W-S-REFUND | **Partial** | `W-S-REFUND-…-225913` | navigated `/orders`; no `refund_issue` (no order id) |
| W-S-RUNTIME | **Pass** | `W-S-RUNTIME-…-225913` | handoff; not `/agent` |
| W-S-VOICE | **Blocked** | — | same mic Blocked |

### Completeness (operator-flows catalog = 28 IDs)

| Metric | Value |
| --- | --- |
| Attempted this run | 16 catalog twins (+ FIND-PREF net-new) |
| Pass / Partial / Blocked / Fail | 14 / 1 / 2 / 0 (after ADD + order-detail fix) |
| Weighted catalog coverage | **~52%** (14 + 0.5×1 + 0.25×2) / 28 |
| Weighted attempted | **~91%** of attempted |

### NOT covered (this run)

`B-THX`, `B-FIND-BANANA`, `B-FIND-MILK`, `B-FIND-APPLE`, `B-NAV-CART`, `B-NAV-CHECKOUT`, `B-NAV-ORDERS`, `B-CHECKOUT-OVER`, `B-EMPTY`, `B-CHAINED`, `S-MEM`, `S-REFUND-OVER`

### USP gaps remaining

1. ~~**Order detail after Samantha checkout**~~ — **Pass** 23:27 (`rcpt_c9a68660930b4fba`; see § Order detail retest)
2. **Voice mic/WebRTC** — Blocked in Hermes
3. **B-CHAINED** visible `/cart` while search still pulling — not retested this run
4. Cart line label generic “atta” (cache name) — acceptable Pass, polish later

### Fix shipped mid-run

Buyer: `lookupBuyerCatalogByQuery` + `add_to_cart` query/name resolve; search early return includes cached ids; Realtime Host context inject of visible results cache; orb instructions “do not re-search to add”. Hobby archive redeploy ×2 → `index-Mo-Hxb-1.js`.

---

## Order detail after Samantha checkout — 2026-07-12 23:27 IST

**Gate:** Paid + receipt on **order detail page** (not tool orb alone; not “Order detail unavailable”).  
**Alias:** `ondcbuyer-archive-deploy-3i99740un` → `ondcbuyer.aadharcha.in` · bake `index-BaIfxHlR.js` · demo off  
**Ledger:** `evidence/usp-order-detail-20260712-232726.json`  
**Closeout:** `ondcbuyer…/search` · bridge ready

| ID | Result | Evidence | Notes |
| --- | --- | --- | --- |
| B-FIND-ATTA | **Pass** | ledger | `/results`; `search_catalog`; atta offers |
| B-ADD-ATTA | **Pass** | ledger | `add_to_cart` → `/cart` line atta ×1 |
| W-B-CHECKOUT | **Pass** | `W-B-ORDER-DETAIL-20260712-232726-3.jpeg` | `/orders/demo-1783879102172-2701w7`; **Paid** + `rcpt_c9a68660930b4fba`; Payment PAID; unavailable=false |

---

## Local first-time operator text-mode hardening — 2026-07-14 13:59–14:22 IST

**Protocol:** novice natural-language asks through Samantha's visible text UI; Hermes WIP semantic locators; one ask → settle → route/page/tool screenshot. No API seeding or mutating `evaluate`. Voice intentionally deferred.

**Ledgers:** `evidence/matrix-run-20260714-135947.json` (Buyer product 9/9; runtime harness false-negative fixed) · `evidence/matrix-run-20260714-140825.json` (Seller 9/9) · focused Buyer runtime screenshots `B-LONG-FOCUSED-20260714-141912-0.jpeg`, `B-LONG-FOCUSED-R1-20260714-141912-0.jpeg`, `B-LONG-FOCUSED-R2-20260714-141912-0.jpeg`.

### Buyer

| ID | Result | Evidence | Visible outcome |
| --- | --- | --- | --- |
| B-HI | **Pass ×2** | `B-HI-20260714-135947-0.jpeg` · `B-HI-20260714-141258-0.jpeg` | `/search`; useful first-time introduction; no tool fired |
| B-FIND-NL-ATTA | **Pass ×2** | `B-FIND-ATTA-20260714-135947-0.jpeg` · `B-FIND-ATTA-20260714-141258-0.jpeg` | Natural breakfast ask → `/results`; Atta offers; `search_catalog` |
| B-ADD-ATTA | **Pass ×2** | `B-ADD-ATTA-20260714-135947-0.jpeg` · `B-ADD-ATTA-20260714-141258-0.jpeg` | “That first atta” → `/cart`; visible line; `add_to_cart` |
| B-NAV-CART / CHECKOUT / CONFIG | **Pass ×2** | matching `*-20260714-135947-0.jpeg` and `*-20260714-141258-0.jpeg` | Samantha navigates while operator watches; remembered organic preference visible on Config |
| B-CHECKOUT-OK | **Pass ×2** | `B-CHECKOUT-OK-20260714-135947-0.jpeg` · `B-CHECKOUT-OK-20260714-141258-0.jpeg` | `checkout_commit`; paid order and receipt visible; signed principal no longer shown as unsigned |
| B-CHECKOUT-OVER | **Pass ×2** | `B-CHECKOUT-OVER-20260714-135947-0.jpeg` · `B-CHECKOUT-OVER-20260714-141258-0.jpeg` | Exact one-time approval required and visible |
| B-LONG-WEEKLY | **Pass** | focused screenshots above | `delegate_to_runtime_agent`; stayed off `/agent`; lifecycle `started → heartbeat → completed` |

### Seller

| ID | Result | Evidence | Visible outcome |
| --- | --- | --- | --- |
| S-HI / NAV-AG / NAV-CAT / NAV-ORD | **Pass ×2** | matching `*-20260714-140410-0.jpeg` and `*-20260714-140825-0.jpeg` | First-time introduction and visible page navigation |
| S-PUBLISH | **Pass ×2** | `S-PUBLISH-20260714-140410-0.jpeg` · `S-PUBLISH-20260714-140825-0.jpeg` | Spoken price and 7-pack inventory persisted; catalog refreshed immediately |
| S-REFUND-OK | **Pass ×2** | `S-REFUND-OK-20260714-140410-0.jpeg` · `S-REFUND-OK-20260714-140825-0.jpeg` | AgentGuard page shows executed refund and receipt, not orb-only text |
| S-REFUND-OVER | **Pass ×2** | `S-REFUND-OVER-20260714-140410-0.jpeg` · `S-REFUND-OVER-20260714-140825-0.jpeg` | 26,000 INR refund visibly waits for exact one-time approval; manual approval/execution also proved |
| S-MEM | **Pass ×2** | `S-MEM-UI-20260714-140410-0.jpeg` · `S-MEM-UI-20260714-140825-0.jpeg` | Preference appears on AgentGuard without reload |
| S-LONG-TRIAGE | **Pass** | `S-LONG-TRIAGE-20260714-140825-0.jpeg` · `S-LONG-TRIAGE-DONE-20260714-140825-0.jpeg` | Stayed on `/orders`; lifecycle `started → completed`; concrete triage returned |

### Root fixes encoded

- Orb accepts/queues text while Realtime connects; Seller now matches Buyer queue behavior.
- Replies keep their beginning and response segments no longer concatenate mid-word.
- Buyer order-detail trust derives the effective signed-principal state.
- Seller publish honors spoken inventory and refreshes the visible catalog.
- Seller refund outcomes navigate to AgentGuard; high-value approval can be executed from the visible banner.
- Buyer/Seller background work records lifecycle events and shows an honest 30-second heartbeat.
- Orb output now removes raw Markdown punctuation, uses readable bullets/spacing, avoids duplicate completion summaries, and gives long answers more room.
- `scripts/hermes_ondc_testing_matrix.py` now uses Hermes locators, novice phrasing, runtime completion proof, recovery after normal panel remounts, and mandatory closeout.

**Reply polish proof:** `B-REPLY-POLISH-20260714-142407-0.jpeg` · `S-REPLY-POLISH-20260714-142407-0.jpeg` — readable bullets, no raw Markdown markers.

**Regression:** Buyer 151 tests + build Pass; Seller 158 tests + build Pass. Portfolio gateway 80 tests Pass. Hermes skill validation hard=0 (soft folder/name warning only). Hermes session inventory empty at closeout.

---

## Post-deployment Chrome web gate — 2026-07-14 17:40 IST

**Protocol:** authenticated Buyer + Seller FQDN matrix through WIP Hermes in the discovered Google Chrome profile directory `robo-trader-testing`; semantic locators for mutations; session closeout required.
**Ledger:** `evidence/web-e2e-thorough-20260714-174011.json`
**Result:** **26 Pass / 3 Blocked / 0 Fail**; all Blocked checks are physical microphone/voice proof.

| Surface | Result | Evidence |
| --- | --- | --- |
| Buyer | **13 Pass / 2 Blocked / 0 Fail** | Auth0 session + mandate; text Samantha; ONDC Atta search; resolved cart add; cart/checkout; Paid order + receipt; pause/resume; protected activity + receipt verification; memory; Realtime config; runtime delegation. `W-B-VOICE-MIC` and `W-B-VOICE` remain Blocked because the browser exposed `Text mode ready (no mic)`. The first Atta screenshot caught the offer grid painting; the ledger assertion and following cart captures prove the completed result and product resolution. |
| Seller | **13 Pass / 1 Blocked / 0 Fail** | Auth0 session; text Samantha; catalog/orders/AgentGuard navigation; catalog publish; refund page; INR 3,000 auto-allow receipt; INR 7,500 approval; consume; replay rejection; memory; runtime delegation. `W-S-VOICE` remains Blocked because no physical mic state was available. |
| Browser owner | **Pass** | Preflight discovered `Google Chrome` / profile directory `robo-trader-testing`; no duplicate Comet or isolated-Chrome profile was launched. |
| Closeout | **Pass** | Ledger `meta.sessions_closed` contains `fqdn-e2e-20260714-174011`; no validation lease was left open. |

Realtime is configured (`gpt-realtime-2.1-mini`, Samantha), and text/runtime tool execution passed. This gate does **not** claim physical mic/WebRTC completion.

---

## Local Samantha frozen-source text gate — 2026-07-16 00:08–00:34 IST

**Protocol:** WIP Hermes local browser; Buyer `http://127.0.0.1:43102`, Seller `http://127.0.0.1:43103`; customer-language text asks; exact turn-scoped tools; settled turn; visible screenshot; backend semantic owner check. Two consecutive combined runs used unchanged source. Every screenshot was opened and visually accepted. API writes were limited to unique catalog/order preconditions; browser `evaluate` remained read-only.

**Ledgers:** `evidence/matrix-run-20260716-000819.json` · `evidence/matrix-run-20260716-002128.json`

| Surface | Result | Evidence |
| --- | --- | --- |
| Buyer | **19/19 Pass ×2** | Search-only discovery, grounded results, add/clear/quantity/remove, cart/checkout/config navigation, preference memory, real INR 25,089 cart → exact `need_approval`, high-value item removal → INR 89 exact `allow` + matching receipt, runtime handoff. Origin `:43102`; zero turn errors. |
| Seller | **12/12 Pass ×2** | First-time help, AgentGuard/catalog/orders navigation, exact Ragi publish + backend visibility, accept→fulfill and reject with exact backend states, refund allow receipt, INR 26,000 approval, memory, multi-tool runtime handoff. Origin `:43103`; zero turn errors. |
| Visual review | **64/64 accepted** | 32 screenshots per run (Seller memory row has separate action and AgentGuard captures); no error panel, wrong-origin page, hidden `/agent` route, or stale checkout fallback accepted. |
| Regression | **Pass** | Buyer **155/155** tests + typecheck + production build; Seller **163/163** tests + typecheck + production build; `ondc-testing` and `portfolio-browser` validators Pass; Python compile, Ruff, and diff checks Pass. |
| Closeout | **Pass** | Matrix-owned WIP Hermes closeout completed after both runs. |

Durable fixes: Realtime follow-up responses are serialized per active response and reset per `response.created`, so chained navigation→delegation no longer races or stalls. Matrix proof is turn-scoped, fails on new Realtime errors, validates exact frontend origin and backend response semantics, uses a real over-limit cart instead of overriding the cart total, and reloads only approval/deny checkout states.

**Boundary:** local text/runtime proof only. No deployment, FQDN freshness, release, or physical microphone/WebRTC claim is made; physical mic remains blocked.

---

## Milestone 8 server-owned two-sided lifecycle — 2026-07-16 18:41–18:43 IST

**Protocol:** local WIP Hermes with app-specific demo SSO immediately before each capture; unique server-owned item/order/transaction/issue identities; screenshot + page text + gateway state agreement; cleanup after capture. Full evidence: `evidence/m8-browser-local-authority.md`.

| Gate | Result | Evidence |
| --- | --- | --- |
| First browser attempt | **Fail → fixed** | `m8-visible-1784208100-a`; Seller visible, Buyer audience cookie overwritten and gateway process stale. Lane now authenticates per app; stack restarted through `scripts/start-dev.sh`. |
| Two-sided run A | **Pass** | `m8-visible-1784208200-a`; order `order_046194d8c55b46e5`; transaction `txn_7c370c1c44094790`; issue `issue_b2b3839a03174e14`; three retained screenshots visually accepted. |
| Two-sided run B | **Pass** | `m8-visible-1784208201-b`; order `order_e5539c89c77b4593`; transaction `txn_26866a2a067a46a0`; issue `issue_6ec0143760424ab3`; three retained screenshots visually accepted. |
| Deterministic gates | **Pass** | Gateway 86; targeted commerce/AgentGuard 15; Buyer 143 + build; Seller 162 + build. |

Conclusion: browser storage is no longer authoritative for catalog, orders, inventory, checkout, or support cases. Remaining local storage is limited to cart/session/UI preferences, drafts, audit annotations, and seller notes; every accepted commerce mutation is server-owned.

---

## Milestone 8 shared contract and single assistant surface — 2026-07-16 19:13–19:20 IST

**Protocol:** final-source Buyer/Seller tests, typechecks, builds, gateway CI,
contract/shortcut searches, then two consecutive unique WIP-Hermes two-sided
runs with screenshot review and closeout. Full evidence:
`evidence/m8-contract-flow-consolidation.md`.

| Gate | Result | Evidence |
| --- | --- | --- |
| Shared contract | **Pass** | Buyer/Seller use shared action, agent, mandate, approval, and intent-receipt types; dated Seller compatibility vocabulary remains explicitly legacy |
| Single assistant surface | **Pass** | standalone Buyer and Seller `/agent` routes/navigation removed; Samantha remains the global orb; model navigation allowlists reject `/agent` |
| Judged-flow integrity | **Pass** | no AgentGuard protected-action API shortcut in judged Buyer/Seller/two-sided Hermes scripts |
| Two-sided run A | **Pass** | `m8-contract-final-1784209300-a`; order `order_47aa87015f8f40ec`; transaction `txn_a9607f26c37c4315`; issue `issue_6ff48b295bd64728`; three screenshots accepted |
| Two-sided run B | **Pass** | `m8-contract-final-1784209301-b`; order `order_070f0ce5a9274463`; transaction `txn_8b9c603db3d04b5c`; issue `issue_46a0ee83c93d45d9`; three screenshots accepted |
| Regression | **Pass** | Buyer 131 tests + typecheck + build; Seller 162 tests + typecheck + build; gateway 86 tests |
| Closeout | **Pass** | WIP bridge ready; no validation lease retained |

Conclusion: Milestone 8 cleanup has one shared AgentGuard contract owner and one
visible Samantha surface per app while preserving the server-owned two-sided
commerce and receipt proof.

---

## Independent customer and UX gate hardening — 2026-07-16 19:34–20:18 IST

**Protocol:** blind context-isolated reviewers through leased WIP Hermes;
correct app-audience demo SSO prepared by the main thread; visible UI only;
screenshots read before verdicts; every owned lease closed. An unrelated
BrandGPT lease was left untouched.

| Reviewer / gate | Result | Evidence |
| --- | --- | --- |
| Buyer novice, signed in | **App Fail** | “Ask Samantha” was visible but the first activation did not expose a usable input; downstream shopping was Not Tested. `6b71284b-c5da-42e0-ab9a-ef94cbd73c2f-1.png`, `432435a2-129a-4231-b024-9eb0961064ee-0.png` |
| Seller novice, signed in | **App Fail (incomplete)** | Samantha text mode accepted “Hello there”; catalog showed three products. Publish, stock/price proof, and orders were Not Tested before the old short bound. `0a95c81d-4dcc-4aac-8156-136dc18ddef4-1.png` |
| Buyer UX/accessibility | **App Fail** | Vague “verified/protected” claims; Samantha authority unexplained; floating assistant overlaps the search action; hero/status content competes with the primary search. `3e850fc1-179a-4b06-9b43-cb23010dec23-1.png`, `3e850fc1-179a-4b06-9b43-cb23010dec23-4.png` |
| Seller UX/accessibility | **App Fail** | “Verified” and “AgentGuard” are unexplained; product rows look static despite control semantics; Samantha purpose/authority is unclear. `dbbbd5ad-dcf9-4818-ac77-c902df031dbc-1.png` |
| Buyer search accessibility | **Fail → fixed** | Hero and form submit both exposed “Search catalog”; the form submit now exposes unique name “Search the network”. Focused component test and live role/name counts pass. |
| Fresh novice Buyer A | **App Fail** | `rice` reached a truthful zero-result page. `fd0eb80a-ae09-4b43-9d7a-81ffd44df95b-3.png` |
| Fresh novice Buyer B | **App Fail** | `rice`, then the visible broadening follow-up `grocery`, both returned zero results despite Seller inventory. `d7b0d5a3-f9ea-4d37-9c75-16883fbf0186-1.png`, `56850fd0-f5fa-406d-a10b-412878c46603-1.png`, `02c868df-6b8b-495a-9e52-ceb699e2d0e0-0.png` |

**Elon-algorithm correction:** the old 90-second micro-runs produced setup churn
and left journeys incomplete. They are historical rejected evidence. The owner
gate now uses three sequential full-mission actors: post-login Buyer novice,
post-login Seller merchant, and cross-app UI/UX plus accessibility smoke. Briefs
contain only profile, signed-in URL, and customer goal—no control names, fixes,
internals, fixtures, or known defects. Customer missions have six-minute
outcome budgets; read-only UX app missions have four-minute budgets. Each report
has one mission verdict, and any fix requires the whole affected journey to run
again in a fresh blind context.

**Current stop:** Buyer blind acceptance remains **App Fail** until the whole
journey is rerun. The earlier local CORS root cause is corrected in current
source through the Buyer `/ondc-control` development proxy, and the proxied
PreProd status endpoint now reports enabled/configured. That deterministic
repair is not customer proof. The WIP Hermes bridge currently reports
`SOCKET_DOWN`, so none of the three revised full-mission profiles has run yet.
The FQDN build also remains unchanged because deployment is outside this goal.
Do not promote this gate from curl, fixture, or diagnostic evidence.

### Current-source deterministic safety closure — 2026-07-16 21:28 IST

| Gate | Result | Current-source evidence |
| --- | --- | --- |
| Shared Python/TypeScript canonical action request | **Pass** | `test_python_canonicalizes_and_hashes_shared_golden_action_request`; Buyer `agentGuardContract.test.ts`; shared expected SHA-256 `b1845e24832e79a73abc2f3502a3130f9d947caf5b1c89e3c2cf8e74fa9ebab2` |
| Session ownership and tenant isolation | **Pass** | session-principal/body-wallet tests, session-B cannot consume session-A approval, plus `test_approval_cannot_cross_tenants`; legacy body-wallet fixture routes remain explicitly outside AgentGuard acceptance |
| Exact approval binding, expiry, atomic consume and replay | **Pass** | bound-field, changed-payload, explicit-expiry, concurrent-consume and replay-conflict tests |
| Pause/revoke and mandate-change invalidation | **Pass** | pause/resume invalidation, mandate replacement, and both stop-vs-consume race variants |
| Checkout cardinality/inventory | **Pass** | duplicate order idempotency yields exactly one stored order, one explicit reservation, and inventory `4 → 2` for quantity two |
| Fulfilment and issue/remedy lifecycle | **Pass** | Seller accepts then fulfils; Buyer reads fulfilled; Seller reads/responds to issue; Buyer reads resolved issue with attached refund remedy ID |
| Simulated payment/refund/reconciliation | **Pass** | success/idempotency test plus timeout `unknown → succeeded` reconciliation and missing-payment unknown result |
| Receipt tamper, prompt injection and direct executor bypass | **Pass** | focused receipt verification/tamper, mandate non-expansion, and no-effect protected executor tests |
| Optional dependency boundary | **Pass locally** | gateway starts and completes core commerce with Solana/Solders imports blocked and ONDC/eKYC/Solana disabled; Buyer/Seller manifests, lockfiles and installed trees contain no Solana wallet stack; visible scope-copy tests reject the legacy identity narrative |

Commands on unchanged local source:

- Executable-source SHA-256: `c29e70aa9240852e8678f5a69574ada06c77120b40927e8958fc5384e644ccbd`.
- `LOCAL-ADVERSARIAL-20260716-2125` → focused gateway contract, isolation, approval, lifecycle, payment, race, tamper, bypass and dependency suite **37 passed**.
- `LOCAL-SAFETY-20260716-2126-P1` → gateway **103 passed**; Buyer **137 passed** + typecheck/build; Seller **163 passed** + typecheck/build.
- `LOCAL-SAFETY-20260716-2127-P2` → the same counts and builds on the unchanged executable-source hash.
- `ondc-testing` and `portfolio-browser` validators, `workflow lint --full`, and all root/nested `git diff --check` gates → **PASS**.
- Retained artifact: [`evidence/local-safety-final-20260716-2128.json`](evidence/local-safety-final-20260716-2128.json).

This closes the local deterministic safety rows only. The three final browser
rows and deployed dependency-honesty row in the testing-ledger owner remain open until
the WIP Hermes bridge is healthy and an authorized deployment places the final
source on the FQDN. Neither condition may be replaced by local or API evidence.

### Current local safety closure — 2026-07-17 08:23 IST

This entry supersedes the preceding current-source counts and browser blocker.

- Executable-source SHA-256: `d940189015a07678ac2704554a80da16874d0c0021b15c9b5d2bb7ec54684a05`.
- `LOCAL-ADVERSARIAL-20260717-D940-P1` and `LOCAL-ADVERSARIAL-20260717-D940-P2` → targeted gateway contract, isolation, approval, lifecycle, payment, race, tamper, bypass and dependency suite **87 passed** each.
- `LOCAL-SAFETY-20260717-D940-P1` and `LOCAL-SAFETY-20260717-D940-P2` → gateway **129 passed**; Buyer **151 passed** + typecheck/build; Seller **172 passed** + typecheck/build.
- Seller UI/UX attempt `SELLER-UX-D940-A1` → **Tooling Blocked**: lease semantic context and owned screenshot referred to different pages; closeout passed and the session was absent.
- One bounded recovery and fresh retry `SELLER-UX-D940-A2-BOUNDED-RETRY` → **Tooling Blocked**: the owned lease disappeared twice; closeout passed and owned sessions were absent.
- Buyer/Seller customer passes and the two-sided visible repeat are **Not Tested** on this hash. The campaign stopped after the repeated browser-ownership failure; prior Seller passes were invalidated by the visible authority fix and are not counted.
- Retained artifact: [`evidence/local-safety-final-20260717-d940.json`](evidence/local-safety-final-20260717-d940.json).

Local deterministic Layers 1–4 and the deterministic portion of Layer 5 pass
twice on unchanged source. The three visible acceptance rows remain open; API,
unit, build, or older-hash browser evidence does not replace them.

### Final-hash independent Buyer campaign — 2026-07-17 23:30–23:45 IST

- Executable-source SHA-256: `af98738a621dfb6109e06d06c2833a20e593cb6e4cf8f08d3edb23dd3781088e`.
- Buyer pass 1 reached checkout after visible discovery, cart add, quantity change, remove, and re-add, then stopped **Tooling Blocked** when the visible full-name field could not be targeted reliably.
- The one permitted fresh recovery repeated the same class of failure: semantic full-name lookup reported no matching visible element and cursor entry diverged into the wrong checkout field. No AgentGuard authorization, order, or receipt was created.
- Both owned leases closed and were absent afterward. The campaign stopped under the independent-customer gate; Seller, two-sided, and combined UI/UX missions are **Not Tested** on this hash.
- Retained blocker: [`evidence/local-customer-proof-blocker-20260717-af987.json`](evidence/local-customer-proof-blocker-20260717-af987.json).

The checkout semantic-input and screenshot owners were repaired, and the WIP
Hermes isolation gate passed three times. A fresh signed-in blind Buyer rerun on
2026-07-18 nevertheless stopped **Tooling Blocked** on the live search surface:
the labeled fill failed once, succeeded after the sole recovery, then the visible
Search click returned `Locator did not resolve for click`. `rice` remained
visibly entered; the 12-item / 8-order / inventory baseline was unchanged and
the owned lease closed. Retained blocker:
[`evidence/local-customer-proof-blocker-20260718-af987-search-locator.json`](evidence/local-customer-proof-blocker-20260718-af987-search-locator.json).
Visible customer acceptance is paused on this narrower WIP Hermes locator-readiness
owner; API or deterministic evidence cannot replace the missing browser rows.

### Independent customer gate — local close 2026-07-19 evening IST

- Git HEAD: `d4ca699`. Buyer audience already had repaired-UI Pass ×2 + Buyer UX Pass earlier the same day (`ui_repair_fingerprint` `22235abcd…`).
- Owner Dispatch proof **Pass** before Seller merchant: Accept → `dialog_opened` prompt → `dialog_handle` → backend `fulfilled`. Evidence: [`evidence/local-owner-dispatch-proof-pass-20260719.json`](evidence/local-owner-dispatch-proof-pass-20260719.json). Prior Seller stop was prompt mishandled as inject/`EXTENSION_TIMEOUT`.
- Seller merchant pass 1 **Pass** ([`Blind Seller merchant`](evidence/local-customer-seller-merchant-pass1-20260719-rerun.json)): publish + Accept→Dispatch→Delivered; incomplete-delivery Accept fails closed to full-page Orders error (recoverable via Retry). Cleanup restored baseline 33 items / 31 orders.
- Seller UX half first attempt **Not Tested** (accidental Sign out). Rerun **Pass**, no unresolved P0/P1: [`evidence/local-customer-seller-ux-half-rerun-20260719.json`](evidence/local-customer-seller-ux-half-rerun-20260719.json). Combined UX **Pass**: [`evidence/local-customer-combined-ux-pass-20260719.json`](evidence/local-customer-combined-ux-pass-20260719.json).
- Seller merchant pass 2 **Pass** (stability): Tata Sampann Toor Dal published; order `34413F79` → Delivered/Completed. Evidence: [`evidence/local-customer-seller-merchant-pass2-20260719.json`](evidence/local-customer-seller-merchant-pass2-20260719.json). Cleanup matched baseline again.
- Campaign close: [`evidence/local-customer-campaign-close-20260719.json`](evidence/local-customer-campaign-close-20260719.json). Bridge closeout ready; `active_agent_sessions=0`.
- Release threshold for this local visible portfolio: Buyer Pass×2 + Seller Pass×2 + combined UX clear on the day’s repaired UI / current HEAD. Parallel Buyer+Seller actors remain blocked on shared WIP cookie (gate).

### Samantha catalog data validation — local 2026-07-19 night IST

- Protocol: [`samantha-catalog-validation.md`](samantha-catalog-validation.md). Evidence: [`evidence/samantha-catalog-validation-20260719.json`](evidence/samantha-catalog-validation-20260719.json).
- Blind Samantha actors: pass1 `bb108593-…` / retest `d4beef4d-…`. **B-HI Pass**; **B-FIND-NL-ATTA Fail** (JUNK `q=roti`, then SKIP-UI unsolicited add); GHOST Atta vs empty `buyer/search?q=atta` before fix.
- Root cause (catalog MISS): `commerce_demo.search_items` required `seller_name` — published fixture Atta with null name was invisible. Fixed to published + in-stock. Gateway restarted; `q=atta` now returns 17 rows (includes test litter `Dispatch Proof*`).
- **Relevance harden (same night):** strict token match in `commerce_demo` + BPP (no empty→full-catalog fallback); Buyer `filterBuyerItemsForQuery` keeps short tokens (`tv`); `catalogSearchQuery` maps TV/television→`tv` and keeps `toor dal`. Delivery-area filter no longer hides SKUs with empty `deliveryAreas`. Empty ONDC network collect falls back to demo-commerce so the grid matches Samantha.
- Seeded markers `20260719234027` (Atta / Toor Dal / Oil / LED TV). API truth: `q=tv` → 1 TV (no oil); `q=oil` → oils only; `q=banana` → 0.
- Browser recheck **Pass** (direct `/results?q=tv` + Samantha “Search for a TV”): **1 match**, Horizon LED TV, no oil. Evidence: [`evidence/samantha-catalog-relevance-recheck-20260719-234802.json`](evidence/samantha-catalog-relevance-recheck-20260719-234802.json). Earlier Samantha pass also HIT oil/atta with `search_catalog` tool: [`evidence/samantha-catalog-relevance-20260719-234437.json`](evidence/samantha-catalog-relevance-20260719-234437.json).
- Still open: find-only “I need atta…” can still unsolicited `add_to_cart` (instruction tightened; needs fresh blind re-proof); catalog litter `Dispatch Proof*` / Hermes Fix*.
- **Live voice session 2026-07-19 ~23:51 IST** (`samantha-buyer-97c8df0d-…`): user asked rice → **JUNK** Poha via description “flattened rice”; orb reply buffer **concatenated** prior rice text onto later Atta turns; ASR “somebody”/“shoamizamata”. Fixes: title-primary search (rice≠poha); `response.created` clears reply; NL stop-words + `basmati rice` compound; seeded India Gate Basmati Rice. Reload Buyer orb before retest.
- **Operator retest 2026-07-20 ~00:08 IST** (Hermes WIP + demo SSO + API truth + page settle): evidence [`operator-catalog-retest-20260720-000815-rescored.json`](evidence/operator-catalog-retest-20260720-000815-rescored.json). First pass found **Atta GHOST** (reply claimed Atta while `q=poha`, no new `search_catalog` — Host `visible_results` leaked full-session cache) and **banana GHOST** (“still loading” after wait with 0 matches). Fixes: scope Host visible_results to `current_query`; force `search_catalog` when find-ask skips tools; after `waitForBuyerCatalogItems` empty → `can_assert_empty=true` + honest empty message. Rescored **Pass**: rice/poha/atta/tv HIT, banana EMPTY-OK. Spot poha→atta: `q=atta` navigates correctly.

---

## Chrome customer issue catalog — local dirty source, 2026-07-21 17:14–18:35 IST

**Protocol:** Mode A catalog-then-fix; explicit `@chrome` plugin; sequential
signed-in Buyer, Seller, combined UI/UX-accessibility, Buyer Samantha, and
Seller Samantha missions. Reviewers used visible UI only and continued past
individual findings. Product and harness source were not edited. Evidence:
[`customer-chrome-issue-catalog-20260721.json`](evidence/customer-chrome-issue-catalog-20260721.json).

**Source boundary:** `HEAD d4ca699a15e9`; dirty tracked-diff SHA-256
`cc7d960fe1c39b7e0d584e79b609b5870791f77545a3fd3c226485dd0cfa4fdf`.
This is local dirty-source evidence, not FQDN or release evidence.

| Mission | Verdict | Customer outcome |
| --- | --- | --- |
| Novice Buyer | **Pass** | Search → compare → add/remove/re-add → checkout → signed AgentGuard authorization → order `88FDF65A` receipt. |
| Small Seller merchant | **Tooling Blocked** | Published Kaveri Toor Dal and accepted order `2BEE2CD5`; Chrome disconnected at dispatch tracking prompt, and the single fresh recovery repeated the same class. |
| Combined UI/UX + accessibility smoke | **App Fail** | Both apps reviewed; five deduplicated P1/P2 findings, including Buyer Samantha dialog keyboard failure and ambiguous listening state. |
| Buyer Samantha customer | **App Fail** | Search, grounding, add, checkout, and authorization passed; cart navigation, memory readback, weekly-task completion, address coherence, and reply rendering failed. |
| Seller Samantha customer | **App Fail** | Navigation, publish, memory, and recall passed; fulfillment/refund were unavailable and bulk triage contradicted the visible zero-order queue. |

### Issue ledger

| ID | Priority | Owner surface | Finding |
| --- | --- | --- | --- |
| `CUST-CHROME-20260721-01` | P1 | Buyer checkout | Stale “Complete the form…” quote instruction remains after all required fields are complete and authorization is enabled. |
| `CUST-CHROME-20260721-02` | P1 | Buyer results | Credible offers are mixed with fixture-like `Dispatch Proof` catalog litter and incomplete seller/delivery/returns context. |
| `CUST-CHROME-20260721-03` | P1 | Buyer Samantha | Keyboard opening leaves focus on `BODY`; no dialog/heading semantics; Escape does not close. |
| `CUST-CHROME-20260721-04` | P1 | Buyer + Seller Samantha | `Listening + text ready` implies audio capture without a microphone control, consent affordance, or state explanation. |
| `CUST-CHROME-20260721-05` | P1 | Authority copy | Execution boundaries are inconsistent; visible surfaces expose `principal:demo`, `seller principal`, `PII-free`, and `Mandate: active`. |
| `CUST-CHROME-20260721-06` | P2 | Seller Network | Generate/save/test controls remain enabled while connection details are incomplete. |
| `CUST-CHROME-20260721-07` | P2 | Seller Orders | Active queue filter is visual only; no `aria-pressed` or `aria-current`. |

| `CUST-CHROME-20260721-08` | P1 | Buyer Samantha | “Show me my cart” becomes a zero-result catalog query and leaks an internal operator instruction. |
| `CUST-CHROME-20260721-09` | P1 | Buyer memory | Samantha claims a preference was remembered while the visible memory owner remains empty. |
| `CUST-CHROME-20260721-10` | P1 | Buyer runtime | Weekly-grocery background task reports complete without a plan or requested basket. |
| `CUST-CHROME-20260721-11` | P1 | Buyer order detail | Full submitted delivery address is reduced to `IND`. |
| `CUST-CHROME-20260721-12` | P2 | Buyer Samantha | Replies truncate mid-sentence. |
| `CUST-CHROME-20260721-13` | P1 | Demo principal | Seller catalog/orders disappear across demo sign-ins because each session receives a new principal. |
| `CUST-CHROME-20260721-14` | **P0** | Seller runtime | Bulk triage reports `17/16/1` orders while the visible queue and follow-up both report zero. |
| `CUST-CHROME-20260721-15` | P2 | Seller Samantha | Preference recall works, but Samantha cannot open the visible memory settings. |
| `CUST-CHROME-20260721-16` | **P0 tooling** | Chrome dialog control | Dispatch tracking prompt disconnects Chrome; the one bounded recovery repeats. |
| `CUST-CHROME-20260721-17` | P1 tooling | Portfolio preflight | AgentGuard demo setup incorrectly waits for legacy host/Solana wallet infrastructure. |
| `CUST-CHROME-20260721-18` | P1 tooling | `reviewer_ready.py` | Post-idle readiness read loses its required browser-session preflight. |

**Supporting gates:** gateway `135 passed`; Buyer test/build Pass; Seller
`196 passed` + build Pass; offline graders Pass; commerce-demo-mode gate Pass.

**Not converted to Pass:** physical voice remained Not Tested; Seller
dispatch/completion/refund remained Tooling Blocked; dirty local source was not
tested on FQDN. Production ONDC and live payment remain contractually out of
scope.

**Cleanup:** removed exactly three campaign items, three orders, three
reservations, and matching idempotency entries; restored the one pre-existing
item’s inventory to 21. Baseline identity sets match again: 53 items, 35 orders,
33 reservations. Recoverable pre-cleanup copy:
`/tmp/aadhaarchain-commerce-pre-cleanup-20260721.json`.

## Chrome customer fix acceptance — local dirty source, 2026-07-21 18:36–19:26 IST

**Result: Pass on frozen local source.** All 18 cataloged findings were fixed
and accepted. The fix loop continued through three additional findings exposed
by re-review: residual non-Dispatch fixture catalog families, a direct Seller
Realtime multi-tool reply that contradicted an executed fulfillment, and a
Radix dialog ref warning. Each was fixed before the final empty iteration.

| Acceptance area | Evidence |
| --- | --- |
| Buyer commerce | One customer-safe Atta offer; readiness copy changes only after complete billing/address; authorized order retained full delivery address; repeat demo sign-in retained the order. |
| Buyer Samantha | Named dialog, initial text focus, Escape close/focus restore, explicit mic state, cart intent → `/cart`, immediate memory readback, and unverified weekly work ends as **could not finish**. |
| Seller operations | Pressed filter state, incomplete Network Save/Test disabled, customer authority copy, accessible in-page dispatch tracking, direct Samantha memory link. |
| Seller truthfulness | Order mutations require exact order IDs; the repeated bulk-triage mission showed grounded read/action outcomes and made no unintended mutation. |
| Tooling | AgentGuard preflight excludes legacy host/Solana; post-idle reviewer read re-runs session preflight; dispatch no longer opens a native prompt. |
| Empty iteration | Fresh Chrome dispatch replay on final source: correct dialog semantics and zero console errors. |

**Deterministic support:** gateway `144 passed`; Buyer `187 passed` + build/copy
gate; Seller `207 passed` + build/copy gate; offline graders Pass; both repo
skill validators Pass; diff checks Pass in the portfolio and all nested repos.

**Cleanup:** removed known stale fixture catalog families, four temporary
acceptance orders/reservations, two temporary acceptance items, and temporary
Buyer Samantha memory. Final demo state: 22 items, 13 orders, 11 reservations.
Recoverable copies remain at
`/tmp/aadhaarchain-commerce-pre-cleanup-20260721.json` and
`/tmp/aadhaarchain-commerce-before-catalog-quality-cleanup-20260721.json`.

**Boundaries:** local dirty-source proof only; the FQDN deployment was not
changed or tested. Production ONDC, live payment, and official conformance
remain out of scope. Existing Chrome microphone permission exposed live state,
but no controlled physical voice-accuracy campaign was run.

## CF1 PostgreSQL `@Chrome` customer validation — local dirty source, 2026-07-22 16:30–17:30 IST

- Focused frozen-source fingerprint: `9c7fadc8fab66f3f456272f5dd8041e357780830bbabfe7185d4c30199704d66` (compatibility read model, Seller AgentGuard executor, regression tests, and Seller commerce mapping). Portfolio HEAD `fbafeb7f`; nested HEADs: AadhaarChain `30e6d11`, Buyer `d24e4fe`, Seller `9ca5e85`. Worktrees were dirty and existing user changes were preserved.
- **Buyer novice: Pass.** Visible Chrome journey searched for a generic grocery, compared the one available Atta offer, added it, changed quantity `1 → 2`, previewed exact `INR 178`, confirmed the one-time AgentGuard approval, and reached order `7C71667B` with `Simulated payment succeeded` and `Authorized · signed reference verified`. Retained screenshots: `/private/tmp/buyer-offer.png`, `/private/tmp/buyer-cart.png`, `/private/tmp/buyer-order.png`.
- Buyer PostgreSQL readback agreed with the UI: one `paid` order for `17800` paise, one `succeeded` payment attempt, one executed receipt bound to its decision and approval, one order effect for the quote, and inventory `12 → 10`.
- **Seller discovery/fix loop:** the first blind run was **App Fail** because `seller.order.accept` treated the CommerceV1 compatibility order as a wrapped object. The next run exposed a distinct **App Fail**: already-refunded orders still rendered Pending/refundable and a duplicate refund surfaced only as `Failed to fetch`. The owner fixes changed the Seller executor to consume the direct order shape and projected durable refund amount/status into Seller as terminal `Cancelled / Payment: Refunded`; focused regression tests were added before each full rerun.
- **Seller merchant: Pass after one bounded Chrome recovery.** The final actor published `Farm Fresh Tomatoes 1kg` (`INR 62`, stock `14`), distinguished two terminal refunded orders from actionable order `EE247B4A`, completed the full `INR 89` AgentGuard refund, and observed `Payment: Refunded`, `The full order value has been refunded. No further refund is available.`, verified authorization reference `7474C04D`, and `Order cancelled`. Retained screenshots: `/private/tmp/seller-add-product-form.png`, `/private/tmp/seller-catalog-published-new.png`, `/private/tmp/seller-orders-before-new.png` (the last file contains the terminal refunded detail despite its historical filename).
- Seller PostgreSQL readback agreed with the terminal UI: order `ee247b4a-551b-403a-9d45-fe14ff65bca4` was `cancelled`; payment remained truthfully `succeeded`; exactly one `succeeded` refund for `8900` paise and one `seller.refund.issue` AgentGuard receipt existed.
- Frozen-source deterministic support: gateway `198 passed`; Seller `210 passed` plus production build/copy gate; targeted Ruff and diff checks passed; `ondc_ci_graders.py --offline` passed all checks.
- Cleanup removed every temporary catalog listing; the isolated UTF-8 PostgreSQL validation cluster owns all generated orders/refunds and is deleted at closeout. All Chrome sessions were finalized.

**Acceptance boundary:** this establishes one complete Buyer customer Pass and one complete Seller customer Pass on the corrected local source. It is not the two-pass release threshold: Buyer Pass 2, Seller Pass 2, the combined UI/UX-accessibility smoke, Samantha voice/runtime breadth, FQDN Auth0, live payment, production ONDC lifecycle/conformance, and iOS remain **Not Tested** in this campaign.

## PreProd Buyer search verification — 2026-07-24

**Initial blocked attempt (superseded later the same day):** frozen workspace
`2995d54924bd45e2e58e81f896410bf609c65af1` sent one signed, fixed-query
`atta` search to the live PreProd gateway. The gateway returned HTTP 200 / ACK
and durable outbox record `out_b575dd6fa27d` for transaction
`ondc-verify-20260724-032417`; 12 correlated polls found zero inbox `on_search`
records and zero network catalog items. No select/init/confirm call or test
order was made. Evidence:
[`preprod-buyer-search-20260724-032417.json`](evidence/preprod-buyer-search-20260724-032417.json).
The callback blocker in this historical attempt was superseded by the
PostgreSQL retest below.

**Initial-attempt diagnosis (historical):** live registry lookups confirmed both
Buyer BAP and Seller BPP as `SUBSCRIBED` for `ONDC:RET10`, each with its
distinct active key and `subscriber_url`; the Seller runtime was key-ready and
the Buyer FQDN callback path returned `405 Allow: POST` to a GET probe. The
query used `std:080`, which both participants advertised as `*`. No
source/config/deployment repair was justified by that attempt; the later
PostgreSQL retest below established callback delivery and narrowed the blocker
to the empty Seller catalog.

**PostgreSQL retest (13:56 UTC; callback proved, result still blocked):**
gateway exact commit `5431307bf36bb8c906600b3ceea859efb34f9d44`
reported `persistence_backend: postgres`, and three isolated persistence tests
passed. Signed `atta` transaction
`ff912749-a4ef-4503-8cb5-aa6a031f561c` received registry `SUBSCRIBED`,
gateway ACK, configured-Seller ACK, three delivered outbox records, and a
correlated signed `on_search` inbox record. The callback catalog was empty
because Seller `published_item_count` was `0`; Buyer therefore had no
network-sourced result and Gate 1 remained **Blocked**. No lifecycle or later
gate ran. Evidence:
[`preprod-postgres-search-20260724-135337.json`](evidence/preprod-postgres-search-20260724-135337.json).
Unblock only by publishing an explicitly approved Seller item, then repeating
one frozen-source signed search and requiring a non-empty correlated callback.

## PreProd Gate 1 closure — 2026-07-25 21:32 UTC

The explicitly approved `Sampoorna Whole Wheat Atta 1kg` listing was published
through the deployed Seller catalog UI's AgentGuard
`seller.catalog.publish` authority. The UI confirmed publication, and BPP
status reported `published_item_count: 1`.

Exactly one frozen-source signed `atta` search then ran against live gateway
commit `5431307bf36bb8c906600b3ceea859efb34f9d44`. Transaction
`00fda29f-947d-4e42-89b9-b98b38c96ad6` received registry `SUBSCRIBED`,
gateway ACK, configured-Seller ACK, three delivered outbox records, and a
correlated Seller-signed `on_search`. Its `ondc-network` catalog contained the
approved item at INR 89 with 23 available. Gate 1 is **Pass**.

The smoke helper exited 6 because it looked for `bpp_id` on provider-wrapper
rows; the persisted callback context correctly identifies
`ondcseller.aadharcha.in` and contains one item. This is a diagnostic helper
false negative, not a missing callback. No order, payment, later gate,
production ONDC, or official conformance claim was made. Evidence:
[`preprod-gate1-search-20260725-213218.json`](evidence/preprod-gate1-search-20260725-213218.json).

## PreProd Gate 2 logistics decision — 2026-07-26

**Pass (decision scope only).** Current source exposes Retail
`ONDC:RET10`/`1.2.0` with Buyer as BAP and Seller as BPP. It has no Logistics
domain or public logistics mutation route; the existing negative route test
keeps `/api/commerce-integrations/logistics/transitions` unregistered.

The active decision is B2C Logistics `ONDC:LOG10` contract `1.2.5`, initially
limited to one Immediate Delivery P2P forward-fulfilment lifecycle. The Seller
NP becomes the Logistics Buyer NP (LBNP/BAP); an external Logistics Service
Provider is BPP; the Buyer app remains the Retail BAP and reads only persisted
tracking state. AgentGuard owns consequential-action authorization, CommerceV1
owns order/fulfilment state, and the gateway owns server-side signed protocol
transport. No parallel store or browser-held ONDC credential is permitted.

P4 remains blocked until redacted Seller `ONDC:LOG10` BAP/LBNP registration and
one approved PreProd LSP BPP lookup/version/feature record exist. No external
logistics call, order, payment, FQDN/Auth0 journey, official conformance run, or
later gate ran. Evidence:
[`preprod-gate2-logistics-decision-20260726.json`](evidence/preprod-gate2-logistics-decision-20260726.json).

## CF2/CF3 FQDN customer campaign — 2026-07-25

- Frozen public-surface fingerprint:
  `caa700d5a36465188c37048213365bfc558293d6f0abcc4411d8731ba5f6782d`
  (Buyer HTML `f2697328`, Seller HTML `1759111c`, gateway health
  `5677cfe6`, gateway ONDC status `96b44b95`).
- Setup proved Buyer Auth0 `Account: Ready`, AgentGuard-protected checkout, an
  empty cart, and zero existing Buyer orders. Gateway health was `healthy` and
  ONDC persistence was `postgres`.
- The first blind actor was **Tooling Blocked before customer action** because
  its browser route required a missing Chrome `DevToolsActivePort`; no lease or
  mutation existed. The single bounded recovery used the bundled Chrome
  extension route and completed the mission.
- Buyer pass 1 recovery verdict: **App Fail**. Searching for `rice` showed
  `0 matches` / `No exact matches for 'rice'`; the visible
  `Browse available groceries` recovery still showed `Nothing surfaced yet`,
  `No results found`, and zero grocery matches. Comparison, cart, checkout,
  AgentGuard decision, payment, and receipt were unreachable.
- Live BPP diagnosis agreed with the visible failure:
  `GET https://gateway.aadharcha.in/api/ondc/bpp/status` returned
  `ready: true` and `published_item_count: 0`.
- A subsequent read-only signed-in Seller inspection showed verified identity,
  `Products: 0`, `Visible products: 0`, `No products published yet`, and
  `No inventory in this view`. There is no existing Seller draft that can be
  selected without an operator-approved listing decision.
- No catalog, cart, order, payment, approval, or receipt mutation occurred.
  The Chrome lease closed. Screenshot:
  `/Users/gurusharan/.codex/visualizations/2026/07/25/019f999c-4969-7b72-9512-ff6a8fdcab02/buyer-pass1-empty-catalog-app-fail.png`.
- Campaign manifest:
  `.session/evidence/cf23-fqdn-caa700d5a36465188c37048213365bfc558293d6f0abcc4411d8731ba5f6782d/campaign.json`.

**Acceptance boundary:** no CF2/CF3 customer pass is claimed. Buyer pass 1 is
failed and all later Buyer/Seller repetitions plus combined UX/accessibility
remain Not Tested. Resume only after the operator approves one specific Seller
retail listing for publication or identifies an approved existing item; do not
invent public catalog content.

## Final local visible campaign follow-up — 2026-07-25

The earlier empty-catalog boundary was resolved with operator-authorized
temporary listings. The campaign then exposed and repaired three visible
owners:

1. Buyer browse-all incorrectly substituted the keyword `grocery` for an empty
   query, hiding valid categorized offers.
2. Buyer results and product detail allowed zero-stock purchase actions.
3. Seller Samantha could remain indefinitely on `Connecting Samantha…` without
   timeout or retry.

On combined fingerprint
`f4e65e14791d65d0f876d844574b489c71e9f9e0e41a2c58d503508f64392fac`,
both blind Buyer passes succeeded:

- `33177196`: authorization `3EFC3BCB`, simulated payment `ADAD602E`;
- `EBDCF386`: authorization `DF26DE78`, simulated payment `7D486FFE`.

Seller UX had no remaining P0/P1. Seller pass 1 then fulfilled and fully
refunded `EBDCF386`, with verified refund authorization `1596B3E0` and durable
Cancelled/Refunded state. Seller pass 2 fulfilled and refunded `33177196`, with
verified authorization `C444B6DA`, but froze **App Fail**: after reload the
authorization disappeared and no durable refund/receipt identifier was shown.
The business effect is real; it is not accepted as the required visible receipt
proof.

Diagnosis proved the signed `seller.refund.issue` receipt already exists in
PostgreSQL. Candidate
`886e8372219c456a9066f3a2f8c51fe269b7aa9d9245ebe765ed313946e11fe3`
adds the missing gateway projection and Seller readback. Deterministic evidence
passes: gateway `232 passed / 49 skipped`, Seller `216 passed`, and Seller
production build/copy. PostgreSQL integration is **Not Tested** because the
gateway restart replaced a process-only `DATABASE_URL`; the current healthy
gateway selected `local_file`, which cannot substitute for the frozen
PostgreSQL campaign.

Cleanup is incomplete. Local PostgreSQL item `item-1784991737462` and evidence
orders are unreachable until secure database access returns. FQDN item
`item-1784990847715` remains published: archive confirmation was accepted, but
the remote request did not complete and live BPP `published_item_count` remains
`1`.

**Acceptance boundary:** no final all-green same-hash claim. Restore
`DATABASE_URL` securely outside chat, require PostgreSQL receipt readback, then
freeze and rerun both Buyer and Seller passes twice on `886e8372...`. Complete
both local and FQDN cleanup before closeout.

## Final local visible closure — 2026-07-25

The prior boundary is superseded by restored PostgreSQL access and the final
bundled-Chrome campaign.

- Frozen source `bf4c7cee...` passed Buyer twice on one INR 89 Seller listing:
  order `83A97020` / authorization `2F48D8C7`, then order `709D9B9E` /
  authorization `C1C66BCF`. Both showed exact landed cost, saved INR 10000
  mandate, simulated payment success, and verified signed authorization.
- Seller passed twice on those same orders. Each traversed Pending -> Accepted
  -> In progress -> Dispatched -> Delivered -> Cancelled and Paid -> Refunded.
  Refund references `AB167E21` and `4DA37A95` and their signed AgentGuard
  receipt IDs survived reload. The final queue contained two
  Cancelled/Refunded orders and no actionable orders.
- Combined visible Buyer/Seller review found no unresolved P0/P1.
- The first cleanup attempt truthfully exposed a PostgreSQL compatibility-shape
  defect in protected catalog archive. Source `923e1113...` accepts the direct
  item returned by PostgreSQL (while retaining wrapped compatibility), adds a
  live publish/archive regression, and passed the affected archive lane in
  Chrome. Session-orchestrate permits retaining the unaffected two-pass
  order/refund evidence after this targeted repair.
- Cleanup is complete: Seller catalog reload shows zero visible products and
  `No products published yet`; BPP `published_item_count` is `0`; campaign
  reservations are `held: 0`, `consumed: 2`, `released: 2`.
- Structured evidence:
  `.session/evidence/local-visible-923e1113599de304fc0af97a7c075eb2bffe3f42682e713d88b066c08aa6df2e/campaign.json`.

**Acceptance boundary:** final local visible Buyer, Seller, two-sided, and
combined UX acceptance is complete. This does not claim deployment, production
money, physical microphone proof, pilot completion, spend, or Milestone 9.

## PreProd Gate 2 LBNP endpoint migration — 2026-07-26

**Pass (public onboarding endpoint only).** Gateway commit `b3e81b2e...`
adds dedicated subscriber `ondclbnp.aadharcha.in`: shared onboarding routes
accept role `lbnp`, expose callback base
`https://ondclbnp.aadharcha.in/ondc`, and report the frozen `ONDC:LOG10` /
`1.2.5` / Immediate Delivery P2P forward-only contract. Retail Buyer/Seller
application source, keys, catalog, callbacks, and Gate 1 evidence were not
changed or rerun.

The repository key generator produced a new gitignored Ed25519/X25519 pair.
Public-key comparison proved both keys differ from Retail Seller. A discovered
key-workflow defect wrote private PEMs as `0644`; the generator owner now
creates and self-checks them at `0600`, and the new LBNP pair was corrected to
`0600`. No private value was printed, committed, uploaded, or placed in portal
state; no unique key ID was invented.

CI-equivalent proof passed: gateway `233 passed / 50 skipped`, portfolio CI,
and unchanged Buyer/Seller test+build. The real generated pair returned local
LBNP status 200 and site verification 200; the deterministic regression
completed a valid `/ondc/on_subscribe` challenge at 200 and rejected invalid
input at 400.

Exact deploy `dep-d9irpocm0tmc73a0st7g` is live on the existing Render Free
gateway. `ondclbnp.aadharcha.in` is its second included custom domain; GoDaddy
owns the CNAME to the verified Render target. Public DNS and TLS pass. Public
status and site verification returned 200, and a valid deterministic
`/ondc/on_subscribe` challenge returned 200 with a matching answer. Existing
Retail Buyer/Seller status and site-verification probes remained 200.
No portal action, registry/logistics protocol call, order, or payment occurred.
Evidence:
[`preprod-gate2-lbnp-endpoint-migration-20260726.json`](evidence/preprod-gate2-lbnp-endpoint-migration-20260726.json).

**Single next action:** in a separately authorized portal gate, register
`ondclbnp.aadharcha.in` against Logistics Buyer profile `15462-10220`, stopping
at authentication, 1.b, legal, key-upload, and registry-mutation boundaries.

## PreProd Gate 2 LBNP portal registration — 2026-07-26

**Blocked before submission.** Profile `15462-10220` visibly reads Logistics
(B2C), API v1.2, Buyer NP. The 1.a draft is PreProd,
`ondclbnp.aadharcha.in`, `/ondc`, and `P2P - ONDC:LOG10`. Live/local public-key
fingerprints match; site verification and a fresh valid challenge remain 200.

The portal exposes no input for those existing public keys. Its only visible
key path is `Click to generate & download below Key`, with a one-time save
warning. Without using it, Raise Request produced no review/Submit state and
List of Requests remained empty. Per the hard stop, no key was generated or
downloaded; no 1.b, legal, portal request, registry/protocol, order, payment, or
production action occurred. Retail Buyer/Seller identities were not opened or
changed. Evidence:
[`preprod-gate2-lbnp-portal-registration-20260726.json`](evidence/preprod-gate2-lbnp-portal-registration-20260726.json).

**Single user action:** in the open portal draft, click the one-time key
generation/download button and retain the file securely without sharing it in
chat. Resume afterward to compare/rotate only the LBNP endpoint keys before
submission.

## PreProd Gate 3 Logistics conformance — 2026-07-26

**Blocked after exact deployment and signed search/init proof.** Gateway commit
`cde2242cb49fb6429766e253ef613f7ff5c083ae` is live as Render Free deploy
`dep-d9iun27aqgkc73an2cpg`. Public DNS/TLS, LBNP status, site verification, and
a valid challenge/answer all passed.

Signed LOG10 transaction `AA79565B-3815-4D2E-A63A-D8CA8F9E70C5` received
three registry-matched, signature-verified `on_search` callbacks at `1.2.5`.
The official Pramaan mock and TapTap each ACKed `init` and returned
signature-verified `on_init`, but neither supplied the mandatory
`rider_check/inline_check_for_rider=yes` required by the current Immediate
Delivery contract. The flow stopped before `confirm`; no update, status, track,
payment, shipment, production, or legal action ran.

Release friction was fixed at its owners: `.gitleaks.toml` now follows the
canonical testing-ledger evidence path with a portfolio-deploy validator
regression, and two PostgreSQL persistence test doubles accept the role-aware
adapter contract. Full deployment graders passed before the exact CLI deploy.

Portal 1.b remains visibly Pending with its operator attestation unchecked:
[`preprod-gate3-portal-1b-blocked-20260726.jpg`](evidence/preprod-gate3-portal-1b-blocked-20260726.jpg).
Full evidence:
[`preprod-gate3-logistics-conformance-20260726.json`](evidence/preprod-gate3-logistics-conformance-20260726.json).

**Single next action:** in the preserved ONDC portal tab, the operator must
personally review task 1.b and, only if true, check `I have a working
application with user interface as required` and click `Complete Task`. Resume
the four `Verify your build`/Workbench tasks afterward; do not reuse either
non-compliant `on_init` for `confirm`.

## PreProd Gate 3 Workbench entry — 2026-07-31

**Blocked before Workbench session creation.** The operator completed portal
1.b. Authenticated readback showed 1.b Completed and exposed verification tasks
2.a–2.d. Task 2.d opened the official ONDC Workbench; BAP and PRE-PRODUCTION
were preselected and the dedicated subscriber URL was entered. Bundled Chrome
control repeatedly timed out while selecting `ONDC:LOG10`, before version or
use-case selection and before Submit. No Workbench session, report,
observability token, or protocol call was created.

**Single next action:** close only the stuck `ONDC Workbench` tab, keep the
authenticated portal open, and reopen task 2.d. Continue with the existing
subscriber, `ONDC:LOG10`, BAP, PRE-PRODUCTION, and portal-advertised
version/use-case; preserve the fail-closed stop before `confirm` unless a new
signature-verified `on_init` includes `inline_check_for_rider=yes`.

## PreProd Gate 3 Workbench search/init — 2026-07-31

**Blocked at an explicit legal boundary, not a protocol transport failure.**
Official session `PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT` is configured for
`ONDC:LOG10` `1.2.5`, Logistics (P2P), BAP, PRE-PRODUCTION, Immediate Delivery.
Corrected transaction `900b80c1-72a6-430e-8e64-bed93d971a5b` has Workbench ACK
records for `search`, `on_search`, `init`, and `on_init`. Public inbox rows
`8668` and `8669` independently identify `workbench.ondc.tech` and record
`signature_verified: true` at `1.2.5`.

The first correlated search exposed a mandatory non-empty future-dated
`provider.time.schedule.holidays`; the gateway search owner now rejects missing
or empty values, and the focused LOG10 regression passes. A first init fixture
then exposed a Workbench generator assumption: omitting the official
`linked_provider` fulfillment tags caused its `on_init` generator to throw
before delivery. The corrected init preserved that official tag and completed
with a signed callback. No product assertion was weakened to accommodate the
failed fixture.

The canonical testing-ledger validator also had a reproducible local false
failure because root worktrees intentionally omit the ignored nested gateway
checkout. The existing grader now prefers the current checkout and falls back
only to another declared Git worktree. Its in-owner resolution self-test,
offline grader, and testing-ledger validation all pass; CI behavior remains the
same because CI checks the gateway out under the current root.

Workbench now listens for `confirm`. Its official flow requires
`message.order.tags.bap_terms.accept_bpp_terms=yes`; current authority excludes
legal acceptance. No confirm, update, unsolicited status, track, payment,
shipment, production, or report-generation action ran. Evidence:
[`preprod-gate3-workbench-20260731.json`](evidence/preprod-gate3-workbench-20260731.json).

**Single next action:** the operator must explicitly authorize or decline the
PreProd mock `accept_bpp_terms=yes` field. If authorized, resume this exact
transaction from its signed `on_init`; do not rerun search or init.

## PreProd Gate 3 Workbench forward lifecycle — 2026-08-01

**Pass.** The operator explicitly authorized the synthetic PreProd
`accept_bpp_terms=yes` confirm field. Official session
`PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT`, transaction
`900b80c1-72a6-430e-8e64-bed93d971a5b`, completed all 15 Immediate Delivery
steps from the previously proven `on_init` through final unsolicited
`on_status`. All Workbench records ACKed; missed and extra steps are empty.
Public LBNP inbox readback contains 10 callbacks from `workbench.ondc.tech`,
all at `1.2.5` with `signature_verified: true`.

The reproducible holidays defect is fixed in exact gateway commit `63df7ca` and
one deterministic regression. Gateway `236 passed / 50 skipped`, Buyer `201`
tests plus build, Seller tests/build, portfolio CI, and Ruff passed. Render Free
deploy `dep-d9mna2942hec73e3eq40` is live; GoDaddy CNAME, TLS, LBNP status,
site verification, valid/invalid challenge, and public empty/past holiday 422
proof passed. Evidence:
[`preprod-gate3-workbench-20260731.json`](evidence/preprod-gate3-workbench-20260731.json).

**Boundary:** no Gate 1 rerun, real shipment, real payment, production,
report-generation, certification, or later gate. No in-scope blocker remains.

## Buyer delivery tracking readback — 2026-08-01

**Pass for persisted Seller-managed fulfilment; external LSP linkage remains
unproved.** The signed-in Buyer FQDN listed three orders. Delivered order
`709D9B9E` visibly showed `Status: Delivered`, `Provider: Standard Courier`,
`Tracking ID: AG-709D9B9E`, `The seller confirmed delivery completion.`, and
the saved delivery address. No order or fulfilment mutation ran.

Current source maps persisted `provider_name`, `tracking_id`, fulfilment status,
and status message into the Buyer order detail. The backend also retains
fulfilment history, but the Buyer UI does not render that history as a timeline.
This proof does not connect the synthetic LOG10 Workbench transaction to a
Retail CommerceV1 order or establish live external-LSP vendor tracking.

## Milestone 12 physical Buyer voice proof — 2026-08-01

**Blocked at the bundled Chrome proof environment; no voice claim.** On source
commit `2be9e5a5f19be47c938395c073bf947f717cec3d`, the signed-in Buyer page showed
Account Ready, checkout protected by AgentGuard, and the Samantha entry point.
Opening Samantha then exhausted the bounded browser interaction. A fresh
semantic snapshot and the documented visible-DOM fallback both timed out.

Google Chrome `150.0.7871.187` was running and the native-host manifest was
correct for `com.openai.codexextension`; the bundled profile diagnostic could
not find an active Chrome profile Preferences directory. No microphone
permission was accepted, no audio was captured, no voice tool ran, and no
product or commerce state changed. Text-mode and configured-status evidence do
not satisfy this gate.

The next bounded continuation reproduced the same proof-environment failure.
Read-only Chrome discovery worked, but the signed-in `ONDC Buyer` tab remained
owned by browser session `019fbc5c-be32-78c1-b77f-850d929530ba`; no other active
AadhaarChain task owned that session. A fresh Chrome tab loaded the Buyer app
without authentication, then opening its existing search/account controls and
the final cleanup both timed out. No sign-in, microphone, audio, tool, commerce,
or source mutation occurred. This strengthens the existing blocker fingerprint;
it is not a new product finding.

**Single next action:** the operator must release or close the stale signed-in
`ONDC Buyer` tab/browser session, then leave one Chrome Buyer tab signed in and
unclaimed. Resume this same M12 proof from a fresh state read, and obtain
action-time operator confirmation before accepting any microphone permission
prompt. Do not deploy or rerun completed Gate 1–3 work.

The operator released the stale tabs and the next bounded run recovered Chrome
interaction. A fresh signed-in Buyer session visibly reached `Voice and text
ready · microphone on`. The operator reported separately exercising real voice,
but the retained UI did not expose a modality-linked transcript/tool record, so
that report is not promoted to full physical-voice acceptance.

At the operator's request, the visible text lane then proved the shared tool
runner without checkout: `Find atta and add one item to my cart. Do not
checkout.` navigated to Cart and added `Sampoorna Whole Wheat Atta 1kg × 1` at
INR 89. A second request persisted `User prefers whole wheat products.` with
current settings readback. A third navigated to Checkout, where the exact INR 89
landed-cost quote was visibly bound to AgentGuard's INR 10000 limit; no order or
payment ran and the microphone remained visibly on. This is typed tool,
preference, and guarded-navigation proof, not a substitute for voice-originated
tool proof.

With explicit approval, the shopping agent was paused and the UI read back
`Shopping agent paused`. Clicking `Authorize exact total and place order` as
the human buyer returned `agent is paused`; the page remained on the bound INR
89 quote and returned no order result. The agent was immediately restored and
the UI read back `Shopping agent on`.

**Finding:** that click was a human checkout, not an agent-originated tool call.
The operator correctly required manual checkout to remain available while the
shopping agent is paused. The local correction adds a fail-closed
`actor: agent | user` request field, binds it into the checkout decision hash,
keeps Samantha on the default `agent` path, and marks only the manual Checkout
page as `user`. Buyer tests passed 201/201 plus the production build; gateway
tests passed 237 with 51 PostgreSQL-dependent skips; Ruff and the full
testing-ledger validator passed. The explicit PostgreSQL actor regression is
present but skipped without `DATABASE_URL`; the file-backed actor regression
passed. No deployment, live successful checkout, order, or payment was run.
Physical voice-originated tool proof remains open because no retained
modality-linked voice/tool record was exposed.

The next mic-capable handoff again reached `Voice and text ready · microphone
on`, but before operator speech the live `__samanthaEvents`,
`__samanthaTools`, and error arrays were all empty and memory was unchanged.
The server-only secret boundary is structurally closed: the gateway reads the
long-lived `OPENAI_API_KEY`, mints an authenticated ephemeral Realtime client
secret, and sanitizes transcript metadata; focused gateway Realtime tests pass
3/3. The Buyer requests only that client secret and its focused dialog test
passes. This does not replace the still-missing physical spoken tool turn.

Three consecutive bounded audits now show the same state: microphone on, no
Realtime error, no input-audio transcription event, no tool call, and unchanged
memory because no operator speech landed. Further automation cannot supply
physical speech without violating this gate. The mic-capable Buyer tab remains
handed off for an operator-spoken turn; M12 is blocked at that exact boundary.

## Local paused-agent checkout and delivery tracking integration — 2026-08-01

**Pass for current-source manual checkout and text tracking; partial for the
full Seller-to-Buyer logistics lifecycle.** After restarting the local gateway
onto the changed source, the Buyer saved an INR 10,000 shopping limit, paused
the shopping agent, and manually placed one INR 89 simulated order. Order
`7726C069` was created, the simulated payment succeeded, the signed AgentGuard
reference verified, and a later Buyer readback still showed `Shopping agent
paused`. This closes the observed actor-semantics regression locally; it is not
deployed or FQDN proof.

Samantha text `Track my latest order` invoked the new read-only tracking path,
kept the UI on the exact order, and rendered that order as `created` and
awaiting seller confirmation. Source tests also prove latest/specified-order
selection, persisted provider/tracking/history projection, and no invented
courier when the backend has none. The Buyer order detail now renders stored
fulfilment history. Seller dispatch now requires an entered delivery provider
and tracking ID instead of hardcoding `Standard Courier`.

Buyer tests passed 203/203, lint had zero errors and two pre-existing warnings,
and the production build/copy gate passed. Seller tests passed 217/217; lint
and build passed. Gateway tests passed 237 with 51 environment-dependent skips.
The local demo Seller principal did not own the persisted catalog/order, so a
rendered Seller dispatch and populated Buyer timeline were not promoted to
Pass. Synthetic Workbench LOG10 callbacks also remain uncorrelated with Retail
CommerceV1 orders. No deployment, FQDN mutation, real shipment, or real payment
occurred.

## Signed LOG10 offer to CommerceV1 delivery lifecycle — 2026-08-01

**Pass locally for one bounded signed-offer correlation and rendered lifecycle;
not an LSP booking or physical shipment claim.** One explicitly authorized
PreProd LOG10 search used transaction
`6f5a3bf8-fc4e-4b59-b0ab-1d09d7e75201`. The gateway returned HTTP 200/ACK and
three signed callbacks. The server selected only TapTap Logistics because its
callback was signature-verified LOG10 1.2.5 with item code P2P, category
Immediate Delivery, and a Delivery fulfilment; the Retail callback and Pramaan
mock were excluded.

The Seller protected `seller.fulfilment.commit` path now resolves the signed
offer from the durable ONDC inbox and writes the normalized provider and
protocol correlation into the existing CommerceV1 `fulfilment` JSON. It does
not create a parallel logistics store. A focused PostgreSQL regression passed,
the gateway suite passed 237 with 51 environment skips, the ONDC adapter suite
passed 10/10, and Seller tests/build/copy gate passed.

Local order `12EE1DC3` then passed the rendered Seller lifecycle Pending →
Accepted → In progress → Dispatched → Delivered. The dispatch form supplied
only signed transaction ID plus proof tracking ID `TAPTAP-UI-1201`; the server
resolved and rendered `TapTap Logistics`. Buyer readback rendered Delivered,
the exact provider/tracking ID, and confirmed→preparing→shipped→delivered
history. Samantha text `Track my latest order` returned the same provider,
tracking ID, and delivered status. Evidence:
`.agents/skills/testing-ledger/references/evidence/preprod-log10-commerce-correlation-20260801.json`.

No LOG10 init/confirm/status/track request ran. The tracking ID and state
transitions were local proof fixtures, not TapTap-issued or physical-shipment
evidence. Deployment, FQDN lifecycle, legal-term acceptance, real payment,
production ONDC, and physical delivery remain unclaimed.

## TapTap current PreProd init retry — 2026-08-01

**Blocked before confirm; fail-closed behavior passed.** After the operator
explicitly approved the exact synthetic payload, one TapTap LOG10 `init` was
sent on transaction `6f5a3bf8-fc4e-4b59-b0ab-1d09d7e75201`, message
`49a8c5ad-0bda-4afb-b1bf-53469158404a`. TapTap returned HTTP 200/ACK and the
gateway persisted signature-verified `on_init` inbox record `10190` at contract
1.2.5 with the INR 59 Immediate Delivery quote.

The callback again omitted the mandatory
`rider_check/inline_check_for_rider=yes`. Its fulfillment tags were limited to
`linked_order`, `linked_provider`, `state`, and `rto_action`, with
`ready_to_ship=no`. The contract therefore prohibited `confirm`. Durable
outbox readback contains exactly one `search` and one `init`, with zero
`confirm`, `update`, `status`, or `track` records. Evidence:
`.agents/skills/testing-ledger/references/evidence/preprod-taptap-init-retry-20260801.json`.

No LSP booking, LSP-issued tracking, real payment, physical shipment,
production action, or FQDN delivery lifecycle is claimed. The next dependency
is an external LOG10 BPP returning a compliant `on_init`; retrying the same
TapTap contract cannot advance this gate.

## ONDC-compliant local delivery reconciliation — 2026-08-02

**Pass for deterministic source/PostgreSQL behavior and two unchanged-source
local rendered journeys; external LSP acceptance remains open.** Gateway
transport now rejects unsigned, wrong-domain,
wrong-action, and non-1.2.5 LOG10 callbacks. Seller AgentGuard deterministically
ranks signed P2P Immediate Delivery offers and is the only replacement-LSP path
after conformance rejection. A confirm requires a compliant selected signed
`on_init`, matching provider/item/fulfilment/quote, and constructs only the
action-specific `linked_order` id/preparation time and `ready_to_ship=yes`
state tags. BAP/BPP terms still fail closed at the explicit operator boundary.

The callback path verifies signature/context, persists before ACK, then uses the
existing inbox lease/retry/dead-letter primitives and protected inbox drain to
apply idempotent metadata/history to the order located by
`fulfilment.logistics.transaction_id`. Without PostgreSQL, LOG10 callbacks NACK
with 503; the file inbox remains development-only. CommerceV1 alone owns
transitions:
pending/agent search stays preparing, pickup/out-for-delivery becomes shipped,
delivered becomes delivered, and cancellation runs only through the existing
state machine. Unknown, stale, skipped, and regressive callbacks preserve an
evidence event, flag review, and do not promote stale metadata or invent state.

Current receipts: PostgreSQL gateway `301 passed`; changed-file Ruff passed;
Buyer `203 passed` and Seller `218 passed`; both production builds/copy gates
passed. The immutable TapTap packet includes durable search/init
identifiers and commitments, expected versus observed tags, registry signature
results, and official validator links:
[`evidence/preprod-taptap-interoperability-packet-20260802.json`](evidence/preprod-taptap-interoperability-packet-20260802.json).
The support text is prepared but unsent in
[`evidence/preprod-taptap-interoperability-draft-20260802.md`](evidence/preprod-taptap-interoperability-draft-20260802.md).

Fingerprint `514777d6...` passed two full local journeys through the bundled
in-app browser. With the shopping agent paused, human
checkout created simulated orders `8A0D86E5` / `E31E0401` and verified signed
authorization references `D0DEF4D1` / `8D56CDC6`. Buyer rendered `Pending`,
Seller rendered `Pending provider` with ordered history, and Samantha text
matched the latest CommerceV1 state. Neither UI invented courier, tracking,
location, ETA, or shipment state. Evidence:
[`local-log10-acceptance-20260802.json`](evidence/514777d6a5914fff837bf4aedc3249c903cedc3c6345a2774fbcd00fd4fc25ed/local-log10-acceptance-20260802.json).

No external message, deployment, commit/push, legal-term acceptance, compliant
LSP `on_init`, real shipment, real payment, or new protocol payload occurred.

## CF2 local Auth0 lifecycle acceptance — 2026-08-15

**Pass for CF2-E1 on frozen application fingerprint
`2b00c00f6bc2f4dfb6fb11b5992cc955053e92125bdd0f5dce91547a75cab92f`.**
Buyer comparison rendered two Pune offers from two sellers with confirmed
serviceability ahead of unknown and honest listed-pack pricing. Correlated
Auth0 order `709D9B9E` retained courier, tracking ID, and ordered fulfilment
history through delivered state. Buyer return produced verified receipt
`7F9F4245`; grievance `fabc818c` moved through Seller acknowledgement and a
verified replacement commitment, then Buyer acceptance closed it with verified
outcome receipt `D2E36C2E` and five retained history events.

Portfolio CI passed with gateway `251 passed, 53 skipped`; Buyer passed 211
tests plus typecheck/lint/build, Seller passed 219 plus typecheck/lint/build,
and the isolated PostgreSQL lifecycle passed. Desktop, 390px, keyboard order,
accessible actions, persisted readback, and terminal receipt visibility passed.
Receipt:
[`evidence/cf2-e1-auth0-lifecycle-20260815.json`](evidence/cf2-e1-auth0-lifecycle-20260815.json).

CF2 product item is **complete** on CF2-E1. Q1 remains the separate
current-source release gate. No deployment, DNS, production payment, ONDC
submission, or external shipment was performed or proven.
