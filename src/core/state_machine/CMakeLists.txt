add_library(state_machine 
    state_machine.cpp 
    states.cpp 
    signals.cpp
    state_machine_utils.cpp
    ext.cpp
)

target_include_directories(state_machine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})