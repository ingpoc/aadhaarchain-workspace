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
| AgentGuard domain | `aadharchain/gateway/app/agentguard.py` | Allow/approval/deny flow, one-time consume, pause, receipt persistence |
| AgentGuard HTTP | `aadharchain/gateway/app/agentguard_routes.py` | Ensure/status/evaluate/consume/pause/receipt route skeleton |
| Gateway tests | `aadharchain/gateway/tests/test_agentguard.py` | Refund and checkout allow, approval, replay and pause proof |
| Buyer guard client | `ondcbuyer/src/lib/agentGuardCheckout.ts` | Checkout integration starting point |
| Seller guard client | `ondcseller/src/lib/agentGuardClient.ts` | Status/evaluate/consume/pause client starting point |
| Buyer commerce | `ondcbuyer/src/lib/localCart.ts`, `localOrders.ts`, `localSupportCases.ts` | UI behavior and data shapes; not cross-app state |
| Seller commerce | `ondcseller/src/lib/localSellerOrders.ts`, `mockCatalog.ts` | UI behavior and data shapes; not cross-app state |
| Agent proposal parsers | `ondcbuyer/src/lib/agentBuyerState.ts`, `ondcseller/src/lib/agentSellerState.ts` | Typed proposal normalization and staging patterns |
| Existing write guards | Buyer/Seller action-policy and backend-enforcement modules | Fail-closed patterns; must converge on AgentGuard |
| Browser framework | `scripts/portfolio_browser.py` and Hermes scripts | Preflight, SSO, fixture and evidence foundation |
| Shared identity helper | `shared/trust-client/src/index.ts` | Optional host assurance adapter during migration |

### Known gaps

- Mandate limits and allowed actions are mostly hardcoded; no mandate editor UI.
- Runtime agents are chat-oriented; shared tool runner (search/navigate/cart/
  execute) is missing — Hermes is automation, not the product agent.
- Buyer Realtime voice (`gpt-realtime-2.1`) not started.
- Some browser-local commerce fixtures remain as fallbacks beside demo-commerce.
- Parallel trust-policy headers still exist on some non-demo write paths.
- Buyer Hermes lane still API-gates approve/pause (UI path incomplete).
- ONDC protocol code is a scaffold; network onboarding and keys do not exist.

## Target repository shape

Prefer this shape unless an existing owner demonstrably fits better:

```text
shared/
  agentguard-contract/       TypeScript schemas, canonicalization, reason codes
aadharchain/gateway/app/
  agentguard.py              Domain service during migration
  agentguard_routes.py       Identity-neutral authenticated API
  commerce_demo.py           Local exchange domain service
  commerce_routes.py         Buyer/Seller demo API
  receipt_signing.py         Keyed receipt issue and verify
  realtime_session.py        Ephemeral OpenAI Realtime client secrets (M12)
ondcbuyer/src/
  lib/agentGuardClient.ts    Shared-contract client
  lib/commerceClient.ts      Shared demo exchange client
  lib/agentTools.ts          Tool runner (search, navigate, cart, checkout)
ondcseller/src/
  lib/agentGuardClient.ts    Shared-contract client
  lib/commerceClient.ts      Shared demo exchange client
  lib/agentTools.ts          Tool runner (publish, refund, order tools)
scripts/
  hermes_agentguard_buyer.py
  hermes_agentguard_seller.py
  hermes_two_sided_commerce.py
```

Do not create a new service merely to match this diagram. The gateway may host
the local exchange for the demo. Separate deployment becomes justified only by
independent scaling, ownership, or security boundaries.

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

### Local commerce exchange

Expose role-authorized endpoints behind the gateway:

```text
POST  /api/demo-commerce/seller/items
PATCH /api/demo-commerce/seller/items/{item_id}
POST  /api/demo-commerce/seller/items/{item_id}/publish
GET   /api/demo-commerce/buyer/search
GET   /api/demo-commerce/buyer/items/{item_id}
POST  /api/demo-commerce/buyer/orders
GET   /api/demo-commerce/buyer/orders/{order_id}
GET   /api/demo-commerce/seller/orders
POST  /api/demo-commerce/seller/orders/{order_id}/transition
POST  /api/demo-commerce/buyer/orders/{order_id}/issues
GET   /api/demo-commerce/seller/issues
POST  /api/demo-commerce/seller/issues/{issue_id}/respond
POST  /api/demo-commerce/seller/issues/{issue_id}/remedy
```

Use idempotency keys for every POST that creates or commits state. Return stable
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

## Milestone 3 — Shared local commerce exchange

### Work

1. Add gateway-owned demo commerce state with transactional persistence. Do not
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

Update this table only with linked evidence. `Not started` is the truthful
initial status even where fragments already exist.

| Milestone | Status | Evidence |
| --- | --- | --- |
| 0. Baseline | **Done** (2026-07-11) | `verify-portfolio` + gateway pytest; Buyer/Seller npm test+build; `agentguard seller --fixture` success. Ledger M0 |
| 1. Shared contract | **Done** | `shared/agentguard-contract` + gateway `agentguard_contract.py`; PrincipalRef session resolution; Buyer/Seller clients import contract; 56 gateway tests |
| 2. Mandates and approval | **Done** | compile/confirm/pause/revoke routes; exact approval consume+replay 409; Seller Confirm mandate UI |
| 3. Shared local exchange | **Done** | `commerce_demo.py` + `/api/demo-commerce`; Buyer/Seller `commerceClient.ts`; two-sided API proof |
| 4. Protected-action coverage | **Done** | Executors registered for taxonomy; `actions/execute`; Seller refund + Buyer checkout call execute/verify |
| 5. Adapters and receipts | **Done** | `payment_adapter.py` + `receipt_signing.py` + `/receipts/verify`; UI verify hooks |
| 6. Buyer/Seller UX | **Done** | Seller mandate/Pause; Buyer authority card; simulated labels; builds OK |
| 7. Browser proof | **Done** | Hermes `agentguard seller --fixture` + `agentguard buyer --fixture` success 2026-07-11 evening; two-sided unique runs `ag-hermes-1783779577-a` / `ag-hermes-1783779578-b`; WIP bridge repaired via `ensure-wip-native-host.sh` |
| 8. Cleanup | **In progress** (2026-07-11) | Deleted dead `agentCommerceState` + unwired `sellerBackendEnforcement`; seller Hermes approve/replay/pause/deny via UI; unique two-sided `run_id`; LEGACY aliases dated 2026-08-01. Remaining: buyer Hermes still API-gated; migrate local* commerce authority; collapse trust-policy headers |
| 9. ONDC integration | Blocked by external onboarding | — |
| 10. Mandate editor | **Done** (2026-07-11) | Seller `/agentguard` edit refund max + allowed actions; Buyer checkout authority card checkout max; gateway `allowed_actions` + limit normalize |
| 11. Agent tool runner (Cursor) | **Done** (2026-07-11) | `ondcbuyer`/`ondcseller` `agentTools.ts`; Cursor agent context includes tool defs; chat path invokes runner |
| 12. Buyer Realtime voice | **Done** (2026-07-11) | Gateway `/api/realtime/status` configured + `gpt-realtime-2.1-mini`; Buyer `SamanthaOrb` global + `/config` mandate/memory; `remember_preference` tool; deleted bulky `VoiceShoppingPanel`. Samantha = short chainable tools; long plans → `delegate_to_runtime_agent` → `/agent` Cursor runtime. |

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
