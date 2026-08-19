# Integration gaps vs product intent

**Owners:** `.session/docs/PRODUCTIDEA.md`, `.session/docs/IMPLEMENTATIONPLAN.md`, `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`.
**Current through:** 2026-08-01 local paused-agent checkout, Buyer tracking, and
signed LOG10-to-CommerceV1 dispatch correlation plus the 2026-07-31 Gate 3 Workbench lifecycle · **Evidence:** [`matrix-status.md`](matrix-status.md),
[`preprod-network-matrix.md`](preprod-network-matrix.md), and
[`evidence/preprod-postgres-search-20260724-135337.json`](evidence/preprod-postgres-search-20260724-135337.json).
Older CF1 and tool/runtime observations below are explicitly historical where
they were not part of the current gate.

Status legend: **Present** (demo-usable) · **Partial** · **Missing** · **External** (ops/onboarding).

| Integration | Intent | Local / code | Live FQDN | Gap |
| --- | --- | --- | --- | --- |
| **Auth0 / session principal** | Host identity → `principal:auth0:…` drives AgentGuard | Present (gateway + Sign in when `VITE_IDENTITY_AUTH_ENABLED`) | **Present** — `gateway.aadharcha.in` + `Domain=.aadharcha.in`; SPA **Sign out** + `/api/auth/me` authenticated | Closed 2026-07-12 (custom domain cutover) |
| **Local demo-continue** | Hermes/`sso demo` automation only | Present | Off in staging (`demo_continue:false`) — correct | None for FQDN PreProd |
| **Gateway logout** | Clear session | Present (`POST /api/auth/logout`) | **Pass** via POST; GET → 405 | UI Sign out must POST; GET hard-stop for naive probes |
| **AgentGuard evaluate/consume/pause/receipts** | Sole money/authority gate | **Present** — PostgreSQL CF1 owner; exact approval, replay rejection, pause/revoke and signed receipts passed. Current source distinguishes `actor: agent | user`; local rendered manual checkout succeeded while the shopping agent remained paused | **Present for prior Auth0 acceptance**; the actor split is not deployed | Deploy/FQDN verification remains open; real payment remains separate |
| **Mandate editor** | Edit limits + allowed actions, confirm | Present (M10) | compile/confirm **Pass** in checkout retest (mandate_id minted) | Seller thorough edit UI still owed |
| **Shared commerce exchange** | Seller publish ↔ Buyer discover same SKU; shared order id | **Present on CF1 PostgreSQL** — two unchanged-source publish/order/refund cycles passed; `/api/demo-commerce` is compatibility-only | **Partial** — deployed Buyer truthful zero-match and Seller protected surfaces passed; public cross-app order was not exercised | Multi-seller and two-sided public lifecycle remain open |
| **Simulated payment** | Labelled simulated; AG before pay | **Pass ×2** with balanced ledger and no duplicate effect | Not exercised on FQDN in the CF1 acceptance | Real payment remains excluded |
| **Signed receipt verify** | Third party can verify Intent Receipt | **Pass** — issue/verify, tamper rejection and current-source Buyer/Seller UI verification | Not re-exercised on FQDN in the CF1 acceptance | Public receipt verification remains unclaimed |
| **ONDC protocol (live Beckn)** | Search/confirm on network | **Partial** — signed lookup/search and configured-Seller discovery; select→init→confirm ACK plus `on_*` stubs; durable inbox/outbox | 2026-07-24 PostgreSQL retest proved signed delivery and correlated `on_search`; result remained blocked because the Seller catalog was empty | Non-empty Buyer result, full lifecycle, portal onboarding and official conformance remain open |
| **ONDC site verification** | Registry challenge | Present | FQDN verification meta **Pass**; NP status via **gateway** origin | FQDN `/ondc/np/*/status` may 404 JSON (not SPA) — rewrite OK if not HTML |
| **Samantha text tools** | Short chainable tools under mandate | **Present** — current-source `track_order` readback opened the latest local order and returned its persisted status without inventing missing courier data | **Historical 2026-07-12 pass** for search/add/nav/memory; `track_order` is not deployed | FQDN track-order verification remains open |
| **Buyer delivery tracking** | Read current order, vendor, tracking id and lifecycle | **Present and locally verified** — AgentGuard binds a deterministically selected signature-verified LOG10 1.2.5 P2P Immediate Delivery offer; a compliant selected `on_init` is required before contract-shaped confirm; persisted `on_confirm`/`on_status`/`on_track` reconcile idempotently into CommerceV1 through inbox lease/retry/dead-letter handling; Buyer, Seller, and Samantha project its normalized provider, verified HTTPS tracking, update, and ordered history | Current TapTap PreProd `init` returned a signed but nonconforming `on_init` missing `rider_check/inline_check_for_rider=yes`, so zero confirm/lifecycle actions ran. Current freeze `514777d6...` receipts: PostgreSQL gateway 301, Buyer 203, Seller 218, both builds, changed-file Ruff, and two unchanged-source rendered passes with paused-agent human checkout. [`packet`](evidence/preprod-taptap-interoperability-packet-20260802.json), [`local acceptance`](evidence/514777d6a5914fff837bf4aedc3249c903cedc3c6345a2774fbcd00fd4fc25ed/local-log10-acceptance-20260802.json) | External proof remains open: compliant signed LSP `on_init`, LSP-issued tracking/lifecycle, Workbench proof for this implementation, deployment, and FQDN proof. Local tracking/delivery values remain fixtures, not a physical shipment |
| **Samantha voice (Realtime)** | User-like mic/WebRTC | Code Present (M12) + orb re-probe fix | Gateway `configured:true`; the operator reports real voice already tested, but no retained modality-linked artifact is recorded here | Operator asked not to repeat microphone testing; do not promote the prior attestation beyond that boundary |
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
