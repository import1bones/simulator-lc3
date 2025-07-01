# LC-3 Simulator Project Structure

## Overview

This document provides a comprehensive overview of the LC-3 Simulator project structure, including all directories, files, and their purposes. The project follows a modular architecture designed for maintainability, scalability, and cross-platform compatibility.

## 📁 Root Directory Structure

```
simulator-lc3/
├── 📄 CMakeLists.txt                    # Main CMake configuration
├── 📄 main.cpp                         # Main simulator executable entry point
├── 📄 Makefile                         # Legacy build support
├── 📄 pyproject.toml                   # Python project configuration
├── 📄 pytest.ini                       # Pytest configuration
├── 📄 requirements.txt                 # Python dependencies
├── 📄 README.md                        # Project overview and quick start
├── 📄 LICENSE                          # Project license
├── 📄 .gitignore                       # Git ignore patterns
├── 📄 CODE_STYLE                       # Code style guidelines
├── 📄 lc3-simulator.code-workspace     # VS Code workspace configuration
│
├── 🏗️ BUILD SYSTEM AND SCRIPTS
├── 📄 lc3_build.py                     # 🆕 Unified CLI interface
├── 📄 build_and_test.py               # Cross-platform Python build script
├── 📄 build_and_test.sh               # Unix shell build script
├── 📄 build_and_test.bat              # Windows batch build script
├── 📁 build_system/                   # 🆕 Modular build system package
│   ├── 📄 __init__.py                 # Package initialization
│   ├── 📄 core.py                     # Core build system classes
│   ├── 📄 dependencies.py             # Dependency management
│   ├── 📄 builders.py                 # Build orchestration
│   ├── 📄 testing.py                  # Test framework
│   ├── 📄 packaging.py                # Package generation
│   ├── 📄 ci.py                       # CI/CD configuration
│   └── 📄 README.md                   # Build system documentation
│
├── 📊 CORE SIMULATOR MODULES
├── 📁 mem/                            # Memory management
│   ├── 📄 CMakeLists.txt              # Memory module build config
│   ├── 📄 memory.h                    # Main memory interface
│   ├── 📄 control_store.h             # Control store management
│   ├── 📄 device_register.h           # Device register interfaces
│   ├── 📄 microsequence.h             # Microsequence definitions
│   └── 📄 register.h                  # Register implementations
│
├── 📁 state_machine/                  # Processor state management
│   ├── 📄 CMakeLists.txt              # State machine build config
│   ├── 📄 state_machine.h             # Main state machine interface
│   ├── 📄 state_machine.cpp           # State machine implementation
│   ├── 📄 state_machine_utils.cpp     # Utility functions
│   ├── 📄 states.h                    # State definitions
│   ├── 📄 states.cpp                  # State implementations
│   ├── 📄 signals.h                   # Signal definitions
│   ├── 📄 signals.cpp                 # Signal handling
│   ├── 📄 state_definitions.h         # State constants and enums
│   ├── 📄 ext.h                       # External interfaces
│   └── 📄 README.md                   # State machine documentation
│
├── 📁 type/                           # Type definitions and opcodes
│   ├── 📄 CMakeLists.txt              # Type module build config
│   ├── 📄 type.h                      # Core type definitions
│   ├── 📄 opcode.h                    # Instruction opcodes
│   └── 📄 trap_vector.h               # TRAP vector definitions
│
├── 🐍 PYTHON INTEGRATION
├── 📁 python_bindings/                # Python-C++ interface
│   ├── 📄 CMakeLists.txt              # Python bindings build config
│   └── 📄 lc3_simulator.cpp           # pybind11 interface implementation
│
├── 🧪 TESTING FRAMEWORK
├── 📁 tests/                          # Comprehensive test suite
│   ├── 📄 conftest.py                 # Pytest configuration and fixtures
│   ├── 📄 test_basic.py               # Basic functionality tests
│   ├── 📄 test_memory.py              # Memory management tests
│   ├── 📄 test_instructions.py        # Instruction execution tests
│   ├── 📄 test_pipeline.py            # Pipeline performance tests
│   ├── 📄 test_integration.py         # Integration tests
│   ├── 📄 test_integration_pipeline.py # Pipeline integration tests
│   ├── 📄 test_io.py                  # Input/output tests
│   ├── 📄 test_isa_performance.py     # ISA performance analysis
│   ├── 📄 test_utils.py               # Test utility functions
│   └── 📄 README.md                   # Testing documentation
│
├── 📝 SAMPLE PROGRAMS
├── 📁 test_programs/                  # LC-3 assembly programs
│   ├── 📄 hello.asm                   # Hello world example
│   ├── 📄 instructions.txt            # Instruction reference
│   └── 📄 [various .asm files]        # Sample LC-3 programs
│
├── 🛠️ DEVELOPMENT TOOLS
├── 📁 scripts/                        # Development and automation scripts
│   ├── 📄 run_tests.py                # Test execution script
│   ├── 📄 analyze_coverage.py         # Coverage analysis
│   ├── 📄 auto_documentation.py       # Documentation generation
│   ├── 📄 benchmark_programs.py       # Performance benchmarking
│   ├── 📄 clean_project.py            # Project cleanup
│   ├── 📄 debug_test.py               # Test debugging utilities
│   ├── 📄 github_summary.py           # GitHub integration
│   ├── 📄 validate_project.py         # Project validation
│   ├── 📄 README.md                   # Scripts documentation
│   └── 📁 reports/                    # Generated report templates
│       ├── 📄 CONDITION_COVERAGE_ANALYSIS.md
│       └── 📄 test_analysis_summary.json
│
├── 📈 ANALYSIS AND REPORTING
├── 📁 analysis/                       # Performance and ISA analysis
│   ├── 📄 enhanced_isa_analysis.py    # Enhanced ISA analysis
│   ├── 📄 enhanced_mips_benchmark.py  # MIPS comparison benchmarks
│   ├── 📄 isa_design_analysis.py      # ISA design analysis
│   ├── 📄 mips_benchmark.py           # Basic MIPS benchmarks
│   └── 📄 README.md                   # Analysis documentation
│
├── 📁 reports/                        # Generated reports and documentation
│   ├── 📄 comprehensive_test_coverage_report.html
│   ├── 📄 COMPREHENSIVE_TEST_COVERAGE_REPORT.md
│   ├── 📄 CONDITION_COVERAGE_ANALYSIS.md
│   ├── 📄 COVERAGE_REPORT.md
│   ├── 📄 detailed_test_report.html
│   ├── 📄 ISA_COMPREHENSIVE_PERFORMANCE_REPORT.md
│   ├── 📄 test_report.html
│   ├── 📄 test_analysis_summary.json
│   └── 📄 README.md                   # Reports documentation
│
├── 📚 DOCUMENTATION
├── 📁 docs/                           # Project documentation
│   ├── 📄 GITHUB_ACTIONS_GUIDE.md     # CI/CD setup guide
│   ├── 📄 PROJECT_STRUCTURE.md        # This document
│   └── 📄 README.md                   # Documentation index
│
├── 📁 data/                           # Data files and configurations
│   └── 📄 README.md                   # Data directory documentation
│
├── 📋 PROJECT MANAGEMENT
├── 📄 PROJECT_COMPLETE_SUMMARY.md     # Project completion summary
├── 📄 BUILD_SYSTEM_MIGRATION.md       # 🆕 Build system migration guide
├── 📄 BUILD_ARCHITECTURE_SUMMARY.md   # 🆕 Architecture documentation
├── 📄 enhanced_isa_analysis_20250630_005323.json # Generated analysis data
│
└── 🔧 BUILD ARTIFACTS (Generated)
    ├── 📁 build/                       # CMake build directory
    ├── 📁 dist/                        # Distribution packages
    ├── 📁 htmlcov/                     # HTML coverage reports
    ├── 📁 .pytest_cache/              # Pytest cache
    └── 📁 __pycache__/                 # Python bytecode cache
```

## 📋 Module Descriptions

### 🏗️ Build System (`build_system/`)
**Purpose**: Modular, cross-platform build architecture
- **Core Features**: Platform detection, configuration management, logging
- **Dependencies**: System and Python package management across platforms
- **Builders**: CMake and Python build orchestration
- **Testing**: Comprehensive test framework with coverage and reporting
- **Packaging**: Multi-format package generation and distribution
- **CI/CD**: Automated CI/CD configuration generation

### 📊 Core Simulator Modules

#### Memory Management (`mem/`)
**Purpose**: LC-3 memory system implementation
- Memory interface and management
- Control store for microcode
- Device register abstractions
- Register implementations

#### State Machine (`state_machine/`)
**Purpose**: LC-3 processor state management
- Main state machine logic
- State definitions and transitions
- Signal handling and processing
- External interface definitions

#### Type Definitions (`type/`)
**Purpose**: Core LC-3 data types and constants
- Fundamental type definitions
- Instruction opcode definitions
- TRAP vector specifications

### 🐍 Python Integration (`python_bindings/`)
**Purpose**: Python-C++ interface using pybind11
- Exposes C++ simulator functionality to Python
- Enables Python-based testing and analysis
- Provides high-level API for simulator control

### 🧪 Testing Framework (`tests/`)
**Purpose**: Comprehensive testing infrastructure
- **Basic Tests**: Core functionality verification
- **Memory Tests**: Memory management validation
- **Instruction Tests**: Instruction execution verification
- **Pipeline Tests**: Performance and pipeline analysis
- **Integration Tests**: End-to-end testing
- **I/O Tests**: Input/output functionality
- **Performance Tests**: Benchmarking and analysis

### 📝 Sample Programs (`test_programs/`)
**Purpose**: LC-3 assembly language examples
- Educational examples
- Test programs for validation
- Instruction reference materials

### 🛠️ Development Tools (`scripts/`)
**Purpose**: Development automation and utilities
- Test execution and management
- Coverage analysis and reporting
- Documentation generation
- Performance benchmarking
- Project maintenance utilities

### 📈 Analysis and Reporting (`analysis/`, `reports/`)
**Purpose**: Performance analysis and documentation generation
- ISA design analysis
- Performance benchmarking
- Comparison with other architectures
- Automated report generation

## 🔗 Dependency Relationships

### Build Dependencies
```
CMake (3.12+) → C++ Compiler → Simulator Executable
     ↓
Python (3.8+) → pybind11 → Python Bindings
     ↓
pytest → Test Framework → Coverage Reports
```

### Module Dependencies
```
main.cpp
  ├── mem/ (Memory Management)
  ├── state_machine/ (Processor Logic)
  └── type/ (Type Definitions)

python_bindings/
  └── All C++ modules (via pybind11)

tests/
  └── python_bindings/ (Test Interface)

build_system/
  ├── CMake Integration
  ├── Python Environment
  └── Test Framework
```

## 📦 Package Structure

### Core Packages
- **Simulator Core**: C++ implementation of LC-3 architecture
- **Python Bindings**: Python interface to simulator
- **Build System**: Cross-platform build and test infrastructure
- **Test Suite**: Comprehensive testing framework
- **Development Tools**: Scripts and utilities for development

### Distribution Packages
- **Binary Package**: Compiled simulator executable and libraries
- **Source Package**: Complete source code distribution
- **Python Wheel**: Python package for pip installation
- **Documentation Package**: Complete documentation set

## 🔧 Configuration Files

### Build Configuration
- **`CMakeLists.txt`**: Main CMake configuration
- **`pyproject.toml`**: Python project metadata and build configuration
- **`pytest.ini`**: Pytest configuration and test discovery
- **`requirements.txt`**: Python dependency specifications

### Development Configuration
- **`.gitignore`**: Git ignore patterns for build artifacts
- **`CODE_STYLE`**: Code formatting and style guidelines
- **`lc3-simulator.code-workspace`**: VS Code workspace settings

### CI/CD Configuration (Generated)
- **`.github/workflows/ci.yml`**: GitHub Actions workflow
- **`.gitlab-ci.yml`**: GitLab CI/CD configuration

## 🚀 Usage Patterns

### Development Workflow
```bash
# Setup
python lc3_build.py deps --install

# Development cycle
python lc3_build.py build --clean
python lc3_build.py test --categories basic memory
python lc3_build.py test --coverage --html-report

# Release preparation
python lc3_build.py build --build-type Release
python lc3_build.py package --all
```

### Testing Workflow
```bash
# Quick tests
python lc3_build.py test --categories basic

# Comprehensive testing
python lc3_build.py test --categories all --parallel --coverage

# Performance analysis
python lc3_build.py test --categories performance --verbose
```

### CI/CD Workflow
```bash
# Setup CI/CD
python lc3_build.py ci-setup github

# Local CI simulation
python lc3_build.py full-build --clean --test --package
```

## 📊 File Statistics

### Code Distribution
- **C++ Source**: ~15 files (Core simulator implementation)
- **Python Source**: ~20 files (Build system, tests, tools)
- **Build Configuration**: ~10 files (CMake, Python, CI/CD)
- **Documentation**: ~15 files (README, guides, reports)
- **Sample Programs**: ~5 files (LC-3 assembly examples)

### Total Project Size
- **Source Code**: ~50,000 lines
- **Documentation**: ~20,000 lines
- **Test Code**: ~15,000 lines
- **Build Scripts**: ~5,000 lines

## 🎯 Key Design Principles

### Modularity
- Clear separation of concerns between modules
- Well-defined interfaces between components
- Independent testing of each module

### Cross-Platform Compatibility
- Platform abstraction in build system
- Consistent behavior across Windows, Linux, macOS
- Platform-specific optimizations where appropriate

### Maintainability
- Comprehensive documentation
- Consistent coding standards
- Automated testing and validation

### Extensibility
- Plugin architecture for build system
- Modular test framework
- Flexible packaging and distribution

## 🔮 Future Structure Evolution

### Planned Additions
- **`plugins/`**: Build system extensions
- **`benchmarks/`**: Performance benchmark suite
- **`examples/`**: Extended example programs
- **`docker/`**: Container configurations
- **`packaging/`**: Advanced packaging configurations

### Scalability Considerations
- Modular architecture supports easy extension
- Build system designed for additional platforms
- Test framework can accommodate new test types
- Documentation structure supports growth

---

This structure provides a solid foundation for the LC-3 simulator project, with clear organization, comprehensive testing, and robust build infrastructure that can scale with project growth and evolving requirements.
