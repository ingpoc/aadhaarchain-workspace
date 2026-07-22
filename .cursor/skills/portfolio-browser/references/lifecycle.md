# Preflight & closeout

## Preflight (`portfolio_browser.py preflight`)

Runs `scripts/preflight.sh`. Exit **0** required before SSO or custom browser work. (`smoke` calls this automatically.)

| Check | Fail symptom | Fix |
| --- | --- | --- |
| Orphan `native_host.py` (no `chrome-extension://` in argv) | `EMPTY_RESPONSE` | Auto-killed; socket cleared |
| Hermes bridge `ready` | Bridge timeout | `sync-wip.sh` + `ensure-wip-native-host.sh` + reload **WIP** unpacked extension; socket `…/hermes-chrome-cursor-wip/run/chrome-bridge.sock` |
| Extension loaded but `SOCKET_DOWN` | Manifest `path` was `native_host.py` → socket under `~/.hermes/run` | `ensure-wip-native-host.sh` (preflight auto); never rewrite to `.py` |
| HTTP 2xx on :43100/login, :43101/health, :43102/search, :43103/dashboard | timeout after 30s | Preflight auto-runs `./scripts/start-dev.sh`; retries 30s |
| Solana validator :8899 getHealth (burner only) | SSO hangs / `wait_for_url_change` on login | Auto: `aadharsolana/scripts/ensure-validator.sh`. Do not `pkill` / wipe ledger for browser lanes |
| Chrome on **same macOS Space** as Cursor | `Chrome portfolio tabs not visible` | Move Chrome desktop, re-run |
| Burner flag in `aadharchain/frontend/.env.local` | (info only) | `true` → `sso burner` uses `dev_auto=1` |

## Reviewer-ready lease probe

Run this after the correct app audience is signed in and before spending a fresh
customer or UI/UX reviewer:

```bash
python3 .cursor/skills/portfolio-browser/scripts/reviewer_ready.py \
  --url http://127.0.0.1:43103/dashboard \
  --expected-marker "Sign out"
```

The probe owns one visible WIP window and proves:

1. Initial semantic context and screenshot come from the expected signed-in URL.
2. The same session, window and tab survive a second visual read after the default
   35-second service-worker idle boundary.
3. Both screenshots exist and are non-empty.
4. The expected signed-in semantic marker remains present.
5. Closeout removes only the probe's lease and the owned session is absent afterward.

Exit `0` with `status: reviewer_ready` is required. Exit `2` is **Tooling Blocked**;
retain its filtered diagnostics and any lease-removal record, clear the browser owner
issue, and allow one bounded retry. Do not dispatch a reviewer or reinterpret this as
product feedback. Use `--expected-url-prefix` when the signed-in surface may add a
known suffix, query or child route.

## Closeout (`portfolio_browser.py closeout [leave_url]`)

Runs `scripts/closeout.sh` → `closeout_leases.py`. Exit **0** required to end a session.

1. Verify bridge `ready`
2. List active Hermes agent leases and **close every window** (owned tokens first; orphan/stale leases via preflight reclaim then closeout)
3. Confirm `active_agent_sessions=0` (or report remaining + fail)
4. Leave URL is only used when reclaiming an orphan that needs a controllable `http(s)` start URL (default `http://127.0.0.1:43102/search`)

### Window / lease identity

| Agents working | Windows | How |
| --- | --- | --- |
| 1 | 1 | Default `HERMES_AGENT_ID` / task id → `portfolio-browser` |
| 2+ concurrent | 1 per agent | Set distinct `HERMES_AGENT_ID` (or `PORTFOLIO_HERMES_MULTI_AGENT=1` with distinct task ids) |

Do **not** pass a fresh `task_id=f"…-{pid}"` or a new decorative session name per step — each unique Hermes `sessionId` opens another window. `run_with_session_preflight` reuses an in-process lease and does not preflight again when the token is already held.

## Solflare approve-only

Popup already open after failed approve:

```bash
python3 .cursor/skills/portfolio-browser/scripts/solflare_sso.py --approve-only
```
