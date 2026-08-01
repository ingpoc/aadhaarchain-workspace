---
name: apisetu-partner-onboarding
description: >-
  Operate ONDC participant onboarding, PreProd subscription evidence, GST HUF
  handoffs, optional Setu eKYC, and paused MeitY/API Setu rails. Use when the
  operator asks about ONDC portal profiles, subscriber IDs, registry keys,
  GSTIN readiness, Token Nxt application evidence, Setu, DigiLocker, or API
  Setu. Triggers: ONDC onboarding, participant portal, GST HUF, subscriber_id,
  PreProd subscribed, Token Nxt, Setu eKYC, MeitY, DigiLocker.
---

# Partner onboarding

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

Durable owner for multi-rail partner onboarding (ONDC + GST companion + Setu + MeitY paused).
Browser UI owner: bundled `@chrome`. [portfolio-browser](../portfolio-browser/SKILL.md) is legacy deterministic replay/diagnosis only.
Ops ladder: [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md) § A5–A8, C3.
Deploy / CI: [portfolio-deploy](../portfolio-deploy/SKILL.md). Auth0: [authentication](../authentication/SKILL.md).

**Standing rule:** append durable portal/GST/FQDN findings to this skill + [`references/ondc-portal-ledger.md`](references/ondc-portal-ledger.md); **no secrets** in markdown.

**Do not** claim **production** ONDC or flip `VITE_COMMERCE_DEMO_MODE` without gate evidence.
**PreProd Beckn search is live** (BAP+BPP) — see [ondc-testing preprod-network-matrix](../ondc-testing/references/preprod-network-matrix.md). That is **not** “live prod network orders.”

## Rails

| Rail | Status | Gate |
| --- | --- | --- |
| **ONDC Participant Portal** | Org **15462**; Buyer `15462-10008` + Seller ISN `15462-10011` — both **PreProd Subscribed** | uk_ids Buyer `1aee68ad-…` / Seller `baf58086-…`. Portal **1.b** attestation = operator. **Prod only after GSTIN** |
| **ONDC Retail PreProd protocol** | BAP+BPP foundation exists; current signed-search result is owned by the PreProd matrix | Gate 1 passed with the approved atta. Do not infer later lifecycle, payment, conformance, or production. |
| **ONDC Logistics Buyer/LBNP** | Profile `15462-10220`; dedicated subscriber **`ondclbnp.aadharcha.in`** is PreProd `SUBSCRIBED` as `ONDC:LOG10` BAP with the latest portal pair | Portal 1.a and operator-completed 1.b are Completed. Official Workbench session `PafpxsF3NAoH3p1uvcHzr152Ec_j3pmT` completed all 15 Immediate Delivery forward-flow steps after explicit operator authorization for the synthetic confirm terms. |
| **GST HUF** | Part A done; Part B is CA-owned | GSTIN remains the production gate. Agent form fill is paused; current status belongs in `gstin-huf.md`. |
| **Setu.co eKYC** | Optional | Not required for AgentGuard M0–7 |
| **MeitY DigiLocker / API Setu** | **PAUSED** | Resume only on explicit operator ask |
| **UPI Circle / agent pay** | Human Circle live; AI/software profiles **CUG pilot only** | No public “onboard AgentGuard as UPI secondary” — AgentGuard stays authority layer |

### Staging vs PreProd (do not conflate)

| Env | Registry subscribe | Portal UI (2026-07-12 inspect) |
| --- | --- | --- |
| **Staging** | `https://staging.registry.ondc.org/subscribe` | Optional; local DER keypairs only if deliberately opening Staging |
| **Pre-Prod** | `https://preprod.registry.ondc.org/ondc/subscribe` | Buyer + Seller **Subscribed**; Grocery `ONDC:RET10`; URIs `/ondc` on FQDNs |
| **Production** | `https://prod.registry.ondc.org/subscribe` | **Blocked until GSTIN (CA)** |

**Keys:** Downloads **`keys`/`keys.json` = Buyer**, **`key1`/`keys (1).json` = Seller** → gitignored `portal-download/{buyer,seller}/`. PreProd `/on_subscribe` + signed search use **portal** PEMs on Render (`ONDC_*_PEM_B64`). Details: [`ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md). Auth0: [authentication](../authentication/SKILL.md).

## Standing policy

| Do | Do not |
| --- | --- |
| Match registry env to portal ACK (**PreProd**) | Assume Staging just because docs prefer it |
| Keep portal PEMs on Render; set `ONDC_ENABLED` + BAP/BPP URIs for PreProd test | Blind re-POST `/subscribe` after portal already Subscribed |
| Keep `VITE_COMMERCE_DEMO_MODE=false` after gate (PreProd); honest “payment simulated” | Claim **prod** network / live UPI / paid orders |
| Encode friction in this skill + ondc-testing matrix | Invent FQDNs — hosts are operator-confirmed |
| Leave portal 1.b checkbox to operator | Agent-attest build readiness |
| Derive each Workbench action from signed callback/session readback | Treat an `activeFlow` label as expectation proof |
| Submit the official Workbench input schema and send within its five-minute expectation | Auto-set `accept_bpp_terms` or another legal-semantic field |

**Keys owner doc:** [`references/ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md). Ladder: [`ondc-sandbox-integration-ladder.md`](references/ondc-sandbox-integration-ladder.md).

### Operator handoff tab lifecycle

Finalize hard-stop operator tabs with `status: "handoff"`. Login, password,
OTP/MFA, CAPTCHA, one-time key download, 1.b attestation, legal acceptance,
and unresolved operator-decision stops make the exact positioned tab part of
the deliverable. After verifying its visible label and location, call
`browser.tabs.finalize({ keep: [{ tab, status: "handoff" }] })` as the final
Chrome action of the turn; do not close, omit, navigate, or call another Chrome
tool afterward. A later turn must rediscover the exact returned user tab before
claiming it. Disposable research, duplicate, blank, and error tabs remain
eligible for normal cleanup.

### LOG10 dedicated-identity rule (2026-07-26)

- Portal readback proved that reusing `ondcseller.aadharcha.in` resolves to its
  existing Retail Seller/ISN record; `Domain Addition` does not provide the
  required Logistics Buyer role. Do not submit that path or change the Seller.
- Use `ondclbnp.aadharcha.in` for profile `15462-10220`, callback base
  `https://ondclbnp.aadharcha.in/ondc`, `ONDC:LOG10` Buyer NP/LBNP/BAP.
  External LSPs remain BPPs; AadhaarChain does not claim fleet ownership.
- Reuse the existing Render gateway directly: deploy the exact verified commit,
  attach its second custom domain, and verify the target before adding the one
  approved GoDaddy CNAME. Then prove public DNS, TLS, site-verification, and
  `/ondc/on_subscribe` before resuming portal environment access. GoDaddy is
  DNS only; do not create a Vercel edge or another runtime.
- Generate a distinct signing/encryption keypair through the existing
  gitignored workflow. Private PEMs must be `0600`; the generator must fail if
  broader permissions survive. Never reuse Retail Buyer/Seller keys or expose
  secrets.
- Portal 1.a exposes only `Click to generate & download below Key`; treat each
  occurrence as operator-only. `Raise Request` opens a second modal with its
  own key control, so the modal's latest generated/downloaded pair supersedes
  the outer draft pair. Reconcile its public fingerprints and key ID against
  the LBNP endpoint before enabling operator Submit; never submit a stale pair.
- Target `1.2.5`; accept `1.2.0` only when the selected LSP advertises it.
  Never route LOG10 through the Retail `1.2.0` mapper.
- The portal banner says ONDC Protocol Workbench replaces Pramaan for protocol
  testing, compliance validation, and reports. Treat that as later
  build-verification tooling, not as a 1.a registration warning or permission
  to start protocol/conformance work.

### Workbench conformance rule (2026-07-31)

- Use one active flow and one transaction. `activeFlow` persists before the
  incoming action, while `flowMap` stays empty until Workbench receives it; use
  the visible listening state or official session readback as the start proof.
- A Workbench action expectation lasts five minutes. Complete the visible input
  form first and send the signed action immediately; do not diagnose an expired
  expectation as an AadhaarChain transaction-ID defect.
- After each BAP action, read the current step. `INPUT-REQUIRED` means submit
  Workbench's schema before expecting its mock callback. In the Immediate
  Delivery flow, the `on_search` feature flags are optional and may remain
  empty; do not invent advertised LSP features.
- Build `init` from the signed `on_search`. Preserve the official P2P
  `linked_provider` fulfillment tag; omitting the tags array makes the current
  Workbench `on_init` generator fail before callback delivery.
- Derive `confirm` only from the signed `on_init` and Workbench payload
  readback. If the official confirm contract requires
  `bap_terms/accept_bpp_terms=yes`, stop for explicit operator authorization;
  conformance authorization alone is not legal acceptance.
- Treat tags as action-specific. Preserve signed identifiers and values, but
  validate each outbound action before dispatch: `rider_check` is required in
  this Workbench `on_init` fixture and invalid in `confirm`, so it must not be
  copied forward blindly.
- An `INPUT-REQUIRED` step with an empty input array still needs exactly one
  official `flow/proceed` call with empty inputs. Verify the resulting callback
  before proceeding again; do not skip or double-trigger it.
- Keep the exact portal and Workbench tabs as handoff deliverables at any
  login, key, attestation, legal, or unresolved operator boundary.

## Current state owner

Use [`.voice/progress.md`](../../../.voice/progress.md) and the
[PreProd network matrix](../ondc-testing/references/preprod-network-matrix.md)
for current gate status. This skill owns portal, identity, key, and hard-stop
rules; it does not maintain a second execution queue.

## Known non-secret values

| Field | Value | Source |
| --- | --- | --- |
| Org / legal name | `GURUSHARAN GUPTA HUF` | Portal 2026-07-12 |
| ONDC org ID | `15462` | Portal |
| Buyer profile | `15462-10008` Retail (B2C) API v1.2 Buyer NP | Integrations |
| Website (signup) | `ondcbuyer.aadharchain.in` | Org form (typo domain — do not use) |
| **Buyer FQDN / subscriber_id** | **`ondcbuyer.aadharcha.in`** | **Operator confirmed 2026-07-12**; profile field; DNS A `76.76.21.21` (Vercel); HTTPS 200 app |
| **Seller FQDN / subscriber_id** | **`ondcseller.aadharcha.in`** | **Operator confirmed 2026-07-12**; DNS A `76.76.21.21` (Vercel); HTTPS 200 app |
| **Logistics profile** | **`15462-10220`** Logistics (B2C) Buyer NP | Portal 1.a/1.b completed; PreProd registry `SUBSCRIBED` |
| **Logistics LBNP FQDN / subscriber_id** | **`ondclbnp.aadharcha.in`** | Public DNS/TLS/site-verification/`on_subscribe` passed; official Workbench Gate 3 passed 2026-08-01 |
| Domain (GoDaddy) | `aadharcha.in` | [`godaddy.md`](references/godaddy.md) — apex/`www`/`ondcbuyer`/`ondcseller`/`flatwatch` → Vercel |
| Address | J-702 Marvel Fria, Wagholi, Pune, Maharashtra **412207** | Org form |
| Org PAN | `AAJHG6948N` | Org form (HUF) |
| ONDC user email | `gurusharan.gupta@aadharcha.in` | User / GoDaddy |
| GST TRN | `272600333290TRN` | gstin-huf.md |
| GST Part A email | `gupta.huf.gurusharan@gmail.com` | gstin-huf.md |
| KYC gaps | GSTIN empty; PAN upload; area of operation; etc. | Profile |
| Seller NP | **`15462-10011`** Retail ISN; business profile last read `Integration in Progress`, while PreProd environment **1.a is Subscribed** | Portal 2026-07-12 |
| Seller role | **ISN** (Inventory Seller Node) | Portal Add another — done |
| TLS termination | **Vercel** (HSTS present; `server: Vercel`) | Live probe 2026-07-12 |
| Host boundary | Retail remains on `ondcbuyer` / `ondcseller`; LOG10 uses the separate `ondclbnp` subscriber. Production remains blocked until its own gate evidence. | Operator + ledger |

## Reference map

| Doc | Owns |
| --- | --- |
| [`references/ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md) | Official key/onboarding process, staging URLs, checklists, local key path |
| [`references/ondc-sandbox-integration-ladder.md`](references/ondc-sandbox-integration-ladder.md) | Code → local smoke → deploy → web ladder; local vs FQDN test verdict; deploy targets |
| [`references/ondc-portal.md`](references/ondc-portal.md) | Portal field map, SPA click notes, post-signup status |
| [`references/ondc-portal-ledger.md`](references/ondc-portal-ledger.md) | Append-only session history |
| [`references/gstin-huf.md`](references/gstin-huf.md) | HUF GST Part A/B; CA path; TRN |
| [`references/godaddy.md`](references/godaddy.md) | `aadharcha.in` DNS / email |

Signup wizard steps / hard-stops / React fill helper: [`ondc-portal.md`](references/ondc-portal.md). Append every portal session to the ledger.

## ONDC portal — short workflow

1. Open the existing authenticated ONDC portal tab through bundled `@chrome`;
   never guess a tab ID.
2. Buyer `15462-10008` — EnvAccessRequest **Pre-Prod Subscribed** for `ondcbuyer.aadharcha.in`. Next: **1.b** (Pending — operator only).
3. Seller `15462-10011` **ISN** — EnvAccessRequest **Pre-Prod Subscribed** for `ondcseller.aadharcha.in` (12/07/2026 02:44 PM; portal `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9`). Next: **1.b** (Pending — operator only). Keys/hosting: [`ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md). Ladder: [`ondc-sandbox-integration-ladder.md`](references/ondc-sandbox-integration-ladder.md).
4. Logistics `15462-10220` — portal 1.a and operator-completed 1.b persisted
   Completed, and the PreProd
   registry returned `SUBSCRIBED` for `ondclbnp.aadharcha.in`,
   `ONDC:LOG10`, BAP, `/ondc`, all cities, and the deployed key ID. Do not
   repeat Submit. The bounded Immediate Delivery Workbench flow is complete;
   do not repeat it or infer report, certification, production, payment, or
   real-shipment status.
5. At a hard stop, leave the portal tab open for the operator.

**Hard stops:** password / captcha / OTP; Approve / legal attestations; changing
the existing Retail Seller registration; Logistics `Domain Addition`; treating
portal key download as subscribe keypairs.

## GST HUF — CA-owned (agent paused)

Agent does **not** fill `reg.gst.gov.in` Part B. Operator + CA complete Part B → GSTIN. Then upload cert to ONDC KYC (A5). Until then: record status if asked; no form drive. Details: [`gstin-huf.md`](references/gstin-huf.md).

GSTIN blocks **prod** only — not staging sandbox key work.

## Setu.co eKYC (optional)

```bash
# aadharchain/gateway/.env (never commit)
SETU_EKYC_ENABLED=true
SETU_EKYC_BASE_URL=https://dg-sandbox.setu.co
SETU_EKYC_CLIENT_ID=<test client id>
SETU_EKYC_CLIENT_SECRET=<test client secret>
SETU_EKYC_PRODUCT_INSTANCE_ID=3c0e3c28-164f-4fb7-9c98-fcb4ccc5011e
```

Code: `aadharchain/gateway/app/setu_ekyc.py`. Local demo fixtures remain valid without Setu.

## MeitY DigiLocker / API Setu (paused)

**Paused 2026-07-11.** Do not drive `partners.apisetu.gov.in` unless operator resumes. Hard stops when resumed: MeriPehchaan OTP, Verify Email OTP, org secrets/legal docs.

## Evidence / Related

| Evidence (cite these — they exist) | Shows |
| --- | --- |
| `references/evidence/fqdn-buyer-live-20260712.jpeg` / `fqdn-seller-live-20260712.jpeg` | FQDNs live on Vercel |
| `references/evidence/ondc-portal-operator-submit-window-20260712.jpeg` | Buyer PreProd **Subscribed** + portal key UI |
| `references/evidence/ondc-seller-1a-subscribed-20260712.jpeg` | Seller PreProd **Subscribed** + portal key UI (`ondcseller.aadharcha.in`) |
| `references/evidence/ondc-postsubmit-buyer-journey-20260712.jpeg` | Org 15462; Buyer `10008` Integration in Progress; Seller `10011` ISN |
| `references/evidence/ondc-postsubmit-keys-ui-20260712.jpeg` / `ondc-postsubmit-integrations-20260712.jpeg` | Post-submit journey (portal-rescan) |
| `references/evidence/staging-whitelist-email-template-20260712.md` | Staging email fallback if PreProd ≠ Staging |
| `references/evidence/staging-subscribe-drafts-20260712.json` | Historical draft bodies only; not an active POST instruction |
| Earlier dated ONDC sandbox captures in `references/evidence/` | Seller Add / ISN / Buyer journey earlier |

- Ledger (append-only): [`references/ondc-portal-ledger.md`](references/ondc-portal-ledger.md)
- Browser driver → [portfolio-browser](../portfolio-browser/SKILL.md) (cursor opacity / SW Inactive / wrong-app traps)
- Demo video (Token Nxt Q33 / PreProd walkthrough) → [demo-video-recording](../demo-video-recording/SKILL.md)
- Auth0 / gateway session → [authentication](../authentication/SKILL.md)
- Deploy / CI/CD / Free-Hobby → [portfolio-deploy](../portfolio-deploy/SKILL.md)
- Buyer/Seller UX matrix → [ondc-testing](../ondc-testing/SKILL.md)
- Ops → [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md)
- Historical Token Nxt application material → [curated answers](references/token-nxt-curated-answers.md) (not an active submission instruction)
