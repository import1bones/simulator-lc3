#ifndef SIGNALS_H
#define SIGNALS_H

#include "../mem/memory.h"
#include "../mem/register.h"
#include "../type/type.h"
#include "ext.h"

/**
 * LC-3 Processor Control Signals
 * These signals control the datapath and are used by the microcode
 */

// Interrupt and control signals
extern uint8_t INT; // Interrupt request signal
extern uint8_t R;   // Ready signal for memory operations
extern uint8_t
    BEN; // Branch enable (computed from condition codes and branch bits)
extern uint8_t PSR_15; // Privilege bit from PSR (0=user, 1=supervisor)
extern uint8_t ACV;    // Access control violation

// Condition code flags (set by arithmetic/logic operations)
extern uint8_t N; // Negative flag (result < 0)
extern uint8_t Z; // Zero flag (result == 0)
extern uint8_t P; // Positive flag (result > 0)

/**
 * Set Access Control Violation flag
 * Checks if current memory access violates privilege rules
 */
void SET_ACV();

/**
 * Set Condition Codes based on register value
 * Updates N, Z, P flags based on the value in register
 * @param r Register value to evaluate
 */
void SET_CC(const lc3_register_t &r);

/**
 * Set Branch Enable signal
 * Computes BEN based on instruction branch bits and current condition codes
 * BEN = (N & n) | (Z & z) | (P & p) where n,z,p are instruction bits 11,10,9
 */
void SET_BEN();

/**
 * Initialize all control signals to default state
 */
inline void INIT_SIGNALS() {
    INT = 0;
    R = 0;
    BEN = 0;
    PSR_15 = 1; // Start in supervisor mode
    ACV = 0;
    N = 0;
    Z = 1; // Start with zero condition
    P = 0;
}

/**
 * Check if any condition code is set
 * @return true if N, Z, or P is set
 */
inline bool ANY_CC_SET() { return N || Z || P; }

/**
 * Get current condition code as 3-bit value
 * @return Condition codes as NZP bits
 */
inline uint8_t GET_CC_BITS() { return (N << 2) | (Z << 1) | P; }

/**
 * Set condition codes from 3-bit value
 * @param cc_bits Condition codes as NZP bits
 */
inline void SET_CC_BITS(uint8_t cc_bits) {
    N = (cc_bits >> 2) & 1;
    Z = (cc_bits >> 1) & 1;
    P = cc_bits & 1;
}

#endif // SIGNALS_H
