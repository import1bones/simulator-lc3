#include "control_store.h"
#include "../types/opcode.h"
#include <string.h>

// Global control store variables
micro_instruction_t control_store[0x40];
uint32_t micro_sequencer[0x40];
micro_instruction_t *control_store_ptr = control_store;

// Global pipeline state
lc3_pipeline_config_t lc3_pipeline_config;
lc3_pipeline_metrics_t lc3_pipeline_metrics;
lc3_instruction_packet_t lc3_pipeline[8];  // Max 8 stage pipeline
uint32_t lc3_current_cycle = 0;
bool lc3_pipeline_enabled = false;

/**
 * Initialize pipeline configuration with default values
 */
void lc3_pipeline_config_init_default(lc3_pipeline_config_t *config) {
    if (!config) return;

    strcpy(config->name, "LC-3 Default Pipeline");

    // Default 5-stage pipeline
    config->stages[0] = LC3_STAGE_FETCH;
    config->stages[1] = LC3_STAGE_DECODE;
    config->stages[2] = LC3_STAGE_EXECUTE;
    config->stages[3] = LC3_STAGE_MEMORY;
    config->stages[4] = LC3_STAGE_WRITEBACK;
    config->depth = 5;

    config->forwarding_enabled = true;
    config->branch_prediction_enabled = false;
    config->out_of_order_execution = false;

    // Timing parameters
    config->clock_frequency = 100;      // 100 MHz
    config->memory_latency = 1;         // 1 cycle
    config->branch_penalty = 2;         // 2 cycles

    config->enable_detailed_metrics = true;
    config->enable_pipeline_trace = false;
}

/**
 * Reset pipeline metrics
 */
void lc3_pipeline_metrics_reset(lc3_pipeline_metrics_t *metrics) {
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

    metrics->memory_reads = 0;
    metrics->memory_writes = 0;
    metrics->memory_stall_cycles = 0;
}

/**
 * Initialize an instruction packet
 */
void lc3_instruction_packet_init(lc3_instruction_packet_t *packet) {
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
    packet->current_stage = LC3_STAGE_FETCH;

    for (int i = 0; i < LC3_STAGE_MAX; i++) {
        packet->stage_completed[i] = false;
    }

    for (int i = 0; i < 4; i++) {
        packet->hazards[i] = LC3_HAZARD_NONE;
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
 * Initialize the LC-3 pipeline
 */
void lc3_pipeline_init(void) {
    lc3_pipeline_config_init_default(&lc3_pipeline_config);
    lc3_pipeline_metrics_reset(&lc3_pipeline_metrics);

    // Initialize all pipeline stages
    for (int i = 0; i < 8; i++) {
        lc3_instruction_packet_init(&lc3_pipeline[i]);
    }

    lc3_current_cycle = 0;
    lc3_pipeline_enabled = true;
}

/**
 * Reset the LC-3 pipeline
 */
void lc3_pipeline_reset(void) {
    lc3_pipeline_metrics_reset(&lc3_pipeline_metrics);

    // Clear all pipeline stages
    for (int i = 0; i < 8; i++) {
        lc3_instruction_packet_init(&lc3_pipeline[i]);
    }

    lc3_current_cycle = 0;
}

/**
 * Configure the LC-3 pipeline
 */
void lc3_pipeline_configure(const lc3_pipeline_config_t *config) {
    if (config) {
        lc3_pipeline_config = *config;
        lc3_pipeline_reset();
    }
}

/**
 * Decode instruction and fill packet information
 */
static void lc3_decode_instruction(lc3_instruction_packet_t *packet, uint16_t instruction, uint16_t pc) {
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
static lc3_hazard_type_t lc3_check_data_hazard(lc3_instruction_packet_t *current, lc3_instruction_packet_t *previous) {
    if (!current || !previous) return LC3_HAZARD_NONE;

    // RAW hazard: previous instruction writes to register that current reads
    if (previous->dest_reg != 0 &&
        (current->src_reg1 == previous->dest_reg || current->src_reg2 == previous->dest_reg)) {
        return LC3_HAZARD_DATA_RAW;
    }

    // WAW hazard: both instructions write to same register
    if (current->dest_reg != 0 && previous->dest_reg != 0 &&
        current->dest_reg == previous->dest_reg) {
        return LC3_HAZARD_DATA_WAW;
    }

    // WAR hazard: current writes to register that previous reads
    if (current->dest_reg != 0 &&
        (previous->src_reg1 == current->dest_reg || previous->src_reg2 == current->dest_reg)) {
        return LC3_HAZARD_DATA_WAR;
    }

    return LC3_HAZARD_NONE;
}

/**
 * Execute one pipeline cycle
 */
void lc3_pipeline_cycle(void) {
    if (!lc3_pipeline_enabled) return;

    lc3_current_cycle++;
    lc3_pipeline_metrics.total_cycles++;

    // Process each stage in reverse order (to avoid conflicts)
    for (int stage = lc3_pipeline_config.depth - 1; stage >= 0; stage--) {
        lc3_instruction_packet_t *packet = &lc3_pipeline[stage];

        if (packet->instruction == 0) continue;  // Empty stage

        lc3_pipeline_stage_t current_stage = lc3_pipeline_config.stages[stage];

        switch (current_stage) {
            case LC3_STAGE_FETCH:
                packet->stage_completed[LC3_STAGE_FETCH] = true;
                break;

            case LC3_STAGE_DECODE:
                // Check for hazards with previous instructions
                for (int i = stage + 1; i < lc3_pipeline_config.depth; i++) {
                    lc3_hazard_type_t hazard = lc3_check_data_hazard(packet, &lc3_pipeline[i]);
                    if (hazard != LC3_HAZARD_NONE) {
                        packet->hazards[packet->num_hazards++] = hazard;
                        if (!lc3_pipeline_config.forwarding_enabled) {
                            packet->stalled = true;
                            packet->stall_cycles++;
                            lc3_pipeline_metrics.stall_cycles++;
                            lc3_pipeline_metrics.data_hazards++;
                        }
                    }
                }

                if (!packet->stalled) {
                    packet->stage_completed[LC3_STAGE_DECODE] = true;
                }
                break;

            case LC3_STAGE_EXECUTE:
                if (packet->is_branch) {
                    lc3_pipeline_metrics.control_hazards++;
                    if (!lc3_pipeline_config.branch_prediction_enabled) {
                        lc3_pipeline_metrics.stall_cycles += lc3_pipeline_config.branch_penalty;
                    }
                }
                packet->stage_completed[LC3_STAGE_EXECUTE] = true;
                break;

            case LC3_STAGE_MEMORY:
                if (packet->needs_memory) {
                    lc3_pipeline_metrics.memory_stall_cycles += lc3_pipeline_config.memory_latency;
                    if (packet->is_load) {
                        lc3_pipeline_metrics.memory_reads++;
                    } else if (packet->is_store) {
                        lc3_pipeline_metrics.memory_writes++;
                    }
                }
                packet->stage_completed[LC3_STAGE_MEMORY] = true;
                break;

            case LC3_STAGE_WRITEBACK:
                packet->completion_cycle = lc3_current_cycle;
                lc3_pipeline_metrics.total_instructions++;
                packet->stage_completed[LC3_STAGE_WRITEBACK] = true;

                // Clear the stage
                lc3_instruction_packet_init(packet);
                break;

            default:
                break;
        }

        // Advance to next stage if not stalled
        if (!packet->stalled && stage < lc3_pipeline_config.depth - 1) {
            if (lc3_pipeline[stage + 1].instruction == 0) {  // Next stage is empty
                lc3_pipeline[stage + 1] = *packet;
                lc3_instruction_packet_init(packet);
            }
        }
    }
}

/**
 * Issue a new instruction into the pipeline
 */
void lc3_pipeline_issue_instruction(uint16_t instruction, uint16_t pc) {
    if (!lc3_pipeline_enabled) return;

    lc3_instruction_packet_t *packet = &lc3_pipeline[0];

    if (packet->instruction != 0) {
        // Pipeline stall - can't issue new instruction
        lc3_pipeline_metrics.stall_cycles++;
        lc3_pipeline_metrics.structural_hazards++;
        return;
    }

    lc3_instruction_packet_init(packet);
    lc3_decode_instruction(packet, instruction, pc);
    packet->issue_cycle = lc3_current_cycle;
}

/**
 * Get current pipeline statistics
 */
void lc3_pipeline_get_metrics(lc3_pipeline_metrics_t *metrics) {
    if (!metrics) return;

    *metrics = lc3_pipeline_metrics;

    // Calculate derived metrics
    if (metrics->total_instructions > 0) {
        metrics->cpi = (double)metrics->total_cycles / metrics->total_instructions;
        metrics->ipc = (double)metrics->total_instructions / metrics->total_cycles;

        // Pipeline efficiency = actual IPC / theoretical max IPC
        double theoretical_max_ipc = 1.0;  // For in-order pipeline
        if (lc3_pipeline_config.out_of_order_execution) {
            theoretical_max_ipc = lc3_pipeline_config.depth;  // Superscalar potential
        }
        metrics->pipeline_efficiency = metrics->ipc / theoretical_max_ipc;
    }
}
