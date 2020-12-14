#ifndef REGISTER_H
#define REGISTER_H
#include"../type/type.h"

typedef uint16_t register_t;
register_t reg[0x8];

register_t *reg_ptr = reg;

register_t pointer_counter;

register_t instruction_reg;

#endif