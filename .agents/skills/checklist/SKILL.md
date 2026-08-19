---
name: checklist
description: AadhaarChain and AgentGuard product-lead checklist adapter. Use for the current high-level product checklist, completed or pending outcomes, blockers, go/no-go posture, stale checklist data, or refreshing and validating .session/checklist/state.json and .session/html/checklist.html. Uses the global checklist-framework for lifecycle, statuses, schema, and rendering.
---

# AgentGuard Checklist Adapter

Use `~/.agents/skills/checklist-framework` for doctrine, statuses, AskQuestion,
queue cycles, and schema. This adapter names owners, proof limits, and commands.

## Checklist control owner

| Concern | Owner |
| --- | --- |
| All checklist items, statuses, blockers, production queue, human-parallel work, and `operator_decisions` | `.session/checklist/checklist.json` |
| Acceptance criteria and gate status | `.agents/skills/testing-ledger/references/checklist-gates.json` |
| Immutable testing receipts | `.agents/skills/testing-ledger/references/evidence/` |
| Generated card linkage | `.session/testing/testing-ledger.json` |

Supporting sources never own status: `.session/docs/PRODUCTIDEA.md`,
`.session/docs/IMPLEMENTATIONPLAN.md`, `.session/docs/PRODUCTION-READINESS.md`,
`.agents/skills/testing-ledger/`.

## Production queue

`go_live_path` is the one ordered plan. Edit phases, `parallel_now`,
`updated_at`, `updated_by`, and reason in the same control-owner pass, then
generate + `--check-current`. Critical open items belong on the path; closed
work does not. The first agent-owned item must be `in_progress`, `testing`, or
`partial`. `parallel_now` requires an existing `operator_boundary`.

Q1 owns frozen-source release. CF2/CF3 complete on their own lifecycle gates
and must not stay open for Q1. B5 completes on preprod/Auth0 signed IGM plus
visible outcome; production IGM is A4/B8, not a B5 hang. Continue A5 even when
A4 is blocked.
Queue cycle rules live in the framework renderer; the exporter fails closed.
Machinery gate: `references/hardening-contract.json`.

## Continuous currency

After every meaningful slice, update `.session/checklist/checklist.json`, then
generate + `--check-current`. Prefer the live view from
`./scripts/start-dev.sh checklist` (default `http://127.0.0.1:8030/checklist.html`;
read `.session/logs/checklist-html.port`). Never invent ports (including
`43106`). Never edit generated HTML/JSON by hand.

## Parallel / multitask

Non-conflicting IDs and files may run together. Honor `go_live_path`; a blocked
`parallel_now` row does not idle the first agent-owned item. Stop only for
Cursor `AskQuestion` when the work in hand needs a human fork — payload rules
are global. Prefer one `checklist.json` writer; merge by item ID if not.

## Applicability

All global lifecycle sections apply. Money and external-provider sections stay
required. Native/voice future-channel work must not displace the production
blocker.

## Commands

```bash
python3 scripts/generate_checklist.py
python3 scripts/generate_checklist.py --check-current
python3 scripts/generate_checklist.py --check
./scripts/start-dev.sh checklist
~/.agents/skills/checklist-framework/scripts/render_checklist.py --root . --check-current
./scripts/verify-portfolio.sh --ci
```

Generate writes `.session/html/checklist.html`. Serve is optional
(`start-dev.sh checklist` or full-stack `all`). Preferred port `8030`, then
`8031+` if busy (cap +20). Detach uses the same setsid double-fork as the
gateway; pid `.session/logs/checklist-html.pid`, port
`.session/logs/checklist-html.port`. Missing HTML regenerates once. A healthy
listener on the selected port is left alone.

Generated caches: `.session/checklist/state.json`,
`.session/testing/testing-ledger.json`, `.session/html/checklist.html`.

A passed `provider_verification` gate still needs explicit freshness, ISO-8601
verification time, and existing evidence refs.

## Operator boundaries

Do not submit ONDC/provider forms, accept terms, expose secrets, spend, deploy,
enable production, or place orders solely because a row names the action.
When blocked **and the work in hand cannot proceed**, AskQuestion only.
Subagents often lack AskQuestion; the parent issues A4 (and other human) forks.

Do not offer Submit / PEM-to-Render / DNS as option `[0]` even when all three
Production 1.a modal pairs + `unique_key_id`s exist — A4 stays blocked until
those operator actions are authorized.

After operator authorizes **PreProd official IGM**, the next agent-owned step
is exact-commit deploy of IGM source to existing
`identity-aadhar-gateway-main` (no PEM/DNS/registry). Do not offer
wait/no-deploy as `[0]` while public `POST /api/ondc/issue` still 404s — that
blocks the authorized path.

After answers: append `operator_decisions` → update remaining_work/status if
needed → generate + `--check-current`. Decisions never complete the item.
