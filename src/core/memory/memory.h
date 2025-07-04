#ifndef MEMORY_H
#define MEMORY_H

#include "../types/type.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint16_t word_t;
extern word_t mem[UINT16_MAX];

extern word_t *mem_ptr;

extern word_t mem_addr_reg;
extern word_t mem_data_reg;

#define SYSTEM_SPACE_ADDR 0x0000
#define SYSTEM_SPACE_LIMIT 0x2FFF

#define TRAP_VECTOR_ADDR 0x0000
#define TRAP_VECTOR_LIMIT 0x00FF

#define INTERRUPT_VECTOR_TABLE_ADDR 0x0100
#define INTERRUPT_VECTOR_TABLE_LIMIT 0x01FF

#define USER_SPACE_ADDR 0x3000
#define USER_SPACE_LIMIT 0xFDFF

#define DEVICE_REGISTER_ADDR 0xFE00
#define DEVICE_REGSITER_LIMIT 0xFFFF

#ifdef __cplusplus
}
#endif

#endif //MEMORY_H