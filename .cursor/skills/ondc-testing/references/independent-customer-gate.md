# Independent customer gate

Run this after build/API checks. Reviewers are blind subagents using bundled
`@chrome` and role briefs only; bundled `@Computer` owns native Mac UI. The WIP
Hermes harness is legacy replay/diagnosis only. This gate tests customer outcomes; it is not the Samantha
text-tool matrix and must not force an assistant interaction into an unrelated
manual shopping, payment, or read-only UX task.

## Outcome and non-goals

The gate answers three customer-level questions:

1. Can an ordinary signed-in Buyer complete a useful shopping outcome without
   implementation knowledge?
2. Can an ordinary signed-in Seller understand and operate the commerce flow
   without implementation knowledge?
3. Do the two signed-in products communicate purpose, authority, state, and
   next actions clearly and accessibly?

It does not maximize reviewer count, assign one subagent per checklist row, or
use customer reviewers for diagnosis. Authentication is setup: every profile
knows how to sign in, but the measured journey begins on the proved signed-in
landing page. API, fixture, and deterministic browser matrices remain the
efficient owners for narrow regression coverage.

## Efficient execution contract

1. **Main thread prepares the audience.** Verify the WIP host/socket, snapshot
   mutable item/order ids once, prepare a Seller order or issue with a visible
   next action, authenticate the correct Buyer or Seller audience, and prove the
   signed-in landing page before starting a reviewer.
   Run host/socket preflight once for the campaign, restart only the service
   whose code or environment changed, and do not start optional wallet/Solana
   dependencies for AgentGuard customer testing. Clear inherited Buyer cart or
   checkout state before the novice starts; test-data cleanup is setup, not a
   customer milestone.
   A read-only semantic check may prove the page has stable interactive controls,
   but none of their roles or names enter the role brief. The actor discovers
   the rendered and accessibility surfaces independently.
   The reviewer starts after login; authentication setup is not part of the
   novice journey unless auth itself is the requested specialist task.
2. **Group by audience, not reviewer.** Authenticate Buyer once, then run the
   Buyer novice and the UX reviewer's Buyer mission. Authenticate Seller once,
   then run the Seller merchant and the UX reviewer's Seller mission. Never
   alternate audiences merely to keep one reviewer's two app reports adjacent.
   Default to sequential execution. Parallel review is allowed only after
   separate browser profiles/storage and non-overlapping backend state have
   been proven; separate windows alone are insufficient isolation.
   **Preserve operator observability:** every active Chrome test window stays
   visible and may be tiled so the operator can watch testing as it happens.
   Do not hide, minimize, or replace visible browser work with headless runs as
   an efficiency measure. Visible windows are intentional evidence surfaces;
   they do not by themselves prove storage isolation or make concurrent
   mutations safe.
   **Keep the control boundary explicit:** `@chrome` owns all web-page
   navigation, reads, clicks, form entry, screenshots, and tab lifecycle. If a
   browser-owned native surface blocks the page and Chrome cannot control it
   (for example a JavaScript alert/confirm, profile chooser, permission prompt,
   extension UI, or file picker), pause page actions and use `@Computer` only
   for that native surface. Fresh-state verify that it cleared, then resume
   Chrome. Never use Computer Use to replace a page action that Chrome can perform.
3. **One coherent journey per lease.** In the default Chrome lane, a control
   lease means one persistent claimed or agent-owned tab for
   the complete app outcome. Target eight minutes after lease readiness for a
   customer journey and six minutes for a read-only UX app review; do not split
   search, cart, checkout, or catalog work into micro-leases or repeated setup
   follow-ups. If the actor is visibly progressing at the target, allow one
   uninterrupted grace period up to a ten-minute customer or eight-minute UX
   hard ceiling. Confirmed bridge, renderer, or input wait does not consume the
   customer budget and makes the affected run Tooling Blocked rather than an app
   timing verdict. A responsive product that still cannot be understood or
   completed by the hard ceiling is App Fail/usability evidence.
   Complete mandatory outcome slices, including keyboard checks, before optional
   breadth exploration. While the actor is inside that budget, the main thread waits passively: no
   status pings, premature finish requests, or checklist-by-checklist follow-ups.
   The actor owns this clock and records its lease-ready and verdict times. The
   main thread must not derive a deadline from subagent spawn time or send a
   freeze instruction without an actor-reported lease-ready timestamp.
   At the hard ceiling, send one freeze-and-close instruction if the actor has not
   returned.
4. **Discover through the visible product.** The actor uses its own fresh page
   context to find controls. When visible text is ambiguous, it may use the
   control's exposed semantic role and accessible name, but receives no locator
   hints from the main thread. Open Samantha only when the customer goal is
   explicitly assistant-driven; manual shopping, payment, and UX missions may
   use the ordinary UI. Batch related form fills into a small number of driver
   operations, leave an already-correct field unchanged, and retain screenshots
   only at outcome boundaries. Re-selecting a correct category, reading every
   field back individually, or photographing intermediate form states is not
   customer evidence and must not consume the complete-journey budget.
5. **One mission verdict, then close.** Allow natural, visible UI-led correction
   while recording the first point of confusion. Hidden retries, fixture-led
   recovery, and diagnostic hints are forbidden. Inspect every retained
   screenshot, freeze one mission verdict before diagnostics, close the owned
   lease, and prove that reviewer's session id is absent. Unrelated active
   leases are reported and left untouched.
6. **Verify at source-freeze boundaries.** During diagnosis, run only the
   smallest owner test that proves the defect and affected fix. Once the source
   is frozen, run the full affected suite and production build once, then run
   the complete blind journey. A later source mutation invalidates only the
   affected frozen-source evidence; do not rerun unrelated suites or restart
   the whole portfolio.
7. **Clear design risk before stability repetition.** On a candidate source
   hash, run customer pass 1 and the UI/UX-accessibility reviewer's relevant app
   half before that audience's customer pass 2. Keep the same UX actor for the
   second app half when the audience changes, then freeze one combined UX
   verdict. If either check finds an unresolved release issue, freeze the
   reports, consolidate the fixes into one owner pass, and restart only affected
   acceptance on the new hash. Never spend pass 2 proving a candidate that the
   relevant design smoke has not cleared.
8. **Fail closed on test-data hygiene.** After every mutating mission—including
   App Fail and Tooling Blocked—freeze its report, retain its evidence, remove
   only the snapshotted item/order delta, and prove the prepared baseline for
   the next actor. Do not dispatch another blind reviewer while cleanup or the
   expected starting state is uncertain.

A bridge or locator failure before the first customer action is a setup/tooling
block, not product feedback. Clear the browser issue, re-establish the audience,
and rerun the whole coherent journey. Do not accumulate partial micro-runs as a
substitute for one customer outcome.

## Default portfolio

Use three profiles with complete missions. This is the minimum portfolio that
keeps Buyer, Seller, and design judgment independent without turning every
checklist row into a subagent:

1. **Novice Buyer customer** — fresh context-isolated actor. Starting after
   login: find a generic grocery using the ordinary UI, compare visible results,
   add one, verify quantity, clear or revise once, add again, reach checkout,
   resolve the visible payment/AgentGuard decision, and finish at a paid
   order/receipt or an honest denial with no unintended effect. The actor may use
   Samantha only when the visible product makes that a natural choice.
2. **Small Seller merchant** — separate fresh context-isolated actor. Starting
   after login: understand the dashboard, inspect products, publish one natural
   grocery listing, verify its visible price and stock, inspect orders, and
   complete the prepared order/refund/AgentGuard outcome through its visible
   terminal order or remedy state.
3. **Combined UI/UX and accessibility-smoke reviewer** — one independent
   read-only actor covering both signed-in apps as a cross-product mission:
   comprehension,
   hierarchy, internal wording, Samantha purpose and authority, navigation and
   scroll, accessible names/headings, keyboard use, readability, and misleading
   state. Return at most five unique prioritized findings across the product,
   not five per page. This is a heuristic accessibility smoke, not a complete
   screen-reader, responsive, or standards-conformance audit.

Add at most one specialist only when the changed surface specifically requires
voice, payment/reconciliation, authentication, responsive/mobile, destructive
Seller, or AgentGuard authority expertise. A specialist receives the whole
relevant customer outcome, never a single locator or repaired step.

### Mission-level pass signals

| Profile | One mission Pass requires |
| --- | --- |
| Novice Buyer | Generic discovery → visible comparison → cart add/edit → checkout → understandable AgentGuard decision → visible paid order/receipt, or an honest denial with no unintended effect |
| Seller merchant | Publish → persisted visible price/stock → prepared order/issue → assigned accept/refund/AgentGuard action → visible terminal order/remedy state. **Dispatch:** `window.prompt` tracking ID is Hermes (`click_text` + `dialog_handle` + `promptText`). Do not reload while open; frozen page ≠ missing content script. OS-native UI is `$macos-cua` ownership, not a Hermes substitute |
| UI/UX + accessibility smoke | Both signed-in app missions completed; primary navigation and controls keyboard-operable; headings/names/state understandable; no blocking overlap; no unresolved P0/P1 finding |

An incomplete mission is **App Fail** unless a bridge/input/lease fault caused
the stop, in which case it is **Tooling Blocked**. Milestones may be listed as
Pass or Not Tested inside the report, but they never combine into “Partial
Pass.” Add a dedicated accessibility specialist when conformance, screen-reader,
responsive, or mobile behavior is itself a release claim.

### Dispatch and repetition rule

- Spawn at most one actor per selected profile per pass. Never spawn per page,
  control, flow ID, or finding.
- Give the actor one complete goal and enough time for the full journey. A
  follow-up is allowed only to continue the same profile into its second app
  audience or to repeat the entire unchanged-source journey.
- After an App Fail, freeze the report. The main thread diagnoses and fixes the
  owner; customer agents do not inspect code or logs.
- Allow one bounded browser recovery for a Tooling Blocked mission. If the same
  lease, bridge, input, or locator failure repeats, stop that campaign with the
  exact blocker instead of accumulating recovery attempts.
- Retest with the same blind brief in a fresh context and rerun the entire
  affected journey. A focused deterministic test may prove the root cause, but
  it cannot replace the customer rerun.
- Buyer and Seller release evidence requires two full successes on unchanged
  source. The second run is stability proof, not a collection of partial
  follow-ups. Do not start pass 2 until the affected UI/UX smoke has cleared the
  same source hash. Repeat the UX mission only when its first run found a
  release issue or the intervening fix changed visible behavior.

## Measured baseline and budget

The 2026-07-16 four-role, 90-second experiment consumed about 44 minutes while
the Buyer customer journey never began and the Seller journey stopped before
publish/order completion. Treat that as the rejected baseline.

Budget the replacement by outcomes, not click count:

- two audience authentications total: Buyer once, Seller once;
- Buyer and Seller customer profiles once per required customer pass; one
  combined UX actor per candidate hash, repeated only after an intervening
  visible fix; no diagnostic subagent;
- one persistent lease per complete app journey: eight-minute customer target
  or six-minute read-only UX target after lease readiness, with one progress
  grace period capped at ten and eight minutes respectively;
- at most five findings per actor and three screenshots per app journey;
- no repeated preflight, login, source discovery, or role explanation inside a
  journey;
- one compact campaign manifest owned by the main thread: source hash, audience,
  verdict, retained screenshots, created-data delta, cleanup proof, and
  closeout. Do not copy reviewer transcripts, earlier findings, implementation
  history, or another actor's report into a blind actor's context.

## Blind-review and efficiency contract

- Use `fork_turns="none"`. Disclose only role, signed-in starting URL, and
  customer goal—never fixes, source, logs, APIs, tool names, fixtures, expected
  arguments, known defects, or hidden state.
- Use visible UI and ordinary language only. No source, logs, APIs, hidden state, or JavaScript-driven interaction.
- Discover controls from the actor's own visible/semantic page context; the
  role brief contains no control names. Never target a generated id/name or
  transient status placeholder. When visible text is ambiguous, use a
  role-qualified exact accessible name discovered from the page instead of a
  text-only click.
  For the keyboard smoke, press Tab until focus visibly reaches a discovered
  interactive target, then activate that target. One Tab/Enter on a skip link
  or link to the current page is not evidence that navigation failed.
  For an assistant-specific task, open the orb and type a harmless phrase; for
  manual shopping or read-only review, do not add this requirement. Apply the
  same stable-label rule to checkout forms. Input/cursor/bridge failure is
  **Tooling Blocked**.
- After the lease is ready, use the complete-journey budget above. If the bridge
  remains healthy but the actor cannot understand or complete the goal in time,
  report **App Fail** with the point of friction. Report **Tooling Blocked** only
  for bridge, input, lease, or locator-system failure.
- After navigation, allow any visible loading state to reach its rendered
  success, empty, error, or retry state before judging the page. Prefer a
  discovered settled landmark over a fixed delay. An initial loading frame is
  neither App Fail nor Pass; only a loading state that outlives the product's
  visible timeout or the journey budget is failure evidence.
- Behave naturally through visible product choices and preserve the first
  friction. Do not use hidden recovery loops, fixture knowledge, or diagnostic
  hints. Report one mission verdict: **Pass**, **App Fail**, **Tooling Blocked**,
  or **Not Tested**; list milestones only as supporting notes.
- Screenshot and read every claim. Cap reports at five findings and three
  screenshots per coherent journey; include exact copy, final URL, and
  closeout.
- Freeze reports before diagnostics; diagnostics cannot rewrite verdicts.
- All default actors are sequential because the WIP
  Chrome profile shares the gateway session cookie. A page showing “Sign out”
  is not sufficient: the app-audience session must match before the reviewer
  starts, or setup is **Tooling Blocked**. Parallelism requires separately
  proven profile/storage and backend-state isolation.
- Use unique window leases and `session_closeout`; require each owned session id
  to be absent afterward. Do not close or fail the review for unrelated leases.
- The main thread snapshots local item/order ids before a mutating review and removes only the created delta after the frozen report. Tests must not pollute the next customer's catalog.
- Fixture matrices, deterministic replay, API smoke, and implementation-agent browser runs are supporting diagnostics only. They cannot replace this gate.

## Release threshold

Buyer and Seller each achieve two full Passes on unchanged source; the UI/UX
and accessibility-smoke mission has no unresolved P0/P1 and is repeated after
any visible release fix; and every Tooling Blocked mission is rerun after the
browser issue is cleared. Never convert incomplete or Tooling Blocked work into
Pass. The main thread owns implementation; reviewers are evidence sidecars,
not code owners.
