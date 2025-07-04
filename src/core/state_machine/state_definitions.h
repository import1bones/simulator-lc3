#ifndef STATE_DEFINITIONS_H
#define STATE_DEFINITIONS_H

#include "../types/type.h"

// State machine state definitions
// These correspond to the microcode control store addresses

namespace LC3States {
    // Fetch cycle states
    constexpr uint8_t FETCH1 = 18;
    constexpr uint8_t FETCH2 = 33;
    constexpr uint8_t FETCH3 = 35;
    constexpr uint8_t DECODE = 32;
    
    // Instruction execution states
    constexpr uint8_t BR_STATE = 0;
    constexpr uint8_t ADD_STATE = 1;
    constexpr uint8_t LD_STATE1 = 2;
    constexpr uint8_t ST_STATE1 = 3;
    constexpr uint8_t ST_STATE2 = 4;
    constexpr uint8_t AND_STATE = 5;
    constexpr uint8_t LDR_STATE1 = 6;
    constexpr uint8_t STR_STATE1 = 7;
    constexpr uint8_t RTI_STATE = 8;
    constexpr uint8_t NOT_STATE = 9;
    constexpr uint8_t LDI_STATE1 = 10;
    constexpr uint8_t STI_STATE1 = 11;
    constexpr uint8_t STI_STATE2 = 13;
    constexpr uint8_t JMP_STATE = 12;
    constexpr uint8_t LEA_STATE = 14;
    constexpr uint8_t TRAP_STATE1 = 15;
    constexpr uint8_t TRAP_STATE2 = 43;
    constexpr uint8_t TRAP_STATE3 = 44;
    constexpr uint8_t TRAP_STATE4 = 45;
    
    // Memory operation states
    constexpr uint8_t MEM_WRITE = 16;
    constexpr uint8_t MEM_READ = 25;
    constexpr uint8_t MEM_READ2 = 28;
    constexpr uint8_t LOAD_IR = 30;
    
    // Subroutine states
    constexpr uint8_t JSRR_STATE = 20;
    constexpr uint8_t JSR_STATE = 21;
    constexpr uint8_t BR_TAKEN = 22;
    constexpr uint8_t ST_PREP = 23;
    
    // Load/Store completion states
    constexpr uint8_t LD_STATE2 = 25;
    constexpr uint8_t LD_STATE3 = 27;
    constexpr uint8_t LDR_STATE2 = 37;
    constexpr uint8_t LDR_STATE3 = 38;
    constexpr uint8_t STR_STATE2 = 39;
    constexpr uint8_t LDI_STATE2 = 40;
    constexpr uint8_t LDI_STATE3 = 41;
    constexpr uint8_t LDI_STATE4 = 42;
    
    // Error and special states
    constexpr uint8_t UNKNOWN_INSTRUCTION = 63;
    constexpr uint8_t HALT_STATE = 62;
    constexpr uint8_t INTERRUPT_STATE = 46;
}

// State machine result codes
enum class StateMachineResult {
    CONTINUE,
    HALT,
    ERROR,
    INTERRUPT
};

// State transition function type
using StateTransitionFunc = uint8_t(*)();

#endif // STATE_DEFINITIONS_H
