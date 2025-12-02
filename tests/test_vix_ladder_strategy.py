"""Tests for VIX-Ladder strategy."""

from datetime import datetime

import pandas as pd
import pytest

from options_hedge.portfolio import Portfolio
from options_hedge.strategies import vix_ladder_strategy


class SimpleMock:
    """Simple mock object for testing."""

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

        # If not provided, create a simple DataFrame with Close prices
        if not hasattr(self, "data"):
            # Create 100 days of fake price data with realistic volatility
            dates = pd.date_range(start="2020-01-01", periods=100)
            closes = [4000.0 * (1.0 + i * 0.0001) for i in range(100)]
            self.data = pd.DataFrame({"Close": closes}, index=dates)


class TestVixLadderStrategy:
    """Test vix_ladder_strategy function."""

    def test_purchases_options(self):
        """Test strategy purchases options."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 20.0)
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "strike_density": 0.10,
        }

        initial_options = len(portfolio.options)

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        # Should have purchased some options
        assert len(portfolio.options) > initial_options
        assert cost > 0
        assert "last_lp_hedge" in params
        assert params["last_lp_hedge"] == current_date

    def test_first_hedge(self):
        """Test first hedge executes."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 20.0)
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "strike_density": 0.10,
        }

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        # Should have created some hedge
        assert "last_lp_hedge" in params
        assert cost > 0

    def test_verbose_mode(self):
        """Test verbose mode prints debug info."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 30.0)
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "strike_density": 0.15,
        }

        # Pass verbose=True as function argument
        cost = vix_ladder_strategy(
            portfolio, 4000.0, current_date, params, market, verbose=True
        )

        assert cost > 0  # Verbose mode executed successfully

    def test_custom_vix_parameter(self):
        """Test using custom VIX parameter."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock()  # No get_vix method
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "vix": 25.0,  # Explicit VIX
            "strike_density": 0.15,
        }

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        # Should use explicit VIX and complete
        assert "last_lp_hedge" in params
        assert cost > 0

    def test_custom_ladder_allocations(self):
        """Test custom ladder budget allocations."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 20.0)
        current_date = datetime(2020, 1, 1)

        custom_ladder = [
            (0.05, 0.15, 0.20),
            (0.15, 0.25, 0.30),
            (0.25, 0.40, 0.25),
            (0.40, 1.00, 0.25),
        ]

        params = {
            "expiry_days": 90,
            "ladder_budget_allocations": custom_ladder,
            "strike_density": 0.15,
        }

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        assert "last_lp_hedge" in params
        assert cost > 0

    def test_insufficient_cash_sells_equity(self):
        """Test strategy sells equity when cash insufficient."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 100  # Very low cash

        market = SimpleMock(get_vix=lambda date: 30.0)  # High VIX
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "strike_density": 0.20,
        }

        initial_equity = portfolio.equity_value

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        # Should have sold equity to raise cash
        assert portfolio.equity_value < initial_equity
        assert cost > 0

    def test_high_beta_increases_budget(self):
        """Test high beta portfolios get larger budget."""
        portfolio_low = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio_low.equity_value = 1_000_000
        portfolio_low.cash = 50_000

        portfolio_high = Portfolio(initial_value=1_000_000, beta=2.0)
        portfolio_high.equity_value = 1_000_000
        portfolio_high.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 20.0)
        current_date = datetime(2020, 1, 1)

        params_low = {
            "expiry_days": 90,
            "strike_density": 0.15,
        }

        params_high = {
            "expiry_days": 90,
            "strike_density": 0.15,
        }

        cost_low = vix_ladder_strategy(
            portfolio_low, 4000.0, current_date, params_low, market
        )
        cost_high = vix_ladder_strategy(
            portfolio_high, 4000.0, current_date, params_high, market
        )

        # High beta should cost more (2x budget)
        assert "last_lp_hedge" in params_low
        assert "last_lp_hedge" in params_high
        assert cost_high > cost_low

    def test_transaction_costs_parameter(self):
        """Test transaction cost rate parameter."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        market = SimpleMock(get_vix=lambda date: 20.0)
        current_date = datetime(2020, 1, 1)

        params = {
            "expiry_days": 90,
            "transaction_cost_rate": 0.10,  # 10% transaction costs
            "strike_density": 0.15,
        }

        cost = vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)

        assert "last_lp_hedge" in params
        assert cost > 0

    def test_fallback_vix_when_market_unavailable(self):
        """Test error raised when VIX unavailable and not provided."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
        portfolio.equity_value = 1_000_000
        portfolio.cash = 50_000

        # Market without get_vix method
        market = SimpleMock()

        current_date = datetime(2020, 1, 1)

        params = {
            "hedge_interval": 7,
            "expiry_days": 90,
            "strike_density": 0.15,
        }

        # Should raise error when VIX not provided and market lacks get_vix
        with pytest.raises(AttributeError):
            vix_ladder_strategy(portfolio, 4000.0, current_date, params, market)
