# AgentGuard — Safe Agentic Commerce on ONDC

## Product definition

AgentGuard lets people and businesses delegate commerce work to AI agents
without delegating unlimited authority.

The agent may discover, prepare, recommend, and communicate freely. Before a
consequential action executes, AgentGuard checks a human-confirmed mandate,
allows the action, requests approval for one exact exception, or blocks it. It
then produces an Intent Receipt that explains what acted, for whom, under which
policy, and with what result.

> Let an agent operate. Keep consequential actions inside human intent.

ONDC Buyer and ONDC Seller demonstrate the same control contract from both
sides of a transaction. AgentGuard is the product; the apps are reference
integrations. AadhaarChain is not a product dependency, and blockchain is not
part of the product architecture.

## Customer problem

AI agents can already search, write, classify, and call APIs. The unresolved
problem is safe authority: API keys and login sessions usually grant far more
power than the user intended. KYC proves identity, and payment limits constrain
value, but neither establishes why an autonomous action was permitted.

The product must answer five questions:

1. Who is the principal and which agent is acting?
2. What outcome and actions did the principal authorize?
3. Which constraints apply to amount, counterparty, category, resource, time,
   and frequency?
4. When must the human approve an exact exception?
5. Can another party later verify the decision without receiving private data?

## First customer

The first payer is a commerce platform, seller platform, or managed-commerce
provider enabling AI-assisted operations. The first end users are:

- a buyer who wants an agent to find and buy an appropriate product; and
- a small seller who wants an agent to run routine store operations.

The initial commercial wedge is seller automation because catalog, inventory,
orders, support, and refunds create frequent high-value actions. The Buyer app
proves that the control contract works across the transaction, not just inside
one back office.

## Irreducible product

### Shared AgentGuard

- Register a principal and an agent using host-application identity.
- Turn natural-language authority into a small deterministic mandate.
- Let the principal **edit** allowed actions and auto-approve limits, then
  confirm the compiled mandate in plain language.
- Evaluate every protected action on the server.
- Allow, block, or request approval for one exact action.
- Bind approval to principal, agent, action, resource, amount, policy version,
  nonce, and expiry; consume it atomically once.
- Pause or revoke authority immediately.
- Issue a signed, privacy-minimizing Intent Receipt.

Without any one of these capabilities, the product cannot safely delegate and
prove consequential action. Everything else must justify itself separately.

### Agent runtime as executor

Runtime agents **operate the Buyer and Seller apps** through a shared tool
runner (search, navigate, cart, checkout, publish, refund). They are not
chat-only copilots. Text protected tool calls AgentGuard `actions/execute`
before mutating commerce state. Tools offered to the model are filtered by the
confirmed mandate so the agent cannot even request disallowed actions.

- **Text host (current):** Cursor agent runtime (`CURSOR_API_KEY`).
- **Voice host (Buyer):** OpenAI Realtime `gpt-realtime-2.1` over WebRTC;
  same tool runner. Wholesale migration to OpenAI Agents SDK is optional later,
  not a requirement for the demo.

Hermes browser scripts are test automation, not the product agent.

### ONDC Buyer

- Configure shopping-agent limits (checkout auto-approve ceiling, allowed
  actions) and confirm the mandate.
- Talk to the shopping agent in text (and later voice) so it searches, navigates
  pages, and adds items to the cart under that mandate.
- Discover a product published by the Seller demo.
- Compare and add it to a cart without approval friction for preparation.
- Let the agent drive checkout through guarded tools.
- Enforce checkout constraints and request approval when needed.
- Execute a simulated payment only after authorization.
- Track the order and raise a cancellation, return, or issue request.
- Show the buyer the agent's current authority and activity receipts.

### ONDC Seller

- Configure operations-agent limits (refund auto-approve ceiling, allowed
  actions) and confirm the mandate.
- Let the operations agent run catalog, inventory, order, and refund tools under
  AgentGuard.
- Create and update catalog items and inventory with an agent.
- Publish the item into the local ONDC-shaped demo exchange.
- Receive the Buyer's order and manage acceptance and fulfilment.
- Let an agent draft customer responses without approval.
- Guard commitments and remedies: publish, inventory reduction, order rejection,
  cancellation, compensation, and refund.
- Show the seller current authority, exceptions, pause, and receipts.

These jobs form one demonstrable loop: seller publishes, buyer discovers and
checks out, seller fulfils or resolves an issue, and both sides retain evidence
of delegated authority.

## Product boundary

AgentGuard governs actions, not reasoning. It does not need to approve search,
comparison, summarization, drafting, or recommendations because those steps are
reversible and create unnecessary consent fatigue. It does govern writes that
spend money, expose or commit scarce inventory, change an order, promise a
remedy, or communicate a binding commercial decision.

The AI proposes structured actions. Deterministic code authorizes them. The
model never decides whether its own action is allowed.

## Relationship to NPCI Token Nxt

NPCI describes Token Nxt as a forum for ideas that improve payment access,
convenience, security, and trust. AgentGuard's contribution is not a new payment
rail. It is the missing authority layer between an AI agent and existing rails:

- plain-language delegation instead of sharing credentials;
- minimum necessary authority rather than account-wide access;
- transaction previews and step-up approval for unusual actions;
- one-time nonces, expiry, pause, and revocation against fraud and replay;
- receipts that connect payment or refund to the user's original intent; and
- no PIN, OTP, full payment credential, or raw identity evidence exposed to the
  model.

UPI Circle, AutoPay, tokenized credentials, or future NPCI agent-payment
interfaces can execute payment authority. AgentGuard supplies semantic purpose,
commerce context, and accountable agent control around them. The demo must not
claim an NPCI integration that does not exist.

## Why ONDC matters

ONDC is valuable because buyer and seller applications can transact without
belonging to one marketplace. That interoperability also creates a natural need
for portable, verifiable agent authority. AgentGuard can help a counterparty
distinguish an authorized agent action from an overreaching or compromised one.

The current repository is an ONDC-shaped local demonstration, not a live ONDC
network participant. Production participation requires onboarding, registry
subscription, protocol signing and verification, asynchronous Beckn request and
callback handling, conformance, payment and settlement, logistics, and issue
workflows. `ARCHITECTURE.md` owns those requirements.

## User experience

The interface should say what will happen, not expose policy machinery:

1. **Configure authority** — pick allowed actions and auto-approve amounts
   (e.g. refunds up to INR 3,000); confirm the mandate.
2. **Tell the agent the job** — text or voice: "I'm looking for apples" or
   "Handle refunds on this order."
3. **Let it work** — the agent navigates, searches, and updates cart/catalog via
   tools; protected actions show a concise preview when approval is required.
4. **Approve an exception** — approve only this action, edit the mandate, or
   decline.
5. **See and stop** — a timeline explains completed actions; Pause is always
   visible.

Risk, not technical complexity, determines friction. Low-risk routine actions
should feel automatic; unusual counterparty, amount, device, velocity, or
content signals trigger explanation and step-up.

## Demonstration narrative

1. A seller edits and confirms a mandate covering catalog, inventory, order,
   support, and refund boundaries.
2. The seller agent (runtime tools) publishes a demo product with available
   inventory.
3. A buyer edits shopping limits, then speaks or types to the shopping agent;
   the agent searches, navigates, and builds a cart.
4. An in-limit checkout succeeds and creates an Intent Receipt.
5. A higher-value checkout requests exact human approval; replay fails.
6. The order appears in Seller; the seller agent accepts and updates fulfilment.
7. The buyer raises an issue; the seller agent drafts a response and proposes a
   refund.
8. An in-limit refund succeeds; an over-limit refund requires approval.
9. The seller pauses the agent; the next protected action fails immediately.

The payment and ONDC exchange are simulated until real integrations exist. The
authorization, approval consumption, pause, and receipt behavior must be real
and server-enforced.

## Success measures

- A new user confirms a mandate without support in under two minutes.
- At least 90% of test users can explain what the agent may do and when it asks.
- Zero protected writes occur without a current AgentGuard decision.
- Zero successful approval replay or protected action after pause/revocation.
- One Seller item completes the Buyer-to-Seller demo loop without data repair.
- Every protected action has a human-readable, cryptographically verifiable
  receipt with no raw identity, address, cart, or payment evidence.
- Three to five commerce operators validate the problem and one agrees to pilot.

## Explicit non-goals

- Aadhaar-based identity, universal identity, reputation, or trust scoring.
- Blockchain, tokens, wallets, staking, or on-chain commerce state.
- Holding money, replacing UPI, or implementing a payment rail.
- Giving an AI PINs, OTPs, unrestricted payment credentials, or administrator
  access.
- Recording model chain-of-thought or raw customer conversations in receipts.
- Claiming live ONDC publication, NPCI access, or regulatory approval before it
  is independently verified.
- Magically wrapping arbitrary third-party browser agents; external agents are
  trusted only when they call AgentGuard APIs under a confirmed mandate.
- Forced migration off Cursor SDK to OpenAI Agents SDK before the shared tool
  runner is proven.
- FlatWatch, land tokenization, and unrelated portfolio applications.

## Feature admission test

A feature enters the product only if removing it breaks the two-sided commerce
loop, a safety invariant, or a measured adoption outcome. It must be enforced or
tested deterministically, and its privacy and UX cost must be lower than its
benefit. Otherwise delete, defer, or leave it in the host application rather
than AgentGuard.

## Sources

- [NPCI Token Nxt](https://www.npci.org.in/token-nxt)
- [ONDC official developer resources](https://github.com/ONDC-Official)

Build: [`IMPLEMENTATIONPLAN.md`](IMPLEMENTATIONPLAN.md). Verify: [`TESTINGPLAN.md`](TESTINGPLAN.md).
Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md). App outcomes: `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`.
