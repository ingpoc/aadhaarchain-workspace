---
name: demo-video-recording
description: >-
  Gated PreProd/submission demo video pipeline: access checks, narrative script
  (goal → problem → USP → walkthrough), Hermes cursor dry-run of every beat,
  then ffmpeg screen record only after the step matrix Passes. Use when creating
  a Token Nxt demo video, Loom/YouTube Q33 submission, product walkthrough, or
  any recording driven by the portfolio-browser cursor. Triggers: record demo,
  demo video, Loom, YouTube walkthrough, Q33, ffmpeg recording.
---

# Demo video recording

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

**Standing rule:** append durable recording findings to this skill + `references/`; **no secrets**.

**Drivers:** browser = [portfolio-browser](../portfolio-browser/SKILL.md) (Hermes WIP only). Native focus/display = `macos-cua`. Samantha/UX claims = [ondc-testing](../ondc-testing/SKILL.md) (**PreProd FQDN `W-*` bar**). Deploy/FQDN = [portfolio-deploy](../portfolio-deploy/SKILL.md). Partner/Token Nxt form = [apisetu-partner-onboarding](../apisetu-partner-onboarding/SKILL.md).

**Default record surface:** FQDN PreProd — `ondcbuyer.aadharcha.in` / `ondcseller.aadharcha.in` / `gateway.aadharcha.in` + Auth0. Loopback only for automation recovery.

## Hard gate (never skip)

```
1. Access     → preflight + permissions + correct env bake (FQDN PreProd)
2. Script     → goal / problem / USP / beat sheet + VO lines
3. Dry-run    → cursor-driven steps; screenshot+Read proof; matrix all Pass
4. Record     → ONLY after step 3 Pass; same script, same selectors
5. Package    → mux VO if needed; unlisted Loom/YouTube; paste URL
```

**Do not start ffmpeg (or any recorder) until the dry-run matrix is Pass.**  
A failed orb (“Gateway unreachable”, “Realtime not configured”), unsigned Seller AG, or missing pointer proof = **stop**.

## When to load

- Token Nxt / GFF application demo video (form Q33)
- “Record a demo”, “Loom”, “walkthrough video”, “cursor demo”
- Re-recording after a product change that affects the PreProd walkthrough

## Phase 1 — Access checklist

Run and require Pass before scripting deep UI:

| Check | How | Pass |
| --- | --- | --- |
| Hermes WIP bridge | `python3 scripts/portfolio_browser.py preflight` | `tier: hermes-wip`, Comet/Chrome visible |
| Screen Recording | `macos-cua` workflow preflight permissions | `screen_recording` + capturable true |
| ffmpeg | `which ffmpeg` + `ffmpeg -f avfoundation -list_devices true -i ""` | Screen index known (which monitor has Comet) |
| PreProd stack | FQDN gateway health + Buyer/Seller 2xx | Realtime `configured:true` if voice claimed |
| App env bake | FQDN apps use gateway identity URL (not accidental loopback) | `gateway.aadharcha.in` on live |
| Auth | Auth0 Sign in (FQDN) | Sign out / principal bound on AG surfaces |
| Display | Comet focused on recorded monitor (`MACOS_CUA_DISPLAY`) | Operator can see labeled Hermes cursor |

Details: [`references/access-checklist.md`](references/access-checklist.md).

**Local trap (2026-07-12/13):** if using loopback for recovery, Vite process env can be FQDN while `.env.local` is loopback (or reverse). `scripts/start-dev.sh` strips inherited `VITE_*`, applies `.env.local`, starts Vite in a **new process group**. Prefer FQDN PreProd for record dry-run.

**Patterns / antipatterns:** [`references/access-checklist.md`](references/access-checklist.md) § Patterns. Driver symptom table: [`portfolio-browser/references/troubleshooting.md`](../portfolio-browser/references/troubleshooting.md). Samantha catalog NL empty: [`ondc-testing`](../ondc-testing/SKILL.md) Friction → fix.

## Phase 2 — Script (narrative first)

Write/update the shot script **before** dry-run. Template: [`references/script-template.md`](references/script-template.md).

Required sections (in order):

1. **Goal of the app** — one sentence product outcome  
2. **Use case / problem** — who hurts, what fails without the product  
3. **USP** — what only this demo proves (e.g. realtime voice + runtime agent under AgentGuard on Buyer+Seller)  
4. **Honesty bounds** — what not to claim (live UPI, prod ONDC, NPCI partnership)  
5. **Beat sheet** — timed shots with VO + exact UI actions/selectors  
6. **Close** — roadmap line if any (future tense only)

Token Nxt instance:  
[`../apisetu-partner-onboarding/references/token-nxt-demo-script.md`](../apisetu-partner-onboarding/references/token-nxt-demo-script.md)

## Phase 3 — Dry-run (cursor, every beat)

Use **visible Hermes cursor only**: `click_text`, `click_selector`, `cursor_type`, `cursor_key`, `cursor_status`, `screenshot`.  
**Never** `evaluate` to click/mutate for demo beats (portfolio-browser / Hermes WIP hard rule).

For each beat in the script:

1. Execute the cursor action  
2. `screenshot` → **Read the image** (pointer + outcome)  
3. Mark Pass/Fail in a step matrix under `references/evidence/<demo-id>/`

Matrix template: [`references/step-matrix-template.md`](references/step-matrix-template.md).  
Token Nxt live matrix: [`../apisetu-partner-onboarding/references/token-nxt-demo-step-matrix.md`](../apisetu-partner-onboarding/references/token-nxt-demo-step-matrix.md).

Map beats to [`ondc-testing`](../ondc-testing/SKILL.md) PreProd flow IDs (`W-B-FIND-NL-ATTA`, `W-B-AG-CONFIRM`, `W-S-AG-PAUSE`, etc.).

### AgentGuard / Samantha selector notes (Buyer)

| Intent | Prefer | Avoid |
| --- | --- | --- |
| Open orb | semantic role locator: button named `Open Samantha` (click **once**) | `click_text "S"`; second orb click toggles closed |
| Type ask | test-id locator `{ "by": "testid", "testId": "samantha-orb-text" }` with `fill` | Lowercase `testid` value key; typing into page search |
| Send | role locator: button named `Send`, exact | Blind Send before panel open |
| Mandate UI | `Preferences & AgentGuard` or nav `Config` → `Confirm mandate` | Assuming panel open |

Seller AG beats require **signed-in** principal on `/agentguard` (not “Trust Unsigned”).

### Pass bar for dry-run

- Every beat: pointer visible in screenshot **or** intentional full-page outcome shot after a proven click  
- Agent ask beat: **visible product outcome** (results/cart/AG card)—not only text in the orb  
- No red gateway/realtime error in frame if claiming agent tools/voice  
- Seller beat: mandate/control UI visible if claimed  

If any required beat Fails → fix access/env/selectors → re-dry-run. **Do not record.**

## Phase 4 — Record

Only after Phase 3 matrix Pass:

1. Focus Comet on the **recorded** display (confirm ffmpeg screen index: main LG vs DELL)  
2. Hide IDE/personal tabs on that display  
3. Start ffmpeg (screen + optional mic); prefer silent UI + mux VO if mic noisy  
4. Replay **the same** dry-run cursor script (no improvised evaluate shortcuts)  
5. Stop; mux VO if separate; spot-check frames (Read mid-video stills)  
6. Export MP4 → upload unlisted Loom/YouTube → store URL in curated answers / evidence

Commands sketch: [`references/record-commands.md`](references/record-commands.md).

## Phase 5 — Package

| Artifact | Where |
| --- | --- |
| Script | `references/` or owning skill `references/` |
| Step matrix | [`references/evidence/README.md`](references/evidence/README.md) + `<demo-id>/` |
| Proof shots | same |
| MP4 | `references/evidence/<demo-id>/` (git LFS / ignore large blobs if needed) |
| Public URL | Form field / curated answers — **no secrets** |

## Modes

| Mode | When | Quality |
| --- | --- | --- |
| **A. Operator voice + Hermes cursor** | Mic available; best for Realtime claim | Best |
| **B. Hermes cursor + TTS VO** | Deadline; voice path blocked | Good if VO explains USP honestly |
| **C. Full auto mic→WebRTC** | Avoid | Unreliable |

## Do not

- Record before dry-run Pass  
- Mix CUA pixel clicks with Hermes for the same beat (pick one pointer story)  
- Claim live UPI / prod ONDC / NPCI partnership on VO  
- Use `evaluate` clicks “just for the recording”  
- Record the wrong monitor (IDE instead of Comet)

## Related

| Surface | Role |
| --- | --- |
| [portfolio-browser](../portfolio-browser/SKILL.md) | Hermes WIP preflight / click_* / SSO |
| [ondc-testing](../ondc-testing/SKILL.md) | PreProd Samantha claim→screenshot Pass bar |
| [authentication](../authentication/SKILL.md) | Auth0 / demo principal |
| [apisetu-partner-onboarding](../apisetu-partner-onboarding/SKILL.md) | Token Nxt form + curated answers |
