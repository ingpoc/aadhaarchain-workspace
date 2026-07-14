# ONDC / Samantha query matrix (thin index)

Natural-language asks → stable flow IDs. **Full journeys, tools, pass signals, change-class map:** [`operator-flows.md`](operator-flows.md) (sole owner).  
Pass = claim verified by screenshot (agent **Read**s the image). Ledger: [`matrix-status.md`](matrix-status.md).

## Buyer (`:43102` / FQDN)

| ID | Example ask | Pass (one-liner) |
| --- | --- | --- |
| B-HI | “hi” | No tools; stay put |
| B-THX | “thanks” | No tools |
| B-FIND-BANANA | “find bananas” | Early `/results`; offers UI |
| B-FIND-ATTA | “search for atta” | Early `/results`; marker if published |
| B-FIND-NL-ATTA | “I need whole wheat atta under 200” | NL → catalog query; results/cart |
| B-FIND-MILK | “find milk under 100” | Results / filter |
| B-FIND-APPLE | “show Shimla apples” | Apple results |
| B-ADD-BANANA | “add banana to my cart” | `/cart` line |
| B-NAV-CART | “go to my cart” | `/cart` |
| B-NAV-CHECKOUT | “go to checkout” | `/checkout` |
| B-NAV-CONFIG | “open config” | `/config` |
| B-NAV-ORDERS | “show my orders” | Orders UI |
| B-MEM-ORG | “remember I prefer organic” | Memory write |
| B-CHECKOUT-OK | “checkout / pay” | Paid+receipt or AG card |
| B-CHECKOUT-OVER | over-limit checkout | need_approval / deny UI |
| B-AG-CONFIRM | Confirm mandate (UI) | Mandate confirmed / active |
| B-EMPTY | unicorn cereal | Honest empty |
| B-LONG-WEEKLY / B-RUNTIME | “plan weekly groceries under 2000” | Handoff; not `/agent` |
| B-VOICE-* | same via mic | Connected + visible outcome |

## Seller (`:43103` / FQDN)

| ID | Example ask | Pass (one-liner) |
| --- | --- | --- |
| S-HI | “hi” | No tools |
| S-NAV-CAT | “open catalog” | `/catalog` |
| S-NAV-ORD | “show orders” | `/orders` |
| S-NAV-AG | “open agentguard” | `/agentguard` |
| S-AG-PAUSE | Pause agent (UI) | Agent paused on `/agentguard` |
| S-PUBLISH | publish simple item | Catalog change |
| S-REFUND-OK | refund in-limit | AG allow/executed |
| S-REFUND-OVER | refund over-limit | need_approval / deny |
| S-MEM | brief confirmations memory | Memory if shown |
| S-LONG-TRIAGE / S-RUNTIME | bulk triage | Handoff; not `/agent` |
| S-VOICE-* | voice twins | Same voice bar |

## Thorough / live

| ID | Notes |
| --- | --- |
| B-TOOL-* / S-TOOL-* | Each tool once — see SKILL thorough bar |
| W-* | FQDN twins of above — **PreProd gate** |
| W-B-FIND-NL-ATTA / W-B-AG-CONFIRM / W-S-AG-PAUSE | Demo-video / PreProd readiness trio |

Gaps: [`integration-gaps.md`](integration-gaps.md).
