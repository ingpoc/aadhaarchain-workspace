# Integration gaps vs product intent

**Owners:** `PRODUCTIDEA.md`, `IMPLEMENTATIONPLAN.md`, `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`.  
**Current through:** 2026-07-22 CF1 release checkpoint · **Evidence:** [`matrix-status.md`](matrix-status.md) and [`evidence/cf1-release-e95340-checkpoint-20260722.json`](evidence/cf1-release-e95340-checkpoint-20260722.json). Older tool/runtime observations below are explicitly historical where they were not part of the CF1 gate.

Status legend: **Present** (demo-usable) · **Partial** · **Missing** · **External** (ops/onboarding).

| Integration | Intent | Local / code | Live FQDN | Gap |
| --- | --- | --- | --- | --- |
| **Auth0 / session principal** | Host identity → `principal:auth0:…` drives AgentGuard | Present (gateway + Sign in when `VITE_IDENTITY_AUTH_ENABLED`) | **Present** — `gateway.aadharcha.in` + `Domain=.aadharcha.in`; SPA **Sign out** + `/api/auth/me` authenticated | Closed 2026-07-12 (custom domain cutover) |
| **Local demo-continue** | Hermes/`sso demo` automation only | Present | Off in staging (`demo_continue:false`) — correct | None for FQDN PreProd |
| **Gateway logout** | Clear session | Present (`POST /api/auth/logout`) | **Pass** via POST; GET → 405 | UI Sign out must POST; GET hard-stop for naive probes |
| **AgentGuard evaluate/consume/pause/receipts** | Sole money/authority gate | **Present** — PostgreSQL CF1 owner; exact approval, replay rejection, pause/revoke and signed receipts passed | **Present for Auth0 acceptance** — protected Buyer/Seller surfaces passed on the deployed source; public mutation/receipt replay was outside this checkpoint | Real-payment and production persistence operations remain separate gates |
| **Mandate editor** | Edit limits + allowed actions, confirm | Present (M10) | compile/confirm **Pass** in checkout retest (mandate_id minted) | Seller thorough edit UI still owed |
| **Shared commerce exchange** | Seller publish ↔ Buyer discover same SKU; shared order id | **Present on CF1 PostgreSQL** — two unchanged-source publish/order/refund cycles passed; `/api/demo-commerce` is compatibility-only | **Partial** — deployed Buyer truthful zero-match and Seller protected surfaces passed; public cross-app order was not exercised | Multi-seller and two-sided public lifecycle remain open |
| **Simulated payment** | Labelled simulated; AG before pay | **Pass ×2** with balanced ledger and no duplicate effect | Not exercised on FQDN in the CF1 acceptance | Real payment remains excluded |
| **Signed receipt verify** | Third party can verify Intent Receipt | **Pass** — issue/verify, tamper rejection and current-source Buyer/Seller UI verification | Not re-exercised on FQDN in the CF1 acceptance | Public receipt verification remains unclaimed |
| **ONDC protocol (live Beckn)** | Search/confirm on network | **Partial** — signed lookup/search and configured-Seller discovery; select→init→confirm ACK plus `on_*` stubs; durable inbox/outbox | Latest protocol-specific FQDN evidence remains the 2026-07-16 matrix row | Full lifecycle, portal onboarding and official conformance remain open |
| **ONDC site verification** | Registry challenge | Present | FQDN verification meta **Pass**; NP status via **gateway** origin | FQDN `/ondc/np/*/status` may 404 JSON (not SPA) — rewrite OK if not HTML |
| **Samantha text tools** | Short chainable tools under mandate | Present | **Historical 2026-07-12 pass** after SPA session + ready-wait — search/add/nav/memory proven with screenshots | Current-source runtime breadth was outside the CF1 gate |
| **Samantha voice (Realtime)** | User-like mic/WebRTC | Code Present (M12) + orb re-probe fix | Gateway `configured:true`; UI **“Text mode ready (no mic)”** (config Pass); mic missing in Hermes | Operator mic for true voice Pass; false “not configured” race **fixed** 2026-07-12 |
| **Runtime agent (Cursor)** | Long handoff via `delegate_to_runtime_agent` | Present (M11) | **Historical 2026-07-12 pass** — gateway `/api/agent/*` + Vercel rewrite; browser W-B/W-S runtime and SSE evidence | Current-source runtime breadth and Free cold-start behavior were outside the CF1 gate |
| **Buyer tools** | `search_catalog`, `navigate_to`, `add_to_cart`, `checkout_commit`, `remember_preference`, `delegate_to_runtime_agent` | Present | **Historical 2026-07-12 pass** for search/add/cart/checkout/order detail | Current-source broad tool-chain retest remains outside CF1 |
| **Hobby Vite bake / agent plane** | FQDN must not call loopback or FlatWatch agent | Present (`loopback.ts` + empty control plane → gateway rewrite) | Required on archive deploys | FlatWatch FQDN 401s portfolio `X-User-Id` |
| **Seller tools** | `navigate_to`, `catalog_publish`, `refund_issue`, `remember_preference`, `delegate_to_runtime_agent` | Present | **Historical 2026-07-12 pass** for navigation/publish/memory/runtime | Current-source broad tool-chain retest remains outside CF1 |
| **Orb text after long search** | Chain asks without stall | **Mitigated** | Root: Realtime waited ~20s for `search_catalog` | Tool poll 3×1.2s; 12s host timeout; queue send while connecting. Buyer redeployed |
| **Wallet / Solana hangar** | Non-goal for AG acceptance | Hangar only | **Cleared** — no Wallet KYC / Solflare primary CTA on FQDN | None |
| **Shared signed receipt across apps** | Same receipt identity Buyer↔Seller | Partial | Missing FQDN proof | After two-sided commerce |
| **MeitY DigiLocker / live NPCI** | Out of Token Nxt demo | Deferred | N/A | Non-goal |

## Must-test coverage map (serious run)

See [`SKILL.md`](../SKILL.md) § Thorough bar and [`query-matrix.md`](query-matrix.md). Every serious web/local run must cover Auth (or documented Skip), commerce path, **all Samantha tools**, **voice when Realtime configured**, **runtime handoff**, Seller mirror, AgentGuard honesty — claim→screenshot→Pass.
