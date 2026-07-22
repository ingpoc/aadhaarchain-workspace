# Operator flow catalog (Samantha text-mode)

**Owner:** this file. IDs are stable. Ledger rows use the same IDs in [`matrix-status.md`](matrix-status.md).  
**Thin ask index:** [`query-matrix.md`](query-matrix.md) — do not duplicate journey detail there.  
**Doctrine:** after every query, Pass requires screenshot (agent **Read**) + frontend route/DOM/tool state + backend owner state to agree. Orb text alone ≠ Pass. Frontend-owned local cart claims must also prove no premature backend order side effect.

Surfaces: local `:43102`/`:43103` or FQDN `ondcbuyer` / `ondcseller.aadharcha.in`. Browser owner: bundled `@chrome`; native Mac owner: bundled `@Computer`. Hermes WIP is legacy diagnostics only.

---

## Change-class → flows to re-run

| Change class | Must re-run |
| --- | --- |
| Realtime / orb UX / instructions | `B-HI`, `B-FIND-*`, `B-RESULT-GROUND`, `B-CHAINED`, `B-VOICE-*`, `S-HI`, `S-ORDER-*`, `S-VOICE-*` |
| `search_catalog` / early `/results` nav | `B-FIND-*`, `B-ADD-*`, `B-CHAINED` |
| `buyerCatalogCache` / network→cart | `B-FIND-*`, `B-RESULT-GROUND`, `B-ADD-*`, `B-CHECKOUT-*` |
| Cart / checkout UI | `B-CLEAR-CART`, `B-REMOVE`, `B-QUANTITY`, `B-NAV-CART`, `B-NAV-CHECKOUT`, `B-CHECKOUT-*` |
| AgentGuard / mandate / DATA_DIR | `B-CHECKOUT-*`, `B-AG-CONFIRM`, `S-ORDER-*`, `S-REFUND-*`, `S-AG-PAUSE`, `*-AG-*` |
| Seller publish / demo-commerce | `S-PUBLISH`, `B-FIND-*` (Atta/marker), `B-FIND-NL-ATTA` |
| Runtime / Cursor control plane | `B-RUNTIME`, `S-RUNTIME` |
| Auth0 / session cookie | `W-*-SPA-SESSION`, then commerce subset |
| Deploy / asset bake only | smoke: `B-HI`, `B-FIND-ATTA` or `B-FIND-NL-ATTA`, `S-NAV-CAT` |
| PreProd readiness / demo video | `W-B-FIND-NL-ATTA`, `W-B-AG-CONFIRM`, `W-S-AG-PAUSE` (+ Auth0) |

---

## Buyer flows

### B-HI — Greeting (no tools)

| | |
| --- | --- |
| **Intent / prompts** | “hi”, “hey Samantha”, “what can you help with?” |
| **Side** | Buyer |
| **UI journey** | Stay on current route (usually `/search`). **Must not** jump to `/results`. |
| **Tools** | None. Fail if `search_catalog` / `navigate_to` in `__samanthaTools`. |
| **Pass signals** | Brief reply; URL unchanged; screenshot of `/search` + orb reply |
| **Settle** | Reply visible; `__samanthaTools` unchanged (no new tool); not Connecting |
| **Code** | `SamanthaOrb` text path; Realtime instructions (“don’t tool on greeting”) |
| **Change map** | Realtime UX |

### B-THX — Thanks (no tools)

| | |
| --- | --- |
| **Intent / prompts** | “thanks”, “that’s all” |
| **Side** | Buyer |
| **UI journey** | No nav |
| **Tools** | None |
| **Pass signals** | Brief reply; no tool row |
| **Settle** | Reply done; no new tools |
| **Code** | Same as B-HI |
| **Change map** | Realtime UX |

### B-FIND-BANANA — Find bananas (visible early results)

| | |
| --- | --- |
| **Intent / prompts** | “find bananas”, “show me bananas”, “search for bananas” |
| **Side** | Buyer |
| **UI journey** | `/search` → **`/results?…&q=…` immediately** (before long ONDC poll finishes) → offers / pulling / list. Not silent background then only cart. |
| **Tools** | `search_catalog` (required). Early host nav in `SamanthaOrb` on tool start; `navigateTo` on tool result may refine query/`ondc_txn`. |
| **Pass signals** | Early pathname `/results`; page shows query / loading / network offers; `__samanthaTools` has `search_catalog` + `navigateTo` containing `/results`. Screenshot of results UI (not orb-only). |
| **Settle** | Early `/results?q=`; pulling stops **or** offers/honest empty; new `search_catalog` tool row; validate names vs bananas (note junk); `__samanthaErrors` clear |
| **Code** | `ondcbuyer/src/components/SamanthaOrb.tsx` (early nav); `agentTools.ts` `search_catalog`; `buyerCatalogCache`; `ResultsPage` |
| **Change map** | Realtime UX; search_catalog; catalog cache; deploy bake |
| **Note** | PreProd fanout may omit our BPP for “banana” — still Pass if network results UI loads; use `B-FIND-ATTA` for Seller marker. |

### B-FIND-ATTA — Find atta / marker SKU

| | |
| --- | --- |
| **Intent / prompts** | “search for atta”, “find atta flour”, “show Sharbati Atta” |
| **Side** | Buyer (proves Seller BPP when published) |
| **UI journey** | Same early `/results` as B-FIND-BANANA |
| **Tools** | `search_catalog` |
| **Pass signals** | Early `/results`; preferably Atta / demo marker in list when `ensure-demo-item` ran |
| **Settle** | Same as FIND-BANANA; prefer **AadhaarChain Whole Wheat Atta** / flour offers in grid |
| **Code** | Same as B-FIND-BANANA; gateway `POST /api/ondc/bpp/ensure-demo-item` |
| **Change map** | publish; search_catalog; PreProd |

### B-FIND-NL-ATTA — Natural-language grocery ask → Atta/cart

| | |
| --- | --- |
| **Intent / prompts** | “I need whole wheat atta under 200”, “get me atta for roti tonight”, grocery phrasing (not only “find atta”) |
| **Side** | Buyer |
| **UI journey** | Orb ask → `search_catalog` (query must extract catalog terms, not dump full NL) → early `/results` → optional `add_to_cart` → `/cart` line when asked to add |
| **Tools** | `search_catalog`; optional `add_to_cart` / `navigate_to` |
| **Pass signals** | Visible results and/or cart line for Atta/flour; `__samanthaTools` shows catalog query ≠ raw essay; screenshot of page (not orb-only) |
| **Settle** | Offers or cart settled; `catalogSearchQuery` / tool args sane |
| **Code** | `ondcbuyer/src/lib/agentTools.ts` `catalogSearchQuery`; `SamanthaOrb` |
| **Change map** | search_catalog; PreProd; Realtime UX |
| **Note** | PreProd readiness + demo-video beat. FQDN twin: `W-B-FIND-NL-ATTA`. |

### B-FIND-MILK / B-FIND-APPLE — Constrained find

| | |
| --- | --- |
| **Intent / prompts** | “find milk under 100”; “show Shimla apples” |
| **Side** | Buyer |
| **UI journey** | Early `/results?q=` |
| **Tools** | `search_catalog` |
| **Pass signals** | Results UI matching intent (or honest empty) |
| **Settle** | Offers settled; query match or honest empty noted |
| **Change map** | search_catalog |

### B-ADD-BANANA — Add to cart (visible line)

| | |
| --- | --- |
| **Intent / prompts** | “add banana to my cart”, “add the first banana”, “add that to cart” (after find) |
| **Side** | Buyer |
| **UI journey** | Prefer prior `/results` → `add_to_cart` → **`/cart`** with line visible |
| **Tools** | `add_to_cart` (item_id from prior `search_catalog` / cache). May chain `search_catalog` first. |
| **Pass signals** | Cart line (name/qty); `__samanthaTools` `add_to_cart` ok + `cartAdds`; screenshot `/cart` |
| **Settle** | Prior FIND settled with visible item; then `/cart` + line; `add_to_cart` ok (not search-only timeout) |
| **Code** | `resolveBuyerCartItem` / `buyerCatalogCache`; `SamanthaOrb` cartAdds → `addToCart` |
| **Change map** | catalog cache; cart; search_catalog |
| **Gap watch** | Network ids not in cache → empty cart (historical Fail); host 12s search race before ids → add Fail |

### B-RESULT-GROUND — Explain what is visibly available

| | |
| --- | --- |
| **Intent / prompts** | “what choices are on this page?”, “what does the first one cost?” after search |
| **Side** | Buyer |
| **UI journey** | Stay on `/results`; answer from rendered/cache-backed Host context |
| **Tools** | None required; do not search again when visible results are already supplied |
| **Pass signals** | Reply names a visible product and price; screenshot shows the same offer on `/results` |
| **Settle** | Reply and rendered offer agree; no false empty claim |
| **Code** | `buildOutboundUserText`; `waitForBuyerCatalogItems`; `buyerCatalogCache` |
| **Change map** | Realtime UX; results grounding |

### B-CLEAR-CART / B-REMOVE / B-QUANTITY — Change the live cart

| | |
| --- | --- |
| **Intent / prompts** | “empty my cart”; “remove that atta”; “make that two packs” |
| **Side** | Buyer |
| **UI journey** | Open `/cart` after the mutation so empty state or updated quantity is visible |
| **Tools** | `clear_cart`; `remove_from_cart`; `set_cart_quantity` |
| **Pass signals** | Matching tool succeeds and `/cart` visibly shows empty state or requested quantity |
| **Settle** | Host cart mutation completed; refreshed cart matches tool evidence |
| **Code** | `runBuyerTool`; Buyer `SamanthaOrb`; cart context/mutations |
| **Change map** | cart UI; Realtime UX |

### B-NAV-CART / B-NAV-CHECKOUT / B-NAV-CONFIG / B-NAV-ORDERS

| | |
| --- | --- |
| **Intent / prompts** | “go to my cart”; “go to checkout”; “open config”; “show my orders” |
| **Side** | Buyer |
| **UI journey** | Target: `/cart`, `/checkout`, `/config`, `/orders` |
| **Tools** | `navigate_to` |
| **Pass signals** | URL + page chrome match; screenshot |
| **Settle** | Pathname = target; `navigate_to` ok; no yank back to `/results` (`navSuperseded` ok on stale search) |
| **Code** | `coerceBuyerNavPath`; early nav on `navigate_to` in orb |
| **Change map** | cart/checkout UI; Realtime UX |

### B-MEM-ORG — Remember preference

| | |
| --- | --- |
| **Intent / prompts** | “remember I prefer organic” |
| **Side** | Buyer |
| **UI journey** | Optional `/config` to show memory |
| **Tools** | `remember_preference`; optional `navigate_to` |
| **Pass signals** | Tool ok; preference visible on `/config` when shown |
| **Settle** | `remember_preference` ok; optional `/config` shows preference |
| **Change map** | Realtime UX; memory store |

### B-CHECKOUT-OK / B-CHECKOUT-OVER

| | |
| --- | --- |
| **Intent / prompts** | “checkout / pay”; over-limit amount ask |
| **Side** | Buyer |
| **UI journey** | `/checkout` or `/orders/{id}` with Paid+receipt **or** AG need_approval/deny card on page |
| **Tools** | `checkout_commit` (+ host session_id / amount fill) |
| **Pass signals** | Page Paid + receipt id **or** AgentGuard decision card — not orb-only |
| **Code** | `agentGuardCheckout`; `writeCheckoutOutcome`; mandate limits |
| **Change map** | AG; cart; DATA_DIR |

### B-AG-CONFIRM — Confirm mandate (Buyer)

| | |
| --- | --- |
| **Intent / prompts** | UI: Preferences & AgentGuard / Config → **Confirm mandate** (not orb-only) |
| **Side** | Buyer |
| **UI journey** | Signed-in principal → `/config` or AG panel → Confirm mandate → status shows confirmed/active |
| **Tools** | Host UI (Hermes `click_text` / selector); optional `ensure` under the hood |
| **Pass signals** | Screenshot: Confirm succeeded or mandate active; not Unsigned / Sign-in not configured |
| **Settle** | Principal bound; mandate confirm control reflects success |
| **Code** | Buyer AG UI; gateway agents/ensure + mandate confirm |
| **Change map** | AG; Auth0/session; DATA_DIR |
| **Note** | PreProd readiness. FQDN: `W-B-AG-CONFIRM`. Auth0 required on FQDN. |

### B-EMPTY — Honest empty

| | |
| --- | --- |
| **Intent / prompts** | “search for purple unicorn cereal” |
| **Side** | Buyer |
| **UI journey** | `/results` with empty / no matches copy |
| **Tools** | `search_catalog` |
| **Pass signals** | Honest empty UI (no mock grocery when ONDC ready) |
| **Change map** | search_catalog; demo-mode gate |

### B-CHAINED — Follow-on ask during/after search (no reload)

| | |
| --- | --- |
| **Intent / prompts** | Immediately after find: “go to my cart”; “add the first … to cart”; “find bananas” (second query) |
| **Side** | Buyer |
| **UI journey** | Prior early `/results` still active → follow-on must **send** (not draft-stuck) → target route/UI (`/cart` line or new results). No page reload between asks. |
| **Tools** | `navigate_to` / `add_to_cart` / `search_catalog` as intent requires |
| **Pass signals** | `fill_send` ok (not `send_disabled`); visible target UI; `__samanthaTools` for intent. **Draft stall alone ≠ Pass** if cart/results UI never lands. |
| **Settle** | First FIND settled (or accepted in-flight); second ask send_ok; final path = intent; `navSuperseded` if search still finishing |
| **Code** | `SamanthaOrb` pending text queue + tool timeout; early `/results` nav must not permanently block later nav |
| **Change map** | Realtime UX; search_catalog; cart |
| **Gap watch** | Stale search `navigateTo` after cart/nav — `navEpoch`/`navSuperseded` + no early-nav yank off committed paths; finishing `search_catalog` must not yank off `/cart` |

### B-RUNTIME — Long handoff

| | |
| --- | --- |
| **Intent / prompts** | “plan weekly groceries under 2000”, multi-step shopping plan |
| **Side** | Buyer |
| **UI journey** | Stay off `/agent`. Orb “I've started… I'll let you know” (or equiv). Later completion/outcome when available. |
| **Tools** | `delegate_to_runtime_agent` — **not** a pile of short tools for the whole plan |
| **Pass signals** | Handoff hint shot; path ≠ `/agent`; tool ok in `__samanthaTools` |
| **Settle** | `delegate_to_runtime_agent` ok; path ≠ `/agent`; handoff hint; no Concurrent response stall without retry |
| **Code** | `samanthaRuntimeHandoff`; gateway `/api/agent/*`; Vercel rewrite |
| **Change map** | runtime |

### B-VOICE-* — Voice twins

Same commerce intents via Realtime mic. Pass: connected session + **visible** tool outcome. Hermes without mic → **Blocked** (text still required).

---

## Seller flows

### S-HI — Greeting

| | |
| --- | --- |
| **Intent / prompts** | “hi” |
| **Side** | Seller |
| **UI journey** | Stay `/dashboard` (or current); no tools |
| **Pass signals** | Brief reply; no nav |
| **Settle** | Reply; no tools; stay on dashboard |
| **Change map** | Realtime UX |

### S-NAV-CAT / S-NAV-ORD / S-NAV-AG

| | |
| --- | --- |
| **Intent / prompts** | “open catalog”; “show orders”; “open agentguard” |
| **Side** | Seller |
| **UI journey** | `/catalog`, `/orders`, `/agentguard` |
| **Tools** | `navigate_to` |
| **Pass signals** | URL + page UI screenshot |
| **Settle** | Pathname match; `navigate_to` ok |
| **Code** | `coerceSellerNavPath` |
| **Change map** | Seller UI; Realtime UX |

### S-AG-PAUSE — Pause agent (Seller)

| | |
| --- | --- |
| **Intent / prompts** | UI on `/agentguard`: **Pause agent** (signed-in) |
| **Side** | Seller |
| **UI journey** | Auth0 (FQDN) or local demo principal → `/agentguard` → Pause agent → paused status visible |
| **Tools** | Host UI click; gateway pause API |
| **Pass signals** | Screenshot: agent paused / protected actions denied; not Trust Unsigned |
| **Settle** | Pause reflected on page; subsequent protected action blocked or need_approval as designed |
| **Code** | Seller AgentGuard page; gateway pause |
| **Change map** | AG; Auth0/session; DATA_DIR |
| **Note** | PreProd readiness. FQDN: `W-S-AG-PAUSE`. |

### S-PUBLISH — Publish item

| | |
| --- | --- |
| **Intent / prompts** | “publish a test atta 1kg at 80 rupees”, “add a catalog item …” |
| **Side** | Seller |
| **UI journey** | Prefer `/catalog` with new item visible |
| **Tools** | `catalog_publish` |
| **Pass signals** | Tool ok; catalog shows item when feasible |
| **Settle** | `catalog_publish` ok; optional item visible on `/catalog` |
| **Change map** | publish; demo-commerce |

### S-ORDER-ACCEPT / S-ORDER-REJECT / S-ORDER-FULFIL — Order lifecycle

| | |
| --- | --- |
| **Intent / prompts** | “accept the newest paid order”; “reject the newest remaining paid order”; “mark that accepted order fulfilled” |
| **Side** | Seller |
| **UI journey** | Samantha executes under AgentGuard → `/orders/{id}` with Accepted, Cancelled, or Delivered visible |
| **Tools** | `accept_order`; `reject_order`; `mark_order_fulfilled` |
| **Pass signals** | Matching tool ok; canonical AgentGuard action/receipt in tool evidence; order page shows the resulting status |
| **Settle** | Tool decision is honest and rendered status matches the executed transition |
| **Code** | Seller `agentTools`; `executeProtectedAction`; demo-commerce transition executor |
| **Change map** | AG; orders; demo-commerce |

### S-RUNTIME — Long handoff

| | |
| --- | --- |
| **Intent / prompts** | Background ops triage / refund attention |
| **Side** | Seller |
| **UI journey** | Stay off `/agent` |
| **Tools** | `delegate_to_runtime_agent` |
| **Pass signals** | Handoff hint; path ≠ `/agent` |
| **Settle** | `delegate_to_runtime_agent` ok; not `/agent` |
| **Change map** | runtime |

### S-REFUND-OK / S-REFUND-OVER

| | |
| --- | --- |
| **Intent / prompts** | “refund order X for 500”; over-limit refund |
| **Side** | Seller |
| **UI journey** | Orders/AG outcome visible |
| **Tools** | Prefer **`refund_issue`** when order id known; navigate+runtime is weaker Pass |
| **Pass signals** | AG allow/receipt or need_approval/deny on page or clear tool decision |
| **Change map** | AG; orders |

### S-MEM — Seller memory

| | |
| --- | --- |
| **Intent / prompts** | “remember I prefer brief confirmations” |
| **Side** | Seller |
| **Tools** | `remember_preference` |
| **Pass signals** | Tool ok; visible on `/agentguard` when UI shows it |
| **Change map** | Realtime UX |

### S-RUNTIME — Bulk triage handoff

| | |
| --- | --- |
| **Intent / prompts** | “triage today’s orders and flag refunds over limit”, long ops ask |
| **Side** | Seller |
| **UI journey** | Not `/agent`; handoff hint |
| **Tools** | `delegate_to_runtime_agent` |
| **Pass signals** | Same as B-RUNTIME |
| **Change map** | runtime |

### S-VOICE-* — Voice twins

Same as Buyer voice bar.

---

## Live FQDN twins

Prefix **`W-`** (e.g. `W-B-FIND-BANANA`, `W-S-NAV-CAT`). Same Pass bar on `https://ondc*.aadharcha.in`. Auth: Auth0 session (or Blocked with Sign-in evidence). Local loopback: `sso demo` only (automation). **PreProd gate = `W-*` on FQDN.**

---

## Session minimum (operator text-mode)

Acceptance is performed first by the experiment-refined pair in [`../SKILL.md`](../SKILL.md): one task-focused novice customer/operator and one combined UX/accessibility reviewer. They use visible UI and natural language only, cap reports, and distinguish App Fail from Tooling Blocked. The implementation agent and fixture-aware scripts may replay these flows for diagnosis, but their results are supporting evidence rather than novice-customer acceptance. Buyer and Seller authenticated runs are sequential because the shared WIP Chrome profile has one gateway session cookie.

**Buyer:** `B-HI` → `B-FIND-NL-ATTA` or `B-FIND-ATTA` (prove **early `/results`**) → `B-ADD-*` if cache allows → `B-AG-CONFIRM` when signed-in → nav cart/checkout → checkout if cart non-empty → `B-RUNTIME`.  
**Seller:** `S-HI` → nav catalog/orders/AG → `S-AG-PAUSE` when signed-in → `S-PUBLISH` or `S-REFUND-*` → `S-RUNTIME` as feasible.  
**PreProd FQDN:** same with `W-*` + Auth0 — readiness gate before demo-video record.  
**Both apps** every serious run.

Append results to [`matrix-status.md`](matrix-status.md). New durable gaps only → [`integration-gaps.md`](integration-gaps.md). New intents discovered in the wild → **add a row here** (do not orphan in chat).
