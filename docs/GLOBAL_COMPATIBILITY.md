# GLOBAL_COMPATIBILITY — capable in every country on every continent, enabled per cell

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner (Backend Lead, Data Engineering Lead build; Compliance Agent reviews) | Compliance Agent | Product Owner (D-050) | B | v1.0 — 2026-09-08 |

**Owner requirement (2026-09-08):** the apps must be compatible with all countries on all continents. **Reading under blueprint 00/07 [Source]:** *compatible* means the software can model, price, schedule, store and display any jurisdiction, currency, venue and language; *enabled* remains a per-cell human act (legal record by a Legal Agent + technical flag by a Compliance role, different persons). "Worldwide never means legal availability" (COMPLIANCE_MATRIX.md). This document states, per dimension, what is built, what is a build item and what stays a human act.

| Dimension | Requirement | Built (dev/sim, evidenced) | Build item (register) | Human act |
|---|---|---|---|---|
| Jurisdictions | any ISO 3166-1 country/territory (250 rows, 7 continents) is a proposable cell; user-assigned codes are simulated cells; anything else refused | `rtcore.world` registry; `JurisdictionRegistry.propose` validation; `JurisdictionCell.simulated`; TC-GLO-001..003 | F-1 registry verified against the ISO 3166/4217 registers; F-2 subdivision codes (states, provinces) for federal regimes | legal record per cell (H-04, H-12); flag by a second person (H-17) |
| Currencies | every position, limit and NAV in any ISO 4217 currency; accounts in any base currency | instrument and account carry currency; concentration-by-currency control (RK-CONC-CCY) | F-3 FX rate as a decision input (fail closed when missing/stale), cross-currency NAV and limits, multi-currency cash ledger | data licence for FX (H-08) |
| Calendars and time | venue sessions and holidays in the venue's own timezone; all timestamps UTC-aware | `SessionCalendar.add_venue_local` (IANA zones), TC-GLO-004; UTC everywhere in schemas | F-4 holiday calendars per venue from a licensed source; DST-aware freshness budgets per venue | — |
| Instruments and venues | any venue and asset class per certified broker; instrument master with country, currency, tick and lot sizes | instrument master fields; per-broker capability discovery | F-5 venue registry (MIC codes), tick tables and settlement conventions per market | broker certification per venue (H-07) |
| Language and formats | operators and customers in their language; numbers, dates and money in local formats; RTL scripts | English UI; reason-code dictionary | F-6 locale packs for the dashboard and reason dictionary (launch locales O-14), CLDR number/date formatting, RTL layout, accessibility per script | approved disclosures per language (H-16) |
| Data residency and privacy | tenant data stored in the tenant's region; retention per jurisdiction; legal hold | tenant `residency_region`; retention fails closed without a schedule | F-7 regional cells and residency enforcement at storage; retention schedules per jurisdiction (O-09, O-10) | DPIA per jurisdiction (O-10) |
| Sanctions and restricted lists | restricted instruments, venues and counterparties per jurisdiction | restricted lists in eligibility (CP-RESTRICTED) | F-8 sanctions-list feeds and screening per cell | licence for the lists (H-08) |
| Tax and reporting | trade and tax reporting per jurisdiction | audit chain and export | F-9 reporting adapters per regime (E11), tax lots and withholding | counsel per cell (Q-J12) |
| Operations | support hours, incident contacts and on-call per market and timezone | alert router; incident response plan | F-10 follow-the-sun on-call model and support hours per market (O-15) | staffing (H-11) |

Rule of thumb for every agent: the registry answers *what* a country uses; only the dual key answers *whether* we may trade there.
