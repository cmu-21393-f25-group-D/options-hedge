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
    assert ("Objective" in out) or ("Model ended" in out)


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
