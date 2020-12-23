#include"states.h"

/*
function define:
    [BEN]
*/
void state_0(const micro_instruction_t micro_instv)
{
    //[BEN]
}

/*
function define:
    DR <- SR1 + (SR2 or SEXT[imm5])
    set CC
*/
void state_1(const micro_instruction_t micro_inst)
{
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    uint16_t SR1idx = ZEXT((instruction_reg >> 6), 2);
    if(bit_table[5] & instruction_reg)
    {
        reg[DRidx] = reg[SR1idx] + SEXT(instruction_reg, 4);
    }  
    else
    {
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
void state_2(const micro_instruction_t micro_inst)
{
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

/*
function define:
    MAR <- pc + SEXT[offset9]
    set ACV
*/
void state_3(const micro_instruction_t micro_inst)
{
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

void state_4(const micro_instruction_t micro_inst)
{

}

void state_5(const micro_instruction_t micro_inst)
{
    uint16_t DRidx = ZEXT((instruction_reg >> 9), 2);
    uint16_t SR1idx = ZEXT((instruction_reg >> 6), 2);
    if(bit_table[5] & instruction_reg)
    {
        reg[DRidx] = reg[SR1idx] & SEXT(instruction_reg, 4);
    }  
    else
    {
        uint16_t SR2idx = ZEXT(instruction_reg, 2);
        reg[DRidx] = reg[SR1idx] & reg[SR2idx];
    }
    SET_CC(reg[DRidx]);
}

void state_6(const micro_instruction_t micro_inst)
{

}

void state_7(const micro_instruction_t micro_inst)
{

}

void state_8(const micro_instruction_t micro_inst)
{

}

void state_9(const micro_instruction_t micro_inst)
{

}

void state_10(const micro_instruction_t micro_inst)
{
    mem_addr_reg = pointer_counter + SEXT(instruction_reg, 8);
    SET_ACV();
}

void state_11(const micro_instruction_t micro_inst)
{

}

void state_12(const micro_instruction_t micro_inst)
{
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);
    pointer_counter = reg[BaseRidx];
}

void state_13(const micro_instruction_t micro_inst)
{

}
void state_14(const micro_instruction_t micro_inst)
{

}

void state_15(const micro_instruction_t micro_inst)
{

}

void state_16(const micro_instruction_t micro_inst)
{
    do
    {
        mem[mem_addr_reg] = mem_data_reg;
        R = 1;
    }
    while(!R);
}

void state_17(const micro_instruction_t micro_inst)
{

}

void state_18(const micro_instruction_t micro_inst)
{
    mem_addr_reg = pointer_counter;
    ++pointer_counter;
    SET_ACV();
    //[INT]
}
void state_19(const micro_instruction_t micro_inst)
{

}

void state_20(const micro_instruction_t micro_inst)
{
    uint16_t BaseRidx = ZEXT((instruction_reg >> 6), 2);    
    reg[7] = pointer_counter;
    pointer_counter = reg[BaseRidx];
}

void state_21(const micro_instruction_t micro_inst)
{
    reg[7] = pointer_counter;
    pointer_counter = pointer_counter + SEXT(instruction_reg, 10); 
}

void state_22(const micro_instruction_t micro_inst)
{
    pointer_counter = pointer_counter + SEXT(instruction_reg, 8);
}

void state_23(const micro_instruction_t micro_inst)
{
    uint16_t SRidx = ZEXT((instruction_reg >> 9), 2);
    mem_data_reg = reg[SRidx];
    //[ACV]
}

void state_24(const micro_instruction_t micro_inst)
{

}

void state_25(const micro_instruction_t micro_inst)
{
    do
    {
        mem_data_reg = mem[mem_addr_reg];
        R=1;
    }
    while(!R);
}

void state_26(const micro_instruction_t micro_inst)
{

}

void state_27(const micro_instruction_t micro_inst)
{
    
}

void state_28(const micro_instruction_t micro_inst)
{
    do
    {
        mem_data_reg = mem[mem_addr_reg];
        R=1;
    }
    while(!R);
}

void state_29(const micro_instruction_t micro_inst)
{

}

void state_30(const micro_instruction_t micro_inst)
{
    instruction_reg = mem_data_reg;
}

void state_31(const micro_instruction_t micro_inst)
{

}

void state_32(const micro_instruction_t micro_inst)
{
    SET_BEN();
    //[IR[15:12]]
}
void state_33(const micro_instruction_t micro_inst)
{
    //[ACV]
}
void state_34(const micro_instruction_t micro_inst);
void state_35(const micro_instruction_t micro_inst)
{
    //[ACV]
}
void state_36(const micro_instruction_t micro_inst);
void state_37(const micro_instruction_t micro_inst);
void state_38(const micro_instruction_t micro_inst);
void state_39(const micro_instruction_t micro_inst);
void state_40(const micro_instruction_t micro_inst);
void state_41(const micro_instruction_t micro_inst);
void state_42(const micro_instruction_t micro_inst);
void state_43(const micro_instruction_t micro_inst);
void state_44(const micro_instruction_t micro_inst);
void state_45(const micro_instruction_t micro_inst);
void state_46(const micro_instruction_t micro_inst);
void state_47(const micro_instruction_t micro_inst);
void state_48(const micro_instruction_t micro_inst);
void state_49(const micro_instruction_t micro_inst);
void state_50(const micro_instruction_t micro_inst);
void state_51(const micro_instruction_t micro_inst);
void state_52(const micro_instruction_t micro_inst);
void state_53(const micro_instruction_t micro_inst);
void state_54(const micro_instruction_t micro_inst);
void state_55(const micro_instruction_t micro_inst);
void state_56(const micro_instruction_t micro_inst);
void state_57(const micro_instruction_t micro_inst);
void state_58(const micro_instruction_t micro_inst);
void state_59(const micro_instruction_t micro_inst);
void state_60(const micro_instruction_t micro_inst);
void state_61(const micro_instruction_t micro_inst);
void state_62(const micro_instruction_t micro_inst);
void state_63(const micro_instruction_t micro_inst);