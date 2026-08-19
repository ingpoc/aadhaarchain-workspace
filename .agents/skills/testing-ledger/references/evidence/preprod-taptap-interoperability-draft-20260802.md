# TapTap / ONDC interoperability message — prepared, not sent

**Status:** Draft only. No recipient has been selected and no message has been sent.

**Subject:** PreProd LOG10 1.2.5 `on_init` missing Immediate Delivery rider-check tag

Hello TapTap / ONDC interoperability team,

We are testing a synthetic ONDC PreProd B2C Logistics flow as the logistics buyer NP. TapTap returned HTTP 200/ACK for `init` and sent a registry-signature-verified `on_init`, but the callback did not contain the rider availability tag required by the current ONDC LOG10 1.2.5 validator for Immediate Delivery.

- BPP: `preprod-bpp.taptap.in`
- Transaction: `6f5a3bf8-fc4e-4b59-b0ab-1d09d7e75201`
- `init` message: `49a8c5ad-0bda-4afb-b1bf-53469158404a`
- Durable outbox: `pg_out_9944`
- Durable `on_init` inbox: `10190`
- Selected offer: `ONDC:LOG10` 1.2.5, `Immediate Delivery`, `P2P`, Delivery
- Expected: `rider_check → inline_check_for_rider=yes`
- Observed fulfillment tag codes: `linked_order`, `linked_provider`, `state`, `rto_action`
- Observed `inline_check_for_rider`: missing

Our LBNP therefore rejected the callback before `confirm`; no shipment, payment, legal-term acceptance, or later lifecycle action was created. We have not retried the identical payload.

Could you please confirm whether TapTap can return the required rider-check tag for this flow and validate the response against the official ONDC references?

- B2C Logistics contract: https://docs.google.com/document/d/1CkfxtqyLbSQccJZyNmf9BSGzJBH13gcLOk_tywV-LBk/edit
- v1.2.5 `on_init` validator: https://github.com/ONDC-Official/reference-implementations/blob/8105e9c57677dbbca22c9fdca897f19454ba5b01/utilities/logistics-b2b/log-verification-utility/utils/logistics/v1.2.5/logOnInit.js
- v1.2.5 `confirm` validator: https://github.com/ONDC-Official/reference-implementations/blob/8105e9c57677dbbca22c9fdca897f19454ba5b01/utilities/logistics-b2b/log-verification-utility/utils/logistics/v1.2.5/logConfirm.js

The attached packet is redacted: it contains immutable payload commitments and protocol identifiers, but no addresses, contacts, GPS coordinates, authorization headers, or keys.
