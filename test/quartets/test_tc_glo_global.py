"""TC-GLO-001..004 — Global compatibility [Committee; D-050; NFR-GLO-01]: any country on any continent can be modelled
(jurisdiction cell, currency, venue calendar in its own timezone) while legal enablement stays per cell by dual key."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

import pytest
from conftest import COMPLIANCE, LEGAL, VENUE
from market_data.calendar import SessionCalendar
from rtcore.errors import ControlDenied, SchemaViolation
from rtcore.schemas.compliance import CustomerType
from rtcore.schemas.market import SessionState
from rtcore.world import CONTINENTS, COUNTRIES, countries_by_continent, is_user_assigned, is_valid_country
from web_bff.platform import BROKER, build_sim_platform


@pytest.mark.tc("TC-GLO-001")
@pytest.mark.req("NFR-GLO-01")
@pytest.mark.quartet("positive")
def test_every_country_on_every_continent_is_a_valid_cell_with_a_currency():  # type: ignore[no-untyped-def]
    """The world registry covers every ISO 3166-1 country/territory on all seven continents with an ISO 4217 currency; each can be proposed as a jurisdiction cell (proposed, never enabled)."""
    assert len(COUNTRIES) >= 249 and set(c.continent for c in COUNTRIES.values()) == set(CONTINENTS)
    assert all(len(countries_by_continent(c)) > 0 for c in CONTINENTS)
    assert all(len(c.alpha2) == 2 and len(c.alpha3) == 3 and len(c.currency) == 3 and c.currency.isupper() for c in COUNTRIES.values())
    spot = {
        "FR": "EUR",
        "JP": "JPY",
        "BR": "BRL",
        "ZA": "ZAR",
        "AU": "AUD",
        "US": "USD",
        "IN": "INR",
        "CN": "CNY",
        "EG": "EGP",
        "SA": "SAR",
        "MX": "MXN",
        "GB": "GBP",
        "KE": "KES",
        "NG": "NGN",
        "AR": "ARS",
        "KR": "KRW",
        "ID": "IDR",
        "TR": "TRY",
        "AQ": "XXX",
        "NZ": "NZD",
    }
    assert {k: COUNTRIES[k].currency for k in spot} == spot
    p = build_sim_platform(enable_cell=False)
    proposed = 0
    for code in COUNTRIES:
        cell = p.jurisdictions.propose(
            country=code, customer_type=CustomerType.PROFESSIONAL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="PAPER"
        )
        assert not cell.simulated and not p.jurisdictions.is_live(cell)
        proposed += 1
    assert proposed == len(COUNTRIES) and all(not p.jurisdictions.is_live(c) for c in p.jurisdictions.cells())


@pytest.mark.tc("TC-GLO-002")
@pytest.mark.req("NFR-GLO-01")
@pytest.mark.quartet("negative")
def test_unknown_country_codes_are_refused_and_simulated_codes_are_labelled():  # type: ignore[no-untyped-def]
    """A cell for a code that is neither ISO 3166-1 nor user-assigned is refused; user-assigned codes (ZZ) are accepted only as simulated and say so."""
    p = build_sim_platform(enable_cell=False)
    for bad in ("XX1", "usa", "", "US-CA", "EU", "UK"):
        with pytest.raises((ControlDenied, SchemaViolation, ValueError)):
            p.jurisdictions.propose(
                country=bad, customer_type=CustomerType.RETAIL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="PAPER"
            )
    assert is_user_assigned("ZZ") and is_user_assigned("XA") and not is_valid_country("ZZ")
    sim = p.jurisdictions.cells()[0]
    assert sim.country == "ZZ" and sim.simulated


@pytest.mark.tc("TC-GLO-003")
@pytest.mark.req("NFR-GLO-01")
@pytest.mark.quartet("abuse")
def test_world_coverage_never_means_legal_availability():  # type: ignore[no-untyped-def]
    """Proposing every country enables nothing: no legal record, no flag, eligibility stays INELIGIBLE; a simulated cell can be exercised in sim but its legal record is labelled simulated in the audit."""
    p = build_sim_platform(enable_cell=False)
    cells = [
        p.jurisdictions.propose(
            country=c, customer_type=CustomerType.RETAIL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="PAPER"
        )
        for c in ("US", "FR", "JP", "NG", "BR", "AU")
    ]
    assert not any(p.jurisdictions.is_live(c) for c in cells)
    assert all(c.legal_record_ref is None and not c.technical_flag for c in cells)
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(cells[0], actor=COMPLIANCE, now=p.now)  # no legal record
    zz = next(c for c in p.jurisdictions.cells() if c.country == "ZZ")
    zz = p.jurisdictions.record_legal(zz, legal_record_ref="SIM-ONLY", actor=LEGAL)
    ev = p.audit.by_action("jurisdiction.legal.recorded")[-1]
    assert ev.payload.get("simulated") is True


@pytest.mark.tc("TC-GLO-004")
@pytest.mark.req("NFR-GLO-01")
@pytest.mark.quartet("recovery")
def test_venue_calendars_work_in_any_timezone_including_day_boundaries():  # type: ignore[no-untyped-def]
    """Venue sessions declared in local time (Tokyo, São Paulo, Sydney) evaluate correctly across the UTC day boundary and honour local-date holidays; UTC-declared venues keep working."""
    cal = SessionCalendar()
    cal.add_venue_local("TSE", time(9, 0), time(15, 0), "Asia/Tokyo", holidays={date(2026, 9, 21)})
    cal.add_venue_local("B3", time(10, 0), time(17, 0), "America/Sao_Paulo")
    cal.add_venue_local("ASX", time(10, 0), time(16, 0), "Australia/Sydney")
    cal.add_venue(VENUE, time(0, 0), time(23, 59, 59))
    assert cal.state("TSE", datetime(2026, 9, 7, 1, 0, tzinfo=UTC)) == SessionState.OPEN  # 10:00 Tokyo, Monday
    assert cal.state("TSE", datetime(2026, 9, 6, 23, 30, tzinfo=UTC)) == SessionState.PRE_OPEN  # 08:30 Tokyo Monday, still Sunday in UTC
    assert cal.state("TSE", datetime(2026, 9, 21, 1, 0, tzinfo=UTC)) == SessionState.CLOSED  # local holiday
    assert cal.state("B3", datetime(2026, 9, 7, 19, 30, tzinfo=UTC)) == SessionState.OPEN  # 16:30 São Paulo
    assert cal.state("B3", datetime(2026, 9, 7, 12, 0, tzinfo=UTC)) == SessionState.PRE_OPEN  # 09:00 São Paulo
    assert cal.state("ASX", datetime(2026, 9, 11, 5, 30, tzinfo=UTC)) == SessionState.OPEN  # 15:30 Sydney Friday
    assert cal.state("ASX", datetime(2026, 9, 12, 1, 0, tzinfo=UTC)) == SessionState.CLOSED  # Saturday in Sydney
    assert cal.state(VENUE, datetime(2026, 9, 7, 14, 0, tzinfo=UTC)) == SessionState.OPEN
    close = cal.close_time("TSE", datetime(2026, 9, 7, 1, 0, tzinfo=UTC))
    assert close is not None and close.astimezone(UTC).hour == 6  # 15:00 Tokyo = 06:00 UTC
