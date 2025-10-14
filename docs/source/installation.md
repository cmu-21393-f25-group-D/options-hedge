# Installation Guide

This guide will walk you through setting up the portfolio insurance optimization project on your local machine.

## Prerequisites

- Python 3.10 or higher
- Git
- A Gurobi license (free academic licenses available)

## Step-by-Step Installation

### 1. Install uv Package Manager

We use `uv` as our Python package manager because it ensures consistent package versions across all team members, preventing "it works on my machine" issues.

```bash
python -m pip install --upgrade pip
pip install uv
```

### 2. Clone the Repository

```bash
git clone https://github.com/cmu-21393-f25-group-D/options-hedge.git
cd options-hedge
```

### 3. Create a Virtual Environment

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
```

### 4. Install the Package

For basic usage:

```bash
uv pip install -e .
```

For development (includes testing, formatting, and linting tools):

```bash
uv pip install -e ".[dev]"
```

For Jupyter notebook support:

```bash
uv pip install -e ".[jupyter]"
```

For documentation building:

```bash
uv pip install -e ".[docs]"
```

For everything:

```bash
uv pip install -e ".[all]"
```

### 5. Install Gurobi

Gurobi is a commercial optimization solver that offers free academic licenses.

1. Visit the [Gurobi Installation Guide](https://www.gurobi.com/documentation/quickstart.html)
2. Download and install Gurobi for your operating system
3. Obtain an academic license from [Gurobi Academic Licensing](https://www.gurobi.com/academia/academic-program-and-licenses/)
4. Activate your license following the instructions

### 6. Install Pre-commit Hooks (For Contributors)

If you plan to contribute code, install pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

These hooks will automatically:

- Format your code with Ruff
- Check for style issues
- Run type checking with mypy
- Verify trailing whitespace and file endings

### 7. Verify Installation

Run the following command to verify everything is set up correctly:

```bash
uv run python -c "import options_hedge; print('Package successfully installed!')"
```

You should also verify Gurobi is working:

```bash
uv run python -c "import gurobipy; print(f'Gurobi version: {gurobipy.gurobi.version()}')"
```

## Troubleshooting

### Virtual Environment Issues

If you have trouble activating the virtual environment:

- **Unix/macOS**: Make sure you're using `source .venv/bin/activate`
- **Windows**: Try `.venv\Scripts\activate.bat` if PowerShell doesn't work

### Gurobi License Issues

If Gurobi can't find your license:

1. Make sure you've activated the license using `grbgetkey YOUR-LICENSE-KEY`
2. Check that the `gurobi.lic` file exists in your home directory
3. Set the `GRB_LICENSE_FILE` environment variable if needed

### Package Installation Errors

If you encounter dependency conflicts:

1. Delete the virtual environment: `rm -rf .venv`
2. Recreate it: `uv venv`
3. Reinstall with fresh cache: `uv pip install --no-cache -e ".[dev]"`

## Next Steps

Once installation is complete:

1. Explore the `examples/` and `notebooks/` directories for usage examples
2. Read the [Contributing Guide](contributing.md) to learn how to contribute
3. Review the [Project Motivation](motivation.md) to understand the problem we're solving
