#!/usr/bin/env python3
"""Inject environment variables into Jupyter kernel spec.

This script modifies a Jupyter kernel's kernel.json file to include
environment variables, ensuring they are available to the kernel subprocess.
"""

import json
import os
import sys


def inject_env_into_kernel(kernel_name: str, env_vars: dict) -> None:
    """Inject environment variables into a Jupyter kernel spec.

    Args:
        kernel_name: Name of the kernel (e.g., 'ci-env')
        env_vars: Dictionary of environment variables to inject
    """
    # Try multiple possible kernel locations
    possible_dirs = [
        os.path.expanduser(f"~/.local/share/jupyter/kernels/{kernel_name}"),
        os.path.expanduser(f"~/Library/Jupyter/kernels/{kernel_name}"),
    ]

    kernel_file = None
    for kernel_dir in possible_dirs:
        test_file = os.path.join(kernel_dir, "kernel.json")
        if os.path.exists(test_file):
            kernel_file = test_file
            break

    if kernel_file is None:
        print(f"Error: Kernel spec '{kernel_name}' not found in:", file=sys.stderr)
        for d in possible_dirs:
            print(f"  - {d}", file=sys.stderr)
        sys.exit(1)

    # Load existing kernel spec
    with open(kernel_file, "r") as f:
        spec = json.load(f)

    # Add or update env section
    if "env" not in spec:
        spec["env"] = {}
    spec["env"].update(env_vars)

    # Write updated spec
    with open(kernel_file, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"✓ Updated kernel spec at {kernel_file}")
    print(f"  Added env vars: {list(env_vars.keys())}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: inject_kernel_env.py <kernel_name> [ENV_VAR=value ...]",
            file=sys.stderr,
        )
        sys.exit(1)

    kernel_name = sys.argv[1]
    env_vars = {}

    # Parse ENV_VAR=value arguments
    for arg in sys.argv[2:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            env_vars[key] = value
        else:
            # Try to get from environment
            if arg in os.environ:
                env_vars[arg] = os.environ[arg]
            else:
                print(f"Warning: {arg} not in environment", file=sys.stderr)

    inject_env_into_kernel(kernel_name, env_vars)
