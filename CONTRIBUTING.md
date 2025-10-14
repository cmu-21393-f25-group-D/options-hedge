# Contributing

Thank you for your interest in contributing to the Portfolio Insurance project! This guide explains the process for contributing to the project.

## Development Setup

1. Fork the repository and clone it:
   ```bash
   git clone https://github.com/your-username/portfolio-insurance.git
   cd portfolio-insurance
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   pip install uv
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   .venv\Scripts\activate     # On Windows
   uv pip install -e ".[dev]"
   ```

3. Install Gurobi:
   - Follow the installation instructions at [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)
   - Set up your Gurobi license

## Development Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```

2. Make your changes and ensure:
   - Code is formatted with black
   - Linting passes with ruff
   - Type hints are added and checked with mypy
   - Tests are added and pass with pytest

3. Run the test suite:
   ```bash
   pytest
   ```

4. Format code:
   ```bash
   black .
   ```

5. Check types:
   ```bash
   mypy src tests
   ```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure CI/CD pipeline passes
4. Request review from maintainers

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings in Google style
- Keep functions focused and short
- Add comments for complex algorithms

## Testing

- Write unit tests for new features
- Include edge cases
- Mock external dependencies
- Aim for high test coverage

## Documentation

- Update docstrings
- Add examples for new features
- Keep mathematical documentation clear
- Update Jupyter Book if needed