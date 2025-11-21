from datetime import datetime
from typing import Any, Dict, Sequence

import pandas as pd

from options_hedge.lp_strategies import lp_floor_hedge_strategy
from options_hedge.options_instruments import Option
from options_hedge.portfolio import Portfolio
from options_hedge.simulation import run_simulation
from options_hedge.strategies import (
    conditional_hedging_strategy,
    quarterly_protective_put_strategy,
)


class DummyMarket:
    """Minimal market stub for tests (no external download)."""

    data: pd.DataFrame

    def __init__(self, prices: Sequence[float]):
        df = pd.DataFrame({"Close": prices})
        returns_col = df["Close"].pct_change().fillna(0.0)
        df["Returns"] = returns_col
        start = datetime(2024, 1, 1)
        df.index = pd.date_range(start=start, periods=len(df), freq="D")
        self.data = df


def test_option_payoff_and_value() -> None:
    expiry = datetime(2025, 1, 1)
    opt = Option(strike=100.0, premium=5.0, expiry=expiry, quantity=2)
    assert opt.payoff(90.0) == (100.0 - 90.0) * 2
    assert opt.payoff(120.0) == 0.0
    # intrinsic value before expiry
    assert opt.value(95.0, datetime(2024, 6, 1)) == (100.0 - 95.0) * 2
    # expired -> zero value
    assert opt.value(95.0, datetime(2025, 1, 2)) == 0.0


def test_portfolio_buy_put_and_total_value() -> None:
    p = Portfolio(initial_value=1000.0, beta=1.0)
    p.buy_put(
        strike=100.0,
        premium=10.0,
        expiry=datetime(2024, 6, 1),
        quantity=1,
    )
    # cash reduced
    assert p.cash == -10.0
    # total value includes equity + cash + option intrinsic
    val = p.total_value(current_price=90.0, current_date=datetime(2024, 1, 10))
    assert val > p.equity_value - 10.0  # includes intrinsic value


def test_quarterly_strategy_interval() -> None:
    prices = [100, 101, 102] + [103] * 200  # sufficient length
    market = DummyMarket(prices)  # conforms to MarketLike
    p = Portfolio(initial_value=1000.0)
    params: Dict[str, Any] = {
        "hedge_interval": 30,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 60,
    }
    # Run limited simulation (first 61 days)
    for date_raw, row in market.data.iloc[:61].iterrows():
        date: datetime = date_raw.to_pydatetime()  # type: ignore[attr-defined]
        price = float(row["Close"])  # type: ignore[arg-type]
        ret = float(row["Returns"])  # type: ignore[arg-type]
        p.update_equity(ret)
        quarterly_protective_put_strategy(
            p,
            price,
            date,
            params,  # type: ignore[arg-type]
        )
    # Expect at least 2 option purchases (day 0 and ~day 30)
    assert len(p.options) >= 2


def test_conditional_strategy_triggers_on_drop() -> None:
    # create prices with a 10% drop over lookback window
    prices = [100.0] * 10 + [90.0] * 15 + [89.0] * 10
    market = DummyMarket(prices)
    p = Portfolio(initial_value=1000.0)
    params: Dict[str, Any] = {
        "lookback_days": 10,
        "drop_threshold": -0.05,
        "vol_multiplier": 2.0,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 30,
    }
    # Run through all days
    for date_raw, row in market.data.iterrows():
        date: datetime = date_raw.to_pydatetime()  # type: ignore[attr-defined]
        price = float(row["Close"])  # type: ignore[arg-type]
        ret = float(row["Returns"])  # type: ignore[arg-type]
        p.update_equity(ret)
        conditional_hedging_strategy(
            p,
            price,
            date,
            params,
            market,  # type: ignore[arg-type]
        )
    # Expect at least one put purchased after drop manifests
    assert any(opt.strike < 100.0 for opt in p.options)


def test_lp_floor_hedge_strategy_buys_minimum() -> None:
    p = Portfolio(initial_value=1000.0)
    # Use a scenario where a 20% drop breaches desired floor (85%)
    params: Dict[str, Any] = {
        "floor_ratio": 0.90,  # want 90% of current equity protected
        "downside_scenario": -0.20,  # 20% drop
        "put_cost": 0.01,
        "strike_ratio": 0.95,
        "expiry_days": 60,
    }
    current_price = 100.0
    lp_floor_hedge_strategy(p, current_price, datetime(2024, 1, 1), params)
    assert len(p.options) >= 1


def test_run_simulation_structure() -> None:
    prices = [100, 101, 102, 103, 104]
    market = DummyMarket(prices)
    p = Portfolio(initial_value=1000.0)
    params: Dict[str, Any] = {
        "hedge_interval": 2,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 10,
    }
    df = run_simulation(market, p, quarterly_protective_put_strategy, params)
    assert len(df) == len(market.data)
    assert {"Date", "Value"}.issubset(df.columns)
