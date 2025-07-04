"""
Clean commands for the LC-3 Simulator.

This module implements the 'clean' command functionality.
"""

import os
import subprocess
import shutil
from pathlib import Path

from build_utils import get_project_root


def clean_project(args):
    """Clean the LC-3 simulator project.

    Args:
        args: Command line arguments

    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()

    # List of directories to clean
    dirs_to_clean = [
        project_root / "build",
        project_root / "__pycache__",
        project_root / ".pytest_cache",
        project_root / ".mypy_cache",
        project_root / "htmlcov",
    ]

    # Add all __pycache__ directories
    for root, dirs, files in os.walk(project_root):
        for dir in dirs:
            if dir == "__pycache__":
                dirs_to_clean.append(Path(root) / dir)

    # Clean additional directories if --all is specified
    if args.all:
        dirs_to_clean.extend(
            [
                project_root / "reports",
                project_root / "data" / "temp",
            ]
        )

    # Clean each directory
    cleaned = False
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"Removing {dir_path}")
            try:
                shutil.rmtree(dir_path)
                cleaned = True
            except Exception as e:
                print(f"Failed to remove {dir_path}: {e}")

    # Clean .coverage files
    for file in project_root.glob(".coverage*"):
        print(f"Removing {file}")
        file.unlink()
        cleaned = True

    if not cleaned:
        print("Nothing to clean.")
    else:
        print("Clean completed.")

    return 0
