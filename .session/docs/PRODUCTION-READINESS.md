# Production readiness — launch ops runbooks (checklist owner)

Operator-facing runbooks for checklist items **O1, O2, O4, A5, A6, A7, A8, B7**. No GSTIN,
portal Submit, DNS, registry, Auth0 tenant cutover, or live PSP signup required to
prepare or exercise these locally.

| Checklist | Section |
| --- | --- |
| O1 | [§ O1 — Telemetry, SLOs, alerting](#o1--telemetry-slos-alerting) |
| O4 | [§ O4 — Incident runbooks](#o4--incident-runbooks) |
| O2 / A6 | [§ A6 / O2 — Backup and restore](#a6--o2--backup-and-restore) |
| A5 | [§ A5 — Auth0 MFA + Attack Protection (no cutover)](#a5--auth0-mfa--attack-protection-no-cutover) |
| A7 | [§ A7 — Razorpay Test Mode secrets](#a7--razorpay-test-mode-secrets) |
| A8 | [§ A8 — Agreement and contacts template](#a8--agreement-contacts-and-disclosures-template) |
| B7 | [§ B7 — PreProd observability log submit](#b7--preprod-observability-log-submit) |

Legacy demo onboarding ladder remains in repo-root [`PRODUCTION-READINESS.md`](../../PRODUCTION-READINESS.md).

---

## Role placeholders (operator fills before go-live)

| Role | Placeholder name | Email | Phone / paging | Backup |
| --- | --- | --- | --- | --- |
| **Incident commander (IC)** | `{IC_NAME}` | `{IC_EMAIL}` | `{IC_PHONE}` | `{IC_BACKUP}` |
| **ONDC engineering on-call** | `{ONDC_ENG_NAME}` | `{ONDC_ENG_EMAIL}` | `{ONDC_ENG_PHONE}` | `{ONDC_ENG_BACKUP}` |
| **AgentGuard / gateway on-call** | `{AG_ENG_NAME}` | `{AG_ENG_EMAIL}` | `{AG_ENG_PHONE}` | `{AG_ENG_BACKUP}` |
| **Finance / payment unknown** | `{FIN_OPS_NAME}` | `{FIN_OPS_EMAIL}` | `{FIN_OPS_PHONE}` | `{FIN_OPS_BACKUP}` |
| **Support / IGM lead** | `{SUPPORT_NAME}` | `{SUPPORT_EMAIL}` | `{SUPPORT_PHONE}` | `{SUPPORT_BACKUP}` |
| **Security / key compromise** | `{SEC_NAME}` | `{SEC_EMAIL}` | `{SEC_PHONE}` | `{SEC_BACKUP}` |
| **Product / legal (A8)** | `{LEGAL_NAME}` | `{LEGAL_EMAIL}` | `{LEGAL_PHONE}` | — |

Paging route placeholder: `{PAGER_SERVICE}` (e.g. PagerDuty / Opsgenie service id).

---

## O1 — Telemetry, SLOs, alerting

**Owner:** Operations lead · **Scope:** gateway (`:43101`), Buyer/Seller FQDNs, ONDC callbacks, simulated/live payment adapter, AgentGuard writes.

### SLO placeholders (operator replaces before approval)

| Surface | SLI (placeholder) | Target (placeholder) | Error budget window |
| --- | --- | --- | --- |
| Gateway health | `GET /health` 2xx | `{SLO_GATEWAY_AVAIL}` e.g. 99.9% | 30d |
| Buyer checkout evaluate | `POST /api/agentguard/actions/evaluate` p95 | `{SLO_AG_EVAL_P95}` e.g. 800ms | 7d |
| ONDC callback ingest | signed `on_*` ACK latency p95 | `{SLO_ONDC_CALLBACK_P95}` e.g. 2s | 7d |
| Callback backlog | unprocessed `ondc_inbox` age | `{SLO_CALLBACK_BACKLOG_MAX}` e.g. 15m | 1d |
| Payment unknown queue | attempts in `unknown` > `{PAYMENT_UNKNOWN_MAX_AGE}` | 0 open > SLA | 1d |
| Agent write denials (unexpected) | deny rate without `reason_code` in allow-list | `{SLO_AG_DENY_SPIKE}` | 1d |

### Must-log (every production environment)

Correlate with **`request_id`** (or trace id) across gateway ↔ commerce ↔ ONDC.

| Event class | Required fields | Emit from |
| --- | --- | --- |
| **HTTP request** | `timestamp`, `request_id`, `method`, `path`, `status`, `duration_ms`, `principal_id` (hashed if logged), `subscriber_id` (ONDC routes) | Gateway access middleware |
| **AgentGuard decision** | `request_id`, `principal_id`, `agent_id`, `action`, `decision`, `reason_code`, `risk_level`, `mandate_id`, `approval_id` | `/api/agentguard/actions/evaluate` |
| **AgentGuard denial** | above + `policy_rule`, `limits_snapshot` | evaluate → deny / need_approval |
| **Approval consume / execute** | `approval_id`, `idempotency_key`, `outcome`, `receipt_id` | approvals + execute |
| **Pause / resume / revoke** | `agent_id`, `actor_principal`, `previous_status`, `new_status` | agent lifecycle routes |
| **Payment attempt** | `commerce_order_id`, `payment_attempt_id`, `provider`, `status`, `idempotency_key`, `amount_paise` | payment adapter |
| **Payment unknown** | `payment_attempt_id`, `provider_ref`, `last_provider_status`, `recovery_state` | webhook + reconciliation job |
| **ONDC outbox send** | `message_id`, `action`, `transaction_id`, `subscriber_id`, `signature_key_id` | outbox dispatch |
| **ONDC inbox receive** | `message_id`, `action`, `transaction_id`, `signature_verified`, `processing_outcome` | `/ondc/on_*` |
| **Callback backlog** | `inbox_unprocessed_count`, `oldest_unprocessed_age_s`, `outbox_retry_count` | periodic metric + threshold breach |
| **IGM state change** | `issue_id`, `order_id`, `from_status`, `to_status`, `owner` | commerce issue routes |

### Must-redact (never log raw)

| Class | Rule |
| --- | --- |
| Session / cookies | Log cookie **names** only; never `aadharcha_session` value |
| Auth0 tokens | Never log access/id/refresh tokens or Auth0 client secret |
| ONDC signing keys | Log `unique_key_id` / fingerprint only; never PEM or private key material |
| Payment PAN/UPI/full instrument | Provider tokens masked; last-4 only if provider returns it |
| PII | No full phone, email, address in info-level logs; use hashed principal or order id |
| Agent prompts / voice audio | Not in production app logs unless explicit debug flag + retention class O6 |
| Portal modal key downloads | Never log JSON key files from Raise Request |

### Must-alert (page IC + domain on-call)

| Alert | Trigger (placeholder threshold) | Primary owner | Runbook |
| --- | --- | --- | --- |
| **Gateway down** | `/health` non-2xx `{ALERT_GATEWAY_DOWN_MIN}` consecutive checks | `{AG_ENG_NAME}` | [O4-1 Service down](#o4-1-service-down) |
| **AgentGuard deny spike** | deny rate > `{ALERT_AG_DENY_RATE}` without deploy correlation | `{AG_ENG_NAME}` | [O4-1](#o4-1-service-down) + evaluate logs |
| **Payment unknown** | any attempt `unknown` > `{PAYMENT_UNKNOWN_MAX_AGE}` OR reconciliation gap | `{FIN_OPS_NAME}` | [O4-2 Payment unknown](#o4-2-payment-unknown) |
| **ONDC callback backlog** | `ondc_inbox` unprocessed > `{SLO_CALLBACK_BACKLOG_MAX}` OR oldest > threshold | `{ONDC_ENG_NAME}` | [O4-5 Callback backlog](#o4-5-ondc-callback-backlog) |
| **IGM SLA breach** | open issue past `{IGM_RESPONSE_SLA}` without owner action | `{SUPPORT_NAME}` | [O4-3 IGM escalate](#o4-3-igm-escalation) |
| **Key compromise signal** | invalid signature spike + key id mismatch OR operator report | `{SEC_NAME}` | [O4-4 Key compromise](#o4-4-signing-key-compromise) |
| **Refund failure** | refund ledger stuck / provider reject | `{FIN_OPS_NAME}` | [O4-6 Refund failure](#o4-6-refund-failure) |
| **Participant timeout** | expected `on_*` missing > `{PARTICIPANT_TIMEOUT}` | `{ONDC_ENG_NAME}` | [O4-7 Participant timeout](#o4-7-participant-timeout) |

### O1 drill checkbox (operator retains evidence)

- [ ] Trigger test alert on `{PAGER_SERVICE}` for **AgentGuard deny spike** (staging).
- [ ] IC acknowledges within `{DRILL_ACK_TARGET}` (placeholder).
- [ ] On-call finds correlated `request_id` in logs and links to runbook section.
- [ ] Post-drill: file evidence under `.session/evidence/o1-alert-drill-YYYYMMDD.json`.

---

## O4 — Incident runbooks

Each runbook: **Detect → Triage → Contain → Recover → Communicate → Post-incident**.  
Financial writes stop when state is unknown (see root PRODUCTION-READINESS launch stop conditions).

### O4-1 Service down

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | `{PAGER_SERVICE}` gateway/Buyer/Seller probe failed | IC |
| 2 Triage | Check Render/Vercel status, recent deploy, `:43101/health`, DB connectivity | `{AG_ENG_NAME}` |
| 3 Contain | If bad deploy: rollback to last known good (operator approval). Enable read-only banner if partial. | IC + `{AG_ENG_NAME}` |
| 4 Recover | Restore service; verify Auth0 session + one read-only Buyer/Seller path | `{AG_ENG_NAME}` |
| 5 Communicate | Status note to `{SUPPORT_NAME}`; no customer PII in public channel | IC |
| 6 Post | Timeline + root cause in `.session/evidence/incident-YYYYMMDD.json` | IC |

**Agent verification (after recovery, local or staging):**

```bash
curl -sf http://127.0.0.1:43101/health
./scripts/verify-portfolio.sh
```

### O4-2 Payment unknown

**Stop:** no new captures/refunds on affected orders until outcome resolved.

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | Alert **Payment unknown** or finance report | `{FIN_OPS_NAME}` |
| 2 Triage | Lookup `commerce_payment_attempts` + provider dashboard by `idempotency_key` / provider ref | `{FIN_OPS_NAME}` |
| 3 Contain | Mark order payment state `unknown`; block duplicate capture | `{AG_ENG_NAME}` |
| 4 Recover | Provider poll/webhook replay; reconcile ledger; signed receipt if write resumed | `{FIN_OPS_NAME}` + `{AG_ENG_NAME}` |
| 5 Communicate | Customer-facing copy via `{SUPPORT_NAME}` — pending, not failed silently | `{SUPPORT_NAME}` |
| 6 Post | Reconciliation note attached to order audit | `{FIN_OPS_NAME}` |

### O4-3 IGM escalation

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | SLA timer or customer escalation | `{SUPPORT_NAME}` |
| 2 Triage | Buyer/Seller issue id, `protocol_order_id`, audit timeline | `{SUPPORT_NAME}` |
| 3 Contain | Assign owner + response target in commerce issue record | `{SUPPORT_NAME}` |
| 4 Recover | Signed `on_issue` / `on_issue_status` if network path; else internal remedy + receipt | `{ONDC_ENG_NAME}` |
| 5 Escalate | Policy escalation contact `{A8_POLICY_ESCALATION}` if unresolved > `{IGM_ESCALATION_SLA}` | IC |
| 6 Post | Closed issue + AgentGuard outcome receipt retained | `{SUPPORT_NAME}` |

### O4-4 Signing key compromise

**Stop:** rotate keys; do not Submit new registry material without operator authorization (A4 boundary).

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | Signature verify failures, leaked PEM report, unauthorized portal access | `{SEC_NAME}` |
| 2 Triage | Identify affected `unique_key_id` / role (Buyer, Seller, LBNP, gateway) | `{SEC_NAME}` + `{ONDC_ENG_NAME}` |
| 3 Contain | Disable outbound ONDC signing for affected role; pause agent writes if AG keys implicated | IC |
| 4 Recover | Generate replacement keys per `~/.agents/skills/ondc`; operator portal Raise Request; re-prove `/ondc/on_subscribe` before traffic | `{ONDC_ENG_NAME}` |
| 5 Communicate | Notify ONDC ops contact `{ONDC_OPS_CONTACT}` if network-facing | IC |
| 6 Post | Rotation log + fingerprint evidence; no secrets in repo | `{SEC_NAME}` |

### O4-5 ONDC callback backlog

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | **Callback backlog** alert; rising `ondc_inbox` unprocessed count | `{ONDC_ENG_NAME}` |
| 2 Triage | Oldest message age, error class (signature, schema, commerce bind) | `{ONDC_ENG_NAME}` |
| 3 Contain | Scale gateway workers if infra-limited; rate-limit junk unsigned POSTs (already 401) | `{AG_ENG_NAME}` |
| 4 Recover | Replay failed inbox after fix; verify CommerceV1 bind + ledger balance | `{ONDC_ENG_NAME}` |
| 5 Communicate | If order state stale for customers, `{SUPPORT_NAME}` uses order id lookup | `{SUPPORT_NAME}` |
| 6 Post | Count of replayed messages + max lag | `{ONDC_ENG_NAME}` |

**Agent verification:**

```bash
# Local gateway — inbox depth (requires psql + local DATABASE_URL)
psql "$DATABASE_URL" -c "SELECT count(*) AS unprocessed FROM ondc_inbox WHERE processed_at IS NULL;"
```

### O4-6 Refund failure

Twin of payment unknown for outbound money.

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | Refund stuck `refund_pending` / provider error | `{FIN_OPS_NAME}` |
| 2 Triage | `commerce_refunds` + AgentGuard receipt for original auth | `{FIN_OPS_NAME}` |
| 3 Contain | No duplicate refund; Seller UI shows exception state | `{AG_ENG_NAME}` |
| 4 Recover | Retry with new idempotency key or manual provider completion | `{FIN_OPS_NAME}` |
| 5 Post | Ledger balanced; issue closed if IGM linked | `{FIN_OPS_NAME}` |

### O4-7 Participant timeout

| Step | Action | Owner |
| --- | --- | --- |
| 1 Detect | Expected `on_confirm` / `on_status` / `on_track` missing > `{PARTICIPANT_TIMEOUT}` | `{ONDC_ENG_NAME}` |
| 2 Triage | Outbox message_id, transaction_id, counterparty subscriber_id | `{ONDC_ENG_NAME}` |
| 3 Contain | Do not duplicate confirm; hold order in explicit pending state | `{AG_ENG_NAME}` |
| 4 Recover | `issue` / cancel per protocol if terminal; or manual reconciliation with network ops | `{ONDC_ENG_NAME}` |
| 5 Post | Record whether timeout was BAP, BPP, or LSP | `{ONDC_ENG_NAME}` |

### O4 drill checkbox (operator)

- [ ] Tabletop **O4-2 Payment unknown** with `{FIN_OPS_NAME}` + `{AG_ENG_NAME}`.
- [ ] Tabletop **O4-5 Callback backlog** with sample inbox rows (redacted).
- [ ] Tabletop **O4-4 Key compromise** — confirm no agent copies PEM to git/Slack.
- [ ] Retain `.session/evidence/o4-incident-drill-YYYYMMDD.json` with participants and timings.

---

## A6 / O2 — Backup and restore

**Owner:** Operations lead · **Production:** encrypted backups + provider retention (operator).  
**Agent-owned local proof:** `scripts/local_postgres_backup_restore.sh` (refuses non-local hosts).

### Recoverability draft (no invented RTO/RPO)

| Asset | Owner store | Backup method (production — operator) | Local exercise |
| --- | --- | --- | --- |
| PostgreSQL (AgentGuard, CommerceV1, ONDC inbox/outbox) | Render Postgres / approved host | Provider encrypted backup + `{RETENTION_DAYS}` | `backup` + `verify-restore` subcommands |
| Object storage (if added) | `{OBJECT_STORE}` | Versioned bucket lifecycle per O6 class | N/A until provisioned |
| Secrets | Render/Vercel/Auth0 dashboards | Not in git; rotation runbook O4-4 | N/A |

Operator-approved targets (fill before go-live): **RTO** `{RTO_PLACEHOLDER}`, **RPO** `{RPO_PLACEHOLDER}`.

### Local backup / restore procedure

```bash
# Requires local Postgres only (127.0.0.1 / localhost / ::1)
export DATABASE_URL='postgresql://USER@127.0.0.1:5432/postgres'

# 1. Backup
./scripts/local_postgres_backup_restore.sh backup

# 2. Restore into isolated DB + integrity checks (does not overwrite source)
./scripts/local_postgres_backup_restore.sh verify-restore

# 3. Fill evidence template
#    .session/evidence/local-postgres-backup-restore-template.json
```

**Integrity checks (verify-restore):** row counts for `agentguard_mandate_versions`, `commerce_orders`, `commerce_ledger_entries`, `ondc_inbox`, `agentguard_receipts`.

### A6 operator remaining

- [ ] Approve RTO/RPO numbers (replace placeholders).
- [ ] Configure encrypted production backups on Render/Neon per O6 retention.
- [ ] Run production restore drill in isolated instance (not local script scope).
- [ ] Failover + capacity evidence for launch envelope.

---

## A8 — Agreement, contacts, and disclosures template

**Operator completes and legal approves before portal Submit.** Do not accept NP Agreement or publish production disclosures without explicit authorization.

### Organisation (from portal readback — verify current)

| Field | Value / placeholder |
| --- | --- |
| Organisation ID | `15462` |
| Legal name | `GURUSHARAN GUPTA HUF` |
| GSTIN | `{GSTIN}` — **empty blocks A4 Submit** |
| Profiles in scope (A2) | Retail Buyer NP, Retail Seller NP-ISN, Logistics Buyer NP |

### Network Participant Agreement

| Item | Status | Operator action |
| --- | --- | --- |
| NP Agreement reviewed | [ ] | `{LEGAL_NAME}` reviews current portal PDF/terms |
| Business / compliance signatory | `{SIGNATORY_NAME}` | |
| Accept in portal | **Unauthorized until operator says Submit** | |

### Operational contacts (portal + public disclosures)

| Contact type | Name | Email | Phone | Hours |
| --- | --- | --- | --- | --- |
| Order status / tracking | `{ORDER_STATUS_CONTACT}` | `{ORDER_STATUS_EMAIL}` | `{ORDER_STATUS_PHONE}` | `{HOURS}` |
| Reconciliation / settlement | `{RECON_CONTACT}` | `{RECON_EMAIL}` | `{RECON_PHONE}` | |
| Payout / finance | `{PAYOUT_CONTACT}` | `{PAYOUT_EMAIL}` | `{PAYOUT_PHONE}` | |
| Grievance (NP) | `{GRIEVANCE_CONTACT}` | `{GRIEVANCE_EMAIL}` | `{GRIEVANCE_PHONE}` | |
| Customer grievance (Buyer-facing) | `{CUST_GRIEVANCE_CONTACT}` | `{CUST_GRIEVANCE_EMAIL}` | `{CUST_GRIEVANCE_PHONE}` | |
| Policy escalation | `{A8_POLICY_ESCALATION}` | `{POLICY_ESC_EMAIL}` | `{POLICY_ESC_PHONE}` | |
| ONDC ops liaison | `{ONDC_OPS_CONTACT}` | `{ONDC_OPS_EMAIL}` | | |

### Retail Buyer disclosures (publish URLs when approved)

| Disclosure | Draft URL / path | Approved [ ] |
| --- | --- | --- |
| Static terms of use | `{BUYER_TERMS_URL}` | |
| Privacy policy | `{BUYER_PRIVACY_URL}` | |
| Refund and return policy | `{BUYER_REFUND_URL}` | |
| Support / contact | `{BUYER_SUPPORT_URL}` | |
| Search ranking / sorting explanation | `{BUYER_SORTING_URL}` | |
| Production go-live notice | `{BUYER_GOLIVE_URL}` | |

### Start-transacting checklist (portal — operator only)

- [ ] All contacts above filled and match portal form fields.
- [ ] Disclosures live on Buyer FQDN and match portal submission.
- [ ] Reconciliation/settlement contacts match B6 owner when PSP selected (A7).
- [ ] **Submit not clicked** until A4 GSTIN/registry authorized separately.

---

## B7 — PreProd observability log submit

**Owner:** ONDC operations · **Operator:** key generation + external submit.  
**Agent:** capture, redact, validate, verification commands.

### Prerequisites

- Conformance source fingerprint recorded (commit / deploy id).
- Redaction rules: [O1 must-redact](#must-redact-never-log-raw).
- Procedure depth: `~/.agents/skills/ondc` Lifecycle + Sources.

### Operator portal steps

1. Sign in to [ONDC portal](https://portal.ondc.org) as organisation `15462`.
2. Navigate to **PreProd observability** / **log submission keys** (exact menu label may change).
3. **Generate** submission key pair — operator only; store private key in `{SECRET_STORE}`, not git.
4. Note `{B7_KEY_ID}` and creation date in portal UI.
5. After agent validation passes, **submit** redacted log bundle to ONDC-Official/verification-logs or portal-upload path ONDC currently names.
6. Retain official validation report PDF/JSON; link in checklist B7 evidence.

### Agent capture and validation (after operator key exists)

```bash
# 1. Export redacted protocol logs for exact conformance run (paths vary by capture setup)
#    Must exclude PEM, cookies, full PII — see O1 must-redact.

# 2. Clone validation utility (operator machine or CI sandbox)
git clone https://github.com/ONDC-Official/log-validation-utility.git
cd log-validation-utility
npm install

# 3. Validate (example — adjust config to ONDC doc for your role/version)
npm run validate -- --input /path/to/redacted/logs --domain RET10 --version 1.2.0

# 4. Record exit code + report path in evidence JSON
```

### Agent verification after operator submit

- [ ] Official report retained at `.session/evidence/b7-ondc-log-validation-YYYYMMDD.json`.
- [ ] Every reported defect closed or explicitly accepted by `{ONDC_ENG_NAME}`.
- [ ] Do **not** treat Workbench scenario green as B7 complete.

### B7 checkbox

- [ ] Operator generated PreProd observability key (`{B7_KEY_ID}`).
- [ ] Agent captured redacted logs for frozen source.
- [ ] log-validation-utility passed locally.
- [ ] Operator submitted to ONDC; report archived.

---

## A5 — Auth0 MFA + Attack Protection (no cutover)

**Owner:** Operator · **Constraint:** keep existing staging/FQDN Auth0 tenant. Do **not** create a new production tenant or switch connections until `A5-20260817-03` is lifted.

### Dashboard steps (existing tenant)

1. Auth0 Dashboard → **Security → Multi-factor Auth** → enable MFA for the app used by Buyer/Seller (prefer Adaptive or Always for Seller elevated actions).
2. **Security → Attack Protection** → enable Brute-force, Suspicious IP throttling, Breached password detection.
3. Confirm callback/logout URLs still match `gateway.aadharcha.in` / local `43101` allowlist (authentication skill).
4. Smoke: Buyer Google login + Seller pause still work; Seller elevated write without MFA still fail-closes on gateway.

### Checkbox

- [ ] MFA enabled on current tenant (`{AUTH0_TENANT}`)
- [ ] Attack Protection toggles on
- [ ] Buyer + Seller smoke after MFA
- [ ] Explicit written approval before any tenant/connection cutover

---

## A7 — Razorpay Test Mode secrets

**Owner:** Operator · **Code:** already fail-closes live `rzp_live_*` keys; suite green locally 2026-09-13.

1. Razorpay Dashboard → Test Mode → copy `rzp_test_` key id + secret (never commit).
2. Set on Render gateway (`identity-aadhar-gateway-main`): `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`.
3. Configure webhook to gateway `/api/.../razorpay/webhook` (exact path in gateway skill/routes).
4. One Test Mode checkout on FQDN; archive payment id in evidence (no live settlement claim).

### Checkbox

- [ ] `rzp_test_*` set on Render (not live)
- [ ] Webhook verified in Test Mode
- [ ] One FQDN Test Mode payment evidence retained
- [ ] Production PSP selection deferred until commercial approval

---

## Cross-links

| Item | Doc |
| --- | --- |
| C3 AgentGuard authority | [`.cursor/skills/agent-runtime-design/references/production-authority.md`](../../.cursor/skills/agent-runtime-design/references/production-authority.md) |
| O6 data classes | § O6 in checklist + privacy inventory (operator) |
| A4 registry / keys | `AGENTS.md` participant-host gate; A4 checklist item |
| Testing evidence | [`.agents/skills/testing-ledger/SKILL.md`](../../.agents/skills/testing-ledger/SKILL.md) |
