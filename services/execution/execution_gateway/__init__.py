"""Execution Gateway [Source: 00, 03; ADR-002, ADR-003].

The only component with a broker route. Accepts authorised order commands from the Control
plane, enforces idempotency (inbox keyed by idempotency_key), holds the executor lease per
account with a monotonic fencing token, and drives monotonic order states.
Protected path: Trading Domain Lead CODEOWNER approval required.
"""

from execution_gateway.gateway import ExecutionGateway, StaleFencingToken
from execution_gateway.lease import Lease, LeaseHeld, LeaseStore

__all__ = ["ExecutionGateway", "StaleFencingToken", "LeaseStore", "Lease", "LeaseHeld"]
