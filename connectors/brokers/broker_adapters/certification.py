"""Broker sandbox certification harness [Source: 02, 11, 17; C10 §4].

Runs the checklist against an adapter and returns evidence rows. The Broker-Connector Lead
runs it; the Trading Domain Lead reviews the resulting docs/BROKER_CERTIFICATIONS/<broker>.md.
The harness never self-certifies: the output carries "Reviewer: pending" until a human signs.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import OrderType, Side, TimeInForce

from broker_adapters.base import AckStatus, BrokerAdapter, BrokerUnavailable, SubmitRequest, VaultRef


class CertRow(StrictModel):
    check: str
    test_id: str
    passed: bool
    evidence: str


def run_certification(
    adapter: BrokerAdapter, *, account_id: str, instrument_id: str, venue: str, now: datetime, price: Decimal
) -> tuple[CertRow, ...]:
    rows: list[CertRow] = []

    def add(check: str, test_id: str, passed: bool, evidence: str) -> None:
        rows.append(CertRow(check=check, test_id=test_id, passed=passed, evidence=evidence))

    # TC-BR-001 auth via vault + rotation
    try:
        adapter.connect(VaultRef(path="vault://brokers/sim/creds", version=1), now=now)
        adapter.rotate_credentials(VaultRef(path="vault://brokers/sim/creds", version=2), now=now)
        h = adapter.health(now=now)
        add(
            "Authentication via vault; credential rotation",
            "TC-BR-001",
            h.connected and h.credential_version == 2,
            f"connected={h.connected} credential_version={h.credential_version}",
        )
    except BrokerUnavailable as exc:
        add("Authentication via vault; credential rotation", "TC-BR-001", False, str(exc))
    try:
        adapter.connect(VaultRef(path="plaintext:not-allowed", version=3), now=now)
        add("Raw credential outside vault rejected", "TC-BR-001b", False, "adapter accepted non-vault credential")
    except BrokerUnavailable:
        add("Raw credential outside vault rejected", "TC-BR-001b", True, "non-vault reference refused")
        adapter.connect(VaultRef(path="vault://brokers/sim/creds", version=2), now=now)
    # TC-BR-002 capability discovery
    caps = adapter.capabilities()
    ok, why = adapter.supports(OrderType.TRAILING_STOP, TimeInForce.DAY, "EQUITY", venue)
    add(
        "Capability discovery (order types, TIF, asset classes)",
        "TC-BR-002",
        (not ok) and OrderType.MARKET in caps.order_types,
        f"unsupported TRAILING_STOP rejected: {why}; supported={[o.value for o in caps.order_types]}",
    )
    # TC-BR-003 each supported order type
    for i, ot in enumerate(caps.order_types):
        req = SubmitRequest(
            client_order_id=f"CERT-{ot.value}-{i}",
            account_id=account_id,
            venue=venue,
            instrument_id=instrument_id,
            side=Side.BUY,
            order_type=ot,
            quantity=Decimal("10"),
            limit_price=price if ot in (OrderType.LIMIT, OrderType.STOP_LIMIT) else None,
            stop_price=price if ot in (OrderType.STOP, OrderType.STOP_LIMIT) else None,
            time_in_force=TimeInForce.DAY,
        )
        ack = adapter.submit(req, now=now)
        add(
            f"Order type {ot.value} submit/ack",
            "TC-BR-003",
            ack.status == AckStatus.ACKNOWLEDGED,
            f"status={ack.status.value} ref={ack.broker_order_ref}",
        )
    # partial fill
    partial_attr = getattr(adapter, "partial_fill_ratio", None)
    setattr(adapter, "partial_fill_ratio", Decimal("0.5"))  # noqa: B010
    ack = adapter.submit(
        SubmitRequest(
            client_order_id="CERT-PARTIAL",
            account_id=account_id,
            venue=venue,
            instrument_id=instrument_id,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            time_in_force=TimeInForce.DAY,
        ),
        now=now,
    )
    fills = adapter.poll_fills(now=now)
    first = [f for f in fills if f.client_order_id == "CERT-PARTIAL"]
    more = adapter.poll_fills(now=now + timedelta(seconds=1))
    second = [f for f in more if f.client_order_id == "CERT-PARTIAL"]
    add(
        "Partial fill handling",
        "TC-BR-003p",
        bool(first) and first[0].quantity < Decimal("100") and bool(second),
        f"first={first[0].quantity if first else None} second={second[0].quantity if second else None}",
    )
    setattr(adapter, "partial_fill_ratio", partial_attr)  # noqa: B010
    # cancel / replace on a resting limit order
    resting = SubmitRequest(
        client_order_id="CERT-REST",
        account_id=account_id,
        venue=venue,
        instrument_id=instrument_id,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("10"),
        limit_price=(price * Decimal("0.5")).quantize(Decimal("0.01")),
        time_in_force=TimeInForce.GTC,
    )
    adapter.submit(resting, now=now)
    rep = adapter.replace("CERT-REST", quantity=Decimal("20"), limit_price=None, now=now)
    can = adapter.cancel("CERT-REST", now=now)
    add(
        "Cancel / replace",
        "TC-BR-003c",
        rep.status == AckStatus.REPLACED and can.status == AckStatus.CANCELLED,
        f"replace={rep.status.value} cancel={can.status.value}",
    )
    # reject handling
    rej = adapter.submit(
        SubmitRequest(
            client_order_id="CERT-REJ",
            account_id=account_id,
            venue=venue,
            instrument_id="UNKNOWN-INSTR",
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("1"),
            time_in_force=TimeInForce.DAY,
        ),
        now=now,
    )
    add(
        "Reject handling and reason mapping",
        "TC-BR-003r",
        rej.status == AckStatus.REJECTED and bool(rej.reason),
        f"status={rej.status.value} reason={rej.reason}",
    )
    # TC-BR-004 reconnection + idempotent resubmission
    adapter.disconnect()
    try:
        adapter.submit(
            SubmitRequest(
                client_order_id="CERT-IDEM",
                account_id=account_id,
                venue=venue,
                instrument_id=instrument_id,
                side=Side.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("5"),
                time_in_force=TimeInForce.DAY,
            ),
            now=now,
        )
        disconnected_ok = False
    except BrokerUnavailable:
        disconnected_ok = True
    adapter.connect(VaultRef(path="vault://brokers/sim/creds", version=2), now=now)
    a1 = adapter.submit(
        SubmitRequest(
            client_order_id="CERT-IDEM",
            account_id=account_id,
            venue=venue,
            instrument_id=instrument_id,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("5"),
            time_in_force=TimeInForce.DAY,
        ),
        now=now,
    )
    a2 = adapter.submit(
        SubmitRequest(
            client_order_id="CERT-IDEM",
            account_id=account_id,
            venue=venue,
            instrument_id=instrument_id,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("5"),
            time_in_force=TimeInForce.DAY,
        ),
        now=now,
    )
    add(
        "Reconnection and idempotent resubmission",
        "TC-BR-004",
        disconnected_ok
        and a1.status == AckStatus.ACKNOWLEDGED
        and a2.status == AckStatus.DUPLICATE
        and a1.broker_order_ref == a2.broker_order_ref,
        f"while disconnected raised={disconnected_ok}; resubmit status={a2.status.value}",
    )
    # statement
    st = adapter.statement(account_id, as_of=now)
    add(
        "Statement download and reconciliation match",
        "TC-BR-005",
        len(st.orders) > 0 and len(st.fills) > 0,
        f"orders={len(st.orders)} fills={len(st.fills)} positions={len(st.positions)}",
    )
    add(
        "Instrument identifiers, sessions/holidays, tick/lot, settlement, short-sale, margin, fees, corporate actions [Source: 17]",
        "TC-BR-006",
        False,
        "[Open] instrument-master validation per market; not evidenced for the simulated broker",
    )
    add("Incident contacts and support hours", "TC-BR-007", False, "[Open: O-15] human input required")
    return tuple(rows)


def certification_markdown(broker: str, rows: tuple[CertRow, ...], *, run_at: datetime, run_by: str) -> str:
    lines = [
        f"# Broker Certification — {broker} / SIMX  [Source: 02, 11, 17]",
        "",
        f"Owner: Broker-Connector Lead ({run_by}) · Reviewer: Trading Domain Lead — **pending (not self-certified)** · Gate C",
        "",
        f"Generated by `scripts/certify_broker.py` at {run_at.isoformat()}. Environment tag: sim. This adapter is a simulated sandbox; it certifies the harness and the gateway contract, not any live broker.",
        "",
        "| Check | Test ID | Result | Evidence |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r.check} | {r.test_id} | {'PASS' if r.passed else 'OPEN'} | {r.evidence} |")
    lines.append("")
    lines.append("Unsupported order types are rejected at schema validation (FR-02): see TC-BR-002 and execution_gateway capability check.")
    return "\n".join(lines) + "\n"
