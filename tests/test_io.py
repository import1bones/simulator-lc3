"""
Test Io implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

"""
Tests for I/O operations and TRAP instructions.
"""
import pytest


class TestBasicTraps:
    """Test basic TRAP instruction functionality."""
    
    def test_halt_trap_execution(self, simulator):
        """Test HALT trap stops execution."""
        # TRAP x25 (HALT)
        halt_instruction = 0xF000 | 0x25
        
        simulator.set_memory(0x3000, halt_instruction)
        initial_pc = simulator.get_pc()
        
        simulator.step()
        
        # Simulator should be halted
        assert simulator.is_halted() == True
        # R7 should contain return address
        assert simulator.get_register(7) == initial_pc + 1
    
    def test_trap_return_address(self, simulator):
        """Test that TRAP instructions save return address."""
        trap_instructions = [
            0xF020,  # GETC
            0xF021,  # OUT
            0xF022,  # PUTS
            0xF023,  # IN
        ]
        
        for i, instruction in enumerate(trap_instructions):
            simulator.reset()
            simulator.set_pc(0x3000 + i * 0x100)  # Different PC for each test
            initial_pc = simulator.get_pc()
            simulator.set_memory(initial_pc, instruction)
            
            simulator.step()
            
            # R7 should contain return address
            assert simulator.get_register(7) == initial_pc + 1
    
    def test_unknown_trap(self, simulator):
        """Test behavior with unknown trap vector."""
        # Use an undefined trap vector
        unknown_trap = 0xF000 | 0x99
        
        simulator.set_memory(0x3000, unknown_trap)
        simulator.step()
        
        # Should halt on unknown trap
        assert simulator.is_halted() == True


class TestOutputTraps:
    """Test output-related TRAP instructions."""
    
    def test_out_trap_character_output(self, simulator):
        """Test OUT trap outputs character."""
        # TRAP x21 (OUT)
        out_instruction = 0xF000 | 0x21
        
        test_char = ord('A')
        simulator.set_register(0, test_char)
        simulator.set_memory(0x3000, out_instruction)
        
        simulator.step()
        
        # Character should be stored in special output location
        assert simulator.get_memory(0xFFFF) == test_char
    
    def test_out_trap_multiple_characters(self, simulator):
        """Test OUT trap with multiple characters."""
        test_chars = [ord('H'), ord('e'), ord('l'), ord('l'), ord('o')]
        
        for i, char in enumerate(test_chars):
            # OUT each character
            simulator.set_register(0, char)
            out_instruction = 0xF000 | 0x21
            simulator.set_memory(0x3000 + i, out_instruction)
            simulator.set_pc(0x3000 + i)
            
            simulator.step()
            
            # Verify character was output
            assert simulator.get_memory(0xFFFF) == char
    
    def test_puts_trap_string_output(self, simulator):
        """Test PUTS trap for string output."""
        # TRAP x22 (PUTS)
        puts_instruction = 0xF000 | 0x22
        
        # Set R0 to point to a string
        string_addr = 0x4000
        simulator.set_register(0, string_addr)
        
        # Set up string in memory: "Hi\0"
        simulator.set_memory(string_addr, ord('H'))
        simulator.set_memory(string_addr + 1, ord('i'))
        simulator.set_memory(string_addr + 2, 0)  # Null terminator
        
        simulator.set_memory(0x3000, puts_instruction)
        simulator.step()
        
        # PUTS should be marked as called
        assert simulator.get_memory(0xFFFE) == 1
    
    def test_out_trap_special_characters(self, simulator):
        """Test OUT trap with special characters."""
        special_chars = [
            0x00,    # Null
            0x09,    # Tab
            0x0A,    # Newline
            0x0D,    # Carriage return
            0x20,    # Space
            0x7F,    # DEL
        ]
        
        for char in special_chars:
            simulator.reset()
            simulator.set_register(0, char)
            out_instruction = 0xF000 | 0x21
            simulator.set_memory(0x3000, out_instruction)
            
            simulator.step()
            
            assert simulator.get_memory(0xFFFF) == char


class TestInputTraps:
    """Test input-related TRAP instructions."""
    
    def test_getc_trap_character_input(self, simulator):
        """Test GETC trap reads character."""
        # TRAP x20 (GETC)
        getc_instruction = 0xF000 | 0x20
        
        input_char = ord('X')
        # Set up input character in special location
        simulator.set_memory(0xFFFD, input_char)
        
        simulator.set_memory(0x3000, getc_instruction)
        simulator.step()
        
        # Character should be in R0
        assert simulator.get_register(0) == input_char
        
        # Condition codes should be set
        n, z, p = simulator.get_condition_codes()
        if input_char == 0:
            assert z == 1
        elif input_char & 0x80:
            assert n == 1
        else:
            assert p == 1
    
    def test_in_trap_character_input(self, simulator):
        """Test IN trap reads character with prompt."""
        # TRAP x23 (IN)
        in_instruction = 0xF000 | 0x23
        
        input_char = ord('Y')
        simulator.set_memory(0xFFFD, input_char)
        
        simulator.set_memory(0x3000, in_instruction)
        simulator.step()
        
        # Character should be in R0
        assert simulator.get_register(0) == input_char
        
        # Condition codes should be set based on input
        n, z, p = simulator.get_condition_codes()
        assert p == 1  # 'Y' is positive
    
    def test_getc_zero_input(self, simulator):
        """Test GETC with zero input."""
        getc_instruction = 0xF000 | 0x20
        
        # Input zero character
        simulator.set_memory(0xFFFD, 0)
        simulator.set_memory(0x3000, getc_instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0
        n, z, p = simulator.get_condition_codes()
        assert z == 1
    
    def test_getc_high_bit_input(self, simulator):
        """Test GETC with high bit set (negative in signed interpretation)."""
        getc_instruction = 0xF000 | 0x20
        
        # Input character with high bit set
        simulator.set_memory(0xFFFD, 0xFF)
        simulator.set_memory(0x3000, getc_instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0xFF


class TestTrapSequences:
    """Test sequences of TRAP instructions."""
    
    def test_input_output_sequence(self, simulator):
        """Test sequence of input followed by output."""
        program = [
            0xF020,  # GETC - read character
            0xF021,  # OUT - output character
            0xF025   # HALT
        ]
        
        # Set up input
        input_char = ord('Z')
        simulator.set_memory(0xFFFD, input_char)
        
        simulator.load_program(program)
        simulator.run()
        
        assert simulator.is_halted() == True
        # Output should match input
        assert simulator.get_memory(0xFFFF) == input_char
    
    def test_echo_program(self, simulator):
        """Test a simple echo program."""
        # Program that reads a character and echoes it back
        program = [
            0xF020,  # GETC
            0xF021,  # OUT
            0x0FFD,  # BR #-3 (loop back)
            0xF025   # HALT (unreachable)
        ]
        
        simulator.load_program(program)
        
        # Simulate multiple input/output cycles
        test_chars = [ord('A'), ord('B'), ord('C')]
        
        for char in test_chars:
            simulator.set_memory(0xFFFD, char)
            
            # Execute GETC
            simulator.step()
            assert simulator.get_register(0) == char
            
            # Execute OUT
            simulator.step()
            assert simulator.get_memory(0xFFFF) == char
            
            # Execute BR (loop back)
            simulator.step()
    
    def test_string_output_program(self, simulator):
        """Test program that outputs a string using PUTS."""
        string_data = [ord('T'), ord('e'), ord('s'), ord('t'), 0]  # "Test"
        
        program = [
            0x2002,  # LD R0, STRING_PTR
            0xF022,  # PUTS
            0xF025,  # HALT
            0x3004   # STRING_PTR: points to string data
        ] + string_data
        
        simulator.load_program(program)
        simulator.run()
        
        assert simulator.is_halted() == True
        # PUTS should have been called
        assert simulator.get_memory(0xFFFE) == 1


class TestTrapErrorConditions:
    """Test error conditions and edge cases for TRAP instructions."""
    
    def test_trap_with_invalid_register_state(self, simulator):
        """Test TRAP instructions with unusual register states."""
        # Test OUT with invalid character codes
        invalid_chars = [0x100, 0x200, 0xFFFF]  # Values larger than 8-bit
        
        for char in invalid_chars:
            simulator.reset()
            simulator.set_register(0, char)
            out_instruction = 0xF000 | 0x21
            simulator.set_memory(0x3000, out_instruction)
            
            simulator.step()
            
            # Should output only the low 8 bits
            assert simulator.get_memory(0xFFFF) == (char & 0xFF)
    
    def test_trap_stack_behavior(self, simulator):
        """Test that TRAPs properly save and can restore context."""
        # Set up various register states
        initial_registers = [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666, 0x7777, 0x8888]
        
        for i, value in enumerate(initial_registers[:7]):  # Don't set R7
            simulator.set_register(i, value)
        
        # Execute a TRAP that doesn't modify registers (except R7)
        getc_instruction = 0xF000 | 0x20
        simulator.set_memory(0xFFFD, ord('A'))  # Set up input
        simulator.set_memory(0x3000, getc_instruction)
        
        initial_pc = simulator.get_pc()
        simulator.step()
        
        # R7 should be modified (return address)
        assert simulator.get_register(7) == initial_pc + 1
        
        # Other registers should be preserved (except R0 which gets input)
        for i in range(1, 7):
            assert simulator.get_register(i) == initial_registers[i]
    
    def test_nested_trap_calls(self, simulator):
        """Test behavior with nested TRAP calls."""
        # This tests the theoretical case where a TRAP handler
        # might call another TRAP (though not typical in LC-3)
        
        program = [
            0xF020,  # GETC
            0xF021,  # OUT (outputs what was just read)
            0xF025   # HALT
        ]
        
        simulator.set_memory(0xFFFD, ord('N'))
        simulator.load_program(program)
        
        # Execute step by step to see intermediate states
        initial_pc = simulator.get_pc()
        
        # First TRAP (GETC)
        simulator.step()
        assert simulator.get_register(7) == initial_pc + 1
        assert simulator.get_register(0) == ord('N')
        
        # Second TRAP (OUT) - should overwrite R7
        simulator.step()
        assert simulator.get_register(7) == initial_pc + 2
        assert simulator.get_memory(0xFFFF) == ord('N')
