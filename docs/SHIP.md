# Ship path (Token Nxt portfolio — $0)

Fix → local test → PR CI → merge main → Portfolio Deploy → public FQDN
`assets/index-*.js` **must match** the no-hyphen `*.vercel.app` production alias.

## Path

1. **Fix** in the owning app repo (`ondc-buyer`, `ondc-seller`, or `aadhaar-chain`).
2. **Local test** in that app: `npm test` / `pytest`. Then from this workspace:

   ```bash
   ./scripts/local-ship-gate.sh
   ```

   Offline only. No Auth0, Chrome, UPI, live ONDC, AgentMail, or
   `VITE_COMMERCE_DEMO_MODE` flip. Render Free + Vercel Hobby (`$0`).
3. **PR + app CI** on the app repo. `cursor/*` pushes skip app CI until a PR
   exists — leave that. Merge to `main`.
4. **Workspace Portfolio CI** (PR → `ingpoc/aadhaarchain-workspace` `main`) is
   unique jobs only: AgentGuard contract parity, Gateway pytest+Postgres,
   offline graders. It does **not** re-run Buyer/Seller vitest (those stay in
   app CI).
5. **Deploy** is manual: Actions → **Portfolio Deploy** → Run workflow with
   `confirm_free_tier=true`. Git is **not** connected on the Vercel projects
   (Connect Git would hit GitHub OAuth / Security Checkpoint). CLI `--prod`
   via this workflow is the ship path. Stay Render **Free**
   (`identity-aadhar-gateway-main`, autoDeploy off) and Vercel **Hobby**.
6. **Public URL proof:** deploy fails unless FQDN `index-*.js` equals
   `vercel.app` `index-*.js`. HTTP 200 on `*.aadharcha.in` is not enough.

## Hyphen vs no-hyphen Vercel trap (2026-08-19)

`workflow_dispatch` run 6 shipped new production to:

| Alias | Bundle |
| --- | --- |
| `https://ondcbuyer.vercel.app` | `index-BNEIAZ9p.js` |
| `https://ondcseller.vercel.app` | `index-XX7NQ1aR.js` |

Public custom domains stayed on **old** bundles for hours because they were
attached to **different** Vercel projects:

| Wrong (hyphen) | Right (no hyphen) | Public FQDN |
| --- | --- | --- |
| `ondc-buyer` | `ondcbuyer` | `ondcbuyer.aadharcha.in` |
| `ondc-seller` | `ondcseller` | `ondcseller.aadharcha.in` |

Domains were moved onto Hobby team **"ingpoc's projects"** projects
`ondcbuyer` and `ondcseller`. `VERCEL_PROJECT_ID_BUYER` /
`VERCEL_PROJECT_ID_SELLER` must keep targeting those no-hyphen projects.

The next P0 cannot silently land on `vercel.app` while `aadharcha.in` stays
old: Portfolio Deploy extracts `assets/index-*.js` from both URLs and **fails
the job** on mismatch. Live FQDN functional journeys stay `--soft`; this hash
check is fail-closed on deploy.

Owner detail: [`.cursor/skills/portfolio-deploy/references/ci-cd.md`](../.cursor/skills/portfolio-deploy/references/ci-cd.md).
