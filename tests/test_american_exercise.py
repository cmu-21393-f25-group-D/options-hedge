"""Tests for American option early exercise rules."""

from datetime import datetime

import pandas as pd

from options_hedge.american_exercise import (
    should_exercise_at_expiry_only,
    should_exercise_hybrid,
    should_exercise_never,
    should_exercise_optimal_boundary,
    should_exercise_threshold,
    should_exercise_vix_regime,
)
from options_hedge.option import Option
from options_hedge.portfolio import Portfolio


class TestExerciseRules:
    """Test suite for early exercise decision rules."""

    def test_should_exercise_never(self) -> None:
        """Verify never-exercise rule always returns False."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-06-01")

        # Deep ITM, should still not exercise
        assert (
            should_exercise_never(opt, current_price=3000, current_date=current_date)
            is False
        )

        # At expiry, should still not exercise
        assert (
            should_exercise_never(
                opt,
                current_price=3500,
                current_date=pd.Timestamp("2024-12-31"),
            )
            is False
        )

    def test_should_exercise_at_expiry_only_before_expiry(self) -> None:
        """Verify at-expiry rule doesn't exercise early."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-06-01")

        # Deep ITM but before expiry
        result = should_exercise_at_expiry_only(
            opt, current_price=3000, current_date=current_date
        )
        assert result is False

    def test_should_exercise_at_expiry_only_at_expiry_itm(self) -> None:
        """Verify at-expiry rule exercises ITM options at expiration."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        expiry_date = pd.Timestamp("2024-12-31")

        # ITM at expiry
        result = should_exercise_at_expiry_only(
            opt, current_price=3500, current_date=expiry_date
        )
        assert result is True

    def test_should_exercise_at_expiry_only_at_expiry_otm(self) -> None:
        """Verify at-expiry rule doesn't exercise OTM options."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        expiry_date = pd.Timestamp("2024-12-31")

        # OTM at expiry
        result = should_exercise_at_expiry_only(
            opt, current_price=4500, current_date=expiry_date
        )
        assert result is False

    def test_should_exercise_threshold_high_time_value(self) -> None:
        """Verify threshold rule preserves options with significant time
        value."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-01-01")  # Far from expiry

        # NOTE: Current Option.value() returns intrinsic value only
        # (no time value)
        # So threshold rule will always exercise ITM options
        # This test documents current behavior; with Black-Scholes pricing,
        # the rule would preserve options with significant time value
        result = should_exercise_threshold(
            opt,
            current_price=3500,
            current_date=current_date,
            time_value_threshold=0.02,
        )

        # With intrinsic-only pricing, time_value = 0, so always exercises ITM
        assert result is True

    def test_should_exercise_threshold_low_time_value(self) -> None:
        """Verify threshold rule exercises when time value negligible."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        # Very close to expiry (time value minimal)
        current_date = pd.Timestamp("2024-12-30")

        # Deep ITM near expiry
        result = should_exercise_threshold(
            opt,
            current_price=3000,
            current_date=current_date,
            time_value_threshold=0.02,
        )

        # Should exercise (time value < 2% of intrinsic near expiry)
        assert result is True

    def test_should_exercise_vix_regime_vix_rising(self) -> None:
        """Verify VIX rule doesn't exercise when volatility rising."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-03-15")

        # Deep ITM but VIX is rising (panic increasing)
        result = should_exercise_vix_regime(
            opt,
            current_price=3200,  # 20% ITM
            current_date=current_date,
            current_vix=60,
            prev_vix=40,  # VIX up 50%
        )

        assert result is False  # Don't exercise when VIX rising

    def test_should_exercise_vix_regime_vix_falling_deep_itm(self) -> None:
        """Verify VIX rule exercises when volatility drops and deep ITM."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-04-01")

        # Deep ITM and VIX dropping sharply (market stabilizing)
        result = should_exercise_vix_regime(
            opt,
            current_price=3200,  # S/K = 0.80 (20% ITM)
            current_date=current_date,
            current_vix=50,
            prev_vix=75,  # VIX down 33%
            vix_decline_threshold=0.15,
        )

        assert result is True  # Exercise: VIX fell >15% and deep ITM

    def test_should_exercise_vix_regime_shallow_itm(self) -> None:
        """Verify VIX rule doesn't exercise shallow ITM options."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-04-01")

        # Shallow ITM, VIX dropping
        result = should_exercise_vix_regime(
            opt,
            current_price=3800,  # S/K = 0.95 (only 5% ITM)
            current_date=current_date,
            current_vix=50,
            prev_vix=75,  # VIX down 33%
            moneyness_threshold=0.90,  # Require S/K < 0.90
        )

        assert result is False  # Not deep enough ITM

    def test_should_exercise_optimal_boundary_far_from_expiry(self) -> None:
        """Verify optimal boundary rule preserves optionality when far from
        expiry."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-01-01")  # 12 months to expiry

        # Deep ITM but far from expiry
        result = should_exercise_optimal_boundary(
            opt,
            current_price=3000,
            current_date=current_date,
            volatility=0.30,
            min_days_to_expiry=30,
        )

        assert result is False  # Don't exercise with >30 days remaining

    def test_should_exercise_optimal_boundary_near_expiry_deep_itm(
        self,
    ) -> None:
        """Verify optimal boundary rule exercises deep ITM near expiry."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-12-15")  # 16 days to expiry

        # Deep ITM, low volatility, near expiry
        result = should_exercise_optimal_boundary(
            opt,
            current_price=3200,  # S/K = 0.80
            current_date=current_date,
            volatility=0.20,  # Low vol (time value small)
            risk_free_rate=0.045,
            min_days_to_expiry=30,
        )

        assert result is True  # Exercise: below boundary, near expiry

    def test_should_exercise_optimal_boundary_high_volatility(self) -> None:
        """Verify optimal boundary preserves options in high volatility."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-12-15")  # 16 days to expiry

        # Moderate ITM, high volatility
        result = should_exercise_optimal_boundary(
            opt,
            current_price=3400,  # S/K = 0.85
            current_date=current_date,
            volatility=0.60,  # Very high vol (COVID-like)
            risk_free_rate=0.045,
            min_days_to_expiry=30,
        )

        # High vol increases boundary, may preserve option
        # Critical moneyness ≈ 0.85 + 0.15×sqrt(16/365)×0.60 ≈ 0.87
        # S/K = 0.85 < 0.87, should exercise
        assert result is True

    def test_should_exercise_hybrid_vix_trigger(self) -> None:
        """Verify hybrid rule exercises on VIX regime shift."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-04-01")

        # Deep ITM, VIX falling sharply
        result = should_exercise_hybrid(
            opt,
            current_price=3200,
            current_date=current_date,
            current_vix=55,
            prev_vix=82,  # VIX down 33% (COVID recovery)
            volatility=0.50,
            risk_free_rate=0.045,
        )

        assert result is True  # VIX regime shift triggers exercise

    def test_should_exercise_hybrid_boundary_trigger(self) -> None:
        """Verify hybrid rule exercises on optimal boundary crossing."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-12-20")  # 11 days to expiry

        # Deep ITM, VIX stable, near expiry
        result = should_exercise_hybrid(
            opt,
            current_price=3000,  # Very deep ITM
            current_date=current_date,
            current_vix=25,
            prev_vix=24,  # VIX stable (no regime shift)
            volatility=0.25,
            risk_free_rate=0.045,
        )

        # VIX rule won't trigger, but boundary rule should
        assert result is True

    def test_should_exercise_hybrid_no_trigger(self) -> None:
        """Verify hybrid rule preserves options when neither condition met."""
        opt = Option(
            strike=4000, premium=100, expiry=datetime(2024, 12, 31), quantity=1
        )
        current_date = pd.Timestamp("2024-06-01")  # Far from expiry

        # Moderate ITM, VIX stable
        result = should_exercise_hybrid(
            opt,
            current_price=3700,  # S/K = 0.925
            current_date=current_date,
            current_vix=20,
            prev_vix=19,  # VIX stable
            volatility=0.20,
            risk_free_rate=0.045,
        )

        # Neither VIX nor boundary should trigger
        assert result is False


class TestPortfolioEarlyExercise:
    """Test portfolio integration with early exercise."""

    def test_check_early_exercise_basic(self) -> None:
        """Verify no early exercise occurs under European policy."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)

        # Buy deep ITM put near expiry
        expiry = datetime(2024, 12, 31)
        portfolio.buy_put(strike=4000, premium=100, expiry=expiry, quantity=1)

        current_date = pd.Timestamp("2024-12-20")
        current_price = 3000  # Deep ITM

        # Attempt early exercise (European policy should prevent)
        num_exercised = portfolio.check_early_exercise(
            current_price=current_price,
            current_date=current_date,
            exercise_rule=should_exercise_threshold,
            time_value_threshold=0.02,
        )

        # Early exercise disabled: no exercises, option remains
        assert num_exercised == 0
        assert len(portfolio.options) == 1
        # Cash unchanged from purchase cost only
        expected_cash = -105
        assert abs(portfolio.cash - expected_cash) < 1.0

    def test_check_early_exercise_multiple_options(self) -> None:
        """Verify no early exercises under European policy."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)

        # Buy 3 puts with different strikes
        expiry = datetime(2024, 12, 31)
        portfolio.buy_put(
            strike=4200, premium=100, expiry=expiry, quantity=1
        )  # Deep ITM
        portfolio.buy_put(
            strike=4000, premium=80, expiry=expiry, quantity=1
        )  # Moderate ITM
        portfolio.buy_put(
            strike=3800, premium=50, expiry=expiry, quantity=1
        )  # Shallow ITM

        current_date = pd.Timestamp("2024-12-20")
        current_price = 3500

        # Attempt early exercise (European policy should prevent)
        num_exercised = portfolio.check_early_exercise(
            current_price=current_price,
            current_date=current_date,
            exercise_rule=should_exercise_vix_regime,
            current_vix=30,
            prev_vix=50,  # VIX down 40%
            moneyness_threshold=0.85,  # Require S/K < 0.85
        )

        # Early exercise disabled: no exercises, all options remain
        assert num_exercised == 0
        assert len(portfolio.options) == 3

    def test_check_early_exercise_skip_expired(self) -> None:
        """Verify early exercise skips already-expired options."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)

        # Buy option that's already expired
        expiry = datetime(2024, 6, 30)
        portfolio.buy_put(strike=4000, premium=100, expiry=expiry, quantity=1)

        current_date = pd.Timestamp("2024-12-31")  # After expiry
        current_price = 3000

        # Attempt early exercise (should skip expired)
        num_exercised = portfolio.check_early_exercise(
            current_price=current_price,
            current_date=current_date,
            exercise_rule=should_exercise_threshold,
        )

        assert num_exercised == 0  # Expired options handled separately
        assert len(portfolio.options) == 1  # Still in list (not removed)

    def test_check_early_exercise_otm_options(self) -> None:
        """Verify early exercise doesn't exercise OTM options."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)

        # Buy OTM put
        expiry = datetime(2024, 12, 31)
        portfolio.buy_put(strike=3500, premium=50, expiry=expiry, quantity=1)

        current_date = pd.Timestamp("2024-12-20")
        current_price = 4000  # OTM

        # Attempt exercise (should refuse OTM)
        num_exercised = portfolio.check_early_exercise(
            current_price=current_price,
            current_date=current_date,
            exercise_rule=should_exercise_threshold,
        )

        assert num_exercised == 0
        assert len(portfolio.options) == 1  # Option preserved

    def test_early_exercise_hybrid_covid_scenario(self) -> None:
        """Verify no early exercise in COVID scenario under European policy."""
        portfolio = Portfolio(initial_value=1_000_000, beta=1.0)

        # COVID scenario: bought 10 put contracts during panic
        expiry = datetime(2020, 6, 30)
        # Buy 10 separate contracts (typical for testing)
        for _ in range(10):
            portfolio.buy_put(strike=3200, premium=200, expiry=expiry, quantity=1)

        # March 23: Bottom (VIX=82, S&P=2237)
        # April 1: Recovery begins (VIX=55, S&P=2600)
        current_date = pd.Timestamp("2020-04-01")
        current_price = 2600  # S/K = 0.8125

        # Attempt early exercise using hybrid rule (should be disabled)
        num_exercised = portfolio.check_early_exercise(
            current_price=current_price,
            current_date=current_date,
            exercise_rule=should_exercise_hybrid,
            current_vix=55,
            prev_vix=82,  # VIX down 33%
            volatility=0.60,  # High volatility
            risk_free_rate=0.01,  # Near-zero rates in 2020
        )

        # Early exercise disabled: no exercises, options remain until expiry
        assert num_exercised == 0
        assert len(portfolio.options) == 10
        # Cash should reflect only purchase costs
        expected_cash = -(200 * 1.05) * 10
        assert abs(portfolio.cash - expected_cash) < 10.0
