# ONDC sandbox — code → local smoke → deploy → web

**Policy:** Staging/sandbox first. **Prod only after GSTIN.** Do not flip `VITE_COMMERCE_DEMO_MODE`. Do not prod-submit. **$0 only** — Render Free / Vercel Hobby ([portfolio-deploy](../portfolio-deploy/SKILL.md)).

FQDNs (operator 2026-07-12): `ondcbuyer.aadharcha.in`, `ondcseller.aadharcha.in`. Keys: env PEM materialize on Render — see [`ondc-sandbox-keys.md`](ondc-sandbox-keys.md).

## Verdict — local vs web

| Can prove locally | Must prove on public FQDN (TLS) |
| --- | --- |
| Unit/API: keygen DER, decrypt challenge fixtures, AgentGuard evaluate/consume, Auth0 code path with local callback | Registry site verification (`ondc-site-verification.html`) |
| Gateway `/api/ondc/*` smoke with `ONDC_*` + mock/outbox (no live registry) | Registry `POST …/on_subscribe` challenge to subscriber URI |
| Buyer/Seller UI + demo commerce + local `AUTH_DEMO_CONTINUE` | Staging `/subscribe` ACK + lookup |
| Optional: tunnel/ngrok to local gateway for *dev* challenge dry-runs (not acceptance) | Staging search/order e2e vs ONDC ref apps |
| Auth0 Universal Login if tenant callbacks include `http://127.0.0.1:43101/...` | Staging/prod Auth0 against `PUBLIC_GATEWAY_URL` on Render |

**Full subscribe / on_subscribe cannot be accepted on localhost alone** — ONDC registry challenges the **whitelisted subscriber_id FQDN** over HTTPS.

## Pending — code (agent)

- [x] Fix `scripts/ondc_generate_keys.py` encryption public → **ASN.1 DER b64**
- [x] Implement site-verification + `/on_subscribe` — `ondc_onboard_routes.py`
- [x] Portal keys materialize → PEMs; PreProd auto key source (`ONDC_KEYS_SOURCE=auto`)
- [x] Env PEM loader for Render ephemeral FS (`ONDC_*_PRIVATE_PEM_B64`)
- [x] Vercel rewrite origin → `identity-aadhar-gateway-main.onrender.com`
- [x] Redeploy gateway + Vercel FQDN projects (2026-07-12)
- [x] PreProd `/subscribe` POST — **skip until needed**; portal already Subscribed; lookup needs signed auth
- [x] Staging/network e2e vs ref apps — **PreProd search+on_search Pass** 2026-07-12 (see ondc-testing `preprod-network-matrix.md`); select/confirm still open

## Pending — integrations (ops + agent)

| Integration | Status | Owner |
| --- | --- | --- |
| ONDC portal Buyer+Seller PreProd | **Subscribed** both | — |
| Portal key downloads | Local portal-download + **Render env PEM_B64** | — |
| Site verification + `/on_subscribe` local | **PASS** | Agent |
| Same on FQDN / Render | **PASS** 2026-07-12 (see Deploy stamp) | Agent |
| PreProd `/subscribe` | Portal Subscribed — **no blind re-POST**; lookup needs auth header | Agent |
| Auth0 on Render | **Live** (`/api/auth/providers` auth0:true, demo_continue:false) | — |
| Demo mode flip | Gated | After network evidence |

## Deploy stamp — 2026-07-12 ($0)

| Surface | Evidence |
| --- | --- |
| Render plan | **Free** (`identity-aadhar-gateway-main`, Docker) |
| Gateway commit | `933cadf` on `ingpoc/aadhaar-chain` `@codex/ondc-onboard-fqdn-20260712` |
| Key material | Render env `ONDC_{BUYER,SELLER}_*_PEM_B64` → `/tmp/ondc-env/{role}` |
| Vercel plan | **Hobby** — projects `ondc-buyer` / `ondc-seller` own FQDNs |
| Buyer deploy | `dpl_6TbnYCSW5dK792iVdCPqsbxuKq4g` → `ondcbuyer.aadharcha.in` |
| Seller deploy | `dpl_3x9Nrr6HdoUwwyg4CTMN96nbBEyR` → `ondcseller.aadharcha.in` |
| Probes | GW health/providers/buyer+seller status **200**; FQDN verify **200** + meta; `POST /ondc/on_subscribe` **400** decrypt (route live, not 404); SPA homes **200** |
| PreProd lookup | `POST …/v2.0/lookup` → NACK / auth header required — **no subscribe POST** |
| Hermes UI | Buyer `/search`, Seller `/dashboard` titles OK |

## Recommended ladder (refined)

1. ~~Code + portal keys local~~ **Done**
2. ~~Deploy — Render Free + Vercel Hobby~~ **Done** 2026-07-12
3. ~~Portal PreProd Subscribed~~ **Done**
4. ~~Live probe — FQDN verification + on_subscribe route~~ **Done**
5. Signed PreProd lookup / network e2e — **Done** BAP+BPP 2026-07-12 (ondc-testing matrix); select/confirm open; **no demo flip**

## Related

- Keys process: [`ondc-sandbox-keys.md`](ondc-sandbox-keys.md)
- Portal ledger: [`ondc-portal-ledger.md`](ondc-portal-ledger.md)
- Auth0: [`../authentication/SKILL.md`](../authentication/SKILL.md)
- Deploy / free-tier: [`../portfolio-deploy/SKILL.md`](../portfolio-deploy/SKILL.md)
- Ops A5–A8 / C3–C5: [`PRODUCTION-READINESS.md`](../../../PRODUCTION-READINESS.md)
- M9 / P0–P5: [`IMPLEMENTATIONPLAN.md`](../../../IMPLEMENTATIONPLAN.md)
