---
name: portfolio-browser
description: >-
  Legacy deterministic AadhaarChain browser harness via Hermes Chrome WIP.
  Use only when explicitly requested or after approved fallback from the
  bundled Chrome plugin. Scripts: portfolio_browser.py,
  parallel_smoke_wip.py. Parallel smoke = 0-token scout then mini fixer. SSO mutex. AgentGuard acceptance uses `sso demo` (no wallet); burner/Solflare are hangar-only.
  Triggers: portfolio browser, Hermes WIP, SSO, Solflare, smoke, parallel smoke,
  multi-app, fixer_packets, preflight, reviewer-ready, durable lease, closeout,
  page diag, console errors.
  Not for partner onboarding workflow ownership (ONDC portal / Setu.co / MeitY) —
  that skill owns the rails; this skill is the Hermes browser driver only.
---

# Portfolio browser

> **Legacy harness.** Bundled `@chrome` is the default browser owner and bundled
> `@Computer` is the default native Mac owner. This skill preserves deterministic
> WIP Hermes replay, diagnostics, and old evidence reproduction only.

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

**Standing rule:** append durable browser/WIP findings to this skill + [`references/troubleshooting.md`](references/troubleshooting.md) / validation ledger; **no secrets** in markdown.

**Legacy window policy (mandatory when this harness is selected):** one working agent → **one** Hermes WIP Chrome window. Two concurrent agents → two windows via distinct `HERMES_AGENT_ID` values. Never invent a new `task_id` / `session_name` per script step — that opens orphan windows. Default lease id is `portfolio-browser` (see `scripts/wip_hermes.py`). End work with `portfolio_browser.py closeout` which now closes **all** active agent leases, not a fixed tab-name list.

**Partner onboarding:** ONDC Participant Portal / Setu.co / MeitY DigiLocker → workflow owned by [`.cursor/skills/apisetu-partner-onboarding/`](../apisetu-partner-onboarding/SKILL.md) + `PRODUCTION-READINESS.md`. Bundled `@chrome` drives current browser work; this skill is only the legacy replay driver. MeitY rail remains **paused** inside that skill.

**Related:** Samantha/UX matrix → [`ondc-testing`](../ondc-testing/SKILL.md). Auth0 → [`authentication`](../authentication/SKILL.md). FQDN/CI deploy → [`portfolio-deploy`](../portfolio-deploy/SKILL.md). PreProd demo video (Hermes cursor dry-run → record) → [`demo-video-recording`](../demo-video-recording/SKILL.md).
## Agent context rule (always)

On every Hermes page under test, treat **UI + console + backend** as one compact context.
Do not conclude pass/fail from UI alone.

**Bridge = Hermes Chrome WIP only** — `wip_hermes.py` forces  
`HERMES_CHROME_BRIDGE_SOCKET=…/hermes-chrome-cursor-wip/run/chrome-bridge.sock`.  
Load unpacked: `…/hermes-chrome-cursor-wip/deploy/extension`. Do **not** use Codex live Hermes.

**WIP host ownership:** the canonical runtime owner is the
[`hermes-chrome` skill](/Users/gurusharan/plugins/hermes-chrome-cursor-wip/skill/SKILL.md).
Before recovery, run
`/Users/gurusharan/plugins/hermes-chrome-cursor-wip/scripts/ensure-wip-native-host.sh`
and use its exact Chrome profile. Do not hard-code a profile in this project
skill, open a different browser's extension page, or duplicate-install the WIP
extension.

**SOCKET_DOWN:** evidence first (`ls`/`lsof` WIP sock + discovered host/profile + manifest `path` + extension **service worker Active vs Inactive**) before repairing. Two distinct causes: (1) SW Inactive → native host died (manifests already `native_host_wip.sh`); (2) classic path trap (`path` → `native_host.py` → binds `~/.hermes/run`). Recover only in the profile returned by `ensure-wip-native-host.sh`: open `chrome://extensions` and reload **Hermes Chrome Bridge (Cursor WIP)**. Do **not** route to another browser/profile, install a second copy, rewrite manifests to `.py`, or switch to live `~/.hermes`. Details: [`references/troubleshooting.md`](references/troubleshooting.md) § WIP socket trap.

**Local stack (2026-07-13):** FQDN `VITE_*` process bake, Vite dying after Shell teardown, SSO on `chrome://` error tabs, orb toggle, `/api`→`:3001` — see troubleshooting table + § Local VITE bake. PreProd UX bar: [`ondc-testing`](../ondc-testing/SKILL.md). Demo video record gate: [`demo-video-recording`](../demo-video-recording/SKILL.md).

**Cursor / wrong-app traps:** Hermes WIP pointer starts at `opacity: 0` until first move/click; “no cursor” usually = wrong host app (Comet vs Chrome) or window behind IDE — see troubleshooting § Cursor visibility.

**Seller Dispatch tracking prompt:** `window.prompt` — Hermes owns it. Batch `click_text` + `dialog_handle` + `promptText`. Do not reload while open; frozen CS reply ≠ missing script. OS-native / Chrome-shell jobs → `$macos-cua` per hermes-chrome `multi-agent.md` ownership table.

| Signal | Source | How |
| --- | --- | --- |
| **UI** | WIP `page_context` | url, title, headings, buttons |
| **Console** | `page_diag` (lane/SSO) or `console_tail` (parallel smoke) | errors / warns / rejections / failed fetch |
| **Backend** | `logs/*.log` | recent error/exception lines |

```bash
# Standalone compact diag for current/active page
python3 scripts/portfolio_browser.py diag
python3 scripts/portfolio_browser.py diag --url http://127.0.0.1:43100/verify
```

`page_diag` starts native `network_watch` before navigation, then reads native `console_tail` and `network_summary`; it does not monkey-patch console/fetch or mutate the page through `evaluate`.
If `page_diag.ok` is false, surface `page_diag.issues` before retrying or claiming success.

## Multi-app orchestration (cost/quality)

**When:** parallel web + buyer + seller smoke / console triage; main agent stays orchestrator.

**Skip:** single-app debug (use `diag` / one lease); SSO (use mutex lane below).

| Role | Does | Tool |
| --- | --- | --- |
| Main | Run scout script, merge packets, advise | no routine browse |
| Scout | Parallel smoke + console | `scripts/parallel_smoke_wip.py` (**0 tokens**) |
| Fixer | Unique `fixer_packets` only | mini model; no browser unless proof needed |
| SSO | Burner / Solflare | this skill `lane` / `sso` — **mutex** |

```bash
export HERMES_CHROME_BRIDGE_SOCKET=/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
python3 scripts/parallel_smoke_wip.py
python3 scripts/parallel_smoke_wip.py --require-rpc   # wallet/balance UI
```

**Do:** script before browser LLMs; ignore extension noise (`ObjectMultiplex`, `MaxListeners`); treat balance/`Failed to fetch` as `:8899` env → `./aadharsolana/scripts/ensure-validator.sh` (getHealth); one retry on stalled lease.

**Don’t:** fan out 3+ browser LLMs for routine smoke; parallelize SSO with other browser agents; “fix” env with product code; `pkill` / `rm -rf aadharsolana/.local-validator` for browser lanes (on-chain fresh ledger only: `start-validator.sh --reset`, mutex); `close_tab` on WIP leases (use closeout).

Evidence: `.optimization/orchestration-experiments.jsonl`.

## Workflow

Validated lane (2× manual pass, 2026-07-06) — see [`references/validation-ledger.md`](references/validation-ledger.md).

```
lane  →  preflight → smoke → sso → closeout   (one preflight; auto-starts stack)
review → preflight → sso → reviewer-ready → actor → closeout
```

| Step | Required | Pass |
| --- | --- | --- |
| **lane** | Full browser validation | exit 0; smoke JSON + SSO + closeout |
| **preflight** | Before ad-hoc browser work | exit 0, `tier: hermes`, HTTP 2xx |
| **reviewer-ready** | After audience login, before a blind reviewer | same session/window/tab across two visual reads separated by idle; signed-in marker; clean closeout |
| **test** | `smoke` and/or `sso` | JSON pass signals below |
| **closeout** | After browser work | exit 0, `bridge ready=True` |
| **diag** | When debugging / after any failed step | compact JSON; `ok: true` or actionable `issues` |

Preflight auto-starts `./scripts/start-dev.sh` when the stack is down. Burner SSO: preflight runs `ensure-validator.sh` (JSON-RPC `getHealth` on `:8899`). FlatWatch `.env` (incl. `CURSOR_API_KEY`) must be loaded into the process via `start-dev.sh` — file present ≠ loaded.

Hermes session leases are process-local. Python child runners must use
`scripts/wip_hermes.py::run_with_session_preflight` immediately before guarded
`run`; a successful shell preflight does not supply the child process lease.

## Commands

```bash
# API-only (stack health + gateway pytest; validated 2×)
./scripts/verify-portfolio.sh

# Validated full lane (preferred SSO regression)
python3 scripts/portfolio_browser.py lane burner seller

# Ad-hoc steps (each runs preflight unless PORTFOLIO_SKIP_PREFLIGHT=1)
python3 scripts/portfolio_browser.py preflight
python3 scripts/portfolio_browser.py smoke
python3 scripts/portfolio_browser.py sso burner [seller|buyer|all]
python3 scripts/portfolio_browser.py sso solflare [seller|buyer]
python3 scripts/portfolio_browser.py commerce seller|buyer [--fixture]

# After the correct audience SSO and before dispatching a blind reviewer
python3 .cursor/skills/portfolio-browser/scripts/reviewer_ready.py \
  --url http://127.0.0.1:43103/dashboard --expected-marker "Sign out"

# AgentGuard (Token Nxt) — Hermes judged lanes validated 2026-07-11 evening
python3 scripts/portfolio_browser.py agentguard seller [--fixture]
python3 scripts/portfolio_browser.py agentguard buyer [--fixture]
# Two-sided: use unique --run-id via hermes_two_sided_commerce.py for consecutive proofs
python3 scripts/portfolio_browser.py two-sided [--fixture]
python3 scripts/hermes_two_sided_commerce.py --fixture --run-id "ag-$(date +%s)-a"
# M12 Samantha / checkout user journeys → ondc-testing skill
python3 scripts/hermes_ondc_testing_matrix.py buyer|seller

python3 scripts/portfolio_browser.py closeout [leave_url]
python3 scripts/portfolio_browser.py diag [--url URL]

# API + browser automation
./scripts/verify-portfolio.sh --browser
```

**SSO stays mutex** with AgentGuard lanes (do not parallelize). Parallel smoke / multi-agent isolation leases are OK without SSO.

## Pass signals

| Command | Pass |
| --- | --- |
| `smoke` | JSON `"success": true`, titles include **ONDC Buyer** + **ONDC Seller** |
| `reviewer_ready.py` | `status: "reviewer_ready"`; identical session/window/tab across both reads; two non-empty screenshots; expected URL and signed-in marker; owned session absent after closeout |
| `sso solflare` | `"signed_in": true`, buttons include **Sign out** |
| `sso burner` | exit 0, Hermes lands on app with **Sign out** |
| `agentguard seller --fixture` | JSON `"success": true`; checks policy/allow/need/replay/pause/deny |
| `agentguard buyer --fixture` | JSON `"success": true`; checks allow/approval/consume/replay/pause/deny |
| `two-sided` / `hermes_two_sided_commerce.py` | `"success": true` with **unique** `run_id` per consecutive pass |
| `diag` | `ok: true` (no console/backend errors); else fix `issues` first |
| Multi-agent isolation (optional gate) | `HERMES_CHROME_BRIDGE_SOCKET=…/run/chrome-bridge.sock python3 …/hermes-chrome-cursor-wip/plugin/hermes_chrome/tests/test_multi_agent_isolation.py` exit 0 |
## Progressive disclosure

- Preflight/reviewer-ready/closeout checks: [`references/lifecycle.md`](references/lifecycle.md)
- Failures: [`references/troubleshooting.md`](references/troubleshooting.md)
- Parallel multi-app (0-token scout): this file § Multi-app orchestration + `scripts/parallel_smoke_wip.py`

Harden with the **Elon Algorithm** (`question → make work → verify → delete → optimize → automate → encode`) and require its source-frozen final gate.

## Related skills

| Skill | Role |
| --- | --- |
| [`ondc-testing`](../ondc-testing/SKILL.md) | Samantha claim→screenshot matrix (local + web FQDN) |
| [`portfolio-deploy`](../portfolio-deploy/SKILL.md) | CI/CD, Free/Hobby FQDN deploy — not required for local lanes |
| [`authentication`](../authentication/SKILL.md) | Auth0 / demo SSO principals |
| [`apisetu-partner-onboarding`](../apisetu-partner-onboarding/SKILL.md) | Portal rails; this skill is driver only |
