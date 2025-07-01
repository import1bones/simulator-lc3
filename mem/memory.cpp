#include "memory.h"

// Global memory and register definitions
word_t mem[UINT16_MAX];
word_t *mem_ptr = mem;
word_t mem_addr_reg;
word_t mem_data_reg;
