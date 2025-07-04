/**
 * @file lc3_simulator.cpp
 * @brief Lc3 Simulator implementation
 * 
 * LC-3 Simulator with Pipeline Extensions
 * 
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

#include "src/core/memory/memory.h"
#include "src/core/memory/register.h"
#include "src/core/state_machine/state_machine.h"
#include "src/core/types/opcode.h"
#include "src/core/types/type.h"
#include "src/core/types/trap_vector.h"
#include <stdint.h>  // For uint16_t, uint8_t
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

class LC3Simulator {
  private:
    word_t memory[UINT16_MAX + 1]; // Allow access to 0x0000 through 0xFFFF
    lc3_register_t registers[8];
    uint16_t pc;
    uint8_t condition_codes[3]; // N, Z, P
    bool halted;

  public:
    LC3Simulator() { reset(); }

    void reset() {
        // Initialize memory to zero
        for (int i = 0; i <= UINT16_MAX; i++) {
            memory[i] = 0;
        }

        // Initialize registers to zero
        for (int i = 0; i < 8; i++) {
            registers[i] = 0;
        }

        // Set PC to user space start
        pc = USER_SPACE_ADDR;

        // Initialize condition codes
        condition_codes[0] = 0; // N
        condition_codes[1] = 1; // Z (start with Z=1)
        condition_codes[2] = 0; // P

        halted = false;
    }

    void load_program(const std::vector<uint16_t> &program,
                      uint16_t start_address = USER_SPACE_ADDR) {
        for (size_t i = 0; i < program.size(); i++) {
            if (start_address + i <= UINT16_MAX) {
                memory[start_address + i] = program[i];
            }
        }
        pc = start_address;
    }

    void step() {
        if (halted)
            return;

        // Fetch instruction
        uint16_t instruction = memory[pc];
        pc++;

        // Decode and execute
        uint16_t opcode = CAST_TO_OPCODE(instruction);
        execute_instruction(instruction, opcode);
    }

    void run(int max_cycles = 10000) {
        int cycles = 0;
        while (!halted && cycles < max_cycles) {
            step();
            cycles++;
        }
    }

    // Getters for testing
    uint16_t get_register(int reg) const {
        if (reg >= 0 && reg < 8) {
            return registers[reg];
        }
        return 0;
    }

    uint16_t get_memory(uint16_t address) const { return memory[address]; }

    uint16_t get_pc() const { return pc; }

    std::tuple<uint8_t, uint8_t, uint8_t> get_condition_codes() const {
        return std::make_tuple(condition_codes[0], condition_codes[1],
                               condition_codes[2]);
    }

    bool is_halted() const { return halted; }

    void set_register(int reg, uint16_t value) {
        if (reg >= 0 && reg < 8) {
            registers[reg] = value;
            update_condition_codes(value);
        }
    }

    void set_memory(uint16_t address, uint16_t value) {
        memory[address] = value;
    }

    void set_pc(uint16_t value) { pc = value; }

  private:
    void execute_instruction(uint16_t instruction, uint16_t opcode) {
        switch (opcode) {
        case ADD:
            execute_add(instruction);
            break;
        case AND:
            execute_and(instruction);
            break;
        case BR:
            execute_br(instruction);
            break;
        case JMP:
            execute_jmp(instruction);
            break;
        case JSR:
            execute_jsr(instruction);
            break;
        case LD:
            execute_ld(instruction);
            break;
        case LDI:
            execute_ldi(instruction);
            break;
        case LDR:
            execute_ldr(instruction);
            break;
        case LEA:
            execute_lea(instruction);
            break;
        case NOT:
            execute_not(instruction);
            break;
        case ST:
            execute_st(instruction);
            break;
        case STI:
            execute_sti(instruction);
            break;
        case STR:
            execute_str(instruction);
            break;
        case TRAP:
            execute_trap(instruction);
            break;
        default:
            // Unknown instruction, halt
            halted = true;
            break;
        }
    }

    void update_condition_codes(uint16_t value) {
        condition_codes[0] = (value & 0x8000) ? 1 : 0;                 // N
        condition_codes[1] = (value == 0) ? 1 : 0;                     // Z
        condition_codes[2] = (value > 0 && !(value & 0x8000)) ? 1 : 0; // P
    }

    uint16_t sign_extend(uint16_t value, int bit_count) {
        if (value & (1 << (bit_count - 1))) {
            // Sign bit is set, extend with 1s
            return value | (0xFFFF << bit_count);
        }
        return value;
    }

    // Instruction implementations
    void execute_add(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t sr1 = (instruction >> 6) & 0x7;

        if (instruction & 0x20) {
            // Immediate mode
            uint16_t imm5 = sign_extend(instruction & 0x1F, 5);
            registers[dr] = registers[sr1] + imm5;
        } else {
            // Register mode
            uint16_t sr2 = instruction & 0x7;
            registers[dr] = registers[sr1] + registers[sr2];
        }
        update_condition_codes(registers[dr]);
    }

    void execute_and(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t sr1 = (instruction >> 6) & 0x7;

        if (instruction & 0x20) {
            // Immediate mode
            uint16_t imm5 = sign_extend(instruction & 0x1F, 5);
            registers[dr] = registers[sr1] & imm5;
        } else {
            // Register mode
            uint16_t sr2 = instruction & 0x7;
            registers[dr] = registers[sr1] & registers[sr2];
        }
        update_condition_codes(registers[dr]);
    }

    void execute_br(uint16_t instruction) {
        bool n = instruction & 0x800;
        bool z = instruction & 0x400;
        bool p = instruction & 0x200;

        if ((n && condition_codes[0]) || (z && condition_codes[1]) ||
            (p && condition_codes[2])) {
            uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
            pc += pc_offset;
        }
    }

    void execute_jmp(uint16_t instruction) {
        uint16_t base_r = (instruction >> 6) & 0x7;
        pc = registers[base_r];
    }

    void execute_jsr(uint16_t instruction) {
        registers[7] = pc; // Save return address

        if (instruction & 0x800) {
            // JSR mode
            uint16_t pc_offset = sign_extend(instruction & 0x7FF, 11);
            pc += pc_offset;
        } else {
            // JSRR mode
            uint16_t base_r = (instruction >> 6) & 0x7;
            pc = registers[base_r];
        }
    }

    void execute_ld(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
        registers[dr] = memory[pc + pc_offset];
        update_condition_codes(registers[dr]);
    }

    void execute_ldi(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
        uint16_t address = memory[pc + pc_offset];
        registers[dr] = memory[address];
        update_condition_codes(registers[dr]);
    }

    void execute_ldr(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t base_r = (instruction >> 6) & 0x7;
        uint16_t offset = sign_extend(instruction & 0x3F, 6);
        registers[dr] = memory[registers[base_r] + offset];
        update_condition_codes(registers[dr]);
    }

    void execute_lea(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
        registers[dr] = pc + pc_offset;
        update_condition_codes(registers[dr]);
    }

    void execute_not(uint16_t instruction) {
        uint16_t dr = (instruction >> 9) & 0x7;
        uint16_t sr = (instruction >> 6) & 0x7;
        registers[dr] = ~registers[sr];
        update_condition_codes(registers[dr]);
    }

    void execute_st(uint16_t instruction) {
        uint16_t sr = (instruction >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
        memory[pc + pc_offset] = registers[sr];
    }

    void execute_sti(uint16_t instruction) {
        uint16_t sr = (instruction >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instruction & 0x1FF, 9);
        uint16_t address = memory[pc + pc_offset];
        memory[address] = registers[sr];
    }

    void execute_str(uint16_t instruction) {
        uint16_t sr = (instruction >> 9) & 0x7;
        uint16_t base_r = (instruction >> 6) & 0x7;
        uint16_t offset = sign_extend(instruction & 0x3F, 6);
        memory[registers[base_r] + offset] = registers[sr];
    }

    void execute_trap(uint16_t instruction) {
        uint16_t trap_vector = instruction & 0xFF;

        // Save return address
        registers[7] = pc;

        switch (trap_vector) {
        case HALT:
            halted = true;
            break;
        case OUT:
            // For testing, we'll just store the character in a special memory
            // location
            memory[0xFFFF] = registers[0] & 0xFF;
            break;
        case PUTS:
            // For testing, we'll mark that PUTS was called
            memory[0xFFFE] = 1;
            break;
        case GETC:
            // For testing, read from a special memory location
            registers[0] = memory[0xFFFD] & 0xFF;
            update_condition_codes(registers[0]);
            break;
        case IN:
            // Similar to GETC but with prompt
            registers[0] = memory[0xFFFD] & 0xFF;
            update_condition_codes(registers[0]);
            break;
        default:
            // Unknown trap, halt
            halted = true;
            break;
        }
    }
};

PYBIND11_MODULE(lc3_simulator, m) {
    m.doc() = "LC-3 Simulator Python Bindings";

    py::class_<LC3Simulator>(m, "LC3Simulator")
        .def(py::init<>())
        .def("reset", &LC3Simulator::reset)
        .def("load_program", &LC3Simulator::load_program, py::arg("program"),
             py::arg("start_address") = USER_SPACE_ADDR)
        .def("step", &LC3Simulator::step)
        .def("run", &LC3Simulator::run, py::arg("max_cycles") = 10000)
        .def("get_register", &LC3Simulator::get_register)
        .def("get_memory", &LC3Simulator::get_memory)
        .def("get_pc", &LC3Simulator::get_pc)
        .def("get_condition_codes", &LC3Simulator::get_condition_codes)
        .def("is_halted", &LC3Simulator::is_halted)
        .def("set_register", &LC3Simulator::set_register)
        .def("set_memory", &LC3Simulator::set_memory)
        .def("set_pc", &LC3Simulator::set_pc);

    // Export constants
    m.attr("USER_SPACE_ADDR") = USER_SPACE_ADDR;
    m.attr("ADD") = ADD;
    m.attr("AND") = AND;
    m.attr("BR") = BR;
    m.attr("JMP") = JMP;
    m.attr("JSR") = JSR;
    m.attr("LD") = LD;
    m.attr("LDI") = LDI;
    m.attr("LDR") = LDR;
    m.attr("LEA") = LEA;
    m.attr("NOT") = NOT;
    m.attr("ST") = ST;
    m.attr("STI") = STI;
    m.attr("STR") = STR;
    m.attr("TRAP") = TRAP;
    m.attr("HALT") = HALT;
    m.attr("OUT") = OUT;
    m.attr("PUTS") = PUTS;
    m.attr("GETC") = GETC;
    m.attr("IN") = IN;
}
