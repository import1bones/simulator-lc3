#ifndef CONTROL_STORE_H
#define CONTROL_STORE_H

#include"../type/type.h"

typedef uint64_t micro_instruction_t;

micro_instruction_t control_store[0x40];

uint32_t micro_sequencer[0x40];

micro_instruction_t *control_store_ptr = control_store;

struct control_signals
{
    uint8_t J;
    uint8_t COND;
    uint8_t IRD;    
};


#endif //CONTROL_STORE_H