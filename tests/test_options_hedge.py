"""Tests for the options hedge optimization module."""

import pytest
from options_hedge.options_hedge import solve_simple_lp


def test_solve_simple_lp() -> None:
    """Test basic LP solution."""
    x, y, obj = solve_simple_lp(x_max=5.0, y_max=7.0)

    # Check bounds are respected
    assert x <= 5.0
    assert y <= 7.0
    assert x >= 0
    assert y >= 0

    # Check optimal solution
    assert pytest.approx(x) == 5.0
    assert pytest.approx(y) == 7.0
    assert pytest.approx(obj) == 12.0  # x + y = 5 + 7 = 12


def test_solve_simple_lp_equal_bounds() -> None:
    """Test with equal bounds."""
    x, y, obj = solve_simple_lp(x_max=10.0, y_max=10.0)

    # Check bounds
    assert x <= 10.0
    assert y <= 10.0

    # Check optimal solution
    assert pytest.approx(x) == 10.0
    assert pytest.approx(y) == 10.0
    assert pytest.approx(obj) == 20.0  # x + y = 10 + 10 = 20
