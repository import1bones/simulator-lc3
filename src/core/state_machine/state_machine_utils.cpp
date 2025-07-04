/**
 * @file state_machine_utils.cpp
 * @brief State Machine Utils implementation
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#include "state_machine.h"
#include "state_definitions.h"
#include <iostream>
#include <unordered_map>

using namespace LC3States;

// State name mapping for debugging
static const std::unordered_map<uint8_t, const char*> state_names = {
    // Fetch cycle
    {FETCH1, "FETCH1"},
    {FETCH2, "FETCH2"}, 
    {FETCH3, "FETCH3"},
    {DECODE, "DECODE"},
    
    // Instruction execution
    {BR_STATE, "BR"},
    {ADD_STATE, "ADD"},
    {LD_STATE1, "LD1"},
    {ST_STATE1, "ST1"},
    {ST_STATE2, "ST2"},
    {AND_STATE, "AND"},
    {LDR_STATE1, "LDR1"},
    {STR_STATE1, "STR1"},
    {RTI_STATE, "RTI"},
    {NOT_STATE, "NOT"},
    {LDI_STATE1, "LDI1"},
    {STI_STATE1, "STI1"},
    {STI_STATE2, "STI2"},
    {JMP_STATE, "JMP"},
    {LEA_STATE, "LEA"},
    {TRAP_STATE1, "TRAP1"},
    {TRAP_STATE2, "TRAP2"},
    {TRAP_STATE3, "TRAP3"},
    {TRAP_STATE4, "TRAP4"},
    
    // Memory operations
    {MEM_WRITE, "MEM_WRITE"},
    {MEM_READ, "MEM_READ"},
    {MEM_READ2, "MEM_READ2"},
    {LOAD_IR, "LOAD_IR"},
    
    // Subroutines
    {JSRR_STATE, "JSRR"},
    {JSR_STATE, "JSR"},
    {BR_TAKEN, "BR_TAKEN"},
    {ST_PREP, "ST_PREP"},
    
    // Load/Store completion
    {LD_STATE2, "LD2"},
    {LD_STATE3, "LD3"},
    {LDR_STATE2, "LDR2"},
    {LDR_STATE3, "LDR3"},
    {STR_STATE2, "STR2"},
    {LDI_STATE2, "LDI2"},
    {LDI_STATE3, "LDI3"},
    {LDI_STATE4, "LDI4"},
    
    // Special states
    {UNKNOWN_INSTRUCTION, "UNKNOWN"},
    {HALT_STATE, "HALT"},
    {INTERRUPT_STATE, "INTERRUPT"}
};

/**
 * Get human-readable name for a state
 * @param state State number
 * @return State name string
 */
const char* get_state_name(uint8_t state)
{
    auto it = state_names.find(state);
    if (it != state_names.end()) {
        return it->second;
    }
    return "UNKNOWN_STATE";
}

/**
 * Log state transition for debugging
 * @param from_state Previous state
 * @param to_state Next state
 */
void log_state_transition(uint8_t from_state, uint8_t to_state)
{
    #ifdef DEBUG_STATE_MACHINE
    std::cout << "State transition: " << get_state_name(from_state) 
              << " (" << static_cast<int>(from_state) << ") -> " 
              << get_state_name(to_state) 
              << " (" << static_cast<int>(to_state) << ")" << std::endl;
    #endif
}

/**
 * Validate state number is within bounds
 * @param state State number to validate
 * @return true if valid, false otherwise
 */
bool is_valid_state(uint8_t state)
{
    return state < 64;
}

/**
 * Check if state is part of fetch cycle
 * @param state State number
 * @return true if fetch state
 */
bool is_fetch_state(uint8_t state)
{
    return state == FETCH1 || state == FETCH2 || state == FETCH3;
}

/**
 * Check if state is decode state
 * @param state State number  
 * @return true if decode state
 */
bool is_decode_state(uint8_t state)
{
    return state == DECODE;
}

/**
 * Check if state is an execution state
 * @param state State number
 * @return true if execution state
 */
bool is_execution_state(uint8_t state)
{
    return !is_fetch_state(state) && !is_decode_state(state) && is_valid_state(state);
}
