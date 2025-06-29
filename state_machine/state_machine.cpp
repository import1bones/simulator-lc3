#include "state_machine.h"
#include "../type/opcode.h"
#include "signals.h"
#include "state_definitions.h"
#include "states.h"

using namespace LC3States;

// State machine variables
uint8_t current_state = FETCH1;
bool machine_halted = false;
bool machine_error = false;

// Forward declarations for state transition functions
uint8_t handle_fetch_states();
uint8_t handle_decode_state();
uint8_t handle_execution_states();
uint8_t determine_next_state_after_execution();
bool should_continue_execution();
void initialize_state_machine(pointer_count_t &pc);
void finalize_state_machine(pointer_count_t &pc);

/**
 * Main state machine execution function
 * Implements the LC-3 processor control unit using microcode-based state
 * machine
 *
 * @param pc Reference to program counter
 * @param mem Pointer to memory array
 * @param reg Pointer to register array
 */
void state_machine(pointer_count_t &pc, word_t *mem, lc3_register_t *reg) {
    initialize_state_machine(pc);

    // Main execution loop
    while (should_continue_execution()) {
        // Execute current state microinstruction
        execute_current_state();

        // Determine next state based on current state and conditions
        current_state = get_next_state();

        // Check for halt or error conditions
        if (check_halt_conditions(mem)) {
            break;
        }

        // Safety check to prevent infinite loops
        if (pointer_counter > UINT16_MAX) {
            machine_error = true;
            break;
        }
    }

    finalize_state_machine(pc);
}

/**
 * Execute the microinstruction for the current state
 */
void execute_current_state() {
    if (current_state < 64) {
        state_function_ptr_array[current_state](control_store[current_state]);
    } else {
        machine_error = true;
    }
}

/**
 * Determine the next state based on current state and processor conditions
 * @return Next state number
 */
uint8_t get_next_state() {
    switch (current_state) {
    // Fetch cycle states
    case FETCH1:
        return handle_fetch_transition();

    case FETCH2:
        return FETCH3;

    case FETCH3:
        return DECODE;

    case DECODE:
        return handle_decode_transition();

    // Execution states - most return to fetch
    default:
        return handle_execution_transition();
    }
}

/**
 * Handle state transitions during fetch cycle
 */
uint8_t handle_fetch_transition() {
    // Check for interrupts during fetch
    if (INT && !PSR_15) {
        return INTERRUPT_STATE;
    }
    return FETCH2;
}

/**
 * Handle instruction decode and branch to appropriate execution state
 */
uint8_t handle_decode_transition() {
    uint16_t opcode = CAST_TO_OPCODE(instruction_reg);

    switch (opcode) {
    case ADD:
        return ADD_STATE;

    case AND:
        return AND_STATE;

    case BR:
        return BR_STATE;

    case JMP:
        return JMP_STATE;

    case JSR:
        // Check bit 11 to distinguish JSR from JSRR
        return (instruction_reg & bit_table[11]) ? JSR_STATE : JSRR_STATE;

    case LD:
        return LD_STATE1;

    case LDI:
        return LDI_STATE1;

    case LDR:
        return LDR_STATE1;

    case LEA:
        return LEA_STATE;

    case NOT:
        return NOT_STATE;

    case RTI:
        return RTI_STATE;

    case ST:
        return ST_STATE1;

    case STI:
        return STI_STATE1;

    case STR:
        return STR_STATE1;

    case TRAP:
        return TRAP_STATE1;

    default:
        // Unknown instruction - this is an error condition
        machine_error = true;
        return UNKNOWN_INSTRUCTION;
    }
}

/**
 * Handle transitions from execution states
 * Most execution states return to fetch, but some have multi-cycle operations
 */
uint8_t handle_execution_transition() {
    switch (current_state) {
    // Multi-cycle load operations
    case LD_STATE1:
        return LD_STATE2;
    case LD_STATE2:
        return LD_STATE3;

    case LDI_STATE1:
        return LDI_STATE2;
    case LDI_STATE2:
        return LDI_STATE3;
    case LDI_STATE3:
        return LDI_STATE4;

    case LDR_STATE1:
        return LDR_STATE2;
    case LDR_STATE2:
        return LDR_STATE3;

    // Multi-cycle store operations
    case ST_STATE1:
        return ST_STATE2;

    case STI_STATE1:
        return STI_STATE2;

    case STR_STATE1:
        return STR_STATE2;

    // Multi-cycle TRAP operations
    case TRAP_STATE1:
        return TRAP_STATE2;
    case TRAP_STATE2:
        return TRAP_STATE3;
    case TRAP_STATE3:
        return TRAP_STATE4;

    // Branch taken
    case BR_STATE:
        return BEN ? BR_TAKEN : FETCH1;

    // All other states return to fetch
    default:
        return FETCH1;
    }
}

/**
 * Check various halt conditions
 */
bool check_halt_conditions(word_t *mem) {
    // Check MCR halt bit
    if (!(mem[MCR] & 0x8000)) {
        machine_halted = true;
        return true;
    }

    // Check for machine error
    if (machine_error) {
        return true;
    }

    // Check for privilege violation
    if (ACV) {
        // In a real implementation, this would trigger an exception
        machine_error = true;
        return true;
    }

    return false;
}

/**
 * Check if execution should continue
 */
bool should_continue_execution() {
    return !machine_halted && !machine_error && pointer_counter <= UINT16_MAX;
}

/**
 * Initialize state machine for execution
 */
void initialize_state_machine(pointer_count_t &pc) {
    pointer_counter = pc;
    current_state = FETCH1;
    machine_halted = false;
    machine_error = false;

    // Initialize condition codes if needed
    if (N == 0 && Z == 0 && P == 0) {
        Z = 1; // Start with zero condition
    }
}

/**
 * Finalize state machine and update external state
 */
void finalize_state_machine(pointer_count_t &pc) { pc = pointer_counter; }
