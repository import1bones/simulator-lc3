# Development Workflow Guide

## 🔄 Daily Development Workflow

This guide provides step-by-step workflows for common development tasks in the LC-3 simulator project.

## 🚀 Getting Started (New Developer)

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd simulator-lc3

# Check system requirements
python lc3_build.py info --system

# Install dependencies
pip install -r requirements.txt

# Initial build and test
python lc3_build.py full-build --test
```

### 2. Verify Everything Works
```bash
# Run a sample program to confirm setup
./build/simulator-lc3 test_programs/hello.asm

# Run the test suite
python lc3_build.py test
```

## 🛠️ Feature Development Workflows

### Adding a New LC-3 Instruction

**Scenario**: You want to add a new custom instruction to the LC-3 ISA.

```bash
# 1. Plan your changes
#    - Define the instruction format in type/opcode.h
#    - Implement the instruction logic in state_machine/states.cpp
#    - Add comprehensive tests

# 2. Make the changes
git checkout -b feature/new-instruction

# Edit opcode definitions
# Edit: type/opcode.h
# Add: New opcode constant and bit patterns

# Edit state machine implementation  
# Edit: state_machine/states.cpp
# Add: Instruction decode and execute logic

# 3. Add tests
# Edit: tests/test_instructions.py
# Add: Test cases for the new instruction

# 4. Build and test
python lc3_build.py build --clean
python lc3_build.py test --suite instructions

# 5. Test with a sample program
# Create: test_programs/test_new_instruction.asm
./build/simulator-lc3 test_programs/test_new_instruction.asm

# 6. Run full test suite
python lc3_build.py test --coverage

# 7. Commit and push
git add .
git commit -m "Add new instruction: [INSTRUCTION_NAME]"
git push origin feature/new-instruction
```

### Improving Memory Management

**Scenario**: You want to optimize memory access patterns or add new memory features.

```bash
# 1. Create feature branch
git checkout -b feature/memory-optimization

# 2. Make changes to memory subsystem
# Edit: mem/memory.h, mem/memory.cpp (if exists)
# Edit: Related files in mem/ directory

# 3. Update or add tests
# Edit: tests/test_memory.py
# Add: Tests for new memory features

# 4. Test memory-specific functionality
python lc3_build.py test --suite memory -v

# 5. Run integration tests
python lc3_build.py test --suite integration

# 6. Check for performance impact
python lc3_build.py test --suite performance
```

### Adding Pipeline Analysis Features

**Scenario**: You want to enhance the pipeline simulation and analysis capabilities.

```bash
# 1. Create feature branch
git checkout -b feature/pipeline-enhancement

# 2. Make changes
# Edit: state_machine/ files for pipeline logic
# Edit: analysis/ files for analysis tools

# 3. Add comprehensive tests
# Edit: tests/test_pipeline.py (if exists)
# Edit: tests/test_isa_performance.py

# 4. Test pipeline functionality
python lc3_build.py test --suite performance

# 5. Run analysis tools
python analysis/enhanced_isa_analysis.py
python analysis/enhanced_mips_benchmark.py

# 6. Generate performance reports
python scripts/benchmark_programs.py
```

## 🧪 Testing Workflows

### Running Targeted Tests

```bash
# Test specific functionality
python lc3_build.py test --suite basic       # Core functionality
python lc3_build.py test --suite memory      # Memory management
python lc3_build.py test --suite instructions # Instruction execution
python lc3_build.py test --suite integration # End-to-end tests
python lc3_build.py test --suite performance # Performance analysis

# Test specific file
pytest tests/test_basic.py -v

# Test specific test case
pytest tests/test_instructions.py::test_add_instruction -v -s
```

### Debugging Failed Tests

```bash
# 1. Run the failing test with detailed output
pytest tests/test_name.py::failing_test -v -s

# 2. Use the debug script
python scripts/debug_test.py tests/test_name.py::failing_test

# 3. Check if it's a build issue
python lc3_build.py build --clean
python lc3_build.py test --suite basic

# 4. Check dependencies
python lc3_build.py info --deps
```

### Performance Testing

```bash
# Run performance benchmarks
python lc3_build.py test --suite performance

# Generate detailed performance report
python analysis/enhanced_mips_benchmark.py

# Create performance comparison
python scripts/benchmark_programs.py
```

## 📊 Code Quality Workflows

### Code Formatting and Linting

```bash
# Format C++ code (if clang-format is available)
find . -name "*.cpp" -o -name "*.h" | xargs clang-format -i

# Format Python code
black .
isort .

# Run linting
flake8 .
pylint build_system/ scripts/ tests/
```

### Coverage Analysis

```bash
# Generate coverage report
python lc3_build.py test --coverage

# View HTML coverage report
# Open htmlcov/index.html in browser

# Generate detailed coverage analysis
python scripts/analyze_coverage.py
```

## 🚢 Release Workflows

### Creating a Release Package

```bash
# 1. Ensure everything is working
python lc3_build.py full-build --test

# 2. Generate documentation
python scripts/auto_documentation.py

# 3. Create package
python lc3_build.py package

# 4. Test the package
# Test installation and basic functionality
```

### Continuous Integration Setup

```bash
# Generate CI configuration files
python lc3_build.py ci github    # GitHub Actions
python lc3_build.py ci gitlab    # GitLab CI

# Commit CI files
git add .github/ .gitlab-ci.yml
git commit -m "Add CI/CD configuration"
```

## 🔧 Maintenance Workflows

### Project Cleanup

```bash
# Clean build artifacts
python scripts/clean_project.py

# Or use the build system
python lc3_build.py clean
```

### Dependency Updates

```bash
# Check for outdated dependencies
pip list --outdated

# Update requirements.txt
pip-review --auto

# Test after updates
python lc3_build.py full-build --test
```

### Project Validation

```bash
# Validate entire project
python scripts/validate_project.py

# Check project structure
python lc3_build.py info
```

## 🚨 Emergency Workflows

### Build System Not Working

```bash
# 1. Try the legacy build system
python build_and_test.py

# 2. Or use direct CMake
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build .

# 3. Check system dependencies
python lc3_build.py info --system --deps
```

### Tests All Failing

```bash
# 1. Clean rebuild
python lc3_build.py build --clean

# 2. Check Python environment
python lc3_build.py info --deps

# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 4. Try minimal test
pytest tests/test_basic.py::test_simple_case -v
```

## 📋 Checklists

### Before Committing
- [ ] Code builds successfully: `python lc3_build.py build`
- [ ] All tests pass: `python lc3_build.py test`
- [ ] Code is formatted: `black .` and `isort .`
- [ ] No new linting errors: `flake8 .`
- [ ] Changes are documented

### Before Pull Request
- [ ] Full test suite passes: `python lc3_build.py full-build --test`
- [ ] Coverage hasn't decreased significantly
- [ ] Documentation is updated
- [ ] Performance impact is acceptable
- [ ] Changes are backward compatible

### Before Release
- [ ] All CI tests pass
- [ ] Documentation is complete and up-to-date
- [ ] Performance benchmarks are run
- [ ] Package builds successfully: `python lc3_build.py package`
- [ ] Manual testing on target platforms

---

**Pro Tips:**
- Use `python lc3_build.py info` to check project status anytime
- The `--help` flag works with all commands: `python lc3_build.py build --help`
- Check `PROJECT_OVERVIEW.md` for quick reference
- Read `BUILD_ARCHITECTURE_SUMMARY.md` for detailed build system information
