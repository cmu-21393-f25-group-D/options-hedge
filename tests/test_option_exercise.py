"""Test option exercise at expiry."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from options_hedge.portfolio import Portfolio


def test_option_exercise_at_expiry():
    """Verify that ITM options are exercised and payoff realized in cash."""
    # Setup
    portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
    initial_cash = portfolio.cash
    
    # Buy a put option
    strike = 4000.0
    premium = 100.0
    current_date = datetime(2023, 1, 1)
    expiry = current_date + timedelta(days=30)
    
    portfolio.buy_put(strike=strike, premium=premium, expiry=expiry, quantity=1)
    
    # Verify option purchased
    assert len(portfolio.options) == 1
    cash_after_purchase = portfolio.cash
    assert cash_after_purchase < initial_cash  # Paid premium + transaction cost
    
    # Market crashes - put is now ITM
    crash_price = 3500.0  # Put is $500 ITM
    expiry_date = pd.Timestamp(expiry)
    
    # Exercise expired options
    portfolio.exercise_expired_options(crash_price, expiry_date)
    
    # Verify option exercised
    assert len(portfolio.options) == 0, "Option should be removed after expiry"
    
    expected_payoff = strike - crash_price  # $500
    expected_cash = cash_after_purchase + expected_payoff
    
    assert portfolio.cash == pytest.approx(expected_cash), (
        f"Cash should increase by payoff: "
        f"got {portfolio.cash}, expected {expected_cash}"
    )


def test_option_expires_worthless():
    """Verify that OTM options expire worthless without cash impact."""
    portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
    
    strike = 4000.0
    premium = 100.0
    current_date = datetime(2023, 1, 1)
    expiry = current_date + timedelta(days=30)
    
    portfolio.buy_put(strike=strike, premium=premium, expiry=expiry, quantity=1)
    cash_after_purchase = portfolio.cash
    
    # Market rises - put is OTM
    high_price = 4500.0
    expiry_date = pd.Timestamp(expiry)
    
    portfolio.exercise_expired_options(high_price, expiry_date)
    
    # Verify option removed but no payoff
    assert len(portfolio.options) == 0
    assert portfolio.cash == cash_after_purchase, "OTM option should not add cash"


def test_option_not_exercised_before_expiry():
    """Verify that options are not exercised before expiry date."""
    portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
    
    strike = 4000.0
    premium = 100.0
    current_date = datetime(2023, 1, 1)
    expiry = current_date + timedelta(days=30)
    
    portfolio.buy_put(strike=strike, premium=premium, expiry=expiry, quantity=1)
    
    # One day before expiry
    before_expiry = pd.Timestamp(expiry - timedelta(days=1))
    crash_price = 3500.0
    
    portfolio.exercise_expired_options(crash_price, before_expiry)
    
    # Option should still exist
    assert len(portfolio.options) == 1, "Option should not be exercised before expiry"


def test_multiple_options_exercise():
    """Verify that multiple options exercise correctly."""
    portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
    
    current_date = datetime(2023, 1, 1)
    expiry1 = current_date + timedelta(days=30)
    expiry2 = current_date + timedelta(days=60)
    
    # Buy two options with different expiries
    portfolio.buy_put(strike=4000.0, premium=100.0, expiry=expiry1, quantity=1)
    portfolio.buy_put(strike=3800.0, premium=80.0, expiry=expiry2, quantity=1)
    
    assert len(portfolio.options) == 2
    cash_after_purchase = portfolio.cash
    
    # First expiry date - only first option should exercise
    expiry1_ts = pd.Timestamp(expiry1)
    crash_price = 3500.0
    
    portfolio.exercise_expired_options(crash_price, expiry1_ts)
    
    assert len(portfolio.options) == 1, "Only first option should be removed"
    
    # First option payoff: 4000 - 3500 = 500
    expected_cash = cash_after_purchase + (4000.0 - crash_price)
    assert portfolio.cash == pytest.approx(expected_cash)
    
    # Second expiry - remaining option exercises
    expiry2_ts = pd.Timestamp(expiry2)
    portfolio.exercise_expired_options(crash_price, expiry2_ts)
    
    assert len(portfolio.options) == 0
    # Second option payoff: 3800 - 3500 = 300
    expected_cash += (3800.0 - crash_price)
    assert portfolio.cash == pytest.approx(expected_cash)
