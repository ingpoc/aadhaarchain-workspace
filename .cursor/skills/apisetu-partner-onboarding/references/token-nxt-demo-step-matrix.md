# Token Nxt demo — cursor step matrix (pre-record)

**Pipeline owner:** [demo-video-recording](../../demo-video-recording/SKILL.md). **Do not record until required beats Pass.**

Retested **2026-07-13** after env-bake fix. Hermes WIP `click_*` / `cursor_*` only.  
Proof: `references/evidence/token-nxt-demo/cursor_proof/dryrun_20260713.json`, `fix13_*.jpeg`.

## Access (required before beats)

| Check | Result | Notes |
| --- | --- | --- |
| Buyer/Seller `VITE_*` = loopback `43101` | **Pass** | Was FQDN process env overriding `.env.local`. Fixed: `start-dev.sh` strips inherited `VITE_*`, loads `.env.local`, starts Vite with `start_new_session=True` (Cursor Shell teardown was killing nohup Vite). |
| Gateway Realtime `configured:true` | **Pass** | `GET :43101/api/realtime/status` |
| Orb no gateway/realtime red error | **Pass** | `realtimeErr:false` after open |
| Buyer `sso demo` | **Pass** | Sign out visible |
| Seller `sso demo` on `/agentguard` | **Pass** | Sign out; **not** Sign-in not configured |
| Hermes WIP socket | **Pass** | Reloaded Comet WIP extension when SW slept |

## Cursor beats

| Beat | Result | Evidence |
| --- | --- | --- |
| Wake pointer (`click_text Search` or Grocery) | **Pass** | `cursor_status.visible=true` |
| Open orb with semantic role locator `{ "by": "role", "role": "button", "name": "Open Samantha", "exact": true }` | **Pass** | Resolve the locator immediately before clicking. Click once because the orb toggles closed on a second click. |
| Type ask + Send | **Pass** | `input[data-testid=samantha-orb-text]` + `click_text Send` |
| Samantha tool outcome | **Pass** | Tools run (`realtimeErr:false`). Keyword extract `catalogSearchQuery` so NL “Find atta under 200…” hits demo-commerce (`atta`). Seeded published Atta ₹89. |
| Config Confirm mandate | **Pass** | `/config` → Confirm mandate |
| Seller `/agentguard` Pause/Confirm | **Pass** | `hasPause` / `hasConfirm` / `hasSignOut`; `signInNotConfigured:false` |

## Recording-ready sequence

1. Detached local Buyer/Seller with loopback `VITE_*` (use fixed `start-dev.sh` or Python `start_new_session`)  
2. `sso demo buyer` + `sso demo seller`  
3. Buyer `/search` → resolve the `Open Samantha` button by semantic role → click once  
4. `input[data-testid=samantha-orb-text]` → ask → Send → wait for reply  
5. `/config` → Confirm mandate  
6. Seller `/agentguard` → show Pause agent / Confirm mandate  
7. ffmpeg Comet on DELL + same cursor script + VO  

## Gate

- [x] All required beats Pass  
- [x] No red gateway/realtime error when claiming agent tools  
- [x] Seller AG signed-in controls visible  
- [x] Samantha ask → visible Atta + add-to-cart (after `catalogSearchQuery` + seeded demo-commerce)

**Historical local record gate:** **Pass** (2026-07-13)

The 2026-07-15 script targets FQDN PreProd and adds an exact eight-beat Hermes
walkthrough plus OpenAI-generated narration. This historical loopback proof does
not authorize that new take. Create fresh FQDN screenshot + image-read proof for
all eight beats before recording.

**Record allowed for the 2026-07-15 FQDN script:** **No — fresh dry-run required.**
