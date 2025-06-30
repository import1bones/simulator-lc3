"""
Basic validation tests that don't require C++ compilation.
These tests validate the Python test infrastructure and pipeline test structure.
"""
import pytest
import sys
import os
from pathlib import Path


def test_test_files_exist():
    """Test that all required test files are present."""
    project_root = Path(__file__).parent.parent
    
    required_test_files = [
        "tests/test_basic.py",
        "tests/test_instructions.py", 
        "tests/test_memory.py",
        "tests/test_io.py",
        "tests/test_integration.py",
        "tests/test_pipeline.py",
        "tests/test_integration_pipeline.py",
        "tests/conftest.py"
    ]
    
    for test_file in required_test_files:
        file_path = project_root / test_file
        assert file_path.exists(), f"Test file missing: {test_file}"


def test_source_files_exist():
    """Test that all required source files are present."""
    project_root = Path(__file__).parent.parent
    
    required_source_files = [
        "main.cpp",
        "mem/control_store.h",
        "mem/control_store.c", 
        "state_machine/state_machine.cpp",
        "state_machine/state_machine.h",
        "state_machine/signals.h",
        "python_bindings/lc3_simulator.cpp"
    ]
    
    for source_file in required_source_files:
        file_path = project_root / source_file
        assert file_path.exists(), f"Source file missing: {source_file}"


def test_pipeline_integration_files_exist():
    """Test that pipeline integration files are present."""
    project_root = Path(__file__).parent.parent
    
    pipeline_files = [
        "PIPELINE_INTEGRATION_GUIDE.md",
        "pipeline_demo_integrated.c",
        "test_pipeline_integration.c",
        "validate_pipeline_integration.py"
    ]
    
    for pipeline_file in pipeline_files:
        file_path = project_root / pipeline_file
        assert file_path.exists(), f"Pipeline file missing: {pipeline_file}"


def test_build_files_exist():
    """Test that build configuration files are present."""
    project_root = Path(__file__).parent.parent
    
    build_files = [
        "CMakeLists.txt",
        "mem/CmakeLists.txt",
        "Makefile"
    ]
    
    for build_file in build_files:
        file_path = project_root / build_file
        assert file_path.exists(), f"Build file missing: {build_file}"


def test_pipeline_functions_declared():
    """Test that pipeline functions are declared in headers."""
    project_root = Path(__file__).parent.parent
    control_store_h = project_root / "mem" / "control_store.h"
    
    assert control_store_h.exists(), "control_store.h not found"
    
    content = control_store_h.read_text(encoding='utf-8', errors='ignore')
    
    required_functions = [
        "lc3_pipeline_init",
        "lc3_pipeline_reset", 
        "lc3_pipeline_configure",
        "lc3_pipeline_cycle",
        "lc3_pipeline_issue_instruction",
        "lc3_pipeline_get_metrics"
    ]
    
    for func in required_functions:
        assert func in content, f"Function {func} not declared in control_store.h"


def test_pipeline_types_defined():
    """Test that pipeline types are defined in headers."""
    project_root = Path(__file__).parent.parent
    control_store_h = project_root / "mem" / "control_store.h"
    
    assert control_store_h.exists(), "control_store.h not found"
    
    content = control_store_h.read_text(encoding='utf-8', errors='ignore')
    
    required_types = [
        "lc3_pipeline_config_t",
        "lc3_pipeline_metrics_t",
        "lc3_instruction_packet_t",
        "lc3_pipeline_stage_t",
        "lc3_hazard_type_t"
    ]
    
    for type_name in required_types:
        assert type_name in content, f"Type {type_name} not defined in control_store.h"


def test_main_cpp_includes_pipeline():
    """Test that main.cpp includes pipeline headers."""
    project_root = Path(__file__).parent.parent
    main_cpp = project_root / "main.cpp"
    
    assert main_cpp.exists(), "main.cpp not found"
    
    content = main_cpp.read_text(encoding='utf-8', errors='ignore')
    
    required_includes = [
        'mem/control_store.h',
        'state_machine/signals.h'
    ]
    
    for include in required_includes:
        assert include in content, f"Include {include} not found in main.cpp"


def test_python_bindings_include_pipeline():
    """Test that Python bindings include pipeline functionality."""
    project_root = Path(__file__).parent.parent
    bindings_cpp = project_root / "python_bindings" / "lc3_simulator.cpp"
    
    assert bindings_cpp.exists(), "lc3_simulator.cpp not found"
    
    content = bindings_cpp.read_text(encoding='utf-8', errors='ignore')
    
    # Check for pipeline includes
    assert 'mem/control_store.h' in content, "Pipeline header not included in Python bindings"
    
    # Check for pipeline methods
    pipeline_methods = [
        'enable_pipeline',
        'reset_pipeline', 
        'configure_pipeline',
        'get_pipeline_metrics'
    ]
    
    for method in pipeline_methods:
        assert method in content, f"Pipeline method {method} not found in Python bindings"


def test_cmake_includes_pipeline():
    """Test that CMake configuration includes pipeline files."""
    project_root = Path(__file__).parent.parent
    mem_cmake = project_root / "mem" / "CmakeLists.txt"
    
    assert mem_cmake.exists(), "mem/CmakeLists.txt not found"
    
    content = mem_cmake.read_text(encoding='utf-8', errors='ignore')
    
    # Check that control_store.c is included in build
    assert 'control_store.c' in content, "control_store.c not included in CMake build"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
