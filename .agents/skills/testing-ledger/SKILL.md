---
name: testing-ledger
description: >-
  Customer-gate lane for ONDC Buyer (:43102) / Seller (:43103) and FQDNs:
  Samantha + AgentGuard blind operator journeys, matrix status, settle–validate–next.
  Doctrine/modes/locks → testing-framework. Triggers: testing-ledger, ONDC, Samantha,
  Buyer Seller matrix, checkout payment, independent customer gate. Bridge:
  bundled Chrome plugin by default; portfolio-browser WIP is legacy diagnostics.
---

# Testing ledger (ONDC customer-gate adapter)

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

**Lane:** customer gate (not drain/prove). Global doctrine: `~/.agents/skills/testing-framework` — modes A/B/C, one owner per contested runtime, capsules. Do not paste those invariants here.

**Default posture:** this skill owns settle–validate–next journey evidence, not browser behavior. Browser work follows bundled `@chrome`; portfolio-browser WIP is an explicitly selected legacy lane. Fix on main and **re-run the whole affected journey**. Use mode **C** after the same tip fails twice; mode **A** only when cataloging unknown fail surface before batch fix.

## Owners

| Concern | Owner |
| --- | --- |
| Historical execution log | [`references/matrix-status.md`](references/matrix-status.md) |
| Checklist-linked acceptance criteria and gate status | [`references/checklist-gates.json`](references/checklist-gates.json) |
| Immutable run evidence | [`references/evidence/`](references/evidence/) |
| Product items and implementation status | [`.session/checklist/checklist.json`](../../../.session/checklist/checklist.json) |
| Generated session snapshot | [`.session/testing/testing-ledger.json`](../../../.session/testing/testing-ledger.json) |
| Generated product-lead view | [`.session/html/checklist.html`](../../../.session/html/checklist.html) — testing is disclosed inside each checklist card |
| Flow catalog | [`references/operator-flows.md`](references/operator-flows.md) |
| Ask → flow ID | [`references/query-matrix.md`](references/query-matrix.md) |
| Protocol + thorough bar | [`references/operator-protocol.md`](references/operator-protocol.md) |
| Samantha catalog HIT/MISS/GHOST | [`references/samantha-catalog-validation.md`](references/samantha-catalog-validation.md) |
| Blind gate profiles/budgets | [`references/independent-customer-gate.md`](references/independent-customer-gate.md) |
| PreProd Beckn | [`references/preprod-network-matrix.md`](references/preprod-network-matrix.md) |
| Gaps / inventory | [`references/integration-gaps.md`](references/integration-gaps.md), [`references/test-inventory.md`](references/test-inventory.md) |
| Browser UI / existing Chrome state | Bundled `@chrome` plugin |
| Legacy Hermes replay / diagnostics | [`portfolio-browser`](../../../.cursor/skills/portfolio-browser/SKILL.md) |
| Auth0 | [`authentication`](../../../.cursor/skills/authentication/SKILL.md) |
| Deploy / CI graders | [`portfolio-deploy`](../../../.cursor/skills/portfolio-deploy/SKILL.md) |
| Samantha tool design | [`agent-runtime-design`](../../../.cursor/skills/agent-runtime-design/SKILL.md) |

**Standing:** retain immutable run evidence, append the historical execution log,
then update the affected gate status in checklist-gates.json. Run the single
checklist refresh command; never edit either session snapshot. The generated
testing link mirrors current `product_status`, and currentness validation must
reject any mismatch. The snapshot contains card links only—not duplicated prose
ledgers. **No secrets.** Do not flip `VITE_COMMERCE_DEMO_MODE` without evidence
gate. Do not claim live ONDC network orders without proof. Fixture/matrix scripts
≠ independent customer acceptance.

Every launch-chain checklist item must have a stable-ID entry in
`references/checklist-gates.json`. Product status remains owned by
`.session/checklist/checklist.json`; the gate file owns only acceptance criteria
and gate status. Every checklist card renders that link or explicitly reports
that testing criteria are not linked. A checklist item can be `complete` only
when implementation evidence exists, acceptance criteria are linked, and every
blocking gate is `passed` or `not_required`. Q1 owns the current-source release
receipt; CF2/CF3 complete when their own blocking lifecycle gates pass.

For local rendered AgentGuard proof, reacquire the demo session after every
gateway restart, then read the current agent and mandate before executing. A
paused agent must remain fail-closed until explicitly resumed, and a newer draft
under the stable mandate ID must be confirmed before its actions are expected to
be authorized. Never bypass either state in the fixture or UI.

### Local gateway / CF acceptance preconditions (fail closed)

- Never migrate or run local CF3 schema work against Render. Export
  `DATABASE_URL=postgresql://gurusharan@127.0.0.1:5432/postgres` before
  `./scripts/start-dev.sh gateway` (overrides `gateway/.env`). Script refuses
  Render/remote hosts unless `ALLOW_REMOTE_DATABASE_URL=1`.
- Detached restart: `start-dev.sh` only (setsid double-fork). Plain `nohup`
  dies with the agent shell.
- After restart, verify OpenAPI has the routes under test (e.g. `/seller/store`,
  `/seller/items` POST/PATCH/import) before claiming UI bugs.
- Transient Seller **mandate not found** after gateway restart → Settings →
  Agent Guard → Refresh + Save (not a product gap). Then retry publish.
- Gateway pytest: `cd aadharchain/gateway && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p asyncio` (or `./scripts/verify-portfolio.sh --ci`). Bare pytest loads broken host plugins.

### Browser bridge for acceptance

Default: bundled `@chrome`. Comet Control lease rules:
[`independent-customer-gate.md`](references/independent-customer-gate.md)
(one durable session per campaign; concurrent A4 vs B5 = distinct ids). Repo
ports: `:43101` / `:43102` / `:43103`.

### ONDC portal readback vs mail

Authenticated portal UI readback ≠ provider-mail readback. Cite the dated
portal evidence (e.g. `evidence/ondc-a4-portal-readback-20260817.json`); do not
promote mail corroboration to current portal proof. Keys / Render deploy /
GoDaddy DNS / registry submit remain operator-authorized only (GoDaddy=DNS,
Render=runtime). Workbench start + RET10 IGM flow: `~/.agents/skills/ondc`
(Workbench lane). Official docs vs GitHub TOC: same skill **Sources** lane.
This app's identities: `.ondc/binding.json`.

### Public ONDC route / IGM standing

- Nested protocol code lives in **`aadharchain/`** git, not workspace HEAD.
  Exact-commit deploy to existing `identity-aadhar-gateway-main` (auto-deploy
  off). Owner: `portfolio-deploy`.
- Empty-body public POST **422/400 = route live**; **404 = missing route**.
  Health `GET /api/health`.
- Keep `/api/ondc/track` on Buyer dispatch (do not regress to
  select/init/confirm-only).
- Workbench mock `on_confirm` mints a new `message_id`. BAP **ACK if
  `transaction_id` matches** confirm/lifecycle outbox; log mismatch; persist
  callback id. Do not NACK that as a pairing failure. Outbound **BPP still
  echoes request `message_id`**. A Workbench COMPLETE ERROR pairing string is
  not live-NACK proof — confirm Render POST `/ondc/np/buyer/on_confirm`.
- Inbound `on_status`: accept camelCase `subscriberID` and Authorization
  `keyId`.
- IGM dispatch must correlate/create a local commerce issue from a confirmed
  ONDC order (`issue_id` or confirm-outbox `order_id`/`transaction_id`).
  Unknown order still 404. Re-read `aadharchain/gateway/app/ondc_routes.py`
  before claiming public behavior.
- Workbench IGM issues may not appear on Auth0 Buyer UI unless the order principal matches; protocol success ≠ customer-visible success.
- Workbench mock `on_issue` / `on_issue_resolved` is `400 Missing issue actions`
  unless BAP `issue` includes `issue_actions.complainant_actions` (OPEN, then
  CLOSE) and BPP `on_issue`/`on_issue_status` includes `respondent_actions`.
  Reuse CommerceV1 legal transitions and existing sign/outbox/inbox. Do not
  invent a parallel IGM store. Do not block IGM resolve on mock `on_confirm`
  ERROR.
- Apply RESOLVED/CLOSED from `issue_actions` (respondent_actions / complainant
  CLOSE) when signed `issue.status` is null; walk unique legal hops
  (`acknowledged` → `resolution_proposed` → `accepted` → `closed`). Do not add
  illegal edges. Protocol-order Buyer URLs (`/orders/B5091e6b53`) must 404 when
  no commerce order exists — never 500.
- BPP `issue_status` / `on_issue_status` must follow commerce terminal state (closed/accepted/resolution_proposed → RESOLVED), not stay PROCESSING because the BAP body is issue_id-only.
- Seller issue card must show the same public issue id the Buyer sees.
- Workbench subscriber-scoped IGM rows are not the Auth0 user’s Buyer/Seller issue.
- B5 completes on preprod/Auth0 signed IGM plus Buyer/Seller-visible outcome; production IGM is A4/B8, not a B5 hang.

### CF3 catalog path facts (as of 2026-08-17 — re-read code)

Gap scanners must re-read current Seller/gateway code. Do **not** claim CSV /
draft / staff missing from historical chat. Present as of 2026-08-17: draft CSV
import, session draft POST/PATCH, Save draft, publish preview before
`seller.catalog.publish`, diagnostics via `buildSellerDiagnostics`, staff roles.
Does not mark CF3 complete. Evidence stamp:
[`references/matrix-status.md`](references/matrix-status.md).

| Mutex | Rule |
| --- | --- |
| Authenticated browser session | One prove/gate owner; Buyer and Seller blind actors **serial** on shared cookie |
| SSO demo | Mutex with other portfolio SSO lanes |
| Gateway `:43101` | Keep up during Auth0; do not restart mid-login |

## Surfaces

| App | Local | FQDN |
| --- | --- | --- |
| Buyer | `http://127.0.0.1:43102` | `https://ondcbuyer.aadharcha.in` |
| Seller | `http://127.0.0.1:43103` | `https://ondcseller.aadharcha.in` |
| Gateway | `http://127.0.0.1:43101` | `https://gateway.aadharcha.in` |

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
| `python3 scripts/ondc_ci_graders.py --offline` | PR-blocking offline graders (demo gate + P0 test scanners) |
| `python3 scripts/ondc_ci_graders.py --live` | Read-only FQDN probes. `--protocol-search` requires a separately authorized search gate. |
| `python3 scripts/ondc_ci_graders.py --bundle-parity` | Optional live probe: FQDN `index-*.js` vs `*.vercel.app`. Fail-closed on deploy. |

### ONDC portal readback

When the operator says an ONDC Chrome/Comet tab is signed in, claim that exact tab
from the current open-tab listing. Do not open a replacement tab. Capture the
signed-in identity, organisation, profile rows, URL, and timestamp before any
reload or navigation; the portal can lose its client session on reload. Record
the result as point-in-time provider evidence, never as continuous login or
production approval. Portal edits, Continue actions, keys, terms, and
submissions remain separate operator-authorized actions.

**Portal ≠ mail:** authenticated portal UI readback is not interchangeable with
provider-mail readback. Mail may corroborate; only dated portal evidence counts
as portal proof (A4 2026-08-17:
[`evidence/ondc-a4-portal-readback-20260817.json`](references/evidence/ondc-a4-portal-readback-20260817.json)).

Refresh both ledgers and the product-lead view after recording evidence:

```bash
python3 scripts/generate_checklist.py
python3 scripts/generate_checklist.py --check-current
```

Return capsules: inline JSON matching global testing-framework capsule schema, or evidence JSON under `references/evidence/`.

## First commands

```bash
# 1. Bridge + apps
# portfolio-browser preflight / start-dev as needed
# Local CF: export DATABASE_URL=postgresql://gurusharan@127.0.0.1:5432/postgres
# before ./scripts/start-dev.sh gateway (see Local gateway preconditions above)

# Gateway proof always routes through the project-owned clean pytest lane.
# Bare pytest may load unrelated host plugins such as anchorpy/pytest_xprocess.
./scripts/verify-portfolio.sh --ci
# Manual equivalent from aadharchain/gateway:
# PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q -p asyncio

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
| `~/.agents/skills/ondc` | Workbench / host / keys / **Sources TOC** / Lifecycle (IGM contract, RSP, logs) |
| `.ondc/binding.json` | This app's public subscriber identities |
| `apisetu-partner-onboarding` | Portal / GST field maps |
| `demo-video-recording` | Demo dry-run → record |
| `review-customer-ui-ux` | Header/attraction UX gate (separate from commerce matrix) |
