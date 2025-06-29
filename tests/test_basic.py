"""
Unit tests for basic LC-3 simulator functionality.
"""
import pytest


class TestSimulatorBasics:
    """Test basic simulator initialization and state management."""
    
    def test_simulator_creation(self, simulator):
        """Test that simulator can be created and initialized."""
        assert simulator is not None
        assert simulator.get_pc() == 0x3000  # Should start at user space
        assert simulator.is_halted() == False
    
    def test_simulator_reset(self, simulator):
        """Test that simulator reset works correctly."""
        # Modify some state
        simulator.set_register(0, 42)
        simulator.set_pc(0x4000)
        
        # Reset and verify
        simulator.reset()
        assert simulator.get_register(0) == 0
        assert simulator.get_pc() == 0x3000
        assert simulator.is_halted() == False
    
    def test_register_access(self, simulator):
        """Test register read/write operations."""
        # Test all 8 registers
        for i in range(8):
            test_value = 0x1000 + i
            simulator.set_register(i, test_value)
            assert simulator.get_register(i) == test_value
        
        # Test invalid register access
        assert simulator.get_register(-1) == 0
        assert simulator.get_register(8) == 0
    
    def test_memory_access(self, simulator):
        """Test memory read/write operations."""
        test_addresses = [0x3000, 0x3001, 0x4000, 0xFFFF]
        
        for addr in test_addresses:
            test_value = 0x1234
            simulator.set_memory(addr, test_value)
            assert simulator.get_memory(addr) == test_value
    
    def test_pc_management(self, simulator):
        """Test program counter operations."""
        test_values = [0x3000, 0x3001, 0x4000, 0x5000]
        
        for pc_value in test_values:
            simulator.set_pc(pc_value)
            assert simulator.get_pc() == pc_value
    
    def test_condition_codes_initialization(self, simulator):
        """Test that condition codes are properly initialized."""
        n, z, p = simulator.get_condition_codes()
        assert n == 0
        assert z == 1  # Should start with Z=1
        assert p == 0


class TestProgramLoading:
    """Test program loading functionality."""
    
    def test_load_simple_program(self, simulator):
        """Test loading a simple program."""
        program = [0x1021, 0xF025]  # ADD R0, R0, #1; HALT
        simulator.load_program(program)
        
        assert simulator.get_memory(0x3000) == 0x1021
        assert simulator.get_memory(0x3001) == 0xF025
        assert simulator.get_pc() == 0x3000
    
    def test_load_program_at_custom_address(self, simulator):
        """Test loading program at custom address."""
        program = [0x1021, 0xF025]
        start_addr = 0x4000
        
        simulator.load_program(program, start_addr)
        
        assert simulator.get_memory(start_addr) == 0x1021
        assert simulator.get_memory(start_addr + 1) == 0xF025
        assert simulator.get_pc() == start_addr
    
    def test_load_empty_program(self, simulator):
        """Test loading an empty program."""
        program = []
        simulator.load_program(program)
        
        # PC should still be set correctly
        assert simulator.get_pc() == 0x3000
    
    def test_load_large_program(self, simulator):
        """Test loading a larger program."""
        # Create a program that fills some memory
        program = [i for i in range(100)]
        simulator.load_program(program)
        
        for i in range(100):
            assert simulator.get_memory(0x3000 + i) == i


class TestConditionCodes:
    """Test condition code functionality."""
    
    def test_condition_codes_zero(self, simulator):
        """Test condition codes when result is zero."""
        simulator.set_register(0, 0)
        n, z, p = simulator.get_condition_codes()
        assert n == 0
        assert z == 1
        assert p == 0
    
    def test_condition_codes_positive(self, simulator):
        """Test condition codes when result is positive."""
        simulator.set_register(0, 42)
        n, z, p = simulator.get_condition_codes()
        assert n == 0
        assert z == 0
        assert p == 1
    
    def test_condition_codes_negative(self, simulator):
        """Test condition codes when result is negative."""
        simulator.set_register(0, 0x8000)  # Negative in 2's complement
        n, z, p = simulator.get_condition_codes()
        assert n == 1
        assert z == 0
        assert p == 0


class TestExecutionControl:
    """Test execution control functionality."""
    
    def test_single_step_execution(self, loaded_simulator):
        """Test single step execution."""
        initial_pc = loaded_simulator.get_pc()
        
        # Execute one instruction
        loaded_simulator.step()
        
        # PC should have incremented
        assert loaded_simulator.get_pc() == initial_pc + 1
        # R0 should have been incremented
        assert loaded_simulator.get_register(0) == 1
    
    def test_halt_detection(self, loaded_simulator):
        """Test that simulator detects halt instruction."""
        # Run the loaded program (ADD R0, R0, #1; HALT)
        loaded_simulator.run()
        
        assert loaded_simulator.is_halted() == True
        assert loaded_simulator.get_register(0) == 1
    
    def test_max_cycles_protection(self, simulator):
        """Test that run() respects max_cycles parameter."""
        # Create an infinite loop program
        program = [
            0x0FFE,  # BR #-2 (infinite loop)
        ]
        simulator.load_program(program)
        
        # Run with limited cycles
        simulator.run(max_cycles=10)
        
        # Should not be halted (still in infinite loop)
        # but should have stopped due to cycle limit
        assert simulator.is_halted() == False
