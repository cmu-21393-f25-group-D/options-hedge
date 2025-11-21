from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

import gurobipy as gp
from gurobipy import GRB

from .portfolio import Portfolio


def lp_floor_hedge_strategy(
    portfolio: Portfolio,
    current_price: float,
    current_date: datetime,
    params: Dict[str, Any],
) -> None:
    """Buy minimum puts (via LP) to secure a floor under a drop scenario."""
    floor_ratio = params.get("floor_ratio", 0.85)
    downside_scenario = params.get("downside_scenario", -0.15)
    put_cost_ratio = params.get("put_cost", 0.01)
    strike_ratio = params.get("strike_ratio", 0.9)
    expiry_days = params.get("expiry_days", 120)

    # Compute scenario values
    strike = current_price * strike_ratio
    scenario_price = current_price * (1 + downside_scenario)
    payoff_per_contract = max(strike - scenario_price, 0.0)
    if payoff_per_contract <= 0:
        return  # No protection possible with selected strike

    equity_after_drop = portfolio.equity_value * (
        1 + downside_scenario * portfolio.beta
    )
    required_floor = portfolio.equity_value * floor_ratio
    premium_per_contract = portfolio.equity_value * put_cost_ratio

    # If already above floor without hedge do nothing
    if equity_after_drop >= required_floor:
        return

    model = gp.Model("lp_floor_hedge")
    n_puts = model.addVar(vtype=GRB.INTEGER, name="n_puts", lb=0)

    # Objective: minimize total premium cost
    model.setObjective(premium_per_contract * n_puts, GRB.MINIMIZE)

    # Constraint: equity after drop + payoff >= required floor
    model.addConstr(
        equity_after_drop + payoff_per_contract * n_puts >= required_floor,
        "floor",
    )

    model.Params.OutputFlag = 0
    model.optimize()
    if model.status == GRB.OPTIMAL and n_puts.X > 0.5:
        quantity = int(round(n_puts.X))
        expiry = current_date + timedelta(days=expiry_days)
        portfolio.buy_put(
            strike=strike,
            premium=premium_per_contract,
            expiry=expiry,
            quantity=quantity,
        )
