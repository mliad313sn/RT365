# MARKET_LAUNCH_CHECKLIST

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Compliance Agent (regulatory) / Trading Domain Lead (technical) / GTM Lead (commercial) | Legal Agent | Compliance & Legal Committee, Executive Steering | F | Draft v1.0 |

Per market [Source: 17]; each item is evidenced, not asserted. Enablement requires legal record + technical flag (dual key) [Source: 07; Committee].
| # | Item | Owner | Evidence | Status |
|---|---|---|---|---|
| 1 | Legal basis and regulator | Legal | COMPLIANCE_MATRIX row | |
| 2 | Broker capability certified | Broker-Connector | BROKER_CERTIFICATIONS/ | |
| 3 | Instrument identifiers | Data Eng | instrument master tests | |
| 4 | Sessions and holidays | Data Eng | calendar tests | |
| 5 | Currencies | Backend | tests | |
| 6 | Tick / lot sizes | Backend | rounding tests | |
| 7 | Order types | Broker-Connector | certification | |
| 8 | Settlement | Trading Domain | tests | |
| 9 | Short-sale rules | Compliance | eligibility tests | |
| 10 | Margin | Chief Risk | limit matrix row | |
| 11 | Taxes / fees | Finance | cost model | |
| 12 | Corporate actions | Data Eng | tests | |
| 13 | Data entitlements | Legal / Data Architect | licence register | |
| 14 | Reporting | Compliance | adapter test | |
| 15 | Surveillance | Compliance | pattern tests | |
| 16 | Support hours | Support | SUPPORT_MODEL | |
| 17 | Incident contacts | SRE | INCIDENT_RESPONSE | |
| 18 | Customer disclosures | Legal / GTM | approved copy (no return claims) | |
