# Production readiness — ops after the local AgentGuard demo

Owner path for **external pilot / production ops** (hosting, KYC rails, ONDC portal,
payments). Not the Token Nxt demo build plan.

| Concern | Owner |
| --- | --- |
| Product / demo narrative | [`PRODUCTIDEA.md`](PRODUCTIDEA.md) |
| Local demo build | [`IMPLEMENTATIONPLAN.md`](IMPLEMENTATIONPLAN.md) milestones 0–7; agent-as-executor M10–12 |
| Demo / PreProd / ONDC test gates | [`TESTINGPLAN.md`](TESTINGPLAN.md) |
| Shared architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |

**Token Nxt PreProd demo:** AgentGuard across **ONDC Buyer + ONDC Seller** (two-sided
commerce loop). Not reputation, credit, land, FlatWatch, or claimed live UAP/ONDC.

Host identity (AadhaarChain SSO / Setu / fixtures) is an **optional adapter**, not
the product hierarchy. AgentGuard principals must become identity-neutral
(IMPLEMENTATIONPLAN Milestone 1).

## Locked recommendation (2026-07-11)

| Rail | Choice | Why |
| --- | --- | --- |
| Local / FQDN PreProd | IMPLEMENTATIONPLAN 0–7 + TESTINGPLAN demo gate + `W-*` | Token Nxt proof on Auth0 + PreProd network |
| KYC (optional host assurance) | Local demo + Setu.co sandbox | Non-blocking for AgentGuard demo; use when replacing fixtures |
| KYC (gov production) | MeitY API Setu / DigiLocker | **Paused** — resume only for production identity |
| Live ONDC | Milestone 9 + TESTINGPLAN Layer 8 | After portal/keys; never required for local demo complete |
| UCP / payments | After real order lifecycle + regulated PSP | No fake NPCI claims |

**Operator decision (2026-07-11):** pause GST Part B + MeitY partner signup; stay local;
pursue **Setu.co sandbox** only as optional KYC. Do not block AgentGuard milestones on GST/MeitY/ONDC portal.

GST TRN `272600333290TRN` kept only if MeitY resumes (Part B due 26/07/2026) — do not block on it.

### Active path — Setu.co sandbox

**Status (2026-07-11):** Bridge login OK. KYC merchant **AadhaarChain** created. DigiLocker test product instance created.

| Item | Value |
| --- | --- |
| Bridge org root | `d07c2bfc-fa07-4f9d-8cbc-8db9e827779d` |
| KYC merchant id | `b22bc0ea-966d-4156-bea5-8962d7b6c093` |
| DigiLocker product instance (`x-product-instance-id`) | `3c0e3c28-164f-4fb7-9c98-fcb4ccc5011e` |
| Test Client IDs | visible in Bridge (two TEST keys) |
| Client secrets | UI shows **API Keys not available** — operator must reveal/copy or ask Setu support |
| Org KYC / go-live | optional for sandbox test; **Resume KYC** only for production |

**Note:** Bridge “KYC → DigiLocker” is Setu’s document/Aadhaar path. Gateway `setu_ekyc.py` targets hosted eKYC (`dg-sandbox.setu.co` `/api/ekyc/`). If secrets appear, wire DigiLocker headers first; adapt client if eKYC endpoints differ from DigiLocker docs.

1. In Bridge product page: copy **Client secret** when available (click reveal/copy).  
2. Paste into `aadharchain/gateway/.env`:

```bash
SETU_EKYC_ENABLED=true
SETU_EKYC_BASE_URL=https://dg-sandbox.setu.co
SETU_EKYC_CLIENT_ID=<test client id>
SETU_EKYC_CLIENT_SECRET=<test client secret>
SETU_EKYC_PRODUCT_INSTANCE_ID=3c0e3c28-164f-4fb7-9c98-fcb4ccc5011e
PUBLIC_GATEWAY_URL=<tunnel to :43101 if webhooks needed>
PUBLIC_WEB_URL=http://127.0.0.1:43100
```

3. Restart stack; if `/api/ekyc/` rejects DigiLocker product, switch client to DigiLocker API docs from Bridge “API docs” link.  
4. Local without secrets: demo upload still works.

Docs: https://docs.setu.co/data/ekyc/quickstart — support: `support@setu.co` if secrets stay unavailable.

**Agent skill for MeitY (paused):** `.cursor/skills/apisetu-partner-onboarding/`  
**Gateway Setu client:** already env-gated (`SETU_EKYC_*`).

## Solflare / wallet note

- **Burner SSO:** fully automated (local only).
- **Solflare / Phantom approve:** runs in *your* browser extension. Agents have no separate production wallet that can approve on your machine. For unattended local proof use burner; for real-wallet validation you click Approve once (or leave Solflare unlocked + known test wallet).

## Goal

**Product hierarchy:** **AgentGuard** → demonstrated on **ONDC Buyer + ONDC Seller**.
Gateway lives in `aadharchain/` as a legacy host. FlatWatch deferred. Aadhaar / wallet
SSO / Setu are replaceable host-assurance adapters — not the submission thesis.

| Owner | Path |
| --- | --- |
| Product thesis | [`PRODUCTIDEA.md`](PRODUCTIDEA.md) |
| Demo build / verification | [`IMPLEMENTATIONPLAN.md`](IMPLEMENTATIONPLAN.md), [`TESTINGPLAN.md`](TESTINGPLAN.md) |
| AadhaarChain (legacy host) | [`aadharchain/GOAL.md`](aadharchain/GOAL.md) |
| ONDC Seller | [`ondcseller/GOAL.md`](ondcseller/GOAL.md) |
| ONDC Buyer | [`ondcbuyer/GOAL.md`](ondcbuyer/GOAL.md) |
| FlatWatch | [`flatwatch/GOAL.md`](flatwatch/GOAL.md) |

### Goal map (local demo vs production later)

| Surface | Local demo (Token Nxt) | Production / pilot later |
| --- | --- | --- |
| **AgentGuard** (`:43101`) | Milestones 0–7: identity-neutral principals, mandates, shared exchange, signed receipts, two-sided browser proof | Durable DB, multi-tenant, pen test — TESTINGPLAN production security gate |
| **ONDC Buyer / Seller** | Real partial PreProd Beckn BAP/BPP + shared exchange + AgentGuard journeys; signed Seller discovery visibly proven | Official conformance, full lifecycle and production network after Milestone 9 |
| **Host identity / SSO** | Auth0/demo session principal adapter; AgentGuard rejects wallet override | Live KYC only if a customer requires that rail |
| **Setu.co sandbox** | Optional non-fixture KYC | Live keys + Bridge org KYC |
| **MeitY / GST / ONDC portal / UCP** | **Not required** for demo complete | Only when choosing that rail |

**Current interim elevated gates:** some demo writes still check verified trust + purpose proof-tokens. Milestone 4 makes AgentGuard the sole authorization owner.

**Do not block** IMPLEMENTATIONPLAN 0–7 on GST, MeitY, Bridge go-live, or ONDC portal signup.

---

## A. Access / registration (human + agent)

| # | Item | Who | Status | Link / action |
| --- | --- | --- | --- | --- |
| A1 | KYC rail (optional host assurance) | Locked optional | **Setu.co sandbox + local demo** — not required for AgentGuard milestones 0–7 | Bridge signup + `SETU_EKYC_*` |
| A2 | MeitY API Setu partner signup | Paused | **paused** | https://partners.apisetu.gov.in/signup — resume later |
| A3 | Org docs + MeitY approval | Paused | **paused** | |
| A3b | **GSTIN (HUF)** | Paused | **Part A done only** — TRN `272600333290TRN`; Part B optional by 26/07/2026 | Do not block sandbox on GST |
| A4 | Subscribe Aadhaar / DigiLocker APIs | You + API provider approve | after A3 | Client ID / secret issued |
| A5 | ONDC Participant Portal account | You | **STOP — signup** | https://portal.ondc.org — complete profile 100% |
| A6 | ONDC subscriber_id whitelist | You request; ONDC approves | after A5 | FQDN + SSL |
| A7 | Production domain + TLS | You / infra | **Buyer/Seller FQDNs live** | `ondcbuyer.aadharcha.in`, `ondcseller.aadharcha.in` (Vercel); gateway still Render |
| A8 | ONDC signing + encryption keypairs | Agent generates; you store secrets | after A7 | `python3 scripts/ondc_generate_keys.py` |
| A8b | **Auth0 tenant (production IdP)** | You | **code ready — HARD STOP on creds** | Dashboard URLs + deploy checklist: `.cursor/skills/authentication/SKILL.md`; paste `AUTH0_DOMAIN` / `CLIENT_ID` / `CLIENT_SECRET` into gateway `.env` + Render |
| A9 | UCP capability profile | Agent later | after ONDC client | https://ucp.dev |
| A10 | Payments (UPI / PSP) | You | stub routes ready | `POST /api/commerce-integrations/payments/intents` (requires AG receipt) |
| A11 | Hosting non-ephemeral state | Agent can blueprint | pending | Postgres + object storage |

### Operator values (fill after portal — never commit secrets)

| Field | Staging | Production |
| --- | --- | --- |
| Auth0 domain | | |
| Auth0 client id | | |
| ONDC subscriber_id | | |
| BAP URI / callback host | | |
| Buyer app origin | | |
| Seller app origin | | |
| Gateway public URL | | |
| Signing unique_key_id | | |

Gateway ONDC adapter: `GET /api/ondc/status`, `POST /api/ondc/search|confirm`, `POST /api/ondc/callback/{action}`.
Flip commerce demo off only via `python3 scripts/commerce_demo_mode_gate.py --allow-with-evidence <file>`.

### STOP checklist — MeitY API Setu (paused — do not drive unless resumed)

Portal: https://www.apisetu.gov.in/  
Partner signup: https://partners.apisetu.gov.in/signup  
SOP: https://cdn.apisetu.gov.in/portal/assets/SOP-APISETU.pdf  
Support: `apisetu.support@digitalindia.gov.in` / DigiLocker partners `partners@digitalindia.gov.in`

**How signup works (when resumed; agent cannot finish alone):**

1. Click **Sign Up Via** → authenticates with **DigiLocker MeriPehchaan** (your phone OTP / DigiLocker login).
2. Register as **API consumer** with a **domain email** (one request per org).
3. Upload (PDF):
   - Proof of Identity
   - Authority Letter
   - Organization PAN
   - GST registration certificate
   - Certificate of Incorporation
4. Write a **valid use case** (draft below — paste/edit on form).
5. Wait for API Management approval → subscribe DigiLocker / Aadhaar APIs → receive **client_id / client_secret**.

**Reply with (minimum to continue):**

| Field | Your value |
| --- | --- |
| Domain email | **`gurusharan.gupta@aadharcha.in`** (GoDaddy; see skill `references/godaddy.md`) |
| Legal org name | |
| MeriPehchaan / DigiLocker ready? | yes/no (you must complete OTP) |
| Org docs available? | list which of the 5 PDFs you have |

**Use-case draft (edit freely):**

> AgentGuard authorizes agentic commerce on ONDC Buyer and Seller for Indian users. We request DigiLocker requester access only if an optional host-assurance KYC rail is required beyond Auth0 session identity. We store only masked fields + verification decision off-chain. Callback / redirect URI: `https://aadharcha.in` (and local gateway callbacks for sandbox if allowed).

After approval + credentials, paste into `aadharchain/gateway/.env` (never commit):

```bash
APISETU_ENABLED=true
APISETU_CLIENT_ID=
APISETU_CLIENT_SECRET=
APISETU_REDIRECT_URI=https://aadharcha.in/verify
# DigiLocker OAuth endpoints from partner docs after approval
```

**Agent continues:** DigiLocker OAuth client in gateway → replace demo verify UI → wire trust completion.

---

## B. Trust substrate (AadhaarChain)

| # | Item | Status |
| --- | --- | --- |
| B1 | Local identity + trust API + burner SSO | **done** |
| B2 | Setu.co eKYC sandbox (env-gated) | **code done** — blocked on Bridge credentials |
| B2b | MeitY DigiLocker / API Setu live verify | **paused** |
| B3 | Consent, retention, audit logs (Aadhaar Act / DPDP) | pending legal + product |
| B4 | Gateway on-chain writes (`SOLANA_ON_CHAIN_ENABLED`) | flagged; optional for v1 commerce |
| B5 | Production secrets (oracle key, session secrets, CORS) | pending env |
| B6 | Rate limits, abuse, webhook auth for KYC callbacks | rate limit done; webhook auth pending |
| B7 | Solflare/Phantom production SSO validation | needs your Approve once |

---

## C. Real ONDC commerce

| # | Item | Status |
| --- | --- | --- |
| C1 | Demo commerce (`VITE_COMMERCE_DEMO_MODE=true`) | **done** (local) |
| C2 | Beckn/ONDC protocol client scaffold | **started** — `ondcbuyer/src/lib/ondc/protocolClient.ts` |
| C3 | Buyer NP + Seller NP (or one role first) | Buyer first — after A5 |
| C4 | Registry subscribe + lookup | after A6–A8 |
| C5 | Staging catalog + end-to-end order with network seller | pending |
| C6 | IGM (issue/grievance), cancellation, returns | pending |
| C7 | Pre-prod checklist + probation on prod | ONDC process |
| C8 | Turn off demo mode; point env to live BAP/BPP URLs | last |

Buyer env (when ready, never commit secrets):

```bash
VITE_COMMERCE_DEMO_MODE=false
VITE_ONDC_SUBSCRIBER_ID=
VITE_ONDC_BAP_URI=
VITE_ONDC_GATEWAY_URL=
VITE_ONDC_REGISTRY_URL=
```

---

## D. Agentic runtime

| # | Item | Status |
| --- | --- | --- |
| D1 | Cursor agent runtime (text `/agent`) | **FQDN validated** — Buyer + Seller background handoff |
| D1b | Shared tool runner under AgentGuard | **FQDN validated** — Buyer checkout + Seller refund/publish; production security gate remains |
| D1c | Buyer Realtime voice (`gpt-realtime-2.1-mini`) | **partial** — gateway/text tools pass; physical mic proof blocked in Hermes |
| D2 | `/.well-known/ucp` capability manifest | **not built** |
| D3 | Map ONDC order lifecycle ↔ UCP | after C2 |
| D4 | Identity linking for agent checkout | after B2 live |
| D5 | Optional: Google Merchant / AI Mode | later |
| D6 | OpenAI Agents SDK host swap | **deferred** until tool runner proven |

### Realtime (M12) env — never commit

```bash
# aadharchain/gateway/.env
OPENAI_API_KEY=sk-...
OPENAI_REALTIME_MODEL=gpt-realtime-2.1
# Browser uses ephemeral client secret from gateway; no OpenAI key in Vite
```

---

## E. Production ops

| # | Item | Status |
| --- | --- | --- |
| E1 | Observability | pending |
| E2 | Backup of identity/trust store | pending (DB) |
| E3 | Incident / IGM runbooks | pending |
| E4 | Security review (auth cookies, CORS, PII) | pending |

---

## Working agreement

1. Agent prepares drafts, scripts, env templates, and portal field lists.
2. **You** fill org identity, legal docs, MeriPehchaan OTP, portal signups, Approve wallet, and paste secrets into `.env` (never commit).
3. Agent continues integration + verification after each unblock.
