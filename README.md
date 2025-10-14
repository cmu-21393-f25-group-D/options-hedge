# Portfolio Insurance Optimization

A modern solution to the retirement dilemma: How can retirees protect their portfolios from market crashes while maintaining growth potential?

This project uses operations research and optimization techniques to find the most cost-effective combination of S&P 500 put options that provide downside protection while preserving upside potential.

## What is Portfolio Insurance?

**Portfolio insurance** is a risk management strategy that uses financial derivatives (in our case, put options) to limit losses from declining asset prices. Think of it like home insurance for your investment portfolio:

- You pay a premium (the cost of the options)
- If nothing bad happens (market goes up), you lose the premium but your portfolio gains value
- If disaster strikes (market crashes), the insurance pays out to cover your losses

By strategically purchasing put options on the S&P 500 index, we can create a "floor" that limits maximum portfolio losses while allowing participation in market gains.

## The Problem We're Solving

### The Retirement Dilemma

Upcoming retirees face a difficult trade-off:

1. **Stay in stocks**: Maintain growth potential and inflation protection, but risk catastrophic losses right when income stops
2. **Move to bonds**: Preserve capital but earn minimal returns in today's low interest-rate environment

With Baby Boomers entering retirement en masse, trillions of dollars are at risk. Traditional asset allocation strategies may no longer provide adequate protection.

### Our Solution

We use optimization to answer: **"What is the cheapest combination of put options needed to guarantee a portfolio won't lose more than X% over a given period?"**

The optimization model:

- **Minimizes**: Total cost of purchasing options
- **While ensuring**: Portfolio is protected against a range of potential market scenarios
- **Allows**: Full participation in market upside

## Project Team

- Akhil Karra
- Zoe Xu
- Vivaan Shroff
- Wendy Wang

## Installation

1. Install uv (Python package manager that also stores versions of packages; makes sure nothing breaks due to mismatched versions):

   ```bash
   python -m pip install --upgrade pip
   pip install uv
   ```

1. Create and activate a virtual environment:

   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   .venv\Scripts\activate     # On Windows
   ```

1. Install the package with development dependencies:

   ```bash
   uv pip install -e ".[dev]"
   ```

1. Install Gurobi:

   Follow the instructions at [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)

1. Install and configure pre-commit hooks:

   ```bash
   pre-commit install
   ```

1. Verify installation:

   ```bash
   uv run python -c "import options_hedge; print('Package successfully installed!')"
   ```

## Code Quality

This project uses pre-commit hooks to maintain code quality. When you commit changes, the following checks are automatically run:

- Code formatting with Ruff
- Style and error checks with Ruff
- Type checking with mypy
- Other checks like trailing whitespace and file endings

If any issues are found:

- For formatting issues: The hooks will automatically fix them
- For other issues: The commit will be blocked until you fix them

After a hook makes automated fixes, you'll need to stage the changes and commit again.

## Usage

See the `examples/` directory for usage examples and the `notebooks/` directory for detailed analysis.

## Development

- Run tests: `uv run pytest`
- Format code: `uv run black .`
- Run linter: `uv run ruff check .`
- Type check: `uv run mypy src tests`
- Run all checks: `uv run pre-commit run --all-files`

## Documentation

The documentation is built using Jupyter Book and hosted on GitHub Pages at [https://akhilkarra.github.io/options-hedge](https://akhilkarra.github.io/options-hedge).

To build locally:

```bash
cd docs
uv run jupyter-book build .
```

## Optional Dependencies

The package can be installed with different sets of dependencies:

```bash
# Basic installation (core functionality only)
uv pip install .

# With development tools (black, ruff, pytest, etc.)
uv pip install -e ".[dev]"

# With Jupyter support (notebooks, plotting, etc.)
uv pip install -e ".[jupyter]"

# With documentation tools
uv pip install -e ".[docs]"

# With all dependencies
uv pip install -e ".[all]"
```

## Development Status

This project is under active development. Current focus areas:

1. Integration with market data providers (e.g., Yahoo Finance, Alpha Vantage) for real-time option prices and market data
2. Optimization model implementation using Gurobi
3. Scenario generation for market conditions
4. Visualization and analysis tools

**Note**: We use market data providers for option pricing rather than implementing pricing models (e.g., Black-Scholes), which allows us to focus on the optimization and hedging strategy while using real market prices.

## License

MIT License - see LICENSE file for details

## Acknowledgments

This project addresses a real-world challenge facing millions of upcoming retirees. We're grateful for feedback from finance professionals and the open-source community.
