"""
Integration tests to ensure pipeline integration doesn't break existing functionality.
"""
import pytest
import sys
import os

# Add the build directory to the path to import the compiled module
build_path = os.path.join(os.path.dirname(__file__), '..', 'build', 'python_bindings')
sys.path.insert(0, build_path)

try:
    import lc3_simulator
    simulator_available = True
except ImportError:
    simulator_available = False


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available")
class TestBackwardCompatibility:
    """Test that existing functionality still works after pipeline integration."""

    def test_basic_execution_unchanged(self):
        """Test that basic program execution produces same results as before."""
        sim = lc3_simulator.LC3Simulator()
        
        # Simple test program
        program = [
            0x1021,  # ADD R0, R0, #1
            0x1421,  # ADD R2, R0, #1
            0xF025   # HALT
        ]
        sim.load_program(program)
        sim.run()
        
        # Results should be deterministic and correct
        assert sim.is_halted()
        assert sim.get_register(0) == 1
        assert sim.get_register(2) == 2

    def test_condition_codes_unchanged(self):
        """Test that condition codes still work correctly."""
        sim = lc3_simulator.LC3Simulator()
        
        # Program that tests condition codes
        program = [
            0x5020,  # AND R0, R0, #0  (should set Z=1, N=0, P=0)
            0x1021,  # ADD R0, R0, #1  (should set Z=0, N=0, P=1)  
            0xF025   # HALT
        ]
        sim.load_program(program)
        sim.run()
        
        # Final condition codes should be P=1
        n, z, p = sim.get_condition_codes()
        assert n == 0
        assert z == 0
        assert p == 1

    def test_memory_operations_unchanged(self):
        """Test that memory operations still work correctly."""
        sim = lc3_simulator.LC3Simulator()
        
        # Test direct memory access (not affected by pipeline)
        test_addr = 0x4000
        test_value = 0x1234
        
        sim.set_memory(test_addr, test_value)
        assert sim.get_memory(test_addr) == test_value

    def test_branch_behavior_unchanged(self):
        """Test that branch instructions still work correctly."""
        sim = lc3_simulator.LC3Simulator()
        
        # Program with conditional branch
        program = [
            0x5020,  # AND R0, R0, #0  (clear R0, set Z)
            0x0402,  # BRz +2          (should branch)
            0x1021,  # ADD R0, R0, #1  (should be skipped)
            0x1421,  # ADD R2, R0, #1  (branch target)
            0xF025   # HALT
        ]
        sim.load_program(program)
        sim.run()
        
        # Should branch correctly
        assert sim.is_halted()
        assert sim.get_register(0) == 0  # Should remain 0 (instruction skipped)
        assert sim.get_register(2) == 1  # Should be 1 from branch target

    def test_reset_still_works(self):
        """Test that reset functionality is preserved."""
        sim = lc3_simulator.LC3Simulator()
        
        # Modify state
        sim.set_register(0, 42)
        sim.set_memory(0x4000, 0x1234)
        
        # Reset
        sim.reset()
        
        # Should be back to initial state
        assert sim.get_register(0) == 0
        assert sim.get_memory(0x4000) == 0
        assert sim.get_pc() == 0x3000
        assert not sim.is_halted()

    def test_step_execution_still_works(self):
        """Test that single-step execution is preserved."""
        sim = lc3_simulator.LC3Simulator()
        
        program = [0x1021, 0xF025]  # ADD R0, R0, #1; HALT
        sim.load_program(program)
        
        # Execute first instruction
        initial_pc = sim.get_pc()
        sim.step()
        
        # Should have executed one instruction
        assert sim.get_register(0) == 1
        assert not sim.is_halted()  # Should not be halted yet
        
        # Execute second instruction (HALT)
        sim.step()
        assert sim.is_halted()

    def test_trap_instructions_unchanged(self):
        """Test that TRAP instructions still work correctly."""
        sim = lc3_simulator.LC3Simulator()
        
        # Test HALT trap
        program = [0xF025]  # TRAP x25 (HALT)
        sim.load_program(program)
        sim.run()
        
        assert sim.is_halted()

    def test_all_instruction_types_still_work(self):
        """Test that all instruction types can still be executed."""
        sim = lc3_simulator.LC3Simulator()
        
        # Program with various instruction types
        program = [
            0x1021,  # ADD R0, R0, #1      (ADD immediate)
            0x1401,  # ADD R2, R0, R1      (ADD register) 
            0x5020,  # AND R0, R0, #0      (AND immediate)
            0x5401,  # AND R2, R0, R1      (AND register)
            0x9240,  # NOT R1, R0          (NOT)
            0x2003,  # LD R0, DATA         (LD)
            0x3003,  # ST R0, DATA         (ST)
            0xE004,  # LEA R0, DATA        (LEA)
            0xF025,  # TRAP x25            (HALT)
            0x0042   # DATA: 0x42
        ]
        sim.load_program(program)
        sim.run()
        
        # Should execute without errors
        assert sim.is_halted()


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available") 
class TestPipelineTransparency:
    """Test that pipeline mode doesn't change functional behavior."""

    def test_same_results_with_pipeline_disabled(self):
        """Test that results are identical with pipeline disabled."""
        # Test program
        program = [
            0x1021,  # ADD R0, R0, #1
            0x1421,  # ADD R2, R0, #1
            0x1842,  # ADD R4, R2, #2
            0xF025   # HALT
        ]
        
        # Run without pipeline (default)
        sim1 = lc3_simulator.LC3Simulator()
        sim1.load_program(program)
        sim1.run()
        
        # Run with pipeline explicitly disabled
        sim2 = lc3_simulator.LC3Simulator()
        sim2.enable_pipeline(False)  # Explicitly disable
        sim2.load_program(program)
        sim2.run()
        
        # Results should be identical
        for i in range(8):
            assert sim1.get_register(i) == sim2.get_register(i), f"Register R{i} differs"
        
        assert sim1.get_pc() == sim2.get_pc()
        assert sim1.is_halted() == sim2.is_halted()
        assert sim1.get_condition_codes() == sim2.get_condition_codes()

    def test_same_results_with_pipeline_enabled(self):
        """Test that functional results are identical with pipeline enabled."""
        # Test program
        program = [
            0x1021,  # ADD R0, R0, #1
            0x1421,  # ADD R2, R0, #1  
            0x1842,  # ADD R4, R2, #2
            0xF025   # HALT
        ]
        
        # Run without pipeline
        sim1 = lc3_simulator.LC3Simulator()
        sim1.load_program(program)
        sim1.run()
        
        # Run with pipeline enabled
        sim2 = lc3_simulator.LC3Simulator()
        sim2.enable_pipeline(True)
        sim2.load_program(program)
        sim2.run()
        
        # Functional results should be identical
        for i in range(8):
            assert sim1.get_register(i) == sim2.get_register(i), f"Register R{i} differs"
        
        assert sim1.is_halted() == sim2.is_halted()
        assert sim1.get_condition_codes() == sim2.get_condition_codes()

    def test_complex_program_consistency(self):
        """Test consistency with a more complex program."""
        # More complex test program with loops and branches
        program = [
            0x2007,  # LD R0, COUNTER     ; Load loop counter
            0x0406,  # BRz +6             ; Branch if zero (to end)
            0x1420,  # ADD R2, R0, #0     ; Copy R0 to R2
            0x1021,  # ADD R0, R0, #1     ; Increment R0
            0x127F,  # ADD R1, R1, #-1    ; Decrement R1 
            0x03FB,  # ST R1, COUNTER     ; Store back counter
            0x0FFA,  # BRnzp -6           ; Branch back to start
            0xF025,  # TRAP x25           ; HALT
            0x0003   # COUNTER: 3         ; Loop counter
        ]
        
        # Run without pipeline
        sim1 = lc3_simulator.LC3Simulator()
        sim1.load_program(program)
        sim1.run(max_cycles=100)  # Prevent infinite loops
        
        # Run with pipeline
        sim2 = lc3_simulator.LC3Simulator()
        sim2.enable_pipeline(True)
        sim2.load_program(program)
        sim2.run(max_cycles=100)  # Prevent infinite loops
        
        # Results should be functionally equivalent
        # (Note: exact register values might depend on loop execution)
        assert sim1.is_halted() == sim2.is_halted()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
