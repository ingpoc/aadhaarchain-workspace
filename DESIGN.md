# AgentGuard Design

## Control owner and evidence boundary

This file is the canonical owner for AgentGuard product design, UX philosophy,
information architecture, interaction behavior, visual direction, accessibility,
and design acceptance. It governs ONDC Buyer, ONDC Seller, and the planned iOS
companion. It does not own API contracts, delivery order, or test implementation.

Use these owners together:

- Product promise and non-goals: [`PRODUCTIDEA.md`](PRODUCTIDEA.md)
- Domain and trust boundaries: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Delivery order: [`IMPLEMENTATIONPLAN.md`](IMPLEMENTATIONPLAN.md)
- Verification evidence: [`TESTINGPLAN.md`](TESTINGPLAN.md)
- Buyer and Seller implementation outcomes: `ondcbuyer/GOAL.md` and
  `ondcseller/GOAL.md`
- Current web tokens and components: `ondcbuyer/src/app.css`,
  `ondcseller/src/app.css`, and each app's `components/ui/`

Decision status:

| Decision | Status | Basis |
| --- | --- | --- |
| AgentGuard is the product and authority layer | Confirmed | Product owner documents |
| Convenience, control, trust, and recovery govern admission | Confirmed | Product promise |
| Risk, not technical complexity, determines friction | Confirmed | Product and architecture owners |
| Buyer, Seller, and iOS remain distinct workspaces | Confirmed | Release plan and platform architecture |
| Cool silver canvas, deep teal accent, Outfit, and JetBrains Mono | Confirmed current direction | Shared shipped web tokens and validated Seller captures |
| Restrained, calm, operational, and human rather than futuristic | Inferred | Financial consequence, frequent operations, and current UI |
| Samantha may name the visible assistant but not the product | Inferred reconciliation | Current app behavior plus AgentGuard product identity |
| Exact navigation and components may evolve by platform | Inferred | Current gaps and planned release scope |

Current captures prove only the existing Seller experience and visual language.
They do not prove that Buyer, Seller, or iOS already meet this document.

## Product promise

> Tell the agent what you need. It searches, compares, prepares the work, and
> acts only inside boundaries you can see and change.

### Design thesis

AgentGuard should make delegated commerce feel calm and legible: the agent does
the operational work, while human authority, financial consequence, and recovery
remain visible at the moment they matter.

### Experience thesis

A person should move from effort or operational pressure to informed confidence:
state the outcome, inspect the prepared result, intervene only at a meaningful
boundary, and leave with verified state plus a clear way to stop or recover.

### First impression

Within five seconds, a user should understand:

1. what needs attention now;
2. what the agent can handle;
3. whether any money, order, inventory, or customer consequence is pending; and
4. where to pause the agent.

### Non-goals

The experience is not:

- an ONDC protocol dashboard;
- an identity, KYC, blockchain, or trust-score product;
- a generic chatbot wrapped around forms;
- an autonomous system that hides consequential work;
- a gamified engagement product;
- a place to expose model internals, tool calls, policy machinery, or raw traces;
- proof of live payment, ONDC, Siri, or Apple capability before evidence exists.

## Governing philosophy

### Principles

1. **Outcome before machinery.** Lead with the product, order, customer, amount,
   deadline, or remedy. Reveal technical provenance only on demand.
2. **Prepared work before irreversible action.** Let the agent search, compare,
   draft, stage, and preview freely. Put friction at the binding boundary.
3. **Landed truth before persuasion.** Compare final payable amount, delivery,
   return conditions, seller reliability, and sponsorship—not headline price.
4. **One consequence, one clear decision.** A consequential screen has one
   dominant action and the exact context needed to judge it.
5. **Trust is continuous.** Authority, active limits, pending approvals, recent
   actions, and Pause are normal product surfaces, not error states.
6. **Verified state beats optimistic language.** Never announce a purchase,
   refund, fulfilment step, or catalog change until the backend verifies it.
7. **Recovery is part of completion.** Receipts, correction, retry, cancellation,
   dispute, and support belong in the journey—not in a remote settings page.
8. **Progressive disclosure protects attention.** Show the decision first,
   supporting evidence second, and protocol/audit detail last.

### Anti-principles

Reject a design that:

- gives the assistant more visual authority than the customer;
- treats every agent action as a notification or approval;
- hides final cost, expiry, changed price, or uncertainty below the primary action;
- uses badges or disabled controls as if they were authorization;
- duplicates Agent, Assistant, AI, and AgentGuard into competing product stories;
- says “AI recommended this” without explaining the basis and trade-off;
- uses decorative glass, gradients, glow, or motion to imply intelligence;
- turns dense operational data into a wall of equally weighted cards;
- removes completed work after a recoverable error;
- makes demo or simulated systems look production-real.

## Audience, context, and trust posture

### Buyer

A buyer may be shopping quickly, comparing unfamiliar sellers, speaking while
hands-busy, or returning to a delayed order. They need plain language, price
confidence, flexible input, and a short path from intent to a prepared basket.

### Seller

A small seller or operator works repeatedly under time pressure. They need an
attention queue, SLA and inventory risk, bulk efficiency, unambiguous drafts
versus binding actions, and fast recovery from exceptions.

### Shared posture

- Assume intermittent connectivity, interrupted sessions, and code-switching.
- Never require expertise in ONDC, AI systems, payment rails, or policy language.
- Treat product descriptions, customer messages, transcripts, and model output
  as untrusted content.
- Keep private identity, address, payment, and raw conversation data out of
  explanations and receipts unless strictly necessary and authorized.
- Use dignity-preserving copy for denial, empty results, fraud review, payment
  uncertainty, and support escalation. Never blame the customer.

## Experience model and critical journeys

The shared journey arc is:

> **Ask → Understand → Prepare → Compare → Check authority → Approve if needed →
> Execute → Verify → Receive receipt → Recover or continue**

### Buyer first-value journey

1. Sign in and set location/delivery preferences.
2. State a need conversationally or search manually.
3. Review the agent's interpreted requirements before results.
4. Compare normalized options and a suggested basket.
5. Edit products, variants, quantities, seller, or preferences.
6. Review final landed cost, fulfilment, returns, and authority outcome.
7. Approve only if the exact transaction exceeds the mandate.
8. See verified payment/order state and an Intent Receipt.

The agent must not fill or purchase a basket before showing its interpretation.
Search failure preserves the request and offers edit, broaden, retry, or manual
browse. A price or inventory change returns to review; it never silently proceeds.

### Buyer repeat and recovery journey

Orders are durable objects, not terminal confirmation screens. Every order shows
the timeline, delivery, invoice, seller/fulfilment party, cancellation/return
rules, issue history, refund state, supporting receipts, and one relevant next
action. Unknown payment or confirmation state is shown as “We are verifying this”
with no blind purchase retry.

### Seller first-value and repeat journey

1. Complete business/store setup without handling identity documents in the UI.
2. Create or import a draft catalog and resolve validation issues.
3. Publish through an exact preview when authority requires it.
4. Work an attention queue ordered by consequence and deadline.
5. Accept/reject, pack, dispatch, substitute, refund, or escalate from the order.
6. See verified state, settlement effect, and receipt.

The Seller Overview must answer: **What needs attention? What is at risk? What
can the agent handle?** Drafts and suggestions must never resemble completed
catalog, inventory, fulfilment, or refund state.

### Approval journey

An approval card must show, in this order:

1. action and consequence;
2. amount, quantity, customer/counterparty, and resource;
3. why approval is required and which boundary was exceeded;
4. what changes after approval;
5. expiry and whether anything has already happened;
6. Approve, Modify, Reject, Ask agent, and View evidence.

Approval binds one exact action. If amount, seller, items, resource, mandate,
inventory commitment, or expiry changes, return to review. Face ID or another
step-up confirms only that bound action, never a reusable session of authority.

### Recovery journey

Every consequential result offers the applicable next path: pause, undo before
commit, cancel, retry safely, reconcile, return, replace, dispute, or contact
support. If recovery is impossible, say why, show what remains true, and identify
the owner of the next response.

## Product objects and information architecture

Primary objects are: Agent, Mandate, Approval, Intent Receipt, Product, Cart,
Quote, Order, Issue, Refund, Catalog Item, Inventory Position, Store, and
Settlement. Relationships should be navigable in both directions: an Order links
to its Approval and Receipt; a Receipt links back to the affected Order; an Agent
links to current authority and activity.

### Buyer web target

- **Home** — conversational entry, active delivery, recent orders, pending
  approvals, saved/reorder suggestions, and agent status.
- **Search** — manual/conversational discovery, results, comparison, and saved
  searches.
- **Cart** — durable basket, seller groups, final-cost preview, and changes.
- **Orders** — active/history, timeline, issues, returns, refunds, and receipts.
- **Agent** — conversation, current mandate, approvals, activity, memory controls,
  and Pause.
- **Account** — identity, locations, payments, privacy, devices, and security.

### Seller web target

- **Overview** — attention queue, SLA risk, low stock, returns, settlement
  exceptions, pending approvals, and agent actions.
- **Orders** — acceptance, packing, fulfilment, exceptions, remedies, and history.
- **Catalog** — drafts, published items, validation, import, pricing, promotions.
- **Inventory** — stock positions, reservations, thresholds, and bulk changes.
- **Agent** — conversation, mandate, approvals, activity, recommendations, Pause.
- **Business** — store, staff, serviceability, policies, settlement, and security.

### iOS target

Buyer mode uses **Today, Agent, Orders, Approvals, Account**. Seller mode uses
**Overview, Orders, Catalog, Agent, Business**. A visible workspace selector
switches roles; Buyer and Seller operations never share a crowded dashboard.
Siri, Spotlight, notifications, widgets, and Live Activities deep-link into these
objects but do not become parallel information architectures.

Navigation expresses destinations, not status. Healthy identity/runtime badges
stay out of the primary bar; surface only actionable problems. On compact web,
preserve the same object hierarchy with a native-feeling menu or bottom
navigation. Do not force desktop pills into a compressed row.

## Disclosure and interaction rules

### Information levels

- **Persistent:** current workspace, relevant agent state, primary object status,
  final cost/financial state, and a reachable Pause control on Agent/Approval
  surfaces.
- **Contextual:** the next action, changed values, SLA/expiry, and authority reason.
- **On demand:** alternatives considered, policy detail, protocol provenance,
  correlation ID, raw audit chronology, and technical diagnostics.
- **Interruptive:** exact approval, price/inventory change at commit, payment/order
  uncertainty, security step-up, or imminent SLA breach.
- **Remove:** decorative status, duplicate explanations, internal tool/runtime
  labels, raw prompts, chain-of-thought, and unactionable telemetry.

### Interaction

- One primary action per decision region. Secondary actions remain visually quiet.
- Destructive and financial actions use explicit verbs: “Pay INR 620,” “Issue INR
  1,250 refund,” “Reject order,” not “Continue.”
- Preserve entered data, filters, transcript, and scroll position after errors or
  authentication handoff.
- Show inline progress for work under three seconds; show cancellable staged
  progress and background continuation for longer operations.
- Never use an ambiguous spinner during a financial write. Name the stage:
  “Preparing checkout,” “Confirming payment,” “Verifying order.”
- Optimistic UI is allowed only for reversible local preparation, never as proof
  of payment, refund, catalog publication, inventory commitment, or fulfilment.

## AI authority, explanation, memory, and recovery

The user sees one assistant identity. Internally specialized capabilities may
route work, but they must not appear as a committee of agents.

The assistant may execute read-only work, prepare reversible drafts, and act
inside a confirmed mandate. It must preview and obtain exact approval for
high-risk exceptions, and must stop safely when authorization cannot be verified.

Every recommendation answers:

- Why this result?
- What alternatives were considered?
- Is it sponsored?
- What information and preference were used?
- What trade-off was made?
- What can the customer change?

Distinguish customer facts, authoritative commerce state, agent interpretation,
and unverified external content. Uncertainty is specific: “Two sellers have not
confirmed inventory,” not “The AI may be wrong.”

Memory controls live with the Agent: view, edit, delete, disable personalization,
or keep a conversation temporary. Conversation memory, preferences, mandates,
commerce records, and derived insights are separate objects.

“Samantha” may be the assistant's conversational name. “AgentGuard” names the
product and its authority/receipt system. Never present them as competing brands.

## Visual identity and theme

### Character

The intended axes are **restrained, human-warm, editorial-operational, airy by
default, serious without severity, and familiar with selective novelty**.

The interface should resemble a calm, well-run service desk—not a bank vault, a
crypto terminal, or a science-fiction command center. Density increases only on
Seller tables and queues where scan efficiency is the job.

### Current visual language

- Cool silver canvas and near-white elevated surfaces.
- Deep teal as the single brand/action accent.
- Charcoal text with quiet slate secondary copy.
- Amber for caution and expiring attention; red only for destructive/error state.
- Light and dark appearances retain semantic roles and contrast.
- Outfit for human-readable display/body text.
- JetBrains Mono only for amounts, quantities, timestamps, countdowns, compact
  references, and state-machine data—not paragraphs or brand headings.

Exact values remain owned by each app's `app.css` until a shared token package is
introduced. Buyer and Seller must converge semantically before creating shared
tokens; do not copy values into a third token owner.

### Geometry, materials, and spacing

- Use open composition, clear section rhythm, and strong type hierarchy before
  adding containers.
- Cards group one coherent object or decision. Avoid cards inside cards when a
  divider or spacing is enough.
- Rounded geometry should feel approachable, not toy-like. Reserve full pills for
  compact status, filters, or small actions; do not make every control a pill.
- Borders carry most grouping. Shadows are shallow and rare, used for temporary
  elevation, approval focus, or an anchored agent surface.
- Primary numbers align and use tabular figures. Financial summaries expose the
  final amount first and the calculation nearby.
- Product imagery supports comparison and recognition; it never substitutes for
  variant, seller, delivery, price, or accessibility text.
- Icons accompany labels for consequential actions and status; icons alone require
  an accessible name and must not carry unique meaning.

### Signature moves

1. **Authority ribbon.** On Agent, Approval, Checkout, and Refund surfaces, a
   compact continuous summary connects current limit, proposed consequence,
   decision, and Pause. It expands into evidence without changing vocabulary.
2. **Intent trace.** Material activity uses a readable sequence—requested,
   understood, checked, approved if needed, executed, verified, receipted. It is
   the same conceptual object in chat, order history, and support.

These moves express the product promise. Do not replace them with a generic
gradient orb, chat bubble, trust score, or technical event log.

## Motion, haptics, and sound

Motion exists to explain state, preserve continuity, confirm a meaningful action,
or orient after a workspace/deep-link transition.

- Use brief opacity/position transitions for staged content and status change.
- Never animate monetary values in a way that delays comprehension.
- Approval expansion should preserve the action card's location and context.
- A completed action may receive one restrained confirmation; repeated agent
  activity does not pulse, glow, or celebrate.
- Voice interruption stops audible output immediately and keeps transcript/tool
  state visible.
- Haptics distinguish selection, successful authenticated approval, and failure,
  but every meaning also appears in text/visual state.
- Sound is opt-in/context-aware and never the only delivery of SLA or payment risk.
- Reduced Motion removes spatial travel and decorative animation while preserving
  immediate state changes and progress text.

## Content voice and terminology

Voice is concise, calm, accountable, and specific. Prefer familiar commerce
language and active verbs. Explain the consequence before the system rule.

Use:

- “The agent needs your approval.”
- “This order is INR 620 above your automatic purchase limit.”
- “No payment was made.”
- “The item was paused because inventory reached zero.”
- “Payment succeeded. We are still verifying the order.”

Avoid customer-facing use of: tool call, executor, principal, runtime, policy
evaluation, guard rejection, model confidence, hallucination, chain-of-thought,
nonce, webhook, callback, or state machine. “AgentGuard” may label the product or
authority area; it is not a substitute for explaining the decision.

Use sentence case. Avoid exclamation marks for money, refunds, disputes, or risk.
Localize currency, dates, address order, pluralization, and names. Support Hindi-
English code-switching without treating one language as an error state.

## Accessibility and inclusion

Accessibility is a release gate and a design input.

- Use semantic landmarks, one logical page heading, real controls, programmatic
  names, and status announcements that do not steal focus.
- Keyboard, switch, pointer, touch, and voice users must complete the same buyer,
  seller, approval, pause, receipt, and recovery journeys.
- Focus order follows the decision hierarchy. Authentication/deep-link return
  restores focus to the initiating control or resulting heading.
- Touch targets are at least 44 by 44 points on native and equivalently generous
  on compact web.
- Text scales/reflows without clipping final cost, expiry, policy reason, or action.
- Color, position, haptic, sound, and motion are never the only state cue.
- Maintain WCAG 2.2 AA contrast at minimum; consequential text and controls should
  exceed minimums where feasible.
- Countdown/expiry includes absolute time and does not demand rapid interaction;
  warn and allow safe refresh before expiration.
- Live voice always provides transcript, text input, silent response, interruption,
  and recovery. Captions and accessible descriptions accompany media.
- Plain-language summaries precede detailed policy, receipt, and audit content.
- Avoid stereotypes in product examples, recommendations, risk, or fraud language.

## Responsive and platform adaptation

Preserve the hierarchy and emotional sequence, not identical layouts.

- **Compact web:** single-column decision flow, sticky contextual action only when
  it does not obscure content, drawers for filters/detail, and reachable navigation.
- **Desktop web:** use width for comparison, queues, evidence beside a decision,
  and stable object context—not for more decorative cards.
- **iPhone:** follow native navigation, sheets, authentication, notifications,
  Dynamic Type, VoiceOver, Reduce Motion, and safe-area behavior.
- **iPad/multitasking:** allow split detail where it preserves selection and task
  continuity; support keyboard and pointer without hiding touch paths.
- **Siri/Shortcuts:** bounded retrieval or flow initiation returns concise speech,
  a structured result, deep link, and explicit next action.
- **Notifications/Live Activities:** show customer-relevant progress or expiring
  decisions only. Sensitive actions open authenticated review.

## State, privacy, safety, and dignity rules

Every important journey or object defines applicable states before visual polish:

- empty/first use;
- loading and progressive loading;
- partial, stale, or awaiting external party;
- ready/active;
- success/verified completion;
- offline/reconnecting;
- permission or authentication required/denied;
- blocked, paused, revoked, expired, withdrawn, or unavailable;
- recoverable error, unknown outcome, and terminal error;
- correction, undo, cancellation, deletion, dispute, and return.

Empty states explain value and offer one next action. Errors preserve completed
work and identify what is safe to retry. Unknown financial state stops duplicate
execution and shows reconciliation progress.

Request permission at the point of benefit. Explain why before invoking location,
microphone, notifications, contacts, biometrics, or tracking. Provide a functional
fallback where the platform permits it.

Never expose full addresses, payment data, raw identity evidence, customer
messages, or model transcripts in headers, notifications, shared screenshots, or
receipts. Support and audit views use minimum necessary disclosure and explicit
role/resource authorization.

## Build handoff contracts

These contracts preserve product intent through implementation. They define
observable outcomes and evidence, not framework structure. Product scope lives in
`PRODUCTIDEA.md`; authoritative behavior and ownership live in `ARCHITECTURE.md`;
delivery sequencing lives in `IMPLEMENTATIONPLAN.md`; executable acceptance and
evidence live in `TESTINGPLAN.md`.

### Buyer discovery and comparison

- **Entry and arrival:** A signed-in buyer starts from Home or Search with a
  serviceable location, then submits a conversational or manual request. Arrival
  is proven by an editable interpretation of the need followed by normalized
  results; a spinner, transcript, or accepted request alone is not arrival.
- **Primary action and postcondition:** The buyer selects an explained option and
  adds a product/variant to the durable cart. The observable postcondition is the
  chosen seller, variant, quantity, and current landed-cost estimate in the cart.
  No order, payment, or protected authority is consumed.
- **Hierarchy and async behavior:** Interpretation and editable constraints come
  first; landed cost and delivery dominate each comparison; reliability, returns,
  cancellation, sponsorship, trade-off, and alternatives follow. Late seller
  results may update counts and options but must not move a focused control,
  silently replace a selection, or hide that comparison is still partial.
- **States and recovery:** Cover first use, loading, partial network response,
  zero results, stale price/availability, offline cache, location permission
  denied, malformed seller content, recoverable failure, and return from product
  detail. Preserve query, interpretation, filters, selection, and scroll position.
- **Navigation, layout, and accessibility:** Back returns to the same result state;
  manual search remains available beside conversation. Compact layouts stack the
  decision sequence and disclose filters on demand; larger layouts may compare
  columns. Interpretation changes, result counts, sponsorship, and price updates
  are semantically announced without stealing focus.
- **Dependencies and acceptance:** Buyer scope is owned by `ondcbuyer/GOAL.md`;
  commerce truth and recommendation boundaries by `ARCHITECTURE.md`; token and
  component behavior by `ondcbuyer/src/app.css` and `components/ui/`. Acceptance
  requires semantic query-to-cart proof, partial/zero-result recovery, landed-cost
  comparison, keyboard/screen-reader completion, compact/desktop captures, and
  evidence from `TESTINGPLAN.md`. Multi-seller production behavior remains a CF2
  dependency until its authoritative services and fixtures exist.

### Buyer checkout and exact approval

- **Entry and arrival:** The buyer enters from a non-empty durable cart after
  address, inventory, price, fulfilment, and quote revalidation. Arrival is the
  exact checkout preview: merchant, items, quantities, final landed cost,
  delivery/return terms, changed values, and the current AgentGuard decision.
- **Primary action and postcondition:** Within mandate, the primary action commits
  the exact checkout. Outside mandate, it opens the bound Approval handoff; it
  does not purchase. Completion requires authoritative payment and order state
  plus a signed Intent Receipt—not a successful client request or agent claim.
- **Hierarchy and async behavior:** Final amount and changed values stay beside
  the action. Progress names the current stage: preparing, confirming payment,
  verifying order. A late price, inventory, mandate, seller, or fulfilment change
  invalidates the preview and returns to review without shifting the action under
  the user's pointer or focus.
- **States and recovery:** Cover ready, revalidating, quote expired, price changed,
  inventory unavailable, address/payment permission required, approval required,
  approval expired/mismatched/consumed, payment declined, payment unknown,
  order-confirmation unknown, offline interruption, success, cancellation before
  commit, and safe retry/reconciliation. Preserve cart and entered delivery data.
- **Navigation, layout, and accessibility:** Back returns to the cart without
  losing valid work. Authentication returns to the exact decision. The action
  summary remains reachable without obscuring full terms. Amount, expiry, change,
  approval scope, and “No payment was made” state must survive text scaling and
  be perceivable without color, motion, haptics, or sound.
- **Dependencies and acceptance:** Authority and commerce contracts are owned by
  `ARCHITECTURE.md`; build phase by CF1–CF2 in `IMPLEMENTATIONPLAN.md`; verification
  by the checkout, replay, reconciliation, receipt, and accessibility gates in
  `TESTINGPLAN.md`. Acceptance requires one verified in-limit purchase, one exact
  over-limit approval, mutated-request rejection, same-key replay with one effect,
  restart recovery, signed-receipt verification, and responsive semantic proof.

### Buyer order, issue, and recovery

- **Entry and arrival:** The buyer opens an order from Orders, a receipt, support,
  notification, deep link, or checkout completion. Arrival is the matching order
  reference with authoritative status and timeline; a generic Orders shell is not
  sufficient.
- **Primary action and postcondition:** The primary action follows current state:
  Track, Cancel, Return, Replace, Review refund, Dispute, or Contact support. The
  postcondition is a persisted request/status with an updated timeline and receipt
  or a clear statement that no change occurred.
- **Hierarchy and async behavior:** Current status, expected next event, and one
  relevant action lead. Seller/fulfilment party, invoice, issue history, refund,
  approvals, and receipts remain linked. Callbacks may append or reconcile events
  but must not reorder history ambiguously or announce completion before verified
  state.
- **States and recovery:** Cover no orders, loading, partial/stale tracking,
  delivered, cancellation/return eligibility, request pending, refund pending,
  duplicate callback, payment-success/order-unknown, offline, permission denied,
  disputed, failed, and closed. Unknown state stops blind retry and shows who is
  verifying what; errors preserve evidence and drafted issue text.
- **Navigation, layout, and accessibility:** Deep links restore the exact order
  and intended action; Back respects the originating list/filter. Compact layouts
  use one chronological reading order; larger layouts may place stable order context
  beside the timeline. Status updates and recovery ownership have stable semantic
  labels and do not rely on a map, color, or animation.
- **Dependencies and acceptance:** Order/issue ownership lives in
  `ARCHITECTURE.md`, Buyer outcomes in `ondcbuyer/GOAL.md`, and transaction-state,
  duplicate-event, refund, support, and assistive-technology proof in
  `TESTINGPLAN.md`. Production cancellation, return, refund, and grievance depth
  remains a CF2 dependency; acceptance cannot be inferred from a static timeline.

### Seller attention to fulfilment

- **Entry and arrival:** A signed-in seller enters Overview directly or through
  an SLA, order, inventory, return, settlement, or approval deep link. Overview
  arrival is proven by an attention queue that answers what needs attention, what
  is at risk, and what the agent can handle—not by aggregate metrics alone.
- **Primary action and postcondition:** The operator opens the highest-consequence
  item and performs or delegates its next valid action. Completion is verified
  catalog, inventory, acceptance, packing, dispatch, remedy, refund, or escalation
  state with customer/settlement impact and receipt where material.
- **Hierarchy and async behavior:** Deadline and consequence order the queue;
  pending acceptance, SLA risk, low stock, returns, approvals, and settlement
  exceptions precede analytics. Agent-completed and merely staged work are
  distinct. New events update queue position without moving the focused item or
  disguising stale data as current.
- **States and recovery:** Cover first store setup, empty catalog/orders, loading,
  partial import, stale inventory, offline, staff permission denied, SLA warning,
  duplicate order event, out-of-stock substitution, rejected transition, refund
  unknown, settlement exception, recoverable retry, escalation, and return to the
  same queue context. Preserve drafts, selections, filters, and evidence.
- **Navigation, layout, and accessibility:** Order/catalog detail returns to the
  same queue or filtered list. Dense desktop tables are allowed when scanning is
  the job; compact layouts preserve consequence order and expose secondary detail
  on demand. Countdown, risk, draft/binding state, and changed inventory require
  textual and semantic cues beyond color.
- **Dependencies and acceptance:** Seller outcomes live in `ondcseller/GOAL.md`;
  authority and state transitions in `ARCHITECTURE.md`; visual owners are
  `ondcseller/src/app.css` and `components/ui/`; end-to-end Seller, SLA, refund,
  keyboard, responsive, and live-capture gates live in `TESTINGPLAN.md`. Complete
  lifecycle, settlement, and analytics behavior remains a CF3 dependency.

### Exact approval review

- **Entry and arrival:** A user enters from Checkout, Agent, Approvals, an order,
  a notification, Siri/App Intent handoff, or an expiring-action deep link. Arrival
  is the exact proposed action with resource/counterparty, amount or quantity,
  consequence, reason, changed values, and expiry; a badge or approval ID alone
  is not arrival.
- **Primary action and postcondition:** Approve authorizes only the displayed
  bound action and proceeds to verified execution. Modify returns to the owning
  draft or
  mandate without executing; Reject records the decline; Ask agent/View evidence
  changes understanding only. The result explicitly states what happened and
  whether money or shared state changed.
- **Hierarchy and async behavior:** Consequence and scope lead, followed by reason,
  change after approval, expiry, supporting evidence, and actions. Expiry,
  revocation, mandate change, price change, or completed execution disables stale
  approval in place and offers the correct return path; controls never silently
  retarget a new proposal.
- **States and recovery:** Cover loading, evidence partial, ready, step-up required,
  biometric unavailable/failed, expired, changed/mismatched, already consumed,
  paused/revoked, rejected, execution pending/unknown, success, offline, and
  notification permission denied. Preserve the proposal through authentication;
  never preserve a reusable approval token for another action.
- **Navigation, layout, and accessibility:** Cancel returns to the originating
  object with no execution. Compact/native presentations may use a sheet or full
  screen; desktop may use a focused panel, but full consequence and evidence stay
  readable. Focus begins at the approval heading, destructive alternatives are
  labelled, expiry is not color-only, and step-up has an accessible fallback when
  platform policy permits.
- **Dependencies and acceptance:** Decision, approval, authentication, privacy,
  and receipt ownership lives in `ARCHITECTURE.md`; native delivery remains
  CF4–CF6 in
  `IMPLEMENTATIONPLAN.md`; exact-binding, replay, expiry, pause/revoke, cross-tenant,
  notification, and accessibility evidence lives in `TESTINGPLAN.md`. Web evidence
  does not prove Face ID, Siri, notification, or native behavior.

### Agent authority, Pause, activity, and receipts

- **Entry and arrival:** The user enters Agent from primary navigation, an agent
  entry control, a pending approval, or a receipt. Arrival is a visible current
  task/conversation plus the current authority ribbon showing active/paused state,
  meaningful limits, pending approvals, and Pause—not a generic chat greeting.
- **Primary action and postcondition:** The conversational primary action asks or
  assigns work; authority controls edit/confirm the mandate or Pause. A confirmed
  mandate creates a new visible authority version; Pause immediately blocks new
  protected execution while preserving read/help capability and saved limits.
- **Hierarchy and async behavior:** Current task and authority precede approvals,
  Intent traces, receipts, then memory/detail controls. Streaming transcript and
  tool progress may grow without covering Pause, moving focused controls, or
  presenting attempted work as verified. Activity uses requested, understood,
  checked, approved if needed, executed, verified, receipted.
- **States and recovery:** Cover first use/no mandate, loading, agent unavailable,
  active, paused, revoked, mandate draft/unconfirmed/stale, pending approval,
  reconnecting voice, interrupted transcript, tool unavailable, policy service
  unavailable, receipt verification failure, offline read-only history, correction,
  resume, memory deletion, and return to the originating commerce object.
- **Navigation, layout, and accessibility:** Agent is a destination, not a floating
  layer competing with the current page. An anchored entry may persist only when
  it does not obscure content or the page's primary action. Text and silent modes,
  transcript recovery, keyboard operation, semantic progress, reduced motion, and
  immediate voice interruption are required; Buyer and Seller workspaces remain
  visibly distinct on every platform.
- **Dependencies and acceptance:** Agent/mandate/tool ownership lives in
  `ARCHITECTURE.md`; Buyer/Seller outcomes in their `GOAL.md` files; Realtime,
  native, memory, and system integration remain sequenced in
  `IMPLEMENTATIONPLAN.md`; mandate, pause, tool, receipt, voice, privacy,
  interruption, responsive, and assistive-technology evidence lives in
  `TESTINGPLAN.md`. Current web/Seller captures do not prove Buyer voice or iOS.

## New-screen decision filter

Before adding or accepting a screen, answer yes to all applicable questions:

1. Does it advance a named customer or operator outcome?
2. Is it a destination or object that cannot live coherently in an existing one?
3. Is the dominant content and single primary action obvious in five seconds?
4. Are authoritative fact, agent interpretation, and untrusted content distinct?
5. Is final cost/consequence visible beside the action it affects?
6. Does risk—not implementation complexity—determine confirmation friction?
7. Are correction, safe exit, and recovery present?
8. Are all material states designed, including offline and unknown outcome?
9. Can the flow be completed with keyboard/screen reader and without color,
   motion, sound, haptics, or vision as the only cue?
10. Does it use the restrained silver/teal system and one of the signature moves
    only when relevant?
11. Does it remove internal jargon and duplicate status?
12. Does live or captured evidence prove the intended hierarchy and behavior?

An attractive screen that fails the authority, consequence, recovery, or
accessibility rules is not AgentGuard design.

## Validation and governance

A design change is complete only when evidence covers:

- **Philosophical fit:** advances convenience, control, trust, or recovery without
  violating an anti-principle.
- **Journey fit:** a representative user can begin, understand, correct, complete,
  and recover without developer help.
- **Trust fit:** exact consequence, authority reason, approval scope, verified
  outcome, Pause, and receipt work as promised.
- **Visual fit:** live capture has clear hierarchy, consistent theme, responsive
  behavior, and no accidental density or pill/card proliferation.
- **Accessibility:** semantic and assistive-technology proof covers the full
  consequential path, not only isolated controls.
- **State fit:** empty, loading, partial, stale, success, error, offline,
  permission, blocked, and recovery states exist where applicable.
- **Handoff fit:** each affected critical journey proves its entry, unique arrival,
  primary action, semantic postcondition, state/recovery coverage, continuity,
  platform invariants, owner dependencies, and acceptance evidence.
- **Parity:** compare live/captured output to the accepted reference; source and
  build success alone are insufficient.

`TESTINGPLAN.md` owns the executable gates and evidence ledger. Mockups and
captures are references, not a second philosophy owner. If implementation and
this file conflict, resolve the owner decision before normalizing the drift.

## Explicit deferrals

- Exact shared token extraction is deferred until Buyer and Seller semantics
  converge and duplication has measurable cost.
- Final iOS component, motion, haptic, sound, App Intent, and Live Activity detail
  is deferred until the native shell and supported OS/device matrix exist.
- Fully autonomous purchase, high-value refund, generic computer use, and open-
  ended Siri execution remain prohibited until customer, security, reconciliation,
  and recovery evidence changes the product boundary.
- Advanced personalization remains opt-in and deferred until preference memory is
  inspectable, editable, deletable, and provenance-aware.
- Multilingual voice expansion follows measured transcription, correction, task
  completion, latency, and safety evidence—not language availability alone.

Reconsider a deferral only through the relevant product, architecture, privacy,
and testing owners; do not introduce it opportunistically in a screen task.
