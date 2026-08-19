# GoDaddy — aadharcha.in (venture)

Venture: **Aadhar Chain**  
`ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3`

## Entry URLs

| Surface | URL |
| --- | --- |
| Venture dashboard | https://dashboard.godaddy.com/venture?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |
| Domain settings | https://dcc.godaddy.com/control/portfolio/aadharcha.in/settings?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |
| DNS | same + `?tab=dns` (or DNS tab in UI) |
| Email users | https://dashboard.godaddy.com/venture/email?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |

Browser owner: bundled `@chrome`. OTP/login → STOP.

## Domain

| Fact | Value |
| --- | --- |
| Domain | `aadharcha.in` |
| Expires | Oct 29, 2026 |
| Auto-renew | **Off** when last observed 2026-07-11; re-read before relying on it |
| Apex / www / app hosts | A → `76.76.21.21` (Vercel) for `@`, `www`, `ondcbuyer`, `ondcseller`, `flatwatch` |
| Gateway FQDN | `gateway.aadharcha.in` — CNAME → `identity-aadhar-gateway-main.onrender.com` (added 2026-07-12; Render Free custom domain + TLS) |
| ONDC Buyer FQDN | `ondcbuyer.aadharcha.in` — operator confirmed 2026-07-12; dig A `76.76.21.21`; HTTPS 200 Vite app |
| ONDC Seller FQDN | `ondcseller.aadharcha.in` — operator confirmed 2026-07-12; dig A `76.76.21.21`; HTTPS 200 Vite app |
| ONDC Logistics Buyer FQDN | `ondclbnp.aadharcha.in` — CNAME → `identity-aadhar-gateway-main.onrender.com` (added 2026-07-26, TTL 1 hour) after the exact Render target was verified; current readiness belongs to `.session/checklist/checklist.json`. |
| Nameservers (last observed 2026-07-11) | GoDaddy `ns73/74.domaincontrol.com` + NS1 `dns1–4.p06.nsone.net` (Vercel-style); re-read before editing |
| Retail live probe | 2026-07-12 — Buyer/Seller TLS OK. This does not prove the pending LBNP record or endpoint. |

DNS tabs present: Records, Forwarding, Nameservers, Hostnames, DNSSEC.  
Quick actions: Manage DNS, Forward Domain, Connect Email, Verify Domain Ownership.

## Email (needed for API Setu)

| Fact | Value |
| --- | --- |
| Mailbox | **`gurusharan.gupta@aadharcha.in`** (Gurusharan Gupta) |
| Extra seats | Often **0 accounts available** — Buy more before creating another user |
| Sign In | From Email page → opens webmail for that user |

API Setu **Official Domain's Email** → use this address; Verify Email OTP → agent STOP.

## Not the production site builder

Venture also has a free GoDaddy site `aadharchain.godaddysites.com` (published). Portfolio production hosts are the DNS A records above (Render/Vercel), not that free builder — do not conflate.

## Agent rules

1. Prefer existing mailbox over buying seats unless operator asks.  
2. GoDaddy is DNS only. Verify the application-hosting target first; then make
   the one approved record change and capture before/after plus public DNS/TLS
   readback.
3. Never store GoDaddy passwords in repo.  
4. Upsells (`aadharchain.in`, `.xyz`, domain protection) are optional — ignore unless asked.
