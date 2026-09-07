"""Identity, tenant, account mode and privileged-action primitives [Source: 02 FR-01; C1; E01].

Out-of-scope capabilities (custody, deposits/withdrawals, market making, copy trading, advice)
have no permission flag here, so no configuration path can enable them [Committee C1 §3].
"""

from identity_service.accounts import Account, AccountRegistry, GateRecord, Tenant
from identity_service.makerchecker import MakerChecker, PendingChange
from identity_service.rbac import Permission, User, authorize, permissions_for

__all__ = [
    "Account",
    "AccountRegistry",
    "GateRecord",
    "Tenant",
    "MakerChecker",
    "PendingChange",
    "Permission",
    "User",
    "authorize",
    "permissions_for",
]
