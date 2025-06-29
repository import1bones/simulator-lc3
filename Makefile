# Makefile for LC-3 Simulator Test Suite
# Provides convenient targets for building, testing, and maintaining the simulator

.PHONY: help build test test-fast test-all test-unit test-integration test-basic test-instructions test-memory test-io
.PHONY: coverage benchmark clean install-deps check-env lint format setup ci

# Default target
help:
	@echo "LC-3 Simulator Test Suite"
	@echo "========================="
	@echo ""
	@echo "Build targets:"
	@echo "  build         - Build the LC-3 simulator with Python bindings"
	@echo "  clean         - Clean build artifacts"
	@echo ""
	@echo "Setup targets:"
	@echo "  setup         - Complete setup (install deps + build)"
	@echo "  install-deps  - Install Python dependencies"
	@echo "  check-env     - Check environment setup"
	@echo ""
	@echo "Test targets:"
	@echo "  test          - Run basic test suite (excludes slow tests)"
	@echo "  test-fast     - Run tests in parallel mode"
	@echo "  test-all      - Run all tests including slow ones"
	@echo "  test-unit     - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo ""
	@echo "Specific test categories:"
	@echo "  test-basic    - Run basic functionality tests"
	@echo "  test-instructions - Run instruction implementation tests"
	@echo "  test-memory   - Run memory-related tests"
	@echo "  test-io       - Run I/O and TRAP tests"
	@echo ""
	@echo "Analysis targets:"
	@echo "  coverage      - Run tests with coverage analysis"
	@echo "  benchmark     - Run performance benchmarks"
	@echo "  lint          - Run code linting"
	@echo "  format        - Format code"
	@echo ""
	@echo "CI targets:"
	@echo "  ci            - Run full CI pipeline"

# Build targets
build:
	@echo "Building LC-3 Simulator..."
	@mkdir -p build
	@cd build && cmake .. && cmake --build . --config Release

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf reports/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete

# Setup targets
setup: install-deps build
	@echo "Setup completed successfully!"

install-deps:
	@echo "Installing Python dependencies..."
	@python3 -m pip install pytest pytest-cov pytest-html pytest-xdist pytest-benchmark numpy
	@python3 -m pip install pybind11[global] || echo "Warning: pybind11 installation failed"

check-env:
	@python3 run_tests.py --check-env

# Test targets
test:
	@echo "Running basic test suite..."
	@python3 run_tests.py --verbose

test-fast:
	@echo "Running tests in parallel..."
	@python3 run_tests.py --parallel --verbose

test-all:
	@echo "Running all tests including slow ones..."
	@python3 run_tests.py --slow --verbose

test-unit:
	@echo "Running unit tests..."
	@python3 run_tests.py --unit-only --verbose

test-integration:
	@echo "Running integration tests..."
	@python3 run_tests.py --integration-only --verbose

# Specific test categories
test-basic:
	@echo "Running basic functionality tests..."
	@python3 run_tests.py --basic --verbose

test-instructions:
	@echo "Running instruction implementation tests..."
	@python3 run_tests.py --instructions --verbose

test-memory:
	@echo "Running memory-related tests..."
	@python3 run_tests.py --memory --verbose

test-io:
	@echo "Running I/O and TRAP tests..."
	@python3 run_tests.py --io --verbose

# Analysis targets
coverage:
	@echo "Running tests with coverage analysis..."
	@python3 run_tests.py --coverage --html-report --verbose
	@echo "Coverage report available at: reports/coverage/index.html"

benchmark:
	@echo "Running performance benchmarks..."
	@python3 run_tests.py --benchmark
	@echo "Benchmark report available at: reports/benchmark_report.html"

lint:
	@echo "Running code linting..."
	@python3 -m flake8 tests/ --max-line-length=100 --ignore=E501,W503 || echo "Install flake8 for linting"

format:
	@echo "Formatting code..."
	@python3 -m black tests/ || echo "Install black for formatting"
	@python3 -m isort tests/ || echo "Install isort for import sorting"

# CI target
ci: check-env build test coverage
	@echo "CI pipeline completed successfully!"

# Development helpers
dev-install:
	@echo "Installing development dependencies..."
	@python3 -m pip install black isort flake8 mypy pytest-xdist pytest-benchmark

watch:
	@echo "Watching for changes and running tests..."
	@python3 -m pytest-watch tests/ -- --verbose

debug:
	@echo "Running tests in debug mode..."
	@python3 run_tests.py --verbose --fail-fast --test-file tests/test_basic.py

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "See tests/README.md for detailed documentation"

# Quick verification
verify: build test-basic
	@echo "Quick verification completed!"

# Full test cycle
full-test: clean setup test-all coverage benchmark
	@echo "Full test cycle completed!"
