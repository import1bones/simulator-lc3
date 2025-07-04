cmake_minimum_required(VERSION 3.12.0)
project(simulator-lc3 VERSION 0.1.0)

include(CTest)
enable_testing()

# Option to build Python bindings
option(BUILD_PYTHON_BINDINGS "Build Python bindings for testing" ON)

# Option to build pipeline extensions
option(BUILD_PIPELINE_EXTENSIONS "Build pipeline performance analysis extensions" ON)

# Add core subdirectories
add_subdirectory(src/core/memory)
add_subdirectory(src/core/state_machine)
add_subdirectory(src/core/types)

# Use main.cpp from src directory
add_executable(simulator-lc3 src/main.cpp)

# Link libraries - pipeline functionality is now integrated into mem module
target_link_libraries(simulator-lc3 state_machine mem type)

# Add include directories for main executable
target_include_directories(simulator-lc3 PRIVATE src/core)

# Add Python bindings if requested
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(python_bindings)
endif()

# Add pipeline extensions if requested
if(BUILD_PIPELINE_EXTENSIONS)
    add_subdirectory(src/core/pipeline)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
