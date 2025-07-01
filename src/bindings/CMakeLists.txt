cmake_minimum_required(VERSION 3.12)

# Find Python first
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Find pybind11 - try different methods
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    # Try to find via Python
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE pybind11_CMAKE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE pybind11_NOT_FOUND
    )
    if(NOT pybind11_NOT_FOUND)
        set(pybind11_DIR ${pybind11_CMAKE_DIR})
        find_package(pybind11 CONFIG REQUIRED)
    else()
        message(FATAL_ERROR "pybind11 not found. Install with: pip3 install pybind11")
    endif()
endif()

# Create the Python module (simplified to avoid linking issues)
pybind11_add_module(lc3_simulator lc3_simulator.cpp)

# Include directories
target_include_directories(lc3_simulator PRIVATE ..)

# Compiler-specific options
target_compile_definitions(lc3_simulator PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_compile_features(lc3_simulator PRIVATE cxx_std_11)
