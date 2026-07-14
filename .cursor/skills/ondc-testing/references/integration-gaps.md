# Integration gaps vs product intent

**Owners:** `PRODUCTIDEA.md`, `IMPLEMENTATIONPLAN.md`, `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`.  
**Date:** 2026-07-12 · **Evidence:** live FQDN probes + matrix § Realtime 17:48 + DATA_DIR/checkout 17:56.

Status legend: **Present** (demo-usable) · **Partial** · **Missing** · **External** (ops/onboarding).

| Integration | Intent | Local / code | Live FQDN | Gap |
| --- | --- | --- | --- | --- |
| **Auth0 / session principal** | Host identity → `principal:auth0:…` drives AgentGuard | Present (gateway + Sign in when `VITE_IDENTITY_AUTH_ENABLED`) | **Present** — `gateway.aadharcha.in` + `Domain=.aadharcha.in`; SPA **Sign out** + `/api/auth/me` authenticated | Closed 2026-07-12 (custom domain cutover) |
| **Local demo-continue** | Hermes/`sso demo` automation only | Present | Off in staging (`demo_continue:false`) — correct | None for FQDN PreProd |
| **Gateway logout** | Clear session | Present (`POST /api/auth/logout`) | **Pass** via POST; GET → 405 | UI Sign out must POST; GET hard-stop for naive probes |
| **AgentGuard evaluate/consume/pause/receipts** | Sole money/authority gate | Present (M0–M7) | **Present** — ensure **200**; checkout `allow` + receipt on FQDN after `DATA_DIR=/tmp/aadharchain-data` | Ephemeral `/tmp` lost on spin-down (expected Free); no Disk |
| **Mandate editor** | Edit limits + allowed actions, confirm | Present (M10) | compile/confirm **Pass** in checkout retest (mandate_id minted) | Seller thorough edit UI still owed |
| **Shared commerce exchange** | Seller publish ↔ Buyer discover same SKU; shared order id | Present locally (`/api/demo-commerce`) | **Partial** — Buyer cart/demo catalog works; Seller live catalog empty; cross-app order not proven on FQDN | Two-sided FQDN loop still open |
| **Simulated payment** | Labelled simulated; AG before pay | Present | **Pass** — Paid + `rcpt_90c6dec41ab8400f` (matrix 17:56) | Signed receipt verify still open |
| **Signed receipt verify** | Third party can verify Intent Receipt | Partial (M5 routes/hooks) | Not exercised on FQDN this run | Browser proof of verify UI still owed |
| **ONDC protocol (live Beckn)** | Search/confirm on network | Present PreProd BAP + BPP | **Partial** — Buyer signed search+on_search Pass; Seller BPP `search`→`on_search` from published demo-commerce (no mock grocery) — see `preprod-seller-bpp-*.json` | select/confirm; demo gate; prod |
| **ONDC site verification** | Registry challenge | Present | FQDN verification meta **Pass**; NP status via **gateway** origin | FQDN `/ondc/np/*/status` may 404 JSON (not SPA) — rewrite OK if not HTML |
| **Samantha text tools** | Short chainable tools under mandate | Present | **Pass** after SPA session + ready-wait — search/add/nav/memory proven with screenshots | Continue Seller tools |
| **Samantha voice (Realtime)** | User-like mic/WebRTC | Code Present (M12) + orb re-probe fix | Gateway `configured:true`; UI **“Text mode ready (no mic)”** (config Pass); mic missing in Hermes | Operator mic for true voice Pass; false “not configured” race **fixed** 2026-07-12 |
| **Runtime agent (Cursor)** | Long handoff via `delegate_to_runtime_agent` | Present (M11) | **Present** — gateway `/api/agent/*` + Vercel rewrite; browser **W-B-RUNTIME / W-S-RUNTIME Pass** (`web-e2e-thorough-20260712-205518.json`); SSE `RUNTIME_OK` earlier | Free cold-start wake |
| **Buyer tools** | `search_catalog`, `navigate_to`, `add_to_cart`, `checkout_commit`, `remember_preference`, `delegate_to_runtime_agent` | Present | early `/results` Pass; **add→cart Pass** 23:20; **checkout+order-detail Pass** 23:27 (`Paid` + `rcpt_c9a68660930b4fba`, not unavailable) | B-CHAINED cart-while-pulling retest still owed |
| **Hobby Vite bake / agent plane** | FQDN must not call loopback or FlatWatch agent | Present (`loopback.ts` + empty control plane → gateway rewrite) | Required on archive deploys | FlatWatch FQDN 401s portfolio `X-User-Id` |
| **Seller tools** | `navigate_to`, `catalog_publish`, `refund_issue`, `remember_preference`, `delegate_to_runtime_agent` | Present | nav/publish/mem/runtime **Pass** (op-visible 21:42) | Prefer explicit `refund_issue` when order exists |
| **Orb text after long search** | Chain asks without stall | **Mitigated** | Root: Realtime waited ~20s for `search_catalog` | Tool poll 3×1.2s; 12s host timeout; queue send while connecting. Buyer redeployed |
| **Wallet / Solana hangar** | Non-goal for AG acceptance | Hangar only | **Cleared** — no Wallet KYC / Solflare primary CTA on FQDN | None |
| **Shared signed receipt across apps** | Same receipt identity Buyer↔Seller | Partial | Missing FQDN proof | After two-sided commerce |
| **MeitY DigiLocker / live NPCI** | Out of Token Nxt demo | Deferred | N/A | Non-goal |

## Must-test coverage map (serious run)

See [`SKILL.md`](../SKILL.md) § Thorough bar and [`query-matrix.md`](query-matrix.md). Every serious web/local run must cover Auth (or documented Skip), commerce path, **all Samantha tools**, **voice when Realtime configured**, **runtime handoff**, Seller mirror, AgentGuard honesty — claim→screenshot→Pass.
