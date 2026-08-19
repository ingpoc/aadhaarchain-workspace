# ONDC participant keys — official process

**Policy:** Retail Buyer/Seller are already PreProd subscribed. LOG10 uses the
separate `ondclbnp.aadharcha.in` identity and a distinct keypair. Production
whitelist/subscribe remains blocked until GSTIN and its own gate evidence. Do
not commit private keys or regenerate an existing participant's keys.

Keys are **generated locally** (Ed25519 signing + X25519 encryption). They are **not** “downloaded as API keys” from the portal. Portal = account + **subscriber_id whitelist / environment access**; registry `/subscribe` registers public keys.

Portal UI **“Click to generate & download below Key”** (Integration journey → Start transacting) ≠ the official Ed25519/X25519 process. Prefer official utilities / `scripts/ondc_generate_keys.py`. Treat portal one-shot download as a separate portal artifact until mapped to a documented field.

## Official docs (authoritative)

This app's portal/GST facts stay here. ONDC procedure + **docs vs GitHub TOC**:
`~/.agents/skills/ondc` Sources (`references/sources.md`). Keys/host/registry
lanes there supersede the Staging rows below.

| Doc | What it defines |
| --- | --- |
| [Onboarding of Participants](https://github.com/ONDC-Official/developer-docs/blob/main/registry/Onboarding%20of%20Participants.md) | Prerequisites, keygen, site-verification, `/on_subscribe`, `/subscribe` (Staging **decommissioned**) |
| [Key format generation](https://github.com/ONDC-Official/developer-docs/blob/main/registry/key-format-generation.md) | Signing = Ed25519 raw b64; encryption public = **ASN.1 DER → b64** |
| [Signing & verification](https://github.com/ONDC-Official/developer-docs/blob/main/registry/signing-verification.md) | `keyId` = `{subscriber_id} | {unique_key_id} | ed25519` |
| [Swagger — Registry Onboarding](https://app.swaggerhub.com/apis-docs/ONDC/ONDC-Registry-Onboarding/2.0.5) | `/subscribe` body (`ops_no` 1 buyer / 2 seller / 4 both; 3 & 5 deprecated) |
| Official utilities | [signing_and_verification](https://github.com/ONDC-Official/reference-implementations/tree/main/utilities/signing_and_verification) · [on_subscribe service](https://github.com/ONDC-Official/reference-implementations/tree/main/utilities/on_subscibe-service) |

## Environments

| Env | Registry `/subscribe` | Gateway (search) | Notes |
| --- | --- | --- | --- |
| **Staging** | retired | retired | Do not subscribe. Historical only. |
| **Pre-Prod** | `https://preprod.registry.ondc.org/ondc/subscribe` | `https://preprod.gateway.ondc.org/search` | This app's live NP env |
| **Production** | `https://prod.registry.ondc.org/subscribe` | `https://prod.gateway.ondc.org/search` | DNS TXT + portal; **blocked until GSTIN** |

Lookup (preferred): `https://preprod.registry.ondc.org/v2.0/lookup` /
`https://prod.registry.ondc.org/v2.0/lookup`. ONDC `/on_subscribe` public
encryption keys are env-specific — copy from Onboarding.md §6 (PreProd ≠ prod).

## Current participant identities

| Identity | Role | Key boundary |
| --- | --- | --- |
| `ondcbuyer.aadharcha.in` | Retail BAP | Existing **PreProd** portal pair (`uk_id` `1aee68ad-…`); do not regenerate or reuse as production |
| `ondcseller.aadharcha.in` | Retail ISN/BPP | Existing **PreProd** portal pair (`uk_id` `baf58086-…`); do not regenerate, reuse as production, or reuse for LOG10 |
| `ondclbnp.aadharcha.in` | LOG10 Buyer NP/LBNP/BAP | Existing **PreProd** portal pair (`uk_id` `9e7388f4-…`); do not regenerate or reuse as production |

**Production keys (2026-08-17):** operator authorized keys-only then
**Generate now** for all three FQDNs. Isolated local pairs exist under
`aadharchain/gateway/.local/ondc-production/{buyer,seller,lbnp}` (gitignored).
Never `--out` onto `ondc-sandbox/` or `portal-download/`. A portal 1.a modal
pair supersedes any local draft and must be reconciled before Submit. Local
generate does not register or submit. Do not copy into Render env or `.env`
production PEM vars.

### Production 1.a Raise Request modal

- Operator action is **Generate + Download**, then **Cancel not Submit**.
- `unique_key_id` is often **absent from `keys.json`** — capture it from the
  Raise Request modal UI. It appears **only after Generate**. Recapturing an
  empty modal would mint a new pair; do not click Generate unless authorized
  to supersede.
- Materialize to gitignored
  `.local/ondc-production-portal-modal/{buyer,seller,lbnp}`. Modal pair
  supersedes `.local/ondc-production/{role}` for later Submit; keep-both until
  human discard. Buyer 2026-08-17 no-ukid pair aside:
  `buyer-20260817-no-ukid`.
- Chrome names downloads `keys (N).json` (2026-08-17: Buyer `(5)` then regen
  `(8)`; Seller `(6)`; LBNP `(7)`). Map by fingerprint, not filename.

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
| Path | PreProd/staging: `aadharchain/gateway/.local/ondc-sandbox/{buyer,seller,lbnp}/` and `portal-download/{role}/`. Production drafts: `.local/ondc-production/{buyer,seller,lbnp}/`. Production modal pairs: `.local/ondc-production-portal-modal/{buyer,seller,lbnp}/`. |
| Gitignore | Nested `aadharchain/.gitignore`: `gateway/.local/` + `data/ondc-keys/`. Workspace also ignores `/aadharchain/` |
| Script default | `scripts/ondc_generate_keys.py` defaults to `data/ondc-keys/` — use `--out` for sandbox path |
| Private PEM mode | `0600`; `scripts/ondc_generate_keys.py` enforces this after each write and fails closed if group/other bits remain |
| Public metadata | Public keys and private-key paths only; private key bytes stay in the `0600` PEMs. `--self-test` blocks private material from `public_metadata.json`. |
| Encryption public | **`asn1_der_spki_b64`** (fixed 2026-07-12); `--convert-existing` supported |
| Wire | Configure only the intended identity after its endpoint gate. Do not change existing Retail env or `ONDC_ENABLED` from this key guide. |

## Map to this repo

| Concern | Owner |
| --- | --- |
| Ops ladder | `.session/docs/PRODUCTION-READINESS.md` A1–A4 and B1–B8 — PreProd identity is captured; production roles and keys follow the approved role/domain decision |
| Onboard hosting | `aadharchain/gateway/app/ondc_onboard_routes.py` — site-verification + `on_subscribe` + status. Retail uses Vercel rewrites; LBNP is the second custom domain on the existing Render gateway. |
| Protocol adapters | Retail signed traffic remains in its existing mapper; LOG10 requires its dedicated namespace/version mapping |
| Browser apps | Never hold ONDC private keys or Registry credentials |

## Portal download vs local DER (2026-07-12)

| Artifact | Path | Role |
| --- | --- | --- |
| Portal Buyer download | Operator: **`keys`** → `~/Downloads/keys.json` → `portal-download/buyer/` (+ PEMs) | PreProd Subscribed `uk_id` `1aee68ad-bc2a-4fc4-b233-7e14c6abba9b` |
| Portal Seller download | Operator: **`key1`** → `~/Downloads/keys (1).json` → `portal-download/seller/` (+ PEMs) | PreProd Subscribed `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9` |
| Portal LBNP download | Operator modal pair → `portal-download/lbnp/` | PreProd Subscribed `uk_id` `9e7388f4-c68e-4006-ac5a-e7517382999f` |
| Local official pairs | `.local/ondc-sandbox/{buyer,seller,lbnp}/` + `public_metadata.json` | Ed25519 + X25519 ASN.1 DER — **different** keypairs from portal; keep for optional Staging |
| Production drafts | `.local/ondc-production/{buyer,seller,lbnp}/` | Local generate-now 2026-08-17; not registered; keep-both until human discard |
| Production modal pairs | `.local/ondc-production-portal-modal/{buyer,seller,lbnp}/` | Raise Request Generate+Download; supersedes draft for later Submit |

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
  public-DNS status is owned by [`.session/checklist/checklist.json`](../../../../.session/checklist/checklist.json).
- Portal environment access, `1.b`, legal tasks, registry mutation, and
  production remain separate authorized gates. Local production draft pairs
  exist 2026-08-17; that does not include DNS, deploy, env copy, or submit.
