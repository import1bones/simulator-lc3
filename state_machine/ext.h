#ifndef EXT_H
#define EXT_H

#include "../type/type.h"

// External declarations - definitions should be in ext.cpp
extern uint16_t bit_table[16];

// Function declarations
uint16_t SEXT(const uint16_t &ir, int bit);
uint16_t ZEXT(const uint16_t &ir, int bit);

#endif // EXT_H
