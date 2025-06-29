"""
Tests for LC-3 instruction implementations.
"""
import pytest


class TestArithmeticInstructions:
    """Test arithmetic instructions (ADD, AND, NOT)."""
    
    def test_add_immediate_mode(self, simulator, instruction_encodings):
        """Test ADD instruction in immediate mode."""
        # ADD R0, R0, #5
        instruction = 0x1000 | (0 << 9) | (0 << 6) | 0x20 | 5
        
        simulator.set_register(0, 10)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 15
        n, z, p = simulator.get_condition_codes()
        assert p == 1 and n == 0 and z == 0
    
    def test_add_register_mode(self, simulator):
        """Test ADD instruction in register mode."""
        # ADD R0, R1, R2
        instruction = 0x1000 | (0 << 9) | (1 << 6) | 2
        
        simulator.set_register(1, 10)
        simulator.set_register(2, 5)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 15
    
    def test_add_overflow(self, simulator):
        """Test ADD instruction with overflow."""
        # ADD R0, R0, #1
        instruction = 0x1000 | (0 << 9) | (0 << 6) | 0x20 | 1
        
        simulator.set_register(0, 0xFFFF)  # -1 in 2's complement
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0
        n, z, p = simulator.get_condition_codes()
        assert z == 1
    
    def test_and_immediate_mode(self, simulator):
        """Test AND instruction in immediate mode."""
        # AND R0, R0, #15
        instruction = 0x5000 | (0 << 9) | (0 << 6) | 0x20 | 15
        
        simulator.set_register(0, 0xFF)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 15
    
    def test_and_register_mode(self, simulator):
        """Test AND instruction in register mode."""
        # AND R0, R1, R2
        instruction = 0x5000 | (0 << 9) | (1 << 6) | 2
        
        simulator.set_register(1, 0xFF)
        simulator.set_register(2, 0x0F)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0x0F
    
    def test_and_zero_result(self, simulator):
        """Test AND instruction resulting in zero."""
        # AND R0, R0, #0
        instruction = 0x5000 | (0 << 9) | (0 << 6) | 0x20 | 0
        
        simulator.set_register(0, 0xFF)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0
        n, z, p = simulator.get_condition_codes()
        assert z == 1
    
    def test_not_instruction(self, simulator):
        """Test NOT instruction."""
        # NOT R0, R1
        instruction = 0x9000 | (0 << 9) | (1 << 6) | 0x3F
        
        simulator.set_register(1, 0x00FF)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0xFF00


class TestControlFlowInstructions:
    """Test control flow instructions (BR, JMP, JSR)."""
    
    def test_branch_not_taken(self, simulator):
        """Test branch instruction when condition is not met."""
        # BRz #5 (branch if zero)
        instruction = 0x0000 | 0x400 | 5
        
        simulator.set_register(0, 1)  # Not zero, so Z=0
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        # PC should just increment normally
        assert simulator.get_pc() == initial_pc + 1
    
    def test_branch_taken_positive(self, simulator):
        """Test branch instruction when condition is met (positive)."""
        # BRp #5 (branch if positive)
        instruction = 0x0000 | 0x200 | 5
        
        simulator.set_register(0, 1)  # Positive, so P=1
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        # PC should branch forward
        assert simulator.get_pc() == initial_pc + 1 + 5
    
    def test_branch_taken_negative(self, simulator):
        """Test branch instruction when condition is met (negative)."""
        # BRn #5 (branch if negative)
        instruction = 0x0000 | 0x800 | 5
        
        simulator.set_register(0, 0x8000)  # Negative
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        assert simulator.get_pc() == initial_pc + 1 + 5
    
    def test_branch_unconditional(self, simulator):
        """Test unconditional branch."""
        # BR #10 (unconditional branch)
        instruction = 0x0000 | 0xE00 | 10
        
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        assert simulator.get_pc() == initial_pc + 1 + 10
    
    def test_branch_backward(self, simulator):
        """Test backward branch with negative offset."""
        # BR #-2 (branch backward)
        # In 9-bit 2's complement, -2 is 0x1FE
        instruction = 0x0000 | 0xE00 | 0x1FE
        
        simulator.set_pc(0x3010)  # Start at higher address
        simulator.set_memory(0x3010, instruction)
        simulator.step()
        
        assert simulator.get_pc() == 0x3010 + 1 - 2
    
    def test_jmp_instruction(self, simulator):
        """Test JMP instruction."""
        # JMP R1
        instruction = 0xC000 | (1 << 6)
        
        simulator.set_register(1, 0x4000)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_pc() == 0x4000
    
    def test_jsr_instruction(self, simulator):
        """Test JSR instruction."""
        # JSR #100
        instruction = 0x4000 | 0x800 | 100
        
        initial_pc = simulator.get_pc()
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        # R7 should contain return address
        assert simulator.get_register(7) == initial_pc + 1
        # PC should jump to target
        assert simulator.get_pc() == initial_pc + 1 + 100
    
    def test_jsrr_instruction(self, simulator):
        """Test JSRR instruction."""
        # JSRR R1
        instruction = 0x4000 | (1 << 6)
        
        simulator.set_register(1, 0x4000)
        initial_pc = simulator.get_pc()
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(7) == initial_pc + 1
        assert simulator.get_pc() == 0x4000


class TestMemoryInstructions:
    """Test memory access instructions (LD, LDI, LDR, ST, STI, STR, LEA)."""
    
    def test_ld_instruction(self, simulator):
        """Test LD instruction."""
        # LD R0, #5
        instruction = 0x2000 | (0 << 9) | 5
        
        # Set up data at target location
        simulator.set_memory(0x3000 + 1 + 5, 0x1234)  # PC+1+offset
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0x1234
    
    def test_ldi_instruction(self, simulator):
        """Test LDI instruction."""
        # LDI R0, #5
        instruction = 0xA000 | (0 << 9) | 5
        
        # Set up indirect addressing
        simulator.set_memory(0x3000 + 1 + 5, 0x4000)  # Pointer
        simulator.set_memory(0x4000, 0x5678)          # Actual data
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0x5678
    
    def test_ldr_instruction(self, simulator):
        """Test LDR instruction."""
        # LDR R0, R1, #10
        instruction = 0x6000 | (0 << 9) | (1 << 6) | 10
        
        simulator.set_register(1, 0x4000)
        simulator.set_memory(0x4000 + 10, 0x9ABC)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0x9ABC
    
    def test_st_instruction(self, simulator):
        """Test ST instruction."""
        # ST R0, #5
        instruction = 0x3000 | (0 << 9) | 5
        
        simulator.set_register(0, 0xDEAD)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_memory(0x3000 + 1 + 5) == 0xDEAD
    
    def test_sti_instruction(self, simulator):
        """Test STI instruction."""
        # STI R0, #5
        instruction = 0xB000 | (0 << 9) | 5
        
        simulator.set_register(0, 0xBEEF)
        simulator.set_memory(0x3000 + 1 + 5, 0x4000)  # Pointer
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_memory(0x4000) == 0xBEEF
    
    def test_str_instruction(self, simulator):
        """Test STR instruction."""
        # STR R0, R1, #10
        instruction = 0x7000 | (0 << 9) | (1 << 6) | 10
        
        simulator.set_register(0, 0xCAFE)
        simulator.set_register(1, 0x4000)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_memory(0x4000 + 10) == 0xCAFE
    
    def test_lea_instruction(self, simulator):
        """Test LEA instruction."""
        # LEA R0, #20
        instruction = 0xE000 | (0 << 9) | 20
        
        initial_pc = simulator.get_pc()
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == initial_pc + 1 + 20


class TestTrapInstructions:
    """Test TRAP instructions."""
    
    def test_halt_trap(self, simulator):
        """Test HALT trap."""
        # TRAP x25
        instruction = 0xF000 | 0x25
        
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.is_halted() == True
    
    def test_out_trap(self, simulator):
        """Test OUT trap."""
        # TRAP x21
        instruction = 0xF000 | 0x21
        
        simulator.set_register(0, ord('A'))
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        # Check that R7 contains return address
        assert simulator.get_register(7) == initial_pc + 1
        # Check that character was output (stored in special location)
        assert simulator.get_memory(0xFFFF) == ord('A')
    
    def test_getc_trap(self, simulator):
        """Test GETC trap."""
        # TRAP x20
        instruction = 0xF000 | 0x20
        
        # Set up input character
        simulator.set_memory(0xFFFD, ord('B'))
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == ord('B')
    
    def test_puts_trap(self, simulator):
        """Test PUTS trap."""
        # TRAP x22
        instruction = 0xF000 | 0x22
        
        simulator.set_memory(0x3000, instruction)
        initial_pc = simulator.get_pc()
        simulator.step()
        
        # Check that PUTS was called (marked in special location)
        assert simulator.get_memory(0xFFFE) == 1
        assert simulator.get_register(7) == initial_pc + 1
