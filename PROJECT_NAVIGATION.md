# 🧭 PROJECT NAVIGATION GUIDE

## 📍 You Are Here: LC-3 Simulator Project

Welcome! This is your complete guide to understanding and navigating the LC-3 Simulator project structure. This project is **well-organized and production-ready** with a modern, modular build system.

## 🚀 Quick Start (30 seconds)

```bash
# 1. Get oriented
python lc3_build.py info --system

# 2. Build the project  
python lc3_build.py build

# 3. Run a sample program
./build/simulator-lc3 test_programs/hello.asm

# 4. Run tests to verify everything works
python lc3_build.py test --suite basic
```

**That's it!** You now have a working LC-3 simulator.

## 📚 Documentation Hierarchy (Read in Order)

### 🎯 Level 1: Getting Started
1. **`PROJECT_OVERVIEW.md`** ← **YOU ARE HERE** - Start here for newcomers
2. **`README.md`** ← Detailed project features and capabilities
3. **`VISUAL_PROJECT_MAP.md`** ← Visual directory structure with icons

### 🔧 Level 2: Development
4. **`DEVELOPMENT_WORKFLOW.md`** ← Daily development workflows and common tasks
5. **`PROJECT_STRUCTURE.md`** ← Complete technical structure breakdown
6. **`CODE_STYLE`** ← Code formatting and style guidelines

### 🏗️ Level 3: Build System
7. **`BUILD_ARCHITECTURE_SUMMARY.md`** ← Build system architecture details
8. **`BUILD_SYSTEM_MIGRATION.md`** ← Migration guide from legacy build system
9. **`build_system/README.md`** ← Modular build system documentation

### 📊 Level 4: Advanced
10. **`docs/`** ← Technical documentation and guides
11. **`reports/`** ← Generated test and coverage reports
12. **`analysis/`** ← Performance analysis tools and results

## 🎯 What Do You Want to Do?

### 👨‍💻 I want to understand the project
- **Start**: `PROJECT_OVERVIEW.md` (this file)
- **Deep dive**: `README.md` → `PROJECT_STRUCTURE.md`
- **Visual learner**: `VISUAL_PROJECT_MAP.md`

### 🏗️ I want to build and run
```bash
# Quick build
python lc3_build.py build

# Full build with tests
python lc3_build.py full-build --test

# Traditional CMake (alternative)
mkdir build && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=ON
cmake --build .
```

### 🧪 I want to run tests
```bash
# All tests
python lc3_build.py test

# Specific test suites
python lc3_build.py test --suite basic
python lc3_build.py test --suite memory  
python lc3_build.py test --suite instructions

# With coverage
python lc3_build.py test --coverage
```

### 💻 I want to develop/contribute
- **Read**: `DEVELOPMENT_WORKFLOW.md` ← Essential development guide
- **Understand structure**: `PROJECT_STRUCTURE.md`
- **Follow style**: `CODE_STYLE`
- **Add tests**: `tests/README.md`

### 🚀 I want to add features
- **Add instruction**: Edit `type/opcode.h` + `state_machine/states.cpp` + `tests/test_instructions.py`
- **Memory features**: Edit `mem/` directory + `tests/test_memory.py`
- **Performance analysis**: Edit `analysis/` directory + `tests/test_isa_performance.py`

### 🔧 I want to understand the build system
- **Modern system**: `build_system/README.md`
- **Architecture**: `BUILD_ARCHITECTURE_SUMMARY.md`
- **Migration info**: `BUILD_SYSTEM_MIGRATION.md`

### 📊 I want to analyze performance
```bash
# Run performance analysis
python analysis/enhanced_isa_analysis.py
python analysis/enhanced_mips_benchmark.py

# Performance tests
python lc3_build.py test --suite performance
```

### 📦 I want to package/deploy
```bash
# Create packages
python lc3_build.py package

# Set up CI/CD
python lc3_build.py ci-setup github
python lc3_build.py ci-setup gitlab
```

## 🗺️ Project Structure Summary

```
📦 simulator-lc3/
├── 🚀 lc3_build.py              # Modern unified CLI (use this!)
├── 🏗️ build_system/             # Modular build framework
├── 💻 Core Simulator/           # mem/, state_machine/, type/, main.cpp
├── 🧪 Testing/                  # tests/, test_programs/
├── 📊 Analysis/                 # analysis/, reports/
├── 🛠️ Scripts/                  # scripts/ (development tools)
├── 📚 Documentation/            # docs/, *.md files
└── ⚙️ Configuration/            # CMakeLists.txt, requirements.txt, etc.
```

## 🚦 Traffic Light System for Editing

### 🟢 GREEN - Safe to Modify
- **Tests**: `tests/` - Add tests freely
- **Programs**: `test_programs/` - Add sample LC-3 programs  
- **Analysis**: `analysis/` - Add performance analysis
- **Scripts**: `scripts/` - Add development utilities
- **Docs**: Documentation files

### 🟡 YELLOW - Modify with Understanding
- **Core**: `mem/`, `state_machine/`, `type/` - Core simulator logic
- **Main**: `main.cpp` - Main executable
- **Bindings**: `python_bindings/` - Python interface
- **Config**: `requirements.txt`, `pyproject.toml`

### 🔴 RED - Expert Level
- **Build System**: `build_system/` - Modular build framework
- **CLI**: `lc3_build.py` - Unified command interface
- **CMake**: `CMakeLists.txt` - Build configuration

## 🆘 Troubleshooting Quick Reference

### Build Issues
```bash
# Clean rebuild
python lc3_build.py build --clean

# Check dependencies
python lc3_build.py info --system
python lc3_build.py deps --check

# Use legacy build (backup)
python build_and_test.py
```

### Test Issues
```bash
# Run specific failing test
pytest tests/test_name.py::test_function -v -s

# Debug mode
python scripts/debug_test.py tests/test_name.py

# Check Python bindings
python lc3_build.py build --clean --build-type Debug
```

### "I'm Lost" Recovery
1. **Return to base**: `PROJECT_OVERVIEW.md` (this file)
2. **Get system info**: `python lc3_build.py info --system`
3. **Quick test**: `python lc3_build.py test --suite basic`
4. **Ask for help**: Check existing GitHub issues

## 🎯 Success Indicators

You'll know the project structure is clear when:
- ✅ Build succeeds: `python lc3_build.py build`
- ✅ Tests pass: `python lc3_build.py test`
- ✅ Sample runs: `./build/simulator-lc3 test_programs/hello.asm`
- ✅ You can navigate to any component easily
- ✅ Documentation answers your questions

## 🤝 Contributing Workflow

1. **Understand**: Read this guide + `DEVELOPMENT_WORKFLOW.md`
2. **Setup**: `python lc3_build.py full-build --test`
3. **Develop**: Make changes following `CODE_STYLE`
4. **Test**: `python lc3_build.py test`
5. **Validate**: `python scripts/validate_project.py`
6. **Submit**: Create pull request

## 📞 Getting Help

1. **Documentation**: Start with relevant `.md` files
2. **CLI Help**: `python lc3_build.py --help`
3. **Command Help**: `python lc3_build.py build --help`
4. **Project Status**: `python lc3_build.py info`
5. **Issues**: GitHub repository issues

## 🎉 Project Strengths

This project excels at:
- ✅ **Clear Structure**: Well-organized modular design
- ✅ **Modern Build System**: Cross-platform, dependency-aware
- ✅ **Comprehensive Testing**: Full test coverage with multiple suites
- ✅ **Great Documentation**: Multiple levels of documentation
- ✅ **Developer-Friendly**: Easy workflows and helpful tools
- ✅ **Performance Analysis**: Built-in benchmarking and analysis
- ✅ **CI/CD Ready**: Automated build and test infrastructure

---

## 🧭 Next Steps

**Choose your adventure:**

**👨‍💻 New Developer**: Read `DEVELOPMENT_WORKFLOW.md`
**🏗️ Build Expert**: Read `BUILD_ARCHITECTURE_SUMMARY.md`  
**🧪 Tester**: Read `tests/README.md`
**📊 Analyst**: Check `analysis/README.md`
**📚 Documenter**: Check `docs/README.md`

**🚀 Ready to Code**: `python lc3_build.py build && ./build/simulator-lc3 test_programs/hello.asm`

---

**Remember**: This project structure is already excellent! These guides just make it easier to navigate and understand. The modular build system, comprehensive testing, and clear documentation make this a professional-grade project.
