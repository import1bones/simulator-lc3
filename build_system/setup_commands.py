"""
Setup commands for the LC-3 Simulator.

This module implements the 'setup' command functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

from build_utils import run_command, get_project_root, read_requirements


def setup_project(args):
    """Set up the development environment for the LC-3 simulator.
    
    Args:
        args: Command line arguments
        
    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    try:
        # Upgrade pip
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install from requirements.txt if it exists
        requirements = read_requirements()
        if requirements:
            run_command([sys.executable, "-m", "pip", "install", "-r", 
                         str(project_root / "requirements.txt")])
        else:
            # Install minimal dependencies
            run_command([sys.executable, "-m", "pip", "install", 
                         "pytest", "pytest-cov", "pybind11"])
        
        print("Python dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Python dependencies: {e}")
        return 1
    
    # If --deps was specified, exit now
    if args.deps:
        return 0
    
    # Build the project
    print("Building the project...")
    try:
        from build_commands import build_project
        build_args = type("Args", (), {
            "clean": False,
            "python_bindings": True,
            "pipeline": True,
            "debug": False
        })
        build_project(build_args)
    except Exception as e:
        print(f"Failed to build the project: {e}")
        return 1
    
    print("Setup completed successfully.")
    return 0
