"""Broker adapter framework [Source: 02; E03]. Credentials live in the vault; adapters hold a VaultRef only."""

from broker_adapters.base import (
    BrokerAck,
    BrokerAdapter,
    BrokerFill,
    BrokerHealth,
    BrokerStatement,
    BrokerUnavailable,
    Capabilities,
    StatementOrder,
    StatementPosition,
    SubmitRequest,
    VaultRef,
)
from broker_adapters.simulated import SimulatedBroker

__all__ = [
    "BrokerAdapter",
    "BrokerAck",
    "BrokerFill",
    "BrokerHealth",
    "BrokerStatement",
    "BrokerUnavailable",
    "Capabilities",
    "StatementOrder",
    "StatementPosition",
    "SubmitRequest",
    "VaultRef",
    "SimulatedBroker",
]
