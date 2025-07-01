# LC-3 Simulator with Integrated Pipeline Extension

A comprehensive implementation of the LC-3 (Little Computer 3) processor simulator with **integrated pipeline simulation and performance analysis capabilities**.

## 🧭 Navigation & Quick Start

**New to this project?** Start here:
- 📍 **[PROJECT_NAVIGATION.md](PROJECT_NAVIGATION.md)** ← **Your complete guide to understanding this project**
- 🎯 **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** ← Quick start and overview
- 🗺️ **[VISUAL_PROJECT_MAP.md](VISUAL_PROJECT_MAP.md)** ← Visual directory structure
- 🔄 **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** ← Developer workflows

**Want to build right now?**
```bash
python lc3_build.py build                    # Modern unified CLI
./build/simulator-lc3 test_programs/hello.asm
```

## Overview

This project implements a full LC-3 simulator that can execute LC-3 assembly programs with advanced pipeline simulation features. The simulator includes:

- Complete instruction set implementation with **real-time pipeline analysis**
- **Integrated custom instruction pipeline configuration**
- Memory management and addressing modes
- I/O operations via TRAP instructions
- **Performance metrics and hazard detection**
- Comprehensive test suite with pytest
- Python bindings for testing and automation

## 🚀 New: Integrated Pipeline Extension

### Key Pipeline Features
- **Directly Integrated**: Pipeline functionality built into the LC-3 core (no external modules)
- **Real-time Performance Analysis**: CPI, IPC, pipeline efficiency tracking
- **Configurable Pipeline**: Customizable depth, forwarding, branch prediction
- **Hazard Detection**: Automatic detection of data, control, and structural hazards
- **Interactive Analysis**: Command-line interface for pipeline inspection

### Quick Pipeline Demo
```bash
# Run with pipeline mode enabled
./simulator-lc3 --pipeline program.obj

# Interactive mode with pipeline analysis
./simulator-lc3 --pipeline --interactive

# Available pipeline commands:
(lc3-sim) pipeline    # Show pipeline status
(lc3-sim) metrics     # Display performance metrics
(lc3-sim) config      # Show pipeline configuration
```

## Features

### Simulator Core
- **Full LC-3 Instruction Set**: ADD, AND, NOT, BR, JMP, JSR, LD, LDI, LDR, LEA, ST, STI, STR, TRAP
- **Memory Management**: 64K word memory space with proper addressing
- **Register File**: 8 general-purpose registers (R0-R7)
- **Condition Codes**: N, Z, P flags for conditional operations
- **I/O Support**: TRAP instructions for input/output operations

### Integrated Pipeline Analysis
- **Real-time Metrics**: CPI (Cycles Per Instruction), IPC (Instructions Per Cycle)
- **Hazard Detection**: RAW, WAW, WAR data hazards; control and structural hazards
- **Pipeline Configuration**: 5-stage default, customizable depth and features
- **Performance Monitoring**: Stall cycles, memory accesses, branch statistics
- **Forwarding Control**: Enable/disable data forwarding to study hazard effects
- **Branch Prediction**: Configurable branch prediction and penalty settings

### Test Architecture
- **Comprehensive Test Suite**: 200+ tests covering all simulator functionality
- **Multiple Test Categories**: Unit, integration, functional, and performance tests
- **Python Bindings**: pybind11-based interface for automated testing
- **Coverage Analysis**: Detailed code coverage reporting
- **CI/CD Ready**: Optimized continuous integration with Python 3.9/3.11 support

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

### Pipeline Extensions
```bash
# Build with pipeline performance analysis
cmake -S . -B build -DBUILD_PIPELINE_EXTENSIONS=ON -DBUILD_PYTHON_BINDINGS=ON
cmake --build build

# Run pipeline performance demo
pip install matplotlib numpy seaborn
python pipeline_demo.py
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

<task id="shell: Build Python Bindings">
{
	"label": "Build Python Bindings",
	"type": "shell",
	"command": "cmake",
	"args": [
		"--build",
		".",
		"--target",
		"python_bindings"
	],
	"group": "build",
	"detail": "Build Python bindings for LC-3 Simulator",
	"options": {
		"cwd": "${workspaceFolder}"
	}
}
</task>
<task id="shell: Run Pipeline Demo">
{
	"label": "Run Pipeline Demo",
	"type": "shell",
	"command": "python",
	"args": [
		"pipeline_demo.py"
	],
	"group": "test",
	"detail": "Run comprehensive pipeline performance testing demo",
	"dependsOn": "Build Python Bindings",
	"options": {
		"cwd": "${workspaceFolder}"
	}
}
</task>
<task id="shell: Run Simple Pipeline Example">
{
	"label": "Run Simple Pipeline Example",
	"type": "shell",
	"command": "python",
	"args": [
		"pipeline_simple_example.py"
	],
	"group": "test",
	"detail": "Run simple pipeline testing example",
	"dependsOn": "Build Python Bindings",
	"options": {
		"cwd": "${workspaceFolder}"
	}
}
</task>

## Pipeline Usage and Examples

### Command Line Usage

```bash
# Basic simulation (traditional mode)
./simulator-lc3 program.obj

# Pipeline mode - shows real-time performance metrics
./simulator-lc3 --pipeline program.obj

# Interactive pipeline mode
./simulator-lc3 --pipeline --interactive

# Verbose pipeline output
./simulator-lc3 --pipeline --verbose program.obj
```

### Interactive Pipeline Commands

When in pipeline mode (`--pipeline --interactive`), additional commands are available:

```bash
(lc3-sim) pipeline    # Show current pipeline status and configuration
(lc3-sim) metrics     # Display comprehensive performance metrics
(lc3-sim) config      # Show detailed pipeline configuration
(lc3-sim) step        # Execute one instruction with pipeline analysis
```

### Pipeline Configuration Example

```c
// Example: Customize pipeline settings
#include "mem/control_store.h"

int main() {
    // Initialize with default 5-stage pipeline
    lc3_pipeline_init();

    // Customize configuration
    lc3_pipeline_config.forwarding_enabled = false;  // Disable forwarding
    lc3_pipeline_config.branch_penalty = 3;          // 3-cycle branch penalty

    // Issue instructions and analyze performance
    lc3_pipeline_issue_instruction(0x1220, 0x3000);  // ADD R1, R0, #0
    lc3_pipeline_issue_instruction(0x1041, 0x3001);  // ADD R2, R1, #1 (RAW hazard!)

    // Execute pipeline cycles
    for (int i = 0; i < 10; i++) {
        lc3_pipeline_cycle();
    }

    // Analyze results
    lc3_pipeline_metrics_t metrics;
    lc3_pipeline_get_metrics(&metrics);
    printf("Performance: CPI=%.3f, Hazards=%llu, Stalls=%llu\n",
           metrics.cpi, metrics.data_hazards, metrics.stall_cycles);

    return 0;
}
```

### Performance Analysis Output

```
Pipeline Performance Metrics:
  Total Instructions: 100
  Total Cycles: 134
  CPI (Cycles per Instruction): 1.340
  IPC (Instructions per Cycle): 0.746
  Pipeline Efficiency: 74.60%
  Stall Cycles: 29
  Data Hazards: 12
  Control Hazards: 8
  Structural Hazards: 0
```

## Documentation

### Quick Reference
- [**PIPELINE_INTEGRATION_GUIDE.md**](PIPELINE_INTEGRATION_GUIDE.md) - Comprehensive pipeline documentation
- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Code organization
- [CODE_STYLE](CODE_STYLE) - Coding standards
- [Test Reports](reports/) - Test coverage and analysis

### Pipeline Documentation
For detailed information about the integrated pipeline extension, see:
- **[Pipeline Integration Guide](PIPELINE_INTEGRATION_GUIDE.md)** - Complete pipeline documentation
- **[Pipeline Features Summary](PIPELINE_FEATURES.md)** - Feature overview
- **Pipeline Examples**: `pipeline_demo_integrated.c`, `test_pipeline_integration.c`
