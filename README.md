# LC-3 Simulator with Pipeline Extensions

A comprehensive implementation of the Little Computer 3 (LC-3) processor simulator with integrated pipeline simulation capabilities.

## Quick Start

```bash
# Build the project
mkdir build && cd build
cmake ..
cmake --build .

# Run a program
./simulator-lc3 path/to/program.obj

# Run with pipeline analysis
./simulator-lc3 --pipeline path/to/program.obj
```

## Documentation

All detailed documentation is located in the `/docs` directory:

- [Documentation Guide](docs/DOCUMENTATION_GUIDE.md) - Start here for navigating all documentation
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Overview of code organization
- [Development Workflow](docs/development/DEVELOPMENT_WORKFLOW.md) - Guide for contributors

## Project Organization

```
simulator-lc3/
├── src/                 # Source code
│   ├── core/            # Core simulator components
│   │   ├── memory/      # Memory subsystem
│   │   ├── pipeline/    # Pipeline simulation
│   │   ├── state_machine/ # LC-3 state machine
│   │   └── types/       # Type definitions
├── python_bindings/     # Python interface
├── tests/               # Test suite
└── docs/                # Documentation
```

## Features

- Complete LC-3 instruction set implementation
- Integrated pipeline simulation with performance metrics
- Memory management with proper addressing
- I/O operations via TRAP instructions
- Comprehensive test suite with Python bindings

## Requirements

- CMake 3.12+
- C++11 compatible compiler
- Python 3.7+ (for testing)
- pybind11 (for Python bindings)

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_basic.py
```

## License

[License information]
