add_library(mem
    control_store.c
    memory.cpp
    register.cpp
)
target_include_directories(mem PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
