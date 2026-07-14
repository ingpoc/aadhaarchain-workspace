# ONDC sandbox / staging keys — official process

**Policy (2026-07-12):** Buyer + Seller **staging/sandbox first**. **Prod whitelist / prod subscribe only after GSTIN (CA)**. Do not flip `VITE_COMMERCE_DEMO_MODE`. Do not commit private keys. Do not invent FQDNs.

Keys are **generated locally** (Ed25519 signing + X25519 encryption). They are **not** “downloaded as API keys” from the portal. Portal = account + **subscriber_id whitelist / environment access**; registry `/subscribe` registers public keys.

Portal UI **“Click to generate & download below Key”** (Integration journey → Start transacting) ≠ the official Ed25519/X25519 process. Prefer official utilities / `scripts/ondc_generate_keys.py`. Treat portal one-shot download as a separate portal artifact until mapped to a documented field.

## Official docs (authoritative)

| Doc | What it defines |
| --- | --- |
| [Onboarding of Participants](https://github.com/ONDC-Official/developer-docs/blob/main/registry/Onboarding%20of%20Participants.md) | Prerequisites (FQDN, SSL, **portal whitelist**), keygen, `ondc-site-verification.html`, `/on_subscribe`, `/subscribe` per env |
| [Key format generation](https://github.com/ONDC-Official/developer-docs/blob/main/registry/key-format-generation.md) | Signing = Ed25519 raw b64; encryption public = **ASN.1 DER → b64** (X25519) |
| [Signing & verification](https://github.com/ONDC-Official/developer-docs/blob/main/registry/signing-verification.md) | Auth header / `keyId` = `{subscriber_id}\|{unique_key_id}\|ed25519` |
| [ONDC-Official profile README](https://github.com/ONDC-Official/.github/blob/main/profile/README.md) | Staging/Pre-Prod vs Prod (DNS TXT **prod only**); gateway/registry endpoints |
| [Tech Quickstart](https://github.com/ONDC-Official/developer-docs/blob/main/Tech_Quickstart_Guide.md) | Index + [Addition to Staging Registry](https://docs.google.com/document/d/1HnOeTBWvYXO8kjAEHSrR6W8XICsPfKGIT6B_IhmvVV0/edit) |
| [Subscribe FAQs](https://docs.google.com/document/d/15Dpy02lqtcU9tslyMqaI4UtnD2rtwnjAbn1narO0364/edit) | Payload field FAQs |
| [Swagger — Registry Onboarding](https://app.swaggerhub.com/apis-docs/ONDC/ONDC-Registry-Onboarding/2.0.5) | `/subscribe` body (`ops_no` 1 buyer / 2 seller / 4 both) |
| [Staging env (Confluence)](https://ondc-issue-logging-cohort1.atlassian.net/wiki/spaces/TG/pages/35160382/6.+Staging+Environment) | Staging gateway + ref-app test targets |
| Official utilities | [signing_and_verification](https://github.com/ONDC-Official/reference-implementations/tree/main/utilities/signing_and_verification) · [on_subscribe service](https://github.com/ONDC-Official/reference-implementations/tree/main/utilities/on_subscibe-service) |

## Environments

| Env | Registry `/subscribe` | Gateway (search) | Notes |
| --- | --- | --- | --- |
| **Staging** (sandbox / early test) | `https://staging.registry.ondc.org/subscribe` | `https://staging.gateway.proteantech.in/search` | Whitelist + SSL + site verification; **no** DNS TXT |
| **Pre-Prod** | `https://preprod.registry.ondc.org/ondc/subscribe` | `https://preprod.gateway.ondc.org/search` | After staging demo/approval |
| **Production** | `https://prod.registry.ondc.org/subscribe` | `https://prod.gateway.ondc.org/search` | DNS TXT + portal admin path; **blocked until GSTIN** |

Lookup (staging): `https://staging.registry.ondc.org/v2.0/lookup`

ONDC staging public encryption key (for `/on_subscribe` challenge) — Onboarding §6:  
`MCowBQYDK2VuAyEAduMuZgmtpjdCuxv+Nc49K0cB6tL/Dj3HZetvVN7ZekM=`

## Checklist — Buyer staging (BAP) then Seller (BPP)

### Buyer

1. **Portal account + profile** — org `15462`, Buyer `15462-10008`, Integration in Progress. *(Done.)*
2. **FQDN = `subscriber_id`** — **`ondcbuyer.aadharcha.in`** (operator confirmed 2026-07-12). Signup typo `ondcbuyer.aadharchain.in` is obsolete. Live: DNS A `76.76.21.21`, HTTPS 200, `server: Vercel`, Vite ONDC Buyer shell.
3. **Staging whitelist** — raise environment access for that FQDN; wait 6–48h. Skip → `Subscriber Id is not whitelisted` (code 132).
4. **Local keygen** — Ed25519 + X25519 → `aadharchain/gateway/.local/ondc-sandbox/buyer/` (see below). Encryption public must be **ASN.1 DER b64** before subscribe.
5. **Host** `https://ondcbuyer.aadharcha.in/ondc-site-verification.html` — meta `ondc-site-verification` = request_id signed with signing private key (**no hash**). Static Vite alone cannot serve this + POST — need gateway/proxy route or Vercel rewrite to gateway.
6. **Host** `POST https://ondcbuyer.aadharcha.in/<callback_url>/on_subscribe` — decrypt challenge; return `{ "answer": "..." }`.
7. **POST `/subscribe`** to **staging** registry (`ops_no` buyer). Expect ACK.
8. **Lookup** staging registry — confirm subscriber record.
9. **E2E** vs staging ref seller. Keep `VITE_COMMERCE_DEMO_MODE=true` until evidence gate.

### Seller (second profile + FQDN)

1. Portal **Add another** business profile: Domain Retail + Role **Seller NP — ISN** (AgentGuard inventory default). **MSN only if marketplace-node** — ask operator only if portal forces a choice.
2. FQDN **`ondcseller.aadharcha.in`** (operator confirmed 2026-07-12) + SSL live (same Vercel A) + **staging whitelist**.
3. Separate keypair under `.local/ondc-sandbox/seller/`.
4. Same site-verification + `/on_subscribe` + `/subscribe` with seller `ops_no` / `sellerApp` (MSN flag aligned).
5. Lookup + E2E vs staging ref buyer.

**Order:** Buyer staging path first, then Seller. Prod path only after GSTIN.

## Local key material

```bash
# Preferred staging path (exists; gitignored)
python3 scripts/ondc_generate_keys.py --out aadharchain/gateway/.local/ondc-sandbox/buyer
python3 scripts/ondc_generate_keys.py --out aadharchain/gateway/.local/ondc-sandbox/seller
```

| Concern | Fact |
| --- | --- |
| Path | `aadharchain/gateway/.local/ondc-sandbox/{buyer,seller}/` — PEMs + `public_metadata.json` + `request_id.txt` |
| Gitignore | Nested `aadharchain/.gitignore`: `gateway/.local/` + `data/ondc-keys/`. Workspace also ignores `/aadharchain/` |
| Script default | `scripts/ondc_generate_keys.py` defaults to `data/ondc-keys/` — use `--out` for sandbox path |
| Encryption public | **`asn1_der_spki_b64`** (fixed 2026-07-12); `--convert-existing` supported |
| Wire | Ask before writing `ONDC_*` into `gateway/.env`. Staging URLs only. `ONDC_ENABLED` can stay false until subscribe ACK |

## Map to this repo

| Concern | Owner |
| --- | --- |
| Ops ladder | `PRODUCTION-READINESS.md` A5–A8, C3–C5 — **A6/A8 for staging now**; **prod A6–A8 after GST** |
| Onboard hosting | `aadharchain/gateway/app/ondc_onboard_routes.py` — site-verification + `on_subscribe` + status (local). Vercel rewrites → `REPLACE_PUBLIC_GATEWAY_ORIGIN` |
| Commerce adapter | `aadharchain/gateway/app/ondc_routes.py` scaffold — signed search later |
| Buyer Vite | `VITE_ONDC_*` staging sketches in `.env.example`; keep demo mode on |

## Portal download vs local DER (2026-07-12)

| Artifact | Path | Role |
| --- | --- | --- |
| Portal Buyer download | Operator: **`keys`** → `~/Downloads/keys.json` → `portal-download/buyer/` (+ PEMs) | PreProd Subscribed `uk_id` `1aee68ad-bc2a-4fc4-b233-7e14c6abba9b` |
| Portal Seller download | Operator: **`key1`** → `~/Downloads/keys (1).json` → `portal-download/seller/` (+ PEMs) | PreProd Subscribed `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9` |
| Local official pairs | `.local/ondc-sandbox/{buyer,seller}/` + `public_metadata.json` | Ed25519 + X25519 ASN.1 DER — **different** keypairs; keep for optional Staging |

**Assessment:** Portal `keys.json` is the **same wire format** as official (signing public 32B raw b64; encryption public ASN.1 DER SPKI b64). Different keypairs from local DER. PreProd `/on_subscribe` must use **portal** PEMs (`ONDC_REGISTRY_ENV=preprod` auto-selects `portal-download/{role}`). Local DER only if deliberately opening Staging `/subscribe`. Never commit either set. Meta (no secrets): `portal-download/README.meta.json`.

Materialize / smoke:

```bash
python3 scripts/ondc_materialize_portal_keys.py
python3 scripts/ondc_onboard_portal_smoke.py
# local: GET :43101/ondc/np/{buyer|seller}/status → keys_source=portal-download
```

## Gap vs portal state (2026-07-12 late)

| Doc step | Our state |
| --- | --- |
| Portal account | Done — org 15462 |
| Buyer / Seller profiles | Done — both PreProd **Subscribed** |
| FQDN + SSL | Vercel 200 |
| Portal keys stored | **Done** — buyer+seller under `portal-download/` (gitignored) |
| Local onboard routes | **Done** — verification + on_subscribe + status; portal PEMs wired |
| Vercel rewrite origin | Set to `identity-aadhar-gateway-main.onrender.com` in repo `vercel.json` — **needs Vercel redeploy** |
| Render gateway onboard routes | **404** today — **needs Render redeploy** of current gateway code + portal keys on host |
| `/subscribe` POST | PreProd drafts ready (`evidence/preprod-subscribe-drafts-20260712.json`) — **do not POST** until FQDN endpoints live; portal may already hold registry row |
| Prod | **Forbidden until GSTIN** |

## Next actions

| Who | Action |
| --- | --- |
| **Operator** | Redeploy Render gateway (include onboard routes + mount/copy `.local` portal PEMs or set `ONDC_*_KEYS_DIR`); redeploy Vercel Buyer+Seller |
| **Agent** | After live: probe FQDN verification + on_subscribe; optional PreProd lookup; POST subscribe only if lookup empty |
| **After GSTIN** | Portal KYC + prod path |
