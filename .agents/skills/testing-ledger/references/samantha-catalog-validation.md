# Samantha catalog data validation (Buyer)

Use this **with** operator journeys when the ask is “does Samantha show the right things?” Blind customer acceptance alone cannot catch hallucinated offers or wrong keywords.

## Ground truth first (required)

Before any Samantha ask, freeze inventory from owners (not from the orb):

```bash
# Demo-commerce published catalog (configured Seller → Buyer search)
curl -s 'http://127.0.0.1:43101/api/demo-commerce/buyer/search' | python3 -m json.tool
# Per-query expected hits
for q in atta dal milk banana flour; do
  curl -s "http://127.0.0.1:43101/api/demo-commerce/buyer/search?q=$q"
done

# ONDC network lane (optional second truth)
python3 scripts/ondc_preprod_smoke.py --base http://127.0.0.1:43101 --search atta
# Inspect catalogs.our_seller_items + count
```

Record a **truth table** for the run:

| Query | Expected demo-commerce titles | Expected ONDC our-seller | Notes |
| --- | --- | --- | --- |
| `atta` | … | … | |
| `dal` | … | … | |
| `banana` | … | … | |
| `roti` / `tonight` | usually **none** | … | NL filler — must not be the search keyword |

If expected inventory is empty, **seed** before blaming Samantha (test-fixtures publish), or mark the case **Blocked: empty catalog**.

## Ask Samantha against the table

For each row:

1. One orb ask using a natural phrase that should resolve to that query (e.g. “I need toor dal” / “show whole wheat atta”).
2. Settle–validate–next.
3. Capture: URL `q=`, results grid titles/prices, orb claim text, `__samanthaTools` `search_catalog` query + returned item names/ids.

## Compare (pass / fail codes)

| Code | Meaning |
| --- | --- |
| **HIT** | Expected item title (or clear synonym) appears in results grid with plausible price |
| **MISS** | Expected item exists in ground truth but not in results / tool payload after settle |
| **JUNK** | Results show unrelated titles for the query (or NL filler keyword like `roti`/`tonight`) |
| **GHOST** | Orb/tool claims a named SKU that is **not** in ground truth and not on the results grid |
| **STALE** | Tool/cache ids refer to items no longer published |
| **SKIP-UI** | Orb adds/navigates to cart without a visible results comparison step when the ask was find-only |

**Samantha catalog Pass** for a query requires HIT and no GHOST/JUNK/STALE on that turn.  
Journey UX Pass is separate (see operator-protocol / independent-customer-gate).

## Suggested smoke set (local)

1. Truth snapshot of `buyer/search`.
2. Ask for a **present** SKU (e.g. published dal or atta) → expect HIT.
3. Ask for a **known-absent** SKU (e.g. banana when not published) → expect honest empty/loading, not GHOST.
4. NL ask that includes purpose words (“atta for roti tonight”) → URL/`q` must be product noun (`atta`), not `roti`/`tonight`.
5. Find-only ask must not unsolicited `add_to_cart` (SKIP-UI).

## Relation to lanes

| Lane | Role |
| --- | --- |
| This doc + API truth table | Data correctness of Samantha search/add claims |
| Blind independent customer gate | Can a novice complete shopping without implementation knowledge |
| `hermes_ondc_testing_matrix.py` | Deterministic regression aid — still not a substitute for truth-table HIT/MISS |

Append outcomes to [`matrix-status.md`](matrix-status.md) with flow ids `B-FIND-*` plus a `data:` note (`HIT`/`MISS`/`GHOST`/…).
