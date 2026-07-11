---
name: portfolio-browser
description: >-
  Browser-test AadhaarChain portfolio (43100–43103) via Hermes Chrome WIP only
  (never ~/.codex or ~/.hermes live). Scripts: portfolio_browser.py,
  parallel_smoke_wip.py. Parallel smoke = 0-token scout then mini fixer. SSO mutex.
  Triggers: portfolio browser, Hermes WIP, SSO, Solflare, smoke, parallel smoke,
  multi-app, fixer_packets, preflight, closeout, page diag, console errors.
  Not for MeitY API Setu / DigiLocker partner signup — use apisetu-partner-onboarding.
---

# Portfolio browser

**Out of scope:** MeitY API Setu / MeriPehchaan / DigiLocker partner org registration → [`.cursor/skills/apisetu-partner-onboarding/`](../apisetu-partner-onboarding/SKILL.md) + `PRODUCTION-READINESS.md`.

## Agent context rule (always)

On every Hermes page under test, treat **UI + console + backend** as one compact context.
Do not conclude pass/fail from UI alone.

**Bridge = Hermes Chrome WIP only** — `wip_hermes.py` forces  
`HERMES_CHROME_BRIDGE_SOCKET=…/hermes-chrome-cursor-wip/run/chrome-bridge.sock`.  
Load unpacked: `…/hermes-chrome-cursor-wip/deploy/extension`. Do **not** use Codex live Hermes.

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

`hermes_run` / bridge `run` auto-attach `page_diag` (install console hooks after each `goto`, dump at end).
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
```

| Step | Required | Pass |
| --- | --- | --- |
| **lane** | Full browser validation | exit 0; smoke JSON + SSO + closeout |
| **preflight** | Before ad-hoc browser work | exit 0, `tier: hermes`, HTTP 2xx |
| **test** | `smoke` and/or `sso` | JSON pass signals below |
| **closeout** | After browser work | exit 0, `bridge ready=True` |
| **diag** | When debugging / after any failed step | compact JSON; `ok: true` or actionable `issues` |

Preflight auto-starts `./scripts/start-dev.sh` when the stack is down. Burner SSO: preflight runs `ensure-validator.sh` (JSON-RPC `getHealth` on `:8899`).

## Commands

```bash
# API-only (stack health + gateway pytest; validated 2×)
./scripts/verify-portfolio.sh

# Validated full lane (preferred)
python3 scripts/portfolio_browser.py lane burner seller

# Ad-hoc steps (each runs preflight unless PORTFOLIO_SKIP_PREFLIGHT=1)
python3 scripts/portfolio_browser.py preflight
python3 scripts/portfolio_browser.py smoke
python3 scripts/portfolio_browser.py sso burner [seller|buyer|all]
python3 scripts/portfolio_browser.py sso solflare [seller|buyer]
python3 scripts/portfolio_browser.py commerce seller|buyer [--fixture]
python3 scripts/portfolio_browser.py agentguard seller|buyer|flatwatch [--fixture]
python3 scripts/portfolio_browser.py closeout [leave_url]
python3 scripts/portfolio_browser.py diag [--url URL]

# API + browser automation
./scripts/verify-portfolio.sh --browser
```

## Pass signals

| Command | Pass |
| --- | --- |
| `smoke` | JSON `"success": true`, titles include **ONDC Buyer** + **ONDC Seller** |
| `sso solflare` | `"signed_in": true`, buttons include **Sign out** |
| `sso burner` | exit 0, Hermes lands on app with **Sign out** |
| `diag` | `ok: true` (no console/backend errors); else fix `issues` first |

## Progressive disclosure

- Preflight/closeout checks: [`references/lifecycle.md`](references/lifecycle.md)
- Failures: [`references/troubleshooting.md`](references/troubleshooting.md)
- Parallel multi-app (0-token scout): this file § Multi-app orchestration + `scripts/parallel_smoke_wip.py`

Built with **workflow-hardening** skill (`make it work → validate → simplify → optimize → automate`).
