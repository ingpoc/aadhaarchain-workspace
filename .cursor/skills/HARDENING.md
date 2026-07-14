# Cursor skill hardening ledger

Owner evidence for the 2026-07-14 Elon Algorithm pass over every repository-owned
skill under `.cursor/skills/`. The skill itself remains the behavior owner; this
ledger records the cross-skill gate and does not duplicate operating instructions.

## Entry contracts

| Skill | Intended outcome | Explicit non-goal | Authoritative independent pass | Safety / cleanup |
| --- | --- | --- | --- | --- |
| `apisetu-partner-onboarding` | Route an operator through ONDC/partner onboarding with current evidence and semantic browser actions | Deploying or submitting irreversible portal actions | Strict skill audit + owner-marker scan + ONDC PreProd harness syntax | Read-only; no browser session or portal mutation |
| `authentication` | Preserve one gateway session-principal contract and a reproducible local demo SSO lane | Adding another identity or wallet authorization stack | Strict audit + 12 gateway OAuth/session/social tests | Test-only; bytecode and pytest cache disabled |
| `demo-video-recording` | Require access, script, and dry-run evidence before recording | Recording or publishing during validation | Strict audit + Samantha locator/evidence checks + ffmpeg availability | Read-only; never starts ffmpeg |
| `ondc-testing` | Test novice Samantha journeys on Buyer and Seller through visible runtime completion | Treating dispatch or HTTP 200 as outcome proof | Strict audit + harness syntax + offline ONDC graders | Offline; never opens Hermes or deploys |
| `portfolio-browser` | Keep WIP Hermes as the sole semantic browser driver with native diagnostics | Product journey ownership or live Hermes fallback | Strict audit + browser-helper syntax and stale-guidance scan | Read-only; never leases a session |
| `portfolio-deploy` | Keep one $0 CI/deploy owner with deterministic preflight checks | Performing a deployment during skill validation | Strict audit + offline ONDC graders | Read-only/offline; never calls Render or Vercel |

## Sequence and evidence

1. Question: each skill must own a distinct operator job; browser mechanics,
   authentication, journey testing, recording, onboarding, and deployment remain
   separate because they have different authority and pass signals.
2. Make it work: strict audit baseline was **1 hard / 7 soft** in **0.38s**.
   Manual checks found the missing API Setu frontmatter, an auth pytest command
   that failed without `PYTHONPATH=.`, non-resolving wildcard references, and
   stale CSS/JavaScript browser advice.
3. Validate: after owner fixes, the complete six-skill validation sequence passed
   twice consecutively. Authentication produced **12 passed** on both runs.
4. Simplify: removed the four legacy Samantha one-off routes from the primary
   testing matrix and deleted stale mutating-`evaluate`, CSS-selector, console
   monkey-patch, and legacy hardening guidance.
5. Optimize: one shared validator replaces six copies of audit and marker logic;
   skill entry points are thin wrappers. Observed single-run times were 0.38s
   onboarding, 2.27s auth, 0.70s recording, 0.89s ONDC testing, 0.79s browser,
   and 0.81s deploy. Budgets are 3s except auth at 5s.
6. Automate/encode: every skill has `scripts/validate.sh` and a source-hashed
   `references/hardening-contract.json`. The final gate must pass twice, with the
   second run using `--require-empty`.

## Known debt

The auth tests emit six dependency deprecations: Pydantic class config,
`pytesseract` use of `pkgutil.find_loader`, and per-request `httpx` cookies.
They are not hidden or treated as skill-gate failures because all assertions pass
and the warnings are owned by gateway dependency/test modernization. Revisit
before Pydantic 3 or Python 3.14 upgrades.
