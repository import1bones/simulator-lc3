# Scripts Directory

This directory contains Python utility scripts for the LC-3 simulator project.

## Files

### Test and Validation Scripts
- **`run_tests.py`** - Main test execution script with coverage reporting and build capabilities
- **`validate_project.py`** - Comprehensive project validation to ensure all components work properly
- **`debug_test.py`** - Debug utilities and test diagnostics
- **`analyze_coverage.py`** - Coverage analysis and reporting utilities

### Project Management Scripts
- **`clean_project.py`** - Clean up auto-generated files (reports, data files, auto-docs)
- **`auto_documentation.py`** - Generate automatic project documentation
- **`github_summary.py`** - Generate GitHub release summaries

### Benchmark and Analysis Scripts
- **`benchmark_programs.py`** - Benchmark program utilities and test data

## Usage

### Running Tests
```bash
# Check environment and build simulator
python3 scripts/run_tests.py --check-env
python3 scripts/run_tests.py --build

# Run all tests with coverage
python3 scripts/run_tests.py --coverage

# Run specific test categories
python3 scripts/run_tests.py --basic
python3 scripts/run_tests.py --instructions
python3 scripts/run_tests.py --integration

# Install dependencies
python3 scripts/run_tests.py --install-deps
```

### Project Validation and Cleanup
```bash
# Validate entire project structure
python3 scripts/validate_project.py

# Clean auto-generated files
python3 scripts/clean_project.py

# Dry run (see what would be removed)
python3 scripts/clean_project.py --dry-run

# Also remove build directory
python3 scripts/clean_project.py --include-build
```

### Coverage Analysis
```bash
# Generate coverage reports
python3 scripts/analyze_coverage.py

# Analyze specific modules
python3 scripts/analyze_coverage.py --module state_machine
```

### Debug Utilities
```bash
# Debug test failures
python3 scripts/debug_test.py --test test_memory.py

# Interactive debugging
python3 scripts/debug_test.py --interactive
```

## Dependencies

- Python 3.8+
- pytest and testing dependencies
- Coverage analysis tools
- CMake and C++ compiler (for building simulator)
- LC-3 simulator Python bindings

Install with: `python3 scripts/run_tests.py --install-deps`

## Notes

- All scripts should be run from the project root directory
- Scripts automatically detect and use the appropriate Python environment
- Coverage data is stored in the project root `.coverage` file
- HTML reports are generated in the `reports/` directory
