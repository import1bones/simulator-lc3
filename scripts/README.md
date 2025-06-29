# Scripts Directory

This directory contains Python utility scripts for the LC-3 simulator project.

## Files

### Test and Validation Scripts
- **`run_tests.py`** - Main test execution script with coverage reporting
- **`debug_test.py`** - Debug utilities and test diagnostics
- **`analyze_coverage.py`** - Coverage analysis and reporting utilities

### Benchmark and Analysis Scripts
- **`benchmark_programs.py`** - Benchmark program utilities and test data

## Usage

### Running Tests
```bash
# Run all tests with coverage
python3 scripts/run_tests.py

# Run with specific options
python3 scripts/run_tests.py --coverage --html-report
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
- LC-3 simulator Python bindings

## Notes

- All scripts should be run from the project root directory
- Scripts automatically detect and use the appropriate Python environment
- Coverage data is stored in the project root `.coverage` file
- HTML reports are generated in the `reports/` directory
