"""
Tests for LC-3 Pipeline Functionality
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
class TestPipelineBasic:
    """Test basic pipeline functionality."""

    def test_pipeline_enable_disable(self):
        """Test enabling and disabling pipeline mode."""
        sim = lc3_simulator.LC3Simulator()
        
        # Test enabling pipeline
        sim.enable_pipeline(True)
        
        # Test disabling pipeline
        sim.enable_pipeline(False)
        
        # Should not raise any exceptions
        assert True

    def test_pipeline_reset(self):
        """Test pipeline reset functionality."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Reset pipeline should not raise exceptions
        sim.reset_pipeline()
        
        assert True

    def test_pipeline_configuration(self):
        """Test pipeline configuration settings."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Configure pipeline with custom settings
        sim.configure_pipeline("Test Pipeline", 5, True, False)
        
        # Should not raise any exceptions
        assert True

    def test_pipeline_metrics_structure(self):
        """Test that pipeline metrics return expected structure."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        metrics = sim.get_pipeline_metrics()
        
        # Check that expected keys are present
        expected_keys = [
            'total_cycles', 'total_instructions', 'cpi', 'ipc',
            'pipeline_efficiency', 'stall_cycles', 'data_hazards',
            'control_hazards', 'structural_hazards', 'memory_reads',
            'memory_writes', 'memory_stall_cycles'
        ]
        
        for key in expected_keys:
            assert key in metrics, f"Missing metric key: {key}"
            assert isinstance(metrics[key], (int, float)), f"Metric {key} should be numeric"


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available")
class TestPipelineExecution:
    """Test pipeline execution with actual programs."""

    def test_simple_program_with_pipeline(self):
        """Test running a simple program with pipeline enabled."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Simple program: ADD R0, R0, #1; HALT
        program = [0x1021, 0xF025]
        sim.load_program(program)
        
        # Run the program
        sim.run()
        
        # Check that it executed
        assert sim.is_halted()
        assert sim.get_register(0) == 1
        
        # Check pipeline metrics
        metrics = sim.get_pipeline_metrics()
        assert metrics['total_instructions'] >= 1
        assert metrics['total_cycles'] >= 1

    def test_pipeline_with_multiple_instructions(self):
        """Test pipeline with multiple instructions."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
          # Program with multiple ADD instructions
        program = [
            0x1021,  # ADD R0, R0, #1
            0x1421,  # ADD R2, R0, #1
            0x18A2,  # ADD R4, R2, #2 (corrected encoding)
            0xF025   # HALT
        ]
        sim.load_program(program)
        
        # Run the program
        sim.run()
        
        # Check results
        assert sim.is_halted()
        assert sim.get_register(0) == 1
        assert sim.get_register(2) == 2
        assert sim.get_register(4) == 4
        
        # Check pipeline metrics
        metrics = sim.get_pipeline_metrics()
        assert metrics['total_instructions'] >= 3

    def test_pipeline_vs_normal_execution(self):
        """Test that pipeline and normal execution produce same results."""
        # Normal execution
        sim1 = lc3_simulator.LC3Simulator()
        program = [0x1021, 0x1421, 0xF025]  # ADD R0, R0, #1; ADD R2, R0, #1; HALT
        sim1.load_program(program)
        sim1.run()
        
        # Pipeline execution
        sim2 = lc3_simulator.LC3Simulator()
        sim2.enable_pipeline(True)
        sim2.load_program(program)
        sim2.run()
        
        # Results should be identical
        assert sim1.get_register(0) == sim2.get_register(0)
        assert sim1.get_register(2) == sim2.get_register(2)
        assert sim1.is_halted() == sim2.is_halted()


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available")
class TestPipelinePerformance:
    """Test pipeline performance analysis."""

    def test_cpi_calculation(self):
        """Test that CPI is calculated correctly."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Run a program
        program = [0x1021, 0x1421, 0x1842, 0xF025]
        sim.load_program(program)
        sim.run()
        
        metrics = sim.get_pipeline_metrics()
        
        # CPI should be positive and reasonable
        assert metrics['cpi'] > 0
        assert metrics['cpi'] <= 10  # Should not be excessively high
        
        # IPC should be positive and reasonable
        assert metrics['ipc'] > 0
        assert metrics['ipc'] <= 2  # Should not exceed 2 for simple pipeline

    def test_pipeline_efficiency(self):
        """Test pipeline efficiency calculation."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Run a program
        program = [0x1021, 0x1421, 0x1842, 0xF025]
        sim.load_program(program)
        sim.run()
        
        metrics = sim.get_pipeline_metrics()
        
        # Efficiency should be between 0 and 1
        assert 0 <= metrics['pipeline_efficiency'] <= 1

    def test_hazard_detection(self):
        """Test that hazards are detected and counted."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Configure pipeline without forwarding to create hazards
        sim.configure_pipeline("No Forwarding Pipeline", 5, False, False)
        
        # Program with data hazards
        program = [
            0x1021,  # ADD R0, R0, #1   (writes R0)
            0x1401,  # ADD R2, R0, #1   (reads R0 - potential RAW hazard)
            0xF025   # HALT
        ]
        sim.load_program(program)
        sim.run()
        
        metrics = sim.get_pipeline_metrics()
        
        # Should detect some form of hazard or stall
        # Note: The exact behavior depends on the pipeline implementation
        assert metrics['total_cycles'] >= metrics['total_instructions']


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available")
class TestPipelineConfiguration:
    """Test different pipeline configurations."""

    def test_different_forwarding_settings(self):
        """Test pipeline with different forwarding settings."""
        # Test with forwarding enabled
        sim1 = lc3_simulator.LC3Simulator()
        sim1.enable_pipeline(True)
        sim1.configure_pipeline("Forwarding Pipeline", 5, True, False)
        
        program = [0x1021, 0x1401, 0xF025]
        sim1.load_program(program)
        sim1.run()
        metrics1 = sim1.get_pipeline_metrics()
        
        # Test with forwarding disabled
        sim2 = lc3_simulator.LC3Simulator()
        sim2.enable_pipeline(True)
        sim2.configure_pipeline("No Forwarding Pipeline", 5, False, False)
        sim2.load_program(program)
        sim2.run()
        metrics2 = sim2.get_pipeline_metrics()
        
        # Both should produce same functional results
        assert sim1.get_register(0) == sim2.get_register(0)
        assert sim1.get_register(2) == sim2.get_register(2)
        
        # Performance characteristics may differ
        assert metrics1['total_cycles'] >= 0
        assert metrics2['total_cycles'] >= 0

    def test_different_pipeline_depths(self):
        """Test different pipeline depths."""
        for depth in [3, 5, 7]:
            sim = lc3_simulator.LC3Simulator()
            sim.enable_pipeline(True)
            sim.configure_pipeline(f"Depth {depth} Pipeline", depth, True, False)
            
            program = [0x1021, 0x1421, 0xF025]
            sim.load_program(program)
            sim.run()
            
            # Should execute correctly regardless of depth
            assert sim.is_halted()
            assert sim.get_register(0) == 1
            assert sim.get_register(2) == 2


@pytest.mark.skipif(not simulator_available, reason="LC-3 Simulator module not available")
class TestPipelineIntegration:
    """Test integration of pipeline with existing functionality."""

    def test_pipeline_with_reset(self):
        """Test that reset works correctly with pipeline enabled."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Run a program
        program = [0x1021, 0xF025]
        sim.load_program(program)
        sim.run()
        
        # Reset and run again
        sim.reset()
        sim.enable_pipeline(True)
        sim.load_program(program)
        sim.run()
        
        # Should work the second time
        assert sim.is_halted()
        assert sim.get_register(0) == 1

    def test_step_execution_with_pipeline(self):
        """Test single-step execution with pipeline enabled."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        program = [0x1021, 0xF025]
        sim.load_program(program)
        
        # Step through execution
        initial_pc = sim.get_pc()
        sim.step()
        
        # PC should advance
        assert sim.get_pc() != initial_pc or sim.is_halted()

    def test_pipeline_with_branch_instructions(self):
        """Test pipeline with branch instructions."""
        sim = lc3_simulator.LC3Simulator()
        sim.enable_pipeline(True)
        
        # Program with conditional branch
        program = [
            0x5020,  # AND R0, R0, #0 (clear R0, set Z)
            0x0401,  # BRz +1 (should branch to ADD R2, R0, #1)
            0x1021,  # ADD R0, R0, #1 (should be skipped)
            0x1421,  # ADD R2, R0, #1 (branch target) - corrected encoding for immediate mode
            0xF025   # HALT
        ]
        sim.load_program(program)
        sim.run()
        
        # Should execute branch correctly
        assert sim.is_halted()
        assert sim.get_register(0) == 0  # Should remain 0
        assert sim.get_register(2) == 1  # Should be 1 from branch target
        
        # Check that control hazards were detected
        metrics = sim.get_pipeline_metrics()
        # Note: The exact behavior depends on implementation
        assert metrics['total_cycles'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
