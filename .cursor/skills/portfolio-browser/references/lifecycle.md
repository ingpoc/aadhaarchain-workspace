# Preflight & closeout

## Preflight (`portfolio_browser.py preflight`)

Runs `scripts/preflight.sh`. Exit **0** required before SSO or custom browser work. (`smoke` calls this automatically.)

| Check | Fail symptom | Fix |
| --- | --- | --- |
| Orphan `native_host.py` (no `chrome-extension://` in argv) | `EMPTY_RESPONSE` | Auto-killed; socket cleared |
| Hermes bridge `ready` | Bridge timeout | `sync-wip.sh` + reload **WIP** unpacked extension; socket `…/hermes-chrome-cursor-wip/run/chrome-bridge.sock` |
| HTTP 2xx on :43100/login, :43101/health, :43102/search, :43103/dashboard | timeout after 30s | Preflight auto-runs `./scripts/start-dev.sh`; retries 30s |
| Solana validator :8899 getHealth (burner only) | SSO hangs / `wait_for_url_change` on login | Auto: `aadharsolana/scripts/ensure-validator.sh`. Do not `pkill` / wipe ledger for browser lanes |
| Chrome on **same macOS Space** as Cursor | `Chrome portfolio tabs not visible` | Move Chrome desktop, re-run |
| Burner flag in `aadharchain/frontend/.env.local` | (info only) | `true` → `sso burner` uses `dev_auto=1` |

## Closeout (`portfolio_browser.py closeout [leave_url]`)

Runs `scripts/closeout.sh`. Exit **0** required to end a session.

1. Verify bridge `ready`
2. Close Hermes sessions: `portfolio-browser`, `aadhaarchain-sso-seller`, `aadhaarchain-sso-buyer`, `solflare-sso`
3. `goto` leave URL (default `http://127.0.0.1:43102/search`)
4. Confirm bridge still `ready`

## Solflare approve-only

Popup already open after failed approve:

```bash
python3 .cursor/skills/portfolio-browser/scripts/solflare_sso.py --approve-only
```
