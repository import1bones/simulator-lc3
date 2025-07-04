#!/usr/bin/env python3
"""
LC-3 Simulator Build System - Main Entry Point

This script serves as the central interface for all build, test, and CI operations
for the LC-3 Simulator project.

Usage:
  python build.py [command] [options]

Commands:
  build       - Build the simulator
  test        - Run tests
  clean       - Clean build artifacts
  setup       - Set up development environment
  ci          - Run CI pipeline locally

Run 'python build.py --help' for detailed usage information.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Ensure we can import modules from the build_system directory
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR / "build_system"))

# Import build system modules
try:
    from build_utils import run_command, get_project_root
    from test_runner import run_tests
    from ci_runner import run_ci_workflow
    from setup_utils import setup_environment
except ImportError as e:
    print(f"Error: Failed to import build system modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LC-3 Simulator Build System")
    
    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build the simulator")
    build_parser.add_argument("--clean", action="store_true", help="Clean before building")
    build_parser.add_argument("--python-bindings", action="store_true", help="Build Python bindings")
    build_parser.add_argument("--pipeline", action="store_true", help="Build with pipeline extensions")
    build_parser.add_argument("--debug", action="store_true", help="Build in debug mode")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--all", action="store_true", help="Run all tests")
    test_parser.add_argument("--fast", action="store_true", help="Run tests in parallel")
    test_parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    test_parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    test_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    test_parser.add_argument("--category", type=str, help="Run specific test category")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("--all", action="store_true", help="Clean everything including reports")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up development environment")
    setup_parser.add_argument("--deps", action="store_true", help="Install dependencies only")
    
    # CI command
    ci_parser = subparsers.add_parser("ci", help="Run CI workflow locally")
    ci_parser.add_argument("--workflow", type=str, default="default", help="Specify workflow to run")
    
    return parser.parse_args()

def main():
    """Main entry point for the build system."""
    args = parse_args()
    
    if not args.command:
        print("No command specified. Use --help for usage information.")
        return 1
    
    try:
        # Execute the requested command
        if args.command == "build":
            from build_commands import build_project
            return build_project(args)
        elif args.command == "test":
            from test_commands import run_test_suite
            return run_test_suite(args)
        elif args.command == "clean":
            from clean_commands import clean_project
            return clean_project(args)
        elif args.command == "setup":
            from setup_commands import setup_project
            return setup_project(args)
        elif args.command == "ci":
            from ci_commands import run_ci
            return run_ci(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except ImportError as e:
        print(f"Error: Failed to import command module: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
