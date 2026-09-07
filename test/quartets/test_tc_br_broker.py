"""TC-BR — Broker adapter certification harness [Source: 02, 11; FR-02]."""

from __future__ import annotations

from decimal import Decimal

import pytest
from broker_adapters.base import BrokerUnavailable, VaultRef
from broker_adapters.certification import run_certification
from broker_adapters.simulated import SimulatedBroker


@pytest.fixture
def sandbox(platform):  # type: ignore[no-untyped-def]
    b = SimulatedBroker(known_instruments={"SIMEQ1": "EQUITY"}, venues=("SIMX",))
    b.set_reference_price("SIMEQ1", Decimal("100"), now=platform.now)
    return run_certification(b, account_id="acct-cert", instrument_id="SIMEQ1", venue="SIMX", now=platform.now, price=Decimal("100"))


@pytest.mark.tc("TC-BR-001")
@pytest.mark.req("FR-02")
@pytest.mark.quartet("positive")
def test_vault_auth_and_rotation(sandbox):  # type: ignore[no-untyped-def]
    """Adapter authenticates only via vault reference and rotates credentials; raw credentials are refused."""
    rows = {r.test_id: r for r in sandbox}
    assert rows["TC-BR-001"].passed and rows["TC-BR-001b"].passed


@pytest.mark.tc("TC-BR-002")
@pytest.mark.req("FR-02")
@pytest.mark.quartet("negative")
def test_capability_discovery_rejects_unsupported(sandbox):  # type: ignore[no-untyped-def]
    """Unsupported order type is rejected by capability discovery before submission."""
    assert {r.test_id: r for r in sandbox}["TC-BR-002"].passed


@pytest.mark.tc("TC-BR-003")
@pytest.mark.req("FR-02")
@pytest.mark.quartet("abuse")
def test_order_types_partial_fill_cancel_replace_reject(sandbox):  # type: ignore[no-untyped-def]
    """Each supported order type acks; partial fills; cancel/replace; broker rejects map to reasons."""
    rows = [r for r in sandbox if r.test_id.startswith("TC-BR-003")]
    assert rows and all(r.passed for r in rows), [(r.check, r.evidence) for r in rows if not r.passed]


@pytest.mark.tc("TC-BR-004")
@pytest.mark.req("FR-02")
@pytest.mark.quartet("recovery")
def test_reconnection_and_idempotent_resubmission(sandbox, platform):  # type: ignore[no-untyped-def]
    """Disconnected submissions raise; after reconnect the same client_order_id is deduplicated; statements download."""
    rows = {r.test_id: r for r in sandbox}
    assert rows["TC-BR-004"].passed and rows["TC-BR-005"].passed
    assert not rows["TC-BR-006"].passed and "[Open]" in rows["TC-BR-006"].evidence  # never self-certified
    b = SimulatedBroker(known_instruments={"SIMEQ1": "EQUITY"})
    with pytest.raises(BrokerUnavailable):
        b.connect(VaultRef(path="s3://plain"), now=platform.now)
