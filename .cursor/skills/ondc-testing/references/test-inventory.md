# ONDC / AgentGuard test inventory

**Owner:** this file. Operator journeys → [`operator-flows.md`](operator-flows.md). CI wiring → [`../../portfolio-deploy/references/ci-cd.md`](../../portfolio-deploy/references/ci-cd.md).  
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
| `verify-portfolio --ci` | Gateway pytest (AgentGuard, auth, ONDC routes) | **G** | PR | `scripts/verify-portfolio.sh` · `ci.yml` gateway |
| Buyer npm lint/typecheck/test/build | Unit + build | **G** | PR | `ondcbuyer` · `ci.yml` |
| Seller npm lint/typecheck/test/build | Unit + build | **G** | PR | `ondcseller` · `ci.yml` |
| gitleaks | Secret scan | **G** | PR | `ci.yml` secret-scan |
| AgentGuard fixture lanes | `portfolio_browser.py agentguard …` | **B** | Ops | portfolio-browser |
| `commerce_demo_mode_gate` | Refuse demo flip without evidence | **G** | PR + Ops | `scripts/commerce_demo_mode_gate.py` |
| `ondc_ci_graders` offline | Gate check + contract smoke | **G** | PR | `scripts/ondc_ci_graders.py --offline` |
| `ondc_ci_graders` live soft | FQDN health/JSON/rewrite/bundle | **H** | Post (non-blocking PR) | `ondc_ci_graders.py --live --soft` |
| Gateway `/api/health` | Wake / liveness | **H** | Post | graders + deploy post-probe |
| `/api/ondc/status` | enabled+configured JSON | **H** | Post | graders |
| `/api/realtime/status` | `configured:true` JSON | **H** | Post | graders |
| `/api/agent/runtime` + `X-User-Id` | JSON not HTML | **H** | Post | graders |
| Buyer/Seller `/api/agent/*` rewrite | JSON via Vercel rewrite | **H** | Post | graders |
| Buyer/Seller `/ondc/*` not SPA HTML | Catch missing rewrite | **H** | Post | graders |
| FQDN bundle `VITE_COMMERCE_DEMO_MODE` | Must be `"false"` in asset | **H** | Post | graders |
| `ondc_preprod_smoke` | Signed status/lookup/(search) | **H** | Post / Ops | `scripts/ondc_preprod_smoke.py` (`--ci` soft) |
| BPP `ensure-demo-item` + published count | Marker catalog | **H** | Ops | gateway API; skill friction table |
| Operator flows B-* / S-* | Samantha text journeys | **B** | Ops / Night | [`operator-flows.md`](operator-flows.md) · Hermes scripts |
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
| B-CHECKOUT-* / S-REFUND-* | **B** + **G** AG pytest | Page Paid/AG card browser; evaluate/deny in pytest |
| B-RUNTIME / S-RUNTIME | **B** + **H** runtime JSON | Handoff UI browser; `/api/agent/runtime` grader |
| B-VOICE-* / S-VOICE-* | **X**/Blocked Hermes | Realtime status **H**; mic **X** |
| S-PUBLISH | **B** + **H** ensure-demo | Catalog UI + published_item_count |
| W-* FQDN twins | **B** / **H** | Same split |

---

## Block PR vs soft probe

| Blocks PR (`ci.yml`) | Soft / `continue-on-error` | Manual Ops only |
| --- | --- | --- |
| gitleaks, gateway pytest, buyer/seller npm, `ondc_ci_graders --offline` | `ondc_ci_graders --live --soft`, optional `ondc_preprod_smoke --ci` | Hermes operator/thorough, agentguard fixture, voice mic |

Deploy `post-probe` should call `--live --soft` (network flake ≠ billing upgrade).
