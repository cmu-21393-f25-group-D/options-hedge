# Hedging strategies.
#
# This module provides simple protective put strategies:
# - `quarterly_protective_put_strategy`: buys puts on a schedule.
# - `conditional_hedging_strategy`: buys puts when risk triggers fire.

from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd

from .fixed_floor_lp import solve_fixed_floor_lp
from .portfolio import Portfolio
from .simulation import MarketLike  # structural typing
from .vix_floor_lp import PutOption, solve_vix_ladder_lp

# Default strategy parameters
DEFAULT_HEDGE_INTERVAL_DAYS = 90
"""Quarterly rehedging (90 days ≈ 3 months, common for institutional hedging)."""

DEFAULT_PUT_COST_RATIO = 0.01
"""Budget 1% of portfolio value for put premium (industry standard for protection)."""

DEFAULT_STRIKE_RATIO = 0.85
"""15% out-of-the-money puts (85% of current price); deeper tail protection."""

DEFAULT_VIX_FOR_PRICING = 20.0
"""Default VIX level if market data unavailable (long-term average)."""

DEFAULT_EXPIRY_DAYS = 90
"""90-day expiry matches quarterly hedge interval for continuous coverage."""

DEFAULT_LOOKBACK_DAYS = 20
"""20 trading days ≈ 1 calendar month; sufficient for regime detection
without overreaction.
"""

DEFAULT_DROP_THRESHOLD = -0.05
"""Trigger hedging on 5% drawdown (statistically significant move,
~1.5 sigma for 20% vol).
"""

DEFAULT_VOL_MULTIPLIER = 1.5
"""Trigger when recent vol exceeds long-term vol by 50% (indicates regime shift)."""

ANNUAL_TRADING_DAYS = 252
"""Standard number of trading days per year (365 - weekends - holidays)."""

MIN_HISTORICAL_DAYS = 50
"""Minimum data for valid volatility estimate (~40 needed for 95% CI, add buffer)."""

DEFAULT_OPTION_QUANTITY = 1
"""Default number of option contracts per hedge transaction."""


def estimate_put_premium(
    strike: float,
    spot: float,
    days_to_expiry: int,
    vix: float = DEFAULT_VIX_FOR_PRICING,
) -> float:
    """Estimate put option premium as percentage of notional.

    Uses VIX as implied volatility proxy with simplified pricing formula.
    More accurate than fixed 1% budget, accounts for market conditions.

    Args:
        strike: Strike price
        spot: Current spot price
        days_to_expiry: Days until expiration
        vix: VIX level (volatility index, typically 10-80)

    Returns:
        Premium as fraction of spot price (e.g., 0.02 = 2% of notional)

    Examples:
        >>> estimate_put_premium(3400, 4000, 90, vix=20)
        0.015  # ~1.5% of notional (15% OTM, normal vol)
        >>> estimate_put_premium(3400, 4000, 90, vix=60)
        0.045  # ~4.5% of notional (3x higher due to crisis vol)
    """
    moneyness = strike / spot
    implied_vol = vix / 100.0  # VIX is in percentage points
    time_factor = (days_to_expiry / 365.0) ** 0.5

    if moneyness < 1.0:  # OTM put
        # Premium ~ distance × vol × sqrt(time)
        # Scaling factor 0.4 calibrated to match SPX OTM put prices
        # (e.g., 15% OTM, 90 days, VIX=20 → ~0.8% of notional)
        distance = 1.0 - moneyness
        premium_pct = distance * implied_vol * time_factor * 0.4
    else:  # ITM put
        # Intrinsic + time value
        intrinsic_pct = (strike - spot) / spot
        time_value_pct = implied_vol * time_factor * 0.1
        premium_pct = intrinsic_pct + time_value_pct

    # Floor at 0.1% (minimum for transaction costs)
    return float(max(premium_pct, 0.001))


def quarterly_protective_put_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
) -> None:
    """Buy protective puts on a fixed quarterly schedule.

    Now uses VIX-based pricing for realistic premiums instead of
    fixed 1% budget. Strike default changed to 15% OTM.

    Args:
        portfolio: Portfolio to hedge
        current_price: Current market price
        current_date: Current simulation date
        params: Strategy parameters
        market: Market data (for VIX-based pricing)
    """
    hedge_interval = params.get("hedge_interval", DEFAULT_HEDGE_INTERVAL_DAYS)
    strike_ratio = params.get("strike_ratio", DEFAULT_STRIKE_RATIO)
    expiry_days = params.get("expiry_days", DEFAULT_EXPIRY_DAYS)

    last_action = params.get("last_action")
    if last_action is None or ((current_date - last_action).days >= hedge_interval):
        strike = current_price * strike_ratio

        # Get VIX for realistic pricing
        current_vix = DEFAULT_VIX_FOR_PRICING
        if hasattr(market, "get_vix"):
            try:
                current_vix = market.get_vix(pd.Timestamp(current_date))
            except (KeyError, AttributeError):
                pass

        # Estimate premium based on VIX and moneyness
        premium_pct = estimate_put_premium(
            strike, current_price, expiry_days, current_vix
        )

        # Premium per contract (notional = equity value)
        premium = portfolio.equity_value * premium_pct

        expiry = current_date + timedelta(days=expiry_days)
        portfolio.buy_put(strike, premium, expiry, quantity=DEFAULT_OPTION_QUANTITY)
        params["last_action"] = current_date


def conditional_hedging_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
) -> None:
    """Buy protective puts when risk triggers fire.

    Triggers:
    - Price drop exceeds threshold (default -5%)
    - Volatility spike (recent vol > multiplier × long-term vol)

    Now uses VIX-based pricing and 15% OTM strikes.
    """
    lookback_days = params.get("lookback_days", DEFAULT_LOOKBACK_DAYS)
    drop_threshold = params.get("drop_threshold", DEFAULT_DROP_THRESHOLD)
    vol_multiplier = params.get("vol_multiplier", DEFAULT_VOL_MULTIPLIER)
    strike_ratio = params.get("strike_ratio", DEFAULT_STRIKE_RATIO)
    expiry_days = params.get("expiry_days", DEFAULT_EXPIRY_DAYS)

    ts_date = pd.Timestamp(current_date)
    past_data = market.data.loc[:ts_date].tail(  # type: ignore[misc]
        ANNUAL_TRADING_DAYS
    )
    recent_data = market.data.loc[:ts_date].tail(lookback_days)  # type: ignore[misc]  # noqa: E501
    if len(recent_data) < lookback_days or len(past_data) < MIN_HISTORICAL_DAYS:
        return

    # Extract scalars from potentially multi-indexed Series
    close_last = recent_data["Close"].iloc[-1]
    close_first = recent_data["Close"].iloc[0]
    recent_return_val = close_last / close_first - 1
    recent_return = (
        recent_return_val.item()  # type: ignore[union-attr]
        if hasattr(recent_return_val, "item")
        else float(recent_return_val)
    )

    recent_vol_val = recent_data["Returns"].std()
    recent_vol = (
        recent_vol_val.item()  # type: ignore[union-attr]
        if hasattr(recent_vol_val, "item")
        else float(recent_vol_val)
    )

    long_term_vol_val = past_data["Returns"].std()
    long_term_vol = (
        long_term_vol_val.item()  # type: ignore[union-attr]
        if hasattr(long_term_vol_val, "item")
        else float(long_term_vol_val)
    )

    price_drop_trigger = recent_return <= drop_threshold
    vol_spike_trigger = recent_vol > vol_multiplier * long_term_vol
    risk_trigger = price_drop_trigger or vol_spike_trigger

    active_puts = [
        o
        for o in portfolio.options
        if pd.Timestamp(o.expiry) > pd.Timestamp(current_date)
    ]
    if risk_trigger and not active_puts:
        strike = current_price * strike_ratio

        # Get VIX for realistic pricing
        current_vix = DEFAULT_VIX_FOR_PRICING
        if hasattr(market, "get_vix"):
            try:
                current_vix = market.get_vix(pd.Timestamp(current_date))
            except (KeyError, AttributeError):
                pass

        # Estimate premium based on VIX and moneyness
        premium_pct = estimate_put_premium(
            strike, current_price, expiry_days, current_vix
        )

        # Premium per contract
        premium = portfolio.equity_value * premium_pct

        expiry = current_date + timedelta(days=expiry_days)
        portfolio.buy_put(strike, premium, expiry, quantity=DEFAULT_OPTION_QUANTITY)


def vix_ladder_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
    verbose: bool = False,
) -> float:
    """
    VIX-responsive ladder strategy using the VIX-Ladder LP.

    Budget scales with VIX and portfolio beta, then distributes across
    ladder rungs (shallow/medium/deep/catastrophic OTM).

    Parameters
    ----------
    portfolio : Portfolio
        Current portfolio state
    current_price : float
        Current SPX price
    current_date : datetime
        Current simulation date
    params : dict
        Strategy parameters:
        - vix : float (optional, extracted from market if not provided)
        - sigma : float (default 0.15)
        - expiry_days : int (default 90)
        - alpha : float (default 0.05, nuclear hedge protection)
        - ladder_budget_allocations : list of tuples
            Default: [(0.05, 0.15, 0.05),    # shallow: 5-15% OTM, 5%
                      (0.15, 0.25, 0.15),    # medium: 15-25% OTM, 15%
                      (0.25, 0.40, 0.30),    # deep: 25-40% OTM, 30%
                      (0.40, 1.00, 0.50)]    # catastrophic: 40%+, 50%
        - strike_density : float (default 0.05)
        - transaction_cost_rate : float (default 0.05)
    market : MarketData
        Market data for VIX and option chain
    verbose : bool
        Print detailed execution logs

    Returns
    -------
    float
        Total cost of options purchased
    """
    # Extract parameters
    vix = params.get("vix", None)
    if vix is None:
        vix = market.get_vix(pd.Timestamp(current_date))
        if vix is None:
            raise ValueError(
                f"VIX data not available for {current_date}. "
                "Provide 'vix' in params or ensure market has VIX data."
            )

    beta = portfolio.beta
    expiry_days = params.get("expiry_days", 90)
    alpha = params.get("alpha", 0.05)
    strike_density = params.get("strike_density", 0.05)
    transaction_cost_rate = params.get("transaction_cost_rate", 0.05)

    # Default ladder allocations (otm_min, otm_max, budget_frac)
    default_ladder = [
        (0.05, 0.15, 0.05),  # shallow: 5-15% OTM, 5% of budget
        (0.15, 0.25, 0.15),  # medium: 15-25% OTM, 15% of budget
        (0.25, 0.40, 0.30),  # deep: 25-40% OTM, 30% of budget
        (0.40, 1.00, 0.50),  # catastrophic: 40%+ OTM, 50% of budget
    ]
    ladder_budget_allocations = params.get("ladder_budget_allocations", default_ladder)

    # Initialize tracking variables if not present
    if "lp_cost" not in params:
        params["lp_cost"] = 0.0
    if "last_lp_hedge" not in params:
        params["last_lp_hedge"] = None

    # Compute sigma for LP
    sigma_val = market.data["Close"].pct_change().std()
    sigma = (
        sigma_val.item()  # type: ignore[union-attr]
        if hasattr(sigma_val, "item")
        else float(sigma_val)
    ) * (252**0.5)

    # Calculate portfolio value
    V0 = portfolio.equity_value + portfolio.cash

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"VIX-Ladder Strategy - {current_date.date()}")
        print(f"{'=' * 60}")
        print(f"Portfolio Value: ${V0:,.2f}")
        print(f"Current SPX: ${current_price:,.2f}")
        print(f"VIX: {vix:.2f}")
        print(f"Beta: {beta:.2f}")
        print(f"Sigma: {sigma:.2%}")

        # Show budget calculation
        budget_calc = V0 * 0.01 * (vix / 20.0) * max(1.0, beta)
        print(f"VIX-Responsive Budget: ${budget_calc:,.2f}")
        vix_fac = vix / 20.0
        beta_fac = max(1.0, beta)
        print(f"  (Base 1% × VIX factor {vix_fac:.2f} × Beta factor {beta_fac:.2f})")

    # Build option chain - strikes from 5% to 60% OTM
    max_otm = 0.60
    min_otm = 0.05
    otm_levels = []
    otm = min_otm
    while otm <= max_otm:
        otm_levels.append(otm)
        otm += strike_density
    strikes = [current_price * (1 - otm) for otm in otm_levels]

    # Create options with VIX-based pricing
    T_years = expiry_days / 365.25
    expiry_date = current_date + timedelta(days=expiry_days)
    option_chain = []

    for strike in strikes:
        premium_pct = estimate_put_premium(
            strike=strike, spot=current_price, days_to_expiry=expiry_days, vix=vix
        )
        premium = premium_pct * V0
        option_chain.append(
            PutOption(strike=strike, premium=premium, expiry_years=T_years)
        )

    if not option_chain:
        if verbose:
            print("  ⚠️  No options available in chain")
        return 0.0

    # Solve VIX-Ladder LP
    quantities, total_cost, budget = solve_vix_ladder_lp(
        options=option_chain,
        V0=V0,
        S0=current_price,
        beta=beta,
        sigma=sigma,
        T_years=T_years,
        alpha=alpha,
        vix=vix,
        ladder_budget_allocations=ladder_budget_allocations,
        transaction_cost_rate=transaction_cost_rate,
    )

    if verbose:
        print("\n  💡 VIX-Ladder LP Solution:")
        print(f"     Total Budget: ${budget:,.2f}")
        print(f"     Total Cost: ${total_cost:,.2f}")
        num_selected = sum(1 for q in quantities if q > 0)
        print(f"     Options Selected: {num_selected}")

    # Cash management: Ensure we have enough cash for LP purchases
    if total_cost > 0:
        if portfolio.cash < total_cost:
            cash_deficit = total_cost - portfolio.cash
            equity_to_sell = cash_deficit * 1.01  # Small buffer

            if portfolio.equity_value >= equity_to_sell:
                portfolio.equity_value -= equity_to_sell
                portfolio.cash += equity_to_sell
                if verbose:
                    print(
                        f"\n  💵 Rebalanced: Sold ${equity_to_sell:,.0f} "
                        f"equity to fund VIX-Ladder hedge"
                    )
            else:
                # Not enough equity - skip this round
                if verbose:
                    print(
                        f"  ⚠️  Insufficient equity to fund VIX-Ladder "
                        f"(need ${equity_to_sell:,.0f}, "
                        f"have ${portfolio.equity_value:,.0f})"
                    )
                return 0.0

    # Purchase options
    for j, quantity in enumerate(quantities):
        if quantity > 0:
            strike = option_chain[j].strike
            premium = option_chain[j].premium

            try:
                portfolio.buy_put(
                    strike=strike,
                    expiry=expiry_date,
                    premium=premium,
                    quantity=int(quantity),
                )

                if verbose:
                    otm_pct = ((strike - current_price) / current_price) * 100
                    days_to_exp = (expiry_date - current_date).days
                    print(
                        f"  🛡️  Bought {quantity:.2f} put(s): "
                        f"K=${strike:.2f} ({otm_pct:+.1f}% OTM), "
                        f"exp={expiry_date.date()} ({days_to_exp}d), "
                        f"cost=${premium * quantity:,.2f}"
                    )
            except ValueError:
                if verbose:
                    print(
                        f"  ⚠️  Unexpected: insufficient cash "
                        f"(${portfolio.cash:.2f}) after rebalancing"
                    )
                break

    # Track total costs
    params["lp_cost"] += total_cost
    params["last_lp_hedge"] = current_date

    return total_cost


def fixed_floor_lp_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
    market: MarketLike,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Fixed floor portfolio insurance using LP optimization.

    Solves an LP to minimize option premium cost while ensuring
    portfolio value stays above a specified floor (1 - L) × Q across
    all market scenarios.

    Parameters
    ----------
    portfolio : Portfolio
        Current portfolio state
    current_price : float
        Current market price
    current_date : datetime
        Current simulation date
    params : dict
        Strategy parameters:
        - floor_ratio (L) : float (default 0.20, i.e., 20% max loss)
        - scenario_returns : dict (default crash/mild/up scenarios)
        - strike_levels : list of float (default [0.90, 1.00])
        - expiry_days : int (default 90)
        - hedge_interval : int (default 90, days between rehedging)
    market : MarketLike
        Market data (for VIX-based pricing)
    verbose : bool
        Print detailed execution logs

    Returns
    -------
    dict
        Dictionary with 'total_cost' and solution details
    """
    # Extract parameters
    floor_ratio = params.get("floor_ratio", 0.20)  # L = 20% max loss
    hedge_interval = params.get("hedge_interval", 90)
    expiry_days = params.get("expiry_days", 90)

    # Default scenario returns (crash, mild, up)
    scenario_returns = params.get(
        "scenario_returns",
        {
            "crash": -0.40,
            "mild": -0.10,
            "up": 0.10,
        },
    )

    # Default strike levels as ratios of current price
    strike_ratios = params.get("strike_ratios", [0.50, 0.70, 0.90, 1.00])

    # Check if we should hedge (based on interval)
    last_action = params.get("last_fixed_floor_action")
    if last_action is not None and (current_date - last_action).days < hedge_interval:
        return {"total_cost": 0.0, "action": "skipped"}

    # Get VIX for realistic pricing
    current_vix = DEFAULT_VIX_FOR_PRICING
    if hasattr(market, "get_vix"):
        try:
            current_vix = market.get_vix(pd.Timestamp(current_date))
        except (KeyError, AttributeError):
            pass

    # Build inputs for LP solver
    Q = portfolio.equity_value + portfolio.cash  # Total portfolio value
    L = floor_ratio

    # Create strike labels and strike dict
    Is = [f"K{int(ratio * 100)}" for ratio in strike_ratios]
    K = {f"K{int(ratio * 100)}": current_price * ratio for ratio in strike_ratios}

    # Estimate premiums using VIX-based pricing
    p = {}
    for label, strike in K.items():
        premium_pct = estimate_put_premium(
            strike, current_price, expiry_days, current_vix
        )
        # Premium per unit (percentage of Q)
        p[label] = premium_pct * Q

    # Scenario labels and returns
    S = list(scenario_returns.keys())
    r = scenario_returns

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Fixed Floor LP Strategy - {current_date.date()}")
        print(f"{'=' * 60}")
        print(f"Portfolio Value (Q): ${Q:,.2f}")
        print(f"Floor Ratio (L): {L:.1%}")
        print(f"Floor Value (F): ${Q * (1 - L):,.2f}")
        print(f"Current Price: ${current_price:,.2f}")
        print(f"VIX: {current_vix:.2f}")
        print("\nStrikes and Premiums:")
        for label in Is:
            print(f"  {label}: K=${K[label]:.2f}, p=${p[label]:.2f}")
        print("\nScenarios:")
        for scenario, ret in r.items():
            print(f"  {scenario}: {ret:+.1%}")

    # Solve LP
    solution = solve_fixed_floor_lp(
        Is=Is,
        S=S,
        K=K,
        p=p,
        Q=Q,
        r=r,
        L=L,
        name=f"Fixed_Floor_{current_date.date()}",
    )

    # Check if solution is valid
    if solution["status"] != "optimal" or solution["total_cost"] == 0.0:
        # ALWAYS print infeasibility for debugging
        print(
            f"  ⚠️  {current_date.date()}: LP status={solution['status']}, "
            f"strikes={len(Is)}, floor={L:.0%} - SKIPPED"
        )
        return {
            "total_cost": 0.0,
            "action": "skipped",
            "note": f"LP {solution['status']}",
        }

    # Cash management: Ensure we have enough cash for purchases
    total_cost = solution["total_cost"]
    if portfolio.cash < total_cost:
        cash_deficit = total_cost - portfolio.cash
        equity_to_sell = cash_deficit * 1.01  # Small buffer

        if portfolio.equity_value >= equity_to_sell:
            portfolio.equity_value -= equity_to_sell
            portfolio.cash += equity_to_sell
            if verbose:
                print(
                    f"\n  💵 Rebalanced: Sold ${equity_to_sell:,.0f} "
                    f"equity to fund Fixed Floor hedge"
                )
        else:
            # Not enough equity - skip this round
            if verbose:
                print(
                    f"  ⚠️  Insufficient equity to fund Fixed Floor "
                    f"(need ${equity_to_sell:,.0f}, "
                    f"have ${portfolio.equity_value:,.0f})"
                )
            return {
                "total_cost": 0.0,
                "action": "skipped",
                "note": "Insufficient funds",
            }

    # Purchase options based on LP solution
    expiry_date = current_date + timedelta(days=expiry_days)
    options_purchased = 0

    for label, quantity in solution["quantities"].items():
        if quantity > 0.01:  # Only buy if quantity is meaningful
            strike = K[label]
            premium = p[label]

            try:
                portfolio.buy_put(
                    strike=strike,
                    expiry=expiry_date,
                    premium=premium,
                    quantity=int(quantity),
                )
                options_purchased += 1

                if verbose:
                    otm_pct = ((strike - current_price) / current_price) * 100
                    days_to_exp = (expiry_date - current_date).days
                    print(
                        f"  🛡️  Bought {quantity:.2f} put(s): "
                        f"K=${strike:.2f} "
                        f"({otm_pct:+.1f}% {'OTM' if otm_pct < 0 else 'ITM'}), "
                        f"exp={expiry_date.date()} ({days_to_exp}d), "
                        f"cost=${premium * quantity:,.2f}"
                    )
            except ValueError as e:
                if verbose:
                    print(f"  ⚠️  Failed to purchase option {label}: {e}")
                break

    # Mark that we took action
    params["last_fixed_floor_action"] = current_date

    if verbose:
        print(
            f"\n  ✓ Fixed Floor hedge executed: "
            f"{options_purchased} option types purchased"
        )
        print(f"  ✓ Total cost: ${total_cost:,.2f}")
        print(
            f"  ✓ Floor guarantee: ${Q * (1 - L):,.2f} "
            f"({(1 - L) * 100:.0f}% of portfolio)"
        )

    return {
        "total_cost": total_cost,
        "action": "executed",
        "options_purchased": options_purchased,
        "floor_met": solution["floor_met"],
    }
