#!/usr/bin/env python3
"""Check that notebooks have been executed (have outputs).

For notebooks in docs/, we want them pre-executed with outputs committed.
This prevents incomplete/empty notebooks from being published.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check_notebook_has_outputs(notebook_path: Path) -> bool:
    """Check if notebook has at least one cell with outputs."""
    try:
        with open(notebook_path, encoding="utf-8") as f:
            nb = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {notebook_path} is not valid JSON")
        return False

    cells = nb.get("cells", [])
    if not cells:
        print(f"Error: {notebook_path} has no cells")
        return False

    # Check if any code cells have outputs
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    if not code_cells:
        # No code cells is OK (markdown-only notebook)
        return True

    cells_with_outputs = [c for c in code_cells if c.get("outputs")]

    if not cells_with_outputs:
        print(f"Error: {notebook_path} has no executed cells (no outputs)")
        print("Execute the notebook locally before committing:")
        print(f"  jupyter nbconvert --execute --inplace {notebook_path}")
        return False

    output_ratio = len(cells_with_outputs) / len(code_cells)
    if output_ratio < 0.5:
        print(
            f"Warning: {notebook_path} has only "
            f"{len(cells_with_outputs)}/{len(code_cells)} cells with outputs"
        )
        print("Consider fully executing the notebook before committing.")
        # Allow but warn
        return True

    print(
        f"✓ {notebook_path} has outputs "
        f"({len(cells_with_outputs)}/{len(code_cells)} cells)"
    )
    return True


def main() -> int:
    """Check all provided notebook files."""
    if len(sys.argv) < 2:
        print(
            "Usage: check_notebook_executed.py <notebook1.ipynb> [notebook2.ipynb ...]"
        )
        return 1

    all_good = True
    for notebook_path in sys.argv[1:]:
        path = Path(notebook_path)
        if not path.exists():
            print(f"Error: {notebook_path} does not exist")
            all_good = False
            continue

        if not check_notebook_has_outputs(path):
            all_good = False

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
