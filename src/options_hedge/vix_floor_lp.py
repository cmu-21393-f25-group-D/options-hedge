"""
VIX-Ladder LP: Linear program for diversified strike protection.

API:
  - PutOption: strike/premium/expiry spec
  - solve_vix_ladder_lp(...): solve LP for ladder-diversified hedge
"""

from dataclasses import dataclass
from typing import List, Tuple

# Constants
DEFAULT_ALPHA = 0.05

# Tolerances
EPSILON = 1e-9
TOLERANCE = 1e-12


@dataclass
class PutOption:
    """Candidate put option specification.

    - strike: strike price K_j
    - premium: premium cost per unit c_j
    - expiry_years: time to expiry in years
    """

    strike: float
    premium: float
    expiry_years: float


__all__ = [
    "PutOption",
    "solve_vix_ladder_lp",
]


def solve_vix_ladder_lp(
    options: List[PutOption],
    V0: float,
    S0: float,
    beta: float,
    sigma: float,
    T_years: float,
    alpha: float = DEFAULT_ALPHA,
    vix: float = 20.0,
    ladder_budget_allocations=None,
    transaction_cost_rate: float = 0.0,
) -> Tuple[List[float], float, float]:
    """Solve ladder LP with VIX-responsive budget for diversified protection.

    Instead of complex floor-based constraints, this uses a simple approach:
    - Budget = f(VIX, beta) × V0
    - Enforce minimum spend in each strike ladder rung
    - Let LP optimize within those constraints

    This creates graduated protection across strike levels, with total budget
    scaling with market volatility and portfolio risk.

    Args:
        options: List of available put options
        V0: Current portfolio value
        S0: Current spot price
        beta: Portfolio beta
        sigma: Implied volatility
        T_years: Time horizon for stress scenario
        alpha: Tail probability for stress (default 5%)
        vix: VIX level (default 20)
        ladder_budget_allocations: Budget fractions, either:
            - List of floats: [0.05, 0.15, 0.30, 0.50]
            - List of tuples: [(otm_min, otm_max, budget_frac), ...]
            Default: [(0.05, 0.15, 0.05), (0.15, 0.25, 0.15),
                      (0.25, 0.40, 0.30), (0.40, 1.00, 0.50)]
        transaction_cost_rate: Transaction cost as fraction of premium

    Returns:
        (quantities, total_cost, budget_allocated)

    Note:
        Total budget = vix_factor × beta_factor × base_budget × V0
        where base_budget = 0.01 (1% of portfolio)
              vix_factor = vix / 20  (normalized to VIX=20)
              beta_factor = max(1.0, beta)  (higher beta = more budget)
    """
    if not options:
        return [], 0.0, 0.0

    # Default ladder allocations
    if ladder_budget_allocations is None:
        ladder_budget_allocations = [
            (0.05, 0.15, 0.05),
            (0.15, 0.25, 0.15),
            (0.25, 0.40, 0.30),
            (0.40, 1.00, 0.50),
        ]

    # Parse ladder allocations - handle both tuple and float formats
    budget_fracs = []
    for item in ladder_budget_allocations:
        if isinstance(item, (tuple, list)):
            # Format: (otm_min, otm_max, budget_frac)
            budget_fracs.append(item[2])
        else:
            # Format: budget_frac only
            budget_fracs.append(item)

    # VIX-responsive budget calculation
    base_budget_pct = 0.01  # 1% of portfolio at VIX=20, beta=1
    vix_factor = vix / 20.0  # Scale with VIX
    beta_factor = max(1.0, beta)  # Higher beta = more risk = more budget
    total_budget = V0 * base_budget_pct * vix_factor * beta_factor

    # Setup option costs with transaction costs
    c = [opt.premium * (1 + transaction_cost_rate) for opt in options]

    # Ladder rungs by OTM percentage
    ladder_rungs = [
        ("shallow", 0.05, 0.15),  # 5-15% OTM
        ("medium", 0.15, 0.25),  # 15-25% OTM
        ("deep", 0.25, 0.40),  # 25-40% OTM
        ("catastrophic", 0.40, 1.0),  # 40%+ OTM
    ]

    # Categorize options into rungs
    rung_indices = [[] for _ in range(4)]
    for j, opt in enumerate(options):
        otm_pct = (S0 - opt.strike) / S0
        for k, (_, otm_min, otm_max) in enumerate(ladder_rungs):
            if otm_min <= otm_pct < otm_max:
                rung_indices[k].append(j)
                break

    # Try Gurobi first
    try:  # pragma: no cover
        import gurobipy as gp
        from gurobipy import GRB

        m = gp.Model("vix_ladder_lp")
        m.Params.OutputFlag = 0

        x_vars = [m.addVar(lb=0.0, name=f"x_{k}") for k in range(len(options))]

        # Objective: minimize total cost
        m.setObjective(
            gp.quicksum(c[j] * x_vars[j] for j in range(len(options))),
            GRB.MINIMIZE,
        )

        # Constraint: total budget limit
        m.addConstr(
            gp.quicksum(c[j] * x_vars[j] for j in range(len(options))) <= total_budget,
            name="budget_limit",
        )

        # Ladder constraints: minimum spend in each rung
        for k, (name, _, _) in enumerate(ladder_rungs):
            budget_frac = budget_fracs[k]
            if rung_indices[k] and budget_frac > 0:
                min_spend = total_budget * budget_frac
                m.addConstr(
                    gp.quicksum(c[j] * x_vars[j] for j in rung_indices[k]) >= min_spend,
                    name=f"ladder_{name}",
                )

        m.optimize()

        if m.Status == GRB.OPTIMAL:
            x_sol = [x_vars[j].X for j in range(len(options))]
            total_cost = sum(c[j] * x_sol[j] for j in range(len(options)))
            return x_sol, total_cost, total_budget
        else:
            # Fall through to greedy
            pass

    except ImportError:
        pass

    # Greedy fallback: allocate budget proportionally to ladder requirements
    x_sol = [0.0] * len(options)

    for k, (name, _, _) in enumerate(ladder_rungs):
        budget_frac = budget_fracs[k]
        if not rung_indices[k] or budget_frac <= 0:
            continue

        rung_budget = total_budget * budget_frac
        # Sort options in this rung by premium (cheapest first)
        rung_opts = sorted(rung_indices[k], key=lambda j: c[j])

        spent = 0.0
        for j in rung_opts:
            if spent >= rung_budget:
                break
            # Buy as many as budget allows
            quantity = (rung_budget - spent) / c[j]
            x_sol[j] = quantity
            spent += c[j] * quantity

    total_cost = sum(c[j] * x_sol[j] for j in range(len(options)))
    return x_sol, total_cost, total_budget
