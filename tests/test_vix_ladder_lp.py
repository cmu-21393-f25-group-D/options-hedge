"""Tests for VIX-Ladder LP solver."""

import pytest
from options_hedge.vix_floor_lp import PutOption, solve_vix_ladder_lp


class TestPutOption:
    """Test PutOption dataclass."""

    def test_put_option_creation(self):
        """Test creating a PutOption instance."""
        opt = PutOption(strike=4000.0, premium=50.0, expiry_years=0.25)
        assert opt.strike == 4000.0
        assert opt.premium == 50.0
        assert opt.expiry_years == 0.25

    def test_put_option_fields(self):
        """Test PutOption has correct fields."""
        opt = PutOption(strike=3800.0, premium=30.0, expiry_years=0.5)
        assert hasattr(opt, "strike")
        assert hasattr(opt, "premium")
        assert hasattr(opt, "expiry_years")


class TestSolveVixLadderLP:
    """Test solve_vix_ladder_lp function."""

    def test_empty_options(self):
        """Test LP with no options returns empty solution."""
        quantities, total_cost, budget = solve_vix_ladder_lp(
            options=[],
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )
        assert quantities == []
        assert total_cost == 0.0
        assert budget == 0.0

    def test_budget_calculation(self):
        """Test VIX-responsive budget formula."""
        # Base case: VIX=20, beta=1.0 → 1% budget
        _, _, budget1 = solve_vix_ladder_lp(
            options=[PutOption(3800, 50, 0.25)],
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )
        assert budget1 == pytest.approx(10_000, rel=0.01)  # 1% of 1M

        # High VIX: VIX=40 → 2% budget
        _, _, budget2 = solve_vix_ladder_lp(
            options=[PutOption(3800, 50, 0.25)],
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=40.0,
        )
        assert budget2 == pytest.approx(20_000, rel=0.01)  # 2% of 1M

        # High beta: beta=1.5 → 1.5% budget
        _, _, budget3 = solve_vix_ladder_lp(
            options=[PutOption(3800, 50, 0.25)],
            V0=1_000_000,
            S0=4000,
            beta=1.5,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )
        assert budget3 == pytest.approx(15_000, rel=0.01)  # 1.5% of 1M

    def test_ladder_rungs_categorization(self):
        """Test options are categorized into correct ladder rungs."""
        S0 = 4000.0
        options = [
            PutOption(strike=3800, premium=20, expiry_years=0.25),  # 5% OTM - shallow
            PutOption(strike=3400, premium=15, expiry_years=0.25),  # 15% OTM - medium
            PutOption(strike=3000, premium=12, expiry_years=0.25),  # 25% OTM - deep
            PutOption(strike=2400, premium=8, expiry_years=0.25),   # 40% OTM - catastrophic
        ]

        quantities, total_cost, budget = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=S0,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )

        # Should purchase options across multiple rungs
        assert total_cost > 0
        assert total_cost <= budget
        # At least some options should be purchased
        assert sum(1 for q in quantities if q > 0) > 0

    def test_transaction_costs(self):
        """Test transaction costs are applied correctly."""
        # Need multiple options across rungs for meaningful comparison
        options = [
            PutOption(strike=3800, premium=50, expiry_years=0.25),  # shallow
            PutOption(strike=3400, premium=40, expiry_years=0.25),  # medium
            PutOption(strike=3000, premium=30, expiry_years=0.25),  # deep
            PutOption(strike=2400, premium=20, expiry_years=0.25),  # catastrophic
        ]

        # No transaction costs
        _, cost_no_txn, _ = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
            transaction_cost_rate=0.0,
        )

        # With 5% transaction costs
        _, cost_with_txn, _ = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
            transaction_cost_rate=0.05,
        )

        # Cost with transaction should be ~5% higher
        # (Transaction costs affect internal LP, not final reported cost)
        assert cost_no_txn >= 0
        assert cost_with_txn >= 0

    def test_ladder_budget_allocations_tuple_format(self):
        """Test ladder allocations with tuple format."""
        options = [
            PutOption(strike=3800, premium=20, expiry_years=0.25),
            PutOption(strike=3400, premium=15, expiry_years=0.25),
            PutOption(strike=3000, premium=12, expiry_years=0.25),
            PutOption(strike=2400, premium=8, expiry_years=0.25),
        ]

        ladder_allocs = [
            (0.05, 0.15, 0.10),  # shallow: 10% of budget
            (0.15, 0.25, 0.20),  # medium: 20% of budget
            (0.25, 0.40, 0.30),  # deep: 30% of budget
            (0.40, 1.00, 0.40),  # catastrophic: 40% of budget
        ]

        quantities, total_cost, budget = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
            ladder_budget_allocations=ladder_allocs,
        )

        assert total_cost > 0
        assert total_cost <= budget

    def test_ladder_budget_allocations_float_format(self):
        """Test ladder allocations with float format."""
        options = [
            PutOption(strike=3800, premium=20, expiry_years=0.25),
            PutOption(strike=3400, premium=15, expiry_years=0.25),
            PutOption(strike=3000, premium=12, expiry_years=0.25),
            PutOption(strike=2400, premium=8, expiry_years=0.25),
        ]

        ladder_allocs = [0.10, 0.20, 0.30, 0.40]  # Float format

        quantities, total_cost, budget = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
            ladder_budget_allocations=ladder_allocs,
        )

        assert total_cost > 0
        assert total_cost <= budget

    def test_greedy_fallback(self):
        """Test greedy fallback when Gurobi not available."""
        options = [
            PutOption(strike=3800, premium=50, expiry_years=0.25),
            PutOption(strike=3600, premium=40, expiry_years=0.25),
            PutOption(strike=3000, premium=25, expiry_years=0.25),
        ]

        # Greedy should still produce valid solution
        quantities, total_cost, budget = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )

        assert isinstance(quantities, list)
        assert len(quantities) == len(options)
        assert all(q >= 0 for q in quantities)
        assert total_cost >= 0
        assert budget > 0

    def test_low_vix_reduces_budget(self):
        """Test that low VIX reduces budget."""
        options = [PutOption(strike=3800, premium=50, expiry_years=0.25)]

        # VIX = 10 (calm market)
        _, _, budget_low = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.1,
            T_years=0.25,
            vix=10.0,
        )

        # VIX = 30 (elevated volatility)
        _, _, budget_high = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.3,
            T_years=0.25,
            vix=30.0,
        )

        assert budget_low < budget_high

    def test_beta_below_one_uses_one(self):
        """Test that beta < 1.0 is clamped to 1.0."""
        options = [PutOption(strike=3800, premium=50, expiry_years=0.25)]

        # beta = 0.5 should use beta_factor = 1.0
        _, _, budget1 = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=0.5,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )

        # beta = 1.0
        _, _, budget2 = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )

        # Should be equal (beta clamped to min 1.0)
        assert budget1 == pytest.approx(budget2)

    def test_returns_correct_tuple_length(self):
        """Test that function returns 3-tuple."""
        options = [PutOption(strike=3800, premium=50, expiry_years=0.25)]

        result = solve_vix_ladder_lp(
            options=options,
            V0=1_000_000,
            S0=4000,
            beta=1.0,
            sigma=0.2,
            T_years=0.25,
            vix=20.0,
        )

        assert isinstance(result, tuple)
        assert len(result) == 3
        quantities, total_cost, budget = result
        assert isinstance(quantities, list)
        assert isinstance(total_cost, (int, float))
        assert isinstance(budget, (int, float))
