# OpenAI voice-agent guidance applied to this repo

Load this reference when designing or reviewing Samantha prompts, tool schemas,
context envelopes, Realtime/runtime handoffs, or evals.

## Primary sources

- [Using realtime models](https://developers.openai.com/api/docs/guides/realtime-models-prompting)
- [Realtime and audio](https://developers.openai.com/api/docs/guides/realtime)
- [Using tools](https://developers.openai.com/api/docs/guides/tools)
- [Realtime Eval Guide](https://developers.openai.com/cookbook/examples/realtime_eval_guide)

These are current web sources. Re-fetch before making claims about current model
IDs, parameters, availability, or limits.

## Guidance → repo rule

| Official guidance | Repo application |
| --- | --- |
| Define responsibilities, decision points, tool behavior, and guardrails | Prompt Samantha with scoped policies, not fixed customer phrases |
| Start simple and add instructions only for observed failures | Each new prompt rule must point to an eval failure it fixes |
| Read-only tools can be eager; consequential writes need confirmation | Search/navigation may act when clear; payment/refund/destructive changes use explicit boundaries |
| Tool prompt and actual list must stay synchronized | Keep both aligned; a missing expected action is a product defect |
| Never claim completion before tool success | Require rendered or persisted readback before user-facing success |
| Current authoritative state must be distinguishable from history | Inject a compact source-labelled state envelope every turn |
| Tool failures need user-safe recovery | Retry transient failures once; do not loop identical calls or expose raw errors |
| Evaluate content and audio independently | Text-mode Pass does not prove mic, recognition, interruption, or prosody |
| Build Crawl → Walk → Run eval maturity | Start with intent/tool cases, then realistic capture, then multi-turn simulations |

## Prompt audit

The prompt should answer these without phrase matching:

1. What customer outcome does the agent own?
2. When should it answer, clarify, act, confirm, delegate, retry, or stop?
3. Which tools are actually available now?
4. Which state source is authoritative if context conflicts?
5. What does it say while a slow action is running?
6. What proves completion?

Reject prompts containing broad, brittle rules such as:

- “call tools immediately” without risk/ambiguity scope;
- “if the user says X, call Y” as a routing mechanism;
- tool names not present in the current tool list;
- “never ask questions” or “always confirm everything”;
- success claims based only on dispatch or HTTP acceptance.

## Tool schema audit

- Description names the user outcome and decision boundary.
- Required arguments are genuinely required.
- Structured arguments retain modifiers such as product type, dietary need,
  budget, quantity, seller, order, or delivery constraint.
- Exact identifiers are confirmed when risk warrants it.
- Result distinguishes `completed`, `loading`, `need_clarification`,
  `need_confirmation`, `failed`, and `unsupported` when applicable.
- Result includes a compact authoritative state summary or reference.
- Tool and prompt use the same canonical name.

Do not transform “organic atta under ₹200” into only `atta`. The model should
produce structured intent such as `{query:"atta", organic:true, max_price:200}`
when the backend supports those fields, or preserve the full semantic query
when it does not.

## Compact context envelope

Use a small typed object rather than prose or a page dump:

```json
{
  "current_task": "buy atta",
  "current_page": "/results",
  "state_status": "current",
  "visible_results": [
    {"id": "item-1", "name": "Whole Wheat Atta", "price_inr": 89}
  ],
  "cart": {"item_count": 0, "items": []},
  "last_tool": {"name": "search_catalog", "status": "completed"},
  "next_safe_step": "add a visible result or refine the search"
}
```

Keep only fields needed for the next decision. Fetch detail on demand. Mark
loading explicitly so the model cannot interpret an interim empty array as
authoritative “no results.”

## Representative customer eval buckets

Use varied natural wording; never pass only one canonical phrase.

| Bucket | Example behavior |
| --- | --- |
| First visit | “I’m new here—can you help me buy atta?” |
| Referential | “Add the one I can see.” |
| Constraint preservation | “Find organic atta under ₹200.” |
| Ambiguity | “Remove that” with multiple cart lines → clarify once |
| Correction | “Not that one—the cheaper atta.” |
| Goal change | “Actually, empty the cart and show me milk.” |
| Consequential write | “Pay now” → verify target/amount and AgentGuard boundary |
| Tool failure | Temporary failure → brief explanation and one retry option |
| Unsupported action | Honest limitation plus closest safe next step |
| Long task | Weekly plan → runtime handoff and terminal completion |
| Seller operations | Natural publish, stock, order, dispatch, refund asks |
| Voice-only | Noise, interruption, exact IDs, names, numbers, and latency |

Grade tool choice, argument fidelity, clarification quality, outcome grounding,
operator-facing language, latency, token use, and audio behavior separately.
