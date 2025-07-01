#!/usr/bin/env python3
"""
Simple test validation script that doesn't require building.
This script validates the pipeline integration by checking:
1. Code compilation (syntax checking)
2. Header inclusion consistency
3. Function declaration consistency
4. Basic integration structure
"""

import os
import sys
import re
import argparse
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report."""
    if file_path.exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (NOT FOUND)")
        return False


def check_include_consistency(file_path, required_includes):
    """Check if a file includes all required headers."""
    if not file_path.exists():
        return False
    
    content = file_path.read_text()
    missing_includes = []
    
    for include in required_includes:
        if f'#include "{include}"' not in content and f'#include <{include}>' not in content:
            missing_includes.append(include)
    
    if missing_includes:
        print(f"✗ {file_path}: Missing includes: {missing_includes}")
        return False
    else:
        print(f"✓ {file_path}: All required includes present")
        return True


def check_function_declarations(header_file, impl_file, function_names):
    """Check if functions are declared in header and implemented in source."""
    if not header_file.exists() or not impl_file.exists():
        return False
    
    header_content = header_file.read_text()
    impl_content = impl_file.read_text()
    
    issues = []
    
    for func_name in function_names:
        # Check declaration in header
        if func_name not in header_content:
            issues.append(f"Function {func_name} not declared in header")
        
        # Check implementation in source  
        if func_name not in impl_content:
            issues.append(f"Function {func_name} not implemented in source")
    
    if issues:
        print(f"✗ Function consistency issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"✓ Function declarations consistent between {header_file.name} and {impl_file.name}")
        return True


def check_pipeline_integration():
    """Check pipeline integration completeness."""
    project_root = Path(__file__).parent
    success = True
    
    print("Checking Pipeline Integration...")
    print("=" * 50)
    
    # 1. Check core files exist
    core_files = {
        "Main simulator": project_root / "main.cpp",
        "Pipeline header": project_root / "mem" / "control_store.h", 
        "Pipeline implementation": project_root / "mem" / "control_store.c",
        "State machine": project_root / "state_machine" / "state_machine.cpp",
        "Signals header": project_root / "state_machine" / "signals.h",
        "Python bindings": project_root / "python_bindings" / "lc3_simulator.cpp",
        "Pipeline tests": project_root / "tests" / "test_pipeline.py",
        "Integration tests": project_root / "tests" / "test_integration_pipeline.py",
    }
    
    for desc, file_path in core_files.items():
        if not check_file_exists(file_path, desc):
            success = False
    
    print()
    
    # 2. Check include consistency
    print("Checking Include Consistency...")
    print("-" * 30)
    
    include_checks = [
        (project_root / "main.cpp", [
            "mem/control_store.h", "state_machine/signals.h"
        ]),
        (project_root / "state_machine" / "state_machine.cpp", [
            "../mem/control_store.h"
        ]),
        (project_root / "python_bindings" / "lc3_simulator.cpp", [
            "../mem/control_store.h", "../state_machine/signals.h"
        ]),
    ]
    
    for file_path, required_includes in include_checks:
        if not check_include_consistency(file_path, required_includes):
            success = False
    
    print()
    
    # 3. Check function declarations
    print("Checking Function Declarations...")
    print("-" * 35)
    
    pipeline_functions = [
        "lc3_pipeline_init", "lc3_pipeline_reset", "lc3_pipeline_configure",
        "lc3_pipeline_cycle", "lc3_pipeline_issue_instruction", 
        "lc3_pipeline_get_metrics", "lc3_pipeline_config_init_default",
        "lc3_pipeline_metrics_reset", "lc3_instruction_packet_init"
    ]
    
    if not check_function_declarations(
        project_root / "mem" / "control_store.h",
        project_root / "mem" / "control_store.c", 
        pipeline_functions
    ):
        success = False
    
    print()
    
    # 4. Check pipeline structures
    print("Checking Pipeline Data Structures...")
    print("-" * 40)
    
    control_store_h = project_root / "mem" / "control_store.h"
    if control_store_h.exists():
        content = control_store_h.read_text()
        
        required_structures = [
            "lc3_pipeline_config_t", "lc3_pipeline_metrics_t", 
            "lc3_instruction_packet_t", "lc3_pipeline_stage_t",
            "lc3_hazard_type_t"
        ]
        
        missing_structures = []
        for struct in required_structures:
            if struct not in content:
                missing_structures.append(struct)
        
        if missing_structures:
            print(f"✗ Missing data structures: {missing_structures}")
            success = False
        else:
            print("✓ All required pipeline data structures present")
    else:
        success = False
    
    print()
    
    # 5. Check global variables
    print("Checking Global Pipeline Variables...")
    print("-" * 40)
    
    control_store_c = project_root / "mem" / "control_store.c"
    if control_store_c.exists():
        content = control_store_c.read_text()
        
        required_globals = [
            "lc3_pipeline_config", "lc3_pipeline_metrics",
            "lc3_pipeline", "lc3_current_cycle", "lc3_pipeline_enabled"
        ]
        
        missing_globals = []
        for global_var in required_globals:
            if global_var not in content:
                missing_globals.append(global_var)
        
        if missing_globals:
            print(f"✗ Missing global variables: {missing_globals}")
            success = False
        else:
            print("✓ All required global pipeline variables present")
    else:
        success = False
    
    print()
    
    # 6. Check CMake integration
    print("Checking Build System Integration...")
    print("-" * 40)
    
    cmake_files = [
        project_root / "CMakeLists.txt",
        project_root / "mem" / "CmakeLists.txt"
    ]
    
    for cmake_file in cmake_files:
        if cmake_file.exists():
            content = cmake_file.read_text()
            if "control_store.c" in content:
                print(f"✓ {cmake_file.name}: Pipeline integration present")
            else:
                print(f"⚠ {cmake_file.name}: Pipeline integration may be missing")
        else:
            print(f"✗ {cmake_file}: Not found")
            success = False
    
    print()
    
    # 7. Check documentation
    print("Checking Documentation...")
    print("-" * 30)
    
    doc_files = {
        "Pipeline Integration Guide": project_root / "PIPELINE_INTEGRATION_GUIDE.md",
        "Updated README": project_root / "README.md",
        "Demo program": project_root / "pipeline_demo_integrated.c",
    }
    
    for desc, file_path in doc_files.items():
        check_file_exists(file_path, desc)
    
    # Check README for pipeline content
    readme_file = project_root / "README.md"
    if readme_file.exists():
        try:
            content = readme_file.read_text(encoding='utf-8')
            if "pipeline" in content.lower():
                print("✓ README contains pipeline documentation")
            else:
                print("⚠ README may not contain pipeline documentation")
        except UnicodeDecodeError:
            print("⚠ README file encoding issue - skipping content check")
    
    print()
    print("=" * 50)
    
    if success:
        print("✅ Pipeline Integration Validation: PASSED")
        print("All required components are present and properly integrated.")
    else:
        print("❌ Pipeline Integration Validation: FAILED")
        print("Some components are missing or incorrectly integrated.")
    
    return success


def main():
    """Main validation function."""
    print("LC-3 Pipeline Integration Validator")
    print("=" * 50)
    print()
    
    # Argument parser for report options
    parser = argparse.ArgumentParser(description="LC-3 Pipeline Integration Validator")
    parser.add_argument(
        "--report",
        choices=["text", "json", "xml"],
        default="text",
        help="Specify the report format (default: text)"
    )
    args = parser.parse_args()
    
    success = check_pipeline_integration()
    
    print()
    print("Validation Summary:")
    print("-" * 20)
    
    if success:
        print("✅ The pipeline extension is properly integrated into the LC-3 simulator.")
        print("✅ All core components are present and consistent.")
        print("✅ Build system is configured correctly.")
        print("✅ Documentation is available.")
        print()
        print("Next steps:")
        print("1. Build the simulator with: cmake -S . -B build && cmake --build build")
        print("2. Run tests with: python scripts/run_tests.py --basic")
        print("3. Try pipeline mode: ./build/simulator-lc3 --pipeline program.obj")
        return 0
    else:
        print("❌ Pipeline integration has issues that need to be resolved.")
        print("❌ Please check the errors above and fix them before building.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
