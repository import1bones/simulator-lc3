# Build System Documentation

This document describes the build system configuration and options for the LC-3 simulator project.

## Build Systems

The project supports two build systems:

### 1. CMake (Primary)
CMake is the primary build system and is required for Python bindings.

**Configuration:**
```bash
mkdir build && cd build
cmake -DBUILD_PYTHON_BINDINGS=ON ..
cmake --build . --parallel
```

**CMake Options:**
- `BUILD_PYTHON_BINDINGS=ON/OFF` - Enable Python bindings (default: OFF)
- `CMAKE_BUILD_TYPE=Debug/Release` - Build configuration (default: Release)
- `CMAKE_CXX_STANDARD=11/14/17/20` - C++ standard (default: 11)

### 2. Makefile (Alternative)
Alternative build system for simpler builds without Python bindings.

**Usage:**
```bash
make help      # Show available targets
make all       # Build everything
make clean     # Clean build artifacts
make install   # Install simulator
```

## Automated Building

### Using Test Runner (Recommended)
```bash
# Check environment and build
python3 scripts/run_tests.py --check-env --build

# Install dependencies and build
python3 scripts/run_tests.py --install-deps --build
```

### CI/CD Integration
The GitHub Actions workflows use the test runner for consistent builds:
```yaml
- name: Build C++ simulator with Python bindings
  run: python3 scripts/run_tests.py --build
```

## Build Dependencies

### Required
- CMake 3.0 or higher
- C++11 compatible compiler (g++, clang++, MSVC)
- Python 3.7+ (for bindings and testing)

### Optional
- pybind11 (for Python bindings)
- pytest (for testing)
- Doxygen (for documentation generation)

## Build Outputs

### C++ Simulator
- **Location:** `build/lc3-simulator` (or `build/lc3-simulator.exe` on Windows)
- **Usage:** `./build/lc3-simulator [program.obj]`

### Python Bindings
- **Location:** `build/python_bindings/lc3_simulator.so` (or `.pyd` on Windows)
- **Usage:** Import as `import lc3_simulator` in Python tests

## Troubleshooting

### Common Issues

**CMake not found:**
```bash
# Install CMake (Ubuntu/Debian)
sudo apt-get install cmake

# Install CMake (macOS)
brew install cmake

# Install CMake (Windows)
# Download from https://cmake.org/download/
```

**Compiler not found:**
```bash
# Install build tools (Ubuntu/Debian)
sudo apt-get install build-essential

# Install build tools (macOS)
xcode-select --install

# Install build tools (Windows)
# Install Visual Studio or Visual Studio Build Tools
```

**Python binding errors:**
```bash
# Install pybind11
pip install pybind11[global]

# Or use the test runner
python3 scripts/run_tests.py --install-deps
```

### Build Verification
```bash
# Validate entire build system
python3 scripts/validate_project.py

# Check environment setup
python3 scripts/run_tests.py --check-env
```

## Cross-Platform Notes

### Windows
- Use Visual Studio or Visual Studio Build Tools
- CMake automatically detects MSVC
- Python bindings create `.pyd` files instead of `.so`

### macOS
- Xcode command line tools required
- CMake supports both Xcode and Unix Makefiles generators
- May need to specify Python version explicitly

### Linux
- Standard build tools (gcc, make) required
- CMake supports various generators (Unix Makefiles, Ninja)
- Python development headers may be needed: `python3-dev`

## Advanced Configuration

### Custom Build Directory
```bash
cmake -B custom_build -DBUILD_PYTHON_BINDINGS=ON
cmake --build custom_build
```

### Debug Builds
```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . --config Debug
```

### Installation
```bash
cmake --install . --prefix /usr/local
```

For more build options and troubleshooting, see the [main documentation hub](README.md).
