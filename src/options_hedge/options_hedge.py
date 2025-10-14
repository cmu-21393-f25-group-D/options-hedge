"""A simple example using Gurobi to verify the project setup."""

import gurobipy as gp
from gurobipy import GRB


def solve_simple_lp(
    x_max: float = 10.0, y_max: float = 10.0
) -> tuple[float, float, float]:
    """Solve a simple linear programming problem.

    Maximize: x + y
    Subject to:
        x <= x_max
        y <= y_max
        x, y >= 0

    Args:
        x_max: Upper bound for x
        y_max: Upper bound for y

    Returns:
        tuple[float, float, float]: Optimal x, y values and objective value
    """
    # Create a new model
    model = gp.Model("hello-world")

    # Create variables
    x = model.addVar(name="x")
    y = model.addVar(name="y")

    # Set objective: maximize x + y
    model.setObjective(x + y, GRB.MAXIMIZE)

    # Add constraints
    model.addConstr(x <= x_max, "c1")
    model.addConstr(y <= y_max, "c2")

    # Optimize
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return x.X, y.X, model.objVal
    else:
        raise RuntimeError("Model did not reach optimality")
