# LC-3 Simulator

A comprehensive implementation of the LC-3 (Little Computer 3) processor simulator with a complete pytest test architecture.

## Overview

This project implements a full LC-3 simulator that can execute LC-3 assembly programs. The simulator includes:

- Complete instruction set implementation
- Memory management and addressing modes
- I/O operations via TRAP instructions
- Comprehensive test suite with pytest
- Python bindings for testing and automation

## Features

### Simulator Core
- **Full LC-3 Instruction Set**: ADD, AND, NOT, BR, JMP, JSR, LD, LDI, LDR, LEA, ST, STI, STR, TRAP
- **Memory Management**: 64K word memory space with proper addressing
- **Register File**: 8 general-purpose registers (R0-R7)
- **Condition Codes**: N, Z, P flags for conditional operations
- **I/O Support**: TRAP instructions for input/output operations

### Test Architecture
- **Comprehensive Test Suite**: 200+ tests covering all simulator functionality
- **Multiple Test Categories**: Unit, integration, functional, and performance tests
- **Python Bindings**: pybind11-based interface for automated testing
- **Coverage Analysis**: Detailed code coverage reporting
- **CI/CD Ready**: Continuous integration support with automated testing

## Building

### Prerequisites
- CMake 3.0 or higher
- C++11 compatible compiler
- Python 3.7+ (for testing)
- pybind11 (for Python bindings)

### Quick Start
```bash
# Complete setup and testing
make setup
make test

# Or manually:
mkdir build && cd build
cmake ..
cmake --build .
```

### With Python Bindings
```bash
# Build with Python bindings for testing
mkdir build && cd build
cmake -DBUILD_PYTHON_BINDINGS=ON ..
cmake --build .
```

## Testing

The project includes a comprehensive pytest test suite with over 200 tests covering all aspects of the simulator.

### Quick Test Run
```bash
# Run basic tests
make test

# Run all tests including slow ones
make test-all

# Run tests with coverage
make coverage
```

### Test Categories

1. **Basic Tests**: Simulator initialization, reset, basic operations
2. **Instruction Tests**: Individual instruction implementations
3. **Memory Tests**: Memory addressing, protection, edge cases
4. **I/O Tests**: TRAP instructions and input/output operations
5. **Integration Tests**: Complete programs and complex scenarios

### Using the Test Runner
```bash
# Install dependencies and run tests
python run_tests.py --install-deps --build

# Run specific test categories
python run_tests.py --instructions  # Instruction tests
python run_tests.py --memory        # Memory tests
python run_tests.py --io            # I/O tests

# Advanced options
python run_tests.py --coverage --html-report --parallel
```

### Test Utilities

The test suite includes comprehensive utilities:

- **LC3TestUtils**: Helper functions for common operations
- **LC3ProgramBuilder**: Programmatic assembly generation
- **LC3Assembler**: Simple assembler for test programs

## Usage

### Running Programs

```cpp
#include "state_machine/state_machine.h"

int main() {
    // Initialize simulator
    LC3Simulator sim;
    
    // Load a program
    std::vector<uint16_t> program = {
        0x1021,  // ADD R0, R0, #1
        0xF025   // TRAP x25 (HALT)
    };
    sim.load_program(program);
    
    // Run the program
    sim.run();
    
    // Check results
    std::cout << "R0 = " << sim.get_register(0) << std::endl;
    
    return 0;
}
```

### Python Interface

```python
import lc3_simulator

# Create simulator
sim = lc3_simulator.LC3Simulator()

# Load and run program
program = [0x1021, 0xF025]  # ADD R0, R0, #1; HALT
sim.load_program(program)
sim.run()

# Check results
print(f"R0 = {sim.get_register(0)}")
print(f"Halted: {sim.is_halted()}")
```

## Architecture

### Directory Structure
```
simulator-lc3/
├── main.cpp              # Main simulator executable
├── CMakeLists.txt         # Build configuration
├── Makefile              # Convenience targets
├── type/                 # Type definitions and constants
├── mem/                  # Memory and register definitions
├── state_machine/        # Core simulator logic
├── python_bindings/      # Python interface
└── tests/                # Comprehensive test suite
    ├── conftest.py       # Test configuration
    ├── test_basic.py     # Basic functionality tests
    ├── test_instructions.py # Instruction tests
    ├── test_memory.py    # Memory tests
    ├── test_io.py        # I/O tests
    ├── test_integration.py # Integration tests
    ├── test_utils.py     # Test utilities
    └── README.md         # Test documentation
```

### Core Components

- **Type System**: Basic types and constants
- **Memory Management**: Memory, registers, and device interfaces
- **State Machine**: Instruction decode and execution logic
- **Python Bindings**: Testing and automation interface

## LC-3 Instruction Set

The simulator implements the complete LC-3 instruction set:

| Instruction | Opcode | Description |
|-------------|--------|-------------|
| ADD | 0001 | Add (register or immediate) |
| AND | 0101 | Bitwise AND (register or immediate) |
| BR | 0000 | Conditional branch |
| JMP | 1100 | Jump |
| JSR/JSRR | 0100 | Jump to subroutine |
| LD | 0010 | Load (PC-relative) |
| LDI | 1010 | Load indirect |
| LDR | 0110 | Load (base+offset) |
| LEA | 1110 | Load effective address |
| NOT | 1001 | Bitwise complement |
| ST | 0011 | Store (PC-relative) |
| STI | 1011 | Store indirect |
| STR | 0111 | Store (base+offset) |
| TRAP | 1111 | System call |

### TRAP Vectors

| Vector | Name | Description |
|--------|------|-------------|
| x20 | GETC | Read character |
| x21 | OUT | Output character |
| x22 | PUTS | Output string |
| x23 | IN | Input character with prompt |
| x25 | HALT | Halt execution |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `make test-all`
5. Submit a pull request

### Test Requirements

- All new features must include tests
- Maintain >80% code coverage
- Tests must pass in parallel execution
- Follow existing test patterns and utilities

## License

This project is open source. See LICENSE file for details.

## References

- [LC-3 Architecture Specification](https://www.cs.utexas.edu/users/fussell/courses/cs310h/lectures/Lecture_10-310h.pdf)
- [Introduction to Computing Systems](https://www.mheducation.com/highered/product/introduction-computing-systems-bits-gates-c-beyond-patt-patel/M9780072467505.html)
