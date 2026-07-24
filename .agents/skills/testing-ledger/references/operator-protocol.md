# Operator protocol + thorough bar (ondc-testing)

Owner detail for the customer-gate lane. Doctrine/modes/locks: `~/.agents/skills/testing-framework`. Gate profiles/budgets: [`independent-customer-gate.md`](independent-customer-gate.md). Flow IDs: [`operator-flows.md`](operator-flows.md).

**USP:** Samantha = talk → preference/memory → right picks → cart. Reliability, results quality, and visible experience are equal. Do not fire-hose prompts.

## Operator text-mode protocol (every run)

1. **Ask like an operator** — natural language via orb text (examples in operator-flows). No phrase/regex command maps; no API-only tool stubs as Pass.
   - **Blinded acceptance first:** the test actor may use only visible labels, pages, and ordinary Buyer/Seller language. It must not know tool names, fixture ids, transaction ids, seeded product names, expected model arguments, or backend implementation details.
   - Freeze the visible result and screenshots before opening logs, transcript events, `window.__samantha*`, or backend state. Those are post-journey diagnostic evidence, never instructions that shape the operator's next ask.
   - A fixture-aware matrix and `scripts/hermes_ondc_blind_operator.py` are deterministic regression aids, not independent acceptance. Only the blind full-mission actors in the independent customer gate can supply that evidence.
2. **Settle–validate–next (hard)** — **one** orb ask, then wait until settled before the next. Chain tests = deliberate second ask **after** Pass on the first. Never stack asks while “Pulling…” / tool race still open.
3. **Watch the frontend** — route changes and page content are the product. Find/search **must** hit `/results?q=` **early** (before long ONDC poll finishes); cart/checkout/AG outcomes must be on-page.
4. **Tool evidence** — read `window.__samanthaTools` (and console via `page_diag` / diag). Orb reply alone ≠ Pass.
5. **Three-way claim check after every query** — screenshot (agent **Read**) + frontend route/DOM/tool state + backend owner state must agree before Pass. If a claim is frontend-owned (for example local cart before checkout), record that boundary and prove no premature backend side effect.
6. **Map intents → catalog** — match ask to a flow ID in operator-flows; use that ID in matrix-status. If a new operator phrasing appears, **append a row to operator-flows** (do not leave orphans in chat).
7. **Runtime** — long asks → `delegate_to_runtime_agent`; stay off `/agent`. “Started” proves only handoff, not completion: require the recorded lifecycle `started → heartbeat → completed` (or a visible failed terminal state) and capture the final UI. Gateway `/api/agent/*` on FQDN (not FlatWatch).
8. **Both apps** — Buyer + Seller each serious run; claim→screenshot→Pass.
9. **Fix if broken** — wrong/empty results or broken experience → diagnose and root-cause in the main thread; use a focused check only to prove the defect owner, then rerun the blind actor's **entire affected customer journey**. Redeploy only when deployment is in scope and required to make the tested environment contain the fix. **Click hang / Tooling Blocked on Hermes:** before inject/SPA bridge theories, grep the app click handler for `prompt`/`confirm`/`alert` (Seller Dispatch = Hermes `dialog_handle`). See hermes-chrome `optimize.md` §4 and portfolio-browser troubleshooting.
10. **Hermes contract** — interact through semantic `locator` actions. JS dialogs are Hermes (`dialog_handle`); OS-native UI is `$macos-cua`. Runtime `evaluate` is read-only diagnostics; never mutate inputs, click controls, or seed mandates with page JavaScript.

## Independent customer gate

After build/API checks, load and follow [`independent-customer-gate.md`](independent-customer-gate.md). That reference solely owns reviewer profiles, post-login audience setup, complete-mission budgets, visible/tiled windows, verdicts, repetition, and specialist admission. Do not restate or improvise a second reviewer contract in the routing skill.

## Settle gate (all required before next ask)

| Check | Pass signal |
| --- | --- |
| Spinner / pulling | No stuck “Pulling…” / Searching; or honest empty + timeout recorded |
| Tools | New `__samanthaTools` entry for this turn (`ok`/message); greetings = explicit no-tool |
| Errors | `__samanthaEvents` / `__samanthaErrors` checked; Realtime errors documented |
| Route / UI | Matches intent (search→`/results?q=…`, add→`/cart` line, etc.) |
| Results quality | Names/prices sensible for query; note crafts-for-bananas; prefer Atta/marker / our BPP when proving Seller |
| Console | `page_diag` / console empty or documented |
| Backend | Every query records the relevant owner check: gateway status/catalog/order/AgentGuard/runtime state, or an explicit frontend-only boundary plus no premature backend side effect |

## Listen surfaces (Hermes while testing)

- `window.__samanthaTools` — `name`, `ok`, `navigateTo`, `cartAdds`, `navSuperseded`
- `window.__samanthaEvents` / `__samanthaErrors`
- Orb hint + reply text
- URL + headings + result grid / cart lines (screenshot → agent **Read**)
- Network: ONDC search/catalogs; `/api/agent/runtime` on handoff
- Optional: tiny Hermes dump of tools+events+url after wait — do not bloat product UI

## Thorough bar (hard — every serious run)

Incomplete unless all pillars attempted with claim→screenshot→Pass (or Blocked + evidence):

| Pillar | What | Pass signal |
| --- | --- | --- |
| **1. Samantha as user (text)** | Natural language via orb; **no** phrase/regex command maps | Screenshot of UI outcome (results/cart/orders/AG), not orb text alone |
| **2. Samantha voice** | Realtime mic/session like a user (WebRTC); not API-only curl | Orb connected (not “Realtime not configured”); voice ask → visible tool outcome shot |
| **3. Runtime agent** | Long handoff via `delegate_to_runtime_agent` (Cursor host; invisible to user) | Orb “I've started… I'll let you know” (or equivalent); **must not** land on `/agent`; completion notify / visible outcome shot |
| **4. Full commerce (Buyer)** | search → add → cart → checkout → **payment** as far as demo allows | Cart line shot; checkout Paid+receipt **or** AG need_approval/deny card on page |
| **5. All Samantha tools** | Discover from `agentTools.ts` + UI + GOAL.md; exercise each | Per-tool row in matrix with screenshot |
| **6. Seller mirror** | catalog/orders/refunds/AgentGuard + tools (publish/refund/nav/memory/handoff) | Same screenshot doctrine |
| **7. Both apps** | Buyer **and** Seller | One side only = incomplete |

### Buyer tools (must cover)

From `ondcbuyer/src/lib/agentTools.ts`: `search_catalog`, `navigate_to`, `add_to_cart`, `checkout_commit`, `remember_preference`, `delegate_to_runtime_agent`.

### Seller tools (must cover)

From `ondcseller/src/lib/agentTools.ts`: `navigate_to`, `catalog_publish`, `refund_issue`, `remember_preference`, `delegate_to_runtime_agent`.

### Voice vs text

- Voice requires gateway Realtime configured (`GET …/api/realtime/status` → `configured:true`) — needs Render `OPENAI_API_KEY` (+ model env). If `configured:false`, mark **W-B-VOICE / W-S-VOICE Blocked** with screenshot of orb hint; do not Pass voice.
- Text mode still required when voice blocked.

### Runtime agent

- Trigger with a long ask (e.g. weekly groceries plan / bulk triage).
- Pass: handoff hint in orb shot + stay off `/agent` + later completion/outcome shot when available.
- Needs gateway process `CURSOR_API_KEY` (file present ≠ loaded — see portfolio-browser / start-dev).

## Permanent doctrine

1. Claim → Hermes screenshot → agent **Read** image → only then Pass.
2. Visible journey required (add banana ⇒ results UI ⇒ cart line).
3. AgentGuard honesty: allow / need_approval / deny as shown.
4. Closeout via portfolio-browser after browser work. WIP socket only.

## Success criteria (compact)

| Ask class | Pass (requires screenshot) |
| --- | --- |
| Greeting / thanks | Brief reply; no tools; URL unchanged |
| Find / show product | Results UI matching items |
| Add to cart | Cart line / `/cart` |
| Navigate | Target route visible |
| Memory | Preference on `/config` or seller `/agentguard` when shown |
| **Checkout / payment** | Page Paid + receipt **or** AG need_approval/deny card |
| Refund / publish | AG/catalog outcome visible |
| **Voice** | Connected Realtime session + tool outcome on page |
| **Runtime handoff** | Handoff hint; not `/agent`; completion/outcome when done |
| Wallet residuals | No Solflare/Phantom/burner primary CTA |

## Workflow

```
1. portfolio-browser preflight (local) or wake gateway (FQDN)
2. Auth: local `sso demo` **or** Auth0 Sign in on FQDN PreProd — stop at OTP for operator; keep gateway awake. **PreProd readiness = FQDN + Auth0 + live gateway.**
3. Buyer: tools + voice (if configured) + runtime handoff + checkout/payment — screenshots
4. Seller: tools + refund/publish + AG + runtime — screenshots
5. Append matrix-status.md; encode durable gaps in references/integration-gaps.md
6. closeout
```

**After any FQDN archive deploy+alias:** do not stop at deploy — immediately run operator-flows deploy-bake smoke (`B-HI`, `B-FIND-NL-ATTA` or `B-FIND-ATTA`, `S-NAV-CAT`) then continue thorough bar as needed. PreProd readiness trio: `W-B-FIND-NL-ATTA`, `W-B-AG-CONFIRM`, `W-S-AG-PAUSE`.
