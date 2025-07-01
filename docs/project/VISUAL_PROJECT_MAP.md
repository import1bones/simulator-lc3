# Visual Project Structure Map

## 🗺️ LC-3 Simulator Project Directory Map

```
simulator-lc3/                                 📦 ROOT PROJECT DIRECTORY
│
├── 🏗️ BUILD SYSTEM & CONFIGURATION           📁 Build and project configuration
│   ├── lc3_build.py                          🚀 UNIFIED CLI INTERFACE (START HERE!)
│   ├── build_and_test.py                     🔄 Cross-platform Python build script  
│   ├── build_and_test.sh                     🐧 Unix/Linux shell script
│   ├── build_and_test.bat                    🪟 Windows batch script
│   ├── CMakeLists.txt                        ⚙️ Main CMake configuration
│   ├── Makefile                              🔨 Legacy Makefile support
│   ├── requirements.txt                      📋 Python dependencies (organized)
│   ├── pyproject.toml                        🐍 Python project metadata
│   ├── pytest.ini                            🧪 Pytest configuration
│   └── build_system/                         📦 MODULAR BUILD FRAMEWORK
│       ├── __init__.py                       📍 Package initialization
│       ├── core.py                           🎯 Core build classes & platform detection
│       ├── dependencies.py                   📦 Dependency management (apt, yum, brew, etc.)
│       ├── builders.py                       🏗️ Build orchestration (CMake, Python, LC3)
│       ├── testing.py                        🧪 Test execution & coverage reporting
│       ├── packaging.py                      📦 Package creation & distribution
│       ├── ci.py                             🔄 CI/CD configuration generation
│       └── README.md                         📖 Build system documentation
│
├── 💻 CORE SIMULATOR MODULES                 📁 Heart of the LC-3 simulator
│   ├── main.cpp                              🚀 Main simulator executable entry point
│   ├── mem/                                  🧠 MEMORY MANAGEMENT MODULE
│   │   ├── CMakeLists.txt                    ⚙️ Memory module build configuration
│   │   ├── memory.h                          💾 Core memory interface & operations
│   │   ├── control_store.h                   🎛️ Control store for microcode
│   │   ├── device_register.h                 📱 Device register interfaces
│   │   ├── microsequence.h                   🔄 Microsequence definitions
│   │   └── register.h                        📊 Register implementations
│   ├── state_machine/                        🔄 PROCESSOR STATE & CONTROL
│   │   ├── CMakeLists.txt                    ⚙️ State machine build configuration
│   │   ├── state_machine.h/.cpp              🎯 Main state machine interface
│   │   ├── state_machine_utils.cpp           🛠️ State machine utility functions
│   │   ├── states.h/.cpp                     📊 State definitions & implementations
│   │   ├── signals.h/.cpp                    📡 Signal definitions & handling
│   │   ├── state_definitions.h               📋 State constants & enumerations
│   │   ├── ext.h                             🔌 External interfaces
│   │   └── README.md                         📖 State machine documentation
│   ├── type/                                 🏷️ TYPE DEFINITIONS & OPCODES
│   │   ├── CMakeLists.txt                    ⚙️ Type module build configuration
│   │   ├── type.h                            🏷️ Core type definitions
│   │   ├── opcode.h                          📝 LC-3 instruction opcodes
│   │   └── trap_vector.h                     🚨 TRAP vector definitions
│   └── python_bindings/                      🐍 PYTHON-C++ INTERFACE
│       ├── CMakeLists.txt                    ⚙️ Python bindings build config
│       └── lc3_simulator.cpp                 🔗 pybind11 interface implementation
│
├── 🧪 TESTING & VALIDATION FRAMEWORK         📁 Comprehensive testing infrastructure
│   ├── tests/                                🧪 TEST SUITE
│   │   ├── conftest.py                       ⚙️ Pytest configuration & fixtures
│   │   ├── test_basic.py                     ✅ Basic functionality tests
│   │   ├── test_memory.py                    🧠 Memory management tests
│   │   ├── test_instructions.py              📝 Instruction execution tests
│   │   ├── test_integration.py               🔗 End-to-end integration tests
│   │   ├── test_io.py                        📱 Input/output operation tests
│   │   ├── test_isa_performance.py           📊 ISA performance analysis
│   │   ├── test_utils.py                     🛠️ Test utility functions
│   │   └── README.md                         📖 Testing framework documentation
│   ├── test_programs/                        📝 LC-3 ASSEMBLY PROGRAMS
│   │   ├── hello.asm                         👋 Hello world example program
│   │   ├── instructions.txt                  📋 Instruction reference
│   │   └── [various .asm files]              📝 Sample LC-3 programs for testing
│   └── scripts/                              🛠️ DEVELOPMENT & AUTOMATION TOOLS
│       ├── run_tests.py                      🧪 Test execution orchestrator
│       ├── analyze_coverage.py               📊 Coverage analysis & reporting
│       ├── auto_documentation.py             📖 Automatic documentation generator
│       ├── benchmark_programs.py             ⚡ Performance benchmarking suite
│       ├── clean_project.py                  🧹 Project cleanup utilities
│       ├── debug_test.py                     🐛 Test debugging tools
│       ├── github_summary.py                🐙 GitHub integration utilities
│       ├── validate_project.py               ✅ Project structure validation
│       ├── README.md                         📖 Scripts documentation
│       └── reports/                          📊 Generated analysis reports
│
├── 📊 ANALYSIS & PERFORMANCE TOOLS           📁 Performance analysis & benchmarking
│   ├── analysis/                             📊 PERFORMANCE ANALYSIS SUITE
│   │   ├── enhanced_isa_analysis.py          🚀 Advanced ISA performance analysis
│   │   ├── enhanced_mips_benchmark.py        ⚡ MIPS comparison benchmarks
│   │   ├── isa_design_analysis.py            🎯 ISA design pattern analysis
│   │   ├── mips_benchmark.py                 📊 Basic MIPS benchmarking
│   │   └── README.md                         📖 Analysis tools documentation
│   └── reports/                              📋 GENERATED REPORTS & ANALYSIS
│       ├── comprehensive_test_coverage_report.html    📊 HTML coverage report
│       ├── COMPREHENSIVE_TEST_COVERAGE_REPORT.md      📋 Markdown coverage report
│       ├── CONDITION_COVERAGE_ANALYSIS.md             🎯 Condition coverage analysis
│       ├── COVERAGE_REPORT.md                         📊 General coverage report
│       ├── detailed_test_report.html                  📋 Detailed HTML test report
│       ├── ISA_COMPREHENSIVE_PERFORMANCE_REPORT.md    ⚡ ISA performance report
│       ├── test_analysis_summary.json                 📊 JSON analysis summary
│       ├── test_report.html                           📋 Basic HTML test report
│       └── README.md                                  📖 Reports documentation
│
├── 📚 DOCUMENTATION & PROJECT INFO           📁 Project documentation & guides
│   ├── docs/                                 📖 TECHNICAL DOCUMENTATION
│   │   ├── GITHUB_ACTIONS_GUIDE.md           🔄 CI/CD setup guide
│   │   ├── PROJECT_STRUCTURE.md              🗺️ Detailed structure breakdown
│   │   └── README.md                         📖 Documentation index
│   ├── data/                                 💾 PROJECT DATA FILES
│   │   └── README.md                         📖 Data directory documentation
│   ├── README.md                             📖 MAIN PROJECT README (features & overview)
│   ├── PROJECT_OVERVIEW.md                   🎯 Quick start & overview guide
│   ├── DEVELOPMENT_WORKFLOW.md               🔄 Developer workflow guide  
│   ├── BUILD_ARCHITECTURE_SUMMARY.md         🏗️ Build system architecture details
│   ├── BUILD_SYSTEM_MIGRATION.md             🔄 Build system migration guide
│   ├── PROJECT_COMPLETE_SUMMARY.md           📋 Complete project summary
│   ├── CODE_STYLE                            🎨 Code style guidelines
│   ├── lc3-simulator.code-workspace          📝 VS Code workspace configuration
│   └── enhanced_isa_analysis_20250630_005323.json  📊 Generated analysis data
│
└── 🔧 PROJECT CONFIGURATION FILES            📁 Git, IDE, and project configuration
    ├── .gitignore                            🚫 Git ignore patterns
    ├── .vscode/                              💻 VS Code configuration
    └── build/                                🏗️ Generated build directory (gitignored)
```

## 🎯 Key Entry Points

### For New Users:
1. **`PROJECT_OVERVIEW.md`** ← 🚀 **START HERE!**
2. **`README.md`** ← Detailed features and capabilities
3. **`lc3_build.py`** ← Build system CLI interface

### For Developers:
1. **`DEVELOPMENT_WORKFLOW.md`** ← Daily development guide
2. **`PROJECT_STRUCTURE.md`** ← Complete structure breakdown
3. **`BUILD_ARCHITECTURE_SUMMARY.md`** ← Build system details

### For Contributors:
1. **`CODE_STYLE`** ← Code formatting guidelines
2. **`tests/README.md`** ← Testing framework guide
3. **`build_system/README.md`** ← Build system documentation

## 🔍 Quick Navigation

| Need to... | Go to... |
|------------|----------|
| **Build the project** | `python lc3_build.py build` |
| **Run tests** | `python lc3_build.py test` |
| **Add new instruction** | Edit `type/opcode.h` + `state_machine/states.cpp` |
| **Debug memory issues** | Check `mem/` module + `tests/test_memory.py` |
| **Analyze performance** | Run `analysis/enhanced_isa_analysis.py` |
| **View test results** | Open `reports/test_report.html` |
| **Understand build system** | Read `build_system/README.md` |
| **Create sample program** | Add to `test_programs/` |

## 📋 File Type Legend

| Icon | Type | Description |
|------|------|-------------|
| 📦 | Package/Module | Python package or major module |
| 🚀 | Executable/CLI | Main executables or CLI interfaces |
| ⚙️ | Configuration | Build configuration files |
| 📝 | Source Code | C++ source files (.cpp, .h) |
| 🧪 | Testing | Test files and testing infrastructure |
| 📖 | Documentation | README files and documentation |
| 📊 | Analysis/Reports | Generated reports and analysis tools |
| 🛠️ | Utilities | Helper scripts and utilities |
| 🎯 | Entry Point | Main starting points for different tasks |

## 🚦 Traffic Light System

### 🟢 GREEN - Safe to Edit
- `tests/` - Add new tests freely
- `test_programs/` - Add sample programs
- `analysis/` - Add analysis tools
- `scripts/` - Add utility scripts

### 🟡 YELLOW - Edit with Care  
- `mem/`, `state_machine/`, `type/` - Core simulator logic
- `main.cpp` - Main executable
- `python_bindings/` - Python interface
- `requirements.txt` - Dependencies

### 🔴 RED - Expert Zone
- `build_system/` - Modular build framework
- `CMakeLists.txt` - Build configuration
- `lc3_build.py` - Unified CLI
- CI/CD configurations

---

**💡 Pro Tip**: Use `python lc3_build.py info` to get a quick overview of the project status and `tree` command (if available) to explore the actual directory structure.
