# ONDC Participant Portal — ledger

Append-only. Agent/operator sessions driving https://portal.ondc.org signup.

## 2026-07-12 — session `ondc-portal-onboard`

| Item | Value |
| --- | --- |
| URL | https://portal.ondc.org/sign-up |
| Reached | **Organisation Details** (wizard step 2 active) |
| Domain | Retail (`#Retail1` checked) |
| Role | **Buyer NP** (`#1` checked) after deliberate Previous → select → Continue |
| Filled | Org name `Aadhar Chain`; Website `https://aadharcha.in` |
| Left blank | Legal Entity Name; Billing/Street/Area; Locality/Town; City/District; Pin Code; State; PAN |
| Hard-stop | Missing legal entity, registered address, State, org PAN (and later User Details password/OTP/mobile) |
| Tab | **Left open** mid-form (no closeout) |
| Maintenance banner | 13 Jul 2026 16:00–22:00 |

### Screenshots

| File | What |
| --- | --- |
| `references/evidence/ondc-org-details-partial-20260712.jpeg` | Org step before role re-check; partial fills |
| `references/evidence/ondc-after-prev-role-check-20260712.jpeg` | Back on Business Profile 2/2 roles |
| `references/evidence/ondc-buyer-np-selected-20260712.jpeg` | After Buyer NP + Continue → Org Details |
| `references/evidence/ondc-org-hardstop-20260712.jpeg` | Hard-stop state: known fields filled, legal/address/PAN empty |

### Notes

- Earlier Continue without viewport scoping skipped proper Buyer selection; Fixed by Previous + label click on Buyer NP + panel-scoped Continue.
- SPA keeps all panels in DOM; off-screen Continues look "visible" to naive queries — use viewport bounds.

## 2026-07-12 — operator-filled Organisation Details + GST check request

| Item | Value |
| --- | --- |
| Session | `ondc-portal-onboard` (tab left open; agent did **not** click Continue) |
| Name of organisation | `GURUSHARAN GUPTA HUF` |
| Website URL | `https://ondcbuyer.aadharchain.in` |
| Legal Entity Name | `GURUSHARAN GUPTA HUF` |
| Country | INDIA |
| Billing/Street/Area | `J-702 Marvel Fria,` |
| Locality/Town | `Wagholi` |
| City/District | `Pune` |
| Pin Code | `412207` |
| State | Maharashtra |
| PAN | `AAJHG6948N` (4th char H = HUF) |
| Continue | **Ready / enabled** — do not advance to User Details unless operator asks |
| GST | Operator asked to check HUF GST account; companion Hermes session `gst-huf-check` |

### Consistency vs GST Part A (`gstin-huf.md` / PRODUCTION-READINESS A3b)

| Check | Result |
| --- | --- |
| Legal name | Match — `GURUSHARAN GUPTA HUF` |
| HUF PAN pattern | Match — `AAJHG6948N` |
| Maharashtra / Pune | Match |
| TRN | `272600333290TRN`; Part B due **26/07/2026** |
| Part A email | `gupta.huf.gurusharan@gmail.com` |
| Website | ONDC uses `ondcbuyer.aadharchain.in` (not `aadharcha.in`) — intentional for this signup |

### GST live check (session `gst-huf-check`)

| Item | Value |
| --- | --- |
| Earlier | TRN resume + captcha hard-stop — `gst-trn-radio-20260712.jpeg`, `gst-trn-hardstop-captcha-20260712.jpeg` |
| URL now | https://reg.gst.gov.in/registration/auth/newappl/business |
| Step | Part B **Business Details** (logged in; Profile 0%; due 26/07/2026) |
| Pre-filled (Part A) | Legal `GURUSHARAN GUPTA HUF`; PAN `AAJHG6948N`; State Maharashtra; District Pune |
| Agent filled | Trade Name = legal name; Constitution **HUF**; commencement **24/08/2024** |
| Operator still needed | Reason to register; liability date; casual/composition/Rule 14A; then SAVE & CONTINUE → Principal Place (address/pin 412207) → later tabs / Aadhaar / uploads |
| SAVE & CONTINUE | **Not ready** — reason + liability date empty |
| ONDC session | `ondc-portal-onboard` untouched |
| Evidence | `gst-fill-snapshot-20260712.jpeg`, `gst-business-details-filled-20260712.jpeg`, `gst-business-details-lower-20260712.jpeg` |

## 2026-07-12 — post-signup inspect (operator completed signup)

| Item | Value |
| --- | --- |
| Session | `ondc-portal-onboard` (reused; still valid / logged in) |
| Logged in | **Yes** — `Gurusharan Gupta Gupta` |
| URL | Started on `/integration-create-plan`; also `/profile`, `/declarations` |
| Org ID | `15462` |
| Org name | `GURUSHARAN GUPTA HUF` |
| Org / integration status | **Initiated Integration** |
| Domain / role | Retail (B2C) API v1.2 · **Buyer NP** |
| Business profile | `15462 - 10008` — Action **Continue** |
| Profile % | No numeric % in UI |
| Profile gaps | Year of incorporation empty; Area of Operation empty; Name as per PAN empty; GSTIN empty; founder empty; KYC uploads empty; consent unchecked; PAN `AAJHG6948N` present |
| Website (profile) | `https://ondcbuyer.aadharcha.in` |
| Declarations | Locked — needs Integration in Progress / Advanced / Live |
| Live ONDC network | **No** — not claimed; demo mode unchanged |
| GST Part B | **Operator / CA-owned** — agent fill paused; `gst-huf-check` left idle on GST dashboard |
| Next (PRODUCTION-READINESS) | Finish A5 profile/KYC (GSTIN after CA) → A6 whitelist → A7 TLS → A8 `scripts/ondc_generate_keys.py` |

### Screenshots

| File | What |
| --- | --- |
| `references/evidence/ondc-postsignup-integrations-20260712.jpeg` | Integrations: Buyer NP Initiated Integration + Continue |
| `references/evidence/ondc-postsignup-profile-20260712.jpeg` | Manage Business Info / KYC incomplete |
| `references/evidence/ondc-postsignup-declarations-20260712.jpeg` | Declarations locked message |
| `references/evidence/ondc-postsignup-home-20260712.jpeg` | `/home` → integrations view (same org status) |

## 2026-07-12 — official docs first (sandbox keys process)

| Item | Value |
| --- | --- |
| Policy | Sandbox/staging Buyer+Seller now; **prod after GSTIN** |
| Primary docs | [Onboarding of Participants](https://github.com/ONDC-Official/developer-docs/blob/main/registry/Onboarding%20of%20Participants.md); [key-format-generation](https://github.com/ONDC-Official/developer-docs/blob/main/registry/key-format-generation.md); [ONDC-Official README](https://github.com/ONDC-Official/.github/blob/main/profile/README.md) |
| Key fact | Keys **generated locally** (Ed25519 + X25519 ASN.1 DER public); portal = whitelist; register via staging `https://staging.registry.ondc.org/subscribe` |
| Staging endpoints | Registry subscribe + v2 lookup; gateway `staging.gateway.proteantech.in` |
| Portal state | Org 15462; Buyer `15462-10008` Integration in Progress; Seller profile missing; whitelist not confirmed |
| Local keys | `.local/ondc-sandbox/{buyer,seller}/` generated earlier — **DER gap** vs docs; not subscribed |
| Skill doc | [`ondc-sandbox-keys.md`](ondc-sandbox-keys.md) |
| Demo mode | Unchanged (`VITE_COMMERCE_DEMO_MODE` not flipped) |
| Next | Operator: FQDNs + ISN/MSN + staging whitelist; Agent: DER fix + on_subscribe/site verification after confirm |

## 2026-07-12 — durable skill encode (session knowledge → owner)

Append-only snapshot so future agents do not re-discover. Control surface: [`../SKILL.md`](../SKILL.md). Keys process: [`ondc-sandbox-keys.md`](ondc-sandbox-keys.md).

| Concern | Durable fact |
| --- | --- |
| Policy | Staging/sandbox Buyer+Seller first; **prod only after GSTIN (CA)**; never flip `VITE_COMMERCE_DEMO_MODE`; never claim live network |
| Keys | Generated **locally** (Ed25519 + X25519); portal download ≠ official signing/encryption process; path `aadharchain/gateway/.local/ondc-sandbox/` (gitignored); DER gap on encryption public before `/subscribe` |
| Staging URLs | Registry `https://staging.registry.ondc.org/subscribe`; gateway `https://staging.gateway.proteantech.in/search`; lookup `…/v2.0/lookup` |
| Portal | Signup done; logged in; org **15462** `GURUSHARAN GUPTA HUF`; Buyer `15462-10008` Initiated Integration / Integration in Progress; Seller **not created**; KYC gaps (GSTIN, PAN upload, area of operation, …) |
| Websites | Signup `ondcbuyer.aadharchain.in`; profile shows `ondcbuyer.aadharcha.in` — do not invent FQDNs; operator confirms staging hosts |
| Org form | J-702 Marvel Fria, Wagholi, Pune 412207, Maharashtra; PAN `AAJHG6948N`; ONDC email `gurusharan.gupta@aadharcha.in` |
| GST | Part A done; TRN `272600333290TRN`; Part B due 26/07/2026; **CA completes**; agent fill paused (not “GST forever” — GSTIN gates **prod**) |
| Hermes | `ondc-portal-onboard` (portal); `gst-huf-check` (GST idle / CA) |
| Seller role | Prefer **ISN** for AgentGuard inventory seller; MSN only if marketplace — operator confirms before Add |
| Next | Operator: staging FQDNs + ISN/MSN + staging whitelist → Agent: Seller profile, DER keys, verification host, staging subscribe, wire `ONDC_*` when asked → After GSTIN: portal KYC + prod path |

No FQDNs invented this encode. portfolio-browser remains browser driver only; this skill owns partner workflow.

## 2026-07-12 — operator FQDN confirm + live DNS/TLS probe

| Item | Value |
| --- | --- |
| Buyer FQDN | **`ondcbuyer.aadharcha.in`** (operator authoritative) |
| Seller FQDN | **`ondcseller.aadharcha.in`** (operator authoritative) |
| Domain | GoDaddy `aadharcha.in` — see [`godaddy.md`](godaddy.md) |
| dig A (both) | `76.76.21.21` |
| HTTPS | Both **HTTP/2 200**; `server: Vercel`; HSTS `max-age=63072000` |
| Body | Vite shells — Buyer title `ONDC Buyer`; Seller title `ONDC Seller` (not parking/empty) |
| GoDaddy DNS edit | **Not needed** — records already match other aadharcha.in Vercel hosts |
| `/on_subscribe` / verification HTML | **Not hosted yet** — static Vercel frontend only; gateway/proxy target TBD |
| Staging whitelist | Still **operator** |
| Seller ISN/MSN | Prefer **ISN**; ask only if portal forces |
| GSTIN | Still CA (prod later) |
| Demo mode | Unchanged |
| Evidence | `evidence/fqdn-buyer-live-20260712.jpeg`, `evidence/fqdn-seller-live-20260712.jpeg` (if Hermes succeeded) |
| Skill updates | `SKILL.md`, `ondc-sandbox-keys.md`, `ondc-portal.md`, `godaddy.md`, this ledger |

## 2026-07-12 — sandbox integration ladder (code / deploy / local-vs-web)

Encoded [`ondc-sandbox-integration-ladder.md`](ondc-sandbox-integration-ladder.md): pending code (DER, on_subscribe, verification, subscribe client, Vercel rewrites); integrations (whitelist wait, Seller profile, Auth0 secrets, Render redeploy); verdict that full registry subscribe cannot be proven on localhost; refined ladder local smoke → deploy → whitelist → staging web → prod after GSTIN. Live probes: FQDNs 200 Vercel; `/ondc-site-verification.html` 404; Render gateway missing Auth0/ONDC/AgentGuard routes vs local repo.

## 2026-07-12 — raise-staging resume (A–F)

Session `ondc-portal-onboard`. No commit. No prod. No demo flip. Auth0 not redone.

| Step | Result |
| --- | --- |
| **A Whitelist** | **HARD-STOP** — Buyer journey `interest=10008&configId=29` → Build components → task **1.a** EnvAccessRequest. Registry field locked **PreProd** (`preprodSubscriberId` / `preprodSubscriberURL`). Filled FQDN `ondcbuyer.aadharcha.in` + URL `/ondc`; domain attempt Grocery/`ONDC:RET10`. **Raise Request → Submit** → toast ``Valid_from` must be in ISO 8601 date format`` + console `saveHandler` TypeError (`status` of undefined). List still “No Configuration added!”. Seller whitelist not raised. Tab left open on 1.a. Fallback email: [`evidence/staging-whitelist-email-template-20260712.md`](evidence/staging-whitelist-email-template-20260712.md). |
| **B Seller ISN** | **DONE** — Integrations **Add another** → Retail B2C API v1.2 → **Seller NP - Inventory Seller Node (ISN)** → `15462 - 10011` Initiated Integration. Evidence: `ondc-seller-profile-after-add-20260712.jpeg`, `ondc-integrations-after-seller-20260712.jpeg`. |
| **C Keys** | **DONE** — `ondc_generate_keys.py` emits `encryption_public_key_format: asn1_der_spki_b64`; buyer+seller under `aadharchain/gateway/.local/ondc-sandbox/` converted. Do not use portal generate&download as official keypairs. |
| **D Hosting code** | **DONE locally** — `aadharchain/gateway/app/ondc_onboard_routes.py` (site-verification + `on_subscribe` + status; path + Host-mapped). `ondcbuyer`/`ondcseller` `vercel.json` rewrites to `REPLACE_PUBLIC_GATEWAY_ORIGIN`. **Deploy pending** — no public gateway origin yet. |
| **E Subscribe** | **DRAFTED only** — [`evidence/staging-subscribe-drafts-20260712.json`](evidence/staging-subscribe-drafts-20260712.json). Do **not** POST until whitelist ACK. Placeholders: `gst_no`, `mobile_no`. |
| **F Skill** | SKILL next-actions + this ledger + keys/ladder gap tables updated. |

**Operator hard-stops:** (1) finish EnvAccessRequest or email techsupport for **staging** whitelist both FQDNs; (2) public gateway URL + replace Vercel placeholder + redeploy; (3) paste `AUTH0_*` separately; (4) no legal Approve / prod.

**Next when cleared:** live verification HTML + on_subscribe on FQDNs → POST staging subscribe drafts → lookup → optional `ONDC_*` wire.


## 2026-07-12 — skill encode + operator PreProd Subscribed (verified)

Append-only. Portal-rescan agent may add more detail after this; do not clobber.

| Concern | Durable fact (screenshot-verified) |
| --- | --- |
| Org | `15462` `GURUSHARAN GUPTA HUF` — Integration in Progress |
| Buyer | `15462-10008` Retail Buyer NP — Integration in Progress |
| Seller | `15462-10011` Retail **ISN** — Initiated Integration |
| Buyer EnvAccess | Subscriber `ondcbuyer.aadharcha.in` · Environment **Pre-Prod** · Status **Subscribed** · Requested 12/07/2026 |
| Portal keys UI | Unique Key ID present; Encryption + Signing public keys shown; Valid 12/07/2026–12/07/2027 — **portal artifact**, not local DER subscribe keypairs |
| Portal download | `~/Downloads/keys.json` copied to gitignored `aadharchain/gateway/.local/ondc-sandbox/portal-download/` (filenames only in skill) |
| Next journey | Task **1.b** Build integration components — **Pending** |
| Staging vs PreProd | Portal UI path = PreProd; Staging registry URL still documented for sandbox docs; confirm which env `/subscribe` targets before POST |
| Evidence (exist) | `ondc-portal-operator-submit-window-20260712.jpeg`, `ondc-postsubmit-buyer-journey-20260712.jpeg`, `ondc-postsubmit-keys-ui-20260712.jpeg`, `ondc-postsubmit-integrations-20260712.jpeg` |
| Evidence cite fix | Prior raise-staging row cited missing `ondc-seller-profile-after-add-*.jpeg` — use `ondc-sandbox-add-seller-role-options-20260712.jpeg`, `ondc-sandbox-seller-role-dropdown-20260712.jpeg`, `ondc-sandbox-integrations-list-20260712.jpeg` instead |
| Auth parallel | Local Auth0 smoke **PASS** — see authentication skill (`aadharchain-gateway-local`, tenant `dev-ejqlkc0qt84udk7i.us.auth0.com`) |
| Next | Seller env access; public gateway + Vercel `REPLACE_PUBLIC_GATEWAY_ORIGIN`; verification + on_subscribe; subscribe with **local DER**; GSTIN→prod later |


## 2026-07-12 — /home operator link (Comet AX; WIP SOCKET_DOWN)

| Item | Value |
| --- | --- |
| URL | https://portal.ondc.org/home (landed Integrations / create-plan shell) |
| Logged in | **Yes** — Gurusharan Gupta Gupta |
| Org | **15462** `GURUSHARAN GUPTA HUF` — **Integration in Progress** |
| Buyer | `15462-10008` Buyer NP Retail B2C — Continue |
| Seller | `15462-10011` Seller NP ISN — Continue |
| WIP | SOCKET_DOWN after one preflight; hermes_run failed; no Hermes cursor_move proof |
| Evidence | `evidence/ondc-home-operator-link-20260712.jpeg` |
| Next click | Buyer **Continue** (`15462-10008`) → confirm 1.a PreProd Subscribed still shown; then Seller Continue for 1.a Pending |


## 2026-07-12 — Seller 1.a PreProd Subscribed (parity with Buyer)

Session `ondc-portal-onboard`. WIP sock up; preflight `hermes-wip` exit 0. No commit secrets. No demo flip. Did **not** check 1.b attestation.

| Item | Value |
| --- | --- |
| Seller journey | `integration-journey-comply?interest=10011&configId=31` |
| Path | Integrations → Seller Continue → Build components expand → 1.a Raise Request **modal** |
| Registry | Locked **PreProd** (same as Buyer) |
| Subscriber ID | `ondcseller.aadharcha.in` |
| Subscriber URL | `/ondc` → `https://ondcseller.aadharcha.in/ondc` |
| Domain | Grocery `ONDC:RET10` (Retail B2C) |
| Cities | Select all cities checked |
| Result | **1.a Completed** 12/07/2026 **02:44 PM**; List of Requests row **Subscribed** |
| Portal keys | `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9`; Encryption/Signing publics present; Valid 12/07/2026–12/07/2027 — portal artifact ≠ local DER |
| Buyer parity | Buyer already Subscribed PreProd; Seller now matches |
| Hard-stop avoided | No OTP/Approve; did not agent-check 1.b |
| Note | Outer inline form + empty Raise Request modal both needed fill; Submit from filled modal succeeded (no Valid_from toast this time) |
| Evidence | `evidence/ondc-seller-continue-after-20260712.jpeg`, `ondc-seller-build-expanded-20260712.jpeg`, `ondc-seller-1a-modal-filled-20260712.jpeg`, `ondc-seller-1a-subscribed-20260712.jpeg`, `ondc-seller-1a-after-submit-20260712.jpeg` |
| Next | Public gateway + Vercel `REPLACE_PUBLIC_GATEWAY_ORIGIN`; verification + on_subscribe with portal keys; Buyer/Seller **1.b** operator-only; GSTIN→prod later |


## 2026-07-12 — portal keys stored + sandbox integration started

No secrets committed. No prod registry POST. Demo mode unchanged.

| Item | Value |
| --- | --- |
| Downloads | `~/Downloads/keys.json` (Buyer ~14:06); `~/Downloads/keys (1).json` (Seller ~14:44; signing prefix matches Seller UI) |
| Stored | `aadharchain/gateway/.local/ondc-sandbox/portal-download/{buyer,seller}/keys.json` + PEMs via `scripts/ondc_materialize_portal_keys.py` |
| vs local DER | Same format; **different** keypairs — PreProd uses portal; Staging optional keeps local |
| Local smoke | `scripts/ondc_onboard_portal_smoke.py` PASS; `:43101/ondc/np/{buyer,seller}/status` → `keys_source=portal-download`, `registry_env=preprod` |
| Vercel | `ondcbuyer`/`ondcseller` `vercel.json` → `identity-aadhar-gateway-main.onrender.com` (redeploy pending) |
| Render | Onboard routes **404** — redeploy blocked for FQDN challenge |
| Drafts | `evidence/preprod-subscribe-drafts-20260712.json` (do not POST until live) |
| Next | Operator Render+Vercel redeploy; Agent FQDN probe + lookup |


## 2026-07-12 — portal keys ingest + sandbox integration start

| Item | Value |
| --- | --- |
| Operator mapping | **`keys` / `keys.json` = Buyer**; **`key1` / `keys (1).json` = Seller** |
| Buyer copy | `~/Downloads/keys.json` → `aadharchain/gateway/.local/ondc-sandbox/portal-download/buyer/keys.json` (+ PEMs materialized) |
| Seller copy | `~/Downloads/keys (1).json` → `…/portal-download/seller/keys.json` (+ PEMs materialized) |
| vs local DER | Fingerprints differ — keep local for optional Staging; **PreProd uses portal** |
| Buyer uk_id | `1aee68ad-bc2a-4fc4-b233-7e14c6abba9b` |
| Seller uk_id | `baf58086-7024-438a-becf-4cfa056ec8d9` |
| Local smoke | PASS — verification HTML + `/on_subscribe` roundtrip both roles (portal PEMs, PreProd enc key) |
| Vercel rewrites | Buyer + Seller → `identity-aadhar-gateway-main.onrender.com` `/ondc/np/{role}/…` |
| Public gateway | Render `/api/health` 200; **ondc onboard routes NOT deployed** (404 / openapi has no ondc paths) |
| FQDN verification | Both `ondc*-aadharcha.in/ondc-site-verification.html` still **404** (rewrite target missing routes) |
| PreProd drafts | `evidence/preprod-subscribe-drafts-20260712.json` — **do not POST** until gateway live + lookup |
| Demo mode | Unchanged |
| Prod | Forbidden until GSTIN |

**Can call PreProd `/subscribe` yet?** No — portal already Subscribed for both uk_ids; FQDN `/on_subscribe` not live; redeploy gateway first; prefer registry lookup before any re-POST.

**Next:** Redeploy gateway with `ondc_onboard_routes` + portal key material on Render; redeploy Vercel if needed; probe FQDN verification + on_subscribe; then lookup PreProd.

## 2026-07-12 — FQDN deploy live ($0 Free/Hobby)

| Item | Value |
| --- | --- |
| Render | **Free** `identity-aadhar-gateway-main`; source `ingpoc/aadhaar-chain` `@codex/ondc-onboard-fqdn-20260712`; commit **`933cadf`** live |
| Keys on Render | Env `ONDC_*_PEM_B64` → status `keys_source=env`; uk_ids buyer `1aee68ad-…` seller `baf58086-…` |
| Auth0 | `GET /api/auth/providers` → auth0 true, demo_continue false, runtime_mode staging |
| Vercel | **Hobby**; FQDN projects **`ondc-buyer`** / **`ondc-seller`** (not ondcbuyer/ondcseller CLI twins) |
| Buyer dpl | `dpl_6TbnYCSW5dK792iVdCPqsbxuKq4g` → `ondcbuyer.aadharcha.in` |
| Seller dpl | `dpl_3x9Nrr6HdoUwwyg4CTMN96nbBEyR` → `ondcseller.aadharcha.in` |
| FQDN verify | Both **200** + `meta name=ondc-site-verification` |
| on_subscribe | FQDN POST **400** decrypt fail on junk challenge (route live; not 404) |
| PreProd lookup | `v2.0/lookup` NACK / auth header required — **no subscribe re-POST** |
| Hermes UI | Buyer `/search`, Seller `/dashboard` |
| Aborted | Vercel Pro Password Protection ($150); any Render Upgrade |
| Demo mode | Unchanged |

**Next:** Signed PreProd lookup if needed; network e2e later; no demo flip.
