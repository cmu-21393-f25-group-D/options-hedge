from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, Protocol

import pandas as pd

from .portfolio import Portfolio


class MarketLike(Protocol):  # pragma: no cover - structural typing aid
    data: pd.DataFrame


def run_simulation(
    market: MarketLike,
    portfolio: Portfolio,
    strategy_fn: Callable[..., Any],
    params: Dict[str, Any],
) -> pd.DataFrame:
    """Run daily simulation using provided market and strategy.

    Accepts any object exposing a "data" DataFrame with at least
    "Close" and "Returns" columns.
    """
    for date, row in market.data.iterrows():
        price = float(row["Close"])  # type: ignore[arg-type]
        daily_return = float(row["Returns"])  # type: ignore[arg-type]
        portfolio.update_equity(daily_return)
        args = inspect.signature(strategy_fn).parameters
        ts_date = pd.Timestamp(date)
        if "market" in args:
            strategy_fn(
                portfolio,
                price,
                ts_date.to_pydatetime(),
                params,
                market,
            )
        else:
            strategy_fn(portfolio, price, ts_date.to_pydatetime(), params)
        total = portfolio.total_value(price, ts_date.to_pydatetime())
        portfolio.record(ts_date.to_pydatetime(), total)
    return pd.DataFrame(portfolio.history)
