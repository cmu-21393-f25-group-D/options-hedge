# Contributing Guide

Thank you for your interest in contributing to the Portfolio Insurance Optimization project! This guide will help you get started.

## Getting Started

1. Make sure you've completed the [Installation Guide](installation.md)
2. Familiarize yourself with the project structure
3. Check out open issues or propose new features

## Development Workflow

### 1. Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/YOUR-USERNAME/options-hedge.git
   cd options-hedge
   ```

3. Add the upstream repository:

   ```bash
   git remote add upstream https://github.com/akhilkarra/options-hedge.git
   ```

### 2. Create a Branch

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:

- `feature/add-option-pricing`
- `fix/gurobi-constraint-bug`
- `docs/update-installation-guide`

### 3. Make Your Changes

Write your code following our style guidelines (see below). The pre-commit hooks will help enforce these automatically.

### 4. Run Tests

Before committing, make sure all tests pass:

```bash
uv run pytest
```

Add new tests for any new functionality:

```python
# tests/test_your_feature.py
def test_your_new_function():
    """Test that your function works correctly."""
    result = your_new_function(input_data)
    assert result == expected_output
```

### 5. Commit Your Changes

We use conventional commits for clear history:

```bash
git add .
git commit -m "feat: add option pricing module"
```

Commit message prefixes:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting changes (no code change)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

The pre-commit hooks will automatically:

- Format your code with Ruff
- Check for linting issues
- Run type checking with mypy
- Verify trailing whitespace

If the hooks make changes, you'll need to stage them and commit again:

```bash
git add .
git commit -m "feat: add option pricing module"
```

### 6. Push and Create a Pull Request

Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- A clear description of the changes
- Any related issue numbers
- Screenshots or examples if applicable

## Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications enforced by Ruff:

- **Line length**: 100 characters maximum
- **Imports**: Organized automatically by isort (part of Ruff)
- **Formatting**: Black-compatible style
- **Type hints**: Required for all function signatures

Example:

```python
from typing import List

import numpy as np
import pandas as pd

from options_hedge.models import Portfolio


def optimize_portfolio(
    portfolio_value: float,
    max_loss_percent: float,
    time_horizon: int = 365,
) -> dict[str, float]:
    """
    Find the optimal option hedge for a portfolio.

    Args:
        portfolio_value: Total portfolio value in dollars
        max_loss_percent: Maximum acceptable loss as a decimal (e.g., 0.10 for 10%)
        time_horizon: Protection period in days (default: 365)

    Returns:
        Dictionary containing optimal hedge details including cost and positions
    """
    # Implementation here
    pass
```

### Documentation Style

Use Google-style docstrings:

```python
def example_function(param1: int, param2: str) -> bool:
    """
    Brief description of what the function does.

    Longer description if needed, explaining the algorithm,
    assumptions, or other important details.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is negative
    """
    pass
```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure (e.g., `src/models.py` → `tests/test_models.py`)
- Use descriptive test names that explain what's being tested

```python
import pytest

from options_hedge.models import Portfolio


def test_portfolio_initialization():
    """Test that Portfolio initializes with correct default values."""
    portfolio = Portfolio(value=1_000_000)
    assert portfolio.value == 1_000_000


def test_portfolio_raises_error_on_negative_value():
    """Test that Portfolio raises ValueError for negative values."""
    with pytest.raises(ValueError, match="Portfolio value must be positive"):
        Portfolio(value=-1000)
```

### Running Tests

Run all tests:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=html
```

Run specific tests:

```bash
uv run pytest tests/test_models.py::test_portfolio_initialization
```

## Development Commands

Here are the common commands you'll use:

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Fix auto-fixable linting issues
uv run ruff check --fix .

# Type checking
uv run mypy src tests

# Run all pre-commit checks
uv run pre-commit run --all-files

# Build documentation
cd docs
uv run jupyter-book build .
```

## Project Structure

```text
options-hedge/
├── src/                    # Source code
│   ├── __init__.py
│   ├── models.py          # Data models
│   ├── optimization.py    # Optimization logic
│   └── data.py            # Data fetching and processing
├── tests/                 # Unit tests
│   ├── test_models.py
│   └── test_optimization.py
├── examples/              # Example scripts
├── notebooks/             # Jupyter notebooks for analysis
├── docs/                  # Documentation (Jupyter Book)
│   └── source/
└── pyproject.toml         # Project configuration
```

## Questions or Problems?

- Check existing issues on GitHub
- Ask in pull request comments
- Reach out to the team members

## Code Review Process

All pull requests require:

1. Passing CI/CD checks (tests, linting, type checking)
2. Review from at least one team member
3. Updated documentation if applicable
4. Tests for new functionality
