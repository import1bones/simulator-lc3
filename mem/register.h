#ifndef REGISTER_H
#define REGISTER_H
#include "../type/type.h"

typedef uint16_t lc3_register_t;

// Register declarations - actual definitions should be in one .cpp file
extern lc3_register_t reg[0x8];
extern lc3_register_t *reg_ptr;
extern lc3_register_t pointer_counter;
extern lc3_register_t instruction_reg;

#endif
