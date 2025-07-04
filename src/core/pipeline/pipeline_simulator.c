#include "pipeline_config.h"
#include "../memory/memory.h"
#include "../memory/register.h"
#include "../types/opcode.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

/**
 * Pipeline Simulator Implementation
 * Provides configurable pipeline simulation for ISA performance testing
 */

// Global pipeline state
static pipeline_config_t g_pipeline_config;
static pipeline_metrics_t g_pipeline_metrics;
static instruction_packet_t g_pipeline[8];  // Max 8 stages
static uint32_t g_current_cycle = 0;
static bool g_pipeline_initialized = false;

// Instruction classification tables
static const char* stage_names[STAGE_MAX] = {
    "FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK", "CUSTOM"
};

static const char* hazard_names[HAZARD_MAX] = {
    "NONE", "DATA_RAW", "DATA_WAW", "DATA_WAR", "CONTROL", "STRUCTURAL"
};

/**
 * Initialize pipeline configuration with default values
 */
void pipeline_config_init_default(pipeline_config_t *config) {
    if (!config) return;

    strcpy(config->name, "Default 5-Stage Pipeline");

    // Default 5-stage pipeline
    config->stages[0] = STAGE_FETCH;
    config->stages[1] = STAGE_DECODE;
    config->stages[2] = STAGE_EXECUTE;
    config->stages[3] = STAGE_MEMORY;
    config->stages[4] = STAGE_WRITEBACK;
    config->depth = 5;

    config->forwarding_enabled = true;
    config->branch_prediction_enabled = false;
    config->out_of_order_execution = false;

    // Timing parameters
    config->clock_frequency = 100;      // 100 MHz
    config->memory_latency = 1;         // 1 cycle
    config->branch_penalty = 2;         // 2 cycles

    // I-Cache configuration
    config->icache.enabled = true;
    config->icache.size = 4096;         // 4KB
    config->icache.line_size = 32;      // 32 bytes
    config->icache.associativity = 1;   // Direct mapped
    config->icache.hit_latency = 1;     // 1 cycle
    config->icache.miss_penalty = 10;   // 10 cycles

    // D-Cache configuration
    config->dcache.enabled = true;
    config->dcache.size = 4096;         // 4KB
    config->dcache.line_size = 32;      // 32 bytes
    config->dcache.associativity = 1;   // Direct mapped
    config->dcache.hit_latency = 1;     // 1 cycle
    config->dcache.miss_penalty = 10;   // 10 cycles

    config->enable_detailed_metrics = true;
    config->enable_pipeline_trace = false;
}

/**
 * Reset pipeline metrics
 */
void pipeline_metrics_reset(pipeline_metrics_t *metrics) {
    if (!metrics) return;

    metrics->total_cycles = 0;
    metrics->total_instructions = 0;
    metrics->stall_cycles = 0;
    metrics->cpi = 0.0;
    metrics->ipc = 0.0;
    metrics->pipeline_efficiency = 0.0;

    metrics->data_hazards = 0;
    metrics->control_hazards = 0;
    metrics->structural_hazards = 0;

    metrics->icache_hits = 0;
    metrics->icache_misses = 0;
    metrics->dcache_hits = 0;
    metrics->dcache_misses = 0;

    metrics->branches_total = 0;
    metrics->branches_predicted_correct = 0;
    metrics->branches_predicted_incorrect = 0;

    metrics->memory_reads = 0;
    metrics->memory_writes = 0;
    metrics->memory_stall_cycles = 0;
}

/**
 * Calculate derived metrics from basic counters
 */
void pipeline_metrics_calculate(pipeline_metrics_t *metrics) {
    if (!metrics || metrics->total_instructions == 0) return;

    metrics->cpi = (double)metrics->total_cycles / metrics->total_instructions;
    metrics->ipc = (double)metrics->total_instructions / metrics->total_cycles;

    // Pipeline efficiency = actual IPC / theoretical max IPC
    double theoretical_max_ipc = 1.0;  // For in-order pipeline
    if (g_pipeline_config.out_of_order_execution) {
        theoretical_max_ipc = g_pipeline_config.depth;  // Superscalar potential
    }
    metrics->pipeline_efficiency = metrics->ipc / theoretical_max_ipc;
}

/**
 * Initialize an instruction packet
 */
void instruction_packet_init(instruction_packet_t *packet) {
    if (!packet) return;

    packet->instruction = 0;
    packet->pc = 0;
    packet->opcode = 0;

    packet->dest_reg = 0;
    packet->src_reg1 = 0;
    packet->src_reg2 = 0;
    packet->immediate = 0;

    packet->issue_cycle = 0;
    packet->completion_cycle = 0;
    packet->current_stage = STAGE_FETCH;

    for (int i = 0; i < STAGE_MAX; i++) {
        packet->stage_completed[i] = false;
    }

    for (int i = 0; i < 4; i++) {
        packet->hazards[i] = HAZARD_NONE;
    }
    packet->num_hazards = 0;
    packet->stalled = false;
    packet->stall_cycles = 0;

    packet->needs_memory = false;
    packet->memory_address = 0;
    packet->is_load = false;
    packet->is_store = false;

    packet->is_branch = false;
    packet->branch_taken = false;
    packet->branch_target = 0;
}

/**
 * Initialize the pipeline simulator
 */
void pipeline_init() {
    pipeline_config_init_default(&g_pipeline_config);
    pipeline_metrics_reset(&g_pipeline_metrics);

    // Initialize all pipeline stages
    for (int i = 0; i < 8; i++) {
        instruction_packet_init(&g_pipeline[i]);
    }

    g_current_cycle = 0;
    g_pipeline_initialized = true;
}

/**
 * Decode instruction and fill packet information
 */
void decode_instruction(instruction_packet_t *packet, uint16_t instruction, uint16_t pc) {
    packet->instruction = instruction;
    packet->pc = pc;
    packet->opcode = CAST_TO_OPCODE(instruction);

    // Extract operands based on instruction format
    switch (packet->opcode) {
        case ADD:
        case AND:
            packet->dest_reg = (instruction >> 9) & 0x7;
            packet->src_reg1 = (instruction >> 6) & 0x7;
            if (instruction & 0x20) {
                // Immediate mode
                packet->immediate = instruction & 0x1F;
                packet->src_reg2 = 0;
            } else {
                // Register mode
                packet->src_reg2 = instruction & 0x7;
                packet->immediate = 0;
            }
            break;

        case NOT:
            packet->dest_reg = (instruction >> 9) & 0x7;
            packet->src_reg1 = (instruction >> 6) & 0x7;
            packet->src_reg2 = 0;
            packet->immediate = 0;
            break;

        case LD:
        case LDI:
        case LEA:
        case ST:
        case STI:
            packet->dest_reg = (instruction >> 9) & 0x7;
            packet->src_reg1 = 0;
            packet->src_reg2 = 0;
            packet->immediate = instruction & 0x1FF;
            packet->needs_memory = (packet->opcode == LD || packet->opcode == LDI ||
                                  packet->opcode == ST || packet->opcode == STI);
            packet->is_load = (packet->opcode == LD || packet->opcode == LDI);
            packet->is_store = (packet->opcode == ST || packet->opcode == STI);
            break;

        case LDR:
        case STR:
            packet->dest_reg = (instruction >> 9) & 0x7;
            packet->src_reg1 = (instruction >> 6) & 0x7;
            packet->src_reg2 = 0;
            packet->immediate = instruction & 0x3F;
            packet->needs_memory = true;
            packet->is_load = (packet->opcode == LDR);
            packet->is_store = (packet->opcode == STR);
            break;

        case BR:
            packet->dest_reg = 0;
            packet->src_reg1 = 0;
            packet->src_reg2 = 0;
            packet->immediate = instruction & 0x1FF;
            packet->is_branch = true;
            break;

        case JMP:
        case JSR:
            packet->dest_reg = 0;
            packet->src_reg1 = (instruction >> 6) & 0x7;
            packet->src_reg2 = 0;
            packet->immediate = instruction & 0x7FF;
            packet->is_branch = true;
            break;

        default:
            // Unknown instruction
            break;
    }
}

/**
 * Check for data hazards between two instructions
 */
hazard_type_t check_data_hazard(instruction_packet_t *current, instruction_packet_t *previous) {
    if (!current || !previous) return HAZARD_NONE;

    // RAW hazard: previous instruction writes to register that current reads
    if (previous->dest_reg != 0 &&
        (current->src_reg1 == previous->dest_reg || current->src_reg2 == previous->dest_reg)) {
        return HAZARD_DATA_RAW;
    }

    // WAW hazard: both instructions write to same register
    if (current->dest_reg != 0 && previous->dest_reg != 0 &&
        current->dest_reg == previous->dest_reg) {
        return HAZARD_DATA_WAW;
    }

    // WAR hazard: current writes to register that previous reads
    if (current->dest_reg != 0 &&
        (previous->src_reg1 == current->dest_reg || previous->src_reg2 == current->dest_reg)) {
        return HAZARD_DATA_WAR;
    }

    return HAZARD_NONE;
}

/**
 * Check for control hazards
 */
bool check_control_hazard(instruction_packet_t *packet) {
    return packet->is_branch;
}

/**
 * Simulate cache access
 */
bool simulate_cache_access(cache_config_t *cache, uint16_t address, bool is_write) {
    if (!cache->enabled) {
        g_pipeline_metrics.memory_stall_cycles += g_pipeline_config.memory_latency;
        return true;  // Always hit if cache disabled
    }

    // Simple cache simulation (direct mapped)
    uint32_t cache_lines = cache->size / cache->line_size;
    uint32_t line_index = (address / cache->line_size) % cache_lines;

    // Simulate 90% hit rate for demonstration
    bool hit = ((address + g_current_cycle) % 10) < 9;

    if (hit) {
        g_pipeline_metrics.memory_stall_cycles += cache->hit_latency;
        if (is_write) {
            g_pipeline_metrics.dcache_hits++;
        } else {
            g_pipeline_metrics.icache_hits++;
        }
    } else {
        g_pipeline_metrics.memory_stall_cycles += cache->miss_penalty;
        if (is_write) {
            g_pipeline_metrics.dcache_misses++;
        } else {
            g_pipeline_metrics.icache_misses++;
        }
    }

    return hit;
}

/**
 * Execute one pipeline cycle
 */
void pipeline_cycle() {
    if (!g_pipeline_initialized) {
        pipeline_init();
    }

    g_current_cycle++;
    g_pipeline_metrics.total_cycles++;

    // Process each stage in reverse order (to avoid conflicts)
    for (int stage = g_pipeline_config.depth - 1; stage >= 0; stage--) {
        instruction_packet_t *packet = &g_pipeline[stage];

        if (packet->instruction == 0) continue;  // Empty stage

        stage_type_t current_stage = g_pipeline_config.stages[stage];

        switch (current_stage) {
            case STAGE_FETCH:
                // Simulate instruction cache access
                simulate_cache_access(&g_pipeline_config.icache, packet->pc, false);
                packet->stage_completed[STAGE_FETCH] = true;
                break;

            case STAGE_DECODE:
                // Check for hazards with previous instructions
                for (int i = stage + 1; i < g_pipeline_config.depth; i++) {
                    hazard_type_t hazard = check_data_hazard(packet, &g_pipeline[i]);
                    if (hazard != HAZARD_NONE) {
                        packet->hazards[packet->num_hazards++] = hazard;
                        if (!g_pipeline_config.forwarding_enabled) {
                            packet->stalled = true;
                            packet->stall_cycles++;
                            g_pipeline_metrics.stall_cycles++;
                            g_pipeline_metrics.data_hazards++;
                        }
                    }
                }

                if (!packet->stalled) {
                    packet->stage_completed[STAGE_DECODE] = true;
                }
                break;

            case STAGE_EXECUTE:
                if (packet->is_branch && check_control_hazard(packet)) {
                    g_pipeline_metrics.control_hazards++;
                    if (!g_pipeline_config.branch_prediction_enabled) {
                        g_pipeline_metrics.stall_cycles += g_pipeline_config.branch_penalty;
                    }
                    g_pipeline_metrics.branches_total++;
                }
                packet->stage_completed[STAGE_EXECUTE] = true;
                break;

            case STAGE_MEMORY:
                if (packet->needs_memory) {
                    simulate_cache_access(&g_pipeline_config.dcache, packet->memory_address, packet->is_store);
                    if (packet->is_load) {
                        g_pipeline_metrics.memory_reads++;
                    } else if (packet->is_store) {
                        g_pipeline_metrics.memory_writes++;
                    }
                }
                packet->stage_completed[STAGE_MEMORY] = true;
                break;

            case STAGE_WRITEBACK:
                packet->completion_cycle = g_current_cycle;
                g_pipeline_metrics.total_instructions++;
                packet->stage_completed[STAGE_WRITEBACK] = true;

                // Clear the stage
                instruction_packet_init(packet);
                break;

            default:
                break;
        }

        // Advance to next stage if not stalled
        if (!packet->stalled && stage < g_pipeline_config.depth - 1) {
            if (g_pipeline[stage + 1].instruction == 0) {  // Next stage is empty
                g_pipeline[stage + 1] = *packet;
                instruction_packet_init(packet);
            }
        }
    }
}

/**
 * Issue a new instruction into the pipeline
 */
void pipeline_issue_instruction(uint16_t instruction, uint16_t pc) {
    instruction_packet_t *packet = &g_pipeline[0];

    if (packet->instruction != 0) {
        // Pipeline stall - can't issue new instruction
        g_pipeline_metrics.stall_cycles++;
        g_pipeline_metrics.structural_hazards++;
        return;
    }

    instruction_packet_init(packet);
    decode_instruction(packet, instruction, pc);
    packet->issue_cycle = g_current_cycle;
}

/**
 * Get current pipeline statistics
 */
void pipeline_get_metrics(pipeline_metrics_t *metrics) {
    if (!metrics) return;
    *metrics = g_pipeline_metrics;
    pipeline_metrics_calculate(metrics);
}

/**
 * Print pipeline configuration
 */
void pipeline_print_config() {
    printf("=== Pipeline Configuration ===\n");
    printf("Name: %s\n", g_pipeline_config.name);
    printf("Depth: %d stages\n", g_pipeline_config.depth);
    printf("Stages: ");
    for (int i = 0; i < g_pipeline_config.depth; i++) {
        printf("%s ", stage_names[g_pipeline_config.stages[i]]);
    }
    printf("\n");
    printf("Forwarding: %s\n", g_pipeline_config.forwarding_enabled ? "Enabled" : "Disabled");
    printf("Branch Prediction: %s\n", g_pipeline_config.branch_prediction_enabled ? "Enabled" : "Disabled");
    printf("Out-of-Order: %s\n", g_pipeline_config.out_of_order_execution ? "Enabled" : "Disabled");
    printf("Clock Frequency: %u MHz\n", g_pipeline_config.clock_frequency);
    printf("Branch Penalty: %u cycles\n", g_pipeline_config.branch_penalty);
    printf("===============================\n");
}

/**
 * Print pipeline metrics
 */
void pipeline_print_metrics() {
    pipeline_metrics_calculate(&g_pipeline_metrics);

    printf("=== Pipeline Performance Metrics ===\n");
    printf("Total Cycles: %llu\n", g_pipeline_metrics.total_cycles);
    printf("Total Instructions: %llu\n", g_pipeline_metrics.total_instructions);
    printf("Stall Cycles: %llu\n", g_pipeline_metrics.stall_cycles);
    printf("CPI: %.3f\n", g_pipeline_metrics.cpi);
    printf("IPC: %.3f\n", g_pipeline_metrics.ipc);
    printf("Pipeline Efficiency: %.1f%%\n", g_pipeline_metrics.pipeline_efficiency * 100);

    printf("\nHazard Statistics:\n");
    printf("  Data Hazards: %llu\n", g_pipeline_metrics.data_hazards);
    printf("  Control Hazards: %llu\n", g_pipeline_metrics.control_hazards);
    printf("  Structural Hazards: %llu\n", g_pipeline_metrics.structural_hazards);

    printf("\nCache Statistics:\n");
    printf("  I-Cache Hits: %llu, Misses: %llu\n",
           g_pipeline_metrics.icache_hits, g_pipeline_metrics.icache_misses);
    printf("  D-Cache Hits: %llu, Misses: %llu\n",
           g_pipeline_metrics.dcache_hits, g_pipeline_metrics.dcache_misses);

    if (g_pipeline_metrics.branches_total > 0) {
        printf("\nBranch Statistics:\n");
        printf("  Total Branches: %llu\n", g_pipeline_metrics.branches_total);
        printf("  Predicted Correct: %llu\n", g_pipeline_metrics.branches_predicted_correct);
        printf("  Predicted Incorrect: %llu\n", g_pipeline_metrics.branches_predicted_incorrect);
    }

    printf("=====================================\n");
}
