"""Unit tests for Portfolio behavior."""

from datetime import datetime, timedelta

import pandas as pd

from options_hedge.portfolio import Portfolio


def test_portfolio_buy_put_updates_cash_and_options() -> None:
    p = Portfolio(initial_value=1000.0, beta=1.0)
    expiry = datetime.now() + timedelta(days=30)
    p.buy_put(strike=90.0, premium=10.0, expiry=expiry, quantity=1)
    assert len(p.options) == 1
    # Cash should be reduced by premium + transaction cost
    # transaction cost = 10.0 * 0.05 = 0.5
    # total cost = 10.0 + 0.5 = 10.5
    assert p.cash == -10.5
    assert p.total_transaction_costs == 0.5


def test_update_equity_and_total_value() -> None:
    p = Portfolio(initial_value=1000.0, beta=1.0)
    # Apply +1% daily return
    p.update_equity(0.01)
    assert p.equity_value > 1000.0
    # No options yet, total value equals equity + cash
    total = p.total_value(
        current_price=100.0, current_date=pd.Timestamp(datetime.now())
    )
    assert total == p.equity_value + p.cash


def test_record_history() -> None:
    p = Portfolio(initial_value=500.0, beta=1.0)
    now = datetime.now()
    p.record(now, 505.0)
    assert len(p.history) == 1
    assert p.history[0]["Date"] == now
    assert p.history[0]["Value"] == 505.0
