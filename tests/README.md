# LC-3 Simulator Test Architecture

This directory contains a comprehensive pytest test suite for the LC-3 simulator. All test-related functionality is now centralized in this directory.

## Test Organization

### Core Test Modules

- **test_runner.py** - Central test runner used by the build system
- **test_environment_setup.py** - Environment setup and verification
- **test_utils.py** - Common test utilities and helper functions
- **conftest.py** - pytest configuration and fixtures

### Test Categories

1. **CLI Tests** (`test_cli.py`)
   - Command-line interface functionality
   - Interactive mode commands
   - Program loading and execution
   - Error handling in CLI context

2. **Basic Tests** (`test_basic.py`)
   - Simulator initialization and reset
   - Register and memory access
   - Program loading
   - Basic execution control

3. **Instruction Tests** (`test_instructions.py`)
   - Individual instruction implementations
   - Arithmetic instructions (ADD, AND, NOT)
   - Control flow instructions (BR, JMP, JSR)
   - Memory instructions (LD, LDI, LDR, ST, STI, STR, LEA)
   - TRAP instructions

4. **Memory Tests** (`test_memory.py`)
   - Memory addressing modes
   - Memory protection
   - Boundary conditions
   - Memory patterns and stress tests

5. **I/O Tests** (`test_io.py`)
   - TRAP instruction functionality
   - Input/output operations
   - Character handling
   - Error conditions

6. **Integration Tests** (`test_integration.py`)
   - Complete program execution
   - Complex algorithms
   - Performance tests
   - Error handling

### Test Utilities

- **`conftest.py`**: Pytest configuration and fixtures
- **`test_utils.py`**: Utility functions and helper classes
- **`run_tests.py`**: Test runner script with various options

## Running Tests

### Prerequisites

1. **Build the Simulator**:
   ```bash
   mkdir build && cd build
   cmake ..
   cmake --build .
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install pytest pytest-cov pytest-html pytest-xdist numpy pybind11
   ```

### Basic Test Execution

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --basic
python run_tests.py --instructions
python run_tests.py --memory
python run_tests.py --io
python run_tests.py --integration

# Run with coverage
python run_tests.py --coverage

# Run with HTML report
python run_tests.py --html-report

# Run in parallel
python run_tests.py --parallel
```

### Advanced Options

```bash
# Build and test in one command
python run_tests.py --build --install-deps

# Run only unit tests
python run_tests.py --unit-only

# Run including slow tests
python run_tests.py --slow

# Run specific test file
python run_tests.py --test-file tests/test_basic.py

# Verbose output with fail-fast
python run_tests.py --verbose --fail-fast
```

### Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run with markers
pytest tests/ -m "unit"
pytest tests/ -m "not slow"
pytest tests/ -m "instruction or memory"

# Run specific test
pytest tests/test_basic.py::TestSimulatorBasics::test_simulator_creation

# With coverage
pytest tests/ --cov=lc3_simulator --cov-report=html
```

## Test Markers

Tests are marked with the following categories:

- `unit`: Unit tests for individual components
- `integration`: Integration tests for component interaction
- `functional`: Functional tests for complete features
- `slow`: Slow-running tests (usually excluded by default)
- `instruction`: Tests for specific instructions
- `memory`: Memory-related tests
- `register`: Register-related tests
- `io`: Input/output tests
- `trap`: TRAP instruction tests

## Fixtures

### Standard Fixtures

- `simulator`: Fresh LC-3 simulator instance
- `loaded_simulator`: Simulator with a simple test program
- `sample_programs`: Dictionary of sample LC-3 programs
- `instruction_encodings`: Dictionary of instruction encodings

### Custom Fixtures

- `build_simulator`: Ensures simulator is built before tests
- Collection modifiers add appropriate markers based on test names

## Test Data

Test programs and data are defined in fixtures and utilities:

- Simple arithmetic programs
- Control flow examples
- Memory access patterns
- I/O sequences
- Complex algorithms (factorial, Fibonacci, etc.)

## Coverage Requirements

- Minimum 80% code coverage required
- Coverage reports generated in HTML format
- Line-by-line coverage analysis available

## Continuous Integration

The test suite is designed for CI/CD integration:

- Fast execution (< 2 minutes for basic tests)
- Parallel execution support
- Machine-readable output formats
- Coverage reporting
- Performance benchmarks

## Extending Tests

### Adding New Tests

1. Create test file in appropriate category
2. Use existing fixtures and utilities
3. Follow naming conventions (`test_*`)
4. Add appropriate markers
5. Update documentation

### Creating Test Programs

Use the `LC3ProgramBuilder` utility:

```python
builder = LC3ProgramBuilder()
program = (builder
    .add_add(0, 0, imm=1)  # ADD R0, R0, #1
    .add_halt()            # TRAP x25
    .build())
```

### Custom Assertions

Use `LC3TestUtils` for common operations:

```python
# Verify condition codes
assert LC3TestUtils.verify_condition_codes(sim, expected_z=1)

# Set up memory block
LC3TestUtils.setup_memory_block(sim, 0x3000, [0x1021, 0xF025])

# Run until halt
halted, cycles = LC3TestUtils.run_until_halt_or_limit(sim)
```

## Performance Testing

Performance tests use pytest-benchmark:

```bash
# Run benchmarks
python run_tests.py --benchmark

# View benchmark report
open reports/benchmark_report.html
```

## Troubleshooting

### Common Issues

1. **Module not found**: Ensure simulator is built and in Python path
2. **CMake errors**: Check CMake version and C++ compiler
3. **Test failures**: Check simulator build and dependencies
4. **Slow tests**: Use `--parallel` flag or exclude with `-m "not slow"`

### Debug Mode

For debugging test failures:

```bash
# Run with verbose output
pytest tests/ -v -s

# Run single test with debugging
pytest tests/test_basic.py::test_name -v -s --pdb
```

## Reports

Test execution generates several reports:

- **Coverage Report**: `reports/coverage/index.html`
- **Test Report**: `reports/test_report.html`
- **Benchmark Report**: `reports/benchmark_report.html`

All reports are self-contained HTML files for easy sharing and analysis.
