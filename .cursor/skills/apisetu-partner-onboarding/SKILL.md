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
Browser driver only: [portfolio-browser](../portfolio-browser/SKILL.md) (Hermes Chrome WIP).
Ops ladder: [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md) § A5–A8, C3.
Deploy / CI: [portfolio-deploy](../portfolio-deploy/SKILL.md). Auth0: [authentication](../authentication/SKILL.md).

**Standing rule:** append durable portal/GST/FQDN findings to this skill + [`references/ondc-portal-ledger.md`](references/ondc-portal-ledger.md); **no secrets** in markdown.

**Do not** claim **production** ONDC or flip `VITE_COMMERCE_DEMO_MODE` without gate evidence.
**PreProd Beckn search is live** (BAP+BPP) — see [ondc-testing preprod-network-matrix](../ondc-testing/references/preprod-network-matrix.md). That is **not** “live prod network orders.”

## Rails

| Rail | Status | Gate |
| --- | --- | --- |
| **ONDC Participant Portal** | Org **15462**; Buyer `15462-10008` + Seller ISN `15462-10011` — both **PreProd Subscribed** | uk_ids Buyer `1aee68ad-…` / Seller `baf58086-…`. Portal **1.b** attestation = operator. **Prod only after GSTIN** |
| **ONDC PreProd protocol** | **BAP+BPP live** on gateway commit **`1ba0a0c`+** (`ONDC_ENABLED`) | search + **select/init/confirm** ACK wired. Buyer may see `ondcseller.aadharcha.in` (Atta); fanout variance OK. **Not** prod / live UPI |
| **GST HUF** | Part A done — TRN `272600333290TRN`; Part B due **26/07/2026** | **CA completes Part B** → GSTIN. Agent fill **paused** |
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

## Policy (2026-07-12)

| Do | Do not |
| --- | --- |
| Match registry env to portal ACK (**PreProd**) | Assume Staging just because docs prefer it |
| Keep portal PEMs on Render; set `ONDC_ENABLED` + BAP/BPP URIs for PreProd test | Blind re-POST `/subscribe` after portal already Subscribed |
| Keep `VITE_COMMERCE_DEMO_MODE=false` after gate (PreProd); honest “payment simulated” | Claim **prod** network / live UPI / paid orders |
| Encode friction in this skill + ondc-testing matrix | Invent FQDNs — hosts are operator-confirmed |
| Leave portal 1.b checkbox to operator | Agent-attest build readiness |

**Keys owner doc:** [`references/ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md). Ladder: [`ondc-sandbox-integration-ladder.md`](references/ondc-sandbox-integration-ladder.md).

## Next actions (operator vs agent)

| # | Who | Action |
| --- | --- | --- |
| 1 | — | ~~FQDNs / ISN / PreProd 1.a / keys / onboard routes / BAP+BPP PreProd search~~ **Done** 2026-07-12 |
| 2 | **Agent** | ~~select/init/confirm + demo mode off~~ **Done** 2026-07-12 evening; tighten fanout reliability; deepen Buyer UI checkout beyond API ACK |
| 3 | **Operator** | Buyer + Seller **1.b** attestation when ready |
| 4 | **After GSTIN (CA)** | Portal KYC → prod registry |
| 5 | **Token Nxt** | Apply by **15 Jul 2026** — [npci.org.in/token-nxt](https://www.npci.org.in/token-nxt). Use the [curated answers](references/token-nxt-curated-answers.md) and [application form inventory](references/token-nxt-application-form.md). **Demo video Q33:** gated pipeline → [demo-video-recording](../demo-video-recording/SKILL.md) (access → script → dry-run Pass → record). Script/matrix: [demo script](references/token-nxt-demo-script.md) / [step matrix](references/token-nxt-demo-step-matrix.md) |

## Prerequisites (Hermes)

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
python3 scripts/portfolio_browser.py preflight   # if bridge down
```

- WIP socket only (never `~/.codex` / `~/.hermes` live).
- Sessions: `ondc-portal-onboard` (portal); `gst-huf-check` (GST idle / CA — do not destroy ONDC tab).
- Actions: `goto`, `wait` (`ms`), semantic `locator`, `screenshot`, and `page_context`. Use `testId` (camel case) for `by: "testid"`.
- SPA duplicates: scope a semantic locator with `within`, `visible`, `exact`, or `nth`; use read-only `evaluate` only for diagnosis. Never click, fill, or dispatch events through `evaluate`.
- Ignore `page_diag` noise from google-analytics / Vite HMR.

## Known non-secret values

| Field | Value | Source |
| --- | --- | --- |
| Org / legal name | `GURUSHARAN GUPTA HUF` | Portal 2026-07-12 |
| ONDC org ID | `15462` | Portal |
| Buyer profile | `15462-10008` Retail (B2C) API v1.2 Buyer NP | Integrations |
| Website (signup) | `ondcbuyer.aadharchain.in` | Org form (typo domain — do not use) |
| **Buyer FQDN / subscriber_id** | **`ondcbuyer.aadharcha.in`** | **Operator confirmed 2026-07-12**; profile field; DNS A `76.76.21.21` (Vercel); HTTPS 200 app |
| **Seller FQDN / subscriber_id** | **`ondcseller.aadharcha.in`** | **Operator confirmed 2026-07-12**; DNS A `76.76.21.21` (Vercel); HTTPS 200 app |
| Domain (GoDaddy) | `aadharcha.in` | [`godaddy.md`](references/godaddy.md) — apex/`www`/`ondcbuyer`/`ondcseller`/`flatwatch` → Vercel |
| Address | J-702 Marvel Fria, Wagholi, Pune, Maharashtra **412207** | Org form |
| Org PAN | `AAJHG6948N` | Org form (HUF) |
| ONDC user email | `gurusharan.gupta@aadharcha.in` | User / GoDaddy |
| GST TRN | `272600333290TRN` | gstin-huf.md |
| GST Part A email | `gupta.huf.gurusharan@gmail.com` | gstin-huf.md |
| KYC gaps | GSTIN empty; PAN upload; area of operation; etc. | Profile |
| Seller NP | **`15462-10011`** Retail ISN — Integration in Progress; **1.a PreProd Subscribed** | Portal 2026-07-12 |
| Seller role | **ISN** (Inventory Seller Node) | Portal Add another — done |
| TLS termination | **Vercel** (HSTS present; `server: Vercel`) | Live probe 2026-07-12 |
| Prod hosts | Same FQDNs unless operator changes; PRODUCTION-READINESS A7 example `buyer.aadharcha.in` is **superseded** for staging/prod by confirmed hosts above | Operator |

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

1. Reuse session `ondc-portal-onboard` → https://portal.ondc.org (already logged in).
2. Buyer `15462-10008` — EnvAccessRequest **Pre-Prod Subscribed** for `ondcbuyer.aadharcha.in`. Next: **1.b** (Pending — operator only).
3. Seller `15462-10011` **ISN** — EnvAccessRequest **Pre-Prod Subscribed** for `ondcseller.aadharcha.in` (12/07/2026 02:44 PM; portal `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9`). Next: **1.b** (Pending — operator only). Keys/hosting: [`ondc-sandbox-keys.md`](references/ondc-sandbox-keys.md). Ladder: [`ondc-sandbox-integration-ladder.md`](references/ondc-sandbox-integration-ladder.md).
4. Mid-form hard-stop → leave tab open; skip closeout. Safe idle → `python3 scripts/portfolio_browser.py closeout`.

**Hard stops:** password / captcha / OTP; Approve / legal attestations; inventing alternate FQDNs; treating portal key download as subscribe keypairs; portal maintenance **13 Jul 2026 ~16:00–22:00 IST**.

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
| `references/evidence/staging-subscribe-drafts-20260712.json` | Draft subscribe bodies (do not POST until env confirmed) |
| Earlier dated ONDC sandbox captures in `references/evidence/` | Seller Add / ISN / Buyer journey earlier |

- Ledger (append-only): [`references/ondc-portal-ledger.md`](references/ondc-portal-ledger.md)
- Browser driver → [portfolio-browser](../portfolio-browser/SKILL.md) (cursor opacity / SW Inactive / wrong-app traps)
- Demo video (Token Nxt Q33 / PreProd walkthrough) → [demo-video-recording](../demo-video-recording/SKILL.md)
- Auth0 / gateway session → [authentication](../authentication/SKILL.md)
- Deploy / CI/CD / Free-Hobby → [portfolio-deploy](../portfolio-deploy/SKILL.md)
- Buyer/Seller UX matrix → [ondc-testing](../ondc-testing/SKILL.md)
- Ops → [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md)
- WIP Hermes → `/Users/gurusharan/plugins/hermes-chrome-cursor-wip/skill/SKILL.md`
