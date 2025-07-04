/**
 * @file pipeline_simulator.h
 * @brief Pipeline Simulator implementation
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#ifndef PIPELINE_SIMULATOR_H
#define PIPELINE_SIMULATOR_H

#include "pipeline_config.h"

/**
 * Pipeline Simulator Functions
 * Provides configurable pipeline simulation for ISA performance testing
 */

// Initialization and configuration
void pipeline_init();
void pipeline_config_set(const pipeline_config_t *config);
void pipeline_config_get(pipeline_config_t *config);

// Simulation control
void pipeline_cycle();
void pipeline_issue_instruction(uint16_t instruction, uint16_t pc);
void pipeline_flush();
void pipeline_reset();

// Metrics and reporting
void pipeline_get_metrics(pipeline_metrics_t *metrics);
void pipeline_print_config();
void pipeline_print_metrics();

// Custom instruction support
void pipeline_register_custom_instruction(const custom_instruction_t *instruction);
void pipeline_remove_custom_instruction(uint16_t opcode);

// Pipeline visualization and debugging
void pipeline_print_state();
void pipeline_export_trace(const char *filename);

#endif // PIPELINE_SIMULATOR_H
