#ifndef EXT_H
#define EXT_H

#include "../types/type.h"

#ifdef __cplusplus
extern "C" {
#endif

extern uint16_t bit_table[16];

// sign extend - fixed for proper 2's complement
uint16_t SEXT(const uint16_t &ir, int bit);

// zero extend
uint16_t ZEXT(const uint16_t &ir, int bit);

#ifdef __cplusplus
}
#endif
#endif // EXT_H
