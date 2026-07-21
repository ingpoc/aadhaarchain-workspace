# Token Nxt demo video — AgentGuard walkthrough (~2:00)

> **Current control owner:** bundled `@chrome` for browser actions and bundled
> `@Computer` for native Mac UI. Hermes-specific action names below preserve the
> 2026-07-15 choreography only; translate them to Chrome-plugin semantic actions
> for a new take unless the operator explicitly approves the legacy fallback.

**Pipeline owner:** [demo-video-recording](../../demo-video-recording/SKILL.md) — access → this script → fresh FQDN dry-run Pass → record → voiceover → package.

## Meta

| Field | Value |
| --- | --- |
| Demo id | `token-nxt-agentguard-20260715` |
| Audience | Token Nxt application reviewers (form Q33) |
| Target length | 1:55–2:10 |
| Browser driver | Bundled Chrome plugin; reuse a claimed/existing tab when safe |
| Record surface | FQDN PreProd: Buyer + Seller + gateway |
| Picture | Chrome full window, 1280×720, 30 fps, screen-only ffmpeg capture |
| Product voice runtime | OpenAI Realtime, currently deployed as `gpt-realtime-2.1-mini` |
| Narration | OpenAI Speech API `gpt-4o-mini-tts`, muxed after capture |
| Disclosure | Keep `AI-generated narration` visible on the title and closing frames |

The narration is deliberately separate from Samantha's Realtime session. OpenAI Realtime is the product's low-latency voice runtime; the Speech API is the appropriate request-based path for a bounded narration file. The narration does **not** count as proof of Samantha's browser microphone/WebRTC path.

## 1. Goal of the app

> AgentGuard lets people delegate commerce tasks to AI agents while retaining one enforceable authority boundary across Buyer and Seller actions.

## 2. Use case / problem

Shopping agents can search, compare, and act faster than a user, but a model must not be the final judge of its own authority. The user needs an independent control plane that can allow an action, require one exact approval, or stop the agent.

## 3. USP demonstrated

One principal-bound AgentGuard contract governs the Buyer tool journey and Seller controls. The model proposes an action; the server-side policy decides whether it may proceed and records the outcome.

## 4. Honesty bounds

- This is a PreProd proof of concept, not production ONDC conformance.
- ONDC discovery is partial: network fanout plus signed configured-Seller search provides deterministic portfolio discovery.
- Payment is simulated; do not claim live UPI or an NPCI partnership.
- The deployed gateway is configured for OpenAI Realtime, but this deterministic take uses Samantha's text input. Do not describe the AI-generated narration as a live Realtime conversation.
- Physical microphone/WebRTC proof remains separate until it is visibly exercised in a fresh dry-run.

## 5. Beat sheet

Resolve every locator immediately before acting. Use only Hermes `click_*`, `cursor_*`, `page_context`, and `screenshot`; never use `evaluate` to click or mutate.

| # | Time | Shot | Exact narration | Hermes action / locator | Pass signal |
| --- | --- | --- | --- | --- | --- |
| 0 | 0:00–0:09 | Buyer title frame | “This walkthrough uses AI-generated narration. AgentGuard makes agentic commerce safe by keeping people in control of what an AI agent may do.” | Lease `https://ondcbuyer.aadharcha.in/search`; wait for stable page; no click. | Buyer brand and `AI-generated narration` disclosure visible. |
| 1 | 0:09–0:23 | Signed-in Buyer search | “Shopping agents can move quickly, but the model must not be the final judge of its own authority. AgentGuard separates an agent’s proposal from permission.” | `page_context`; show signed-in state and search surface. Wake the labeled pointer with `click_text` on `Search` only if needed. | Buyer search surface and signed-in state visible; pointer visible. |
| 2 | 0:23–0:36 | Open Samantha | “On the ONDC Buyer app, Samantha uses authorized tools behind one principal-bound session. This take uses text so every step is reproducible.” | Resolve semantic role `{ "by": "role", "role": "button", "name": "Open Samantha", "exact": true }`; click once. | Samantha panel open; no gateway or Realtime error. |
| 3 | 0:36–0:58 | Ask and run tools | “We ask: find atta under two hundred rupees and add it to my cart. Samantha searches the configured ONDC path and performs the tool action instead of only returning chat.” | `cursor_type` into `input[data-testid=samantha-orb-text]`: `Find atta under 200 rupees and add it to my cart.` Then resolve and `click_text` `Send`; wait for the visible outcome. | Tool result is visible; Seller Atta appears; no red error. |
| 4 | 0:58–1:11 | Visible cart outcome | “The result is a visible commerce outcome: Seller Atta at eighty-nine rupees, added to the Buyer cart.” | Use the existing visible control to show the cart/result. Do not add a second item if the tool already added it. | Atta, price, and cart state visible in the page—not only in Samantha text. |
| 5 | 1:11–1:31 | Buyer mandate | “Now the authority layer. In Preferences and AgentGuard, the user confirms the mandate that defines allowed actions and limits. The model proposes; server policy decides.” | Navigate with visible UI to `Config` / `Preferences & AgentGuard`; resolve `Confirm mandate`; click once only if the dry-run fixture expects confirmation. | Mandate and confirmed state visible. |
| 6 | 1:31–1:48 | Seller AgentGuard | “The Seller side uses the same control contract. A signed-in operator can inspect the mandate, pause the agent, or require confirmation without inventing a second authorization system.” | Use the existing Seller leased window at `https://ondcseller.aadharcha.in/agentguard`; show `Pause agent` and `Confirm mandate`. Do not pause during the final take unless the dry-run includes the recovery. | Signed-in Seller controls visible; not `Trust Unsigned` or sign-in error. |
| 7 | 1:48–2:04 | Closing frame | “Today this proves guarded discovery, tool execution, cart state, and two-sided control. Live UPI Circle agent payment remains the roadmap. AgentGuard is the authority layer ready to govern that future action.” | Return to a clean AgentGuard summary or prepared closing frame. Hold for two seconds after narration. | Closing claim and `AI-generated narration` disclosure visible; no production claim. |

## 6. Narration master

Use this exact text for the generated track:

> This walkthrough uses AI-generated narration. AgentGuard makes agentic commerce safe by keeping people in control of what an AI agent may do.
>
> Shopping agents can move quickly, but the model must not be the final judge of its own authority. AgentGuard separates an agent’s proposal from permission.
>
> On the ONDC Buyer app, Samantha uses authorized tools behind one principal-bound session. This take uses text so every step is reproducible.
>
> We ask: find atta under two hundred rupees and add it to my cart. Samantha searches the configured ONDC path and performs the tool action instead of only returning chat.
>
> The result is a visible commerce outcome: Seller Atta at eighty-nine rupees, added to the Buyer cart.
>
> Now the authority layer. In Preferences and AgentGuard, the user confirms the mandate that defines allowed actions and limits. The model proposes; server policy decides.
>
> The Seller side uses the same control contract. A signed-in operator can inspect the mandate, pause the agent, or require confirmation without inventing a second authorization system.
>
> Today this proves guarded discovery, tool execution, cart state, and two-sided control. Live UPI Circle agent payment remains the roadmap. AgentGuard is the authority layer ready to govern that future action.

OpenAI speech direction:

> Calm, precise Indian English; confident but not promotional; approximately 135 words per minute. Pause briefly between paragraphs. Pronounce ONDC as O-N-D-C and UPI as U-P-I. Keep product names crisp. Do not add or paraphrase words.

Recommended built-in voice: `coral`. Generate the narration only after the final words are approved. The API key remains server-side or in the operator environment and must never be written to evidence.

## 7. Recording and mux sequence

1. Run the demo-video access checks and a **fresh FQDN dry-run** of all eight beats.
2. Claim or create the required Buyer and Seller Chrome tabs through the bundled plugin. Keep both on the recorded macOS Space.
3. Generate `vo.mp3` with OpenAI `gpt-4o-mini-tts`; measure its duration.
4. Record a silent Chrome-plugin walkthrough paced to the narration.
5. Mux `take.mp4` + `vo.mp3` with ffmpeg. If timing differs by more than five percent, revise the narration or redo the take instead of heavily stretching audio.
6. Extract and read representative frames: title/disclosure, Samantha outcome, mandate, Seller controls, and close.
7. Finalize Chrome-plugin tabs: close temporary tabs and hand off claimed user tabs.
8. Upload the final MP4 unlisted and paste the URL into Token Nxt form Q33.

## 8. Record gate

- [x] Gateway, Buyer, and Seller FQDN return healthy responses (checked 2026-07-15).
- [x] Gateway reports OpenAI Realtime configured with `gpt-realtime-2.1-mini` (checked 2026-07-15).
- [x] Historical Hermes Chrome WIP bridge check passed (2026-07-15); this does not replace a fresh Chrome-plugin preflight.
- [x] ffmpeg 8.0.1 is available; screen devices 0 and 1 are discoverable.
- [ ] Chrome-plugin controlled window is visible on the recorded macOS Space.
- [ ] Fresh FQDN dry-run matrix passes every beat with screenshot + image-read proof.
- [ ] Final narration text is approved before the OpenAI Speech request.

**Record allowed now:** **No** — prepare the Chrome window, then complete the fresh FQDN dry-run.

## 9. Output

Store working evidence under:

`.cursor/skills/apisetu-partner-onboarding/references/evidence/token-nxt-demo-20260715/`

Expected files: `dryrun.json`, proof screenshots, `vo.mp3`, `take.mp4`, and `demo-final.mp4`. Keep large media ignored or outside Git unless intentionally using Git LFS. Upload the final video to Loom or YouTube as unlisted and place its URL in form Q33.
