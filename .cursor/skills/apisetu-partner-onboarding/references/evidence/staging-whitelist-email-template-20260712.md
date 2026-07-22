# Staging whitelist email (send if portal EnvAccessRequest keeps failing)

**To:** techsupport@ondc.org  
**Cc:** gurusharan.gupta@aadharcha.in  
**Subject:** Staging subscriber_id whitelist — org 15462 GURUSHARAN GUPTA HUF (Buyer + Seller Retail)

Hello ONDC Tech Support,

Please whitelist the following subscriber_ids for **Staging** registry access (not production):

| Role | Profile | subscriber_id (FQDN) |
| --- | --- | --- |
| Buyer NP | 15462-10008 Retail B2C API v1.2 | `ondcbuyer.aadharcha.in` |
| Seller NP — ISN | 15462-10011 Retail B2C API v1.2 | `ondcseller.aadharcha.in` |

Org: **15462** — **GURUSHARAN GUPTA HUF**  
Domain: Retail (B2C) / `ONDC:RET10`  
Email: gurusharan.gupta@aadharcha.in  

Portal note: Buyer Integration Journey task 1.a EnvAccessRequest UI is locked to **Registry=PreProd** and Submit fails with ``Valid_from` must be in ISO 8601 date format`` + `saveHandler` undefined status (portal bug). We need **staging** whitelist ACK to call `https://staging.registry.ondc.org/subscribe`.

Thank you.
