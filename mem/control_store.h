#ifndef CONTROL_STORE_H
#define CONTROL_STORE_H

#include"../type/type.h"
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint64_t micro_instruction_t;

// External declarations (definitions in control_store.c)
extern micro_instruction_t control_store[0x40];
extern uint32_t micro_sequencer[0x40];
extern micro_instruction_t *control_store_ptr;

/**
 * Pipeline Stage Types for LC-3
 */
typedef enum {
    LC3_STAGE_FETCH = 0,
    LC3_STAGE_DECODE,
    LC3_STAGE_EXECUTE,
    LC3_STAGE_MEMORY,
    LC3_STAGE_WRITEBACK,
    LC3_STAGE_CUSTOM,
    LC3_STAGE_MAX
} lc3_pipeline_stage_t;

/**
 * Pipeline Hazard Types
 */
typedef enum {
    LC3_HAZARD_NONE = 0,
    LC3_HAZARD_DATA_RAW,     // Read After Write
    LC3_HAZARD_DATA_WAW,     // Write After Write
    LC3_HAZARD_DATA_WAR,     // Write After Read
    LC3_HAZARD_CONTROL,      // Branch/Jump hazards
    LC3_HAZARD_STRUCTURAL,   // Resource conflicts
    LC3_HAZARD_MAX
} lc3_hazard_type_t;

/**
 * LC-3 Pipeline Configuration
 */
typedef struct {
    char name[64];
    lc3_pipeline_stage_t stages[8];  // Max 8 pipeline stages
    uint8_t depth;
    bool forwarding_enabled;
    bool branch_prediction_enabled;
    bool out_of_order_execution;

    // Timing parameters
    uint32_t clock_frequency;        // in MHz
    uint32_t memory_latency;         // in cycles
    uint32_t branch_penalty;         // in cycles

    // Performance monitoring
    bool enable_detailed_metrics;
    bool enable_pipeline_trace;
} lc3_pipeline_config_t;

/**
 * LC-3 Pipeline Performance Metrics
 */
typedef struct {
    // Basic metrics
    uint64_t total_cycles;
    uint64_t total_instructions;
    uint64_t stall_cycles;

    // Performance ratios
    double cpi;                      // Cycles per instruction
    double ipc;                      // Instructions per cycle
    double pipeline_efficiency;     // Actual IPC / Theoretical max IPC

    // Hazard statistics
    uint64_t data_hazards;
    uint64_t control_hazards;
    uint64_t structural_hazards;

    // Memory access statistics
    uint64_t memory_reads;
    uint64_t memory_writes;
    uint64_t memory_stall_cycles;
} lc3_pipeline_metrics_t;

/**
 * LC-3 Instruction Pipeline Packet
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
    lc3_pipeline_stage_t current_stage;
    bool stage_completed[LC3_STAGE_MAX];

    // Hazard tracking
    lc3_hazard_type_t hazards[4];    // Max 4 hazards per instruction
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
} lc3_instruction_packet_t;

/**
 * Traditional LC-3 Control Signals
 */
struct control_signals
{
    uint8_t J;
    uint8_t COND;
    uint8_t IRD;
};

// Global pipeline state
extern lc3_pipeline_config_t lc3_pipeline_config;
extern lc3_pipeline_metrics_t lc3_pipeline_metrics;
extern lc3_instruction_packet_t lc3_pipeline[8];  // Max 8 stage pipeline
extern uint32_t lc3_current_cycle;
extern bool lc3_pipeline_enabled;

// Pipeline management functions
void lc3_pipeline_init(void);
void lc3_pipeline_reset(void);
void lc3_pipeline_configure(const lc3_pipeline_config_t *config);
void lc3_pipeline_cycle(void);
void lc3_pipeline_issue_instruction(uint16_t instruction, uint16_t pc);
void lc3_pipeline_get_metrics(lc3_pipeline_metrics_t *metrics);

// Helper functions
void lc3_pipeline_config_init_default(lc3_pipeline_config_t *config);
void lc3_pipeline_metrics_reset(lc3_pipeline_metrics_t *metrics);
void lc3_instruction_packet_init(lc3_instruction_packet_t *packet);

#ifdef __cplusplus
}
#endif

#endif //CONTROL_STORE_H
