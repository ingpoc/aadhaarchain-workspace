---
name: agent-runtime-design
description: >-
  Design, implement, or review Samantha-style Realtime voice agents and
  long-running runtime agents with model-driven intent, safe and synchronized
  tools, authoritative UI/state grounding, compact context, token-efficient
  handoffs, and representative evals. Use when working on voice-agent prompts,
  tool schemas, function calling, Realtime sessions, runtime delegation,
  context-window or token-cost work, agent UX, or when an agent feels
  deterministic, lacks an expected action, contradicts the screen, repeats
  work, or leaks internals.
---

# Agent runtime design

> **Self-validate after edits.** Run `./scripts/validate.sh` from this skill directory.

This skill owns **how** voice and runtime agents are designed. It does not own
the ONDC customer test inventory or its Pass criteria; those remain in
[`ondc-testing`](../ondc-testing/SKILL.md).

## Owner boundary

| Concern | Owner |
| --- | --- |
| Natural-language intent, clarification, tool choice, conversational response | Model |
| Tool schemas, argument validation, authorization, idempotency, execution | Deterministic host |
| Current page, visible results, cart/order state, persisted outcome | Product state owners |
| Short low-latency interaction | Realtime agent |
| Long multi-step planning or execution | Runtime agent |
| Customer journeys and Pass/Fail evidence | `ondc-testing` |
| Consequential-action authority | AgentGuard |

**Model owns semantic intent.** Never route a user's utterance with keyword,
regex, fixed-phrase, or last-token rules. The host may normalize a selected
tool's arguments only when meaning is preserved (trim whitespace, validate a
schema, canonicalize a confirmed identifier). It must not discard qualifiers,
infer a different intent, or select a tool on the model's behalf.

## Design workflow

1. Write the real customer job in first-time-user language.
2. Inventory every action the customer reasonably expects the agent to perform.
3. Define model/host ownership before editing prompts or tools.
4. Design tools and authoritative state readback together.
5. Set a per-turn context budget and a Realtime/runtime handoff boundary.
6. Evaluate natural multi-turn behavior; turn every real failure into a case.

Do not optimize prompts or tokens before one end-to-end customer path works.

## Model-driven intent

The model decides whether to answer, clarify, call short tools, confirm a
consequential action, delegate long work, or recover after failure.

Prompt responsibilities and decision points, not command phrases. Avoid broad
rules such as “call tools immediately”; they make the agent over-eager and
literal. Prefer scoped policy:

```text
Use a read tool when intent and required fields are clear.
Ask one clarification when a required field is missing or ambiguous.
Before a consequential write, summarize the target and consequence, then
proceed only after the user's request or confirmation is unambiguous.
```

Examples demonstrate behavior; they must not become the only accepted wording.

## Tool contract

Every user action needs a real tool or an honest unsupported response. Keep the
prompt and current tool list synchronized.

| Requirement | Rule |
| --- | --- |
| Name | Stable verb-object name; never rename only in prompt text |
| Description | State outcome, when to use, when to clarify, and confirmation boundary |
| Arguments | Structured fields that preserve qualifiers; no raw user-prompt parsing |
| Availability | Expose every action executable in the current session; do not mention absent tools |
| Result | Compact `ok`, user-safe message, authoritative state, and safe next action |
| Failure | No raw error; retry once only if transient, then alternate/escalate |
| Completion | Claim success only after rendered or persisted readback matches |

Use high eagerness for low-risk reads. Use explicit confirmation boundaries for
purchases, payments, cancellations, refunds, destructive changes, and exact
identifiers. Do not ask repetitive confirmation for harmless or already-
confirmed work.

## State grounding

The model cannot infer what the user sees unless the host supplies it. Before
each turn, inject a compact authoritative envelope:

- current task and current page;
- visible result names/IDs that the user can refer to;
- live cart/order/catalog summary;
- active constraints and confirmation state;
- latest successful or failed tool outcome;
- next safe step when work is still loading.

After a tool call, send the authoritative post-action state—not only “request
accepted.” Never say “nothing found” while results are still loading. Never let
stale transcript text override a current tool result or rendered state.

## Context and token efficiency

Use the smallest context that preserves correct decisions:

1. Keep stable role, policies, and tool rules in one concise structured prompt.
2. Send current authoritative state each turn; do not dump the DOM, full catalog,
   raw backend responses, or entire transcript.
3. Include only relevant visible candidates (normally the top few), with stable
   IDs and the fields needed for the next decision.
4. Retrieve details on demand through tools instead of preloading them.
5. Compact completed history into a source-labelled state summary; keep recent
   turns needed for references and corrections.
6. Keep tool outputs small and typed. Internal IDs stay in machine context, not
   operator-facing prose.
7. Measure cached input, non-cached input, output, latency, retries, and tool
   failures separately. Do not reduce model judgment merely to lower tokens.

Token efficiency is a constraint on representation, not permission to replace
semantic understanding with deterministic routing.

## Realtime and runtime split

| Realtime agent | Runtime agent |
| --- | --- |
| Dialogue, clarification, short reads/writes, visible navigation | Multi-step plans, research, bulk work, long loops |
| One turn should settle quickly | Lifecycle may span many turns or minutes |
| Short natural preamble only when latency is noticeable | Emits `started → heartbeat → completed|failed` |
| Returns a visible product outcome | Returns a compact outcome and authoritative references |

Delegate a compact brief: customer goal, constraints, relevant current state,
authorization references, desired visible outcome, and stop condition. Do not
send the full transcript. Samantha remains the user-facing identity; never leak
runtime provider names, internal session IDs, `/agent`, or sprint wording.

## Evaluation loop

Use [`references/openai-agent-guidance.md`](references/openai-agent-guidance.md)
for the prompt/tool/context audit and representative eval buckets.

- **Text first:** tool choice, arguments, clarification, policy, state grounding.
- **Voice separately:** recognition, interruption, latency, tone, exact entities.
- **Crawl:** single-turn intent/tool cases.
- **Walk:** realistic text/audio capture and noisy inputs.
- **Run:** multi-turn goal changes, references, corrections, and tool failures.

Record the trajectory: user turn, compact state, model tool call, tool result,
visible/persisted readback, response, latency, and token usage.

## Quality gate

- [ ] No deterministic user-intent routing or semantic query truncation
- [ ] Prompt responsibilities match the actual tool list
- [ ] Expected Buyer/Seller actions have tools or honest fallback
- [ ] Ambiguity produces one focused clarification, not guessing
- [ ] Consequential actions respect confirmation and AgentGuard
- [ ] Tool success is grounded in visible or persisted state
- [ ] Realtime/runtime handoff has a terminal lifecycle
- [ ] Context envelope is compact, current, source-labelled, and sufficient
- [ ] Customer-language evals cover paraphrases, references, corrections, and goal changes
- [ ] Token reductions preserve model judgment and measured task quality

## Sources

Official OpenAI guidance is summarized in
[`references/openai-agent-guidance.md`](references/openai-agent-guidance.md).
Re-fetch those sources when model/API behavior or recommended models may have changed.
