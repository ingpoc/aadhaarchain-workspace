# AgentGuard Commerce Implementation Plan

## How to use this plan

This is the execution owner for building the AgentGuard demonstration defined in
`PRODUCTIDEA.md`, `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`, and
`ARCHITECTURE.md`. A new agent should read `AGENTS.md` (routing), those files,
this plan, and `TESTINGPLAN.md` before editing.

Work in milestone order. Do not build later milestones around placeholders from
an earlier one. Every milestone ends only when its acceptance tests pass and its
status is recorded in the progress table. If repository reality contradicts
this plan, stop, update the owner document with evidence, and then implement;
do not invent a parallel contract.

## Target outcome

Deliver one honest, local, two-sided commerce demonstration:

1. Seller confirms bounded authority for an operations agent.
2. Seller agent publishes a product with inventory.
3. Buyer agent discovers that exact product and prepares a cart.
4. AgentGuard allows a routine checkout or requests exact approval.
5. Simulated payment produces one shared order visible to Seller.
6. Seller agent accepts and progresses fulfilment under its mandate.
7. Buyer opens an issue; Seller drafts a response and proposes a remedy/refund.
8. AgentGuard guards the remedy, rejects replay, and rejects action after pause.
9. Buyer and Seller show human-readable, verifiable Intent Receipts.

The demo must label ONDC exchange, payment, logistics, and settlement as
simulated. AgentGuard authorization, atomic approval consumption, pause, server
enforcement, and receipt integrity must be real.

## Non-negotiable invariants

- AI output is an untrusted proposal, never an authorization decision.
- Every protected mutation re-evaluates authority on the server that executes
  or owns the mutation.
- The authenticated principal is derived server-side; callers cannot select
  another principal by submitting a wallet or subject ID.
- Approval is bound to one canonical action envelope and consumed atomically.
- Duplicate delivery never duplicates order, inventory, payment, refund, or
  receipt effects.
- Pause and revocation are checked immediately before execution.
- AgentGuard stores minimum metadata and commitments, not raw identity, address,
  cart, conversation, payment credential, or order evidence.
- No PIN, OTP, private key, broad session credential, or administrator secret is
  placed in model context.
- Buyer and Seller use one action, decision, approval, and receipt protocol.
- Unsupported protected actions fail closed.
- Blockchain, Aadhaar, Solana, and live NPCI access are not dependencies.

## Current-state inventory

### Keep and evolve

| Surface | Current owner | What is reusable |
| --- | --- | --- |
| AgentGuard domain | `aadharchain/gateway/app/agentguard.py` plus `aadharchain/gateway/app/persistence/agentguard_repository.py` | PostgreSQL-backed mandates, decisions, exact one-time approvals, pause/revoke and receipts when `DATABASE_URL` selects CF1 PostgreSQL |
| AgentGuard HTTP | `aadharchain/gateway/app/agentguard_routes.py` | Ensure/status/evaluate/consume/pause/receipt route skeleton |
| Gateway tests | `aadharchain/gateway/tests/test_agentguard.py` | Refund and checkout allow, approval, replay and pause proof |
| Buyer guard client | `ondcbuyer/src/lib/agentGuardCheckout.ts` | Exact checkout evaluation, approval, protected execution and receipt client |
| Seller guard client | `ondcseller/src/lib/agentGuardClient.ts` | Status/evaluate/execute/pause and receipt client |
| CommerceV1 | `aadharchain/gateway/app/commerce_v1.py` | Durable single-seller carts, quotes, inventory reservations, orders, payment attempts, ledger entries and refunds |
| Commerce compatibility | `aadharchain/gateway/app/commerce_compat.py` | `/api/demo-commerce` request/response compatibility over the process-selected commerce owner; not an independent store |
| ONDC messaging | `aadharchain/gateway/app/persistence/ondc_repository.py` | Durable inbox/outbox, persist-before-ACK, deduplication, correlation, leases, retries and dead-letter recovery |
| Agent proposal parsers | `ondcbuyer/src/lib/agentBuyerState.ts`, `ondcseller/src/lib/agentSellerState.ts` | Typed proposal normalization and staging patterns |
| Mutation authority inventory | `aadharchain/gateway/app/mutation_inventory.py` | Executable CF0 classification for every non-safe route; completeness fails closed on an unknown route family |
| Browser framework | `scripts/portfolio_browser.py` and Hermes scripts | Preflight, SSO, fixture and evidence foundation |
| Shared identity helper | `shared/trust-client/src/index.ts` | Optional host assurance adapter during migration |

### Known gaps

- Decision Contract v2 is frozen across the canonical, Buyer and Seller
  packages with policy, risk, required action, expiry and decision identifiers.
  V1 is compatibility-only and cannot authorize; its deletion gate is recorded
  in the contract README and `ARCHITECTURE.md`.
- Mandate editors cover the demo actions and limits, not the complete Buyer and
  Seller production mandate.
- The CF1 commerce foundation is durable in PostgreSQL when `DATABASE_URL`
  selects that process backend. CommerceV1 owns carts, quotes, inventory,
  orders, simulated payment attempts, ledger entries and refunds;
  `/api/demo-commerce` is a compatibility adapter, not a second state owner.
  Multi-seller checkout, fulfilment, returns, settlement and regulated payment
  remain production gaps.
- Buyer and Seller prove bounded demo journeys, not the complete search-to-
  remedy and onboarding-to-settlement customer lifecycles.
- ONDC search is PreProd partial; official onboarding, conformance, and the full
  asynchronous transaction lifecycle remain incomplete.
- Browser Realtime and text tools exist, but native voice, physical-audio proof,
  reconnect, latency/cost telemetry, and voice evaluations remain open.
- No iOS application, Face ID approval flow, App Intents, Live Activities, or
  on-device intelligence router exists in this workspace.
- Production privacy classification, observability, support, reconciliation,
  incident response, and global autonomous-action pause remain launch gates.

## Target repository shape

Prefer this shape unless an existing owner demonstrably fits better:

```text
shared/
  agentguard-contract/       TypeScript schemas, canonicalization, reason codes
aadharchain/gateway/app/
  agentguard.py              Domain service during migration
  agentguard_routes.py       Identity-neutral authenticated API
  commerce_v1.py             Durable cart/order/payment-ledger owner
  commerce_v1_routes.py      Versioned Buyer/Seller commerce API
  commerce_compat.py         Legacy request/response adapter only
  persistence/               PostgreSQL repositories and migrations
  receipt_signing.py         Keyed receipt issue and verify
  realtime_session.py        Ephemeral OpenAI Realtime client secrets (M12)
ondcbuyer/src/
  lib/agentGuardClient.ts    Shared-contract client
  lib/commerceClient.ts      Compatibility client over CommerceV1
  lib/agentTools.ts          Tool runner (search, navigate, cart, checkout)
ondcseller/src/
  lib/agentGuardClient.ts    Shared-contract client
  lib/commerceClient.ts      Compatibility client over CommerceV1
  lib/agentTools.ts          Tool runner (publish, refund, order tools)
scripts/
  hermes_agentguard_buyer.py
  hermes_agentguard_seller.py
  hermes_two_sided_commerce.py
```

Do not create a new service merely to match this diagram. The gateway currently
hosts CommerceV1 and its compatibility adapter. Separate deployment becomes
justified only by independent scaling, ownership, or security boundaries.

## Canonical domain contract

Implement the structures in `ARCHITECTURE.md` as versioned schemas. Use one
canonical JSON encoding for hashing and signing. Reject unknown protected action
names and incompatible schema versions.

### Required action names

```text
buyer.checkout.commit
buyer.order.cancel
buyer.return.submit
buyer.remedy.accept
seller.catalog.publish
seller.price.change
seller.inventory.commit
seller.order.accept
seller.order.reject
seller.fulfilment.commit
seller.remedy.promise
seller.refund.issue
```

Preparation such as search, comparison, cart preparation, catalog drafting,
support drafting, and diagnosis is intentionally absent from authorization.

### Required decision reasons

At minimum define stable codes for:

```text
within_policy
approval_required_amount
approval_required_counterparty
approval_required_action
agent_paused
agent_revoked
mandate_missing
mandate_expired
policy_version_stale
action_not_allowed
resource_out_of_scope
counterparty_out_of_scope
amount_exceeded
quantity_exceeded
frequency_exceeded
aggregate_exceeded
approval_expired
approval_mismatch
approval_consumed
request_expired
nonce_replayed
principal_mismatch
execution_unknown
```

UI copy may translate these codes but must not parse prose to determine logic.

## API contract

Retain `/api/agentguard` during migration. Replace wallet-selected authority
with authenticated principal context. Exact HTTP status conventions must be
shared by both apps.

### Agent and mandate

```text
POST /api/agentguard/agents
GET  /api/agentguard/agents/current?role=buyer|seller
POST /api/agentguard/mandates/compile
POST /api/agentguard/mandates/{id}/confirm
GET  /api/agentguard/mandates/{id}
POST /api/agentguard/agents/{id}/pause
POST /api/agentguard/agents/{id}/revoke
```

Compilation may use AI to propose a policy, but confirmation accepts only the
displayed canonical mandate. Phase one may use safe templates with editable
limits while keeping the compile interface.

### Action lifecycle

```text
POST /api/agentguard/actions/evaluate
POST /api/agentguard/approvals/{id}/approve
POST /api/agentguard/actions/execute
GET  /api/agentguard/receipts/{id}
POST /api/agentguard/receipts/verify
```

`actions/execute` is the preferred mutation boundary: authenticate, load current
mandate and status, evaluate or atomically consume exact approval, call a named
server-side executor, persist the result, and issue a receipt. Until all writes
use it, existing route handlers must call the same domain function immediately
before mutation. A client-provided prior `allow` decision is never sufficient.

### Shared commerce exchange

All commerce writes use the AgentGuard action boundary above. The exchange
exposes public catalog reads and session-principal-scoped order/support reads:

```text
GET   /api/demo-commerce/buyer/search
GET   /api/demo-commerce/buyer/items/{item_id}
GET   /api/demo-commerce/buyer/orders
GET   /api/demo-commerce/buyer/orders/{order_id}
GET   /api/demo-commerce/seller/orders
GET   /api/demo-commerce/seller/orders/{order_id}
GET   /api/demo-commerce/buyer/issues
GET   /api/demo-commerce/seller/issues
```

The Buyer/Seller order and issue routes derive ownership from the signed session;
query or body identifiers cannot select another principal. Demo-runtime-only
setup mutations live under `/api/demo-commerce/test-fixtures/*`, return 404 in
staging/production/unknown runtime modes, and are never product APIs.

Use idempotency keys for every AgentGuard action that creates or commits state. Return stable
`transaction_id`, `message_id`, resource version, and current state. Model
publication, order, fulfilment, and issue lifecycles as explicit state machines.

## Milestone 0 — Establish baseline

### Work

1. Run the commands in `TESTINGPLAN.md` under Baseline.
2. Record pass/fail, current commit, environment, and known failures in the
   existing validation ledger.
3. Confirm Buyer `:43102`, Seller `:43103`, gateway `:43101`, and authenticated
   sessions work without changing ports.
4. Capture the current Seller AgentGuard browser proof.

### Exit criteria

- Baseline evidence exists before structural edits.
- Existing failures are distinguished from regressions.
- No feature deletion or script simplification has occurred.

## Milestone 1 — Shared identity-neutral AgentGuard contract

### Work

1. Create `shared/agentguard-contract` with schemas, action constants, decision
   codes, canonical JSON rules, and TypeScript exports.
2. Mirror or generate Pydantic models in the gateway; add cross-language golden
   fixtures to prevent schema drift.
3. Introduce `PrincipalRef` and remove wallet from the authorization domain.
   Host identity = Auth0 + optional local `demo-continue` session cookies; session
   carries `principal_id`. Body `wallet_address` is legacy-only and cannot
   override a social/demo session.
4. Version agents and mandates. Add validity, allowed actions, scopes, per-action
   and aggregate limits, frequency, and approval rules.
5. Change Buyer and Seller clients to consume the shared contract and bind UI
   login to Auth0 / demo-continue (no wallet CTA for AgentGuard).

### Primary files

- New `shared/agentguard-contract/`.
- `aadharchain/gateway/app/agentguard.py`.
- `aadharchain/gateway/app/agentguard_routes.py`.
- `aadharchain/gateway/app/social_auth_routes.py` and `session_auth.py`.
- Buyer/Seller AuthContext + AgentGuard clients.

### Exit criteria

- Caller-supplied wallet cannot select the authorization principal when a
  social/demo session is present.
- Buyer and Seller serialize identical fixtures.
- Unknown actions and schema versions fail closed.
- Existing refund and checkout tests pass; demo principal session can ensure an
  agent without a wallet body.
- Portfolio AG lanes use `sso demo` (not burner/Solana).

### Status (2026-07-11)

Contract package + principal session adapter **landed**. Google env-gated;
`AUTH_DEMO_CONTINUE` default on for local Hermes automation.
## Milestone 2 — Mandate confirmation and exact approval

### Work

1. Implement compile, review, and confirm. Start with deterministic templates;
   an LLM may suggest fields but cannot create active authority.
2. Display purpose, actions, limits, counterparties/resources, duration, and
   approval triggers in plain language.
3. Bind approval to the canonical request hash, principal, agent, resource,
   counterparty, amount/quantity, mandate version, nonce, and expiry.
4. Consume approval and nonce atomically under concurrent requests.
5. Implement pause and revoke; do not rely on a cached client status.
6. Preserve immutable mandate history and invalidate stale pending approvals when
   the policy changes.

### Exit criteria

- A principal can understand and confirm one Buyer and one Seller mandate.
- Changed amount, resource, counterparty, action, or mandate version invalidates
  an approval.
- Expired, replayed, concurrent, paused, and revoked actions fail deterministically.

## Milestone 3 — Shared commerce exchange (historical demo milestone)

This milestone introduced the server-owned exchange. CF1 subsequently moved
its authoritative cart/order/payment-ledger path to CommerceV1 PostgreSQL;
`/api/demo-commerce` now preserves compatibility and must not regain an
independent file-backed state owner.

### Work

1. Add gateway-owned commerce state with transactional persistence. Do not
   use browser localStorage as the cross-app source of truth.
2. Define versioned `Item`, `Inventory`, `Order`, `Fulfilment`, `Issue`, and
   `Remedy` records plus transition rules.
3. Implement an outbox/inbox-shaped local delivery path so requests and callbacks
   can be duplicated, delayed, and replayed in tests.
4. Migrate Seller catalog publication and order views to the shared API.
5. Migrate Buyer search, product, checkout-created order, order detail, and
   support cases to the same API.
6. Keep localStorage only for non-authoritative drafts or cache; show an explicit
   demo badge.

### State rules

- Published item versions are immutable events; edits create a new version.
- Checkout reserves inventory exactly once using an idempotency key.
- Order state transitions reject stale versions and impossible transitions.
- Payment `unknown` never becomes paid merely because a client retries.
- Issue and remedy state link to the same order and transaction identity.

### Exit criteria

- One Seller item is discoverable in Buyer without fixture duplication.
- One Buyer checkout creates exactly one Seller-visible order.
- Seller fulfilment changes appear in Buyer.
- A Buyer issue appears in Seller and its response returns to Buyer.
- Duplicate requests/callbacks cause no duplicate effect.

## Milestone 4 — Guard every admitted consequential action

### Work

1. Map every action in the taxonomy to a server executor and policy evaluator.
2. Route Buyer checkout, cancellation, return, and remedy acceptance through the
   common execution boundary.
3. Route Seller publication, price change, inventory commitment, order decision,
   fulfilment commitment, remedy promise, and refund through it.
4. Replace parallel Aadhaar/trust header gates as authorization owners. Host
   assurance may remain an input signal, never the independent allow decision.
5. Ensure agent tools call protected server endpoints, not local mutation
   helpers. Human direct writes use explicit human authority paths and audit.
6. Deny any protected route with no registered AgentGuard action mapping.

### Primary integration surfaces

- Buyer `protectedBuyerActions.ts`, `buyerActionPolicy.ts`, Checkout and order
  pages, and agent control plane.
- Seller `sellerActionPolicy.ts`, `sellerApiRuntime.js`, backend enforcement,
  catalog/order pages, and agent control plane.
- Gateway AgentGuard and commerce executors.

### Exit criteria

- There is one authorization owner for protected Buyer and Seller mutations.
- Direct API, modified UI, or agent-tool calls cannot bypass AgentGuard.
- Search and drafting remain usable when AgentGuard is unavailable, while
  protected mutations fail closed.

## Milestone 5 — Execution adapters and signed receipts

### Work

1. Add a named simulated payment adapter supporting success, decline, timeout,
   unknown, reconciliation, and refund. Never place secrets in the model path.
2. Finalize a receipt only with the observed adapter result and external
   reference commitment.
3. Canonicalize and sign receipts with an issuer key ID. Keep keys server-side
   and design rotation from the start.
4. Add independent verification by receipt payload/signature and by receipt ID.
5. Render concise Buyer/Seller receipt views: action, principal role, agent,
   resource, amount, mandate version, approval if any, result, and time.
6. Redact or hash private evidence and test dictionary-attack-sensitive fields
   with keyed commitments where necessary.

### Exit criteria

- Receipt tampering fails verification.
- Adapter timeout yields `unknown`; retry reconciles before new execution.
- Refund references the original transaction and cannot exceed allowed state or
  remaining refundable amount.
- The verifier needs no raw identity or commerce evidence.

## Milestone 6 — Intuitive Buyer and Seller journeys

### Buyer

1. Keep search, comparison, product and cart surfaces simple.
2. Show a concise agent authority card near agent controls.
3. At checkout show merchant, items, total, fulfilment, and why approval is or is
   not required.
4. Show order, issue, remedy, pause, and receipt state without policy jargon.

### Seller

1. Provide one operations-agent surface covering authority and activity; avoid
   duplicate generic Agent and AgentGuard product stories.
2. Let the agent stage catalog, inventory, order, support, and remedy proposals.
3. Distinguish drafts from binding actions and ask only at the protected boundary.
4. Keep Pause visible from agent and approval surfaces.

### Exit criteria

- A new user can explain current authority and complete the demo without API
  tools, hidden fixtures, or manual localStorage edits.
- Approval copy names action, counterparty/customer, resource/order, amount or
  quantity, consequence, and expiry.
- Simulated systems are visibly labelled without undermining the real safety proof.

## Milestone 7 — Browser proof and demo packaging

### Work

1. Add `agentguard buyer` to `scripts/portfolio_browser.py` and a Buyer Hermes
   script covering allow, exact approval, replay, pause, and receipt.
2. Update the Seller script so judged approval and replay behavior occur through
   visible UI; API calls are permitted only for fixture setup and independent
   verification.
3. Add one `two-sided` command that executes the complete target outcome with a
   unique run ID and captures structured evidence.
4. Make preflight reset only run-scoped demo fixtures, never user state.
5. Record two consecutive manual passes in the validation ledger before deleting
   old paths or simplifying wrappers.

### Exit criteria

- `TESTINGPLAN.md` demo gate passes twice consecutively.
- Failure output identifies the failed app, step, URL, console error, API result,
  and run ID.
- Demo reset and rerun are deterministic.

## Milestone 8 — Cleanup after proof

Only after Milestone 7:

- Remove browser-local authoritative catalog/order/support fixtures replaced by
  the shared exchange.
- Remove parallel protected-write trust gates replaced by AgentGuard.
- Remove duplicate Buyer/Seller action and receipt types.
- Merge or relabel generic agent navigation that competes with the product story.
- Remove direct-API shortcuts from judged browser flows.
- Keep compatibility adapters only when a current caller and deletion date are
  documented.
- Do not remove identity onboarding, SSO, or existing regression lanes merely
  because they are outside the judged demo.

## Milestone 9 — ONDC integration, separately gated

Do not start this milestone to improve the local submission. Begin only with an
approved participant role/domain and official environment access.

1. Complete ONDC portal onboarding, subscriber/role/domain registration, public
   callbacks, signing/encryption keys, TLS, and Registry discovery.
2. Implement versioned protocol mappers for the active ONDC domain specification.
3. Add signed asynchronous request/callback lifecycle, inbox/outbox,
   ACK/NACK, schema validation, idempotency, retry and observability.
4. Integrate regulated payment/settlement, logistics, tracking, returns, issue
   and grievance contracts.
5. Pass official staging/pre-production conformance before production claims.

The Browser apps must talk to a server-side BAP/BPP adapter; signing keys and
Registry credentials must never be shipped in Vite environment variables.

### Production readiness track (P0–P5)

Parallel ops/code track documented in `PRODUCTION-READINESS.md`:

| Phase | Status (repo) | Notes |
| --- | --- | --- |
| P0 Auth0 social | **code** | Gateway Auth0 Authorization Code Flow; UI Sign in; Google optional |
| P1 Demo auth gated | **code** | Staging/prod force-off demo-continue; Simulated exchange labels |
| P2 Portal A5–A8 | **ops** | Operator signup; `scripts/ondc_generate_keys.py` |
| P3 BAP adapter | **PreProd partial, validated 2026-07-14** | Signed gateway fanout + configured Seller BPP search, `on_search` inbox, visible Buyer Atta discovery; official conformance and full lifecycle remain |
| P4 PSP/logistics/IGM | **scaffold** | `/api/commerce-integrations/*` stubs (AG receipt required for pay) |
| P5 Flip demo mode | **gated** | `scripts/commerce_demo_mode_gate.py` — no flip without evidence |

## Milestone 10 — Mandate editor

### Work

1. Seller `/agentguard` and Buyer authority surface: edit allowed_actions and
   auto_approve_max_inr (refund / checkout), then compile and confirm.
2. Stop hardcoding 5000/10000 in client compile payloads; pass UI values to
   `POST /api/agentguard/mandates/compile`.
3. Show plain-language summary of the edited mandate before confirm.
4. Pause remains immediate and independent of edit flow.

### Exit criteria

- User can lower checkout/refund auto limit and see need_approval at the new
  threshold without code change.
- Disabling an allowed action removes it from compile and blocks that tool.
- Unit/API tests cover compile with custom limits; browser proof optional.

## Milestone 11 — Agent tool runner (Cursor host)

**Status (2026-07-14): implemented and FQDN validated for Buyer and Seller text
tools/runtime.** Search→cart→checkout receipt, catalog publish, latest-order
refund, background handoff, mandate filtering, principal scoping, and visible
approval/replay paths passed twice. This does not close the production security
gate.

### Work

1. Add `ondcbuyer/src/lib/agentTools.ts` and Seller twin: search_catalog,
   navigate_to, add_to_cart, checkout_commit, catalog_publish, refund_issue.
2. Protected tools call AgentGuard `actions/execute`; reads only update UI/cart.
3. Filter offered tools by confirmed mandate.
4. Wire Cursor agent runtime to invoke tools (not chat-only staging).
5. Add judged agent-tool browser proof when stable; keep Hermes AG lanes.

### Exit criteria

- Text agent path: search → navigate → cart → in-limit checkout with receipt.
- Tool absent from mandate cannot execute (client filter + server deny).
- No wholesale OpenAI Agents SDK migration in this milestone.

## Milestone 12 — Buyer Realtime voice

**Status (2026-07-14): partial.** Gateway Realtime and shared tools are configured;
text-mode Realtime/runtime passed twice. The Hermes browser exposed no physical
microphone, so the mic exit criterion below remains open rather than inferred.

### Work

1. Gateway endpoint mints ephemeral OpenAI Realtime client secrets
   (`OPENAI_API_KEY` server-side only).
2. Buyer WebRTC session with `gpt-realtime-2.1-mini`; `session.tools` from mandate.
3. Same tool runner as Milestone 11.
4. PreProd script: speak product intent → search/navigate/cart under AgentGuard.

### Exit criteria

- Mic session completes search→cart without typing.
- Protected checkout still hits AgentGuard; pause still denies.
- Browser never holds long-lived OpenAI keys.

## Customer-first production program (CF0–CF8)

Milestones 0–12 establish the demo and agent-executor foundation. They do not
authorize a production or real-customer-money claim. The commercial product is
delivered through the following program. Existing ONDC P0–P5 labels remain the
network-enablement subtrack inside CF1–CF3; they are not substitutes for the
customer journey or financial-safety gates.

| Phase | Scope | Exit criteria |
| --- | --- | --- |
| CF0. Product and contract alignment | Buyer/Seller journey maps; domain model; order, payment, return, issue, and approval states; risk taxonomy; tool inventory; mandate/decision/approval/receipt schemas; KPI baseline | Every journey has an owner and backend source of truth; every write has a risk tier; every sensitive action maps to AgentGuard |
| CF1. Production commerce foundation | Transactional storage; durable cart and order modules; ONDC inbox/outbox and correlation; payment sandbox; financial ledger; idempotency; audit events; authorization and recovery framework | One sandbox purchase completes; duplicate calls cannot duplicate payment/order; events reconstruct the transaction |
| CF2. Complete Buyer | Location-aware discovery; landed-cost comparison; persistent multi-seller cart; checkout; tracking; cancellation; return/refund; issue flow; approvals; receipts; support entry | Search-to-order-to-remedy works without developer repair; final landed cost precedes approval; mandate cannot be exceeded |
| CF3. Complete Seller | Business/store setup; catalog/import; inventory; order SLA operations; fulfilment; returns/refunds; settlement; analytics; agent approvals | Seller operates the full lifecycle; protected writes use AgentGuard; high-value remedies require step-up |
| CF4. iOS companion | SwiftUI shell; native authentication; Today, Orders, Approvals, Agent, Account; role/workspace switching; push; deep links; secure generated client; Face ID-bound approval | User tracks orders and approves exact requests; no production secret ships in the bundle; Buyer/Seller modes remain distinct |
| CF5. Native Realtime voice | Backend session broker; native interactive audio; transcript and tool cards; interruption, reconnect, recovery; multilingual evaluations; latency/cost telemetry | Read tasks are reliable; writes always traverse AgentGuard; verified backend outcome precedes success speech |
| CF6. Siri and App Intents | Typed product/order/store/approval/refund entities; bounded read and navigation intents; App Shortcuts; Spotlight; review-and-authenticate handoff | Siri retrieves status; high-risk requests open exact review; no intent bypasses backend authorization |
| CF7. On-device intelligence | Availability-aware router; local classification, summarization, rewriting, redaction, and offline help; prompt/OS regression suite | App works without the local model; local output is never authoritative transaction data |
| CF8. Production hardening and launch | Threat/privacy/accessibility review; load and resilience tests; SLOs; support console; runbooks; feature flags; phased rollout; rollback; reconciliation and global pause | Financial reconciliation passes; critical flows have monitored SLOs/runbooks; support can recover; autonomous writes can be stopped globally |

**CF0 closure (2026-07-23):** CF0 is complete at frozen application-source
fingerprint
`cb0769ea45b0f9e9cf63c825706d8fee1eeb3facf97d8e28bb3a832d1d026215`.
`cf0.journey.v1`, lifecycle contract `cf0.v1`, Decision Contract v2, the
83-route executable `cf0.write-risk.v1` inventory, and `cf0.kpi.v1` are the canonical
owners. PostgreSQL, deterministic, build, offline grader, two-pass bundled
Chrome, responsive/accessibility, exact-source deploy, and FQDN/Auth0 gates
passed. CF1 implementation evidence remains valid historical foundation; it
does not substitute for this CF0 contract-closure evidence.

### Build order and release priority

1. Preserve the frozen CF0 contracts and rerun their parity/inventory gates
   before changing production contracts.
2. Build CF1 as modules in the existing gateway unless evidence requires a
   deployment split. Start with decision-contract v2, durable cart/order state,
   idempotency, audit events, and the financial ledger.
3. Build CF2 and CF3 against the same frozen contracts and state machines.
4. Start CF4 only after generated API contracts, deep links, native token
   exchange, approval semantics, and notification payloads are stable.
5. Add CF5 and CF6 on top of the native core; keep all write authority in the
   backend. CF7 is an enhancement, never a launch dependency.
6. Run CF8 gates throughout; its final external evidence blocks release.

**P0 — before real customer money:** server authorization, durable cart/order,
ONDC state/callback handling, payment reconciliation, idempotency, mandate,
approvals, audit/receipts, refund lifecycle, hardened authentication,
monitoring, support, and recovery.

**P1 — strong launch:** landed-cost comparison, complete Seller catalog and
inventory, push, Face ID approval, native voice, bounded App Intents,
explainable recommendations, Live Activities, and operational analytics.

**P2 — differentiators:** on-device intelligence, predictive replenishment,
household profiles, demand forecasting, multilingual voice, richer system
entities, proactive suggestions, continuity, and watch-based approvals.

P2 must never delay or weaken a P0 control.

## Work-package rules for agents

Each implementation agent receives exactly one bounded work package with:

- milestone and acceptance criterion;
- files it owns and files it may only read;
- canonical schema/version;
- commands from `TESTINGPLAN.md` it must run;
- expected evidence artifact; and
- explicit non-goals.

Parallel work is safe only after shared contracts merge. Good parallel packages
are Buyer UI, Seller UI, gateway receipt signing, and test fixtures against a
frozen contract. Do not parallelize competing schema definitions, state-machine
owners, or migrations of the same protected route.

Agents must preserve unrelated changes, inspect the live diff before editing,
and report unsupported assumptions. A milestone is not complete because code
builds; its specified behavior and negative cases must pass.

## Progress table

Update this table only with linked evidence. Status describes implemented and
verified repository reality, not the intended production claim; incomplete
release or external gates stay explicit in the evidence column.

| Milestone | Status | Evidence |
| --- | --- | --- |
| 0. Baseline | **Done** (2026-07-11) | `verify-portfolio` + gateway pytest; Buyer/Seller npm test+build; `agentguard seller --fixture` success. Ledger M0 |
| 1. Shared contract | **Done** | `shared/agentguard-contract` + gateway `agentguard_contract.py`; PrincipalRef session resolution; Buyer/Seller clients import contract; 56 gateway tests |
| 2. Mandates and approval | **Done** | compile/confirm/pause/revoke routes; exact approval consume+replay 409; Seller Confirm mandate UI |
| 3. Shared commerce exchange | **Done; superseded by CF1 storage owner** | Historical `commerce_demo.py` + `/api/demo-commerce` proof established the two-sided API. CommerceV1 PostgreSQL now owns authoritative CF1 state and `/api/demo-commerce` is compatibility-only. |
| 4. Protected-action coverage | **Done** | Executors registered for taxonomy; `actions/execute`; Seller refund + Buyer checkout call execute/verify |
| 5. Adapters and receipts | **Done** | `payment_adapter.py` + `receipt_signing.py` + `/receipts/verify`; UI verify hooks |
| 6. Buyer/Seller UX | **Done** | Seller mandate/Pause; Buyer authority card; simulated labels; builds OK |
| 7. Browser proof | **Done** | Hermes `agentguard seller --fixture` + `agentguard buyer --fixture` success 2026-07-11 evening; two-sided unique runs `ag-hermes-1783779577-a` / `ag-hermes-1783779578-b`; WIP bridge repaired via `ensure-wip-native-host.sh` |
| 8. Cleanup | **Done** (2026-07-16) | Consequential Buyer/Seller order, return, fulfilment, catalog publish/archive, checkout, and support writes use AgentGuard plus the shared server exchange. Browser-local catalog/order/support stores and displaced trust-policy callers are deleted. Buyer/Seller clients use shared action, agent, mandate, approval, and intent-receipt types; the standalone `/agent` pages/navigation are deleted in favor of each app's global Samantha orb. Dated Seller/Netlify compatibility callers remain only until their documented post-2026-08-01 deletion gate. Final visible runs `m8-contract-final-1784209300-a` and `m8-contract-final-1784209301-b` preserve unique order/transaction/issue identity across Seller and Buyer. |
| 9. ONDC integration | **Partial; external conformance blocked** | Signed PreProd search/on_search and configured-Seller discovery are proven; PostgreSQL inbox/outbox, persist-before-ACK, deduplication, correlation, leases, retries and dead-letter recovery are implemented. Full lifecycle semantics, portal onboarding and official conformance remain open. See `.cursor/skills/ondc-testing/references/preprod-network-matrix.md` and `matrix-status.md`. |
| 10. Mandate editor | **Done** (2026-07-11) | Seller `/agentguard` edit refund max + allowed actions; Buyer checkout authority card checkout max; gateway `allowed_actions` + limit normalize |
| 11. Agent tool runner (Cursor) | **Done** (2026-07-11) | `ondcbuyer`/`ondcseller` `agentTools.ts`; Cursor agent context includes tool defs; chat path invokes runner |
| 12. Buyer Realtime voice | **Partial** (2026-07-14) | Gateway session path, Buyer `SamanthaOrb`, text tools, and mandate/memory integration pass; physical microphone journey remains unproved |
| CF0. Product/contract alignment | **Complete; release validated** (2026-07-23) | `cf0.journey.v1`, six `cf0.v1` lifecycle families, Decision Contract v2, the exhaustive 83-route `cf0.write-risk.v1` inventory and `cf0.kpi.v1` are canonical. PostgreSQL, deterministic/build/offline, Buyer/Seller bundled Chrome ×2, responsive/accessibility, exact-source deployment and FQDN/Auth0 acceptance pass at fingerprint `cb0769ea45b0f9e9cf63c825706d8fee1eeb3facf97d8e28bb3a832d1d026215`. |
| CF1. Production foundation | **Implemented; release validated** (2026-07-22) | Frozen fingerprint `e95340b069cab63b75f436e0d5fdfe4e667545c40d2ee9b378f1b5957914db26`: process-selected PostgreSQL ownership covers AgentGuard, CommerceV1 and ONDC; compatibility routes do not create a second store. Gateway/Buyer/Seller/build/offline gates, PostgreSQL two-cycle readback, Buyer and Seller bundled Chrome Pass 1+2, combined responsive/accessibility smoke, matching deployment, and FQDN/Auth0 Buyer/Seller acceptance passed. Payment remains simulated; this is not a production-money or production-ONDC claim. See `.cursor/skills/ondc-testing/references/matrix-status.md`. |
| CF2. Complete Buyer | **Partial** | Search, cart, exact landed-cost checkout, AgentGuard approval, orders, receipts and bounded remedy UI exist. Location-aware normalized multi-seller comparison, full tracking/cancellation/return/replacement/grievance/support lifecycle and current-source release proof remain. |
| CF3. Complete Seller | **Partial** | Catalog publish/archive, inventory, order actions, protected refunds, mandates, Pause and receipts exist. Onboarding, roles/import, complete SLA fulfilment, settlement, analytics and current-source release proof remain. |
| CF4. iOS companion | Not started | No native project in workspace |
| CF5. Native Realtime voice | Not started | Browser/text evidence does not prove native physical audio |
| CF6. Siri/App Intents | Not started | No native intent target in workspace |
| CF7. On-device intelligence | Not started | Optional after native core |
| CF8. Hardening/launch | Not started | External security, privacy, operational, and financial evidence required |

## Definition of demo complete

The **Token Nxt local demo** (milestones 0–7) is complete when all are true:

- Milestones 0–7 pass; cleanup may follow without changing behavior.
- Seller-published data, Buyer order, Seller fulfilment, and Buyer issue share
  stable transaction identities in server-owned state.
- Every admitted protected action is server-enforced through AgentGuard.
- Routine and exceptional checkout and refund paths are visible in the UI.
- Replay, expiry, tampering, cross-principal access, duplicate delivery, timeout,
  pause, and revocation negative tests pass.
- Receipts verify independently and contain no prohibited evidence.
- Two consecutive full browser passes are recorded.
- UI and documentation make no live ONDC, NPCI, payment, or blockchain claim.

The **agent-as-executor PreProd story** additionally requires milestones 10–12:
editable mandate, Cursor tool execution across the app, and Buyer Realtime voice
on the same runner.
