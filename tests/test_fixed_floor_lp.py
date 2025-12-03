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


def test_case_1(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 1")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_case_2a(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 2A (L=0.10)")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_case_2b(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 2B (L=0.30)")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_case_3(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 3")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_case_4(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 4 (Q=1000)")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out) or ("infeasible" in out)


def test_case_5(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 5")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_case_6(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Test Case 6")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


# Additional test cases for comprehensive coverage


def test_tight_floor_high_cost(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Tight Floor Test")
    out = capsys.readouterr().out
    assert "Objective" in out
    # Tight floor should require more protection
    assert "Floor F = 95.00" in out


def test_loose_floor_low_cost(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Loose Floor Test")
    out = capsys.readouterr().out
    assert "Objective" in out
    assert "Floor F = 60.00" in out


def test_single_strike_single_scenario(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test minimal case: one strike, one scenario."""
    Is = ["K95"]
    S = ["crash"]

    K = {"K95": 95.0}
    p = {"K95": 2.0}

    Q = 100.0
    L = 0.15

    r = {"crash": -0.30}

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Minimal Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_extreme_crash_scenario(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Extreme Crash Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_asymmetric_strikes(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Asymmetric Strikes Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out) or ("infeasible" in out)


def test_varied_premiums(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Varied Premiums Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out) or ("infeasible" in out)


def test_large_portfolio(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Large Portfolio Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out) or ("infeasible" in out)
    # Floor should scale with portfolio (only check if not infeasible)
    if "infeasible" not in out:
        assert "Floor F = 8500.00" in out


def test_many_scenarios(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Many Scenarios Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)


def test_zero_loss_floor(capsys: pytest.CaptureFixture[str]) -> None:
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

    solve_fixed_floor_lp(Is, S, K, p, Q, r, L, name="Zero Loss Floor Test")
    out = capsys.readouterr().out
    assert ("Objective" in out) or ("Model ended" in out)
    assert "Floor F = 100.00" in out
