#ifndef PIPELINE_CONFIG_H
#define PIPELINE_CONFIG_H

#include "../types/type.h"
#include <stdint.h>
#include <stdbool.h>

/**
 * Pipeline Stage Types
 */
typedef enum {
    STAGE_FETCH = 0,        // Instruction fetch
    STAGE_DECODE,           // Instruction decode
    STAGE_EXECUTE,          // Execute/ALU operations
    STAGE_MEMORY,           // Memory access
    STAGE_WRITEBACK,        // Register writeback
    STAGE_CUSTOM,           // User-defined stage
    STAGE_MAX
} stage_type_t;

/**
 * Pipeline Hazard Types
 */
typedef enum {
    HAZARD_NONE = 0,
    HAZARD_DATA_RAW,        // Read After Write
    HAZARD_DATA_WAW,        // Write After Write
    HAZARD_DATA_WAR,        // Write After Read
    HAZARD_CONTROL,         // Branch/Jump hazards
    HAZARD_STRUCTURAL,      // Resource conflicts
    HAZARD_MAX
} hazard_type_t;

/**
 * Cache Configuration
 */
typedef struct {
    bool enabled;
    uint32_t size;              // in bytes
    uint32_t line_size;         // in bytes
    uint8_t associativity;
    uint32_t hit_latency;       // in cycles
    uint32_t miss_penalty;      // in cycles
} cache_config_t;

/**
 * Pipeline Configuration Structure
 */
typedef struct {
    char name[64];
    stage_type_t stages[8];     // Max 8 pipeline stages
    uint8_t depth;
    bool forwarding_enabled;
    bool branch_prediction_enabled;
    bool out_of_order_execution;

    // Timing parameters
    uint32_t clock_frequency;   // in MHz
    uint32_t memory_latency;    // in cycles
    uint32_t branch_penalty;    // in cycles

    // Cache configuration
    cache_config_t icache;
    cache_config_t dcache;

    // Performance monitoring
    bool enable_detailed_metrics;
    bool enable_pipeline_trace;
} pipeline_config_t;

/**
 * Custom Instruction Definition
 */
typedef struct {
    char name[32];
    uint16_t opcode;
    uint16_t mask;
    stage_type_t required_stages[8];
    uint8_t num_stages;
    uint32_t execution_cycles;
    bool uses_memory;
    bool is_branch;
    char description[128];
} custom_instruction_t;

/**
 * Pipeline Performance Metrics
 */
typedef struct {
    // Basic metrics
    uint64_t total_cycles;
    uint64_t total_instructions;
    uint64_t stall_cycles;

    // Performance ratios
    double cpi;                 // Cycles per instruction
    double ipc;                 // Instructions per cycle
    double pipeline_efficiency; // Actual IPC / Theoretical max IPC

    // Hazard statistics
    uint64_t data_hazards;
    uint64_t control_hazards;
    uint64_t structural_hazards;

    // Cache statistics
    uint64_t icache_hits;
    uint64_t icache_misses;
    uint64_t dcache_hits;
    uint64_t dcache_misses;

    // Branch prediction statistics
    uint64_t branches_total;
    uint64_t branches_predicted_correct;
    uint64_t branches_predicted_incorrect;

    // Memory access statistics
    uint64_t memory_reads;
    uint64_t memory_writes;
    uint64_t memory_stall_cycles;
} pipeline_metrics_t;

/**
 * Instruction Packet
 * Represents an instruction as it flows through the pipeline
 */
typedef struct {
    uint16_t instruction;
    uint16_t pc;
    uint16_t opcode;

    // Operand information
    uint8_t dest_reg;
    uint8_t src_reg1;
    uint8_t src_reg2;
    uint16_t immediate;

    // Pipeline state
    uint32_t issue_cycle;
    uint32_t completion_cycle;
    stage_type_t current_stage;
    bool stage_completed[STAGE_MAX];

    // Hazard tracking
    hazard_type_t hazards[4];   // Max 4 hazards per instruction
    uint8_t num_hazards;
    bool stalled;
    uint32_t stall_cycles;

    // Memory access info
    bool needs_memory;
    uint16_t memory_address;
    bool is_load;
    bool is_store;

    // Branch info
    bool is_branch;
    bool branch_taken;
    uint16_t branch_target;
} instruction_packet_t;

// Function declarations for pipeline management
void pipeline_config_init_default(pipeline_config_t *config);
void pipeline_metrics_reset(pipeline_metrics_t *metrics);
void pipeline_metrics_calculate(pipeline_metrics_t *metrics);
void instruction_packet_init(instruction_packet_t *packet);

#endif // PIPELINE_CONFIG_H
