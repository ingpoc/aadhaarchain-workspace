# ONDC UI surface audit — stale AadhaarChain branding

Date: 2026-07-12  
Scope: user-facing Buyer (`:43102`) + Seller (`:43103`) copy/CTAs.  
Product truth: **AgentGuard** + ONDC apps; gateway host stays `aadharchain/` (not renamed).  
Runtime: `CURSOR_API_KEY` present on gateway + FlatWatch — not a residual.

## Counts

| Bucket | Removed / rewritten |
| --- | --- |
| UI strings (tsx/components/pages) | ~45+ AadhaarChain / identity-anchor / Resolve-in-AC CTAs |
| Shared trust-client messages (workspace + vendored copies) | 12 state messages + 2 fetch reasons |
| App READMEs (buyer/seller) | Rewritten product framing (2 files) |
| Left intentionally | `public/usecase.html` (legacy deck), `@aadharchain/agentguard-contract` package name, gateway folder, env var names `VITE_AADHAAR_API_URL` |

## Behavior fix (not just copy)

Demo/Google `principal:*` sessions had `walletAddress=null` → legacy trust defaulted to `no_identity` → **blocked checkout/catalog** and shamed users with “Resolve trust in AadhaarChain”.  

Now: `sessionSkipsLegacyTrust` / `elevatedTrustSatisfied` / `effectiveElevatedTrustState` skip legacy wallet-KYC wall; AgentGuard remains the money gate. Dead `:43100` trust CTAs removed from headers/notices. **Hangar user-copy purged** (code comments OK).

## Page inventory

| App | Route | Stale found | Fix applied | Tested? | Notes |
| --- | --- | --- | --- | --- | --- |
| Buyer | Shell / header | Trust meta “AadhaarChain…”, link to `:43100` | AgentGuard/session copy; no identity-host link | unit `App.test` | Google/Demo buttons already correct |
| Buyer | `/search` | AC trust CTA + copy | AgentGuard copy; notice only if not elevated | **Hermes 2026-07-12** DOM scan + shot `UI-AUDIT-search-*` | no AC strings |
| Buyer | `/results` | none material | — | none | |
| Buyer | `/product/:id` | AC checkout note | AgentGuard wording | none | |
| Buyer | `/cart` | “Verify on AadhaarChain” | Hide notice when session elevated | **Hermes 2026-07-12** `UI-AUDIT-cart-*` | empty cart OK |
| Buyer | `/checkout` | Trust-aware + AC wall + unpaid after AG | AG success card kept; AC wall gated; demo policy trust coerced | **Hermes 2026-07-12** cart→AG allow→redirect `/orders/:id`; shots `UI-AUDIT-checkout-*` / `UI-AUDIT-checkout-visit-*` | no AC / Resolve-trust / identity-anchor; unpaid form not shown after allow |
| Buyer | `/orders` | none material | — | none | |
| Buyer | `/orders/:id` | Resolve-in-AC CTA; cancel blocked | Session elevated; no AC CTA | **Hermes 2026-07-12** Paid + receipt `UI-AUDIT-checkout-paid-20260712-023201-*` | no AC strings; Paid badge + `rcpt_*` visible |

| Buyer | `/config` | already demo/Google oriented | — | none | |
| Buyer | `/agent` | Sign in to AC / Verify in AC | Google/demo copy; elevated gate | none | |
| Buyer | Samantha orb | none AC product name | — | prior matrix | |
| Buyer | TrustNotice/Chip | “AadhaarChain trust check”, Open AC | “Trust check”; no default `:43100` CTA | unit TrustStatus.test | |
| Seller | Shell / header | AC trust detail + `:43100` links | Session copy; links removed | none | |
| Seller | `/dashboard` | TrustNotice + publish disabled | elevatedOk gate | **Hermes 2026-07-12** `UI-AUDIT-seller-dash-*` | no AC strings |
| Seller | `/catalog` | Restricted until AC | Session elevated opens writes | unit CatalogPage.test | |
| Seller | `/catalog/new` edit | AC subtitles + Resolve CTA | Session copy; block only if !elevated | unit ProductEditPage.test | |
| Seller | `/orders` | actions disabled without verified | session principal allowed | none | |
| Seller | `/config` | Resolve operator trust in AC | CTA dropped; session can mutate | none | |
| Seller | `/agentguard` | TrustNotice chrome | Copy via TrustStatus | prior AG seller lane | |
| Seller | `/agent` | Sign in to AC | Google/demo copy | none | |
| Seller | TrustNotice | AC badge + Resolve CTA | Trust check; no `:43100` CTA | none | |
| Shared | trust-client reasons | identity anchor / AC verify | Sign-in / “optional advanced setup” (no hangar jargon) | unit trust.test | |

## Still untested (browser / ondc-testing)

- Seller catalog/config/orders write paths under demo SSO (unit covered; browser write not in this pass).
- Full Samantha matrix not re-run in this pass.
- `usecase.html` still has legacy AadhaarChain deck (intentional).

## Hermes spot-check (2026-07-12)

Demo SSO buyer: search/cart — no `AadhaarChain` / resolve-trust / identity-anchor in DOM. Seller dashboard same. Evidence: `references/evidence/UI-AUDIT-*-20260712-022651-*.jpeg`.

Checkout paid path (cart banana → Samantha `checkout_commit` allow → `/orders/{id}`): **Pass**. Paid + receipt; no AC / Resolve-trust / identity-anchor. Evidence: `references/evidence/UI-AUDIT-checkout-*-20260712-023201-*.jpeg` + `ui-audit-checkout-paid-20260712-023201.json`. Host-fill fix: `SamanthaOrb` `handleToolCallRef` (Realtime `onmessage` was stale on empty `subtotal`).

## Code files changed (this purge)

- `ondcbuyer/src/lib/trust.ts`, `protectedBuyerActions.ts`, `buyerActionPolicy.ts`, `agentBuyerState.ts`
- `ondcbuyer/src/components/TrustStatus.tsx` (+ test)
- `ondcbuyer/src/App.tsx` (+ test)
- `ondcbuyer/src/pages/{Checkout,Search,Cart,ProductDetail,OrderDetail,AgentChat}Page.tsx`
- `ondcbuyer/shared/trust-client/src/index.ts`, `ondcbuyer/README.md`
- `ondcseller/src/lib/{trust,sellerActionPolicy}.ts` (+ tests)
- `ondcseller/src/components/TrustStatus.tsx`
- `ondcseller/src/App.tsx`
- `ondcseller/src/pages/{ProductEdit,Catalog,Dashboard,Config,Orders,AgentChat}Page.tsx` (+ related tests)
- `ondcseller/shared/trust-client/src/index.ts`, `ondcseller/README.md`
- `shared/trust-client/src/index.ts`
- `ondcseller/src/lib/sellerApiRuntime.js` (error strings)

## Intentionally not rewritten

- `*/public/usecase.html` — long legacy narrative deck
- Package name `@aadharchain/agentguard-contract`
- Folder `aadharchain/` / gateway URLs
- AGENTS.md / ARCHITECTURE.md (out of this UI pass except inventory)
