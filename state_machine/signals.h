#ifndef SIGNALS_H
#define SIGNALS_H

#include"../type/type.h"
#include"../mem/memory.h"

uint8_t INT = 0;
uint8_t R = 0;
uint8_t BEN = 0;
uint8_t PSR_15 = 0;
uint8_t ACV = 0;

uint8_t N=0;
uint8_t Z=0;
uint8_t P=8;

void SET_ACV()
{
    ACV = (mem_addr_reg < USER_SPACE_ADDR || mem_addr_reg > USER_SPACE_LIMIT) && PSR_15;
}

void SET_CC(const register_t &r)
{
    N=0;Z=0;P=0;
    if(r == 0)
        Z=1;
    else if(r & bit_table[15])
        N=1;
    else
        P=1;   
}

void SET_BEN()
{
        BEN = (instruction_reg & bit_table[11]) + 
              (instruction_reg & bit_table[10]) +
              (instruction_reg & bit_table[9]);
}

#endif //SIGNALS_H