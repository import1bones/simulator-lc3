#!/bin/bash

# VS Code Setup Verification Script for LC-3 Simulator
# This script checks if all required tools and dependencies are installed

echo "🔧 LC-3 Simulator VS Code Setup Verification"
echo "============================================="
echo

# Check if we're in the right directory
if [ ! -f "CMakeLists.txt" ] || [ ! -d "state_machine" ]; then
    echo "❌ Error: Please run this script from the LC-3 simulator project root directory"
    exit 1
fi

echo "📁 Project structure: ✅"

# Check required tools
echo "🔍 Checking required tools..."

# CMake
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
    echo "  ✅ CMake: $CMAKE_VERSION"
else
    echo "  ❌ CMake: Not found (install with: brew install cmake)"
    MISSING_TOOLS=1
fi

# C++ Compiler
if command -v clang++ &> /dev/null; then
    CLANG_VERSION=$(clang++ --version | head -n1 | cut -d' ' -f4)
    echo "  ✅ Clang++: $CLANG_VERSION"
else
    echo "  ❌ Clang++: Not found"
    MISSING_TOOLS=1
fi

# Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "  ✅ Python 3: $PYTHON_VERSION"
else
    echo "  ❌ Python 3: Not found"
    MISSING_TOOLS=1
fi

# pytest
if python3 -c "import pytest" 2>/dev/null; then
    PYTEST_VERSION=$(python3 -c "import pytest; print(pytest.__version__)")
    echo "  ✅ pytest: $PYTEST_VERSION"
else
    echo "  ❌ pytest: Not found (install with: pip3 install pytest)"
    MISSING_TOOLS=1
fi

# pybind11
if python3 -c "import pybind11" 2>/dev/null; then
    PYBIND_VERSION=$(python3 -c "import pybind11; print(pybind11.__version__)")
    echo "  ✅ pybind11: $PYBIND_VERSION"
else
    echo "  ❌ pybind11: Not found (install with: pip3 install pybind11)"
    MISSING_TOOLS=1
fi

echo

# Check VS Code files
echo "📄 Checking VS Code configuration files..."
VSCODE_FILES=(
    ".vscode/tasks.json"
    ".vscode/launch.json"
    ".vscode/settings.json"
    ".vscode/c_cpp_properties.json"
    ".vscode/extensions.json"
)

for file in "${VSCODE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file: Missing"
        MISSING_CONFIG=1
    fi
done

echo

# Test basic build
echo "🔨 Testing basic build..."
if [ -d "build" ]; then
    echo "  🗑️  Cleaning existing build directory..."
    rm -rf build
fi

mkdir -p build
cd build

if cmake .. -DCMAKE_BUILD_TYPE=Debug -DBUILD_PYTHON_BINDINGS=ON &> /dev/null; then
    echo "  ✅ CMake configuration: Success"
    
    if cmake --build . --config Debug &> /dev/null; then
        echo "  ✅ Build: Success"
        BUILD_SUCCESS=1
    else
        echo "  ❌ Build: Failed"
    fi
else
    echo "  ❌ CMake configuration: Failed"
fi

cd ..

echo

# Summary
echo "📋 Summary"
echo "=========="

if [ -z "$MISSING_TOOLS" ] && [ -z "$MISSING_CONFIG" ] && [ "$BUILD_SUCCESS" ]; then
    echo "🎉 All checks passed! Your VS Code setup is ready for LC-3 simulator development."
    echo ""
    echo "💡 Next steps:"
    echo "  1. Open VS Code: code lc3-simulator.code-workspace"
    echo "  2. Install recommended extensions when prompted"
    echo "  3. Use Cmd+Shift+B to build the project"
    echo "  4. Use Cmd+Shift+T to run tests"
    echo ""
    echo "📖 See .vscode/README.md for detailed documentation"
else
    echo "⚠️  Some issues were found. Please address them before proceeding:"
    
    if [ "$MISSING_TOOLS" ]; then
        echo "  • Install missing development tools"
    fi
    
    if [ "$MISSING_CONFIG" ]; then
        echo "  • VS Code configuration files are missing"
    fi
    
    if [ -z "$BUILD_SUCCESS" ]; then
        echo "  • Build failed - check dependencies and configuration"
    fi
    
    echo ""
    echo "📖 Refer to the project README.md for installation instructions"
fi

echo
