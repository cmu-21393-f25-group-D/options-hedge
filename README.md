# Portfolio Insurance Optimization

[![CI](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml/badge.svg)](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cmu-21393-f25-group-D/options-hedge/main.svg)](https://results.pre-commit.ci/latest/github/cmu-21393-f25-group-D/options-hedge/main)
[![Coverage](https://raw.githubusercontent.com/cmu-21393-f25-group-D/options-hedge/main/coverage.svg)](https://github.com/cmu-21393-f25-group-D/options-hedge)
[![Jupyter Book](https://img.shields.io/badge/Jupyter%20Book-Docs-blue?logo=jupyter)](https://cmu-21393-f25-group-D.github.io/options-hedge)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **A modern solution to the retirement dilemma**: How can retirees protect their portfolios from market crashes while maintaining growth potential?

This project uses operations research and optimization to find cost-effective combinations of S&P 500 put options that provide downside protection while preserving upside potential.

## ⚠️ IMPORTANT DISCLAIMER

**This is an educational project developed for CMU 21-393 (Operations Research II). NOT suitable for actual investment decisions.**

**Key limitations and simplifying assumptions:**

- **Simplified option pricing:** Uses intrinsic value only (no Black-Scholes, no Greeks, no time decay, no implied volatility surface)
- **Free-tier data:** Uses yfinance instead of professional data vendors (subject to survivorship bias and data quality issues)
- **Educational focus:** Designed to demonstrate OR concepts, not production portfolio management

**Always consult a licensed financial advisor for real investment decisions.**

**What this project demonstrates:**

- ✅ Linear programming for cost minimization under portfolio floor constraints
- ✅ VIX-adaptive hedging strategies
- ✅ Transaction cost modeling (bid-ask spreads for options)
- ✅ Simulation framework with multiple hedging strategies
- ✅ Software engineering best practices (testing, type hints, CI/CD)
- ✅ Integration of optimization with financial simulations

📖 **[Read the full documentation](https://cmu-21393-f25-group-D.github.io/options-hedge)**

## Quick Start

```bash
# Install uv package manager
pip install uv

# Clone and setup
git clone https://github.com/cmu-21393-f25-group-D/options-hedge.git
cd options-hedge
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with development tools
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

📚 **[Full installation guide](https://cmu-21393-f25-group-D.github.io/options-hedge/installation.html)**

## The Problem

With the U.S. population aged 65+ projected to nearly double from 52 million (2018) to 95 million (2060), millions of retirees face a critical challenge:

- **Stay in stocks?** Risk catastrophic losses right when income stops
- **Move to bonds?** Accept minimal returns and lose purchasing power to inflation

We use **linear programming** to determine:

1. What is the optimal protection level for retirement portfolios? (VIX-adaptive floor)
2. What is the cheapest combination of put options to achieve that protection? (LP cost minimization)

**Key OR contribution:** `vix_floor_lp.py` implements a scenario-free linear program that minimizes premium costs subject to portfolio floor constraints, with adaptive floor levels based on market volatility (VIX) and portfolio beta.

🔍 **[Explore the full motivation and problem statement](https://cmu-21393-f25-group-D.github.io/options-hedge/motivation.html)**

## Project Team

- Akhil Karra
- Zoe Xu
- Vivaan Shroff
- Wendy Wang

## Contributing

We welcome contributions! Please see our [contributing guide](https://cmu-21393-f25-group-D.github.io/options-hedge/contributing.html) for:

- Development workflow
- Code style guidelines
- Testing requirements
- Pull request process

## Development Commands

```bash
# Run tests
uv run pytest

# Code quality checks
uv run ruff check .
uv run mypy src tests
uv run pre-commit run --all-files

# Build documentation
cd docs && uv run jupyter-book build .
```

## Documentation

Complete documentation is available at **[cmu-21393-f25-group-D.github.io/options-hedge](https://cmu-21393-f25-group-D.github.io/options-hedge)**

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Academic Integrity Notice

This project was developed as coursework for CMU 21-393 (Operations Research). While the code is open source under the MIT License, we strongly encourage students in similar courses to develop their own solutions.

**This repository demonstrates:**

- How to apply linear programming to real-world portfolio problems
- Software engineering practices for OR projects (testing, type hints, documentation)
- Integration of optimization with financial simulations

**Use this as inspiration, not a template.** The learning comes from wrestling with the problem yourself.
