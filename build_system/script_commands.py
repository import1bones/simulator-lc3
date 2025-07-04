"""
Script Commands implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

import sys
import importlib.util
import os
from pathlib import Path

from build_utils import get_project_root


def run_script(args):
    """Run a Python script with the build environment configured.

    This ensures all scripts have access to the project modules and paths.

    Args:
        args: Command line arguments with the script path

    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()
    script_path = args.script

    print(f"Running script: {script_path}")

    # Check if script exists
    script_file = Path(script_path)
    if not script_file.is_absolute():
        script_file = project_root / script_path

    if not script_file.exists():
        print(f"Error: Script not found: {script_file}")
        return 1

    # Make sure the script directory and build directory are in sys.path
    script_dir = script_file.parent
    build_dir = project_root / "build"

    for path in [str(project_root), str(script_dir), str(build_dir)]:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variables if needed
    os.environ["LC3_PROJECT_ROOT"] = str(project_root)
    os.environ["LC3_BUILD_DIR"] = str(build_dir)

    try:
        # Run the script
        spec = importlib.util.spec_from_file_location("script", script_file)
        if spec is None:
            print(f"Error: Could not load script: {script_file}")
            return 1

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Call main function if it exists
        if hasattr(module, "main"):
            result = module.main()
            if isinstance(result, int):
                return result

        return 0
    except Exception as e:
        print(f"Error executing script: {e}")
        return 1
