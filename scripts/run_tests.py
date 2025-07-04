#!/usr/bin/env python3
"""
Test runner script for LC-3 Simulator tests.

This script provides various options for running the test suite:
- Run all tests
- Run specific test categories
- Generate coverage reports
- Run performance tests
- Build the simulator if needed
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


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
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if capture_output and e.stdout:
            print(f"stdout: {e.stdout}")
        if capture_output and e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def build_simulator(project_root):
    """Build the LC-3 simulator with Python bindings."""
    print("Building LC-3 Simulator...")

    build_dir = project_root / "build"
    build_dir.mkdir(exist_ok=True)

    # Configure with CMake
    cmake_cmd = ["cmake", "-DBUILD_PYTHON_BINDINGS=ON", ".."]
    if not run_command(cmake_cmd, cwd=build_dir):
        print("Failed to configure project with CMake")
        return False

    # Build (use parallel jobs for faster builds)
    import multiprocessing

    jobs = multiprocessing.cpu_count()
    build_cmd = [
        "cmake",
        "--build",
        ".",
        "--config",
        "Release",
        "--parallel",
        str(jobs),
    ]
    if not run_command(build_cmd, cwd=build_dir):
        print("Failed to build project")
        return False

    print("Build completed successfully!")
    return True


def install_dependencies():
    """Install Python dependencies for testing."""
    print("Installing Python dependencies...")

    # Install test dependencies
    deps = [
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "pytest-xdist>=3.0",
        "pytest-html>=3.0",
        "pytest-benchmark>=4.0",
        "numpy>=1.20",
    ]

    for dep in deps:
        cmd = [sys.executable, "-m", "pip", "install", dep]
        if not run_command(cmd):
            print(f"Failed to install {dep}")
            return False

    # Try to install pybind11
    cmd = [sys.executable, "-m", "pip", "install", "pybind11[global]"]
    if not run_command(cmd):
        print(
            "Warning: Failed to install pybind11. You may need to install it manually."
        )

    return True


def run_tests(project_root, args):
    """Run the test suite with specified options."""
    test_dir = project_root / "tests"

    # Build pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]

    # Add test directory
    pytest_cmd.append(str(test_dir))

    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")

    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(
            [
                "--cov=lc3_simulator",
                "--cov-report=html:reports/coverage",
                "--cov-report=term-missing",
            ]
        )

    # Add HTML report if requested
    if args.html_report:
        pytest_cmd.extend(["--html=reports/test_report.html", "--self-contained-html"])

    # Add parallel execution if requested
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])

    # Add markers for test categories
    markers = []
    if args.unit_only:
        markers.append("unit")
    if args.integration_only:
        markers.append("integration")
    if args.functional_only:
        markers.append("functional")
    if args.slow:
        markers.append("slow")
    if not args.slow and not any(
        [args.unit_only, args.integration_only, args.functional_only]
    ):
        markers.append("not slow")

    if markers:
        pytest_cmd.extend(["-m", " or ".join(markers)])

    # Add specific test categories
    if args.instructions:
        pytest_cmd.append(str(test_dir / "test_instructions.py"))
    elif args.memory:
        pytest_cmd.append(str(test_dir / "test_memory.py"))
    elif args.io:
        pytest_cmd.append(str(test_dir / "test_io.py"))
    elif args.basic:
        pytest_cmd.append(str(test_dir / "test_basic.py"))
    elif args.integration:
        pytest_cmd.append(str(test_dir / "test_integration.py"))

    # Add fail fast if requested
    if args.fail_fast:
        pytest_cmd.append("-x")

    # Add specific test file if provided
    if args.test_file:
        pytest_cmd.append(args.test_file)

    # Create reports directory
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    print(f"Running tests with command: {' '.join(pytest_cmd)}")

    # Run tests
    start_time = time.time()
    success = run_command(pytest_cmd)
    end_time = time.time()

    print(f"\nTest execution completed in {end_time - start_time:.2f} seconds")

    if args.coverage and success:
        print(f"Coverage report generated in: {reports_dir}/coverage/index.html")

    if args.html_report and success:
        print(f"Test report generated in: {reports_dir}/test_report.html")

    return success


def run_benchmarks(project_root):
    """Run performance benchmarks."""
    print("Running performance benchmarks...")

    test_dir = project_root / "tests"

    benchmark_cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_dir),
        "-m",
        "slow",
        "--benchmark-only",
        "--benchmark-html=reports/benchmark_report.html",
    ]

    return run_command(benchmark_cmd)


def check_simulator_module(project_root):
    """Check if the LC-3 simulator module is built and available."""
    build_dir = project_root / "build" / "python_bindings"

    # Check if build directory exists
    if not build_dir.exists():
        return False

    # Try to import the module
    sys.path.insert(0, str(build_dir))
    try:
        import lc3_simulator

        print("✅ LC-3 simulator module is available")
        return True
    except ImportError:
        print("❌ LC-3 simulator module not found or not built")
        return False
    finally:
        # Remove from path to avoid conflicts
        if str(build_dir) in sys.path:
            sys.path.remove(str(build_dir))


def check_environment():
    """Check if the environment is properly set up."""
    print("Checking environment...")

    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False

    # Check if cmake is available
    try:
        subprocess.run(["cmake", "--version"], capture_output=True, check=True)
        print("✅ CMake is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ CMake is not installed or not in PATH")
        return False

    # Check if a C++ compiler is available
    for compiler in ["g++", "clang++", "cl"]:
        try:
            subprocess.run([compiler, "--version"], capture_output=True, check=True)
            print(f"✅ Found C++ compiler: {compiler}")
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    else:
        print("⚠️ Warning: No C++ compiler found. Build may fail.")

    print("Environment check completed.")
    return True


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="LC-3 Simulator Test Runner")

    # Build options
    parser.add_argument(
        "--build", action="store_true", help="Build the simulator before running tests"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install Python dependencies"
    )
    parser.add_argument(
        "--check-env", action="store_true", help="Check environment setup"
    )

    # Test execution options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose test output"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--html-report", action="store_true", help="Generate HTML test report"
    )
    parser.add_argument(
        "--parallel", "-p", action="store_true", help="Run tests in parallel"
    )
    parser.add_argument(
        "--fail-fast", "-x", action="store_true", help="Stop on first failure"
    )

    # Test categories
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration-only", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--functional-only", action="store_true", help="Run only functional tests"
    )
    parser.add_argument("--slow", action="store_true", help="Include slow tests")

    # Specific test types
    parser.add_argument(
        "--basic", action="store_true", help="Run basic functionality tests"
    )
    parser.add_argument(
        "--instructions", action="store_true", help="Run instruction tests"
    )
    parser.add_argument("--memory", action="store_true", help="Run memory tests")
    parser.add_argument("--io", action="store_true", help="Run I/O tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )

    # Other options
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmarks"
    )
    parser.add_argument("--test-file", help="Run specific test file")

    args = parser.parse_args()

    # Get project root directory (script is now in scripts/ subdirectory)
    project_root = Path(__file__).parent.parent

    # Check environment if requested
    if args.check_env:
        env_ok = check_environment()
        module_ok = check_simulator_module(project_root)

        if not env_ok:
            return 1

        if not module_ok:
            print("\n⚠️ LC-3 simulator module is not built.")
            print("To build it, run: python3 scripts/run_tests.py --build")
            print("Or in CI/automated environments, the build should happen first.")

        return 0 if env_ok else 1

    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print("Failed to install dependencies")
            return 1

    # Build simulator if requested
    if args.build:
        if not build_simulator(project_root):
            print("Failed to build simulator")
            return 1

    # Run benchmarks if requested
    if args.benchmark:
        if not run_benchmarks(project_root):
            print("Benchmark execution failed")
            return 1
        return 0

    # Run tests
    if not run_tests(project_root, args):
        print("Test execution failed")
        return 1

    print("All tests completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
