from gurobipy import GRB
import gurobipy as gp


def solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test"):
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


def test_case_1():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 1")
    return None


def test_case_2A():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 2A (L=0.10)")
    return None


def test_case_2B():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 2B (L=0.30)")
    return None


def test_case_3():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 3")
    return None


def test_case_4():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 4 (Q=1000)")
    return None


def test_case_5():
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 5")
    return None


def test_case_6():
    """
    Test Case 6 – More scenarios (stress testing)
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

    solve_portfolio_insurance(Is, S, K, p, Q, r, L, name="Test Case 6")
    return None


if __name__ == "__main__":
    test_case_1()
    test_case_2A()
    test_case_2B()
    test_case_3()
    test_case_4()
    test_case_5()
    test_case_6()
