/**
 * LC-3 Pipeline Demo Program
 * Shows how to use the integrated pipeline functionality
 */
#include <stdio.h>
#include "mem/control_store.h"

void demo_pipeline_basic() {
    printf("\n=== Basic Pipeline Demo ===\n");

    // Initialize pipeline
    lc3_pipeline_init();
    printf("Pipeline initialized with configuration: %s\n", lc3_pipeline_config.name);

    // Enable pipeline mode
    lc3_pipeline_enabled = true;

    // Demo some sample instructions
    uint16_t instructions[] = {
        0x1220,  // ADD R1, R0, #0
        0x1401,  // ADD R2, R0, #1
        0x1622,  // ADD R3, R0, #2
        0x1843,  // ADD R4, R0, #3
        0xF025   // HALT
    };

    printf("Issuing instructions to pipeline:\n");
    for (int i = 0; i < 5; i++) {
        printf("  Cycle %d: Issuing instruction 0x%04X\n", lc3_current_cycle + 1, instructions[i]);
        lc3_pipeline_issue_instruction(instructions[i], 0x3000 + i);
        lc3_pipeline_cycle();

        // Show pipeline state
        lc3_pipeline_metrics_t metrics;
        lc3_pipeline_get_metrics(&metrics);
        printf("    Total instructions: %llu, CPI: %.2f\n",
               metrics.total_instructions, metrics.cpi);
    }

    // Run a few more cycles to clear the pipeline
    printf("Running additional cycles to clear pipeline:\n");
    for (int i = 0; i < lc3_pipeline_config.depth; i++) {
        lc3_pipeline_cycle();
        lc3_pipeline_metrics_t metrics;
        lc3_pipeline_get_metrics(&metrics);
        printf("  Cycle %d: Instructions completed: %llu\n",
               lc3_current_cycle, metrics.total_instructions);
    }
}

void demo_pipeline_hazards() {
    printf("\n=== Pipeline Hazard Demo ===\n");

    // Reset pipeline
    lc3_pipeline_reset();

    // Configure pipeline without forwarding to show hazards
    lc3_pipeline_config.forwarding_enabled = false;
    printf("Forwarding disabled to demonstrate hazards\n");

    // Instructions that create data hazards
    uint16_t hazard_instructions[] = {
        0x1220,  // ADD R1, R0, #0    (writes R1)
        0x1401,  // ADD R2, R0, R1    (reads R1 - RAW hazard!)
        0x1622   // ADD R3, R1, #2    (reads R1 - another RAW hazard!)
    };

    printf("Issuing instructions with data hazards:\n");
    for (int i = 0; i < 3; i++) {
        printf("  Issuing instruction 0x%04X\n", hazard_instructions[i]);
        lc3_pipeline_issue_instruction(hazard_instructions[i], 0x3000 + i);
        lc3_pipeline_cycle();

        lc3_pipeline_metrics_t metrics;
        lc3_pipeline_get_metrics(&metrics);
        printf("    Data hazards detected: %llu, Stalls: %llu\n",
               metrics.data_hazards, metrics.stall_cycles);
    }

    // Now enable forwarding and reset
    printf("\nEnabling forwarding and repeating...\n");
    lc3_pipeline_reset();
    lc3_pipeline_config.forwarding_enabled = true;

    for (int i = 0; i < 3; i++) {
        lc3_pipeline_issue_instruction(hazard_instructions[i], 0x3000 + i);
        lc3_pipeline_cycle();

        lc3_pipeline_metrics_t metrics;
        lc3_pipeline_get_metrics(&metrics);
        printf("    With forwarding - Stalls: %llu\n", metrics.stall_cycles);
    }
}

void demo_pipeline_performance() {
    printf("\n=== Pipeline Performance Analysis ===\n");

    // Reset and configure for performance test
    lc3_pipeline_reset();
    lc3_pipeline_config_init_default(&lc3_pipeline_config);

    // Run a larger set of instructions
    printf("Running performance benchmark with %d instructions...\n", 100);

    for (int i = 0; i < 100; i++) {
        uint16_t instr = 0x1220 + (i % 8);  // Various ADD instructions
        lc3_pipeline_issue_instruction(instr, 0x3000 + i);
        lc3_pipeline_cycle();
    }

    // Clear pipeline
    for (int i = 0; i < lc3_pipeline_config.depth; i++) {
        lc3_pipeline_cycle();
    }

    // Show final performance metrics
    lc3_pipeline_metrics_t final_metrics;
    lc3_pipeline_get_metrics(&final_metrics);

    printf("Final Performance Results:\n");
    printf("  Total Instructions: %llu\n", final_metrics.total_instructions);
    printf("  Total Cycles: %llu\n", final_metrics.total_cycles);
    printf("  CPI (Cycles per Instruction): %.3f\n", final_metrics.cpi);
    printf("  IPC (Instructions per Cycle): %.3f\n", final_metrics.ipc);
    printf("  Pipeline Efficiency: %.1f%%\n", final_metrics.pipeline_efficiency * 100.0);
    printf("  Total Stalls: %llu cycles\n", final_metrics.stall_cycles);
    printf("  Data Hazards: %llu\n", final_metrics.data_hazards);
    printf("  Control Hazards: %llu\n", final_metrics.control_hazards);
    printf("  Structural Hazards: %llu\n", final_metrics.structural_hazards);
}

int main() {
    printf("LC-3 Pipeline Extension Demo\n");
    printf("============================\n");

    // Run the demos
    demo_pipeline_basic();
    demo_pipeline_hazards();
    demo_pipeline_performance();

    printf("\n=== Demo Complete ===\n");
    printf("The pipeline extension is successfully integrated into LC-3!\n");

    return 0;
}
