---
name: ondc-testing
description: >-
  Customer-gate lane for ONDC Buyer (:43102) / Seller (:43103) and FQDNs:
  Samantha + AgentGuard blind operator journeys, matrix status, settle–validate–next.
  Doctrine/modes/locks → testing-framework. Triggers: ondc-testing, Samantha,
  Buyer Seller matrix, checkout payment, independent customer gate. Bridge:
  bundled Chrome plugin by default; portfolio-browser WIP is legacy diagnostics.
---

# ONDC testing (customer-gate adapter)

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

**Lane:** customer gate (not drain/prove). Global doctrine: `~/.agents/skills/testing-framework` — modes A/B/C, one owner per contested runtime, capsules. Do not paste those invariants here.

**Default posture:** settle–validate–next blind journeys through bundled `@chrome`; use bundled `@Computer` only for native Mac UI. Fix on main and **re-run the whole affected journey**. The portfolio-browser WIP lane is explicit legacy fallback/diagnosis only. Use mode **C** after the same tip fails twice; mode **A** only when cataloging unknown fail surface before batch fix.

## Owners

| Concern | Owner |
| --- | --- |
| Pass record | [`references/matrix-status.md`](references/matrix-status.md) |
| Flow catalog | [`references/operator-flows.md`](references/operator-flows.md) |
| Ask → flow ID | [`references/query-matrix.md`](references/query-matrix.md) |
| Protocol + thorough bar | [`references/operator-protocol.md`](references/operator-protocol.md) |
| Samantha catalog HIT/MISS/GHOST | [`references/samantha-catalog-validation.md`](references/samantha-catalog-validation.md) |
| Blind gate profiles/budgets | [`references/independent-customer-gate.md`](references/independent-customer-gate.md) |
| PreProd Beckn | [`references/preprod-network-matrix.md`](references/preprod-network-matrix.md) |
| Gaps / inventory | [`references/integration-gaps.md`](references/integration-gaps.md), [`references/test-inventory.md`](references/test-inventory.md) |
| Browser UI / existing Chrome state | Bundled `@chrome` plugin + `browser-plugin-preflight` |
| Legacy Hermes replay / diagnostics | [`portfolio-browser`](../portfolio-browser/SKILL.md) |
| Auth0 | [`authentication`](../authentication/SKILL.md) |
| Deploy / CI graders | [`portfolio-deploy`](../portfolio-deploy/SKILL.md) |
| Samantha tool design | [`agent-runtime-design`](../agent-runtime-design/SKILL.md) |

**Standing:** append Pass/Fail/Blocked + screenshot paths to matrix-status. **No secrets.** Do not flip `VITE_COMMERCE_DEMO_MODE` without evidence gate. Do not claim live ONDC network orders without proof. Fixture/matrix scripts ≠ independent customer acceptance.

## Mutexes (contested → stop)

| Mutex | Rule |
| --- | --- |
| Authenticated Chrome profile/session | One prove/gate owner; Buyer and Seller blind actors **serial** on shared cookie |
| SSO demo | Mutex with other portfolio SSO lanes |
| Gateway `:43101` | Keep up during Auth0; do not restart mid-login |

## Surfaces

| App | Local | FQDN |
| --- | --- | --- |
| Buyer | `http://127.0.0.1:43102` | `https://ondcbuyer.aadharcha.in` |
| Seller | `http://127.0.0.1:43103` | `https://ondcseller.aadharcha.in` |
| Gateway | `http://127.0.0.1:43101` | `https://gateway.aadharcha.in` |

Legacy diagnostic helper only:

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
python3 scripts/portfolio_browser.py closeout https://ondcbuyer.aadharcha.in/search
```

## Prove / record entry

| Command | Role |
| --- | --- |
| Load [`operator-protocol.md`](references/operator-protocol.md) then [`independent-customer-gate.md`](references/independent-customer-gate.md) | Acceptance bar |
| Append [`matrix-status.md`](references/matrix-status.md) | Record Pass/Fail/Blocked |
| `python3 scripts/ondc_preprod_smoke.py` | Fail-closed Beckn smoke; `--order` for paid-order path |
| `python3 scripts/hermes_ondc_testing_matrix.py` | Diagnostic matrix — **not** blind acceptance |
| `python3 scripts/hermes_ondc_blind_operator.py` | Deterministic replay aid — **not** context-isolated gate evidence |
| `python3 scripts/hermes_checkout_retest.py` | Checkout/payment helper |
| `python3 scripts/hermes_operator_visible_search.py` | FQDN early `/results` smoke |
| `python3 scripts/ondc_ci_graders.py --offline` | PR soft/offline graders |

Return capsules: inline JSON matching global testing-framework capsule schema, or evidence JSON under `references/evidence/`.

## First commands

```bash
# 1. Bridge + apps
# portfolio-browser preflight / start-dev as needed

# 2. Local demo principal (AG lanes)
python3 scripts/portfolio_browser.py sso demo buyer   # or seller — serial

# 3. Customer gate
# Follow references/independent-customer-gate.md (Buyer → Seller → UX; one mission per lease)

# 4. Record + closeout
# Append matrix-status.md; portfolio_browser closeout
```

## Diagnostic routing (on failure only)

| Failure class | Open |
| --- | --- |
| Search/fanout | [`ondc-fetch-doctrine.md`](references/ondc-fetch-doctrine.md) |
| Product gap | [`integration-gaps.md`](references/integration-gaps.md) |
| Browser/env | portfolio-browser troubleshooting |
| Deploy/alias/CI | portfolio-deploy |

## Related

| Skill | When |
| --- | --- |
| `testing-framework` | Modes, locks, capsules, lane split |
| `portfolio-browser` | WIP bridge, preflight, SSO, closeout |
| `authentication` | Auth0 / session principal |
| `portfolio-deploy` | Free/Hobby deploy, CI |
| `apisetu-partner-onboarding` | PreProd portal / keys |
| `demo-video-recording` | Demo dry-run → record |
| `review-customer-ui-ux` | Header/attraction UX gate (separate from commerce matrix) |
