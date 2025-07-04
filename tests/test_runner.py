"""
Test Runner implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

"""
LC-3 Simulator Test Runner

This module provides functions for running the LC-3 simulator test suite.
It is used by the build system's 'test' command.
"""

import os
import sys
import subprocess
from pathlib import Path

# Make sure we can import from parent directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import build system utilities
try:
    from build_system.build_utils import run_command
except ImportError:
    # Fallback implementation if build_utils is not available
    def run_command(cmd, cwd=None, capture_output=False):
        """Run a shell command and return the result."""
        print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

        try:
            if capture_output:
                result = subprocess.run(
                    cmd, cwd=cwd, capture_output=True, text=True, check=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(cmd, cwd=cwd, check=True)
                return None
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            raise


def get_project_root():
    """Get the project root directory."""
    return PROJECT_ROOT


def run_test_suite(args):
    """Run the test suite for the LC-3 simulator.

    Args:
        args: Command line arguments with the following attributes:
            - fast: Run tests in parallel
            - all: Run all tests
            - unit: Run unit tests only
            - integration: Run integration tests only
            - coverage: Generate coverage report
            - category: Run specific test category

    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()

    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]

    # Add options based on arguments
    if args.fast:
        pytest_cmd.append("-xvs")
    else:
        pytest_cmd.append("-v")

    # Add test selection based on arguments
    if args.all:
        # Run all tests
        pass  # No additional arguments needed
    elif args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    elif args.category:
        # Run specific test category
        pytest_cmd.append(f"tests/test_{args.category}.py")
    else:
        # Default: run basic tests
        pytest_cmd.append("tests/test_basic.py")

    # Add coverage options
    if args.coverage:
        pytest_cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    # Run the tests
    try:
        run_command(pytest_cmd, cwd=project_root)
        print("Tests completed successfully.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
        return 1


if __name__ == "__main__":
    # If called directly, provide a simple command-line interface
    import argparse

    parser = argparse.ArgumentParser(description="Run LC-3 Simulator tests")
    parser.add_argument("--fast", action="store_true", help="Run tests in parallel")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--category", type=str, help="Run specific test category")

    args = parser.parse_args()
    sys.exit(run_test_suite(args))
