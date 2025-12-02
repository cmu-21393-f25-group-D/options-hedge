"""Simulation harness.

Defines `run_simulation` to iterate over market data and apply strategies,
recording portfolio value through time.
"""

from datetime import datetime
from typing import Any, Callable, Dict, Protocol

import pandas as pd

from .portfolio import Portfolio


class MarketLike(Protocol):  # pragma: no cover - structural typing aid
    data: pd.DataFrame


StrategyFunction = Callable[
    [Portfolio, float, datetime, Dict[str, Any], MarketLike], None
]
"""Strategy function signature: (portfolio, price, date, params, market) -> None.

All strategies must accept these 5 parameters in this order, even if they
don't use all of them (e.g., quarterly strategy ignores market parameter).
"""


def run_simulation(
    market: MarketLike,
    portfolio: Portfolio,
    strategy_fn: StrategyFunction,
    params: Dict[str, Any],
) -> pd.DataFrame:
    """Run daily simulation using provided market and strategy.

    Args:
        market: Object with 'data' DataFrame with 'Close' and 'Returns'
        portfolio: Portfolio to track through simulation
        strategy_fn: Strategy function with 5-parameter signature
        params: Strategy-specific parameters

    Returns:
        DataFrame with portfolio history (Date, Value columns)
    """
    for date, row in market.data.iterrows():
        # Extract scalar values from potentially Series objects
        close_val = row["Close"]
        price = (
            float(close_val.iloc[0]) if hasattr(close_val, "iloc") else float(close_val)
        )

        returns_val = row["Returns"]
        daily_return = (
            float(returns_val.iloc[0])
            if hasattr(returns_val, "iloc")
            else float(returns_val)
        )

        portfolio.update_equity(daily_return)

        ts_date = pd.Timestamp(str(date))
        strategy_fn(
            portfolio,
            price,
            ts_date.to_pydatetime(),
            params,
            market,
        )

        # Exercise expired options to realize payoffs
        portfolio.exercise_expired_options(price, ts_date)

        total = portfolio.total_value(price, ts_date)
        portfolio.record(ts_date.to_pydatetime(), total)

    return pd.DataFrame(portfolio.history)
