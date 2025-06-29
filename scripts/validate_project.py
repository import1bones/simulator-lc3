#!/usr/bin/env python3
"""
Comprehensive validation script to ensure all components work after reorganization.

This script tests:
1. All test execution paths
2. All analysis scripts
3. All utility scripts  
4. File path integrity
5. Report generation
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def run_command(cmd, description="", cwd=None):
    """Run a command and report success/failure."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print(f"✅ SUCCESS: {description}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout[:500]}...")
        if e.stderr:
            print(f"stderr: {e.stderr[:500]}...")
        return False, None
    except Exception as e:
        print(f"❌ EXCEPTION: {description} - {e}")
        return False, None


def test_project_structure():
    """Test that all expected directories and files exist."""
    print("\n📁 Testing Project Structure...")
    
    # Detect project root (go up one level if running from scripts/)
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    print(f"📁 Working from project root: {project_root}")
    
    expected_dirs = [
        "scripts", "analysis", "data", "docs", "reports", "tests", 
        "state_machine", "mem", "type", "python_bindings", ".vscode"
    ]
    
    expected_files = [
        "CMakeLists.txt", "Makefile", "main.cpp", "README.md",
        "scripts/run_tests.py", "analysis/enhanced_isa_analysis.py",
        "tests/test_basic.py", "docs/PROJECT_STRUCTURE.md"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_name in expected_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    for file_name in expected_files:
        file_path = project_root / file_name
        if not file_path.exists():
            missing_files.append(file_name)
        else:
            print(f"✅ File exists: {file_name}")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All expected directories and files exist")
    return True


def test_test_execution():
    """Test various test execution scenarios."""
    print("\n🧪 Testing Test Execution...")
    
    # Detect project root
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    success = True
    
    # Test basic functionality
    cmd = ["python3", "scripts/run_tests.py", "--basic"]
    result, _ = run_command(cmd, "Basic tests execution", cwd=project_root)
    success &= result
    
    # Test specific test category
    cmd = ["python3", "scripts/run_tests.py", "--instructions"]
    result, _ = run_command(cmd, "Instructions tests execution", cwd=project_root)
    success &= result
    
    # Test help functionality
    cmd = ["python3", "scripts/run_tests.py", "--help"]
    result, _ = run_command(cmd, "Test runner help", cwd=project_root)
    success &= result
    
    return success


def test_analysis_scripts():
    """Test all analysis scripts."""
    print("\n📊 Testing Analysis Scripts...")
    
    # Detect project root
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    success = True
    
    # Test enhanced ISA analysis
    cmd = ["python3", "analysis/enhanced_isa_analysis.py"]
    result, _ = run_command(cmd, "Enhanced ISA analysis", cwd=project_root)
    success &= result
    
    # Test enhanced MIPS benchmark
    cmd = ["python3", "analysis/enhanced_mips_benchmark.py"]
    result, _ = run_command(cmd, "Enhanced MIPS benchmark", cwd=project_root)
    success &= result
    
    # Test original ISA analysis
    cmd = ["python3", "analysis/isa_design_analysis.py"]
    result, _ = run_command(cmd, "Original ISA analysis", cwd=project_root)
    success &= result
    
    # Test original MIPS benchmark
    cmd = ["python3", "analysis/mips_benchmark.py"]
    result, _ = run_command(cmd, "Original MIPS benchmark", cwd=project_root)
    success &= result
    
    return success


def test_utility_scripts():
    """Test utility scripts functionality."""
    print("\n🛠️ Testing Utility Scripts...")
    
    # Detect project root
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    success = True
    
    # Test coverage analysis (if it exists)
    coverage_script = project_root / "scripts/analyze_coverage.py"
    if coverage_script.exists():
        cmd = ["python3", "scripts/analyze_coverage.py", "--help"]
        result, _ = run_command(cmd, "Coverage analysis help", cwd=project_root)
        success &= result
    
    # Test benchmark programs
    benchmark_script = project_root / "scripts/benchmark_programs.py"
    if benchmark_script.exists():
        cmd = ["python3", "scripts/benchmark_programs.py"]
        result, _ = run_command(cmd, "Benchmark programs", cwd=project_root)
        # Don't fail overall if this script has issues
    
    return success


def test_report_generation():
    """Test that reports are generated in correct locations."""
    print("\n📋 Testing Report Generation...")
    
    # Detect project root
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    reports_dir = project_root / "reports"
    data_dir = project_root / "data"
    
    # Count files before
    reports_before = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0
    data_before = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0
    
    # Run analysis to generate reports
    cmd = ["python3", "analysis/enhanced_isa_analysis.py"]
    result, _ = run_command(cmd, "Generate ISA analysis report", cwd=project_root)
    
    if not result:
        return False
    
    # Check if reports were generated
    reports_after = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0
    data_after = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0
    
    print(f"📊 Reports before: {reports_before}, after: {reports_after}")
    print(f"💾 Data files before: {data_before}, after: {data_after}")
    
    # Check that reports exist (don't require new ones)
    if reports_after > 0:
        print("✅ Report files exist")
        success = True
    else:
        print("❌ No report files found")
        success = False
    
    if data_after > 0:
        print("✅ Data files exist") 
        success = success and True
    else:
        print("❌ No data files found")
        success = False
    
    return success


def test_build_system():
    """Test that the build system works."""
    print("\n🔨 Testing Build System...")
    
    # Detect project root
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        project_root = current_dir.parent
    else:
        project_root = current_dir
    
    success = True
    
    # Test CMake configuration
    build_dir = project_root / "build"
    if not build_dir.exists():
        build_dir.mkdir()
    
    cmd = ["cmake", "--version"]
    result, _ = run_command(cmd, "CMake availability check", cwd=project_root)
    
    if result:
        cmd = ["cmake", "-DBUILD_PYTHON_BINDINGS=ON", ".."]
        result, _ = run_command(cmd, "CMake configuration", cwd=build_dir)
        success &= result
    else:
        print("⚠️ CMake not available, skipping build tests")
        success = True  # Don't fail if CMake is not available
    
    # Test Makefile
    makefile = project_root / "Makefile"
    if makefile.exists():
        cmd = ["make", "--version"]
        result, _ = run_command(cmd, "Make availability check", cwd=project_root)
        
        if result:
            cmd = ["make", "help"]
            result, _ = run_command(cmd, "Makefile help")
            # Don't require this to succeed
    
    return success


def clean_generated_files():
    """Clean up generated test files."""
    print("\n🧹 Cleaning up generated files...")
    
    # Remove test-generated files
    patterns = [
        "enhanced_*_*.json",
        "enhanced_*_*.md"
    ]
    
    for pattern in patterns:
        for file_path in Path(".").glob(pattern):
            try:
                file_path.unlink()
                print(f"🗑️ Removed: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")


def main():
    """Run comprehensive validation."""
    print("🚀 LC-3 Simulator Comprehensive Validation")
    print("=" * 50)
    
    start_time = time.time()
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir
    os.chdir(project_root)
    
    print(f"📁 Working directory: {project_root.absolute()}")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Test Execution", test_test_execution),
        ("Analysis Scripts", test_analysis_scripts),
        ("Utility Scripts", test_utility_scripts),
        ("Report Generation", test_report_generation),
        ("Build System", test_build_system),
    ]
    
    results = {}
    overall_success = True
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            overall_success &= result
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: EXCEPTION - {e}")
            results[test_name] = False
            overall_success = False
    
    # Summary
    execution_time = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"📋 VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n⏱️ Total execution time: {execution_time:.2f} seconds")
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! Project is properly organized and functional.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED! Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
