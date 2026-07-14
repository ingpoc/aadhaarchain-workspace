---
name: ondc-testing
description: >-
  Product UX / Samantha / AgentGuard user-journey testing for ONDC Buyer
  (:43102) and Seller (:43103) and live FQDNs. Thorough bar: Samantha voice +
  text tools, Cursor runtime handoff, full search→cart→checkout→payment,
  Seller refunds/AG. claim→screenshot→Pass. Triggers: ondc-testing, Samantha,
  Realtime voice, runtime agent, Buyer Seller matrix, checkout payment.
  Bridge: portfolio-browser WIP only.
---

# ONDC testing (Samantha + AgentGuard journeys)

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

**Scope:** product UX on **both** Buyer and Seller — local (`:43102`/`:43103`) **and** live FQDNs.  
**Not this skill:** Hermes WIP bridge/preflight/SSO → [`portfolio-browser`](../portfolio-browser/SKILL.md). Deploy/env → [`portfolio-deploy`](../portfolio-deploy/SKILL.md). Auth0 → [`authentication`](../authentication/SKILL.md). ONDC portal → [`apisetu-partner-onboarding`](../apisetu-partner-onboarding/SKILL.md). Demo video dry-run→record → [`demo-video-recording`](../demo-video-recording/SKILL.md).

**Standing:** append Pass/Fail/Blocked + screenshot paths to [`references/matrix-status.md`](references/matrix-status.md). **No secrets** in markdown. Do not flip `VITE_COMMERCE_DEMO_MODE` without evidence gate. Do not claim live ONDC network orders without proof.

**Operator flows (durable catalog):** [`references/operator-flows.md`](references/operator-flows.md) — intents, UI journeys, tools, pass signals, change-class map. Thin ask index: [`references/query-matrix.md`](references/query-matrix.md).

**PreProd Beckn (real sellers):** [`references/preprod-network-matrix.md`](references/preprod-network-matrix.md) + `scripts/ondc_preprod_smoke.py`.

**USP:** Samantha = talk → preference/memory → right picks → cart. Reliability, **results quality**, and **visible experience** are equal. Do not fire-hose prompts.

### Operator text-mode protocol (every `/ondc-testing` run)

1. **Ask like an operator** — natural language via orb text (examples in operator-flows). No phrase/regex command maps; no API-only tool stubs as Pass.
2. **Settle–validate–next (hard)** — **one** orb ask, then wait until settled before the next. Chain tests = deliberate second ask **after** Pass on the first. Never stack asks while “Pulling…” / tool race still open.
3. **Watch the frontend** — route changes and page content are the product. Find/search **must** hit `/results?q=` **early** (before long ONDC poll finishes); cart/checkout/AG outcomes must be on-page.
4. **Tool evidence** — read `window.__samanthaTools` (and console via `page_diag` / diag). Orb reply alone ≠ Pass.
5. **Map intents → catalog** — match ask to a flow ID in operator-flows; use that ID in matrix-status. If a new operator phrasing appears, **append a row to operator-flows** (do not leave orphans in chat).
6. **Runtime** — long asks → `delegate_to_runtime_agent`; stay off `/agent`. “Started” proves only handoff, not completion: require the recorded lifecycle `started → heartbeat → completed` (or a visible failed terminal state) and capture the final UI. Gateway `/api/agent/*` on FQDN (not FlatWatch).
7. **Both apps** — Buyer + Seller each serious run; claim→screenshot→Pass.
8. **Fix if broken** — wrong/empty results or broken experience → root-cause + Hobby archive redeploy if needed → re-prove **that single flow** before continuing the catalog.
9. **Hermes contract** — interact through semantic `locator` actions. Runtime `evaluate` is read-only diagnostics; never mutate inputs, click controls, or seed mandates with page JavaScript.

#### Settle gate (all required before next ask)

| Check | Pass signal |
| --- | --- |
| Spinner / pulling | No stuck “Pulling…” / Searching; or honest empty + timeout recorded |
| Tools | New `__samanthaTools` entry for this turn (`ok`/message); greetings = explicit no-tool |
| Errors | `__samanthaEvents` / `__samanthaErrors` checked; Realtime errors documented |
| Route / UI | Matches intent (search→`/results?q=…`, add→`/cart` line, etc.) |
| Results quality | Names/prices sensible for query; note crafts-for-bananas; prefer Atta/marker / our BPP when proving Seller |
| Console | `page_diag` / console empty or documented |
| Backend | When relevant: gateway `/api/ondc/status`, catalogs txn, `ensure-demo-item`, runtime curl/network |

#### Listen surfaces (Hermes while testing)

- `window.__samanthaTools` — `name`, `ok`, `navigateTo`, `cartAdds`, `navSuperseded`
- `window.__samanthaEvents` / `__samanthaErrors`
- Orb hint + reply text
- URL + headings + result grid / cart lines (screenshot → agent **Read**)
- Network: ONDC search/catalogs; `/api/agent/runtime` on handoff
- Optional: tiny Hermes dump of tools+events+url after wait — do not bloat product UI

### Friction → fix (2026-07-12 — do not re-learn)

| Friction | Fix |
| --- | --- |
| Empty Buyer catalog / bananas from **mock** | Mock fallback **removed** when `/api/ondc/status` enabled+configured; use network catalogs or honest empty |
| `ONDC_ENABLED` alone / local outbox stub | Need signed dispatch (`ondc_crypto`) + Render env BAP/BPP URIs + keys — see portfolio-deploy |
| Seller “onboarded” but Buyer never sees us | Need BPP `/ondc/np/seller/search` → `on_search` + Seller Vercel `/ondc/:path*` rewrite + **published** demo-commerce item (`POST /api/ondc/bpp/ensure-demo-item`) |
| Free wake → `published_item_count: 0` | Gateway lifespan auto-`ensure_preprod_marker_item` when `ONDC_ENABLED`; still OK to `POST …/bpp/ensure-demo-item` after cold start |
| **Results `Failed to fetch` / `ONDC gateway dispatch failed:`** | Render Free **hibernate-wake** (`x-render-routing: hibernate-wake-error` → 503 empty) + racing catalog polls. Fix: `fetchGateway`/`wakeGateway` retries in `protocolClient`; ResultsPage auto-retry ×3; stale `useApi` run-id. Wake gateway before operator find. |
| **Laggy Samantha search (double ONDC poll)** | Tool + ResultsPage both collected = 2× fanout. **Doctrine:** [`ondc-fetch-doctrine.md`](references/ondc-fetch-doctrine.md) — `dispatchBuyerSearch` once; page `ondcCollectFromTxn`; first paint not gated on prefer-BPP. |
| Hobby bake: `.env.local` loopback (`127.0.0.1:43102/43101`) in Vite | FQDN: `loopback.ts` guards + empty commerce base; leave `VITE_AGENT_CONTROL_PLANE_URL` empty + `/api/agent` rewrite → **gateway** (not FlatWatch — FQDN FlatWatch 401s portfolio `X-User-Id`) |
| **Inverse:** local `:43102` with FQDN `VITE_*` in Vite **process** env | Shell leak overrides `.env.local` → orb “Gateway unreachable” / “Realtime not configured” though `:43101` Realtime is fine. Fix: `start-dev.sh` / portfolio-browser troubleshooting § Local VITE bake |
| Samantha NL ask → “demo-commerce empty” though `GET …/buyer/search?q=atta` has rows | Full sentence was used as `q=` (API returns 0). **`catalogSearchQuery`** in `agentTools.ts` extracts keyword (`atta`). Seed: `POST …/demo-commerce/seller/items` + publish and/or `ensure-demo-item` |
| Local cart `fetch …:43102/api/cart` 500 / Vite proxy `ECONNREFUSED :3001` | Vite `/api` proxy pointed at dead `:3001`. Proxy to `:43101` (Buyer+Seller `vite.config.ts`, 2026-07-13) |
| Buyer **Cart error** `Refresh cart failed … 404` with `VITE_COMMERCE_DEMO_MODE=false` | `VITE_BUYER_COMMERCE_URL` set to Vite self (`:43102`/`:43103`) or empty-looking remote — gateway has **no** `/api/cart`. Leave `VITE_BUYER_COMMERCE_URL` / `VITE_API_BASE_URL` **unset**; local cart via `cartFailurePolicy` (treat self-ports as non-cart hosts; 404 → local fallback). Do **not** point commerce URL at Buyer/Seller origin |
| Seller **Orders unavailable** / `Failed to fetch` on `/orders` | `VITE_API_BASE_URL=http://localhost:3001` (dead) + demo mode false → legacy `/api/seller/orders`. Prefer `listCommerceSellerOrders` → `GET :43101/api/demo-commerce/seller/orders` (OrdersPage 2026-07-13). Leave `VITE_API_BASE_URL` empty; Vite `/api` → gateway. Restart Vite after `.env.local` edits |
| Realtime stalls on full ONDC poll (~20s) | Never block `search_catalog` tool turn on full poll; early `/results`; ResultsPage keeps pulling; host **12s** race + pending text queue |
| Chained `navigate_to`/`add_to_cart` yanked back to `/results` | `navEpoch` / `navSuperseded` — finishing `search_catalog` must not override later cart/checkout nav |
| Archive deploy+alias then stop | **Immediately** re-run operator-flows smoke (`B-HI`, `B-FIND-NL-ATTA` or `B-FIND-ATTA`, Seller nav) — deploy alone ≠ Pass |
| Banana search missing our BPP | PreProd **fanout variance** — prove with Atta / marker SKU or direct `POST ondcseller…/ondc/search`; do not declare Seller broken |
| `POST ondcseller…/ondc/on_search` → 405/SPA | Missing `/ondc/:path*` rewrite (same for Buyer callbacks) |
| Flip demo mode to “go live” | **Gate required** — `commerce_demo_mode_gate.py --allow-with-evidence`; unlocked 2026-07-12 (PreProd only; not prod UPI) |
| Render CLI 401 | Expired token — Hermes dashboard or `render login` |
| Vercel git deploy BLOCKED | HUF author — non-git `--archive=tgz` + alias |
| CI graders | `ondc_ci_graders.py --offline` **blocks** PR; FQDN `--live --soft` is `continue-on-error` — see [`test-inventory.md`](references/test-inventory.md) |

Gateway code: nested `aadharchain/` repo branch `codex/ondc-onboard-fqdn-20260712` (≥`1ba0a0c` — select/init/confirm).

## Thorough bar (hard — every serious run)

A run is **incomplete** unless all of the following are attempted with claim→screenshot→Pass (or Blocked + evidence of blocker):

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

## Live FQDN surfaces

| App | URL |
| --- | --- |
| Buyer | `https://ondcbuyer.aadharcha.in` |
| Seller | `https://ondcseller.aadharcha.in` |
| Gateway | `https://gateway.aadharcha.in` |

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
# sessions e.g. web-e2e-buyer / web-e2e-seller
python3 scripts/portfolio_browser.py closeout https://ondcbuyer.aadharcha.in/search
```

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

## Scripts (helpers, not the bar)

| Script | Role |
| --- | --- |
| `scripts/ondc_preprod_smoke.py` | Signed status/lookup/search (+ optional catalogs) against gateway |
| `scripts/hermes_ondc_testing_matrix.py` | **Primary** novice-operator Buyer+Seller matrix, semantic locators, lifecycle proof, screenshots, mandatory closeout |
| `scripts/hermes_checkout_retest.py` | Checkout/payment gate |
| `scripts/hermes_operator_visible_search.py` | FQDN operator: early `/results` + Seller smoke |
| `scripts/ondc_ci_graders.py` | Offline (PR) + live soft FQDN JSON/rewrite/bundle graders |

Legacy one-off Samantha scripts are diagnosis-only. They do not replace the primary matrix or its completion and closeout assertions.

## References

- [Operator flow catalog](references/operator-flows.md) — intents, journeys, tools, change-class map (**owner**)
- [Test inventory](references/test-inventory.md) — what we run, cadence, G/H/B/X gradeability, PR vs soft
- [Query matrix](references/query-matrix.md) — thin ask → ID index
- [PreProd network matrix](references/preprod-network-matrix.md) — BAP+BPP real-data gate
- [Integration gaps](references/integration-gaps.md)
- [Evidence template](references/evidence-template.md)
- [Matrix status](references/matrix-status.md)
- [UI surface audit](references/ui-surface-audit.md)
- Owners: `PRODUCTIDEA.md`, `IMPLEMENTATIONPLAN.md`, `TESTINGPLAN.md`, app `GOAL.md`

## Related skills

| Skill | When |
| --- | --- |
| [`portfolio-browser`](../portfolio-browser/SKILL.md) | WIP bridge, preflight, SSO, closeout |
| [`authentication`](../authentication/SKILL.md) | Auth0 / `VITE_IDENTITY_*` |
| [`portfolio-deploy`](../portfolio-deploy/SKILL.md) | Free/Hobby deploy, CI, Render/Vercel env (**names only**) |
| [`apisetu-partner-onboarding`](../apisetu-partner-onboarding/SKILL.md) | PreProd portal / keys |
