# LC-3 Simulator CLI Testing Framework

This document describes the Command Line Interface (CLI) testing framework for the LC-3 Simulator. The framework provides comprehensive testing of the simulator-lc3 binary's CLI functionality.

## Overview

The `test_cli.py` file implements a robust testing framework for validating the behavior of the LC-3 simulator when used as a command-line tool. This ensures that the binary operates correctly in both interactive and non-interactive modes.

## Key Features

- **Binary Verification**: Tests that the simulator binary exists and is executable
- **Basic Invocation Testing**: Verifies the simulator can be invoked without arguments
- **Command Testing**: Tests all interactive mode commands (step, run, mem, reg, etc.)
- **Program Loading**: Tests that programs can be loaded from files
- **Program Execution**: Tests program execution in both interactive and non-interactive modes
- **Error Handling**: Verifies the simulator handles invalid commands gracefully

## Test Structure

The test suite is organized into a class called `TestCLI` which implements:

1. **Helper Methods**:
   - `run_simulator()`: Wrapper for running the simulator binary with specified arguments and inputs

2. **Test Fixtures**:
   - `verify_simulator_binary`: Ensures the simulator binary exists
   - `sample_program_file`: Creates a test LC-3 program file for testing

3. **Test Cases**:
   - Basic invocation tests
   - Interactive command tests
   - Program loading and execution tests

## Sample Tests

- `test_basic_invocation`: Verifies the simulator starts in interactive mode without errors
- `test_help_command`: Verifies the help command works and displays all available commands
- `test_load_program`: Tests loading a program from a file and executing it
- `test_step_command`: Tests stepping through program execution in interactive mode
- `test_run_command`: Tests running a full program in interactive mode
- `test_memory_command`: Tests memory inspection in interactive mode
- `test_reset_command`: Tests the simulator reset functionality

## Running CLI Tests

CLI tests can be run using the build system:

```bash
./build.py test --category cli
```

Or using pytest directly:

```bash
python -m pytest tests/test_cli.py -v
```

## Extending the Tests

To add new CLI tests:

1. Add a new test method to the `TestCLI` class in `tests/test_cli.py`
2. Use the `run_simulator()` method to invoke the simulator with appropriate arguments
3. Assert on the expected output or behavior

Example:

```python
def test_new_feature(self):
    """Test a new simulator CLI feature."""
    returncode, stdout, _ = self.run_simulator(
        input_data="new_command\nquit\n"
    )

    assert returncode == 0
    assert "Expected output" in stdout
```

## Integration with Test Runner

The CLI tests are fully integrated with the central test runner and can be invoked through the build system's test command. They are also included in the comprehensive test suite when running all tests.
