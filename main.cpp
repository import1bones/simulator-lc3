#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "state_machine/state_machine.h"
#include "state_machine/signals.h"
#include "mem/memory.h"
#include "mem/register.h"
#include "mem/device_register.h"
#include "mem/control_store.h"  // Add pipeline support
#include "type/trap_vector.h"

// Pipeline mode flag
bool pipeline_mode = false;
bool verbose_mode = false;

void initialize_simulator() {
    // Initialize registers
    for(int i = 0; i < 8; i++) {
        reg[i] = 0;
    }

    // Initialize memory
    for(int i = 0; i < UINT16_MAX; i++) {
        mem[i] = 0;
    }

    // Set up initial state
    pointer_counter = USER_SPACE_ADDR; // Start at user space
    instruction_reg = 0;
    mem_addr_reg = 0;
    mem_data_reg = 0;

    // Initialize device registers
    mem[KBSR] = 0x0000; // Keyboard status register
    mem[KBDR] = 0x0000; // Keyboard data register
    mem[DSR] = 0x8000;  // Display status register (ready)
    mem[DDR] = 0x0000;  // Display data register
    mem[PSR] = 0x8002;  // Processor status register (supervisor mode, positive CC)
    mem[MCR] = 0x8000;  // Machine control register (clock enabled)

    // Set up trap vectors
    mem[GETC] = 0x3000;  // Example trap service routine addresses
    mem[OUT] = 0x3100;
    mem[PUTS] = 0x3200;
    mem[IN] = 0x3300;
    mem[PUTSP] = 0x3400;
    mem[HALT] = 0x3500;

    // Initialize control signals
    INIT_SIGNALS();

    // Initialize pipeline if enabled
    if (pipeline_mode) {
        lc3_pipeline_init();
        lc3_pipeline_config_init_default(&lc3_pipeline_config);
        lc3_pipeline_enabled = true;
        if (verbose_mode) {
            printf("Pipeline mode enabled: %s\n", lc3_pipeline_config.name);
        }
    }
}

void load_program(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if(!file) {
        printf("Error: Cannot open file %s\n", filename);
        return;
    }

    // Read origin address
    uint16_t origin;
    if(fread(&origin, sizeof(uint16_t), 1, file) != 1) {
        printf("Error: Cannot read origin address\n");
        fclose(file);
        return;
    }

    // Convert from little-endian if necessary
    origin = ((origin & 0xFF) << 8) | ((origin >> 8) & 0xFF);

    printf("Loading program at address 0x%04X\n", origin);
    pointer_counter = origin;

    // Load program into memory
    uint16_t address = origin;
    uint16_t instruction;
    while(fread(&instruction, sizeof(uint16_t), 1, file) == 1 && address < UINT16_MAX) {
        // Convert from little-endian if necessary
        instruction = ((instruction & 0xFF) << 8) | ((instruction >> 8) & 0xFF);
        mem[address++] = instruction;
    }

    fclose(file);
    printf("Program loaded successfully\n");
}

void print_state() {
    printf("\n=== LC-3 Simulator State ===\n");
    printf("PC: 0x%04X\n", pointer_counter);
    printf("IR: 0x%04X\n", instruction_reg);
    printf("Registers:\n");
    for(int i = 0; i < 8; i++) {
        printf("  R%d: 0x%04X (%d)\n", i, reg[i], (int16_t)reg[i]);
    }
    printf("Condition Codes: N=%d Z=%d P=%d\n", N, Z, P);
    printf("PSR: 0x%04X\n", mem[PSR]);

    // Print pipeline status if enabled
    if (pipeline_mode && lc3_pipeline_enabled) {
        printf("Pipeline Status:\n");
        printf("  Mode: %s\n", lc3_pipeline_config.name);
        printf("  Depth: %d stages\n", lc3_pipeline_config.depth);
        printf("  Cycle: %u\n", lc3_current_cycle);
        printf("  CPI: %.3f\n", lc3_pipeline_metrics.cpi);
        printf("  Total Instructions: %llu\n", lc3_pipeline_metrics.total_instructions);
        printf("  Stall Cycles: %llu\n", lc3_pipeline_metrics.stall_cycles);
        printf("  Pipeline Efficiency: %.2f%%\n", lc3_pipeline_metrics.pipeline_efficiency * 100.0);
    }

    printf("=============================\n");
}

void run_interactive() {
    char command[100];
    printf("LC-3 Simulator Interactive Mode\n");
    printf("Commands: step, run, reg, mem <addr>, load <file>, reset, quit\n");
    if (pipeline_mode) {
        printf("Pipeline commands: pipeline, metrics, config\n");
    }

    while(1) {
        printf("(lc3-sim) ");
        if(!fgets(command, sizeof(command), stdin)) break;

        // Remove newline
        command[strcspn(command, "\n")] = 0;

        if(strcmp(command, "quit") == 0 || strcmp(command, "q") == 0) {
            break;
        }
        else if(strcmp(command, "step") == 0 || strcmp(command, "s") == 0) {
            uint16_t old_pc = pointer_counter;
            if (pipeline_mode && lc3_pipeline_enabled) {
                lc3_pipeline_issue_instruction(mem[pointer_counter], pointer_counter);
                lc3_pipeline_cycle();
            }
            state_machine(pointer_counter, mem, reg);
            if(pointer_counter == old_pc) pointer_counter++; // Prevent infinite loop
            print_state();
        }
        else if(strcmp(command, "run") == 0 || strcmp(command, "r") == 0) {
            printf("Running program...\n");
            state_machine(pointer_counter, mem, reg);
            printf("Program halted.\n");
            print_state();
        }
        else if(strcmp(command, "reg") == 0) {
            print_state();
        }
        else if(strncmp(command, "mem ", 4) == 0) {
            uint16_t addr = (uint16_t)strtol(command + 4, NULL, 0);
            printf("Memory[0x%04X] = 0x%04X (%d)\n", addr, mem[addr], (int16_t)mem[addr]);
        }
        else if(strncmp(command, "load ", 5) == 0) {
            load_program(command + 5);
        }
        else if(strcmp(command, "reset") == 0) {
            initialize_simulator();
            printf("Simulator reset.\n");
        }
        else if(strcmp(command, "pipeline") == 0 && pipeline_mode) {
            printf("Pipeline Status:\n");
            printf("  Enabled: %s\n", lc3_pipeline_enabled ? "Yes" : "No");
            printf("  Configuration: %s\n", lc3_pipeline_config.name);
            printf("  Depth: %d stages\n", lc3_pipeline_config.depth);
            printf("  Current Cycle: %u\n", lc3_current_cycle);
            printf("  Forwarding: %s\n", lc3_pipeline_config.forwarding_enabled ? "Enabled" : "Disabled");
            printf("  Branch Prediction: %s\n", lc3_pipeline_config.branch_prediction_enabled ? "Enabled" : "Disabled");
        }
        else if(strcmp(command, "metrics") == 0 && pipeline_mode) {
            lc3_pipeline_metrics_t metrics;
            lc3_pipeline_get_metrics(&metrics);
            printf("Pipeline Performance Metrics:\n");
            printf("  Total Cycles: %llu\n", metrics.total_cycles);
            printf("  Total Instructions: %llu\n", metrics.total_instructions);
            printf("  CPI (Cycles per Instruction): %.3f\n", metrics.cpi);
            printf("  IPC (Instructions per Cycle): %.3f\n", metrics.ipc);
            printf("  Pipeline Efficiency: %.2f%%\n", metrics.pipeline_efficiency * 100.0);
            printf("  Stall Cycles: %llu\n", metrics.stall_cycles);
            printf("  Data Hazards: %llu\n", metrics.data_hazards);
            printf("  Control Hazards: %llu\n", metrics.control_hazards);
            printf("  Structural Hazards: %llu\n", metrics.structural_hazards);
        }
        else if(strcmp(command, "config") == 0 && pipeline_mode) {
            printf("Pipeline Configuration:\n");
            printf("  Name: %s\n", lc3_pipeline_config.name);
            printf("  Stages: ");
            for(int i = 0; i < lc3_pipeline_config.depth; i++) {
                const char* stage_names[] = {"FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK", "CUSTOM"};
                printf("%s ", stage_names[lc3_pipeline_config.stages[i]]);
            }
            printf("\n");
            printf("  Clock Frequency: %u MHz\n", lc3_pipeline_config.clock_frequency);
            printf("  Memory Latency: %u cycles\n", lc3_pipeline_config.memory_latency);
            printf("  Branch Penalty: %u cycles\n", lc3_pipeline_config.branch_penalty);
        }
        else if(strcmp(command, "help") == 0 || strcmp(command, "h") == 0) {
            printf("Available commands:\n");
            printf("  step (s)     - Execute one instruction\n");
            printf("  run (r)      - Run until halt\n");
            printf("  reg          - Show register state\n");
            printf("  mem <addr>   - Show memory contents at address\n");
            printf("  load <file>  - Load program from file\n");
            printf("  reset        - Reset simulator\n");
            printf("  quit (q)     - Exit simulator\n");
            if (pipeline_mode) {
                printf("Pipeline commands:\n");
                printf("  pipeline     - Show pipeline status\n");
                printf("  metrics      - Show performance metrics\n");
                printf("  config       - Show pipeline configuration\n");
            }
        }
        else {
            printf("Unknown command. Type 'help' for available commands.\n");
        }
    }
}

int main(int argc, char *argv[])
{
    printf("LC-3 Simulator v1.0\n");

    // Parse command line arguments
    for(int i = 1; i < argc; i++) {
        if(strcmp(argv[i], "--pipeline") == 0 || strcmp(argv[i], "-p") == 0) {
            pipeline_mode = true;
            printf("Pipeline mode enabled\n");
        }
        else if(strcmp(argv[i], "--verbose") == 0 || strcmp(argv[i], "-v") == 0) {
            verbose_mode = true;
            printf("Verbose mode enabled\n");
        }
        else if(strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            printf("Usage: %s [options] [program.obj]\n", argv[0]);
            printf("Options:\n");
            printf("  -p, --pipeline   Enable pipeline simulation mode\n");
            printf("  -v, --verbose    Enable verbose output\n");
            printf("  -i, --interactive Run in interactive mode\n");
            printf("  -h, --help       Show this help message\n");
            return 0;
        }
    }

    printf("Initializing...\n");

    // Initialize the simulator
    initialize_simulator();

    // Find non-option arguments
    char* program_file = NULL;
    bool interactive_requested = false;

    for(int i = 1; i < argc; i++) {
        if(argv[i][0] != '-') {
            program_file = argv[i];
        }
        else if(strcmp(argv[i], "-i") == 0 || strcmp(argv[i], "--interactive") == 0) {
            interactive_requested = true;
        }
    }

    if(program_file) {
        // Load program from command line argument
        load_program(program_file);

        if(interactive_requested) {
            // Interactive mode
            run_interactive();
        } else {
            // Run program automatically
            printf("Running program...\n");
            if (pipeline_mode && lc3_pipeline_enabled) {
                printf("Pipeline simulation active\n");
            }
            state_machine(pointer_counter, mem, reg);
            printf("Program execution completed.\n");
            print_state();

            // Print final pipeline metrics if enabled
            if (pipeline_mode && lc3_pipeline_enabled) {
                lc3_pipeline_metrics_t final_metrics;
                lc3_pipeline_get_metrics(&final_metrics);
                printf("\nFinal Pipeline Performance:\n");
                printf("  Total Instructions: %llu\n", final_metrics.total_instructions);
                printf("  Total Cycles: %llu\n", final_metrics.total_cycles);
                printf("  CPI: %.3f\n", final_metrics.cpi);
                printf("  Pipeline Efficiency: %.2f%%\n", final_metrics.pipeline_efficiency * 100.0);
            }
        }
    } else {
        // Interactive mode without loading a program
        printf("No program specified. Starting in interactive mode.\n");
        run_interactive();
    }

    return 0;
}
