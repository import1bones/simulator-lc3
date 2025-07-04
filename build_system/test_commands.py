"""
Test runner functionality for the LC-3 Simulator.

This module implements the 'test' command functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

from build_utils import run_command, get_project_root


def run_test_suite(args):
    """Run the test suite for the LC-3 simulator.
    
    Args:
        args: Command line arguments
        
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
