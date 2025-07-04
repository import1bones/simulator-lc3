#ifndef STATES_H
#define STATES_H

#include "../types/type.h"

#include "../memory/device_register.h"
#include "../memory/memory.h"
#include "../memory/register.h"
#include "../memory/control_store.h"

#include"../state_machine/ext.h"
#include"../state_machine/signals.h"

#define SUPERVISOR_MODE 0x8000

void state_0(const micro_instruction_t micro_inst);
void state_1(const micro_instruction_t micro_inst);
void state_2(const micro_instruction_t micro_inst);
void state_3(const micro_instruction_t micro_inst);
void state_4(const micro_instruction_t micro_inst);
void state_5(const micro_instruction_t micro_inst);
void state_6(const micro_instruction_t micro_inst);
void state_7(const micro_instruction_t micro_inst);
void state_8(const micro_instruction_t micro_inst);
void state_9(const micro_instruction_t micro_inst);
void state_10(const micro_instruction_t micro_inst);
void state_11(const micro_instruction_t micro_inst);
void state_12(const micro_instruction_t micro_inst);
void state_13(const micro_instruction_t micro_inst);
void state_14(const micro_instruction_t micro_inst);
void state_15(const micro_instruction_t micro_inst);
void state_16(const micro_instruction_t micro_inst);
void state_17(const micro_instruction_t micro_inst);
void state_18(const micro_instruction_t micro_inst);
void state_19(const micro_instruction_t micro_inst);
void state_20(const micro_instruction_t micro_inst);
void state_21(const micro_instruction_t micro_inst);
void state_22(const micro_instruction_t micro_inst);
void state_23(const micro_instruction_t micro_inst);
void state_24(const micro_instruction_t micro_inst);
void state_25(const micro_instruction_t micro_inst);
void state_26(const micro_instruction_t micro_inst);
void state_27(const micro_instruction_t micro_inst);
void state_28(const micro_instruction_t micro_inst);
void state_29(const micro_instruction_t micro_inst);
void state_30(const micro_instruction_t micro_inst);
void state_31(const micro_instruction_t micro_inst);
void state_32(const micro_instruction_t micro_inst);
void state_33(const micro_instruction_t micro_inst);
void state_34(const micro_instruction_t micro_inst);
void state_35(const micro_instruction_t micro_inst);
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

typedef void (*state_function_ptr)(const micro_instruction_t micro_inst);

//define and inital state_function_ptr_array.
//through a state function and change signa.
extern state_function_ptr state_function_ptr_array[64];

#endif
