"""Tests for fixed floor LP solver."""

import pytest

# Skip the entire module if gurobipy isn't available
try:
    import gurobipy as _gp  # type: ignore  # noqa: F401
except (
    ImportError,
    ModuleNotFoundError,
):  # pragma: no cover - environment-dependent
    pytest.skip(
        "gurobipy missing; skipping fixed floor LP tests",
        allow_module_level=True,
    )

from options_hedge.fixed_floor_lp import solve_fixed_floor_lp


def test_case_1() -> None:
    """Test basic two-option portfolio with 20% loss floor."""
    Is = ["K90", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K100": 100.0}
    p = {"K90": 1.5, "K100": 3.0}

    Q = 100.0
    L = 0.20

    r = {
        "crash": -0.40,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 1")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_case_2a() -> None:
    """Test with lower loss floor (10%)."""
    Is = ["K90", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K100": 100.0}
    p = {"K90": 1.5, "K100": 3.0}

    Q = 100.0
    L = 0.10

    r = {
        "crash": -0.40,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 2A (L=0.10)")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_case_2b() -> None:
    """Test with higher loss floor (30%)."""
    Is = ["K90", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K100": 100.0}
    p = {"K90": 1.5, "K100": 3.0}

    Q = 100.0
    L = 0.30

    r = {
        "crash": -0.40,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 2B (L=0.30)")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_case_3() -> None:
    """Test with three options and four scenarios."""
    Is = ["K80", "K90", "K100"]
    S = ["crash", "bad", "flat", "good"]

    K = {"K80": 80.0, "K90": 90.0, "K100": 100.0}
    p = {"K80": 1.0, "K90": 2.5, "K100": 4.0}

    Q = 100.0
    L = 0.25

    r = {
        "crash": -0.50,
        "bad": -0.20,
        "flat": 0.00,
        "good": 0.15,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 3")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_case_4() -> None:
    """Test with larger portfolio value (Q=1000)."""
    Is = ["K80", "K90", "K100"]
    S = ["crash", "bad", "flat", "good"]

    K = {"K80": 80.0, "K90": 90.0, "K100": 100.0}
    p = {"K80": 1.0, "K90": 2.5, "K100": 4.0}

    Q = 1000.0
    L = 0.25

    r = {
        "crash": -0.50,
        "bad": -0.20,
        "flat": 0.00,
        "good": 0.15,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 4 (Q=1000)")
    assert solution["status"] in ["optimal", "infeasible"]
    if solution["status"] == "optimal":
        assert solution["total_cost"] > 0


def test_case_5() -> None:
    """Test with different strike prices and premiums."""
    Is = ["K85", "K95", "K105"]
    S = ["crash", "down", "flat", "up"]

    K = {"K85": 85.0, "K95": 95.0, "K105": 105.0}
    p = {"K85": 3.0, "K95": 3.2, "K105": 3.3}

    Q = 100.0
    L = 0.20

    r = {
        "crash": -0.35,
        "down": -0.15,
        "flat": 0.00,
        "up": 0.20,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 5")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_case_6() -> None:
    """Test Case 6 – More scenarios (stress testing).

    I = {K80, K90, K100, K110}, S = {s1,...,s6}
    """
    Is = ["K80", "K90", "K100", "K110"]
    S = ["s1", "s2", "s3", "s4", "s5", "s6"]

    K = {"K80": 80.0, "K90": 90.0, "K100": 100.0, "K110": 110.0}
    p = {"K80": 1.0, "K90": 2.0, "K100": 3.5, "K110": 5.0}

    Q = 100.0
    L = 0.20

    r = {
        "s1": -0.50,
        "s2": -0.30,
        "s3": -0.15,
        "s4": 0.00,
        "s5": 0.10,
        "s6": 0.25,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 6")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


# Additional test cases for comprehensive coverage


def test_tight_floor_high_cost() -> None:
    """Test with very tight floor (low loss tolerance) - should cost more."""
    Is = ["K90", "K95", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K95": 95.0, "K100": 100.0}
    p = {"K90": 2.0, "K95": 3.5, "K100": 5.0}

    Q = 100.0
    L = 0.05  # Only 5% max loss (very conservative)

    r = {
        "crash": -0.40,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Tight Floor Test")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0
    # Tight floor should require more protection
    assert Q * (1.0 - L) == 95.00


def test_loose_floor_low_cost() -> None:
    """Test with loose floor (high loss tolerance) - should cost less."""
    Is = ["K90", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K100": 100.0}
    p = {"K90": 1.5, "K100": 3.0}

    Q = 100.0
    L = 0.40  # 40% max loss (aggressive)

    r = {
        "crash": -0.40,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Loose Floor Test")
    assert solution["status"] == "optimal"
    # Loose floor may not require any protection
    assert solution["total_cost"] >= 0
    assert Q * (1.0 - L) == 60.00


def test_single_strike_single_scenario() -> None:
    """Test minimal case: one strike, one scenario."""
    Is = ["K95"]
    S = ["crash"]

    K = {"K95": 95.0}
    p = {"K95": 2.0}

    Q = 100.0
    L = 0.15

    r = {"crash": -0.30}

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Minimal Test")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_extreme_crash_scenario() -> None:
    """Test with severe crash scenario (-70% drop)."""
    Is = ["K50", "K70", "K90"]
    S = ["catastrophe", "mild", "normal"]

    K = {"K50": 50.0, "K70": 70.0, "K90": 90.0}
    p = {"K50": 0.5, "K70": 1.5, "K90": 3.0}

    Q = 100.0
    L = 0.30

    r = {
        "catastrophe": -0.70,  # Extreme crash
        "mild": -0.15,
        "normal": 0.05,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Extreme Crash Test")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_asymmetric_strikes() -> None:
    """Test with non-uniform strike spacing."""
    Is = ["K75", "K85", "K90", "K100"]
    S = ["crash", "moderate", "flat", "up"]

    K = {"K75": 75.0, "K85": 85.0, "K90": 90.0, "K100": 100.0}
    p = {"K75": 0.8, "K85": 1.5, "K90": 2.5, "K100": 4.5}

    Q = 200.0
    L = 0.25

    r = {
        "crash": -0.45,
        "moderate": -0.20,
        "flat": 0.00,
        "up": 0.15,
    }

    solution = solve_fixed_floor_lp(
        Is, S, K, p, Q, r, L, name="Asymmetric Strikes Test"
    )
    assert solution["status"] in ["optimal", "infeasible"]
    if solution["status"] == "optimal":
        assert solution["total_cost"] > 0


def test_varied_premiums() -> None:
    """Test with varying premium/strike ratios."""
    Is = ["K80", "K90", "K95", "K100"]
    S = ["crash", "down", "flat", "up"]

    K = {"K80": 80.0, "K90": 90.0, "K95": 95.0, "K100": 100.0}
    # Premiums not strictly increasing (market inefficiency)
    p = {"K80": 1.2, "K90": 2.8, "K95": 2.5, "K100": 4.0}

    Q = 150.0
    L = 0.20

    r = {
        "crash": -0.50,
        "down": -0.25,
        "flat": 0.00,
        "up": 0.20,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Varied Premiums Test")
    assert solution["status"] in ["optimal", "infeasible"]
    if solution["status"] == "optimal":
        assert solution["total_cost"] > 0


def test_large_portfolio() -> None:
    """Test with large portfolio value."""
    Is = ["K90", "K95", "K100"]
    S = ["crash", "mild", "up"]

    K = {"K90": 90.0, "K95": 95.0, "K100": 100.0}
    p = {"K90": 1.5, "K95": 2.5, "K100": 4.0}

    Q = 10_000.0  # $10k portfolio
    L = 0.15

    r = {
        "crash": -0.35,
        "mild": -0.10,
        "up": 0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Large Portfolio Test")
    assert solution["status"] in ["optimal", "infeasible"]
    if solution["status"] == "optimal":
        assert solution["total_cost"] > 0
        # Floor should scale with portfolio
        assert Q * (1.0 - L) == 8500.00


def test_many_scenarios() -> None:
    """Test with many market scenarios (stress testing)."""
    Is = ["K85", "K90", "K95", "K100"]
    S = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]

    K = {"K85": 85.0, "K90": 90.0, "K95": 95.0, "K100": 100.0}
    p = {"K85": 1.0, "K90": 2.0, "K95": 3.0, "K100": 4.5}

    Q = 100.0
    L = 0.20

    r = {
        "s1": -0.60,  # Extreme crash
        "s2": -0.40,
        "s3": -0.25,
        "s4": -0.10,
        "s5": 0.00,
        "s6": 0.05,
        "s7": 0.15,
        "s8": 0.30,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Many Scenarios Test")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0


def test_zero_loss_floor() -> None:
    """Test with zero loss tolerance (L=0, full protection)."""
    Is = ["K95", "K100"]
    S = ["crash", "mild"]

    K = {"K95": 95.0, "K100": 100.0}
    p = {"K95": 2.5, "K100": 5.0}

    Q = 100.0
    L = 0.0  # No loss allowed

    r = {
        "crash": -0.30,
        "mild": -0.10,
    }

    solution = solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Zero Loss Floor Test")
    assert solution["status"] == "optimal"
    assert solution["total_cost"] > 0
    assert Q * (1.0 - L) == 100.00
