# ONDC Participant Portal — field map

Discovered / updated 2026-07-12 via Hermes WIP session `ondc-portal-onboard`.

## URLs

| Surface | URL |
| --- | --- |
| Signup | https://portal.ondc.org/sign-up |
| Login | https://portal.ondc.org / login |
| Post-signup home / integrations | https://portal.ondc.org/integration-create-plan |
| Manage Business Info (profile) | https://portal.ondc.org/profile |
| Declarations and KYC | https://portal.ondc.org/declarations (locked until network status advances) |
| Maintenance note (seen) | Portal downtime **13 Jul 2026 16:00–22:00** IST |

## Post-signup status (2026-07-12 afternoon) — **account exists**

| Item | Observed |
| --- | --- |
| Logged in | Yes — header user `Gurusharan Gupta Gupta` |
| Org ID | `15462` |
| Org name | `GURUSHARAN GUPTA HUF` |
| Org / integration status | **Integration in Progress** (Buyer); Seller **Initiated Integration** |
| Domain + role | Retail (B2C) API v **1.2** · Buyer NP + Seller NP **ISN** |
| Business profile IDs | Buyer `15462 - 10008` Continue; Seller `15462 - 10011` Continue |
| Buyer EnvAccessRequest | **Pre-Prod Subscribed** for `ondcbuyer.aadharcha.in` (2026-07-12 operator) |
| Seller EnvAccessRequest | **Pre-Prod Subscribed** for `ondcseller.aadharcha.in` (2026-07-12 02:44 PM agent; `uk_id` `baf58086-7024-438a-becf-4cfa056ec8d9`) |
| Profile % | **No numeric %** in UI; KYC incomplete (GSTIN empty, PAN name/upload empty, consent unchecked) |
| Website (profile field) | `https://ondcbuyer.aadharcha.in` |
| **Buyer FQDN (confirmed)** | `ondcbuyer.aadharcha.in` — operator 2026-07-12; DNS+TLS live (Vercel) |
| **Seller FQDN (confirmed)** | `ondcseller.aadharcha.in` — operator 2026-07-12; DNS+TLS live (Vercel) |
| PAN | `AAJHG6948N` (present) |
| Declarations | Blocked until status is Integration in Progress / Advanced / Live |
| Live network | **No** — do not claim; keep `VITE_COMMERCE_DEMO_MODE` |

**Policy:** staging/sandbox Buyer+Seller first ([`ondc-sandbox-keys.md`](ondc-sandbox-keys.md)); **prod only after GSTIN**. Keys = local Ed25519/X25519 + staging `/subscribe`, not portal “generate & download”.

Evidence: `references/evidence/ondc-postsignup-*-20260712.jpeg`, `ondc-sandbox-*-20260712.jpeg`, `ondc-portal-operator-submit-window-20260712.jpeg`, `ondc-postsubmit-*-20260712.jpeg`. Ledger same date. Auth0: [`../authentication/SKILL.md`](../authentication/SKILL.md).

## Wizard structure (signup — historical)

SPA keeps **all steps in DOM** (horizontal/off-screen panels). Step indicator classes: `.step.completed` / `.step.active` / `.step.inactive`.

| Wizard step | Substeps | Title cues |
| --- | --- | --- |
| 1 Business Profile | 1/2 domain → 2/2 role | "Define your ONDC business profile" |
| 2 Organisation Details | form | "Tell us about your organisation" |
| 3 User Details | form | (first_name input present in DOM early) |

**Continue / Previous:** many duplicates in DOM. Use a semantic role locator scoped with `within`, `visible`, `exact`, or `nth` to the panel containing the active title.

**Get Started:** use an exact visible role locator for the button. Do not call DOM `.click()` through `evaluate`.

## Business Profile — domain (1/2)

| Control | Selector / note |
| --- | --- |
| Retail | `#Retail1` (preferred) |
| Other domains | Logistics, Travel, Financial Services, Mobility, Agriculture, ONEST, Services, Other |

## Business Profile — role (2/2) Retail

| Role | Radio id | Prefer |
| --- | --- | --- |
| Buyer NP | `#1` | **Yes** (done — profile `15462-10008`) |
| Seller NP - Marketplace Seller Node (MSN) | `#2` | only if marketplace-node |
| Seller NP - Inventory Seller Node (ISN) | `#3` | **default** for AgentGuard inventory seller (Add another) |
| Sell via an existing ONDC Marketplace | `#8` | no |
| TSP - Buyer | `#4` | no (unless TSP path) |
| TSP - Seller | `#5` | no |

Portal may log React warning: `RadioboxInput` `id` number vs string — ignore; label click still works.

## Organisation Details (signup — operator-filled)

| Label | Required | Confirmed fill (operator 2026-07-12) |
| --- | --- | --- |
| Name of your organisation | * | `GURUSHARAN GUPTA HUF` |
| Website URL | * | Signup used `https://ondcbuyer.aadharchain.in` (typo); **authoritative** `https://ondcbuyer.aadharcha.in` + Seller `https://ondcseller.aadharcha.in` (operator 2026-07-12) |
| Legal Entity Name | * | `GURUSHARAN GUPTA HUF` |
| Registered Address for | | INDIA |
| Billing/Street/Area | * | `J-702 Marvel Fria,` |
| Locality/Town | * | `Wagholi` |
| City/District | * | `Pune` |
| Pin Code | * | `412207` |
| State | * | Maharashtra (`#react-select-2-input` / `state_id`) |
| PAN for Organisation | * | `AAJHG6948N` (HUF) |

Admin checkbox (later step / user): `#EditableYes` — "Add this user as Administrator…"

Same HUF entity as GST Part A — see [`gstin-huf.md`](gstin-huf.md). **GST Part B = operator/CA** (agent fill paused). Portal KYC GSTIN upload waits on CA GSTIN.

## User Details (signup completed by operator)

Password / OTP were hard-stops for agents — operator completed signup. Account live as above.

## Hermes session

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
# reuse session
python3 -c "import sys; sys.path.insert(0,'scripts'); from portfolio_browser import hermes_run; ..."
# session='ondc-portal-onboard'
# GST companion: session='gst-huf-check' — idle / CA-owned; do not agent-fill
```
