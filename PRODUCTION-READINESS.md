# Production readiness — trust substrate + ONDC + UCP

Owner path for going from local demo → production-grade AadhaarChain portfolio.
Update status in place. Do not invent access; stop when human org credentials are required.

## Locked recommendation (2026-07-11)

| Rail | Choice | Why |
| --- | --- | --- |
| KYC (now) | **Local demo + commercial Setu.co eKYC sandbox** | Ship verify → trust without MeitY org KYC / GST |
| KYC (later) | MeitY API Setu / DigiLocker | Paused — resume when ready for gov production access |
| ONDC | **Buyer NP first** (still later) | After trust rail is live |
| UCP | **After ONDC protocol client** | Needs real order lifecycle |

**Operator decision (2026-07-11):** pause GST Part B + MeitY partner signup; stay local; pursue **Setu.co sandbox**.

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

**Hierarchy:** AadhaarChain trust substrate → **AgentGuard** (flagship) → ONDC Seller first → Buyer / FlatWatch later.

Product promise: verify once, disclose minimally, delegate safely, revoke anytime — not “Aadhaar on blockchain,” not SSI wallets, not universal reputation, not land title tokenization.

| Owner | Path |
| --- | --- |
| Product thesis | [`PRODUCTIDEA.md`](PRODUCTIDEA.md) |
| AadhaarChain | [`aadharchain/GOAL.md`](aadharchain/GOAL.md) |
| ONDC Seller (first AgentGuard deploy) | [`ondcseller/GOAL.md`](ondcseller/GOAL.md) |
| ONDC Buyer | [`ondcbuyer/GOAL.md`](ondcbuyer/GOAL.md) |
| FlatWatch | [`flatwatch/GOAL.md`](flatwatch/GOAL.md) |

### Goal map (what each surface needs)

| Surface | Needs for the goal | Sandbox / local test (enough now) | Production later |
| --- | --- | --- | --- |
| **AadhaarChain** (`:43100` / `:43101`) | Verify → minimal trust claims → SSO + proof-tokens; AgentGuard foundation | Demo upload **or** Setu sandbox → trust; burner SSO; fixtures OK for lanes | Live KYC; durable DB; AgentGuard policy/approval |
| **ONDC Buyer** (`:43102`) | AadhaarChain login; trust chip; elevated checkout = verified + `buyer_checkout_identity_proof` | Identity auth on; demo commerce; elevated lane with fixture/Setu-verified wallet | Real Beckn; NP whitelist; payments |
| **ONDC Seller** (`:43103`) | First AgentGuard surface; elevated publish = verified + seller proof-token | Same SSO/trust; demo catalog; AgentGuard refund demo next | Real BPP / network catalog |
| **Setu.co sandbox** | Optional non-fixture KYC → gateway completes verification → trust | Client id/secret + product instance | Live keys + Bridge org KYC |
| **MeitY / GST** | Not required for local or Setu sandbox | **Paused** | Only if gov KYC chosen |
| **ONDC portal / UCP** | Not required for trust+SSO+demo proof | **Later** | After trust + AgentGuard seller slice |

**Elevated commerce (goal-critical):** SSO cookie alone is not enough — checkout / catalog publish need `trust_state=verified` + purpose-specific proof-token.

**Sandbox test order:** (1) `lane burner seller` → (2) trust verified (fixture or Setu) → (3) elevated demo commerce → (4) Setu secrets only to replace fixtures. Do not block 1–3 on GST/MeitY/Bridge go-live.

---

## A. Access / registration (human + agent)

| # | Item | Who | Status | Link / action |
| --- | --- | --- | --- | --- |
| A1 | KYC rail (active) | Locked | **Setu.co sandbox + local demo** | Bridge signup + `SETU_EKYC_*` |
| A2 | MeitY API Setu partner signup | Paused | **paused** | https://partners.apisetu.gov.in/signup — resume later |
| A3 | Org docs + MeitY approval | Paused | **paused** | |
| A3b | **GSTIN (HUF)** | Paused | **Part A done only** — TRN `272600333290TRN`; Part B optional by 26/07/2026 | Do not block sandbox on GST |
| A4 | Subscribe Aadhaar / DigiLocker APIs | You + API provider approve | after A3 | Client ID / secret issued |
| A5 | ONDC Participant Portal account | You | **STOP — signup** | https://portal.ondc.org — complete profile 100% |
| A6 | ONDC subscriber_id whitelist | You request; ONDC approves | after A5 | FQDN + SSL |
| A7 | Production domain + TLS | You / infra | pending | e.g. `buyer.aadharcha.in` |
| A8 | ONDC signing + encryption keypairs | Agent generates; you store secrets | after A7 | |
| A9 | UCP capability profile | Agent later | after ONDC client | https://ucp.dev |
| A10 | Payments (UPI / PSP) | You | pending | not demo mode |
| A11 | Hosting non-ephemeral state | Agent can blueprint | pending | Postgres + object storage |

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

> AadhaarChain anchors a Solana wallet to a verified Indian identity for ONDC buyer/seller trust. We request DigiLocker requester access to obtain user-consented e-Aadhaar / identity documents, store only masked fields + verification decision off-chain, and expose a trust read API to portfolio apps (ONDC buyer/seller). No full Aadhaar number is retained. Callback / redirect URI: `https://aadharcha.in` (and local `http://127.0.0.1:43100` for sandbox if allowed).

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

## D. Agentic UCP

| # | Item | Status |
| --- | --- | --- |
| D1 | Cursor agent runtime (local FlatWatch/ONDC agent pages) | **local done** |
| D2 | `/.well-known/ucp` capability manifest | **not built** |
| D3 | Map ONDC order lifecycle ↔ UCP | after C2 |
| D4 | Identity linking for agent checkout | after B2 live |
| D5 | Optional: Google Merchant / AI Mode | later |

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
