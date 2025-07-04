#ifndef REGISTER_H
#define REGISTER_H
#include "../type/type.h"

typedef uint16_t lc3_register_t;
lc3_register_t reg[0x8];

lc3_register_t *reg_ptr = reg;

lc3_register_t pointer_counter;

lc3_register_t instruction_reg;

#endif
