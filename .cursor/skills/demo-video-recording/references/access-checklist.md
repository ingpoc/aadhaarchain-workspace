# Access checklist (demo video)

**Default:** FQDN PreProd. Mark Pass only with evidence.

| # | Check | Command / proof | Pass criteria | Status |
| --- | --- | --- | --- | --- |
| 1 | Hermes WIP | `python3 scripts/portfolio_browser.py preflight` | `tier: hermes-wip`; Comet/Chrome up | |
| 2 | Screen Recording | macos-cua permissions preflight | capturable true | |
| 3 | ffmpeg devices | `ffmpeg -f avfoundation -list_devices true -i ""` | Screen index for Comet known | |
| 4 | Gateway health | `curl` FQDN `gateway.aadharcha.in/health` (wake Free if needed) | 2xx | |
| 5 | Realtime (if claimed) | `GET …/api/realtime/status` on FQDN | `configured: true` | |
| 6 | Buyer FQDN | `https://ondcbuyer.aadharcha.in` | App 2xx; identity → gateway | |
| 7 | Seller FQDN | `https://ondcseller.aadharcha.in` | App 2xx | |
| 8 | Buyer Auth0 | Sign in → Sign out on Buyer | Principal bound | |
| 9 | Seller Auth0 | Sign in → `/agentguard` | Confirm/Pause visible; not Sign-in not configured | |
| 10 | Display | Comet on recorded monitor | Operator sees labeled Hermes cursor | |

## Patterns / antipatterns (PreProd record)

| Do | Do not |
| --- | --- |
| Dry-run on FQDN with Auth0 + live gateway | Record against broken Realtime / unsigned Seller AG |
| Leave `chrome://extensions` before Hermes SSO/actions; reload WIP SW if sock missing | Point scripts at `~/.hermes` or `launch-wip-chrome` to “fix” Comet |
| Open orb: semantic role locator `Open Samantha` **once** | `evaluate` clicks for demo beats; double-click orb; rely on `click_text "S"` |
| Map beats to ondc-testing `W-*` PreProd flows | Invent parallel Pass bars |
| Seed/ensure PreProd marker Atta if fanout empty | Claim prod ONDC / live UPI on VO |

Loopback recovery traps (VITE bake, detached Vite, `:3001` proxy): [`portfolio-browser/references/troubleshooting.md`](../../portfolio-browser/references/troubleshooting.md).  
Token Nxt matrix: [`../apisetu-partner-onboarding/references/token-nxt-demo-step-matrix.md`](../../apisetu-partner-onboarding/references/token-nxt-demo-step-matrix.md).

## Evidence

Save access Pass notes under `references/evidence/<demo-id>/access-pass.md` (optional) with timestamps and curl snippets — no secrets.
