#include "ext.h"

// Global definitions
uint16_t bit_table[16] = {0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020,
                          0x0040, 0x0080, 0x0100, 0x0200, 0x0400, 0x0800,
                          0x1000, 0x2000, 0x4000, 0x8000};

// sign extend - fixed for proper 2's complement
uint16_t SEXT(const uint16_t &ir, int bit) {
    uint16_t mask = (1 << (bit + 1)) - 1; // Mask for lower (bit+1) bits
    uint16_t value = ir & mask;
    // If the sign bit is set, extend the sign
    if (value & (1 << bit)) {
        value |= (~mask);
    }
    return value;
}

// zero extend
uint16_t ZEXT(const uint16_t &ir, int bit) {
    uint16_t ans = ir;
    for (int i = bit + 1; i < 16; ++i) {
        // 0xFFFF & tem = tem
        // 0 & x = 0
        ans = ans & (~bit_table[i]);
    }
    return ans;
}
