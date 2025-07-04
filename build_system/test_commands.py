"""
Test runner functionality for the LC-3 Simulator.

This module implements the 'test' command functionality.
It delegates to the centralized test runner in tests/test_runner.py.
"""

import sys
import os
from pathlib import Path

from build_utils import get_project_root


def run_test_suite(args):
    """Run the test suite for the LC-3 simulator.
    
    Args:
        args: Command line arguments
        
    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()
    test_runner_path = project_root / "tests" / "test_runner.py"
    
    # Check if test runner exists
    if not test_runner_path.exists():
        print(f"Error: Test runner not found at {test_runner_path}")
        return 1
    
    # Import the test runner
    sys.path.insert(0, str(project_root / "tests"))
    try:
        # Import test runner dynamically
        import test_runner
        return test_runner.run_test_suite(args)
    except ImportError as e:
        print(f"Error importing test runner: {e}")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1
