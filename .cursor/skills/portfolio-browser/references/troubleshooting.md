# Troubleshooting

Re-run `python3 scripts/portfolio_browser.py preflight` first.

| Symptom | Cause | Fix |
| --- | --- | --- |
| HTTP checks fail, stack down | Ran browser steps without stack | Use `lane` or let preflight auto-start `start-dev.sh` |
| SSO hangs / `wait_for_url_change` still on `/login?…&dev_auto=1` | Validator `:8899` down or flapping | `./aadharsolana/scripts/ensure-validator.sh` (preflight auto-runs this for burner). Probe **getHealth**, not `GET /` |
| `Failed to fetch balance` / RPC console errors on web | Same — env, not product | Ensure validator; do **not** “fix” wallet UI code |
| Preflight RPC fail after agent `pkill` / `rm -rf .local-validator` | Improvised reset; Agave 2.2 has **no** `admin.rpc` | Browser lanes: ensure only. On-chain fresh ledger: `start-validator.sh --reset` (mutex). Never wipe ledger under a live process |
| `Use closeout to release…` / close_tab error | WIP leased sessions forbid `close_tab` | `goto` next URL; release via `closeout` |
| `Detached while handling command` on checkout fills | WIP `fill_selector` mid-chain on React inputs | Use evaluate value-setter (`FILL_DELIVERY_JS` in `hermes_elevated_commerce.py`) |
| `EMPTY_RESPONSE` | Orphan WIP `native_host.py` or dead pipe | Preflight (auto sync-wip); reload WIP unpacked extension |
| `No Chrome window named "Solflare"` | Popup on another Space or not open | Same Space as Cursor; click Sign in; `--approve-only` within 5s |
| CUA `list_windows` timeout | cua-driver slow | `solflare_sso.py` uses Quartz poll + AX snap — do not call `list_windows` |
| `No visible clickable element matched text: Phantom` | Burner on | Use `sso burner` or `sso solflare` |
| cliclick misses Approve | Wrong Space | Move Chrome; `approve_solflare.py` fallback inside `solflare_sso.py` |
| Search `undefined` in URL | Stale nav state | Use `/results?q=rice` directly |
| UI looks fine but flow fails | Console/backend errors ignored | `python3 scripts/portfolio_browser.py diag --url <page>`; fix `page_diag.issues` |
| `page_diag.console.installed: false` | Hook not run after navigation | Ensure actions go through `hermes_run` / bridge `run` (auto-wrap) |
| Hydration mismatch on `:43100/home` in parallel smoke | Known Next SSR/client drift | Fixer packet ok to note; not a WIP/SSO blocker |

Manual Hermes reload: load unpacked from `…/hermes-chrome-cursor-wip/deploy/extension` → Reload. Host browser may be Chrome or Comet — check native-host parent.
