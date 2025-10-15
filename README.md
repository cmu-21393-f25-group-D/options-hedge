# Portfolio Insurance Optimization

[![CI](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml/badge.svg)](https://github.com/cmu-21393-f25-group-D/options-hedge/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cmu-21393-f25-group-D/options-hedge/main.svg)](https://results.pre-commit.ci/latest/github/cmu-21393-f25-group-D/options-hedge/main)
[![Jupyter Book](https://img.shields.io/badge/Jupyter%20Book-Docs-blue?logo=jupyter)](https://cmu-21393-f25-group-D.github.io/options-hedge)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **A modern solution to the retirement dilemma**: How can retirees protect their portfolios from market crashes while maintaining growth potential?

This project uses operations research and optimization to find cost-effective combinations of S&P 500 put options that provide downside protection while preserving upside potential.

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

We use optimization to determine:

1. What is the optimal protection level for retirement portfolios?
2. What is the cheapest combination of options to achieve that protection?

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

This project was developed as coursework for CMU 21-393 (Operations Research). While the code is open source under the MIT License, we strongly encourage students in similar courses to develop their own solutions. This repository is intended as a reference and learning resource, not a template for submission.
