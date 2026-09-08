"""Reason-code dictionary [Source: 09; C8 §2]: plain-language explanation and a 'what you can do' line per code.

The Support & Training Lead and Frontend Lead co-own the customer-facing text; localisation [Open: O-14].
Rendered to docs/REASON_CODES.md by scripts/export_reason_codes.py.
"""

from __future__ import annotations

REASON_CODES: dict[str, tuple[str, str, str]] = {
    # code: (family, plain-language explanation, what you can do)
    "RK-AUTH-STATUS": (
        "Authorisation",
        "The account is not active for trading.",
        "Contact your tenant administrator; trading resumes only after the account status is restored.",
    ),
    "RK-AUTH-ACCOUNT": (
        "Authorisation",
        "The intent names an account that does not match the account snapshot.",
        "Resubmit with the correct account.",
    ),
    "RK-AUTH-STRATEGY": (
        "Authorisation",
        "This strategy is not authorised for this account.",
        "Ask the Model Risk Committee to enable the strategy for the account.",
    ),
    "RK-AUTH-MODE": (
        "Authorisation",
        "The account mode does not allow orders (Observe).",
        "Promote the account mode through the gates; Observe mode is analytics only.",
    ),
    "RK-HALT-MODE": ("Halt", "The account is HALTED.", "A two-person restore by different lines of defense is required."),
    "RK-HALT-KS": (
        "Halt",
        "A Kill Switch is active at a level covering this order.",
        "Wait for the two-person deactivation; no new risk is taken while active.",
    ),
    "RK-HALT-INPUT": (
        "Halt",
        "A required input (policy, account or market snapshot) was unavailable; the engine fails closed.",
        "Nothing to change on the order; operations restore the input and the intent can be resubmitted.",
    ),
    "RK-INTEG": (
        "Integrity",
        "The intent changed after validation (hash mismatch); an S1 alert is raised.",
        "Resubmit as a new intent; intents are immutable after validation.",
    ),
    "RK-AUTH-TENANT": (
        "Authorisation",
        "The intent's tenant does not match the account's tenant.",
        "Check the identity scope; cross-tenant submission is never allowed.",
    ),
    "RK-NAV": (
        "Sizing",
        "Net asset value is zero or negative; no exposure ratio can be computed safely.",
        "Nothing to change on the order; operations investigate the account.",
    ),
    "RK-LOSS": (
        "Loss limit",
        "The daily loss limit is already breached; no new risk is taken.",
        "Await the runtime halt review; risk-reducing orders may still be allowed per policy.",
    ),
    "RK-LOSS-UNDEFINED": ("Policy", "No daily loss limit is defined at any level.", "Trading Risk Committee sets it (O-07)."),
    "RK-EXPIRED": ("Validity", "The intent expired before it was decided.", "Resubmit with a later expiry."),
    "RK-LIST-TRADABLE": ("Lists", "The instrument is not tradable in the instrument master.", "Choose a tradable instrument."),
    "RK-SESS": (
        "Session",
        "The market session is not open.",
        "Submit during the venue session; limit orders in pre-open only where policy allows.",
    ),
    "RK-SESS-VENUE": ("Session", "The venue is reported unhealthy.", "Wait for venue health to recover; cancel-only applies meanwhile."),
    "RK-FRESH": ("Data", "Market data is older than the freshness budget.", "Nothing to change on the order; the feed must recover first."),
    "RK-FRESH-CLOCK": (
        "Data",
        "Ingest timestamp precedes the market timestamp (clock anomaly).",
        "Data engineering investigates clock synchronisation.",
    ),
    "RK-FRESH-QUALITY": ("Data", "The snapshot is flagged as suspect, stale or missing.", "Wait for a clean snapshot."),
    "RK-FRESH-PROV": ("Data", "The snapshot provenance is not a licensed (or simulated) feed.", "Only licensed feeds may drive decisions."),
    "RK-FRESH-INTENT": ("Data", "The intent's market timestamp is in the future.", "Check the strategy clock."),
    "RK-FRESH-UNDEFINED": ("Policy", "No freshness budget is defined for this asset class.", "Trading Risk Committee sets it (O-07)."),
    "RK-FX-MISSING": (
        "Data",
        "No exchange rate is available for a currency this account holds, so its value cannot be stated.",
        "Nothing to change on the order; the FX source must deliver a rate for the pair before trading resumes.",
    ),
    "RK-FX-STALE": (
        "Data",
        "The exchange rates are older than the freshness budget (or dated in the future), so the account value is not current.",
        "Nothing to change on the order; the FX source must publish a current snapshot.",
    ),
    "RK-FX-UNDEFINED": (
        "Policy",
        "No FX freshness budget is defined, and an undefined budget is never treated as unlimited.",
        "Trading Risk Committee sets the budget per pair and asset class (O-07).",
    ),
    "RK-INSTR-ID": ("Instrument", "Instrument in the intent does not match the snapshot.", "Resubmit with matching instrument."),
    "RK-INSTR-VENUE": ("Instrument", "Venue in the intent does not match the instrument's venue.", "Resubmit with the instrument's venue."),
    "RK-INSTR-PIT": (
        "Instrument",
        "The instrument was not valid (listed) at the intent's market time.",
        "Check the point-in-time universe.",
    ),
    "RK-INSTR-LOT": ("Instrument", "Quantity is not a multiple of the lot size.", "Round the quantity to the lot size."),
    "RK-INSTR-TICK": ("Instrument", "Price is not a multiple of the tick size.", "Round the price to the tick size."),
    "RK-INSTR-SHORT": ("Instrument", "The instrument is not shortable.", "Short selling is unavailable for this instrument."),
    "RK-BP": ("Sizing", "Insufficient buying power.", "Reduce the order size."),
    "RK-CAP": (
        "Sizing",
        "Order notional exceeds the effective per-order cap (minimum across platform, tenant, account, strategy, instrument).",
        "Reduce the order size or request a limit change via maker-checker.",
    ),
    "RK-CAP-POS": ("Sizing", "Resulting position would exceed the per-instrument cap.", "Reduce the order size."),
    "RK-CAP-AGG": (
        "Sizing",
        "Open same-side orders plus this order exceed the cap (order splitting is aggregated).",
        "Cancel open orders or reduce size.",
    ),
    "RK-CAP-UNDEFINED": ("Policy", "No cap is defined at any level.", "Trading Risk Committee sets it (O-07)."),
    "RK-EXP": ("Exposure", "Gross exposure would exceed the limit.", "Reduce exposure."),
    "RK-EXP-NET": ("Exposure", "Net exposure would exceed the limit.", "Reduce directional exposure."),
    "RK-CONC": ("Concentration", "Single-name concentration would exceed the limit.", "Diversify or reduce."),
    "RK-CONC-SECTOR": ("Concentration", "Sector concentration would exceed the limit.", "Diversify across sectors."),
    "RK-CONC-COUNTRY": ("Concentration", "Country concentration would exceed the limit.", "Diversify across countries."),
    "RK-CONC-CCY": ("Concentration", "Currency concentration would exceed the limit.", "Diversify across currencies."),
    "RK-LEV": ("Leverage", "Leverage would exceed the limit.", "Reduce gross exposure."),
    "RK-COLLAR": (
        "Price",
        "Limit or stop price is outside the collar around the reference price (fat-finger protection).",
        "Check the price.",
    ),
    "RK-DUP": ("Duplicate", "An identical intent was already processed.", "No action; the earlier intent stands."),
    "RK-RATE": ("Rate", "Orders per minute would exceed the limit.", "Slow down."),
    "RK-RATE-OPEN": ("Rate", "Open-order count would exceed the limit.", "Cancel or wait for fills."),
    "RK-LIQ": ("Liquidity", "Order is too large relative to average daily volume.", "Reduce size or work the order."),
    "RK-LIQ-APPROVAL": ("Liquidity", "Order is large relative to average daily volume; a human must approve.", "Await approval."),
    "RK-VOL-APPROVAL": ("Volatility", "Realised volatility is above the regime threshold; a human must approve.", "Await approval."),
    "RK-PROT": (
        "Protective",
        "A protective stop is required by policy and is missing or on the wrong side.",
        "Add a protective stop below entry (long) or above entry (short).",
    ),
    "RK-PROT-APPROVAL": ("Protective", "Protective stop missing; a human must approve.", "Await approval or add a stop."),
    "RK-CORR": ("Correlated risk", "Exposure to a correlated group would exceed the limit.", "Reduce exposure in the group."),
    "RK-MODE-SUPERVISED": ("Mode", "The account is in Supervised mode: every order needs human approval.", "Await approval in the queue."),
    "RK-ENVELOPE": (
        "Autonomy",
        "The order would exceed the capital envelope for bounded autonomy.",
        "Await human approval or reduce size.",
    ),
    "RK-AUTONOMY-SUSPENDED": (
        "Autonomy",
        "Autonomy is suspended (SLO safety semantics or break); orders need approval.",
        "Await approval; an operator restores autonomy.",
    ),
    "CP-HALT-INPUT": ("Eligibility", "An eligibility input was unavailable; the engine fails closed.", "Operations restore the input."),
    "CP-INTEG": ("Eligibility", "Intent hash mismatch.", "Resubmit as a new intent."),
    "CP-TENANT": ("Eligibility", "Customer and intent belong to different tenants.", "Check account configuration."),
    "CP-JURIS-NOCELL": (
        "Jurisdiction",
        "No compliance-matrix row exists for this country, customer type, broker, venue, asset class and mode.",
        "Market enablement (P5) has not happened; nothing to change on the order.",
    ),
    "CP-JURIS-LEGAL": ("Jurisdiction", "No signed legal record for this cell.", "Legal record required (dual key)."),
    "CP-JURIS-FLAG": ("Jurisdiction", "Technical flag not activated for this cell.", "Second-person flag activation required (dual key)."),
    "CP-JURIS-DUALKEY": (
        "Jurisdiction",
        "Legal signer and flag activator must be different persons.",
        "Compliance corrects the activation.",
    ),
    "CP-PERM": ("Permissions", "The customer is not permitted to trade this asset class.", "Product permissions are set at onboarding."),
    "CP-APPR": ("Suitability", "Complex product requires an appropriateness assessment.", "Complete the assessment."),
    "CP-DISCL": (
        "Disclosures",
        "The current disclosure pack for this market has not been acknowledged (none, an older version, or a future-dated record).",
        "Review and acknowledge the current disclosures through onboarding; nothing to change on the order.",
    ),
    "CP-MODE-CONSENT": (
        "Consent",
        "No recorded consent exists for operating this account in the requested mode.",
        "Consent for the mode is recorded through onboarding; orders in that mode are unavailable until then.",
    ),
    "CP-CLASS": (
        "Classification",
        "The customer classification has no assessor evidence, was self-declared, or is dated in the future.",
        "Classification is established and recorded by an assessor; it cannot be self-declared.",
    ),
    "CP-SHORT": ("Permissions", "Short selling not permitted for this customer.", "Not available."),
    "CP-SHORT-BAN": ("Lists", "Short-sale ban applies to this instrument.", "Not available while the ban applies."),
    "CP-LIST-INSTR": ("Lists", "Instrument is on the restricted list.", "Not available."),
    "CP-LIST-ISSUER": ("Lists", "Issuer is on the restricted list.", "Not available."),
    "CP-LIST-VENUE": ("Lists", "Venue is on the restricted list.", "Not available."),
    "CP-LIST-WHITELIST": ("Lists", "Instrument is not on the whitelist in force.", "Not available."),
    "CP-SCOPE-MARKET-MAKING": (
        "Scope",
        "Strategy declares two-sided resting quotes (market making is out of scope).",
        "Not registrable without separate approval [Source: 01].",
    ),
    "CP-SCOPE-COPY-TRADING": ("Scope", "Strategy replicates other accounts (copy trading is out of scope).", "Not registrable."),
    "CP-SCOPE-ADVICE": ("Scope", "Strategy provides personalised advice (out of scope).", "Not registrable."),
    "CP-SURV-CANCEL-RATIO": ("Surveillance", "Expected cancel ratio could produce layering/spoofing patterns.", "Redesign the strategy."),
    "CP-SURV-CLOSE": ("Surveillance", "Strategy trades in the closing window (marking-the-close risk).", "Redesign the strategy."),
    "RT-LOSS-DAILY": ("Runtime halt", "Daily loss limit reached.", "Kill Switch applied; two-person restore after review."),
    "RT-LOSS-WEEKLY": ("Runtime halt", "Weekly loss limit reached.", "Kill Switch applied; two-person restore after review."),
    "RT-LOSS-MONTHLY": ("Runtime halt", "Monthly loss limit reached.", "Kill Switch applied; two-person restore after review."),
    "RT-NAV": ("Runtime halt", "Net asset value is zero or negative.", "Kill Switch applied; operations investigate."),
    "RT-LOSS-DAILY-UNDEFINED": (
        "Runtime halt",
        "No daily loss limit defined: the monitor fails closed.",
        "Trading Risk Committee sets it (O-07).",
    ),
    "RT-LOSS-WEEKLY-UNDEFINED": (
        "Runtime halt",
        "No weekly loss limit defined: the monitor fails closed.",
        "Trading Risk Committee sets it (O-07).",
    ),
    "RT-LOSS-MONTHLY-UNDEFINED": (
        "Runtime halt",
        "No monthly loss limit defined: the monitor fails closed.",
        "Trading Risk Committee sets it (O-07).",
    ),
    "RT-DRAWDOWN-UNDEFINED": (
        "Runtime halt",
        "No drawdown limit defined: the monitor fails closed.",
        "Trading Risk Committee sets it (O-07).",
    ),
    "RT-DRAWDOWN": ("Runtime halt", "Peak-to-trough drawdown limit reached.", "Kill Switch applied; two-person restore after review."),
    "RT-FREQ": ("Runtime halt", "Abnormal order frequency.", "Kill Switch applied; investigate the strategy."),
    "RT-SLIPPAGE": ("Runtime halt", "Slippage above threshold.", "Cancel-only review."),
    "RT-REJECTS": ("Runtime halt", "Broker rejection rate above threshold.", "Cancel-only review."),
    "RT-LATENCY": ("Runtime halt", "Risk-decision latency above threshold.", "Autonomy suspended until restored."),
    "RT-CONNECTIVITY": ("Runtime halt", "Broker connectivity lost.", "Cancel-only; reconcile on reconnect."),
    "RT-DRIFT": ("Runtime halt", "Model drift threshold breached.", "Signals suspended; Model Risk review."),
    "RT-RECON": ("Runtime halt", "Open reconciliation break.", "Account in Supervised until resolved with two-person confirmation."),
    "RT-VENUE": ("Runtime halt", "Venue health failed.", "Cancel-only until venue recovers."),
    # Integrity of the durable control store against the audit chain that witnesses its journal head
    # (O-128, D-061 (5); ADR-018 amendment 1). These are operator-facing, not customer-facing: they are raised
    # before any order exists, and the platform refuses to start rather than trade on a store it cannot trust.
    "STORE-JOURNAL-ROLLBACK": (
        "Integrity",
        "The control store's journal is behind the head recorded in the audit trail: the store was rolled back or replaced.",
        "Nothing to change on any order; the platform will not start. Operations restore the store from a backup that matches the "
        "recorded head, and the incident is investigated before trading resumes.",
    ),
    "STORE-JOURNAL-FORK": (
        "Integrity",
        "The control store's history was rewritten: its journal digest disagrees with the one the audit trail recorded.",
        "Nothing to change on any order; the platform will not start. Operations treat this as a suspected tampering incident and "
        "restore from a backup that matches the recorded head.",
    ),
    "STORE-JOURNAL-UNWITNESSED": (
        "Integrity",
        "The audit trail holds no record of this control store's history, so its contents cannot be trusted.",
        "Nothing to change on any order; the platform will not start. Operations restore the audit trail and the store together, "
        "from the same point in time.",
    ),
    "STORE-JOURNAL-STALE": (
        "Integrity",
        "The control store has moved further ahead of the audit trail than the configured ceiling allows.",
        "Nothing to change on any order. Operations restore the audit trail's availability; the ceiling itself is a configured "
        "value and is not changed to clear the condition.",
    ),
    "STORE-JOURNAL-WITNESS-UNTRUSTED": (
        "Integrity",
        "The audit trail that witnesses the control store does not itself verify against its external anchor.",
        "Nothing to change on any order. Operations restore the external anchor or the audit trail; the check is never disabled "
        "to make the platform start.",
    ),
}


def explain(code: str) -> dict[str, str]:
    family, text, action = REASON_CODES.get(
        code, ("Unknown", "No dictionary entry for this code (defect: every code must be documented).", "Contact support.")
    )
    return {"code": code, "family": family, "explanation": text, "what_you_can_do": action}
