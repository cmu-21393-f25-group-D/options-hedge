"""Unit tests for the simulation harness."""

from datetime import datetime
from typing import Any, Dict

import pandas as pd

from options_hedge.portfolio import Portfolio
from options_hedge.simulation import MarketLike, run_simulation


class FakeMarket:
    def __init__(self) -> None:
        idx = pd.date_range("2025-01-01", periods=5, freq="D")
        self.data = pd.DataFrame(
            {
                "Close": [100, 101, 99, 100, 102],
                "Returns": [0.0, 0.01, -0.0198, 0.0101, 0.0199],
            },
            index=idx,
        )

    def get_vix(self, date: pd.Timestamp) -> float:
        """Mock VIX getter."""
        return 20.0


def dummy_strategy(
    portfolio: Portfolio,
    price: float,
    date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
) -> None:
    # No-op strategy, just a placeholder
    pass


def test_run_simulation_records_history() -> None:
    mkt = FakeMarket()
    p = Portfolio(initial_value=1000.0, beta=1.0)
    params: Dict[str, Any] = {}
    hist = run_simulation(mkt, p, dummy_strategy, params)
    assert len(hist) == len(mkt.data)
    assert {"Date", "Value"}.issubset(set(hist.columns))
