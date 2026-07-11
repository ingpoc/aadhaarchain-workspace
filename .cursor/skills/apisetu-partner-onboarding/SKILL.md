---
name: apisetu-partner-onboarding
description: >-
  MeitY API Setu / DigiLocker partner signup (PAUSED 2026-07-11 — prefer Setu.co
  sandbox + local demo). Resume when operator asks for gov production KYC.
  Also holds GoDaddy aadharcha.in and paused GSTIN HUF TRN notes. Triggers:
  API Setu, apisetu.gov.in, MeriPehchaan, DigiLocker partner, MeitY onboarding,
  GSTIN HUF, GoDaddy aadharcha.in — not for routine local verify (use SETU_EKYC_*).
---

# API Setu partner onboarding (paused)

**Status (2026-07-11):** Operator chose **pause MeitY + GST**; stay local; use **Setu.co eKYC sandbox**.  
Do not drive partners.apisetu.gov.in or GST Part B unless explicitly resumed.

Active KYC path → `PRODUCTION-READINESS.md` § Active path — Setu.co sandbox + gateway `SETU_EKYC_*`.  
Local demo upload / fixtures remain valid without any external KYC.

Owner plan: [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md).  
Browser runtime (when resumed): **Hermes Chrome WIP** on **Comet**.

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
```

## Do not confuse

| Wrong | Right (now) |
| --- | --- |
| Push MeitY / GST to unblock verify | Local demo or **Setu.co** `SETU_EKYC_*` |
| Commercial Setu.co vs MeitY | Setu.co = **active sandbox**; MeitY = **paused** gov path |
| `portfolio-browser` | Local 43100–43103 only |

## Hard stops (when MeitY resumed)

1. **MeriPehchaan OTP**  
2. **Verify Email OTP**  
3. **Org secrets / legal** — GSTIN, docs, etc.

## Paused artifacts

| Item | Note |
| --- | --- |
| GST TRN | `272600333290TRN` — Part B optional by 26/07/2026 |
| GoDaddy | [`references/godaddy.md`](references/godaddy.md) |
| GST HUF | [`references/gstin-huf.md`](references/gstin-huf.md) |
| MeitY form friction | OAuth `?code=` → `useSelectedTab`; `keepWindow` on OTP |

## Related

- Portfolio browser → `.cursor/skills/portfolio-browser/`  
- Setu.co eKYC code → `aadharchain/gateway/app/setu_ekyc.py` + verify UI  
- WIP → `/Users/gurusharan/plugins/hermes-chrome-cursor-wip/skill/SKILL.md`
