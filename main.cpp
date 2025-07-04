/**
 * @file main.cpp
 * @brief Main entry point for the LC-3 simulator
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "state_machine/state_machine.h"
#include "mem/memory.h"
#include "mem/register.h"
#include "mem/device_register.h"
#include "type/trap_vector.h"

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
    printf("=============================\n");
}

void run_interactive() {
    char command[100];
    printf("LC-3 Simulator Interactive Mode\n");
    printf("Commands: step, run, reg, mem <addr>, load <file>, reset, quit\n");
    
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
        else if(strcmp(command, "help") == 0 || strcmp(command, "h") == 0) {
            printf("Available commands:\n");
            printf("  step (s)     - Execute one instruction\n");
            printf("  run (r)      - Run until halt\n");
            printf("  reg          - Show register state\n");
            printf("  mem <addr>   - Show memory contents at address\n");
            printf("  load <file>  - Load program from file\n");
            printf("  reset        - Reset simulator\n");
            printf("  quit (q)     - Exit simulator\n");
        }
        else {
            printf("Unknown command. Type 'help' for available commands.\n");
        }
    }
}

int main(int argc, char *argv[])
{
    printf("LC-3 Simulator v1.0\n");
    printf("Initializing...\n");
    
    // Initialize the simulator
    initialize_simulator();
    
    if(argc > 1) {
        // Load program from command line argument
        load_program(argv[1]);
        
        if(argc > 2 && strcmp(argv[2], "-i") == 0) {
            // Interactive mode
            run_interactive();
        } else {
            // Run program automatically
            printf("Running program...\n");
            state_machine(pointer_counter, mem, reg);
            printf("Program execution completed.\n");
            print_state();
        }
    } else {
        // Interactive mode without loading a program
        printf("No program specified. Starting in interactive mode.\n");
        run_interactive();
    }
    
    return 0;
}