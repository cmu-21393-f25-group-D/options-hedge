"""Early exercise rules for American put options in portfolio insurance.

This module provides multiple strategies for deciding when to exercise
American-style put options before expiration.
"""

from __future__ import annotations

import pandas as pd

from .option import Option


def should_exercise_never(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    **kwargs,
) -> bool:
    """Never exercise early (European-style behavior).

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    **kwargs
        Ignored (for interface compatibility)

    Returns
    -------
    bool
        Always False (never exercise early)
    """
    return False


def should_exercise_at_expiry_only(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    **kwargs,
) -> bool:
    """Exercise only at expiration (current behavior).

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    **kwargs
        Ignored (for interface compatibility)

    Returns
    -------
    bool
        True only if at expiration and ITM
    """
    expiry_ts = pd.Timestamp(option.expiry)
    intrinsic = max(option.strike - current_price, 0)

    return current_date >= expiry_ts and intrinsic > 0


def should_exercise_threshold(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    time_value_threshold: float = 0.02,
    **kwargs,
) -> bool:
    """Exercise when time value falls below threshold.

    Exercise if intrinsic value is positive and remaining time value
    is less than threshold fraction of intrinsic value.

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    time_value_threshold : float, optional
        Exercise when time_value < threshold × intrinsic (default: 0.02 = 2%)
    **kwargs
        Ignored (for interface compatibility)

    Returns
    -------
    bool
        True if should exercise now

    Examples
    --------
    >>> opt = Option(strike=4000, premium=100, expiry=datetime(2024, 12, 31))
    >>> # Current price = 3500, intrinsic = 500
    >>> # If option value = 510, time value = 10 (2% of intrinsic)
    >>> should_exercise_threshold(opt, 3500, pd.Timestamp('2024-10-01'))
    True  # Time value only 2% of intrinsic, exercise now
    """
    intrinsic = max(option.strike - current_price, 0)

    if intrinsic == 0:
        return False

    # Current option value includes both intrinsic and time value
    total_value = option.value(current_price, current_date)
    time_value = total_value - intrinsic

    # Exercise if time value has decayed to negligible amount
    return time_value < time_value_threshold * intrinsic


def should_exercise_vix_regime(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    current_vix: float,
    prev_vix: float,
    vix_decline_threshold: float = 0.15,
    moneyness_threshold: float = 0.90,
    **kwargs,
) -> bool:
    """Exercise when VIX drops significantly (market stabilizing).

    Exercises deep ITM puts when volatility regime shifts from high to low,
    indicating market has likely bottomed and is stabilizing.

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    current_vix : float
        Current VIX level
    prev_vix : float
        Previous period VIX level
    vix_decline_threshold : float, optional
        Exercise when VIX drops by this fraction (default: 0.15 = 15%)
    moneyness_threshold : float, optional
        Exercise when S/K below this level (default: 0.90 = 10% ITM)
    **kwargs
        Ignored (for interface compatibility)

    Returns
    -------
    bool
        True if should exercise now

    Examples
    --------
    >>> # COVID crash: VIX peaked at 82, then dropped to 60 (-27%)
    >>> # Put is deep ITM (S=2500, K=3000, S/K=0.83)
    >>> should_exercise_vix_regime(
    ...     opt, current_price=2500, current_date=pd.Timestamp('2020-04-01'),
    ...     current_vix=60, prev_vix=82
    ... )
    True  # VIX dropped 27%, exercise to lock in gains
    """
    intrinsic = max(option.strike - current_price, 0)

    if intrinsic == 0:
        return False

    # Check moneyness (S/K)
    moneyness = current_price / option.strike
    is_deep_itm = moneyness < moneyness_threshold

    # Check VIX decline (signal of market stabilization)
    if prev_vix <= 0:
        return False  # Invalid previous VIX

    vix_change = (current_vix - prev_vix) / prev_vix
    vix_declining_sharply = vix_change < -vix_decline_threshold

    # Exercise if deep ITM AND VIX has dropped significantly
    return is_deep_itm and vix_declining_sharply


def should_exercise_optimal_boundary(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    volatility: float,
    risk_free_rate: float = 0.045,
    min_days_to_expiry: int = 30,
    **kwargs,
) -> bool:
    """Exercise based on approximate optimal stopping boundary.

    Uses simplified Longstaff-Schwartz approximation. Exercises when
    moneyness crosses below critical threshold that depends on time
    remaining and volatility.

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    volatility : float
        Annualized volatility (e.g., 0.30 for 30%)
    risk_free_rate : float, optional
        Risk-free rate (default: 0.045 = 4.5%)
    min_days_to_expiry : int, optional
        Don't exercise if more than this many days remain (default: 30)
    **kwargs
        Ignored (for interface compatibility)

    Returns
    -------
    bool
        True if should exercise now

    Notes
    -----
    Approximate optimal boundary for American puts:
    S* / K ≈ 0.80 + 0.15 × sqrt(T) × σ

    Where T = time to expiry (years), σ = volatility

    Examples
    --------
    >>> # Deep ITM put with 20 days to expiry, high vol (40%)
    >>> should_exercise_optimal_boundary(
    ...     opt, current_price=3200, current_date=pd.Timestamp('2020-03-15'),
    ...     volatility=0.40  # Strike = 4000, S/K = 0.80
    ... )
    True  # Below optimal boundary, exercise now
    """
    intrinsic = max(option.strike - current_price, 0)

    if intrinsic == 0:
        return False

    expiry_ts = pd.Timestamp(option.expiry)
    days_to_expiry = (expiry_ts - current_date).days

    # Don't exercise if too far from expiry (preserve optionality)
    if days_to_expiry > min_days_to_expiry:
        return False

    # Compute moneyness S/K
    moneyness = current_price / option.strike

    # Approximate optimal exercise boundary
    # Rule: Exercise when S/K < critical_moneyness
    # Formula: S*/K ≈ base_level + volatility_adjustment
    time_to_expiry_years = days_to_expiry / 365.0

    # Base level decreases with interest rates (carrying cost)
    # High rates → exercise earlier to capture intrinsic value
    base_level = 0.85 - 0.10 * risk_free_rate

    # Volatility adjustment increases boundary (more optionality)
    # High vol → wait longer before exercising
    vol_adjustment = 0.15 * (time_to_expiry_years**0.5) * volatility

    critical_moneyness = base_level + vol_adjustment

    # Exercise if current moneyness below critical level
    return moneyness < critical_moneyness


def should_exercise_hybrid(
    option: Option,
    current_price: float,
    current_date: pd.Timestamp,
    current_vix: float,
    prev_vix: float,
    volatility: float,
    risk_free_rate: float = 0.045,
    **kwargs,
) -> bool:
    """Hybrid rule combining VIX regime and optimal boundary.

    Exercises when EITHER:
    1. VIX regime shift detected (market stabilizing), OR
    2. Optimal boundary crossed (deep ITM near expiry)

    This combines market timing signal (VIX) with mathematical
    optimality (boundary), providing robust exercise decisions.

    Parameters
    ----------
    option : Option
        The option to evaluate
    current_price : float
        Current underlying price
    current_date : pd.Timestamp
        Current date
    current_vix : float
        Current VIX level
    prev_vix : float
        Previous period VIX level
    volatility : float
        Annualized volatility (for boundary calculation)
    risk_free_rate : float, optional
        Risk-free rate (default: 0.045 = 4.5%)
    **kwargs
        Additional parameters passed to sub-rules

    Returns
    -------
    bool
        True if should exercise now

    Examples
    --------
    >>> # COVID crash recovery (VIX 80→55, S=2600, K=3200)
    >>> should_exercise_hybrid(
    ...     opt, current_price=2600, current_date=pd.Timestamp('2020-04-01'),
    ...     current_vix=55, prev_vix=80, volatility=0.60
    ... )
    True  # VIX dropped 31%, triggers regime-based exercise
    """
    # Try VIX regime rule first (market signal)
    if should_exercise_vix_regime(
        option,
        current_price,
        current_date,
        current_vix=current_vix,
        prev_vix=prev_vix,
        **kwargs,
    ):
        return True

    # Fall back to optimal boundary (mathematical rule)
    return should_exercise_optimal_boundary(
        option,
        current_price,
        current_date,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        **kwargs,
    )
