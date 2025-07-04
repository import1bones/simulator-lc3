"""
LC-3 Simulator Test Environment Configuration

This module handles test environment setup, verification, and configuration.
"""

import os
import sys
import subprocess
import pytest
from pathlib import Path

# Make sure we can import from parent directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_project_root():
    """Get the project root directory."""
    return PROJECT_ROOT


def get_test_programs_dir():
    """Get the directory containing test programs."""
    return PROJECT_ROOT / "test_programs"


def run_build_command(clean=False, python_bindings=True):
    """Run the build command to ensure simulator is compiled.
    
    Args:
        clean: Whether to clean before building
        python_bindings: Whether to build Python bindings
        
    Returns:
        True if build succeeds, False otherwise
    """
    try:
        cmd = [sys.executable, str(PROJECT_ROOT / "build.py"), "build"]
        
        if clean:
            cmd.append("--clean")
        
        if python_bindings:
            cmd.append("--python-bindings")
        
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def verify_test_environment():
    """Verify that the test environment is set up correctly.
    
    Returns:
        True if environment is valid, False otherwise
    """
    # Check if build directory exists
    build_dir = PROJECT_ROOT / "build"
    if not build_dir.exists():
        print("Build directory not found. Running build...")
        if not run_build_command():
            return False
    
    # Check if Python bindings are available
    try:
        import lc3_simulator
        return True
    except ImportError:
        print("LC-3 simulator Python bindings not found.")
        print("Running build with Python bindings...")
        return run_build_command(python_bindings=True)


def setup_test_environment():
    """Set up the test environment for LC-3 simulator tests.
    
    This function is called by conftest.py to ensure proper setup.
    """
    # Verify environment
    if not verify_test_environment():
        pytest.fail("Failed to set up test environment")
    
    # Add build directory to Python path for importing bindings
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        sys.path.insert(0, str(build_dir))


# Run environment setup if the module is executed directly
if __name__ == "__main__":
    if verify_test_environment():
        print("Test environment verified successfully.")
        sys.exit(0)
    else:
        print("Test environment verification failed.")
        sys.exit(1)
