# ONDC fetch doctrine (Buyer)

**Owner:** ondc-testing. Compact control vs data plane for PreProd Beckn search.

## Beckn data plane

- Search is **async**: `POST /api/ondc/search` → ACK + `transaction_id` ≠ catalogs. UI progress = inbox/`on_search` poll.
- **One intent → one txn**: never double-dispatch the same user ask (tool + ResultsPage both calling collect).
- **ACK ≠ enrichment**: Realtime tool returns on ACK + navigate; ResultsPage fills progressively.
- **Prefer-BPP** only when proving our Seller — do **not** gate first paint on full fanout.
- **Fail soft**: Free GW cold → wake/retry + “Pulling…”; hard error only after retries.

## Software control plane

- Samantha Realtime stays snappy: `search_catalog` = `dispatchBuyerSearch` + `navigateTo` + fast return (no catalog fanout in the tool).
- ResultsPage owns pull for `q` / `ondc_txn`; single-flight collect per txn; wait/peek for shared dispatch after early nav.
- Progressive: pulling → partial hits (`onPartial`) → complete; cold miss auto-retries.
- `navEpoch`: later cart/nav wins over stale search `navigateTo`.
- Observable: `__samanthaTools` + settle-validate before next ask.

## Code map

| Concern | Owner |
| --- | --- |
| Shared dispatch | `dispatchBuyerSearch` / `peekRecentSearchTxn` in `protocolClient.ts` |
| Catalog poll | `ondcCollectFromTxn` (single-flight) |
| Tool | `agentTools.ts` `search_catalog` |
| Page | `useApi`/`ResultsPage` — collect only; cold retry UI |
| Cache for add | `buyerCatalogCache` via `rememberOndcCatalogItems` on partial/final |

## Friction stamps

| Issue | Doctrine fix |
| --- | --- |
| Double ONDC poll / lag | Shared dispatch + page collect-only |
| Failed to fetch / hibernate 503 | `fetchGateway` retries + ResultsPage auto-retry |
| Hung catalogs (37s) | 8s abort per catalog GET |
| Prefer-BPP blocking paint | First non-empty batch paints; prefer optional |
