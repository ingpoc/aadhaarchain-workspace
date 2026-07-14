# Token Nxt demo video — script (~2:30)

**Pipeline owner:** [demo-video-recording](../../demo-video-recording/SKILL.md) — access → this script → dry-run matrix Pass → record.

Target: Loom/YouTube link for form Q33.  
Record: Comet/Chrome full window · 1280×720 or retina scaled · 30fps.  
Voice track: operator live **or** post TTS from this script (macOS `say` / ElevenLabs).

## Honest framing (on-screen or VO)

> Proof of concept: realtime voice + runtime agents under AgentGuard on ONDC Buyer and Seller.  
> Cart and mandates are live today. UPI Circle agent payment is the roadmap once NPCI opens that path—AgentGuard is the authority layer that makes it safe.

**Do not say on camera:** live UPI, prod ONDC orders, “we are an NPCI partner.”

---

## Shot list

| T | Shot | Action | VO |
| --- | --- | --- | --- |
| 0:00–0:10 | Title | `AgentGuard` + URLs Buyer/Seller | “Safe agentic commerce—agents that work, with limits you control.” |
| 0:10–0:35 | Buyer home | Open `ondcbuyer.aadharcha.in` (FQDN PreProd). Show signed-in principal. | “Buyer side on ONDC. You talk—or type—what you need.” |
| 0:35–1:10 | Samantha | Open orb. Prefer **voice** if operator available; else text: “Find atta under 200 rupees and add to cart.” Show tool activity + results/cart. | “Realtime voice issues real tool calls—search, compare, add to cart. No hunting through menus.” |
| 1:10–1:40 | AgentGuard | Open authority / mandate. Lower refund or checkout max / remove an allowed action. Show need_approval or block. | “AgentGuard restricts what the agent may do. The model proposes; policy decides.” |
| 1:40–2:05 | Approve / pause | Approve one exception **or** Pause agent. Show receipt / status. | “Step-up for one exact action—or pause everything instantly.” |
| 2:05–2:20 | Seller (cut) | Seller `/agentguard` or refund demo—same control contract. | “Same contract on the Seller NP—we run both sides.” |
| 2:20–2:30 | Close | Slide: voice + runtime + AgentGuard → future UPI Circle under same mandate | “When agent UPI Circle onboarding opens, the same guarded agent can complete payment. Until then: live demo of authority + cart.” |

---

## Voice lines (clean VO take)

1. Safe agentic commerce—agents that work, with limits you control.  
2. On the Buyer app, a realtime voice agent and a runtime agent share one tool runner.  
3. Ask for what you need; tools search the ONDC network and add items to the cart.  
4. AgentGuard is the authority layer: you set allowed actions and amounts.  
5. Protected steps are evaluated on the server—allow, ask once, or block.  
6. We also run the Seller side under the same contract.  
7. Payment via UPI Circle agents is the roadmap after NPCI’s pilot path is available. Today we prove the control plane and live cart.

---

## Recording modes

| Mode | Who | Quality for Token Nxt |
| --- | --- | --- |
| **A. Operator voice + Hermes clicks** | You speak to Samantha; Hermes/CUA assists UI | **Best** |
| **B. Hermes UI + TTS VO** | Fully agent-produced | Good / honest if captions say “text agent path” or VO explains voice USP |
| **C. Full auto voice** | Agent drives mic into WebRTC | **Not reliable**—skip |

Recommended for deadline: **Mode A** if you can spare 10 minutes; else ship **Mode B** tonight and re-record Mode A before 15 Jul if possible.

---

## Technical checklist

- [ ] Gateway Realtime `configured:true` (FQDN ✓ as of 2026-07-12)  
- [ ] Screen Recording allowed for Terminal / Cursor (CUA preflight ✓)  
- [ ] `ffmpeg` available  
- [ ] Portfolio browser preflight (Hermes WIP)  
- [ ] Auth0 session on FQDN Buyer + Seller (PreProd record default)  
- [ ] Hide IDE / personal tabs; only Buyer (+ optional Seller) window  
- [ ] Export MP4 ≤ ~50–80 MB for Forms/YouTube/Loom  

## Output path

`references/evidence/token-nxt-demo-YYYYMMDD.mp4`  
Upload to Loom/YouTube unlisted → paste URL into form Q33.
