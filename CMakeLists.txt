cmake_minimum_required(VERSION 3.12.0)
project(simulator-lc3 VERSION 0.1.0)

include(CTest)
enable_testing()

# Option to build Python bindings
option(BUILD_PYTHON_BINDINGS "Build Python bindings for testing" OFF)

add_subdirectory(mem)
add_subdirectory(state_machine)
add_subdirectory(type)

add_executable(simulator-lc3 main.cpp)

target_link_libraries(simulator-lc3 state_machine mem type)

# Add Python bindings if requested
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(python_bindings)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
