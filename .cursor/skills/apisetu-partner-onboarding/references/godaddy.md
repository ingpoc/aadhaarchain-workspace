# GoDaddy — aadharcha.in (venture)

Validated via Hermes Chrome WIP on Comet (2026-07-11).  
Venture: **Aadhar Chain**  
`ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3`

## Entry URLs

| Surface | URL |
| --- | --- |
| Venture dashboard | https://dashboard.godaddy.com/venture?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |
| Domain settings | https://dcc.godaddy.com/control/portfolio/aadharcha.in/settings?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |
| DNS | same + `?tab=dns` (or DNS tab in UI) |
| Email users | https://dashboard.godaddy.com/venture/email?ventureId=5f74c5ac-83e6-433b-a6ee-7b497c3a65f3 |

Browser: **WIP Hermes on Comet** (logged-in GoDaddy session). Not Cursor IDE browser. OTP/login → STOP.

## Domain

| Fact | Value |
| --- | --- |
| Domain | `aadharcha.in` |
| Expires | Oct 29, 2026 |
| Auto-renew | **Off** (operator decision) |
| Apex / www / app hosts | A → `76.76.21.21` (Vercel-style) for `@`, `www`, `ondcbuyer`, `ondcseller`, `flatwatch` |

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
2. DNS edits for ONDC/TLS only with explicit operator ask; record before/after.  
3. Never store GoDaddy passwords in repo.  
4. Upsells (`aadharchain.in`, `.xyz`, domain protection) are optional — ignore unless asked.
