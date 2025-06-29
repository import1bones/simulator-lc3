#ifndef OPCODE_H
#define OPCODE_H

#include"type.h"

#define BR 0x0000
#define ADD 0x1000
#define LD 0x2000
#define ST 0x3000
#define JSR 0x4000
#define AND 0x5000
#define LDR 0x6000
#define STR 0x7000
#define RTI 0x8000
#define NOT 0x9000
#define LDI 0xA000
#define STI 0xB000
#define JMP 0xC000

#define UNUSED_OP 0xD000

#define LEA 0xE000
#define TRAP 0xF000

#define CAST_TO_OPCODE(instruction) (uint16_t)(instruction & 0xF000)

#endif //OPCODE_H