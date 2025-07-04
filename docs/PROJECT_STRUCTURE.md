# LC-3 Simulator Project Structure

This document provides an overview of the LC-3 simulator project structure, explaining the purpose and organization of each directory.

## Project Root

The root directory contains the main build system entry point and core project files:

- `build.py`: Main entry point for the build system
- `CMakeLists.txt`: CMake project definition
- `main.cpp`: Main simulator entry point
- `README.md`: Project overview and documentation entry point

## Core Components

### Memory Subsystem (`mem/`)

Contains memory-related components:

- `memory.h`: Memory subsystem implementation
- `register.h`: Register definitions and operations
- `device_register.h`: Device register implementations
- `control_store.h`: Control store definitions
- `microsequence.h`: Microsequence implementation

### State Machine (`state_machine/`)

Contains the LC-3 state machine implementation:

- `state_machine.h/cpp`: Main state machine implementation
- `states.h/cpp`: State definitions and handlers
- `signals.h`: Signal definitions and handlers
- `ext.h`: Extension interfaces

### Type Definitions (`type/`)

Contains type definitions and constants:

- `type.h`: Basic type definitions
- `opcode.h`: Operation code definitions
- `trap_vector.h`: Trap vector definitions

## Build System (`build_system/`)

Contains the build system implementation:

- `build_utils.py`: Utility functions for the build system
- `build_commands.py`: Build command implementations
- `test_commands.py`: Test command implementations
- `clean_commands.py`: Clean command implementations
- `setup_commands.py`: Setup command implementations
- `ci_commands.py`: CI workflow implementations
- `init.sh`: Build system initialization script
- `README.md`: Build system documentation

## Tests (`tests/`)

Contains the test suite:

- `test_runner.py`: Main test runner
- `test_environment_setup.py`: Test environment configuration
- `conftest.py`: pytest configuration and fixtures
- `test_basic.py`: Basic simulator tests
- `test_instructions.py`: Instruction execution tests
- `test_memory.py`: Memory subsystem tests
- `test_io.py`: I/O operation tests
- `test_integration.py`: Integration tests
- `test_cli.py`: Command-line interface tests
- `test_utils.py`: Test utilities and helpers
- `README.md`: Test suite documentation

## Documentation (`docs/`)

Contains project documentation:

- `README.md`: Documentation overview
- `INDEX.md`: Documentation index
- `DOCUMENTATION_GUIDE.md`: Guide to documentation
- `PROJECT_STRUCTURE.md`: This document

### Documentation Subdirectories

- `development/`: Development-related documentation
  - `CLI_TESTING_FRAMEWORK.md`: CLI testing framework documentation
  - `TEST_REORGANIZATION.md`: Test reorganization documentation
  - `BUILD_ARCHITECTURE_SUMMARY.md`: Build architecture documentation
  - Other development documentation

- `project/`: Project overview documentation
  - `PROJECT_OVERVIEW.md`: Project overview
  - `PROJECT_NAVIGATION.md`: Navigation guide
  - Other project documentation

- `ci/`: CI/CD documentation
  - `PIPELINE_INTEGRATION_GUIDE.md`: Pipeline integration guide
  - `GITHUB_ACTIONS_GUIDE.md`: GitHub Actions guide
  - Other CI documentation

## Scripts (`scripts/`)

Contains utility scripts:

- `fix_python_bindings.py`: Python binding fixes
- `validate_docs.py`: Documentation validation
- `cleanup_reports.py`: Report cleanup utilities
- Other utility scripts

## Build Output (`build/`)

Contains build outputs:

- `simulator-lc3`: Main simulator binary
- Generated Python bindings
- Other build artifacts
