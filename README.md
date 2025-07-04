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
├── build.py            # Unified build system entry point
├── mem/                # Memory subsystem
├── state_machine/      # LC-3 state machine
├── type/               # Type definitions
├── build_system/       # Build system modules
├── tests/              # Test suite with CLI testing
├── docs/               # Documentation
│   ├── development/    # Development documentation
│   │   └── CLI_TESTING_FRAMEWORK.md  # CLI testing documentation
│   └── project/        # Project documentation
└── scripts/            # Utility scripts
```

## Features

- Complete LC-3 instruction set implementation
- Integrated pipeline simulation with performance metrics
- Memory management with proper addressing
- I/O operations via TRAP instructions
- Interactive CLI with support for debugging and inspection
- Comprehensive testing framework including CLI tests
- Comprehensive test suite with Python bindings

## Requirements

- CMake 3.12+
- C++11 compatible compiler
- Python 3.7+ (for testing)
- pybind11 (for Python bindings)

## Testing

The project uses a unified build system for testing:

```bash
# Run all tests
./build.py test --all

# Run specific test categories
./build.py test --category basic
./build.py test --category cli
./build.py test --category instructions

# Generate test coverage report
./build.py test --coverage
```

See [tests/README.md](tests/README.md) for more details on the test structure.

## License

[License information]
