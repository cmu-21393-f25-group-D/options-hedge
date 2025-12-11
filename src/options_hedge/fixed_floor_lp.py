import gurobipy as gp
from gurobipy import GRB


def solve_fixed_floor_lp(
    Is: list, S: list, K: dict, p: dict, Q: float, r: dict, L: float, name: str = "Test"
) -> dict:
    """Solve Fixed Floor LP and return solution.

    Returns
    -------
    dict
        Solution with keys:
        - 'quantities': dict mapping strike labels to quantities
        - 'total_cost': float, total premium cost
        - 'shortfalls': dict mapping scenarios to shortfall amounts
        - 'floor_met': bool, whether floor constraint is satisfied
        - 'status': str, optimization status
    """
    m = gp.Model(f"portfolio_insurance_{name}")
    m.Params.OutputFlag = 0

    V = {s: Q * (1.0 + r[s]) for s in S}
    F = Q * (1.0 - L)

    Payoff = {(i, s): max(0.0, K[i] - V[s]) for i in Is for s in S}

    x = m.addVars(Is, lb=0.0, name="x")
    z = m.addVars(S, lb=0.0, name="z")
    m.setObjective(
        gp.quicksum(p[i] * x[i] for i in Is) + gp.quicksum(z[s] for s in S),
        GRB.MINIMIZE,
    )

    # Floor constraint with shortfall variable z[s]
    # V[s] + Payoffs - z[s] >= F  =>  z[s] = shortfall below floor
    for s in S:
        m.addConstr(
            V[s] + gp.quicksum(Payoff[i, s] * x[i] for i in Is) - z[s] >= F,
            name=f"floor_guarantee[{s}]",
        )

    m.optimize()

    if m.Status == GRB.OPTIMAL:
        # Check if floor met in all scenarios (shortfalls near zero)
        floor_met = all(z[s].X < 1e-4 for s in S)

        # Return solution
        return {
            "quantities": {i: x[i].X for i in Is},
            "total_cost": sum(p[i] * x[i].X for i in Is),
            "shortfalls": {s: z[s].X for s in S},
            "floor_met": floor_met,
            "status": "optimal",
        }
    elif m.Status == GRB.INFEASIBLE:
        return {
            "quantities": dict.fromkeys(Is, 0.0),
            "total_cost": 0.0,
            "shortfalls": dict.fromkeys(S, 0.0),
            "floor_met": False,
            "status": "infeasible",
        }
    else:
        return {
            "quantities": dict.fromkeys(Is, 0.0),
            "total_cost": 0.0,
            "shortfalls": dict.fromkeys(S, 0.0),
            "floor_met": False,
            "status": "error",
        }
