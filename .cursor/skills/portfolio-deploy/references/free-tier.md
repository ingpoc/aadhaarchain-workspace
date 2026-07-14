# Free-tier policy (portfolio — $0 hard gate)

> **HARD POLICY — $0 ONLY.** Always stay on free tier. Do **not** mistakenly
> spend even one cent. **Abort** any upgrade, billing change, or paid add-on.
> Cold starts OK. No Render Disk for PEMs. **Confirm Free (Render compute) /
> Hobby (Vercel + Render workspace) before every deploy.**
>
> Docs stamped **2026-07-12** from [Render free](https://render.com/docs/free),
> [new workspace plans](https://render.com/docs/new-workspace-plans),
> [outbound bandwidth](https://render.com/docs/outbound-bandwidth),
> [Vercel Hobby](https://vercel.com/docs/plans/hobby),
> [fair use](https://vercel.com/docs/limits/fair-use-guidelines).

Generic Render flows: `~/.agents/skills/render-deploy/SKILL.md` + Cursor Render
plugin skills — **do not duplicate** here.

## Operator abort rules

| Signal | Action |
| --- | --- |
| Dashboard/CLI offers upgrade, Pro, paid instance, billing card | **Stop.** Do not click / confirm |
| Prompt to attach **Render Disk** (for PEMs or anything) | **Abort.** Use env + `/tmp` |
| Paid Postgres / always-on “fix” for cold starts | **Abort.** Cold starts accepted |
| Plan shows anything other than Free compute / Hobby workspace | **Do not deploy** until corrected |
| “Add payment method” to unlock reliability | **Abort.** Prefer suspend-over-bill |
| Custom domain beyond Hobby included count (new plan) | **Abort** or drop unused domains first |
| Vercel Password Protection / Pro trial with card | **Abort** (Hobby has Auth protection only) |

## Confirm before deploy

1. Render gateway **instance type** = **Free** (512 MB / 0.1 CPU)
2. Render **workspace plan** = **Hobby** ($0) — note legacy vs new (below)
3. Vercel `ondcbuyer` + `ondcseller` = **Hobby**
4. No Disk, no paid Postgres/KV, no paid add-ons in the deploy path
5. Billing page: prefer **no payment method** (or pipeline spend limit **$0**) so overages **suspend** instead of charge

---

## Render — Free feature inventory

### Free compute types (what exists)

| Type | Free? | Portfolio use |
| --- | --- | --- |
| Web service | **Yes** (Free instance) | Gateway — **in use** |
| Static site | **Yes** (counts bandwidth + pipeline) | Skip — Buyer/Seller on Vercel |
| Postgres | **Yes** but **1/workspace**, **1 GB**, **expires 30 days** (+14d grace → delete or upgrade) | **Do not use** for AgentGuard/ONDC keys |
| Key Value (Redis-compatible) | **Yes** but **1/workspace**, in-memory only, data lost on restart | Skip (no need) |
| Background worker / cron / private service | **No** Free instance | Skip |
| Persistent **Disk** | **Not on Free** (paid attach) | **Never** |

### Free web service — included capabilities

| Feature | Free? | Notes |
| --- | --- | --- |
| Custom domains + managed TLS | **Yes** | `gateway.aadharcha.in` — **in use** |
| Env vars + secret files | **Yes** | PEMs via `*_PEM_B64` / secrets — **in use** |
| Environment groups | **Yes** (Hobby) | Low value with **one** service — unused |
| HTTP health checks | **Yes** | Set path `/health` or `/api/health` — **configure** |
| Auto-deploy from Git branch | **Yes** | Intentionally muted; Actions `workflow_dispatch` owns prod |
| Service previews (PR) | **Yes** | Optional; burns pipeline minutes — skip unless needed |
| Log streams to external sink | **Yes** (log stream traffic **not** billed as outbound BW) | Skip until free sink exists |
| Rollbacks | **Yes** (last **2** deploys only) | Use on bad deploy |
| Zero-downtime deploys | Limited (no Disk helps) | Default TCP/HTTP health |
| Metrics / dashboard logs | **Yes** | Retention is short; pull when debugging |
| Private network **receive** | **No** on Free web | Free can **send** to same-region datastores/paid |
| SSH / one-off jobs / edge caching / scale >1 | **No** on Free | Abort if prompted to unlock via paid |

### Free web service — hard limits

| Constraint | Value | Implication |
| --- | --- | --- |
| Spin-down | **15 min** idle (HTTP + WS) | Cold start ~**1 min**; wake `/api/health` before demos |
| Ephemeral FS | Always | Writes vanish on redeploy/restart/spin-down |
| Free instance hours | **750 / month / workspace** | Spun-down time does **not** consume hours |
| Concurrent instances | **1** | No horizontal scale |
| Restarts | Anytime | Expect occasional blips |
| Outbound SMTP ports 25/465/587 | Blocked | No mail from Free web |
| Reserved listen ports | 18012, 18013, 19099 | Avoid |
| Service-initiated traffic flood | May suspend service | Keep outbound API chatter modest |
| Spun-down `/robots.txt` | Auto disallow-all (no wake) | Fine for API gateway |

### Workspace plan quotas (bandwidth / builds / domains)

Render split **workspace plan** (Hobby/Pro/…) from **instance type** (Free/Starter/…).

| Quota | Legacy Hobby | **New Hobby** (opt-in now; auto **2026-08-01**) |
| --- | --- | --- |
| Plan fee | $0 | $0 |
| Outbound bandwidth | **100 GB**/mo | **5 GB**/mo then **$0.15/GB** if card on file |
| Build pipeline minutes | **500**/mo | **500**/mo (then bill or disable builds) |
| Custom domains included | 2 | **2** then **$0.25/domain/mo** |
| Services cap | Unlimited | **25** total |

**Portfolio domain math:** Render custom domain today = `gateway.aadharcha.in` (1 of 2). Buyer/Seller FQDNs are **Vercel**, not Render. Stay ≤2 Render custom domains forever on Hobby.

**Bandwidth math:** Prefer **legacy Hobby** until forced migration; after **2026-08-01** treat **5 GB** as the real ceiling. Demo SPA traffic hits Vercel; gateway responses + Auth0/OpenAI/Cursor egress count on Render.

### What triggers **charges** on Render (abort)

| Trigger | Cost signal | Portfolio action |
| --- | --- | --- |
| Upgrade Free → **Starter** (or any paid instance) | ~$7+/mo compute | **Abort** |
| Attach **persistent Disk** | Paid; Free cannot | **Abort** — use `DATA_DIR=/tmp/…` + env PEMs |
| Create/upgrade **paid Postgres** | Monthly compute | **Abort**; Free Postgres is throwaway-only |
| Free Postgres past 30d → “upgrade to keep data” | Paid | **Delete** DB; never upgrade |
| Exceed bandwidth **with payment method** | $/GB | Prefer **no card**; else suspend-over-bill |
| Exceed pipeline minutes **with card** / no spend limit | $ | Set spend limit **$0** or no card |
| Custom domains **> included** (new Hobby) | $0.25/mo each | Drop extras; do not add 3rd |
| Opt into **Pro/Scale** workspace | $25+ / $499+ | **Abort** |
| Edge caching / paid add-ons | Paid | **Abort** |

**Card-on-file trap:** Even with Free instances, a payment method turns bandwidth/pipeline overages into **bills**. No card → services/builds **suspend** instead. For $0 policy, **no payment method** is the safer default.

---

## Vercel — Hobby feature inventory

### Included usage (Hobby — no overage billing; pause instead)

| Resource | Hobby included | Portfolio note |
| --- | --- | --- |
| Fast Data Transfer | **~100 GB**/mo | Buyer+Seller SPA + rewrite proxies |
| Fast Origin Transfer | **~10 GB**/mo | Rewrites to gateway count toward origin |
| Edge Requests | **~1M**/mo | |
| Function invocations | **1M** | Vite static → near-zero functions |
| Active CPU / Provisioned Memory | 4 CPU-hrs / 360 GB-hrs | |
| Deployments / day | **100** | Batch; don’t loop CLI |
| Projects | **200** | |
| Domains / project | **50** | `ondcbuyer` / `ondcseller` FQDNs — **in use** |
| Preview deployments | **Yes** | Free; use Preview env vars |
| Runtime logs | **1 hour** | |
| Web Analytics events | **50k**/mo | Hobby-free — **enable** |
| Speed Insights | **10k events**, **1 project** | Enable on **Buyer only** |
| WAF IP blocks / custom rules | 3 / 3 | Optional |
| DDoS mitigation | On by default | Keep |
| Deployment Protection | **Vercel Authentication** (previews) | Production stays public on Hobby |
| Password Protection | **Pro add-on** | **Abort** if offered |
| Log drains | Pro | Skip |
| Team / multi-seat git deploy | Blocked for HUF author | Use archive/`--archive=tgz` workaround — **known** |

### Commercial-use rule (fair use)

Hobby = **non-commercial personal** only. Revenue, paid consulting to build/host, ads, donations → requires Pro. Token Nxt **sandbox/demo** stays Hobby; if FQDN hosting becomes paid commercial use, **policy conflict** — escalate to operator (still $0 → leave Hobby or stop commercial use; never silent Pro upgrade).

### What triggers **charges** / forced Pro on Vercel

| Trigger | Effect | Action |
| --- | --- | --- |
| Upgrade to **Pro** | $20+/seat + usage | **Abort** |
| **Password Protection** add-on | Paid (Pro) | **Abort** — use public prod + Auth0 |
| Web Analytics **Plus** / Speed Insights Plus | Paid add-ons | **Abort** — stay on included quotas |
| Exceed Hobby quotas | **Pause** (not charge) | Wait for reset; reduce traffic |
| Commercial-use enforcement | Forced Pro or suspension | Keep demo non-commercial |
| Blob / paid storage overages | Can bill on paid plans | Don’t enable paid storage |

Hobby does **not** bill overages the way Pro does — it **pauses**. Still abort any path that asks for a card.

---

## Configure these free features (maximize $0 value)

### Render gateway — do / verify

| Action | Status intent | How |
| --- | --- | --- |
| Instance = **Free** | Required | Dashboard → service → Instance type |
| Custom domain + TLS | **In use** | `gateway.aadharcha.in` |
| Env secrets (Auth0, PEMs, CORS, …) | **In use** | Environment tab — never git |
| `DATA_DIR=/tmp/aadharchain-data` | **Live** | Dockerfile default + Render env; AgentGuard ensure **200**; **no Disk** |
| HTTP health check path `/health` or `/api/health` | **Live** | Dashboard Health Check Path = `/api/health` (Free instance); app also serves `/health` |
| Auto-deploy from Git | **Skip intentionally** | Prefer Actions `workflow_dispatch` + `confirm_free_tier` |
| Service previews | **Skip** | Burns pipeline minutes |
| Log stream | **Skip** | No free sink yet; dashboard logs OK |
| Env groups | **Skip** | Single service — no share target |
| Free Postgres / KV | **Skip** | 30-day trap / ephemeral KV |
| Wake before demos | **In use** | `curl` `/api/health` |

### Vercel Buyer / Seller — do / verify

| Action | Status intent | How |
| --- | --- | --- |
| Projects on **Hobby** | Required | Settings → Billing |
| Production aliases FQDNs | **In use** | `ondcbuyer.aadharcha.in` / `ondcseller.aadharcha.in` |
| Preview + Production env (`VITE_IDENTITY_*`, …) | **In use** | Mirror Production → Preview |
| `vercel.json` rewrites → gateway FQDN | **In use** | Redeploy after change |
| Web Analytics (included) | **Live** | Package + script **200**; Hobby **Enable** clicked 2026-07-12 on `ondc-buyer` + `ondc-seller` (boards left Demo Data → live 0-event) |
| Speed Insights | **Buyer only** | Live in Buyer bundle; Seller skipped (Hobby 1-project quota) |
| Password Protection | **Never** | Abort |
| Git-author seat block | **Workaround** | Non-git archive deploy (see SKILL CLI) |

---

## Gaps — free but unused vs intentionally skipped

| Feature | Why unused / skipped |
| --- | --- |
| Render Free Postgres | 30-day expiry + upgrade trap; AgentGuard file store OK with `/tmp` |
| Render Free Key Value | Restart wipes data; no shared-cache need yet |
| Render static sites | Buyer/Seller already on Vercel Hobby CDN |
| Render env groups | Only one Free web service |
| Render auto-deploy on push | Intentionally gated by Actions free-tier confirm |
| Render service previews | Pipeline-minute cost; low value for gateway |
| Render log drains/streams | No free third-party sink configured |
| Vercel Speed Insights on Seller | Hobby = **1 project**; Buyer preferred |
| Vercel Edge Config / Blob | Not needed for Vite SPA shells |
| Vercel WAF custom rules | Optional; defaults + DDoS enough for demo |
| Always-on / paid Disk | Explicit **non-goals** ($0) |

---

## Charge-risk watchlist (encode in every deploy)

Check these **before** any mutate. Any “yes” → **abort** or fix without spending.

1. **Render Disk attach** UI / Blueprint `disk` / `diskSizeGB`
2. **Instance type** ≠ Free (Starter/Standard/…)
3. **Payment method** on Render + bandwidth near limit (esp. after **2026-08-01** → 5 GB)
4. **Custom domains** count > Hobby included (**2** on new Hobby)
5. Free **Postgres** aging toward day 30 / upgrade email
6. **Pipeline minutes** exhausted with card / no $0 spend limit
7. Vercel **Pro** / Password Protection / Analytics Plus / Speed Insights Plus
8. Hobby **commercial-use** expansion (paid commercial FQDN hosting)
9. Accidental **second** paid region/service clutter toward 25-service cap
10. “Just upgrade to fix cold start / Permission denied” — fix `DATA_DIR=/tmp/aadharchain-data` instead

### Ephemeral storage best practice (Free)

```text
DATA_DIR=/tmp/aadharchain-data
ONDC_ENV_KEYS_DIR=/tmp/ondc-env
```

Image/Dockerfile and Render env should agree. **Never** attach Disk to “fix” Permission denied on `./data`.

---

## Portfolio stamp (2026-07-12)

| Surface | Plan | Free features active |
| --- | --- | --- |
| Gateway | Render Free instance + Hobby workspace | Custom domain TLS, env PEMs, health `/api/health`, cold-start accepted, `/tmp` data dir |
| Buyer/Seller | Vercel Hobby | FQDN aliases, Preview envs, rewrites, Web Analytics **enabled** (Hobby) |
| CI | GitHub Actions free | Graders; deploy only via `confirm_free_tier=true` |

### Applied live — 2026-07-12 evening ($0 Free/Hobby)

| Item | Result |
| --- | --- |
| Render `DATA_DIR=/tmp/aadharchain-data` | **Confirmed live** — `POST /api/agentguard/agents/ensure` **200** (writable; no Disk / no gateway redeploy needed) |
| Gateway health routes | `/health` + `/api/health` **200** on `gateway.aadharcha.in` + onrender |
| Render health-check setting | **Confirmed live** — Settings → Health Checks path `/api/health`; instance **Free** (Hermes WIP 2026-07-12). Evidence: `references/evidence/render-health-check-api-health-20260712.jpeg` |
| Vercel Hobby Buyer | Archive redeploy + alias `ondcbuyer.aadharcha.in` — bundle has `/_vercel/insights` + `/_vercel/speed-insights` |
| Vercel Hobby Seller | Archive redeploy + alias `ondcseller.aadharcha.in` — Web Analytics only (no Speed Insights) |
| Vercel Web Analytics Enable | **Done** Hobby-included (not Pro $20) on `ondc-buyer` + `ondc-seller`; Demo Data cleared → live boards (0 events pending traffic). Evidence: `vercel-*-analytics-enabled-20260712.jpeg` |
| FQDN probes | GW health/providers/buyer+seller status **200**; both `/ondc-site-verification.html` **200**; SPA shells **200** |
| Analytics script CDN | `/_vercel/insights/script.js` **200** both; Speed Insights script **200** (Buyer component wired) |
| Spend | **$0** — no Disk / Starter / Pro / Password Protection / Analytics Plus |

**Remaining operator UI (no spend):** none for this free-tier maximize pass.
