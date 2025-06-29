#include "signals.h"

// Control signal variable definitions
uint8_t INT = 0;
uint8_t R = 0;
uint8_t BEN = 0;
uint8_t PSR_15 = 1; // Start in supervisor mode
uint8_t ACV = 0;

// Condition code flags
uint8_t N = 0;
uint8_t Z = 1; // Start with zero condition
uint8_t P = 0;

/**
 * Set Access Control Violation flag
 * Checks if current memory access violates privilege rules
 */
void SET_ACV() {
    // ACV is set if:
    // 1. Accessing system space (< USER_SPACE_ADDR) while in user mode (PSR_15
    // = 0)
    // 2. OR accessing invalid memory regions
    ACV =
        ((mem_addr_reg < USER_SPACE_ADDR || mem_addr_reg > USER_SPACE_LIMIT) &&
         !PSR_15);
}

/**
 * Set Condition Codes based on register value
 * Updates N, Z, P flags based on the value in register
 * Only one condition code should be set at a time
 */
void SET_CC(const lc3_register_t &r) {
    // Clear all condition codes first
    N = 0;
    Z = 0;
    P = 0;

    if (r == 0) {
        Z = 1; // Zero condition
    } else if (r & bit_table[15]) {
        N = 1; // Negative condition (MSB set in 2's complement)
    } else {
        P = 1; // Positive condition
    }
}

/**
 * Set Branch Enable signal
 * Computes BEN based on instruction branch bits and current condition codes
 * BEN = (N & n) | (Z & z) | (P & p) where n,z,p are instruction bits 11,10,9
 */
void SET_BEN() {
    // Extract branch condition bits from instruction
    uint8_t n_bit =
        (instruction_reg & bit_table[11]) ? 1 : 0; // Bit 11: branch if negative
    uint8_t z_bit =
        (instruction_reg & bit_table[10]) ? 1 : 0; // Bit 10: branch if zero
    uint8_t p_bit =
        (instruction_reg & bit_table[9]) ? 1 : 0; // Bit 9: branch if positive

    // BEN is set if any requested condition matches current condition codes
    BEN = (N && n_bit) || (Z && z_bit) || (P && p_bit);
}
