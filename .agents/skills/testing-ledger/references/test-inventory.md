# ONDC / AgentGuard test inventory

**Owner:** this file. Operator journeys → [`operator-flows.md`](operator-flows.md). CI wiring → [`portfolio-deploy`](../../../../.cursor/skills/portfolio-deploy/references/ci-cd.md).
**Legend (gradeability):**

| Class | Meaning |
| --- | --- |
| **G** Gradable now | Deterministic script/pytest; fail-closed; no LLM |
| **H** Gradable with small harness | Needs thin HTTP/bundle probe (shipped or 1-file) |
| **B** Browser/Hermes only | Visible UI / Samantha / claim→screenshot |
| **X** External / Blocked | OTP, mic, prod ONDC, paid infra |

Cadence: **PR** (blocks merge) · **Post** (post-deploy / soft FQDN) · **Night** (manual thorough) · **Ops** (operator `/ondc-testing`).

---

## Inventory

| ID / surface | What | Class | Cadence | Owner |
| --- | --- | --- | --- | --- |
| `verify-portfolio --ci` | Gateway pytest (AgentGuard, auth, ONDC routes); `--skip-contract` in the unique gateway job | **G** | PR | `scripts/verify-portfolio.sh` · `ci.yml` gateway |
| AgentGuard contract parity | Canonical vs Buyer/Seller/gateway fixtures | **G** | PR | `scripts/verify_agentguard_contract_sync.py` · `ci.yml` agentguard-contract |
| Buyer npm lint/typecheck/test/build | Unit + build | **G** | App PR | `ondcbuyer` app CI — **not** Portfolio CI |
| Seller npm lint/typecheck/test/build | Unit + build | **G** | App PR | `ondcseller` app CI — **not** Portfolio CI |
| Local ship gate | Offline graders before commit/deploy | **G** | Ops | `scripts/local-ship-gate.sh` |
| gitleaks | Secret scan | **G** | PR | `ci.yml` secret-scan |
| AgentGuard fixture lanes | `portfolio_browser.py agentguard …` | **B** | Ops | portfolio-browser |
| `commerce_demo_mode_gate` | Refuse demo flip without evidence | **G** | PR + Ops | `scripts/commerce_demo_mode_gate.py` |
| `ondc_ci_graders` offline | Gate check + 2026-08-19 P0 test scanners | **G** | PR | `scripts/ondc_ci_graders.py --offline` |
| Buyer P0 scanners | Pause exclusive, guest cart/checkout lock, address collapse, Agent Guard deep link | **G** | PR | `buyer_p0_regression_tests` in `ondc_ci_graders.py --offline` |
| Seller P0 scanners | Empty store setup, refund copy, dashboard stay, unauth return-to | **G** | PR | `seller_p0_regression_tests` in `ondc_ci_graders.py --offline` |
| Gateway P0 scanners | Short-id GET, refund `need_approval`, store GET 200 draft | **G** | PR | Fail-closed `gateway_p0_regression_tests_missing` if aadhaar-chain#7 tests disappear |
| `ondc_ci_graders` live soft | FQDN health/JSON/rewrite/bundle | **H** | Post (non-blocking PR) | `ondc_ci_graders.py --live --soft` |
| FQDN vs vercel.app `index-*.js` | Custom domain serving this production | **H** | Post fail-closed on deploy; PR advisory `--soft` | `ondc_ci_graders.py --bundle-parity` |
| Gateway `/api/health` | Wake / liveness | **H** | Post | graders + deploy post-probe |
| `/api/ondc/status` | enabled+configured JSON | **H** | Post | graders |
| `/api/realtime/status` | `configured:true` JSON | **H** | Post | graders |
| `/api/agent/runtime` + `X-User-Id` | JSON not HTML | **H** | Post | graders |
| Buyer/Seller `/api/agent/*` rewrite | JSON via Vercel rewrite | **H** | Post | graders |
| Buyer/Seller `/ondc/*` not SPA HTML | Catch missing rewrite | **H** | Post | graders |
| FQDN bundle `VITE_COMMERCE_DEMO_MODE` | Must be `"false"` in asset | **H** | Post | graders |
| `ondc_preprod_smoke` | Signed lookup/search/catalog; optional fail-closed item+quote select→init→confirm | **H** | Post / Ops | `scripts/ondc_preprod_smoke.py --search atta --order` (`--ci` soft only) |
| BPP `ensure-demo-item` + published count | Marker catalog | **H** | Ops | gateway API; skill friction table |
| Operator flows B-* / S-* | Samantha text journeys | **B** | Ops / Night | [`operator-flows.md`](operator-flows.md) · Hermes scripts |
| Buyer `track_order` + fulfilment timeline | Latest/specified order readback, no invented courier, history projection and rendered order detail | **G** + **B** | PR / Ops | Buyer unit/build plus local bundled-browser journey |
| Seller dispatch provider capture | Require actual provider + tracking id before guarded dispatch | **G** + **B** | PR / Ops | Seller unit/build; rendered lifecycle needs an owning Seller principal |
| Signed LOG10 delivery reconciliation | Deterministically select a signature-verified LOG10 1.2.5 P2P Immediate Delivery offer; reject nonconforming or mismatched `on_init`; build allowlisted confirm; persist-before-ACK and reconcile duplicate/stale/skipped/cancelled lifecycle callbacks into CommerceV1; project one Buyer/Seller/Samantha view | **G** + **B** | PR / Ops | Current freeze `514777d6...`: PostgreSQL gateway 301; Buyer 203/build; Seller 218/build; changed-file Ruff; unchanged-source rendered Pass 1+2 with paused-agent human checkout. External compliant LSP lifecycle remains required. [`packet`](evidence/preprod-taptap-interoperability-packet-20260802.json), [`local acceptance`](evidence/514777d6a5914fff837bf4aedc3249c903cedc3c6345a2774fbcd00fd4fc25ed/local-log10-acceptance-20260802.json) |
| Independent customer portfolio | Three full-mission actors: post-login Buyer novice, Seller merchant, and cross-app UI/UX + accessibility smoke; no subagent per step; one mission verdict; screenshot read; no internals | **B** | Ops / release | [`independent-customer-gate.md`](independent-customer-gate.md) |
| Early `/results` visible search | UX ship prove | **B** | Ops | `hermes_operator_visible_search.py` |
| Thorough FQDN matrix | Full Buyer+Seller | **B** | Night | `hermes_fqdn_e2e_thorough.py` |
| Voice mic / WebRTC | Realtime voice Pass | **X**→**B** | Ops | Blocked in Hermes without mic |
| Auth0 OTP fresh browser | Universal Login | **X** | Ops | authentication skill |
| Live UPI / prod ONDC order | Non-goal Token Nxt | **X** | — | do not claim |
| Two-sided FQDN shared order | Cross-app commerce | **B** / **H** | Night | integration-gaps |
| Signed receipt verify UI | Third-party verify | **B** | Night | integration-gaps |

---

## Operator flow → gradeability

| Flow ID | Class | Notes |
| --- | --- | --- |
| B-HI / S-HI | **B** | Need `__samanthaTools` empty + route |
| B-FIND-* (early `/results`) | **B** (+ **H** search API) | UI early-nav Hermes; network search API soft-gradable |
| B-ADD-* | **B** | Cart DOM; cache harness future |
| B-NAV-* / S-NAV-* | **B** | Route after tool |
| B-TRACK-* | **G** + **B** | Read-only `track_order`; Buyer order detail owns current status and timeline |
| B-CHECKOUT-* / S-REFUND-* | **B** + **G** AG pytest | Page Paid/AG card browser; evaluate/deny in pytest |
| B-RUNTIME / S-RUNTIME | **B** + **H** runtime JSON | Handoff UI browser; `/api/agent/runtime` grader |
| B-VOICE-* / S-VOICE-* | **X**/Blocked Hermes | Realtime status **H**; mic **X** |
| S-PUBLISH | **B** + **H** ensure-demo | Catalog UI + published_item_count |
| W-* FQDN twins | **B** / **H** | Same split |

---

## Block PR vs soft probe

| Blocks PR (`ci.yml`) | Soft / `continue-on-error` | Manual Ops only |
| --- | --- | --- |
| gitleaks, AgentGuard contract, gateway pytest+Postgres, `ondc_ci_graders --offline` | `ondc_ci_graders --live --soft`, `--bundle-parity --soft` on PR, optional `ondc_preprod_smoke --ci` | Hermes operator/thorough, agentguard fixture, voice mic |

Buyer/Seller vitest blocks **app** PRs, not Portfolio CI.

Deploy `post-probe` keeps `--live --soft` (network flake ≠ billing upgrade) and **fail-closes** `--bundle-parity` (FQDN hash must match `*.vercel.app`).
