"""
Build commands for the LC-3 Simulator.

This module implements the 'build' command functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

from build_utils import run_command, get_project_root, ensure_dir_exists


def build_project(args):
    """Build the LC-3 simulator project.
    
    Args:
        args: Command line arguments
        
    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()
    build_dir = project_root / "build"
    
    # Clean if requested
    if args.clean and build_dir.exists():
        print("Cleaning build directory...")
        run_command(["rm", "-rf", str(build_dir)])
    
    # Ensure build directory exists
    ensure_dir_exists(build_dir)
    
    # Prepare CMake arguments
    cmake_args = [
        "cmake",
        "-S", str(project_root),
        "-B", str(build_dir),
    ]
    
    # Add build type
    if args.debug:
        cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
    else:
        cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])
    
    # Add Python bindings option
    if args.python_bindings:
        cmake_args.extend(["-DBUILD_PYTHON_BINDINGS=ON"])
    else:
        cmake_args.extend(["-DBUILD_PYTHON_BINDINGS=OFF"])
    
    # Add pipeline extensions option
    if args.pipeline:
        cmake_args.extend(["-DBUILD_PIPELINE_EXTENSIONS=ON"])
    else:
        cmake_args.extend(["-DBUILD_PIPELINE_EXTENSIONS=OFF"])
    
    # Run CMake configure
    try:
        run_command(cmake_args)
        
        # Run build
        run_command(["cmake", "--build", str(build_dir)])
        
        print("Build completed successfully.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return 1
