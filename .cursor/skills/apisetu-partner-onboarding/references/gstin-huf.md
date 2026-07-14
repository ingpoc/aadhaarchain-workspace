# GSTIN for Gurusharan Gupta HUF

Official apply (free): https://www.gst.gov.in → REGISTER → https://reg.gst.gov.in/registration/  
Guide context: GimBooks blog is explanatory only — **file on gst.gov.in**, not third-party paid portals.

## Entity

| Field | Value |
| --- | --- |
| Constitution | **HUF** (Part B — Business Details) |
| Legal name (as on PAN) | **GURUSHARAN GUPTA HUF** |
| HUF PAN | **`AAJHG6948N`** (4th char **H** = HUF) |
| Formation date (PAN) | 24/08/2024 |
| Part A type | **Taxpayer** (`APLRG`) |
| Email for GST Part A | `gupta.huf.gurusharan@gmail.com` (not required to be `@aadharcha.in`) |
| Principal place (Part A / ONDC match) | J-702 Marvel Fria, Wagholi, Pune, Maharashtra **412207** — INDIA |
| Part A snapshot | Taxpayer; Maharashtra / Pune; legal name + HUF PAN match; email above; mobile on form |
| **Status** | **Part A done. Part B = operator / CA-owned** — agent fill **paused** 2026-07-12 (not agent-driven) |
| **TRN** | **`272600333290TRN`** — Part B due by **26/07/2026** |
| ARN / GSTIN | Not yet — CA/operator files Part B → GSTIN unlocks **prod** ONDC + portal KYC upload (A5). Staging sandbox proceeds without GSTIN. |
| Resume | Operator/CA only. Hermes `gst-huf-check` may idle at GST dashboard or be closed. Do **not** agent-fill Business Details / SAVE & CONTINUE unless operator explicitly reopens agent fill. |

## Link to ONDC

ONDC Participant Portal (signup done 2026-07-12) uses the **same HUF entity**: org ID `15462`, legal name `GURUSHARAN GUPTA HUF`, PAN `AAJHG6948N`, Maharashtra/Pune address above. Profile website field: `https://ondcbuyer.aadharcha.in`. GSTIN upload on portal waits on CA Part B.

## HUF documents (Part B)

- HUF PAN card  
- Karta PAN + Aadhaar + photo  
- HUF declaration / affidavit (Karta)  
- Principal place of business address proof  
- Bank proof (HUF / “as Karta of HUF” account)  
- Aadhaar OTP auth for Karta (or DSC/EVC)

## Companion check workflow — **PAUSED (operator / CA)**

**Do not agent-fill Part B from 2026-07-12.** Operator finishes via CA → GSTIN for **prod** ONDC + portal KYC. Staging sandbox is not blocked by missing GSTIN. Agents: leave `gst-huf-check` idle or close; never invent captcha/OTP; never SAVE & CONTINUE.

Historical resume path (operator only if CA needs TRN re-entry):

1. Open `https://reg.gst.gov.in/registration/` (session `gst-huf-check` — not `ondc-portal-onboard`).
2. Select radio **Temporary Reference Number (TRN)** (`#radiotrn`).
3. Enter TRN `272600333290TRN` in `#trnno`.
4. **HARD STOP** at captcha / OTP — operator/CA only.
5. After GSTIN issued: upload registration certificate to ONDC profile KYC (A5).

Never invent State/District/mobile/OTP/captcha. Do not commit PAN images or captcha images as secrets; ledger screenshots under `references/evidence/` OK.

## Live check (2026-07-12) — Hermes `gst-huf-check`

### Morning — TRN resume
- Reached TRN resume path; TRN prefilled; **captcha required** before PROCEED / OTP / Part B.
- Evidence: `references/evidence/gst-trn-radio-20260712.jpeg`, `gst-trn-hardstop-captcha-20260712.jpeg`.

### Afternoon — Part B Business Details (operator past captcha/OTP)
- URL was `…/auth/newappl/business`; Profile **0%**; agent had filled Trade Name / HUF / commencement — **stop**.
- Later idle check: session on `…/auth/dashboard` — leave alone.
- **Operator decision:** Part B completed via **CA** — agent fill paused for this TRN. CA path supplies GSTIN before **prod** ONDC; staging/sandbox is not blocked. Reopen agent fill only on explicit operator ask.
- Evidence: `gst-fill-snapshot-20260712.jpeg`, `gst-business-details-filled-20260712.jpeg`, `gst-business-details-lower-20260712.jpeg`.

## WIP session note (2026-07-11)

Part A completed → TRN issued. Earlier Comet prefill notes superseded by TRN resume path above.
