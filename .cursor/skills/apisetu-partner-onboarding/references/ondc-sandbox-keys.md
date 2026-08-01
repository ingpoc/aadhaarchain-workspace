# ONDC participant keys — official process

**Policy:** Retail Buyer/Seller are already PreProd subscribed. LOG10 uses the
separate `ondclbnp.aadharcha.in` identity and a distinct keypair. Production
whitelist/subscribe remains blocked until GSTIN and its own gate evidence. Do
not commit private keys or regenerate an existing participant's keys.

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

## Current participant identities

| Identity | Role | Key boundary |
| --- | --- | --- |
| `ondcbuyer.aadharcha.in` | Retail BAP | Existing Retail Buyer keys; do not regenerate |
| `ondcseller.aadharcha.in` | Retail ISN/BPP | Existing Retail Seller keys; do not regenerate or reuse for LOG10 |
| `ondclbnp.aadharcha.in` | LOG10 Buyer NP/LBNP/BAP | Distinct Ed25519/X25519 pair; portal registration remains gated |

For every new identity, prove its own TLS, site-verification,
`/ondc/on_subscribe`, registry/portal readback, and key source. An HTTP 200 from
another participant's mapper is a failure, not reuse.

## Local key material

```bash
# Inspect the existing generator before a separately authorized new identity.
python3 scripts/ondc_generate_keys.py --help
```

| Concern | Fact |
| --- | --- |
| Path | `aadharchain/gateway/.local/ondc-sandbox/{buyer,seller,lbnp}/` — PEMs + `public_metadata.json` + `request_id.txt` |
| Gitignore | Nested `aadharchain/.gitignore`: `gateway/.local/` + `data/ondc-keys/`. Workspace also ignores `/aadharchain/` |
| Script default | `scripts/ondc_generate_keys.py` defaults to `data/ondc-keys/` — use `--out` for sandbox path |
| Private PEM mode | `0600`; `scripts/ondc_generate_keys.py` enforces this after each write and fails closed if group/other bits remain |
| Public metadata | Public keys and private-key paths only; private key bytes stay in the `0600` PEMs. `--self-test` blocks private material from `public_metadata.json`. |
| Encryption public | **`asn1_der_spki_b64`** (fixed 2026-07-12); `--convert-existing` supported |
| Wire | Configure only the intended identity after its endpoint gate. Do not change existing Retail env or `ONDC_ENABLED` from this key guide. |

## Map to this repo

| Concern | Owner |
| --- | --- |
| Ops ladder | `PRODUCTION-READINESS.md` A5–A8, C3–C5 — **A6/A8 for staging now**; **prod A6–A8 after GST** |
| Onboard hosting | `aadharchain/gateway/app/ondc_onboard_routes.py` — site-verification + `on_subscribe` + status. Retail uses Vercel rewrites; LBNP is the second custom domain on the existing Render gateway. |
| Protocol adapters | Retail signed traffic remains in its existing mapper; LOG10 requires its dedicated namespace/version mapping |
| Browser apps | Never hold ONDC private keys or Registry credentials |

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

## State routing

- Retail Buyer/Seller public endpoint and network evidence is historical and
  remains owned by the testing ledger; never re-run it from this key guide.
- The LBNP pair exists only for its dedicated identity. Current deployment and
  public-DNS status is owned by [`.voice/progress.md`](../../../../.voice/progress.md).
- Portal environment access, `1.b`, legal tasks, registry mutation, and
  production remain separate authorized gates.
