# Hello World Example

This is a simple demonstration of using Gurobi optimization in Python. We'll solve a basic linear programming problem to verify that our project setup works correctly.

## Problem Description

We're solving a very simple maximization problem:

```
maximize: x + y
subject to:
    x ≤ x_max
    y ≤ y_max
    x, y ≥ 0
```

This trivial problem lets us verify:
1. Gurobi installation and licensing
2. Project dependencies
3. Testing framework
4. CI/CD pipeline

## Usage

```python
from options_hedge import solve_simple_lp

# Solve with default bounds (10.0)
x, y, obj = solve_simple_lp()
print(f"Optimal solution: x={x}, y={y}, objective={obj}")

# Solve with custom bounds
x, y, obj = solve_simple_lp(x_max=5.0, y_max=7.0)
print(f"Optimal solution: x={x}, y={y}, objective={obj}")
```

## Next Steps

1. Design the portfolio insurance model
2. Implement option pricing functions
3. Create the optimization model
4. Add visualization and analysis tools
5. Write documentation and examples
