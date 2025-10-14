# Portfolio Insurance Optimization

This project implements a portfolio insurance strategy for retirees using put options on the S&P 500 index. It uses optimization techniques to find the most cost-effective combination of put options that protect a portfolio against downside risk while maintaining upside potential.

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
