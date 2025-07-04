"""
Utility functions for the build system.

This module provides common functionality for build, test, and CI operations.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_project_root():
    """Get the absolute path to the project root directory."""
    # If the build.py is in the root, the root is the parent of this script
    if Path(__file__).name == "build.py":
        return Path(__file__).parent.resolve()

    # If we're in build_system dir, go up one level
    if Path(__file__).parent.name == "build_system":
        return Path(__file__).parent.parent.resolve()

    # Otherwise assume we're already in the root
    return Path(os.getcwd()).resolve()


def run_command(cmd, cwd=None, capture_output=False, env=None):
    """Run a shell command and return the result.

    Args:
        cmd: The command to run (string or list)
        cwd: Working directory (optional)
        capture_output: If True, capture and return stdout
        env: Environment variables dictionary (optional)

    Returns:
        The command output if capture_output is True, otherwise None

    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    try:
        if capture_output:
            result = subprocess.run(
                cmd, cwd=cwd, capture_output=True, text=True, check=True, env=env
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, cwd=cwd, check=True, env=env)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if capture_output and e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        raise


def ensure_dir_exists(path):
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)
    return path


def read_requirements():
    """Read requirements.txt file and return a list of packages."""
    project_root = get_project_root()
    requirements_path = project_root / "requirements.txt"

    if not requirements_path.exists():
        return []

    with open(requirements_path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]
