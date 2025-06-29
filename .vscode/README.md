# VS Code Configuration for LC-3 Simulator

This directory contains VS Code configuration files to provide an optimal development experience for the LC-3 simulator project.

## Files Overview

### `tasks.json`
Defines build and test tasks:
- **Build Tasks**: CMake configuration, building, and cleaning
- **Test Tasks**: Running pytest suites (all tests, specific test files, coverage)
- **Development Tasks**: Code formatting, Python bindings compilation

### `launch.json`
Provides debugging configurations:
- **C++ Debugging**: Debug the main simulator and state machine
- **Python Debugging**: Debug test scripts and pytest runs
- **Process Attachment**: Attach debugger to running processes

### `settings.json`
Workspace-specific settings:
- **C++ Configuration**: Compiler settings, IntelliSense, formatting
- **Python Configuration**: Testing, linting, and formatting
- **CMake Integration**: Automatic configuration and build settings
- **File Associations**: Proper syntax highlighting for project files

### `c_cpp_properties.json`
C++ IntelliSense configuration:
- Include paths for all project modules
- Compiler configuration for macOS with Clang
- Integration with CMake compile commands

### `extensions.json`
Recommended VS Code extensions:
- C++ development tools (IntelliSense, CMake, formatting)
- Python development and testing tools
- Git integration and code quality extensions

## Quick Start

1. **Open the workspace**:
   ```bash
   code lc3-simulator.code-workspace
   ```

2. **Install recommended extensions** when prompted by VS Code

3. **Build the project**:
   - Press `Cmd+Shift+P` and run "Tasks: Run Task"
   - Select "CMake Build" or use `Cmd+Shift+B`

4. **Run tests**:
   - Press `Cmd+Shift+P` and run "Tasks: Run Task"
   - Select "Run All Tests" or use `Cmd+Shift+T`

## Available Tasks

### Build Tasks
- **CMake Configure**: Configure the build system
- **CMake Build** (Default): Build the simulator with debug info
- **CMake Clean**: Clean build artifacts
- **Build Python Bindings**: Compile Python bindings for testing

### Test Tasks
- **Run All Tests** (Default): Execute the complete pytest suite
- **Run Basic Tests**: Test basic functionality
- **Run Memory Tests**: Test memory management
- **Run Instruction Tests**: Test instruction execution
- **Generate Test Coverage**: Create HTML coverage report

### Development Tasks
- **Run LC-3 Simulator**: Execute the compiled simulator
- **Format C++ Code**: Format all source files with clang-format

## Debugging

### C++ Debugging
- **Debug LC-3 Simulator**: Debug the main application
- **Debug State Machine**: Debug with breakpoint in state machine
- **Debug Current C++ File**: Debug the currently open C++ file

### Python Debugging
- **Debug Python Tests**: Debug the test runner
- **Debug Specific Test File**: Debug the currently open test file

## Keyboard Shortcuts

- `Cmd+Shift+B`: Build (CMake Build)
- `Cmd+Shift+T`: Test (Run All Tests)
- `F5`: Start debugging (based on current file type)
- `Cmd+Shift+P`: Command palette

## Features

### Code Intelligence
- **IntelliSense**: Auto-completion for C++ and Python
- **Go to Definition**: Navigate to function/class definitions
- **Find References**: Find all usages of symbols
- **Error Squiggles**: Real-time syntax and semantic error detection

### Integrated Testing
- **Test Discovery**: Automatic discovery of pytest tests
- **Test Execution**: Run tests from the Test Explorer panel
- **Coverage Reports**: Generate and view test coverage

### Git Integration
- **GitLens**: Enhanced git blame and history
- **Git Graph**: Visual representation of git history
- **Source Control**: Built-in git operations

### Code Quality
- **Automatic Formatting**: Format on save for C++ and Python
- **Linting**: Real-time code quality checks
- **Spell Checking**: Catch typos in comments and strings

## Configuration Details

### C++ Settings
- **Standard**: C++17
- **Compiler**: Clang++ (macOS default)
- **Formatter**: ClangFormat with LLVM style
- **IntelliSense**: Enhanced with compile commands from CMake

### Python Settings
- **Interpreter**: System Python 3
- **Testing Framework**: pytest
- **Formatter**: Black
- **Linter**: Pylint and Flake8

### CMake Integration
- **Auto-configure**: Automatically configure on workspace open
- **Build Type**: Debug (for development)
- **Python Bindings**: Enabled by default
- **Compile Commands**: Generated for IntelliSense

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Ensure CMake is installed: `brew install cmake`
   - Check that all dependencies are available
   - Try "CMake Clean" followed by "CMake Build"

2. **Python Tests Don't Run**:
   - Verify Python 3 is installed: `python3 --version`
   - Install test dependencies: `pip3 install pytest pybind11`
   - Build Python bindings first: "Build Python Bindings" task

3. **IntelliSense Not Working**:
   - Run "CMake Configure" to generate compile commands
   - Restart the C++ extension: `Cmd+Shift+P` → "C++: Restart IntelliSense"
   - Check that `build/compile_commands.json` exists

4. **Debugger Not Attaching**:
   - Ensure the project is built with debug symbols
   - Check that the executable path matches in `launch.json`
   - Try building with "CMake Build" (Debug configuration)

### Performance Tips

- **Large Projects**: Use "Search Exclude" settings to avoid indexing build artifacts
- **IntelliSense**: Let the initial indexing complete before heavy development
- **Testing**: Use specific test tasks instead of running all tests during development

## Customization

You can customize the configuration by modifying:
- `settings.json`: Workspace-specific settings
- `tasks.json`: Add new build or test tasks
- `launch.json`: Add new debugging configurations
- `c_cpp_properties.json`: Modify include paths or compiler settings

## Integration with CI/CD

The VS Code tasks are designed to match the project's Makefile and testing infrastructure, ensuring consistency between local development and continuous integration environments.
