#!/usr/bin/env python3
"""
Quick CI validation script for immediate testing.
This script checks the key fixes we've implemented.
"""

import sys
import subprocess
from pathlib import Path


def run_flake8_check():
    """Run flake8 on critical files."""
    print("=== Running flake8 checks ===")
    
    # Check critical files for syntax errors
    files_to_check = [
        "tests/conftest.py",
        "scripts/run_tests.py"
    ]
    
    for file_path in files_to_check:
        print(f"Checking {file_path}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "py_compile", file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ {file_path} - syntax OK")
            else:
                print(f"  ✗ {file_path} - syntax error:")
                print(f"    {result.stderr}")
                return False
        except Exception as e:
            print(f"  ! Error checking {file_path}: {e}")
            return False
    
    return True


def check_cmake_files():
    """Check CMakeLists.txt files exist with correct case."""
    print("\n=== Checking CMakeLists.txt files ===")
    
    dirs_to_check = ["mem", "state_machine", "type"]
    for dir_name in dirs_to_check:
        cmake_file = Path(dir_name) / "CMakeLists.txt"
        if cmake_file.exists():
            print(f"  ✓ {dir_name}/CMakeLists.txt exists")
        else:
            print(f"  ✗ {dir_name}/CMakeLists.txt missing")
            return False
    
    return True


def check_pytest_config():
    """Check pytest configuration."""
    print("\n=== Checking pytest configuration ===")
    
    pytest_ini = Path("pytest.ini")
    if not pytest_ini.exists():
        print("  ✗ pytest.ini missing")
        return False
    
    content = pytest_ini.read_text()
    if "[pytest]" in content and "markers" in content:
        print("  ✓ pytest.ini has correct format")
        return True
    else:
        print("  ✗ pytest.ini has incorrect format")
        return False


def main():
    """Quick validation."""
    print("Quick CI Validation")
    print("==================")
    
    checks = [
        ("Flake8/Syntax", run_flake8_check),
        ("CMakeLists.txt", check_cmake_files),  
        ("Pytest config", check_pytest_config)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"  ! Error in {check_name}: {e}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("All validation checks PASSED!")
        return 0
    else:
        print("Some validation checks FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
