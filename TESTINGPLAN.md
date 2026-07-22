# AgentGuard Commerce Testing Plan

## Purpose

This is the verification owner for the AgentGuard Buyer/Seller product. It tells
an agent what to test, how to test it, what evidence to retain, and which claims
each test permits.

Testing is layered. Fast deterministic tests run first; API integration,
cross-application contract, browser, adversarial, and future ONDC conformance
follow. A higher layer does not replace a lower one, and a build does not prove
runtime behavior.

## Truthful test states

- **Current baseline:** existing tests and validated Seller browser lane.
- **Demo gate:** required for the local Token Nxt demonstration.
  Status (2026-07-11 night): **Buyer Samantha 11/11** · **Seller Samantha 5/5** ·
  **Seller AG fixture Pass ×2** (demo principal UI allow/approve/replay/pause/deny).
  Buyer AG Hermes + two-sided unique runs remain separately validated.
- **Production security gate:** required before any external pilot with real
  users or money.
- **ONDC conformance gate:** blocked until official participant onboarding,
  environment access, and active domain specifications exist.

Never report an ONDC, NPCI, payment, or production pass based on demo fixtures.

## Environments and ports

| Service | Local URL | Test role |
| --- | --- | --- |
| AadhaarChain web | `http://127.0.0.1:43100` | Existing login/onboarding compatibility |
| Gateway and AgentGuard | `http://127.0.0.1:43101` | API, authorization and shared demo state |
| ONDC Buyer | `http://127.0.0.1:43102` | Buyer UI and browser journey |
| ONDC Seller | `http://127.0.0.1:43103` | Seller UI and browser journey |
| FlatWatch API/web | `:43104` / `:43105` | Existing runtime dependency only; not product acceptance |

Solana `:8899` is not part of AgentGuard acceptance. Do not start or validate it
unless an unrelated explicit task requires it.

## Evidence standard

Every test run records:

- commit or working-tree identifier and timestamp;
- command, environment flags, browser/runtime version, and fixture/run ID;
- pass/fail/blocked plus first failing assertion;
- API status and stable reason code for protected actions;
- browser URL, visible pass signal, console errors, and relevant network failure;
- receipt/order/transaction IDs with private fields redacted; and
- whether the system under test was real, simulated, or stubbed.

Use `.cursor/skills/portfolio-browser/references/validation-ledger.md` for
manual/browser validation. Store machine-readable run artifacts under an
existing evidence directory if one exists; otherwise add a run-scoped directory
only when the test harness needs it. Never commit secrets or raw PII.

Two consecutive manual passes are required before browser-flow simplification or
deleting old validation paths.


### Demo principal auth (Milestone 1 host identity)

Precond: gateway up; `AUTH_DEMO_CONTINUE=true` (local automation). Auth0 preferred for PreProd/staging (`AUTH0_*`).

```bash
# local Hermes automation
# or manual: Buyer → Sign in (Auth0) / demo-continue / optional Google
```

```bash
curl -s http://127.0.0.1:43101/api/auth/providers
# → auth0 / google / demo_continue flags

python3 scripts/portfolio_browser.py sso demo buyer
# or manual: Buyer → Sign in (Auth0) / demo-continue / optional Google
```

Pass signals: `/api/auth/me` returns `principal_id` (`principal:auth0:…`, `principal:demo:…`, or `principal:google:…`);
no wallet required; AgentGuard `agents/ensure` with credentials and **no** body wallet succeeds;
body wallet on a social/demo session returns 403.

Burner/Solflare SSO is **legacy hangar** — not AgentGuard acceptance.

## Baseline gate

Run before implementation and after any broad change:

```bash
./scripts/setup.sh                 # only for a fresh clone or missing deps
./scripts/verify-portfolio.sh      # starts stack if required; gateway pytest
cd ondcbuyer && npm test && npm run build
cd ../ondcseller && npm test && npm run build
```

Browser baseline:

```bash
python3 scripts/portfolio_browser.py sso demo buyer
python3 scripts/portfolio_browser.py agentguard buyer --fixture
python3 scripts/portfolio_browser.py agentguard seller --fixture
```

Known current limitation: burner/Solflare SSO is hangar-only. AgentGuard
acceptance uses `sso demo` + `agentguard buyer|seller --fixture`.

Baseline failure policy:

1. Re-run only the smallest deterministic failing test to classify it.
2. Check whether the failure predates the current diff.
3. Do not weaken assertions, reset unrelated state, or label it flaky without
   repeated evidence.
4. Record a blocked external dependency separately from a product failure.

## Test data strategy

Each run uses a unique `run_id` and deterministic principals:

```text
buyer principal: buyer-{run_id}
seller principal: seller-{run_id}
buyer agent: buyer-agent-{run_id}
seller agent: seller-agent-{run_id}
item SKU: SKU-{run_id}
transaction: generated once by exchange
idempotency keys: {run_id}:{step}:{attempt}
```

Fixtures may create authenticated demo sessions and confirmed safe mandates.
They may not directly create the order, consume approval, change fulfilment,
issue refund, or produce the receipt in the judged browser flow.

Reset deletes only records for the current run ID. Tests must also pass without
reset when an identical request is replayed, proving idempotency rather than a
clean database illusion.

## Layer 1 — Schema and deterministic unit tests

### Shared contract

Test both Python and TypeScript against the same golden fixtures:

- canonical JSON is byte-identical independent of key insertion order;
- every action name and decision reason round-trips;
- unknown action/schema version is rejected;
- absent optional amount does not become zero silently;
- currency, amount, quantity, timestamps, TTL, and IDs validate strictly;
- evidence hash changes when any bound action field changes;
- private fields are not present in ActionRequest or IntentReceipt schemas.

### Mandate evaluator

For Buyer and Seller test:

- allowed action, resource, counterparty, amount, quantity and time;
- denied action and resource;
- exact per-action boundary: below, equal and one unit above;
- aggregate and frequency boundary, including concurrent requests;
- new or out-of-scope counterparty escalation;
- missing, inactive, expired and future mandate;
- stale policy version;
- paused and revoked agent;
- request timestamp and expiry;
- unsupported action fails closed;
- evaluator remains deterministic for identical state and input.

### Approval and nonce

- approval binds every canonical action field;
- changed action, amount, quantity, counterparty, resource, purpose, principal,
  agent, policy version or expiry fails;
- consume succeeds once;
- sequential replay returns conflict;
- concurrent consume has exactly one winner;
- expired/revoked approval fails;
- mandate update invalidates pending approval;
- pause racing with execute prevents any action authorized after pause commit.

### State machines

Test all legal and illegal transitions for:

- item draft → published → superseded/withdrawn;
- inventory available → reserved → committed/released;
- order created → confirmed → accepted/rejected → dispatched → delivered;
- cancellation and return branches;
- issue open → acknowledged → resolution proposed → accepted/rejected → closed;
- payment/refund pending → success/declined/unknown → reconciled.

Impossible, stale-version and duplicate transitions must not mutate state.

### Existing commands

```bash
cd aadharchain/gateway && .venv/bin/python -m pytest tests/test_agentguard.py -q
cd ondcbuyer && npm test
cd ondcseller && npm test
```

Add focused files next to their owners rather than one giant end-to-end unit
test. Preserve current Buyer journey, cart failure, order, Seller catalog,
Seller order, action-policy, and backend-enforcement coverage.

## Layer 2 — AgentGuard API integration

Use authenticated test clients and isolated transactional state.

### Authentication and tenancy

- anonymous calls to agent, mandate, evaluate, approval, execute, pause and
  receipt-private endpoints fail;
- request body cannot override authenticated principal;
- Buyer cannot operate Seller agent or vice versa;
- tenant A cannot read, approve, pause, execute or verify private metadata for
  tenant B;
- logout, expired session and session rotation invalidate authority correctly;
- CSRF and CORS behavior matches the chosen cookie/token architecture.

### Full action lifecycle

For one Buyer checkout and Seller refund:

1. Create agent.
2. Compile mandate.
3. Confirm canonical mandate.
4. Evaluate routine action and execute.
5. Evaluate exceptional action and receive approval-required.
6. Approve exact request.
7. Execute and atomically consume.
8. Replay and assert conflict with no second effect.
9. Pause and assert the next protected action fails.
10. Revoke and assert old approvals remain unusable.

Repeat contract tests for all protected action names even if their executors are
simple demo adapters.

### Execution result semantics

Inject adapters that return success, decline, timeout, malformed result, and
temporary unavailability:

- success creates one effect and signed receipt;
- decline records failure without pretending authorization failed;
- timeout yields `execution_unknown` and prevents blind re-execution;
- reconciliation with the same idempotency key discovers the real result;
- malformed adapter output fails safely and is audited;
- receipt references the exact request and observed result.

### Receipt verification

- valid receipt verifies by payload and by ID;
- changed byte, field, signature, key ID or canonicalization fails;
- old receipt verifies after signing-key rotation;
- revoked current agent does not invalidate historical receipt truth;
- receipt contains no Aadhaar number/document, wallet secret, address, cart,
  conversation, PIN, OTP, payment credential or raw order evidence;
- hash commitments cannot be recomputed trivially from low-entropy personal data.

## Layer 3 — Shared commerce contract tests

Run against the gateway API without a browser.

### Catalog and discovery

- Seller publishes one SKU; Buyer search returns the same ID, version, price,
  seller and available quantity.
- Draft and withdrawn versions are not discoverable.
- Edit creates a new version; stale version update fails.
- Duplicate publish returns the original result and does not duplicate listing.
- Malicious product text remains inert data and cannot change agent policy.

### Checkout and inventory

- Buyer order uses current product/version and quote.
- Checkout reserves inventory exactly once.
- Concurrent orders cannot oversell.
- Price/version change between cart and commit causes re-quote, not silent buy.
- Payment decline releases reservation as designed.
- Payment unknown keeps a reconcilable state and does not create a second charge.
- Idempotent retry returns the same order and payment reference.

### Seller order and Buyer status

- Seller sees the same order and `transaction_id`.
- Only legal accept/reject/dispatch/deliver transitions succeed.
- Buyer observes each committed transition.
- Duplicate and out-of-order callback delivery creates no regression or second
  notification effect.

### Issue and remedy

- Buyer issue is linked to an owned order and appears in Seller.
- Seller draft response is unprotected; binding promise/refund is protected.
- Buyer sees response and can accept/reject an applicable remedy.
- Refund cannot exceed paid/refundable amount or execute twice.
- Unauthorized party cannot read or mutate the case.

## Layer 4 — Frontend component and integration tests

### Buyer

Retain and extend tests around:

- search stream and empty/error/loading states;
- product version and availability display;
- cart persistence as non-authoritative cache;
- quote change and stale cart recovery;
- authority card, mandate review, approval preview and Pause;
- checkout allow, approval-required, decline, unknown and retry/reconcile;
- order timeline, issue creation, remedy and receipt verification;
- accessible keyboard/focus/error behavior.

Relevant current owners include `buyerJourneyContract.test.ts`,
`buyerActionPolicy.test.ts`, `orderApi.test.ts`, page tests, and trust/auth tests.

### Seller

Retain and extend tests around:

- catalog create/edit/publish and validation;
- inventory floor, reservation and conflicting update;
- received order transition controls;
- agent proposal staging versus committed action;
- customer issue response and binding remedy distinction;
- refund allow, approval, decline, unknown and receipt;
- authority card, exception preview and Pause;
- accessible keyboard/focus/error behavior.

Relevant owners include Catalog/Product tests, local order tests,
`agentSellerState.test.ts`, action-policy, API-runtime and backend-enforcement
tests. Replace local-only assumptions as shared exchange state lands.

### UI security assertions

- Hiding or enabling a button never changes server authorization.
- Modified localStorage cannot grant authority, change price, create order, or
  forge receipt.
- Error messages do not leak policy internals, keys, other tenant IDs, or PII.
- Untrusted product/customer content renders safely and cannot inject markup or
  instructions into privileged model context.

## Layer 5 — Browser acceptance

Use the validated portfolio browser/Hermes lane. Test visible behavior and pair
it with console and API evidence.

Deployed strict lane (no fixture writes or in-page fetch/mutation):

```bash
python3 scripts/hermes_fqdn_e2e_thorough.py both
```

Final evidence on 2026-07-14: Buyer clean runs `030751` + `031443`; Seller clean
runs `023601` + `031443`. Physical mic is recorded `Blocked`; Realtime
configuration, text tools, and background runtime are `Pass`.

### Buyer AgentGuard lane

Required command after implementation:

```bash
python3 scripts/portfolio_browser.py agentguard buyer --fixture
```

Required visible steps:

1. Authenticated Buyer and active shopping agent.
2. Plain-language confirmed mandate.
3. Seller-published product discovered and added to cart.
4. Routine checkout allowed and receipt visible.
5. Exceptional checkout preview and exact approval.
6. Approval consumed once; replay visibly rejected.
7. Pause visible; next protected action rejected.
8. Receipt verifier reports valid.

### Seller AgentGuard lane

```bash
python3 scripts/portfolio_browser.py agentguard seller --fixture
```

Required visible steps:

1. Authenticated Seller and active operations agent.
2. Plain-language confirmed mandate.
3. Catalog publication and order action inside policy.
4. Buyer issue visible and response draft staged.
5. Routine refund allowed and receipt visible.
6. Exceptional refund preview and exact approval.
7. Approval consumed once; replay visibly rejected.
8. Pause visible; next protected action rejected.
9. Receipt verifier reports valid.

Critical approval, consume, replay, pause, and receipt steps must operate through
the UI. Direct API calls are allowed for fixture preparation and independent
postcondition verification only.

### Two-sided lane

Required command after implementation:

```bash
python3 scripts/portfolio_browser.py two-sided --fixture
```

Pass signals:

- Seller-created unique SKU is visible in Buyer.
- Buyer checkout creates one order with a captured transaction ID.
- The same ID appears in Seller without reload hacks or data repair.
- Seller transition appears in Buyer.
- Buyer issue appears in Seller; response/remedy returns to Buyer.
- Inventory and financial effects occur exactly once.
- Both receipt views verify.
- Browser console has no uncaught errors and protected API requests have expected
  status/reason codes.

Run twice consecutively with different run IDs and record both passes before
declaring the demo stable.

### Mandate editor lane (Milestone 10)

1. Open Seller `/agentguard` (and Buyer authority surface).
2. Lower refund or checkout auto-approve max; confirm mandate.
3. Trigger an amount between old and new threshold → need_approval.
4. Remove an allowed action; attempt that tool/action → deny.

### Agent tool runner lane (Milestone 11)

1. Authenticated Buyer with Cursor runtime enabled.
2. Agent tools: search → navigate → add_to_cart without manual page clicks.
3. In-limit checkout_commit via tool → receipt; over-limit → approval UI.
4. Tool not in mandate never appears or server-denies if forced.

### Buyer Realtime voice lane — Samantha (Milestone 12)

Manual / Hermes-assist until automated. No `portfolio_browser` subcommand yet.
Product UX matrix + visible bar: `.cursor/skills/ondc-testing/SKILL.md`.

**Precondition**

```bash
# Gateway must have OPENAI_API_KEY set; then:
curl -s http://127.0.0.1:43101/api/realtime/status
# Expect: configured:true, model:gpt-realtime-2.1-mini, agent_name:Samantha
```

Missing `OPENAI_API_KEY` → lane **blocked** (not fail). Record blocked + status body.

**Pass signals**

1. **Orb:** On Buyer shop routes (`:43102`), `data-testid=samantha-orb` visible bottom-right; tap starts a Realtime session; hint/link reaches `/config`.
2. **Config:** Open `/config` (`buyer-config-page`); edit checkout auto-max and allowed actions → Confirm mandate; Samantha memory clear/edit controls visible.
3. **Voice:** Mic connected; speak product intent; tools drive search and/or cart; `remember_preference` persists and appears on `/config`.
4. **Authority:** `checkout_commit` still gated by AgentGuard (allow / need_approval / deny as mandate requires).
5. **Secrets:** Browser receives ephemeral client-secret only — no long-lived OpenAI API key in page, storage, or bundle.

## Layer 6 — Adversarial and abuse tests

### Authorization attacks

- Change principal/agent/resource/amount/counterparty in transit.
- Reuse approval across roles, tenants, resources or policy versions.
- Race consume, pause, revoke, mandate update and execution.
- Call protected executor directly without evaluate/approval.
- Forge client allow result, receipt, callback or identity header.
- Replay old signed request within and outside TTL.

### Agent and content attacks

- Product description instructs agent to ignore mandate or expose secrets.
- Customer issue asks Seller agent to refund a different order/payee.
- Tool result contains fake approval or system instruction.
- Model emits unknown action, extra fields, negative values, huge values, NaN,
  scientific notation, alternate currency, or encoded payload.
- Realtime/Cursor session requests a tool excluded from the confirmed mandate;
  runner must refuse and AgentGuard must deny if called.
- Agent repeatedly splits one disallowed amount into smaller actions; aggregate
  and frequency controls detect or escalate it.

### Web and operational security

- CSRF, CORS, session fixation, cookie flags and logout invalidation.
- XSS from catalog/customer content and unsafe URL handling.
- Rate limits on compile, evaluate, approval and execute.
- Tenant isolation and object-level authorization.
- Secret and PII scan of browser bundle, logs, receipts and model prompts.
- Database/key outage fails protected writes closed while reads/drafts degrade.
- Backup restore preserves nonce consumption and receipt verification.

Production security gate additionally requires an independent threat model,
dependency/security scan, key-management review, privacy/retention review, and
incident-recovery exercise.

## Layer 7 — Performance and resilience

Define targets before external pilot. At minimum measure:

- p50/p95/p99 evaluate and execute latency;
- approval creation and consume contention;
- catalog search and order callback throughput;
- duplicate-message rate and deduplication success;
- adapter timeout and reconciliation backlog;
- receipt signing/verification latency;
- database recovery point and recovery time.

Load tests must preserve safety invariants. A faster run with duplicate charge,
oversold inventory, missed pause, or double approval is a failure.

Inject process termination between authorization, external execution, state
commit, and receipt finalization. Recovery must converge using transaction and
idempotency identifiers without guessing whether money moved.

## Layer 8 — ONDC conformance, future blocked lane

Do not treat this as part of the local demo pass. Start only with official
subscriber IDs, roles, domains, environment endpoints, keys, and active
specification version.

Test:

- Registry subscription and lookup, subscriber/role/domain/callback correctness;
- request and callback signing, digest, signature verification and key rotation;
- active domain schemas for `search/on_search`, `select/on_select`,
  `init/on_init`, `confirm/on_confirm`, status, track, update, cancel, and
  applicable issue/grievance APIs;
- context correlation: domain, action, version, location, transaction ID,
  message ID, timestamp, TTL, BAP/BPP IDs and URIs;
- ACK/NACK, invalid signature/schema, timeout, retry, duplicate, late and
  out-of-order callback behavior;
- catalog, quote, payment, settlement, refund, logistics, return and grievance
  reconciliation;
- official log validation, staging/pre-production scenarios, observability and
  go-live criteria.

Required evidence includes redacted onboarding state, official conformance
reports, signed message fixtures, callback traces, retry/failure proof, and
network discovery evidence. `ondcbuyer/src/lib/ondc/protocolClient.ts` remains a
scaffold until this gate begins.

## Layer 9 — Customer-money journey and financial safety

This layer is separate from demo acceptance. Run it against production-like
transactional storage, a payment sandbox with signed webhooks, and isolated
Buyer/Seller tenants.

### Buyer journey

- sign in, set serviceable location, search manually and conversationally;
- deduplicate and compare total landed cost, delivery, seller reliability,
  cancellation, return eligibility, sponsorship, and alternatives;
- persist and restore a multi-seller cart across sessions/devices;
- revalidate inventory and price before payment, exposing every change;
- create one payment and one order under retry, timeout, refresh, duplicate
  callback, and concurrent-submit conditions;
- track, partially cancel, return/replace, refund, dispute, and inspect the
  complete customer-visible transaction record.

### Seller journey

- register/configure business, store, staff roles, serviceability, settlement,
  operating hours, and policies without handling identity documents in the UI;
- create/import/validate/publish catalog, variants, taxes, price, promotion, and
  inventory with draft/published states;
- accept/reject within SLA, pack, dispatch, substitute, partially fulfil, and
  manage exception/customer communication queues;
- validate return eligibility, review evidence, issue full/partial refund or
  replacement, escalate high-value remedies, and reconcile settlement.

### Financial invariants

- provider webhook authentication and replay protection pass;
- internal ledger balances independently of provider dashboard status;
- payment/order/refund/settlement idempotency keys survive retries and failover;
- payment-success/order-unknown and refund-pending states reconcile without
  blind financial retry;
- every material transition has one correlation ID, audit event, policy
  decision, approval when applicable, and final receipt;
- policy or authorization unavailability stops financial writes safely.

## Layer 10 — iOS, voice, and system integration

Run on supported device/OS combinations and include at least one real device for
authentication, notification, audio, interruption, backgrounding, and network
transition proof.

- generated Swift client matches the backend contract and order/approval state
  fixtures used by TypeScript;
- Buyer and Seller workspace switching cannot cross resource authorization;
- Face ID approval produces a short-lived backend token bound to device, user,
  decision, resource, action, amount, and expiry; replay or substitution fails;
- sensitive notification actions open review and authentication instead of
  executing invisibly;
- deep links, App Intents, App Shortcuts, Spotlight entities, and Live
  Activities expose only bounded, non-sensitive data;
- native voice covers interruption, reconnect, transcript recovery, Bluetooth,
  text fallback, silent mode, and progress states for long tools;
- the bundle and device logs contain no long-lived model, payment, refund, ONDC,
  or signing credentials;
- on-device intelligence unavailable/declined/offline fallbacks work, and local
  model output never commits authoritative commerce state.

## Layer 11 — Agent evaluations, observability, and operations

Maintain a versioned evaluation set for normal and ambiguous shopping, unsafe
or blocked categories, limit violations, conflicting preferences, unsupported
locations, price changes, catalog prompt injection, malicious seller text,
approval bypass, refund fraud, transcription errors, code-switching, and
interrupted conversations.

Score intent, tool, parameters, policy outcome, unauthorized-action count,
verified completion, explanation accuracy, and customer correction. Track
search/checkout/refund/SLA success, policy and approval outcomes, voice latency
and cost, crashes, callback failures, and support recovery under one correlation
ID. Production exercises must prove alerting, runbooks, backup/restore, support
inspection, feature rollback, and a global pause for autonomous writes.

## Release decision matrix

| Claim | Minimum required gate |
| --- | --- |
| AgentGuard domain logic works | Layers 1–2 pass |
| Buyer and Seller share commerce state | Layer 3 pass |
| Buyer/Seller UI passes local acceptance | Layers 1–5 pass twice (including AgentGuard browser proof) |
| Mandate editable + agent tools execute under AG | Milestone 10–11 Layer 5 lanes |
| Buyer Samantha voice under AG | M12: `/api/realtime/status` + orb + `/config` + voice tools lane |
| Safe for controlled external pilot | Layers 1–7 plus security review |
| ONDC network integrated | Layer 8 official conformance evidence |
| Customer-money commerce integrated | Layer 9 plus regulated provider evidence and reconciliation tests |
| Native companion ready | Layer 10 on supported simulators and real devices |
| Production ready | Layers 1–11 plus external security, privacy, accessibility, operational, and regulatory gates |

## Current local safety checklist

The latest CF1 evidence is the 2026-07-22 PostgreSQL `@Chrome` campaign in
`.cursor/skills/ondc-testing/references/matrix-status.md`. Its focused frozen
source fingerprint is
`9c7fadc8fab66f3f456272f5dd8041e357780830bbabfe7185d4c30199704d66`.
It records gateway `198 passed`, Seller `210 passed` plus production build/copy
gate, offline ONDC graders, one complete Buyer customer Pass and one complete
Seller customer Pass with PostgreSQL readback. The worktree was dirty and the
campaign did not establish the required unchanged-source two-pass release
threshold. The older `af98738a` two-pass deterministic artifact remains
historical evidence only; it is not the current CF1 source fingerprint.

- [x] Focused CF1 deterministic support passes on the recorded fingerprint (gateway 198; Seller 210 plus production build/copy gate; targeted Ruff/diff checks; offline ONDC graders).
- [x] Buyer and Seller builds pass.
- [x] Shared schema golden fixtures pass in Python and TypeScript.
- [x] Authenticated ownership and tenant isolation pass.
- [x] Exact approval binding, expiry, atomic consume and replay tests pass.
- [x] Seller SKU reaches Buyer through signed Beckn search/callback and server-owned exchange.
- [x] Checkout creates one order and one inventory reservation.
- [x] Seller fulfilment reaches Buyer.
- [x] Buyer issue and Seller remedy complete.
- [x] Simulated payment/refund success and unknown reconciliation pass.
- [x] Pause and revoke races fail safely.
- [x] Receipts verify and tampering fails.
- [x] Prompt-injection and direct-API bypass attempts fail.
- [ ] Buyer AgentGuard browser lane passes twice on unchanged current source (2026-07-22 current-source Pass 1 complete; Pass 2 not tested).
- [ ] Seller AgentGuard browser lane passes twice on unchanged current source (2026-07-22 current-source Pass 1 complete after owner fixes and one bounded Chrome recovery; Pass 2 not tested).
- [ ] Combined two-sided discovery/order/refund and responsive semantic UI/UX-accessibility smoke passes twice on unchanged current source.
- [ ] Current CF1 source is deployed and revalidated through FQDN/Auth0; the 2026-07-22 campaign was local only.
- [ ] Controlled physical microphone/WebRTC voice proof passes if voice is claimed; configured or text-ready status is not voice proof.
- [x] Validation ledger contains commands, run IDs and artifacts.
- [x] Product UI avoids environment/test labels and describes simulated payment and logistics truthfully.
- [x] No blockchain, Aadhaar, live ONDC or NPCI dependency is implied by the current local product bundle; boot-independence, prohibited-copy and no-Solana-wallet-dependency assertions pass twice.
