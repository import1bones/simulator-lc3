cmake_minimum_required(VERSION 3.12.0)

# Pipeline Performance Analysis Library
add_library(pipeline
    pipeline_simulator.c
)

target_include_directories(pipeline PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(pipeline mem type)

# Install headers
install(FILES
    pipeline_config.h
    pipeline_simulator.h
    DESTINATION include/pipeline
)

# Install Python analysis scripts
install(FILES
    pipeline_tester.py
    isa_extension_analyzer.py
    DESTINATION scripts/pipeline
)
