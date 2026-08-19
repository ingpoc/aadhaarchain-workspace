# ONDC sandbox — code → local smoke → deploy → web

**Policy:** Retail Buyer/Seller are already PreProd subscribed. The active
LOG10 path is a separate LBNP identity and must prove its own public endpoint
before portal registration. **Prod only after GSTIN and separate gate
evidence. $0 only** — Render Free / Vercel Hobby
([portfolio-deploy](../../portfolio-deploy/SKILL.md)).

Retail FQDNs: `ondcbuyer.aadharcha.in`, `ondcseller.aadharcha.in`. LOG10:
`ondclbnp.aadharcha.in` (public onboarding endpoint passed 2026-07-26; portal
registration pending). Keys: env PEM materialize on Render — see
[`ondc-sandbox-keys.md`](ondc-sandbox-keys.md).

## Verdict — local vs web

| Can prove locally | Must prove on public FQDN (TLS) |
| --- | --- |
| Unit/API: keygen DER, decrypt challenge fixtures, AgentGuard evaluate/consume, Auth0 code path with local callback | Registry site verification (`ondc-site-verification.html`) |
| Gateway `/api/ondc/*` smoke with `ONDC_*` + mock/outbox (no live registry) | Registry `POST …/on_subscribe` challenge to subscriber URI |
| Buyer/Seller UI + local `AUTH_DEMO_CONTINUE` | Registry/portal subscription + lookup |
| Optional: tunnel/ngrok to local gateway for *dev* challenge dry-runs (not acceptance) | Staging search/order e2e vs ONDC ref apps |
| Auth0 Universal Login if tenant callbacks include `http://127.0.0.1:43101/...` | Staging/prod Auth0 against `PUBLIC_GATEWAY_URL` on Render |

**Full subscribe / on_subscribe cannot be accepted on localhost alone** — ONDC registry challenges the **whitelisted subscriber_id FQDN** over HTTPS.

## Retail foundation (completed)

- [x] Fix `scripts/ondc_generate_keys.py` encryption public → **ASN.1 DER b64**
- [x] Implement site-verification + `/on_subscribe` — `ondc_onboard_routes.py`
- [x] Portal keys materialize → PEMs; PreProd auto key source (`ONDC_KEYS_SOURCE=auto`)
- [x] Env PEM loader for Render ephemeral FS (`ONDC_*_PRIVATE_PEM_B64`)
- [x] Vercel rewrite origin → `identity-aadhar-gateway-main.onrender.com`
- [x] Redeploy gateway + Vercel FQDN projects (2026-07-12)
- [x] Retail portal records already Subscribed — no blind `/subscribe` replay
- [x] Signed PreProd Gate 1 search + correlated `on_search` passed
      2026-07-25; do not repeat the frozen search

## Current boundaries

| Integration | Status | Owner |
| --- | --- | --- |
| Retail Buyer/Seller PreProd | **Subscribed**; preserve registration, keys, callbacks, and Gate 1 evidence | Testing ledger |
| LBNP local identity | Dedicated subscriber, callback base, and distinct keypair exist | Gateway owner |
| LBNP public endpoint | **Pass** — DNS, TLS, status, site verification, and valid challenge/answer | Portfolio deploy |
| LBNP portal environment access | Not raised/subscribed; endpoint prerequisite now satisfied | Partner onboarding |
| Production | Blocked until GSTIN and separate evidence | Production readiness |

## Deploy stamp — 2026-07-12 ($0)

| Surface | Evidence |
| --- | --- |
| Render plan | **Free** (`identity-aadhar-gateway-main`, Docker) |
| Gateway commit | `933cadf` on `ingpoc/aadhaar-chain` `@codex/ondc-onboard-fqdn-20260712` |
| Key material | Render env `ONDC_{BUYER,SELLER}_*_PEM_B64` → `/tmp/ondc-env/{role}` |
| Vercel plan | **Hobby** — projects `ondc-buyer` / `ondc-seller` owned FQDNs that day. **Superseded 2026-08-19:** FQDNs on no-hyphen `ondcbuyer` / `ondcseller`; see [`docs/SHIP.md`](../../../../docs/SHIP.md) |
| Buyer deploy | `dpl_6TbnYCSW5dK792iVdCPqsbxuKq4g` → `ondcbuyer.aadharcha.in` |
| Seller deploy | `dpl_3x9Nrr6HdoUwwyg4CTMN96nbBEyR` → `ondcseller.aadharcha.in` |
| Probes | GW health/providers/buyer+seller status **200**; FQDN verify **200** + meta; `POST /ondc/on_subscribe` **400** decrypt (route live, not 404); SPA homes **200** |
| PreProd lookup | `POST …/v2.0/lookup` → NACK / auth header required — **no subscribe POST** |

## LBNP deploy stamp — 2026-07-26 ($0)

| Surface | Evidence |
| --- | --- |
| Render runtime | Existing Free service; exact commit `b3e81b2e...`, deploy `dep-d9irpocm0tmc73a0st7g` |
| DNS | GoDaddy CNAME `ondclbnp` → `identity-aadhar-gateway-main.onrender.com`; second included Render domain |
| Key material | Distinct env-backed LBNP pair; local private PEMs enforced at `0600` |
| Probes | Public DNS/TLS, dedicated status, site verification, and valid challenge/answer **pass**; Retail probes remain 200 |
| Claim boundary | Endpoint readiness only; no portal, registry, LSP, logistics protocol, order, payment, or production claim |

## Active LOG10 ladder

1. Reuse the existing gateway and HTTPS edge; no parallel service.
2. Verify the exact hosting target before changing DNS.
3. Add the one approved GoDaddy record.
4. Prove public DNS, TLS, site-verification, and `/ondc/on_subscribe` readback.
5. Only then resume portal environment access for profile `15462-10220`.
6. Stop before `1.b`, legal tasks, registry mutation, protocol calls, or
   production unless separately authorized.

## Related

- Keys process: [`ondc-sandbox-keys.md`](ondc-sandbox-keys.md)
- Portal ledger: [`ondc-portal-ledger.md`](ondc-portal-ledger.md)
- Auth0: [`authentication`](../../authentication/SKILL.md)
- Deploy / free-tier: [`portfolio-deploy`](../../portfolio-deploy/SKILL.md)
- Ops A5–A8 / C3–C5: [`.session/docs/PRODUCTION-READINESS.md`](../../../../.session/docs/PRODUCTION-READINESS.md)
- Current milestone sequencing: [`.session/docs/IMPLEMENTATIONPLAN.md`](../../../../.session/docs/IMPLEMENTATIONPLAN.md)
