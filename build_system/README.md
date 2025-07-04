# LC-3 Simulator Build System

This directory contains the unified build system for the LC-3 Simulator project. All build, test, and CI operations are managed through a single interface.

## Overview

The build system provides a unified interface for:

- Building the simulator
- Running tests
- Setting up the development environment
- Running CI workflows locally
- Cleaning the project

## Getting Started

Initialize the build system:

```bash
./build_system/init.sh
```

This will create a symbolic link `lc3-build` in the project root for convenience.

## Using the Build System

### Building the Simulator

```bash
./build.py build [options]

Options:
  --clean            Clean before building
  --python-bindings  Build Python bindings
  --pipeline         Build with pipeline extensions
  --debug            Build in debug mode
```

### Running Tests

```bash
./build.py test [options]

Options:
  --all          Run all tests
  --fast         Run tests in parallel
  --unit         Run unit tests only
  --integration  Run integration tests only
  --coverage     Generate coverage report
  --category CATEGORY  Run specific test category (e.g., cli, basic, instructions)
```

To specifically test the simulator-lc3 CLI:

```bash
./build.py test --category cli
```

### Setting Up the Environment

```bash
./build.py setup [options]

Options:
  --deps         Install dependencies only
```

### Running CI Workflows Locally

```bash
./build.py ci [options]

Options:
  --workflow WORKFLOW  Specify workflow to run (default, nightly, cross-platform)
```

### Cleaning the Project

```bash
./build.py clean [options]

Options:
  --all          Clean everything including reports
```

## Structure

- `build.py`: Main entry point in project root
- `build_system/`: Core build system modules
  - `build_utils.py`: Utility functions
  - `build_commands.py`: Build command implementation
  - `test_commands.py`: Test command dispatcher (delegates to tests/test_runner.py)
  - `clean_commands.py`: Clean command implementation
  - `setup_commands.py`: Setup command implementation
  - `ci_commands.py`: CI command implementation
  - `init.sh`: Initialization script
- `tests/`: Test-related modules
  - `test_runner.py`: Main test runner implementation
  - `test_environment_setup.py`: Test environment configuration
  - `test_utils.py`: Test utilities and helpers
  - `test_cli.py`: Command-line interface tests
  - `test_basic.py`: Basic simulator functionality tests
  - `test_instructions.py`: Instruction execution tests

## Integration with CI

GitHub Actions workflows have been updated to use this build system for consistent behavior between local development and CI environments.
