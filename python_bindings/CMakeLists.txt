cmake_minimum_required(VERSION 3.12)

# Find pybind11
find_package(pybind11 REQUIRED)

# Create the Python module
pybind11_add_module(lc3_simulator lc3_simulator.cpp)

# Include directories
target_include_directories(lc3_simulator PRIVATE ..)

# Compiler-specific options
target_compile_definitions(lc3_simulator PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_compile_features(lc3_simulator PRIVATE cxx_std_11)
