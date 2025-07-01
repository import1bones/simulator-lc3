# LC-3 Simulator Build System Migration Guide

## Overview

The LC-3 simulator build system has been refactored into a robust, modular, cross-platform architecture. This guide helps you migrate from the legacy shell scripts to the new Python-based build system.

## What's New

### 🏗️ Modular Architecture
- **`build_system/`** - Core build system modules
- **Platform abstraction** - Unified interface across Windows, Linux, and macOS
- **Dependency management** - Automatic detection and installation
- **Test framework** - Comprehensive testing with coverage and reporting
- **Package generation** - Multi-format distribution packages
- **CI/CD integration** - Automated workflow generation

### 🚀 New Features
- Cross-platform dependency resolution
- Parallel test execution with detailed reporting
- Coverage analysis with HTML reports
- Performance benchmarking
- Automated package creation (binary, source, wheel)
- GitHub Actions / GitLab CI configuration generation
- Build caching and optimization

### 🛠️ Unified CLI
```bash
# New unified command-line interface
python lc3_build.py build --clean --release
python lc3_build.py test --coverage --html-report
python lc3_build.py package --all
python lc3_build.py ci-setup github
```

## Migration Path

### Phase 1: Backward Compatibility ✅
The legacy scripts (`build_and_test.py`, `build_and_test.sh`, `build_and_test.bat`) continue to work and automatically use the new system when available.

### Phase 2: New CLI Usage (Recommended)
Start using the new unified CLI for better features and consistency:

```bash
# Replace old usage with new CLI
# Old: python build_and_test.py --clean --test-categories basic memory
# New: python lc3_build.py full-build --clean --test --test-categories basic memory
```

### Phase 3: Direct Module Usage (Advanced)
For advanced workflows, use the build system modules directly:

```python
from build_system import create_builder, TestRunner, PackageManager

# Create and configure builder
builder = create_builder()
builder.full_build()

# Run specific tests
test_runner = TestRunner(builder.logger, builder.config.platform)
results = test_runner.run_suite("performance")

# Create packages
package_manager = PackageManager(builder.config, builder.project, builder.logger)
package_manager.create_binary_package()
```

## Quick Start

### 1. Install Dependencies
```bash
# Ensure Python 3.8+ is installed
python --version

# Install required packages (automatic on first run)
python lc3_build.py deps --install
```

### 2. Build the Project
```bash
# Simple build
python lc3_build.py build

# Clean build with tests
python lc3_build.py full-build --clean --test

# Release build with packaging
python lc3_build.py build --build-type Release
python lc3_build.py package --all
```

### 3. Run Tests
```bash
# Basic tests
python lc3_build.py test

# Comprehensive testing
python lc3_build.py test --categories all --coverage --html-report

# Performance tests
python lc3_build.py test --categories performance
```

### 4. Set Up CI/CD
```bash
# GitHub Actions
python lc3_build.py ci-setup github

# GitLab CI
python lc3_build.py ci-setup gitlab
```

## Command Reference

### Build Commands
```bash
# Configure and build
python lc3_build.py build

# Clean build
python lc3_build.py build --clean

# Release build
python lc3_build.py build --build-type Release

# Configure only
python lc3_build.py build --configure-only

# Disable Python bindings
python lc3_build.py build --no-python
```

### Test Commands
```bash
# Run basic tests
python lc3_build.py test --categories basic

# Run with coverage
python lc3_build.py test --coverage --html-report

# Run in parallel
python lc3_build.py test --parallel

# Run specific suites
python lc3_build.py test --categories memory instructions pipeline
```

### Package Commands
```bash
# Create binary package
python lc3_build.py package --binary

# Create all packages
python lc3_build.py package --all

# Custom version
python lc3_build.py package --all --version 2.0.0
```

### Utility Commands
```bash
# Check dependencies
python lc3_build.py deps --check

# System information
python lc3_build.py info --all

# Clean artifacts
python lc3_build.py clean --all
```

## Configuration

### Build Configuration
The build system can be configured through:

1. **Command line arguments** (highest priority)
2. **Environment variables**
3. **Configuration files** (planned for future)
4. **Default settings** (lowest priority)

### Environment Variables
```bash
# Build configuration
export LC3_BUILD_TYPE=Release
export LC3_PLATFORM=linux
export LC3_ARCHITECTURE=x86_64

# Python configuration
export LC3_PYTHON_BINDINGS=ON
export LC3_PYTHON_EXE=python3.11

# Test configuration
export LC3_TEST_PARALLEL=ON
export LC3_TEST_COVERAGE=ON
```

## Platform-Specific Notes

### Windows
- Requires Visual Studio Build Tools or Visual Studio 2019+
- PowerShell 5.1+ recommended
- Windows 10+ supported

### Linux
- GCC 7+ or Clang 6+ required
- CMake 3.12+ required
- Ubuntu 18.04+, CentOS 7+, Fedora 30+ supported

### macOS
- Xcode Command Line Tools required
- CMake 3.12+ (install via Homebrew)
- macOS 10.15+ supported

## Troubleshooting

### Common Issues

1. **Python module import fails**
   ```bash
   # Rebuild Python bindings
   python lc3_build.py build --clean
   python lc3_build.py build
   ```

2. **CMake not found**
   ```bash
   # Check dependencies
   python lc3_build.py deps --check
   
   # Install missing dependencies
   python lc3_build.py deps --install
   ```

3. **Tests fail on specific platform**
   ```bash
   # Run with verbose output
   python lc3_build.py test --verbose
   
   # Check specific test category
   python lc3_build.py test --categories basic --verbose
   ```

4. **Build fails with generator errors**
   ```bash
   # Specify generator explicitly
   python lc3_build.py build --generator "Unix Makefiles"
   
   # On Windows with Visual Studio
   python lc3_build.py build --generator "Visual Studio 17 2022"
   ```

### Debug Mode
```bash
# Enable debug logging
python lc3_build.py build --verbose

# Show all system information
python lc3_build.py info --all

# Generate dependency report
python lc3_build.py deps --report
```

## Migration Checklist

- [ ] Verify new CLI works: `python lc3_build.py info --system`
- [ ] Test basic build: `python lc3_build.py build`
- [ ] Verify tests pass: `python lc3_build.py test`
- [ ] Check packaging: `python lc3_build.py package --binary`
- [ ] Set up CI/CD: `python lc3_build.py ci-setup github`
- [ ] Update documentation and scripts to use new CLI
- [ ] Train team members on new commands
- [ ] Remove dependency on legacy shell scripts (optional)

## Future Enhancements

The new build system provides a foundation for:

- **IDE integration** - VS Code tasks, CLion CMake presets
- **Docker support** - Containerized builds
- **Advanced packaging** - MSI installers, DEB/RPM packages
- **Documentation generation** - Automated API docs
- **Release automation** - Automated versioning and releases
- **Performance tracking** - Historical benchmark data
- **Quality gates** - Automated code quality checks

## Support

For questions or issues:

1. Check this migration guide
2. Run `python lc3_build.py info --all` for system diagnostics
3. Check the build system documentation in `build_system/`
4. Create an issue with the error output and system information

---

*This migration guide will be updated as the build system evolves. Last updated: $(date)*
