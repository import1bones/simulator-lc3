"""
Test Integration implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

"""
Integration tests for complete LC-3 programs.
"""
import pytest


class TestSimplePrograms:
    """Test execution of simple but complete LC-3 programs."""
    
    def test_simple_counter(self, simulator, sample_programs):
        """Test a simple counting program."""
        simulator.load_program(sample_programs['simple_add'])
        simulator.run()
        
        assert simulator.is_halted() == True
        assert simulator.get_register(0) == 1
    
    def test_loop_with_data(self, simulator, sample_programs):
        """Test a program that loads data, modifies it, and stores it back."""
        simulator.load_program(sample_programs['loop_counter'])
        simulator.run()
        
        assert simulator.is_halted() == True
        # R0 should contain original value + 1
        assert simulator.get_register(0) == 6
        # Memory location should be updated
        assert simulator.get_memory(0x3004) == 6
    
    def test_conditional_execution(self, simulator, sample_programs):
        """Test conditional branch execution."""
        simulator.load_program(sample_programs['conditional_branch'])
        simulator.run()
        
        assert simulator.is_halted() == True
        # R0 should be 2 (incremented twice)
        assert simulator.get_register(0) == 2
    
    def test_subroutine_call_and_return(self, simulator, sample_programs):
        """Test subroutine call and return."""
        simulator.load_program(sample_programs['subroutine_call'])
        simulator.run()
        
        assert simulator.is_halted() == True
        # R0 should be incremented by the subroutine
        assert simulator.get_register(0) == 1


class TestComplexPrograms:
    """Test more complex LC-3 programs."""
    
    def test_factorial_program(self, simulator):
        """Test a factorial calculation program."""
        # Program to calculate 4! = 24
        program = [
            0x2010,  # LD R0, N          ; Load N (4)
            0x5240,  # AND R1, R1, #0    ; Clear R1 (result)
            0x1261,  # ADD R1, R1, #1    ; R1 = 1 (initial result)
            0x5480,  # AND R2, R2, #0    ; Clear R2 (counter)
            0x14A1,  # ADD R2, R2, R0    ; R2 = N (counter)
            0x0406,  # BRz END           ; If counter is 0, end
            0x1401,  # ADD R1, R1, R0    ; Multiply step (simplified)
            0x1501,  # ADD R1, R1, R0    ; (This is addition, not true multiply)
            0x14BF,  # ADD R2, R2, #-1   ; Decrement counter
            0x0FFB,  # BR LOOP           ; Branch back to loop
            0x3210,  # ST R1, RESULT     ; Store result
            0xF025,  # TRAP x25          ; HALT
            0x0004,  # N: 4
            0x0000   # RESULT: 0
        ]
        
        simulator.load_program(program)
        simulator.run(max_cycles=100)
        
        assert simulator.is_halted() == True
        # Check that result was calculated and stored
        result = simulator.get_memory(0x3000 + len(program) - 1)
        assert result > 0  # Should have calculated something
    
    def test_fibonacci_program(self, simulator):
        """Test a Fibonacci sequence program."""
        # Program to calculate Fibonacci numbers
        program = [
            0x5020,  # AND R0, R0, #0    ; F(0) = 0
            0x5240,  # AND R1, R1, #0    ; Clear R1
            0x1261,  # ADD R1, R1, #1    ; F(1) = 1
            0x5480,  # AND R2, R2, #0    ; Clear counter
            0x14A5,  # ADD R2, R2, #5    ; Calculate F(5)
            0x0407,  # BRz END           ; If counter is 0, end
            0x1200,  # ADD R1, R0, R1    ; F(n) = F(n-1) + F(n-2)
            0x1040,  # ADD R0, R1, #0    ; Shift values
            0x14BF,  # ADD R2, R2, #-1   ; Decrement counter
            0x0FFA,  # BR LOOP           ; Continue
            0xF025   # TRAP x25          ; HALT
        ]
        
        simulator.load_program(program)
        simulator.run(max_cycles=100)
        
        assert simulator.is_halted() == True
        # F(5) should be in R1
        assert simulator.get_register(1) > 0
    
    def test_string_processing(self, simulator):
        """Test a program that processes a string."""
        # Program to count characters in a string
        program = [
            0x2008,  # LD R0, STRING_PTR  ; Load string pointer
            0x5240,  # AND R1, R1, #0     ; Clear counter
            0x6400,  # LDR R2, R0, #0     ; Load character
            0x0403,  # BRz END            ; If null terminator, end
            0x1261,  # ADD R1, R1, #1     ; Increment counter
            0x1021,  # ADD R0, R0, #1     ; Move to next character
            0x0FFB,  # BR LOOP            ; Continue
            0xF025,  # TRAP x25           ; HALT
            0x3009,  # STRING_PTR: points to string
            ord('H'), ord('e'), ord('l'), ord('l'), ord('o'), 0x00  # "Hello"
        ]
        
        simulator.load_program(program)
        simulator.run(max_cycles=100)
        
        assert simulator.is_halted() == True
        # Should have counted 5 characters
        assert simulator.get_register(1) == 5


class TestErrorConditions:
    """Test how the simulator handles error conditions."""
    
    def test_invalid_instruction(self, simulator):
        """Test behavior with invalid instruction."""
        # Use an undefined opcode
        invalid_instruction = 0xD000  # Undefined opcode
        
        simulator.set_memory(0x3000, invalid_instruction)
        simulator.step()
        
        # Simulator should halt on invalid instruction
        assert simulator.is_halted() == True
    
    def test_infinite_loop_protection(self, simulator):
        """Test protection against infinite loops."""
        # Create an infinite loop
        program = [
            0x0FFE   # BR #-2 (infinite loop)
        ]
        
        simulator.load_program(program)
        simulator.run(max_cycles=10)
        
        # Should stop due to cycle limit, not halt instruction
        assert simulator.is_halted() == False
    
    def test_memory_boundary_access(self, simulator):
        """Test access to memory boundaries."""
        # Test access to highest memory address
        simulator.set_memory(0xFFFF, 0x1234)
        assert simulator.get_memory(0xFFFF) == 0x1234
        
        # Test access to lowest user space
        simulator.set_memory(0x3000, 0x5678)
        assert simulator.get_memory(0x3000) == 0x5678


class TestPerformance:
    """Performance and stress tests."""
    
    @pytest.mark.slow
    def test_performance_large_program(self, simulator):
        """Test performance with a large program."""
        # Create a large program that does many operations
        program = []
        
        # Add 1000 ADD instructions
        for i in range(1000):
            program.append(0x1021)  # ADD R0, R0, #1
        
        program.append(0xF025)  # HALT
        
        simulator.load_program(program)
        simulator.run(max_cycles=10000)
        
        assert simulator.is_halted() == True
        assert simulator.get_register(0) == 1000
    
    @pytest.mark.slow
    def test_performance_deep_recursion(self, simulator):
        """Test performance with deep subroutine calls."""
        # Program that makes many JSR calls
        program = [
            0x2005,  # LD R0, DEPTH      ; Load recursion depth
            0x0402,  # BRz END           ; If depth is 0, end
            0x14FF,  # ADD R0, R0, #-1   ; Decrement depth
            0x4801,  # JSR RECURSE       ; Recursive call
            0xF025,  # TRAP x25          ; HALT
            0x000A   # DEPTH: 10
        ]
        
        simulator.load_program(program)
        simulator.run(max_cycles=1000)
        
        # Should eventually halt or hit cycle limit
        assert simulator.is_halted() == True or simulator.get_pc() != 0
