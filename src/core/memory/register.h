#ifndef REGISTER_H
#define REGISTER_H
#include "../types/type.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint16_t lc3_register_t;
extern lc3_register_t reg[0x8];

extern lc3_register_t *reg_ptr;

extern lc3_register_t pointer_counter;

extern lc3_register_t instruction_reg;

#ifdef __cplusplus
}
#endif

#endif
