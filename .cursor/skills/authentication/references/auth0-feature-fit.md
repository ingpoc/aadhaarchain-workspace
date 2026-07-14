# Auth0 feature fit (AgentGuard + ONDC)

Canonical Auth0 docs: https://auth0.com/docs

## Identity vs authorization split

| Layer | Owner | Examples |
| --- | --- | --- |
| Who is the user? | **Auth0** + gateway session | Login, MFA, social, org membership |
| What may the agent spend / refund? | **AgentGuard** | Mandates, evaluate, approve, receipts |
| What is on the network? | **ONDC adapter** (later) | Beckn search/confirm |

Never merge AG money policy into Auth0 Actions.

## Recommended adoption order

1. **Now:** Universal Login, social connections (Google via Auth0), Authorization Code Flow (done in gateway), Attack Protection on.
2. **Next (Seller prod):** MFA for elevated seller principals; optional Adaptive MFA.
3. **When multi-tenant sellers:** Organizations + Post-Login Action → `org_id` custom claim → copy into `aadharcha_session` / AG agent metadata.
4. **Later:** Passkeys/passwordless via Universal Login; enterprise SAML; refresh tokens only if a non-cookie client appears.

## Post-Login Action pattern (safe)

Allowed: enrich tokens/session with identity metadata.

```javascript
exports.onExecutePostLogin = async (event, api) => {
  if (event.user.email_verified) {
    api.idToken.setCustomClaim('email_verified', true);
  }
  if (event.organization) {
    api.idToken.setCustomClaim('org_id', event.organization.id);
    api.idToken.setCustomClaim('org_name', event.organization.display_name);
  }
  // Do NOT set checkout limits or AgentGuard decisions here.
};
```

Gateway may later read ID token claims during callback and persist on the session cookie payload (`display_name`, `email`, optional `org_id`).

## Audience (`AUTH0_AUDIENCE`)

Use when calling a separate Auth0 Resource Server API. Current portfolio apps use the **gateway cookie**, not Auth0 access tokens, for AG. Set audience only if introducing Auth0-protected APIs beyond the cookie session.

## Logout (prod polish)

1. `POST /api/auth/logout` — clear `aadharcha_session` (exists).
2. Optional redirect to `https://{AUTH0_DOMAIN}/v2/logout?client_id=…&returnTo=…` with `returnTo` on Auth0 allowlist (Buyer/Seller FQDNs + local `:43102`/`:43103`).

## Deploy hosts (cookie + CORS)

| Surface | Host |
| --- | --- |
| Buyer | `https://ondcbuyer.aadharcha.in` |
| Seller | `https://ondcseller.aadharcha.in` |
| Gateway | `https://identity-aadhar-gateway-main.onrender.com` |

Cross-site session: gateway sets host-only `aadharcha_session` with `SameSite=None; Secure` when staging/prod (or HTTPS `PUBLIC_GATEWAY_URL`). SPA uses `credentials: 'include'` to the Render origin. Do not set `Domain=.aadharcha.in` while the cookie is issued from `*.onrender.com`.

## Testing

| Env | How to sign in |
| --- | --- |
| Local loopback | `AUTH_DEMO_CONTINUE=true` → demo-continue CTA / hermes `sso demo` |
| Local + Auth0 | Set `AUTH0_*`, Sign in CTA, real Universal Login |
| Staging/PreProd | Auth0 only (demo-continue forced off) |

Providers probe: `GET /api/auth/providers` → `{ auth0, google, demo_continue, runtime_mode }`.
