"""Backtest engine [Source: 08; ADR-008]: the production eligibility, risk and execution code against a simulated broker.

Metrics inform decisions; they do not prove future profitability [Source: 08].
"""

from backtest_engine.costs import CostModel
from backtest_engine.metrics import BacktestMetrics, compute_metrics
from backtest_engine.runner import DISCLAIMER, BacktestReport, BacktestRunner

__all__ = ["CostModel", "BacktestMetrics", "compute_metrics", "BacktestRunner", "BacktestReport", "DISCLAIMER"]
