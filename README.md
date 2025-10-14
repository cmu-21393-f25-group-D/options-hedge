# Portfolio Insurance Optimization

This project implements a portfolio insurance strategy for retirees using options on the S&P 500 index. It uses optimization techniques to find the most cost-effective combination of put options that protect a portfolio against downside risk while maintaining upside potential.

## Features

- Portfolio insurance strategy using S&P 500 put options
- Optimization model to minimize option costs while ensuring downside protection
- Analysis of different strike prices and expiration dates
- Visualization of strategy performance under various market scenarios
- Back-testing capabilities using historical data

## Installation

1. Install uv (Python package manager):
```bash
python -m pip install --upgrade pip
pip install uv
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
```

3. Install the package with development dependencies:
```bash
uv pip install -e ".[dev]"
```

4. Install Gurobi:
Follow the instructions at [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)

5. Verify installation:
```bash
uv run python -c "import options_hedge; print('Package successfully installed!')"
```

## Usage

See the `examples/` directory for usage examples and the `notebooks/` directory for detailed analysis.

## Development

- Run tests: `uv run pytest`
- Format code: `uv run black .`
- Run linter: `uv run ruff check .`
- Type check: `uv run mypy src tests`
- Run all checks: `uv run pre-commit run --all-files`

## Documentation

The documentation is built using Jupyter Book and hosted on GitHub Pages. To build locally:

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

## License

MIT License - see LICENSE file for details