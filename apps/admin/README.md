# apps/admin — Tenant administration console [Source: 02 FR-01, FR-16; E10/E14]

Not built in the dev/sim environment. Tenant, user, role, broker-connection and PIM administration are served by the identity service APIs (`services/identity`) and, for now, by the operator endpoints of the BFF. The admin console is scheduled under goals/build/E10 and E14 after IdP/MFA integration (MISSING_ACTIONS) and the design system exist. ADR-012 records the console decision.
