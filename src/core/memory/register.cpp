/**
 * @file register.cpp
 * @brief Register implementation
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#include "register.h"

lc3_register_t reg[0x8];
lc3_register_t *reg_ptr = reg;
lc3_register_t pointer_counter;
lc3_register_t instruction_reg;
