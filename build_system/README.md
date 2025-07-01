# LC-3 Simulator Build System

A comprehensive, cross-platform build architecture for the LC-3 computer architecture simulator.

## Overview

This build system provides a unified, modular approach to building, testing, and packaging the LC-3 simulator across Windows, Linux, and macOS platforms. It replaces the previous collection of shell scripts with a robust Python-based architecture that supports advanced features like dependency management, automated testing, coverage reporting, and CI/CD integration.

## Features

### 🏗️ Cross-Platform Build Support
- **Windows**: Visual Studio 2019+, MinGW, Clang
- **Linux**: GCC, Clang on Ubuntu, CentOS, Fedora, Arch, openSUSE
- **macOS**: Xcode Command Line Tools, Homebrew packages

### 🔧 Modular Architecture
- **Core system**: Platform detection, configuration management
- **Dependency management**: Automatic system and Python package resolution
- **Build orchestration**: CMake and Python build coordination
- **Testing framework**: Comprehensive test execution with reporting
- **Package generation**: Multiple distribution formats
- **CI/CD integration**: Automated workflow generation

### 🚀 Advanced Capabilities
- Parallel builds and test execution
- Code coverage analysis with HTML reports
- Performance benchmarking and tracking
- Automated dependency installation
- Multi-format package creation (ZIP, TAR.GZ, Wheel)
- GitHub Actions and GitLab CI configuration generation
- Build caching and incremental builds

## Quick Start

### Prerequisites

- **Python 3.8+** (required)
- **CMake 3.12+** (required)
- **Git** (required)
- **C++ Compiler** (platform-specific)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd simulator-lc3
   ```

2. **Check system compatibility**:
   ```bash
   python lc3_build.py info --system
   ```

3. **Install dependencies**:
   ```bash
   python lc3_build.py deps --install
   ```

### Basic Usage

```bash
# Build the project
python lc3_build.py build

# Run tests
python lc3_build.py test

# Create packages
python lc3_build.py package --all

# Full build cycle
python lc3_build.py full-build --clean --test --package
```

## Command Reference

### Build Commands

#### `build` - Build the project
```bash
python lc3_build.py build [options]

Options:
  --clean                 Clean before building
  --build-type TYPE       Debug, Release, RelWithDebInfo, MinSizeRel
  --platform PLATFORM     windows, linux, macos (auto-detected)
  --architecture ARCH     x86_64, x86, arm64, arm
  --generator GEN         CMake generator to use
  --no-python            Disable Python bindings
  --configure-only       Only configure, don't build
  --cmake-args ARGS      Additional CMake arguments
```

**Examples**:
```bash
# Debug build (default)
python lc3_build.py build

# Release build with clean
python lc3_build.py build --clean --build-type Release

# Configure only
python lc3_build.py build --configure-only
```

#### `test` - Run test suites
```bash
python lc3_build.py test [options]

Options:
  --categories CATS      Test categories: basic, memory, instructions, 
                        pipeline, integration, io, performance, all
  --coverage            Generate coverage report
  --html-report         Generate HTML test report
  --parallel            Run tests in parallel
  --timeout SECONDS     Test timeout (default: 300)
  --no-deps-check       Skip dependency verification
```

**Examples**:
```bash
# Run basic tests
python lc3_build.py test --categories basic

# Comprehensive testing with coverage
python lc3_build.py test --categories all --coverage --html-report

# Parallel test execution
python lc3_build.py test --parallel
```

#### `package` - Create distribution packages
```bash
python lc3_build.py package [options]

Options:
  --binary              Create binary package
  --source              Create source package
  --wheel               Create Python wheel
  --all                 Create all package types
  --version VERSION     Override version
  --output-dir DIR      Output directory
```

**Examples**:
```bash
# Create binary package
python lc3_build.py package --binary

# Create all packages with custom version
python lc3_build.py package --all --version 2.0.0
```

#### `deps` - Manage dependencies
```bash
python lc3_build.py deps [options]

Options:
  --check               Check all dependencies
  --install             Install missing dependencies
  --report              Generate dependency report
  --requirements FILE   Install from requirements file
```

#### `ci-setup` - Configure CI/CD
```bash
python lc3_build.py ci-setup PLATFORM [options]

Platforms:
  github                GitHub Actions
  gitlab                GitLab CI

Options:
  --matrix-platforms    Platforms for build matrix
  --python-versions     Python versions to test
  --no-coverage         Disable coverage in CI
  --no-performance      Disable performance tests
```

**Examples**:
```bash
# Set up GitHub Actions
python lc3_build.py ci-setup github

# Custom GitLab CI with specific platforms
python lc3_build.py ci-setup gitlab --matrix-platforms linux windows
```

#### `full-build` - Complete build cycle
```bash
python lc3_build.py full-build [options]

Options:
  --clean               Clean before building
  --test                Run tests after building
  --package             Create packages after testing
  --test-categories     Test categories to run
  --coverage            Generate coverage report
```

#### `clean` - Clean build artifacts
```bash
python lc3_build.py clean [options]

Options:
  --all                 Clean everything
  --build               Clean build directory
  --python              Clean Python artifacts
  --dist                Clean distribution packages
```

#### `info` - Show system information
```bash
python lc3_build.py info [options]

Options:
  --config              Show build configuration
  --dependencies        Show dependency status
  --system              Show system information
  --all                 Show all information
```

## Architecture Overview

### Module Structure

```
build_system/
├── __init__.py         # Package initialization and exports
├── core.py             # Core classes and platform detection
├── dependencies.py     # Dependency management
├── builders.py         # Build orchestration
├── testing.py          # Test execution and reporting
├── packaging.py        # Package generation
└── ci.py              # CI/CD configuration generation
```

### Core Classes

#### `BuildConfiguration`
Central configuration for all build operations:
```python
from build_system import BuildConfiguration, BuildType, BuildPlatform

config = BuildConfiguration(
    platform=BuildPlatform.LINUX,
    build_type=BuildType.RELEASE,
    generator="Unix Makefiles"
)
```

#### `LC3Builder`
High-level build orchestrator:
```python
from build_system import create_builder

builder = create_builder()
builder.configure()
builder.build()
```

#### `TestRunner`
Comprehensive test execution:
```python
from build_system.testing import TestRunner

runner = TestRunner(logger, platform)
results = runner.run_suite("basic", coverage=True)
```

#### `PackageManager`
Multi-format package creation:
```python
from build_system.packaging import PackageManager

manager = PackageManager(config, project, logger)
binary_pkg = manager.create_binary_package()
wheel_pkg = manager.create_python_wheel()
```

## Advanced Usage

### Custom Build Configurations

```python
from build_system import (
    create_builder, 
    BuildConfiguration, 
    BuildType, 
    ProjectSettings
)

# Custom configuration
config = BuildConfiguration(
    build_type=BuildType.RELEASE,
    cmake_args=["-DENABLE_OPTIMIZATION=ON"],
    env_vars={"CC": "clang", "CXX": "clang++"}
)

# Custom project settings
project = ProjectSettings(
    name="LC3Simulator",
    version="2.0.0",
    enable_coverage=True,
    enable_sanitizers=True
)

# Create builder with custom settings
builder = create_builder(config=config, project=project)
```

### Programmatic Test Execution

```python
from build_system.testing import TestRunner, TestReportGenerator

# Initialize test runner
runner = TestRunner(logger, platform)

# Run specific test suites
results = {
    "basic": runner.run_suite("basic"),
    "memory": runner.run_suite("memory", parallel=True),
    "performance": runner.run_suite("performance", timeout=600)
}

# Generate reports
reporter = TestReportGenerator(logger, project_root)
reporter.generate_summary_report(results)
reporter.print_summary(results)
```

### Custom Package Creation

```python
from build_system.packaging import PackageSpec, PackageFormat

# Custom package specification
spec = PackageSpec(
    name="LC3Simulator-Custom",
    version="2.0.0",
    format=PackageFormat.TAR_XZ,
    include_files=["build/simulator-lc3*", "docs/**/*"],
    exclude_patterns=["**/*.tmp", "**/__pycache__/**"],
    metadata={"build_type": "optimized", "features": ["gui", "debugger"]}
)

# Create package
package_path = package_manager.create_binary_package(spec)
```

### CI/CD Configuration Generation

```python
from build_system.ci import GitHubActionsGenerator, CIConfig, BuildMatrix

# Configure build matrix
matrix = BuildMatrix(
    platforms=[BuildPlatform.LINUX, BuildPlatform.WINDOWS],
    python_versions=["3.9", "3.10", "3.11"],
    build_types=[BuildType.DEBUG, BuildType.RELEASE]
)

# Create CI configuration
ci_config = CIConfig(
    project_name="LC3Simulator",
    platforms=[CIPlatform.GITHUB_ACTIONS],
    build_matrix=matrix
)

# Generate workflow
generator = GitHubActionsGenerator(ci_config, logger)
workflow_file = generator.generate_main_workflow()
```

## Platform-Specific Details

### Windows

**Requirements**:
- Visual Studio 2019 or newer (Build Tools sufficient)
- Windows 10 version 1903 or newer
- PowerShell 5.1 or newer

**Automatic Setup**:
```bash
# Check Visual Studio installation
python lc3_build.py deps --check

# Install Python dependencies
python lc3_build.py deps --install
```

**Manual Setup**:
1. Install Visual Studio Build Tools 2019+
2. Install Python 3.8+ from python.org
3. Install Git for Windows

### Linux

**Requirements**:
- GCC 7+ or Clang 6+
- CMake 3.12+
- Python 3.8+

**Automatic Setup**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential cmake python3 python3-pip git

# CentOS/RHEL/Fedora
sudo dnf install gcc gcc-c++ cmake python3 python3-pip git

# Install Python dependencies
python3 lc3_build.py deps --install
```

### macOS

**Requirements**:
- Xcode Command Line Tools
- Homebrew (recommended)
- Python 3.8+

**Setup**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install dependencies via Homebrew
brew install cmake python3 git

# Install Python dependencies
python3 lc3_build.py deps --install
```

## Testing Framework

### Test Categories

The build system organizes tests into logical categories:

- **`basic`**: Core functionality tests
- **`memory`**: Memory management and allocation tests
- **`instructions`**: Instruction execution and decoding tests
- **`pipeline`**: Pipeline performance and behavior tests
- **`integration`**: End-to-end integration tests
- **`io`**: Input/output and file handling tests
- **`performance`**: Performance benchmarking tests

### Coverage Reporting

Coverage analysis is integrated with multiple output formats:

```bash
# Generate coverage with HTML report
python lc3_build.py test --coverage --html-report

# Coverage files generated:
# - coverage.json (machine-readable)
# - htmlcov/ (HTML report)
# - coverage.xml (Cobertura format for CI)
```

### Test Reports

Multiple test report formats are supported:

- **JSON**: Machine-readable test results
- **HTML**: Interactive test reports with filtering
- **Console**: Colored terminal output with summaries
- **JUnit XML**: CI/CD integration format

## Package Distribution

### Supported Formats

- **Binary packages**: Platform-specific executables and libraries
- **Source packages**: Complete source distribution
- **Python wheels**: Python package installation
- **Container images**: Docker/Podman containers (planned)

### Package Contents

#### Binary Package
- Compiled simulator executable
- Python bindings (if enabled)
- Runtime libraries
- Documentation
- Sample programs
- License files

#### Source Package
- Complete source code
- Build system
- Test suites
- Documentation
- Configuration files

### Distribution Workflow

```bash
# Create release distribution
python lc3_build.py package --all --version 2.0.0

# Generated files:
# dist/
# ├── LC3Simulator-2.0.0-linux-x86_64.tar.gz
# ├── LC3Simulator-2.0.0-src.tar.gz
# ├── lc3_simulator-2.0.0-py3-none-any.whl
# ├── checksums.txt
# └── RELEASE_NOTES.md
```

## CI/CD Integration

### GitHub Actions

The build system generates comprehensive GitHub Actions workflows:

```yaml
# Generated .github/workflows/ci.yml includes:
- Multi-platform build matrix (Windows, Linux, macOS)
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)
- Parallel test execution
- Coverage reporting
- Artifact collection
- Automated releases on tags
```

### GitLab CI

GitLab CI/CD configuration with similar capabilities:

```yaml
# Generated .gitlab-ci.yml includes:
- Docker-based builds
- Caching for faster builds
- Parallel job execution
- Coverage integration
- Package artifact management
```

### Custom CI Integration

The build system can be integrated with any CI/CD platform:

```bash
# Generic CI script
python lc3_build.py deps --install
python lc3_build.py build --build-type Release
python lc3_build.py test --categories all --coverage
python lc3_build.py package --all
```

## Configuration

### Environment Variables

The build system respects the following environment variables:

```bash
# Build configuration
LC3_BUILD_TYPE=Release|Debug|RelWithDebInfo|MinSizeRel
LC3_GENERATOR="Visual Studio 17 2022"|"Unix Makefiles"|"Ninja"
LC3_PLATFORM=windows|linux|macos
LC3_ARCHITECTURE=x86_64|x86|arm64|arm

# Feature flags
LC3_PYTHON_BINDINGS=ON|OFF
LC3_BUILD_TESTS=ON|OFF
LC3_ENABLE_COVERAGE=ON|OFF

# Paths
LC3_BUILD_DIR=/path/to/build
LC3_INSTALL_PREFIX=/path/to/install
LC3_PYTHON_EXE=/path/to/python

# Test configuration
LC3_TEST_PARALLEL=ON|OFF
LC3_TEST_TIMEOUT=300
LC3_TEST_CATEGORIES=basic,memory,instructions
```

### Configuration Files

Support for configuration files is planned for future releases:

```toml
# pyproject.toml [tool.lc3_build] section
[tool.lc3_build]
build_type = "Release"
enable_python_bindings = true
enable_coverage = true
parallel_jobs = 4

[tool.lc3_build.test]
categories = ["basic", "memory", "instructions"]
parallel = true
coverage = true
html_report = true

[tool.lc3_build.package]
formats = ["binary", "wheel"]
include_docs = true
```

## Troubleshooting

### Common Issues

1. **Python module import fails**
   ```bash
   # Symptoms: ImportError when running tests
   # Solution: Rebuild Python bindings
   python lc3_build.py build --clean
   ```

2. **CMake configuration errors**
   ```bash
   # Symptoms: CMake configuration fails
   # Solution: Check dependencies and generator
   python lc3_build.py deps --check
   python lc3_build.py build --generator "Unix Makefiles"
   ```

3. **Test failures on specific platforms**
   ```bash
   # Symptoms: Tests pass locally but fail in CI
   # Solution: Use verbose mode and check platform differences
   python lc3_build.py test --verbose --categories basic
   ```

4. **Permission errors during build**
   ```bash
   # Symptoms: Permission denied errors
   # Solution: Check file permissions and build directory
   python lc3_build.py clean --all
   python lc3_build.py build
   ```

### Debug Mode

Enable comprehensive debugging:

```bash
# Maximum verbosity
python lc3_build.py --verbose build --verbose

# System diagnostics
python lc3_build.py info --all

# Dependency analysis
python lc3_build.py deps --report
```

### Log Files

The build system generates detailed logs:

```
build/
├── cmake_config.log      # CMake configuration log
├── build.log            # Build process log
└── test_results/        # Test execution logs
    ├── basic.log
    ├── memory.log
    └── ...
```

## Development

### Contributing to the Build System

The build system is designed to be extensible and maintainable:

1. **Adding new platforms**:
   - Extend `PlatformDetector` in `core.py`
   - Add platform-specific logic in `dependencies.py`
   - Update CI generators in `ci.py`

2. **Adding new test categories**:
   - Update `TestRunner._define_test_suites()` in `testing.py`
   - Add corresponding test files in `tests/`
   - Update documentation

3. **Adding new package formats**:
   - Extend `PackageFormat` enum in `packaging.py`
   - Implement format-specific creation logic
   - Add tests for new format

### Code Organization

The build system follows these principles:

- **Separation of concerns**: Each module has a specific responsibility
- **Platform abstraction**: Platform-specific code is isolated
- **Composition over inheritance**: Prefer composition for flexibility
- **Comprehensive logging**: All operations are logged for debugging
- **Error handling**: Graceful failure with informative messages

### Testing the Build System

The build system itself has tests:

```bash
# Run build system tests
python -m pytest build_system/tests/ -v

# Integration tests
python lc3_build.py test --categories integration
```

## Performance

### Build Performance

The build system is optimized for performance:

- **Incremental builds**: Only rebuild changed components
- **Parallel compilation**: Use all available CPU cores
- **Build caching**: Cache CMake configuration and dependencies
- **Dependency caching**: Avoid redundant package installations

### Benchmarks

Typical build times on modern hardware:

| Configuration | Clean Build | Incremental | Test Suite |
|---------------|-------------|-------------|------------|
| Debug         | 2-5 min     | 30-60 sec   | 1-3 min    |
| Release       | 3-7 min     | 45-90 sec   | 1-3 min    |
| Full CI       | 8-15 min    | N/A         | 5-10 min   |

## Roadmap

### Near-term Improvements
- **IDE integration**: VS Code tasks and settings
- **Docker support**: Containerized builds
- **Configuration files**: TOML/YAML configuration
- **Plugin system**: Extensible build steps

### Long-term Goals
- **Cross-compilation**: Build for different target platforms
- **Advanced packaging**: MSI/DEB/RPM installers
- **Documentation generation**: Automated API documentation
- **Performance tracking**: Historical build and test metrics
- **Quality gates**: Code quality and security scanning

## License

This build system is part of the LC-3 Simulator project and is licensed under the same terms as the main project.

---

For questions, issues, or contributions, please see the main project documentation or create an issue in the project repository.
