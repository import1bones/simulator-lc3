#include "states.h"

/*
function define:
    [BEN]
*/
void state_0(const micro_instruction_t micro_inst) {
    //[BEN] - Branch if BEN is set
    if (BEN) {
        pointer_counter = pointer_counter + SEXT(instruction_reg, 8);
    }
}

/*
function define:
    DR <- SR1 + (SR2 or SEXT[imm5])
    set CC
*/
void state_1(const micro_instruction_t micro_inst) {
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    uint16_t SR1idx = ZEXT((instruction_reg >> 6), 2);
    if (bit_table[5] & instruction_reg) {
        reg[DRidx] = reg[SR1idx] + SEXT(instruction_reg, 4);
    } else {
        uint16_t SR2idx = ZEXT(instruction_reg, 2);
        reg[DRidx] = reg[SR1idx] + reg[SR2idx];
    }
    SET_CC(reg[DRidx]);
}

/*
function define:
    MAR <- pc + SEXT[offset9]
    set ACV
*/
void state_2(const micro_instruction_t micro_inst) {
    // LD: PC-relative addressing using 9-bit offset
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

/*
function define:
    MAR <- pc + SEXT[offset9]
    set ACV
*/
void state_3(const micro_instruction_t micro_inst) {
    // ST: PC-relative addressing using 9-bit offset
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

void state_4(const micro_instruction_t micro_inst) {
    // ST2: Write memory
    do {
        mem[mem_addr_reg] = mem_data_reg;
        R = 1;
    } while (!R);
}

void state_5(const micro_instruction_t micro_inst) {
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    uint16_t SR1idx = ZEXT((instruction_reg >> 6), 2);
    if (bit_table[5] & instruction_reg) {
        reg[DRidx] = reg[SR1idx] & SEXT(instruction_reg, 4);
    } else {
        uint16_t SR2idx = ZEXT(instruction_reg, 2);
        reg[DRidx] = reg[SR1idx] & reg[SR2idx];
    }
    SET_CC(reg[DRidx]);
}

void state_6(const micro_instruction_t micro_inst) {
    // LDR: Calculate effective address (BaseR + SEXT[offset6])
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);
    // Extract 6-bit offset and sign extend properly
    uint16_t offset6 = instruction_reg & 0x3F; // Get lower 6 bits
    mem_addr_reg =
        reg[BaseRidx] +
        SEXT(offset6, 5); // Sign extend 6-bit value (bit 5 is sign bit)
    SET_ACV();
}

void state_7(const micro_instruction_t micro_inst) {
    // STR: Calculate effective address (BaseR + SEXT[offset6])
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);
    // Extract 6-bit offset and sign extend properly
    uint16_t offset6 = instruction_reg & 0x3F; // Get lower 6 bits
    mem_addr_reg =
        reg[BaseRidx] +
        SEXT(offset6, 5); // Sign extend 6-bit value (bit 5 is sign bit)
    SET_ACV();
}

void state_8(const micro_instruction_t micro_inst) {
    // RTI: Return from interrupt
    if (PSR_15) {
        // Supervisor mode - restore PC and PSR
        pointer_counter = mem[reg[6]]; // Pop PC
        reg[6]++;
        mem[PSR] = mem[reg[6]]; // Pop PSR
        reg[6]++;
        PSR_15 = (mem[PSR] & 0x8000) ? 1 : 0;
    }
}

void state_9(const micro_instruction_t micro_inst) {
    // NOT: Bitwise complement
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    uint16_t SRidx = ZEXT((instruction_reg >> 6), 2);
    reg[DRidx] = ~reg[SRidx];
    SET_CC(reg[DRidx]);
}

void state_10(const micro_instruction_t micro_inst) {
    // LDI1: Calculate PC + offset for indirect addressing
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

void state_11(const micro_instruction_t micro_inst) {
    // STI2: Get indirect address - read pointer from first location
    do {
        mem_addr_reg = mem[mem_addr_reg]; // Read the pointer from memory
        R = 1;
    } while (!R);
    SET_ACV();
}

void state_12(const micro_instruction_t micro_inst) {
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);
    pointer_counter = reg[BaseRidx];
}

void state_13(const micro_instruction_t micro_inst) {
    // STI3: Write data to the final indirect address
    do {
        mem[mem_addr_reg] = mem_data_reg; // Store data at the indirect address
        R = 1;
    } while (!R);
}
void state_14(const micro_instruction_t micro_inst) {
    // LEA: Load effective address
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    reg[DRidx] = pointer_counter + SEXT(instruction_reg, 8);
    SET_CC(reg[DRidx]);
}

void state_15(const micro_instruction_t micro_inst) {
    // TRAP: Execute trap
    uint16_t trap_vector = ZEXT(instruction_reg, 7);
    reg[7] = pointer_counter;           // Save return address
    pointer_counter = mem[trap_vector]; // Jump to trap service routine
}

void state_16(const micro_instruction_t micro_inst) {
    do {
        mem[mem_addr_reg] = mem_data_reg;
        R = 1;
    } while (!R);
}

void state_17(const micro_instruction_t micro_inst) {}

void state_18(const micro_instruction_t micro_inst) {
    mem_addr_reg = pointer_counter;
    ++pointer_counter;
    SET_ACV();
    //[INT]
}
void state_19(const micro_instruction_t micro_inst) {}

void state_20(const micro_instruction_t micro_inst) {
    // JSRR: Jump to subroutine register
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);
    reg[7] = pointer_counter;        // Save return address
    pointer_counter = reg[BaseRidx]; // Jump to address in BaseR
}

void state_21(const micro_instruction_t micro_inst) {
    // JSR: Jump to subroutine with PC-relative addressing
    reg[7] = pointer_counter; // Save return address (current PC)
    // Extract 11-bit offset and sign extend (bit 10 is sign bit)
    uint16_t offset11 = instruction_reg & 0x7FF; // Get lower 11 bits
    pointer_counter =
        pointer_counter + SEXT(offset11, 10); // PC + SEXT[PCoffset11]
}

void state_22(const micro_instruction_t micro_inst) {
    pointer_counter = pointer_counter + SEXT(instruction_reg, 8);
}

void state_23(const micro_instruction_t micro_inst) {
    uint16_t SRidx = ZEXT((instruction_reg >> 9), 2);
    mem_data_reg = reg[SRidx];
    //[ACV]
}

void state_24(const micro_instruction_t micro_inst) {}

void state_25(const micro_instruction_t micro_inst) {
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_26(const micro_instruction_t micro_inst) {}

void state_27(const micro_instruction_t micro_inst) {}

void state_28(const micro_instruction_t micro_inst) {
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_29(const micro_instruction_t micro_inst) {}

void state_30(const micro_instruction_t micro_inst) {
    instruction_reg = mem_data_reg;
}

void state_31(const micro_instruction_t micro_inst) {}

void state_32(const micro_instruction_t micro_inst) {
    SET_BEN();
    //[IR[15:12]]
}
void state_33(const micro_instruction_t micro_inst) {
    //[ACV]
}
void state_34(const micro_instruction_t micro_inst) {
    // LD2: Read memory into MDR
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_35(const micro_instruction_t micro_inst) {
    // FETCH3: Load instruction from memory
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_36(const micro_instruction_t micro_inst) {
    // LD3: Load data into destination register
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    reg[DRidx] = mem_data_reg;
    SET_CC(reg[DRidx]);
}

void state_37(const micro_instruction_t micro_inst) {
    // LDR2: Read memory for LDR
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_38(const micro_instruction_t micro_inst) {
    // LDR3: Load data into destination register for LDR
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    reg[DRidx] = mem_data_reg;
    SET_CC(reg[DRidx]);
}

void state_39(const micro_instruction_t micro_inst) {
    // STR2: Write data to memory for STR
    uint16_t SRidx = ZEXT((instruction_reg >> 9), 2);
    mem_data_reg = reg[SRidx];
    do {
        mem[mem_addr_reg] = mem_data_reg;
        R = 1;
    } while (!R);
}

void state_40(const micro_instruction_t micro_inst) {
    // LDI2: Get indirect address - read pointer from first location
    do {
        mem_addr_reg = mem[mem_addr_reg]; // Read the pointer from memory
        R = 1;
    } while (!R);
    SET_ACV();
}

void state_41(const micro_instruction_t micro_inst) {
    // LDI3: Read from indirect address
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_42(const micro_instruction_t micro_inst) {
    // LDI4: Load into destination register
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    reg[DRidx] = mem_data_reg;
    SET_CC(reg[DRidx]);
}

void state_43(const micro_instruction_t micro_inst) {
    // TRAP2: Continue trap execution
    mem_addr_reg = ZEXT(instruction_reg, 7);
}

void state_44(const micro_instruction_t micro_inst) {
    // TRAP3: Get trap service routine address
    do {
        mem_data_reg = mem[mem_addr_reg];
        R = 1;
    } while (!R);
}

void state_45(const micro_instruction_t micro_inst) {
    // TRAP4: Jump to trap service routine
    pointer_counter = mem_data_reg;
}

void state_46(const micro_instruction_t micro_inst) {
    // Interrupt handling state
    if (INT && !PSR_15) {
        // Save state and switch to supervisor mode
        reg[6]--; // SSP
        mem[reg[6]] = mem[PSR];
        reg[6]--;
        mem[reg[6]] = pointer_counter;
        PSR_15 = 1;
        pointer_counter = mem[0x0100]; // Interrupt vector
    }
}

void state_47(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_48(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_49(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_50(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_51(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_52(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_53(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_54(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_55(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_56(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_57(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_58(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_59(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_60(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_61(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_62(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}

void state_63(const micro_instruction_t micro_inst) {
    // Additional state for complex operations
}
