import gurobipy as gp
from gurobipy import GRB


def solve_fixed_floor_lp(
    Is: list, S: list, K: dict, p: dict, Q: float, r: dict, L: float, name: str = "Test"
) -> None:
    print("\n" + "=" * 60)
    print(f"  {name}")
    print("=" * 60)

    m = gp.Model(f"portfolio_insurance_{name}")
    m.Params.OutputFlag = 0

    V = {s: Q * (1.0 + r[s]) for s in S}
    F = Q * (1.0 - L)

    Payoff = {(i, s): max(0.0, K[i] - V[s]) for i in Is for s in S}

    x = m.addVars(Is, lb=0.0, name="x")
    z = m.addVars(S, lb=0.0, name="z")

    m.setObjective(gp.quicksum(p[i] * x[i] for i in Is), GRB.MINIMIZE)

    for s in S:
        m.addConstr(
            V[s] + gp.quicksum(Payoff[i, s] * x[i] for i in Is) + z[s] >= F,
            name=f"downside_protection[{s}]",
        )

    m.optimize()

    if m.Status == GRB.OPTIMAL:
        print(f"Objective (min total premium) = {m.ObjVal:.4f}")
        print("\nOption positions x_i:")
        for i in Is:
            print(f"  x[{i}] = {x[i].X:.4f}")

        print("\nShortfalls z_s (scenario slacks):")
        for s in S:
            print(f"  z[{s}] = {z[s].X:.4f}")

        print("\nScenario portfolio values without options (V_s) and floor F:")
        for s in S:
            print(f"  V[{s}] = {V[s]:.2f}")
        print(f"\n  Floor F = {F:.2f}")
    else:
        print(f"Model ended with status {m.Status}")

    return None
