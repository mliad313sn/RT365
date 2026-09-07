"""Data-provider adapters [Source: 08]. No licence or entitlement is assumed [Open: O-12]."""

from data_providers.base import DataProvider, RawBar
from data_providers.simulated import SimulatedFeed

__all__ = ["DataProvider", "RawBar", "SimulatedFeed"]
