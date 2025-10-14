# Portfolio Insurance Optimization

[![CI](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml/badge.svg)](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cmu-21393-f25-group-D/options-hedge/main.svg)](https://results.pre-commit.ci/latest/github/cmu-21393-f25-group-D/options-hedge/main)
[![Jupyter Book](https://img.shields.io/badge/Jupyter%20Book-Docs-blue?logo=jupyter)](https://cmu-21393-f25-group-D.github.io/options-hedge)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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

The documentation is built using Jupyter Book and hosted on GitHub Pages at [https://cmu-21393-f25-group-D.github.io/options-hedge](https://cmu-21393-f25-group-D.github.io/options-hedge).

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

MIT License - see [LICENSE](LICENSE) file for details.

## Academic Integrity Notice

This project was developed as coursework for CMU 21-393 (Operations Research). While the code is open source under the MIT License, we strongly encourage students in similar courses to develop their own solutions. This repository is intended as a reference and learning resource, not a template for submission.

## Acknowledgments

This project addresses a real-world challenge facing millions of upcoming retirees. We're grateful for feedback from finance professionals and the open-source community.
