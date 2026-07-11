# GSTIN for Gurusharan Gupta HUF

Official apply (free): https://www.gst.gov.in → REGISTER → https://reg.gst.gov.in/registration/  
Guide context: GimBooks blog is explanatory only — **file on gst.gov.in**, not third-party paid portals.

## Entity

| Field | Value |
| --- | --- |
| Constitution | **HUF** (Part B — Business Details) |
| Legal name (as on PAN) | **GURUSHARAN GUPTA HUF** |
| HUF PAN | Operator-provided (4th char **H**) |
| Formation date (PAN) | 24/08/2024 |
| Part A type | **Taxpayer** (`APLRG`) |
| Email for GST Part A | Operator choice — **not** required to be `@aadharcha.in` (API Setu uses domain email separately) |
| Part A snapshot (2026-07-11) | Taxpayer; Maharashtra / Pune; legal name + HUF PAN match card; email `gupta.huf.gurusharan@gmail.com`; mobile on form |
| **TRN** | **`272600333290TRN`** — Part B due by **26/07/2026** |
| Resume | `reg.gst.gov.in/registration/` → Temporary Reference Number (TRN) → enter TRN + captcha |

## HUF documents (Part B)

- HUF PAN card  
- Karta PAN + Aadhaar + photo  
- HUF declaration / affidavit (Karta)  
- Principal place of business address proof  
- Bank proof (HUF / “as Karta of HUF” account)  
- Aadhaar OTP auth for Karta (or DSC/EVC)

## Agent workflow (WIP Comet)

1. Open `https://reg.gst.gov.in/registration/`  
2. Part A: Taxpayer + legal name + HUF PAN + email + **State/District** + mobile + captcha  
3. **STOP** before PROCEED — email OTP + mobile OTP + captcha  
4. After TRN: Part B → constitution **HUF**, upload docs, Aadhaar auth  
5. Track ARN on portal until GSTIN issued (often 3–7+ working days)

Never invent State/District/mobile. Never store captcha/OTP. Do not commit PAN images to git.

## WIP session note (2026-07-11)

Part A prefilled in Comet: Taxpayer, legal name, PAN, email. Left open with `keepWindow`. Awaiting State, District, mobile, captcha → operator OTP.
