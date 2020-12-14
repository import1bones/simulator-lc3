#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include"../type/type.h"
#include"../mem/register.h"
#include"../mem/control_store.h"
#include"../mem/memory.h"
typedef uint16_t instruction_t;
typedef uint16_t pointer_count_t;

void state_machine(pointer_count_t& pc, word_t *mem, register_t *reg);
#endif // STATE_MACHINE_H
