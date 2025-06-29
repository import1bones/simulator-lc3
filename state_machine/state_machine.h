#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include "../mem/control_store.h"
#include "../mem/device_register.h"
#include "../mem/memory.h"
#include "../mem/register.h"
#include "../type/type.h"
#include "state_definitions.h"

typedef uint16_t instruction_t;
typedef uint16_t pointer_count_t;

// External state machine variables
extern uint8_t current_state;
extern bool machine_halted;
extern bool machine_error;

// Main state machine function
void state_machine(pointer_count_t &pc, word_t *mem, lc3_register_t *reg);

// State machine control functions
void execute_current_state();
uint8_t get_next_state();

// State transition handlers
uint8_t handle_fetch_transition();
uint8_t handle_decode_transition();
uint8_t handle_execution_transition();

// Condition checking functions
bool check_halt_conditions(word_t *mem);
bool should_continue_execution();

// State machine lifecycle functions
void initialize_state_machine(pointer_count_t &pc);
void finalize_state_machine(pointer_count_t &pc);

// Utility functions for state machine debugging and monitoring
const char *get_state_name(uint8_t state);
void log_state_transition(uint8_t from_state, uint8_t to_state);

#endif // STATE_MACHINE_H
