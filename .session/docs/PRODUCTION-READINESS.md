# Production launch policy

This file defines launch boundaries and stop conditions. It does not own
checklist status. [`../checklist/checklist.json`](../checklist/checklist.json) is the single product-lead
control owner; referenced plans, evidence, portals, and email only support a
deliberate update to that JSON.

Local, FQDN, or PreProd proof never authorizes production ONDC, real customer
money, legal acceptance, or a physical shipment. Historical evidence never
becomes current-source acceptance by implication.

## Generated view

```bash
python3 scripts/generate_checklist.py
python3 scripts/generate_checklist.py --check-current
```

This writes ignored caches only:

- `.session/checklist/state.json`
- `.session/testing/testing-ledger.json`
- `.session/html/checklist.html`

Never edit generated files. Update `.session/checklist/checklist.json`, cite the retained evidence,
then regenerate. Portal and provider observations must include a current readback
before their checklist status changes.

## Launch stop conditions

Stop financial writes when identity, role/resource authorization, AgentGuard,
payment verification, or authoritative order state cannot be established. Never
silently retry a purchase or refund after an unknown provider outcome. Every
launch rehearsal must prove rollback, global agent-write pause, and reconciliation
from immutable identifiers.

## Operator boundaries

The agent may prepare code, drafts, field lists, and read-only verification. The
operator owns legal acceptance, organisation/contact data, portal submissions,
provider selection, spend, secrets, DNS publication, deployment, and production
enablement. A checklist row never grants authority for those actions.

## O1 — Telemetry and response controls (stubs)

Draft only. Names what must be logged, redacted, and alertable on critical paths.
It does **not** approve numeric SLOs, dashboards, paging trees, or a retained
alert drill. Those remain open under checklist **O1**. Runbook fail-closed
actions stay under [O4](#o4--incident-and-financial-unknown-runbooks-stubs);
data-class retention for telemetry stays under [O6](#o6--production-data-class-inventory-draft).

Correlation baseline (stub): every actionable event carries a stable
`request_id` / `trace_id`, session principal id (not wallet body), optional
`mandate_id` + mandate version, and commerce/ONDC ids only when already
authoritative. Do not invent transaction or message ids in logs.

### Must log (stub)

| Signal | Minimum fields (stub) | Owner surface |
| --- | --- | --- |
| AgentGuard denial | Decision outcome `deny`, action name, reason code, principal, agent id, mandate id/version, resource scope summary, `request_id` | Gateway `:43101` authorization path |
| Payment unknown | Checkout/order id, PSP reference if present, prior known state, transition to `unknown`, callback absence or conflict flag, CommerceV1 correlation keys | Payment + commerce ledger |
| ONDC callback backlog | Queue name/topic, oldest age, depth, last successful drain, affected action families (`on_*` / payment), participant FQDN when known | Gateway inbox/outbox / callback workers |

Also retain (stub, not yet SLO-bound): gateway/Buyer/Seller health and error
rate; agent-write allow/deny counts; callback attempt + dedupe outcomes.

### Must redact (stub)

| Class | Never emit in cleartext logs/metrics/traces | Prefer |
| --- | --- | --- |
| Secrets | Signing keys, session tokens, provider API keys, Auth0 secrets | Presence/rotation markers only |
| PII | Phone, email, address, full legal name in free text | Stable opaque principal id; hashed where Architecture requires |
| Payment payloads | Full PAN/instrument, raw PSP bodies, customer-money amounts in unconstrained text | Tokenized PSP ref + coarse status |
| ONDC / model | Raw signed protocol dumps, prompts, chain-of-thought, tool args with PII | Action name, result code, id hashes; signed evidence stays in durable store, not log lines |
| Support export | Unredacted ticket dumps into telemetry backends | O6/O7-approved summaries |

Hashes prove binding; they do not make guessable personal data anonymous.

### Must alert / page (stub)

| Condition | Detect (stub) | Alert class (stub) | Response control link |
| --- | --- | --- | --- |
| AgentGuard denial spike or auth-path outage | Deny rate or auth error budget breach vs baseline; auth dependency down | Page when write path cannot establish authorization; ticket otherwise | Pause autonomous agent writes (O4 service incident) |
| Payment unknown | Order left `unknown` past reconcile window; conflicting PSP vs ledger | Page — financial-unknown | Hold order; no silent capture/refund retry (O4 payment unknown) |
| ONDC / payment callback backlog | Queue age or depth beyond lag SLO placeholder | Page when financial effects would use stale callbacks | Stop dependent financial effects; drain from signed readback only (O4 callback backlog) |

### SLO placeholders (not approved)

| Path | Placeholder intent | Still open |
| --- | --- | --- |
| Gateway auth / AgentGuard | Availability + deny-decision latency | Numeric targets; dashboard; drill |
| Buyer / Seller HTTP | Availability + error budget | Per-env baselines |
| Callbacks | Lag (age/depth) and drain success | Numbers referenced by O4 “lag SLO” |
| Payments | Time-to-authoritative outcome; unknown-state budget | Provider-specific thresholds |
| Agent writes | Allow/deny observability; pause control tested | Global write-pause rehearsal |

No CF3 catalog work, A4 keys/DNS/deploy, or production enablement is implied by
these stubs.

## O4 — Incident and financial-unknown runbooks (stubs)

Draft only. These stubs name detection, fail-closed actions, and recovery
targets. They do **not** assign named on-call trees, phone numbers, or
provider tickets. Escalation contacts and retained exercises remain open under
checklist **O4**.

Shared stop conditions from [Launch stop conditions](#launch-stop-conditions)
and [Operator boundaries](#operator-boundaries) apply to every scenario below.
AgentGuard on `:43101` remains the sole authorization boundary; never silently
retry a purchase or refund after an unknown provider outcome.

| Scenario | Detect (stub) | Fail-closed action (stub) | Recover / close (stub) | Still open |
| --- | --- | --- | --- | --- |
| Service incident | Health, error budget, or deploy regression on gateway / Buyer / Seller | Pause autonomous agent writes; freeze financial writes when auth or order state is unclear | Restore from known-good commit; prove health before re-enabling writes | Named responders; RTO/RPO exercise |
| Payment unknown | PSP callback missing, conflicting, or non-authoritative after checkout | Do not retry capture/refund; hold order in reconciliation; no customer-money assumption | Reconcile from immutable provider + CommerceV1 identifiers once authoritative | PSP contact path; refund-failure twin runbook |
| IGM escalation | Open issue past SLA or buyer/seller dispute needing network path | Keep support lookup read-safe; no secret exposure; no auto-settlement | Follow ONDC IGM path with operator-owned submissions | Staffed IGM ownership; rehearsal evidence |
| Key compromise | Suspected leak of signing, session, or provider credentials | Rotate affected secrets; revoke sessions/mandates; pause agent writes tied to the key | Reconcile modal vs draft keypairs before any portal resubmit; prove `/ondc/on_subscribe` only after operator-approved rotate | Operator-owned rotate/submit; contact tree |
| Callback backlog | ONDC or payment callbacks queued beyond lag SLO | Stop new financial effects that depend on stale callbacks; do not invent identifiers | Drain from signed callback/readback only; derive later IDs from authoritative payloads | Lag SLO numbers ([O1](#o1--telemetry-and-response-controls-stubs)); backlog drill |

Participant-host, DNS, and production-key work stay under the A4 / portal
operator boundary. These stubs never authorize deploy, DNS publish, or live
orders.

## O6 — Production data-class inventory (draft)

Draft only. Not an approved retention/deletion policy. Lawful purpose, access
roles, export, minimization, and enforced controls remain open under checklist
**O6**. Values below are placeholders for operator/privacy review.

| Data class | Examples (draft) | Retention (draft) | Deletion (draft) | Model-visible? (draft) | Notes |
| --- | --- | --- | --- | --- | --- |
| PII / identity | Session principal, contact fields, org profile | TBD — minimize; session vs durable split | TBD — subject request + legal hold | No by default | Session principal owns AgentGuard access; no wallet-body auth |
| Commerce | Orders, line items, mandate versions, receipts | TBD — bind to order/mandate lifecycle | TBD — soft-delete vs purge after hold | No financial payloads to models | Immutable mandate versions retained for audit |
| Payment | PSP refs, amounts, pending/succeeded/failed/unknown | TBD — reconcile window then archive | TBD — never delete sole reconciliation key early | No | Unknown outcome → no silent retry (see O4) |
| ONDC protocol | Signed callbacks, transaction/message IDs, catalog snapshots | TBD — network/audit requirement | TBD — retain signed evidence for dispute window | No raw protocol dumps to models | Derive IDs from signed readback only |
| Support | Tickets, IGM threads, operator notes | TBD — support SLA + legal | TBD — redact PII on export | Summaries only if approved | Safe lookup without secrets (ties to O7) |
| Telemetry | Metrics, traces, redacted logs | TBD — short operational window | TBD — auto-expire | Aggregates only | Redact PII/secrets in logs ([O1](#o1--telemetry-and-response-controls-stubs); Architecture) |
| Model-visible | Prompts, tool args, agent traces allowed into models | TBD — explicit allow-list only | TBD — purge with session/mandate end | Yes only if class allow-listed | Default deny; hashes ≠ plaintext eligibility |

## A6 — Recoverability and operational retention (draft)

Draft only. Not backup certification, not approved RTO/RPO, and not a
privacy/deletion policy. Checklist **A6** stays partial until encrypted backup,
a dated restore exercise, failover, and launch-envelope capacity are proved
with operator-approved recovery objectives. Do **not** invent RTO/RPO hours or
object-retention days here.

**Owners and non-duplication**

| Concern | Owner |
| --- | --- |
| Backup, restore, failover, capacity proofs | This section (checklist **A6**) |
| Data-class lawful purpose, deletion, export, model eligibility | [O6 — Production data-class inventory](#o6--production-data-class-inventory-draft) |
| What must persist at runtime | [`ARCHITECTURE.md` — Storage and integrity](ARCHITECTURE.md#storage-and-integrity) |
| Financial-unknown / incident fail-closed | [O4 stubs](#o4--incident-and-financial-unknown-runbooks-stubs) and [Launch stop conditions](#launch-stop-conditions) |

A6 owns *how* durable state is backed up and restored. O6 owns *whether/how
long* each class may be retained or deleted. Do not copy the O6 inventory into
this section; classify retention policy there, then bind backup jobs to the
approved classes.

### Surfaces in scope (draft)

| Surface | Durable owner today (draft) | Recoverability requirement (draft) | Still open under A6 |
| --- | --- | --- | --- |
| CommerceV1 | Gateway PostgreSQL when `DATABASE_URL` selects CF1 persistence | Restore orders, line items, issues, refunds, reservations, and ledger rows to a consistent state machine; never invent order/payment identifiers after restore | Encrypted backup; dated restore drill |
| AgentGuard | Same PostgreSQL — mandates, decisions, approvals, nonces, receipts | Restored receipts remain independently verifiable; mandate/revocation epochs stay coherent; pause/revoke must not be weaker after restore | Issuer-key backup and rotation path with historical verify |
| ONDC protocol | Inbox/outbox, dedup keys, correlation, leases, dead-letter | Persist-before-ACK and dedup survive restore; drain only from signed callback/readback; do not ACK without a durable row | Replay/drain rehearsal after restore |
| Session / auth | Session principal owns AgentGuard access (not wallet body) | Expired or unrestored sessions must not substitute for AgentGuard decisions; re-auth then re-evaluate | Confirm session-store owner and fail-closed on missing session store |
| Operational objects | Production object store TBD; testing-ledger evidence is not the production store | Once an approved store exists, encrypt at rest and bind retention to O6 classes | Encrypted object retention config and access controls |

Architecture already requires encrypting sensitive data at rest/in transit,
tenant segregation, retention limits, and log redaction. A6 proves those
controls operationally for the launch envelope; it does not redefine them.

### Fail-closed rules (draft)

- Missing encrypted backups, unknown backup freshness, or an unproven restore →
  do not claim durable production hosting; do not enable production financial or
  agent writes on that basis.
- After any restore: prove gateway health, AgentGuard evaluate/consume path, and
  commerce/ONDC consistency **before** re-enabling autonomous agent writes or
  financial mutations.
- Restore never authorizes silent retry of purchase or refund after an unknown
  provider outcome (same stop conditions as O4 / launch policy).
- Placeholder or guessed RTO/RPO values are not targets. Operator must approve
  measurable objectives before A6 can complete.
- Deletion/purge schedules for PII, commerce, payment, ONDC, support, telemetry,
  and model-visible classes remain under **O6**; A6 backup jobs must not retain
  plaintext beyond an approved O6 class rule once that policy exists.

### Required proofs before A6 complete

1. Encrypted backups configured with access controls for the production
   PostgreSQL (and any approved object store).
2. A dated restore exercise succeeds and is retained as evidence.
3. Failover behavior and capacity evidence cover the approved launch envelope.
4. Operator-approved, measurable recovery objectives (RTO/RPO) recorded — not
   drafted placeholders treated as acceptance.

Until those proofs exist, treat recoverability as unproved even though
PostgreSQL is the active persistence owner.
