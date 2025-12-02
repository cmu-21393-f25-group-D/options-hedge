"""Unit tests for Option primitives."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from options_hedge.option import Option


def test_put_payoff_and_value_before_expiry() -> None:
    expiry = datetime.now() + timedelta(days=30)
    opt = Option(strike=100.0, premium=2.5, expiry=expiry, quantity=2)
    # Intrinsic payoff
    assert opt.payoff(90.0) == (100.0 - 90.0) * 2
    assert opt.payoff(110.0) == 0.0
    # Value equals intrinsic when before expiry
    current = pd.Timestamp(datetime.now())
    assert opt.value(90.0, current) == (100.0 - 90.0) * 2
    assert opt.value(110.0, current) == 0.0


def test_put_value_after_expiry_is_zero() -> None:
    expiry = datetime.now() + timedelta(days=1)
    opt = Option(strike=100.0, premium=2.5, expiry=expiry, quantity=1)
    after = pd.Timestamp(expiry + timedelta(days=1))
    assert opt.value(50.0, after) == 0.0


def test_total_cost() -> None:
    expiry = datetime.now() + timedelta(days=10)
    opt = Option(strike=50.0, premium=3.0, expiry=expiry, quantity=5)
    assert pytest.approx(opt.total_cost()) == 15.0
