/**
 * @file memory.cpp
 * @brief Memory implementation
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#include "memory.h"

word_t mem[UINT16_MAX];
word_t *mem_ptr = mem;
word_t mem_addr_reg;
word_t mem_data_reg;
