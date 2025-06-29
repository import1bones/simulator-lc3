#include"state_machine.h"
#include"states.h"
#include"../type/opcode.h"
#include"signals.h"

uint8_t current_state = 18; // Start with fetch state

void state_machine(pointer_count_t& pc, word_t *mem, register_t *reg)
{
    // Initialize PC
    pointer_counter = pc;
    
    // Main execution loop
    while(pointer_counter <= UINT16_MAX) 
    {
        // Execute current state
        state_function_ptr_array[current_state](control_store[current_state]);
        
        // Simple state transition logic (this would be more complex in real implementation)
        switch(current_state) {
            case 18: // FETCH1
                current_state = 33; // FETCH2 
                break;
            case 33: // FETCH2
                current_state = 35; // FETCH3
                break;
            case 35: // FETCH3
                current_state = 32; // DECODE
                break;
            case 32: // DECODE
                // Branch based on instruction opcode
                switch(CAST_TO_OPCODE(instruction_reg)) {
                    case ADD: current_state = 1; break;
                    case AND: current_state = 5; break;
                    case BR:  current_state = 0; break;
                    case JMP: current_state = 12; break;
                    case JSR: 
                        if(instruction_reg & bit_table[11]) 
                            current_state = 21; // JSR
                        else 
                            current_state = 20; // JSRR
                        break;
                    case LD:  current_state = 2; break;
                    case LDI: current_state = 10; break;
                    case LDR: current_state = 6; break;
                    case LEA: current_state = 14; break;
                    case NOT: current_state = 9; break;
                    case RTI: current_state = 8; break;
                    case ST:  current_state = 3; break;
                    case STI: current_state = 11; break;
                    case STR: current_state = 7; break;
                    case TRAP: current_state = 15; break;
                    default: current_state = 18; break; // Unknown instruction, restart
                }
                break;
            default:
                // Most states return to fetch
                current_state = 18;
                break;
        }
        
        // Update PC reference
        pc = pointer_counter;
        
        // Simple halt condition (when MCR bit 15 is 0)
        if(mem[MCR] & 0x8000) break;
    }
}