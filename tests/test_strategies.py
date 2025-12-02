"""Unit tests for hedging strategies."""

from datetime import datetime, timedelta

import pandas as pd

from options_hedge.portfolio import Portfolio
from options_hedge.strategies import (
    conditional_hedging_strategy,
    quarterly_protective_put_strategy,
)


class FakeMarket:
    def __init__(self, dates: pd.DatetimeIndex) -> None:
        self.data = pd.DataFrame(
            {
                "Close": pd.Series(100.0, index=dates),
                "Returns": pd.Series(0.0, index=dates),
            }
        )

    def get_vix(self, date: pd.Timestamp) -> float:
        """Mock VIX getter."""
        return 20.0


def test_quarterly_strategy_buys_puts_on_schedule() -> None:
    p = Portfolio(initial_value=1000.0, beta=1.0)
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    mkt = FakeMarket(dates)
    params = {
        "hedge_interval": 90,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 90,
    }
    today = datetime(2025, 1, 1)
    quarterly_protective_put_strategy(p, 100.0, today, params, mkt)
    assert len(p.options) == 1
    # next call within interval should not buy
    next_day = today + timedelta(days=1)
    quarterly_protective_put_strategy(p, 100.0, next_day, params, mkt)
    assert len(p.options) == 1
    # after interval, should buy again
    after_interval = today + timedelta(days=91)
    quarterly_protective_put_strategy(p, 100.0, after_interval, params, mkt)
    assert len(p.options) == 2


def test_conditional_strategy_triggers_on_drop_or_vol_spike() -> None:
    p = Portfolio(initial_value=1000.0, beta=1.0)
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    mkt = FakeMarket(dates)
    # craft recent drop
    mkt.data.loc[dates[-1], "Close"] = 90.0
    params = {
        "lookback_days": 20,
        "drop_threshold": -0.05,
        "vol_multiplier": 1.5,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 90,
    }
    conditional_hedging_strategy(
        p,
        90.0,
        dates[-1].to_pydatetime(),
        params,
        mkt,
    )
    assert len(p.options) == 1
