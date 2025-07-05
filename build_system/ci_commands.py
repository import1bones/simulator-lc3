"""
Ci Commands implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

"""
CI commands for the LC-3 Simulator.

This module implements the 'ci' command functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

from build_utils import run_command, get_project_root


def run_ci(args):
    """Run a CI workflow locally.

    Args:
        args: Command line arguments

    Returns:
        0 on success, non-zero on error
    """
    project_root = get_project_root()

    workflow = args.workflow
    print(f"Running CI workflow: {workflow}")

    if workflow == "default":
        # Run the default CI workflow
        return run_default_workflow()
    elif workflow == "nightly":
        # Run the nightly build workflow
        return run_nightly_workflow()
    elif workflow == "cross-platform":
        # Run cross-platform checks
        return run_cross_platform_workflow()
    elif workflow == "benchmark":
        # Run comprehensive benchmarking
        return run_benchmark_workflow()
    else:
        print(f"Unknown workflow: {workflow}")
        print("Available workflows: default, nightly, cross-platform, benchmark")
        return 1


def run_default_workflow():
    """Run the default CI workflow."""
    try:
        # Step 1: Install dependencies
        print("Step 1: Installing dependencies...")
        from setup_commands import setup_project

        setup_args = type("Args", (), {"deps": True})
        setup_project(setup_args)

        # Step 2: Build the project
        print("Step 2: Building the project...")
        from build_commands import build_project

        build_args = type(
            "Args",
            (),
            {"clean": True, "python_bindings": True, "pipeline": True, "debug": False},
        )
        build_project(build_args)

        # Step 3: Run tests
        print("Step 3: Running tests...")
        from test_commands import run_test_suite

        test_args = type(
            "Args",
            (),
            {
                "all": False,
                "fast": True,
                "unit": False,
                "integration": False,
                "coverage": True,
                "category": None,
            },
        )
        run_test_suite(test_args)

        print("CI workflow completed successfully.")
        return 0
    except Exception as e:
        print(f"CI workflow failed: {e}")
        return 1


def run_nightly_workflow():
    """Run the nightly build workflow."""
    try:
        # Step 1: Full clean
        print("Step 1: Cleaning everything...")
        from clean_commands import clean_project

        clean_args = type("Args", (), {"all": True})
        clean_project(clean_args)

        # Step 2: Full build with all options
        print("Step 2: Building with all options...")
        from build_commands import build_project

        build_args = type(
            "Args",
            (),
            {"clean": True, "python_bindings": True, "pipeline": True, "debug": True},
        )
        build_project(build_args)

        # Step 3: Run all tests
        print("Step 3: Running all tests...")
        from test_commands import run_test_suite

        test_args = type(
            "Args",
            (),
            {
                "all": True,
                "fast": False,
                "unit": False,
                "integration": False,
                "coverage": True,
                "category": None,
            },
        )
        run_test_suite(test_args)

        print("Nightly workflow completed successfully.")
        return 0
    except Exception as e:
        print(f"Nightly workflow failed: {e}")
        return 1


def run_cross_platform_workflow():
    """Run cross-platform checks.

    This function detects the platform and runs appropriate checks.
    """
    try:
        import platform

        system = platform.system()
        print(f"Running cross-platform checks on {system}")

        # Step 1: Install dependencies
        print("Step 1: Installing dependencies...")
        from setup_commands import setup_project

        setup_args = type("Args", (), {"deps": True})
        setup_project(setup_args)

        # Step 2: Build the project with platform-specific options
        print("Step 2: Building with platform-specific options...")
        from build_commands import build_project

        # Set different build options based on platform
        python_bindings = True
        pipeline_enabled = True
        debug_mode = False

        if system == "Windows":
            # Windows-specific settings
            print("Applying Windows-specific build settings")
        elif system == "Darwin":
            # macOS-specific settings
            print("Applying macOS-specific build settings")
        else:
            # Linux/other settings
            print("Applying Linux/default build settings")

        build_args = type(
            "Args",
            (),
            {
                "clean": True,
                "python_bindings": python_bindings,
                "pipeline": pipeline_enabled,
                "debug": debug_mode,
            },
        )
        build_project(build_args)

        # Step 3: Run basic tests (platform-independent subset)
        print("Step 3: Running basic platform tests...")
        from test_commands import run_test_suite

        test_args = type(
            "Args",
            (),
            {
                "all": False,
                "fast": True,
                "unit": False,
                "integration": False,
                "coverage": False,
                "category": "basic",
            },
        )
        run_test_suite(test_args)

        print(f"Cross-platform workflow completed successfully on {system}")
        return 0
    except Exception as e:
        print(f"Cross-platform workflow failed: {e}")
        return 1


def run_benchmark_workflow():
    """Run comprehensive benchmark workflow.

    This workflow focuses on performance analysis and benchmarking.
    """
    try:
        import time

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        print(f"Running benchmark workflow ({timestamp})...")

        # Step 1: Install dependencies
        print("Step 1: Installing dependencies...")
        from setup_commands import setup_project

        setup_args = type("Args", (), {"deps": True})
        setup_project(setup_args)

        # Step 2: Build optimized version
        print("Step 2: Building optimized version...")
        from build_commands import build_project

        build_args = type(
            "Args",
            (),
            {
                "clean": True,
                "python_bindings": True,
                "pipeline": True,
                "debug": False,
            },
        )
        build_project(build_args)

        # Step 3: Run performance benchmarks
        print("Step 3: Running performance benchmarks...")
        from script_commands import run_script

        # Ensure directories exist
        reports_dir = Path("reports")
        data_dir = Path("data")
        reports_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)

        # Run benchmarks
        benchmark_script = "scripts/benchmark_programs.py"
        benchmark_args = type("Args", (), {"script": benchmark_script})
        run_script(benchmark_args)

        # Step 4: Run ISA analysis
        print("Step 4: Running ISA analysis...")
        isa_script = "analysis/enhanced_isa_analysis.py"
        isa_args = type("Args", (), {"script": isa_script})
        run_script(isa_args)

        # Step 5: Run MIPS comparison
        print("Step 5: Running MIPS comparison analysis...")
        mips_script = "analysis/enhanced_mips_benchmark.py"
        mips_args = type("Args", (), {"script": mips_script})
        run_script(mips_args)

        # Step 6: Run complete ISA design analysis
        print("Step 6: Running complete ISA design analysis...")
        design_script = "analysis/isa_design_analysis.py"
        design_args = type("Args", (), {"script": design_script})
        run_script(design_args)

        print("Benchmark workflow completed successfully.")
        print("Reports available in reports/ directory")
        print("Analysis data available in data/ directory")
        return 0
    except Exception as e:
        print(f"Benchmark workflow failed: {e}")
        return 1
