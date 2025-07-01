# LC-3 Simulator Project Overview

## 🎯 What is this project?

This is a **comprehensive LC-3 (Little Computer 3) processor simulator** with advanced features including pipeline simulation, performance analysis, and cross-platform build support. The project is designed for educational use, research, and development of computer architecture concepts.

## 🚀 Quick Start

### Prerequisites
- **C++ Compiler**: GCC, Clang, or MSVC
- **CMake**: Version 3.12 or higher
- **Python**: Version 3.8 or higher (for testing and bindings)

### Build and Run (Simple)
```bash
# Clone and navigate to project
cd simulator-lc3

# Quick build using the unified CLI
python lc3_build.py build

# Run the simulator
./build/simulator-lc3

# Run with sample program
./build/simulator-lc3 test_programs/hello.asm
```

### Build and Test (Comprehensive)
```bash
# Full build with testing
python lc3_build.py full-build --test

# Or use traditional CMake
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build .
```

## 📁 Project Structure at a Glance

```
simulator-lc3/
├── 🏗️  BUILD SYSTEM
│   ├── lc3_build.py          # 🆕 Unified CLI (use this!)
│   ├── build_system/         # 🆕 Modular build framework
│   ├── CMakeLists.txt        # CMake configuration
│   └── requirements.txt     # Python dependencies
│
├── 💻  CORE SIMULATOR
│   ├── main.cpp             # Main executable
│   ├── mem/                 # Memory management
│   ├── state_machine/       # Processor state logic
│   ├── type/                # Type definitions & opcodes
│   └── python_bindings/     # Python-C++ interface
│
├── 🧪  TESTING & VALIDATION
│   ├── tests/               # Comprehensive test suite
│   ├── test_programs/       # Sample LC-3 programs
│   └── scripts/             # Development tools
│
└── 📚  DOCUMENTATION & REPORTS
    ├── docs/                # Technical documentation
    ├── reports/             # Test and coverage reports
    └── analysis/            # Performance analysis tools
```

## 🎛️ Key Features

### Core Simulator
- ✅ **Complete LC-3 ISA**: All 15 instructions implemented
- ✅ **Memory Management**: 64K word memory space
- ✅ **I/O Support**: TRAP instructions for system calls
- ✅ **Register File**: 8 general-purpose registers + condition codes

### Advanced Features
- 🚀 **Pipeline Simulation**: Real-time pipeline analysis
- 📊 **Performance Metrics**: CPI, IPC, hazard detection
- 🔧 **Python Bindings**: Automated testing and analysis
- 🌐 **Cross-Platform**: Windows, Linux, macOS support

## 🛠️ Development Workflow

### 1. Make Changes
```bash
# Edit C++ code in mem/, state_machine/, type/, or main.cpp
# Edit tests in tests/
# Edit sample programs in test_programs/
```

### 2. Build and Test
```bash
# Quick build
python lc3_build.py build

# Full build with tests
python lc3_build.py full-build --test

# Run specific tests
python lc3_build.py test --suite basic
python lc3_build.py test --suite memory
python lc3_build.py test --suite instructions
```

### 3. Package and Deploy
```bash
# Create distribution package
python lc3_build.py package

# Generate coverage report
python lc3_build.py test --coverage
```

## 📖 Key Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Detailed project description and features |
| `PROJECT_STRUCTURE.md` | Complete directory structure breakdown |
| `BUILD_ARCHITECTURE_SUMMARY.md` | Build system architecture details |
| `BUILD_SYSTEM_MIGRATION.md` | Migration guide for build system |
| `build_system/README.md` | Modular build system documentation |

## 🔧 Command Reference

### Using the Unified CLI (`lc3_build.py`)

```bash
# Information
python lc3_build.py info                    # Project information
python lc3_build.py info --system          # System information
python lc3_build.py info --deps            # Dependencies status

# Building
python lc3_build.py build                  # Standard build
python lc3_build.py build --clean          # Clean build
python lc3_build.py build --build-type Release  # Release build

# Testing
python lc3_build.py test                   # Run all tests
python lc3_build.py test --suite basic     # Run specific test suite
python lc3_build.py test --coverage        # With coverage analysis

# Full Workflow
python lc3_build.py full-build --test --package  # Complete workflow
```

### Using Traditional Tools

```bash
# CMake (manual)
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build .

# Python tests (manual)
pytest tests/ -v

# Legacy scripts (still supported)
./build_and_test.sh    # Unix/Linux/macOS
./build_and_test.bat   # Windows
python build_and_test.py  # Cross-platform Python
```

## 🎯 Common Tasks

### I want to...

**Run a sample program:**
```bash
python lc3_build.py build
./build/simulator-lc3 test_programs/hello.asm
```

**Add a new instruction:**
1. Edit `type/opcode.h` to add opcode
2. Edit `state_machine/states.cpp` to add implementation
3. Add test in `tests/test_instructions.py`
4. Run `python lc3_build.py test --suite instructions`

**Add performance analysis:**
1. Edit code in relevant modules
2. Add test in `tests/test_isa_performance.py`
3. Run `python lc3_build.py test --suite performance`

**Debug a failing test:**
```bash
python lc3_build.py test --suite basic -v
# Or run pytest directly
pytest tests/test_basic.py::specific_test -v -s
```

**Generate documentation:**
```bash
python scripts/auto_documentation.py
```

## 🚨 Troubleshooting

### Build Issues
- **CMake not found**: Install CMake 3.12+
- **Compiler errors**: Ensure GCC/Clang/MSVC is properly installed
- **Python binding errors**: Check pybind11 installation

### Test Issues
- **Tests failing**: Run `python lc3_build.py build --clean` first
- **Import errors**: Ensure Python bindings are built (`-DBUILD_PYTHON_BINDINGS=ON`)

### Platform-Specific
- **Windows**: Use PowerShell or Command Prompt
- **Linux**: Ensure build-essential is installed
- **macOS**: Install Xcode Command Line Tools

## 🤝 Contributing

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes** following the code style in `CODE_STYLE`
4. **Test thoroughly**: `python lc3_build.py full-build --test`
5. **Submit pull request**

## 📞 Support

- **Documentation**: Check `docs/` directory
- **Issues**: Use GitHub issues for bug reports
- **Questions**: Check existing documentation first

---

**Next Steps**: Read `README.md` for detailed features, then dive into `PROJECT_STRUCTURE.md` for complete architecture understanding.
