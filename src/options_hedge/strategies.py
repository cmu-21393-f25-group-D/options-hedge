from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd

from .portfolio import Portfolio
from .simulation import MarketLike  # structural typing


def quarterly_protective_put_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
) -> None:
    hedge_interval = params.get("hedge_interval", 90)
    put_cost_ratio = params.get("put_cost", 0.01)
    strike_ratio = params.get("strike_ratio", 0.9)
    expiry_days = params.get("expiry_days", 90)

    last_action = params.get("last_action")
    if last_action is None or ((current_date - last_action).days >= hedge_interval):
        strike = current_price * strike_ratio
        premium = portfolio.equity_value * put_cost_ratio
        expiry = current_date + timedelta(days=expiry_days)
        portfolio.buy_put(strike, premium, expiry, quantity=1)
        params["last_action"] = current_date


def conditional_hedging_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
) -> None:
    lookback_days = params.get("lookback_days", 20)
    drop_threshold = params.get("drop_threshold", -0.05)
    vol_multiplier = params.get("vol_multiplier", 1.5)
    put_cost_ratio = params.get("put_cost", 0.01)
    strike_ratio = params.get("strike_ratio", 0.9)
    expiry_days = params.get("expiry_days", 90)

    ts_date = pd.Timestamp(current_date)
    past_data = market.data.loc[:ts_date].tail(252)
    recent_data = market.data.loc[:ts_date].tail(lookback_days)
    if len(recent_data) < lookback_days or len(past_data) < 50:
        return

    recent_return = float(
        recent_data["Close"].iloc[-1] / recent_data["Close"].iloc[0] - 1
    )
    recent_vol = float(recent_data["Returns"].std())
    long_term_vol = float(past_data["Returns"].std())

    price_drop_trigger = recent_return <= drop_threshold
    vol_spike_trigger = recent_vol > vol_multiplier * long_term_vol
    risk_trigger = price_drop_trigger or vol_spike_trigger

    active_puts = [
        o
        for o in portfolio.options
        if pd.Timestamp(o.expiry) > pd.Timestamp(current_date)
    ]
    if risk_trigger and not active_puts:
        strike = current_price * strike_ratio
        premium = portfolio.equity_value * put_cost_ratio
        expiry = current_date + timedelta(days=expiry_days)
        portfolio.buy_put(strike, premium, expiry, quantity=1)
