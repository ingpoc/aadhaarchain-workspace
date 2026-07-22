# Troubleshooting

Re-run `python3 scripts/portfolio_browser.py preflight` first.

| Symptom | Cause | Fix |
| --- | --- | --- |
| HTTP checks fail, stack down | Ran browser steps without stack | Use `lane` or let preflight auto-start `start-dev.sh` |
| SSO hangs / `wait_for_url_change` still on `/login?…&dev_auto=1` | Validator `:8899` down or flapping | `./aadharsolana/scripts/ensure-validator.sh` (preflight auto-runs this for burner). Probe **getHealth**, not `GET /` |
| `Failed to fetch balance` / RPC console errors on web | Same — env, not product | Ensure validator; do **not** “fix” wallet UI code |
| Preflight RPC fail after agent `pkill` / `rm -rf .local-validator` | Improvised reset; Agave 2.2 has **no** `admin.rpc` | Browser lanes: ensure only. On-chain fresh ledger: `start-validator.sh --reset` (mutex). Never wipe ledger under a live process |
| `Use closeout to release…` / close_tab error | WIP leased sessions forbid `close_tab` | `goto` next URL; release via `closeout` |
| Many Chrome windows after one agent run | New `task_id`/`session_name` per step (e.g. `portfolio-page-diag-{pid}`) opens a new lease | Use default `portfolio-browser`; `closeout` now closes **all** leases via `closeout_leases.py` |
| Want 2 agents → 2 windows | Need distinct lease ids | Export distinct `HERMES_AGENT_ID` per agent (or `PORTFOLIO_HERMES_MULTI_AGENT=1`) |
| `WIP Hermes run requires preflight for this session` after shell preflight passed | Hermes lease tokens are process-local; a child runner cannot reuse the wrapper process lease | Child runners must call `wip_hermes.run_with_session_preflight` immediately before `run`; never bypass `LEASE_REQUIRED` |
| `already leased…` / `Invalid browser lease token` mid form fill; `sessions` still lists the id (`busy: false`) | Agent used short-lived `python3 -c` / one-shot `hermes_run` then exited — token died; extension lease remained | Multi-page / partner fills (Token Nxt, ONDC portal): `durable_lease_controller.py` for the whole campaign (same session id). `hermes_run` only inside one long-lived process. Do not invent a new session id. Owner: hermes-chrome `optimize.md` |
| `Detached while handling command` on checkout fills | Element remounted during a long React action chain | Re-resolve the input with a semantic `locator` and `fill`; split at the remount boundary. Never use an `evaluate` value-setter |
| `EMPTY_RESPONSE` / `SOCKET_DOWN` | Orphan host, dead pipe, **SW Inactive**, or wrong socket path | **Evidence first** (§ below) — do not `launch-wip-chrome` or switch to `~/.hermes` |
| `SOCKET_DOWN` + extension On + **service worker (Inactive)** | MV3 SW slept → `connectNative` dropped → native host exited → WIP sock gone (manifests often still correct) | Run `ensure-wip-native-host.sh`; open the exact discovered Chrome profile and reload the WIP extension. Never copy a remembered profile name from this project reference |
| `SOCKET_DOWN` + manifest `path` ends in `native_host.py` | Classic path trap → host bound `~/.hermes/run/…` | `ensure-wip-native-host.sh` then reload; never rewrite manifests to `.py` |
| `No Chrome window named "Solflare"` | Popup on another Space or not open | Same Space as Cursor; click Sign in; `--approve-only` within 5s |
| CUA `list_windows` timeout | cua-driver slow | `solflare_sso.py` uses Quartz poll + AX snap — do not call `list_windows` |
| `No visible clickable element matched text: Phantom` | Burner on | Use `sso burner` or `sso solflare` |
| cliclick misses Approve | Wrong Space | Move Chrome; `approve_solflare.py` fallback inside `solflare_sso.py` |
| Search `undefined` in URL | Stale nav state | Use `/results?q=rice` directly |
| UI looks fine but flow fails | Console/backend errors ignored | `python3 scripts/portfolio_browser.py diag --url <page>`; fix `page_diag.issues` |
| `page_diag.console.installed: false` | Hook not run after navigation | Ensure actions go through `hermes_run` / bridge `run` (auto-wrap) |
| Hydration mismatch on `:43100/home` in parallel smoke | Known Next SSR/client drift | Fixer packet ok to note; not a WIP/SSO blocker |
| Hermes pointer invisible at session start | Cursor overlay injects at `opacity: 0` (parked off-screen) until first `cursor_move` / `click_*` / `fill_*` | Run a move/click; there is **no** `cursor_show` (only `cursor_hide`). Proof = screenshot of host window, not `cursor_status` alone |
| Skill running but operator sees no pointer | **Wrong browser app** — WIP native host parent is Comet while watching Chrome (or reverse); or window behind Cursor IDE | Confirm which app owns the WIP extension + socket; raise that window. Preflight checks Chrome **or** Comet |
| Orb “Gateway unreachable” / “Realtime not configured” on **local** `:43102` while `:43101/api/realtime/status` is `configured:true` | Vite process env has FQDN `VITE_*` (shell leak) overriding `.env.local` loopback | `ps eww -p $(pgrep -f ondcbuyer.*vite)` — if `VITE_IDENTITY_URL=https://gateway…`, restart via `./scripts/start-dev.sh` (strips inherited `VITE_*`, loads `.env.local`). Do **not** “fix” Realtime on gateway. Prefer proving Realtime + Samantha on **FQDN PreProd** when validating readiness |
| Buyer/Seller die between Cursor Shell turns after `nohup npm run dev` | Shell teardown SIGKILLs process group; plain `nohup` not enough | Use `start-dev.sh` (Python `start_new_session=True`) or equivalent detached start. Verify with a **second** shell curl after the starter exits |
| `hermes_demo_sso` / bridge preflight rejects a missing URL, `Frame … error page`, or content-script injection on `chrome://` / `about:blank` | Window isolation requires an explicit controllable URL; an active non-http tab is not a valid target | Keep `preflight.url` set to the Buyer/Seller return URL. SSO may recover via session `goto`; do **not** switch to `~/.hermes` |
| Vite log spam `proxy … /api/cart` → `ECONNREFUSED` `:3001` | Stale Vite `server.proxy['/api']` → `localhost:3001` | Buyer/Seller `vite.config.ts` must proxy `/api` → `http://127.0.0.1:43101` (entitlements/agent stay `:43104`). Restart Vite after change |
| Buyer `/cart` UI: “Refresh cart failed … 404” | `.env.local` has `VITE_BUYER_COMMERCE_URL=http://127.0.0.1:43102` (or `:43103`) — app treats Vite as remote cart host; gateway has no `/api/cart` | Unset `VITE_BUYER_COMMERCE_URL` / `VITE_API_BASE_URL`. Code: `cartFailurePolicy` + local fallback on 404. Restart Vite. UI pass = cart lines / empty-cart copy, **not** Cart error card |
| Seller `/orders`: “Orders unavailable” / Failed to fetch | `VITE_API_BASE_URL=http://localhost:3001` with `VITE_COMMERCE_DEMO_MODE=false` | Unset `VITE_API_BASE_URL`. Orders load via `GET /api/demo-commerce/seller/orders` on `:43101` (`OrdersPage` → `listCommerceSellerOrders`). UI pass = filter pills + order cards (or honest empty), **not** spinner forever / error card |
| Samantha orb fails / panel closes immediately | The orb is a **toggle** and a second click closes it; the page may also have remounted | Re-resolve a semantic role locator for button `Open Samantha` and click once; fill test-id `samantha-orb-text` with `testId` camel case. Split the sequence at a remount boundary instead of using CSS selectors or page JavaScript |
| Seller `/agentguard` “Sign-in not configured” / no Pause | No demo/Auth0 principal on seller origin | `sso demo seller` then open `/agentguard`; require Sign out + Confirm mandate / Pause agent |
| `click_text` / Dispatch hangs; `EXTENSION_TIMEOUT` / “content script missing” after a prior `page_context` worked | Click opened `window.prompt`/`confirm`/`alert` (Seller Dispatch tracking ID) or an OS sheet — CS reply freezes; inject/reload theories waste runs | **App handler first:** grep `prompt(`/`confirm(`/`alert(` on that control. JS dialog → Hermes `dialog_handle` + `promptText` (batch with click). OS sheet → `$macos-cua` via hermes `multi-agent.md`. Do not reload while a JS dialog is open; do not burn repeated Accept→Dispatch proofs on inject hypotheses without that one grep |

## Local VITE bake trap (2026-07-12/13)

Vite prefers **process env** over `.env.local`. Exporting `VITE_IDENTITY_URL=https://gateway.aadharcha.in` in the agent shell (or leftover from FQDN work) makes local `:43102`/`:43103` call FQDN while you browse loopback.

```bash
# Prove bake (buyer vite PID):
ps eww -p "$(pgrep -f 'ondcbuyer/node_modules/.bin/vite' | head -1)" | tr ' ' '\n' | grep '^VITE_IDENTITY'
# Local loopback expect: http://127.0.0.1:43101 — not gateway.aadharcha.in
# PreProd readiness: prefer FQDN apps with Vercel-baked gateway URL + Auth0
```

Owner fix: `scripts/start-dev.sh` `start_node` — strip `VITE_*`, apply `.env.local`, detach. PreProd UX: [`ondc-testing`](../ondc-testing/SKILL.md).

Portfolio browser **only** accepts:

`/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock`

A socket at `~/.hermes/run/chrome-bridge.sock` is the **live** Hermes path — not WIP. Extension “loaded” is not enough.

### Evidence path before “fixing” (mandatory)

```bash
ls -la /Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock
lsof /Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock 2>/dev/null
# manifest path must end with native_host_wip.sh (Comet + Chrome):
python3 -c "import json;from pathlib import Path
for a in ('Comet','Google/Chrome'):
 p=Path.home()/f'Library/Application Support/{a}/NativeMessagingHosts/com.hermes.chrome_bridge_cursor_wip.json'
 print(a, json.loads(p.read_text())['path'] if p.exists() else 'MISSING')"
bash /Users/gurusharan/plugins/hermes-chrome-cursor-wip/scripts/ensure-wip-native-host.sh
# Trust its Chrome profile output; the Hermes owner skill, not this project reference, owns the current expected profile.
# Open that profile's chrome://extensions and inspect service worker Active/Inactive.
```

| Observation | Meaning | Do |
| --- | --- | --- |
| Manifest ends `native_host_wip.sh`, no WIP sock, SW **Inactive** | Host died with SW | Reload / wake SW only in the discovered browser/profile |
| Manifest ends `native_host.py` | Classic path trap | `ensure-wip-native-host.sh` + reload |
| Live sock only; agents “fix” by using `~/.hermes` | Wrong workaround | Refuse — stay on WIP |
| Installing or launching a second WIP copy while another profile owns it | Wrong profile; splits cookies and socket ownership | Reopen the discovered owner profile; do not duplicate-install |

### Timeline sample (Auth0 → drop, 2026-07-12 IST)

| Time | Event | WIP sock |
| --- | --- | --- |
| 13:46–14:01 | Auth0 Hermes on Comet (dashboard → Universal Login evidence) | up |
| 14:07 | `start-dev.sh` (gateway only — does not kill Chrome) | — |
| 14:08 | `/tmp/hermes-refused.json`: socket not found after wake | **down** |
| 14:11 | Auth0 signed-in evidence (`auth0-buyer-signedin-20260712.*`) | up briefly |
| 14:09–14:15 | Recovery agent: `ensure` + `launch-wip-chrome` (`/tmp/launch-wip.out`); false “path trap” text while manifests already `native_host_wip.sh` | down / wrong profile |
| 14:13+ | Portal agent: sock missing; Comet SW **Inactive** + debugger banner | **down** |

| Wrong | Right |
| --- | --- |
| NativeMessagingHosts `path` → `…/native_host.py` | `path` → `…/native_host_wip.sh` |
| Agents rewrite manifests to `.py` “to fix” | Run `ensure-wip-native-host.sh` only |
| Point scripts at `~/.hermes/run/…` | Keep WIP socket only |
| Guess Comet or Chrome from whichever app is open | Use `ensure-wip-native-host.sh` app + profile discovery |
| Watch one profile while another holds the WIP extension | Match the discovered app **and profile directory** |

Repair in the Chrome profile reported by the Hermes owner preflight:

```bash
bash /Users/gurusharan/plugins/hermes-chrome-cursor-wip/scripts/ensure-wip-native-host.sh
# Operator/agent: exact reported profile → chrome://extensions or comet://extensions → Reload
# Wait until: ls …/run/chrome-bridge.sock && lsof that sock
python3 scripts/portfolio_browser.py preflight
```

## Cursor visibility (Hermes WIP)

- Overlay always injected; **starts hidden** (`opacity: 0`) until a cursor-driving action.
- `page_context` / `evaluate` / `snapshot` alone never reveal the pointer.
- Partner portal / Auth0 / deploy browser work: [apisetu-partner-onboarding](../apisetu-partner-onboarding/SKILL.md), [authentication](../authentication/SKILL.md), [portfolio-deploy](../portfolio-deploy/SKILL.md), [ondc-testing](../ondc-testing/SKILL.md).
