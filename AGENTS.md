# AadhaarChain Portfolio — Agent Control Surface

Read this first. **Product:** [AgentGuard](PRODUCTIDEA.md), safe agentic commerce authority. The Token Nxt demo is ONDC Buyer + ONDC Seller under one control contract; `aadharchain/` hosts the gateway only. FlatWatch and Solana are deferred. Full detail (participant-host gate, hardening gate, browser lanes, real-vs-stubbed, host identity, agent runtime): [docs/AGENT-CONTROL-SURFACE.md](docs/AGENT-CONTROL-SURFACE.md).

## Owners (don't invent parallel contracts)

Thesis `PRODUCTIDEA.md` · design `.voice/DESIGN.md` · contracts `.voice/ARCHITECTURE.md` · milestones `.voice/IMPLEMENTATIONPLAN.md` · current state and evidence gates `.voice/progress.md` (wins over stale status lines) · verification `.agents/skills/testing-ledger/SKILL.md` · app outcomes `ondcbuyer/GOAL.md`, `ondcseller/GOAL.md`, `aadharchain/GOAL.md` · ops `PRODUCTION-READINESS.md`. AgentGuard APIs on `:43101` are the sole authorization boundary.

Current state is owned by `.voice/progress.md`: Gate 1 published `Sampoorna Whole Wheat Atta 1kg` (signed search proof `preprod-gate1-search-20260725-213218.json`), Gates 2–3 passed, and current-source FQDN `W-*` remains open.

## Read the detail first when

- adding an ONDC participant FQDN, DNS, Render target or Workbench run: "Active ONDC participant-host gate" (fail-closed order);
- changing scripts: "Workflow hardening gate" (no simplifying before two manual passes);
- touching auth, sessions or the agent runtime: "Host identity" and "Agent runtime".

## Agent runs (Codex)

- Scope: change only the files the handoff names; anything else, stop and report.
- Before editing: read the handoff and the files it names; nothing else unless needed.
- Tests: run `./scripts/verify-portfolio.sh`, then `npm test && npm run build` in each app you touched (`ondcbuyer`, `ondcseller`), and `./scripts/local-ship-gate.sh` before commit; done means they pass. Fresh clone: `./scripts/setup.sh` then `./scripts/start-dev.sh`. Add or update a test for each behaviour change.
- Siblings: before finishing, search the allowed files for other code paths that repeat the pattern you fixed and fix them too.
- Style: follow existing patterns; no new dependency without the handoff saying so.
- Fail loud: no silent fallbacks, no skipped or weakened tests or gates.
- Secrets: never print or commit them; read from the environment or Keychain inside the process. Razorpay Test Mode and preprod only; no live keys.
- Git: work only on your `codex/<task>` branch; never commit to main.
- Output: last message = what changed (files), test result, open questions. No narration.

## Never

Production ONDC/NPCI claims before milestone 9 with official evidence; ports `3000`/`3002` for ONDC (use `43102`/`43103`); production URLs in local tests; FlatWatch AgentGuard or Solana for Token Nxt acceptance.
