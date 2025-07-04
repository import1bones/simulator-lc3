"""
Test suite for the simulator-lc3 command-line interface.

This module provides tests for verifying the functionality of the simulator-lc3 binary
when used as a command-line tool.
"""

import pytest
import subprocess
from pathlib import Path

from test_environment_setup import get_project_root

# Path to the simulator-lc3 binary
SIMULATOR_PATH = Path(get_project_root()) / "build" / "simulator-lc3"


class TestCLI:
    """Test the command-line interface of the simulator-lc3 binary."""

    @pytest.fixture(scope="function")
    def verify_simulator_binary(self):
        """Ensure the simulator binary exists before running tests."""
        assert SIMULATOR_PATH.exists(), (
            f"simulator-lc3 binary not found at {SIMULATOR_PATH}. "
            "Please build the project before running tests."
        )

    def run_simulator(self, args=None, input_data=None, timeout=10):
        """Run the simulator with the given arguments and input data.

        Args:
            args: List of command-line arguments to pass to the simulator
            input_data: String to pass as stdin to the simulator
            timeout: Timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = [str(SIMULATOR_PATH)]
        if args:
            cmd.extend(args)

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if input_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = process.communicate(input=input_data, timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Process timed out"

    def test_simulator_exists(self):
        """Test that the simulator binary exists."""
        # Just check that the binary exists
        assert SIMULATOR_PATH.exists(), "simulator-lc3 binary not found"

    def test_basic_invocation(self):
        """Test that the simulator can be invoked without arguments."""
        returncode, stdout, _ = self.run_simulator()

        # Should start in interactive mode without errors
        assert returncode == 0 or returncode == 130  # Normal exit or Ctrl+C
        assert "LC-3 Simulator v1.0" in stdout
        assert "Initializing..." in stdout
        assert "No program specified. Starting in interactive mode" in stdout

    def test_help_command(self):
        """Test that the help command works in interactive mode."""
        returncode, stdout, _ = self.run_simulator(input_data="help\nquit\n")

        assert returncode == 0
        assert "Available commands:" in stdout
        assert "step (s)" in stdout
        assert "run (r)" in stdout
        assert "quit (q)" in stdout

    def test_invalid_command(self):
        """Test that invalid commands are handled gracefully."""
        returncode, stdout, _ = self.run_simulator(input_data="invalid_command\nquit\n")

        assert returncode == 0
        assert "Unknown command" in stdout

    @pytest.fixture
    def sample_program_file(self, tmp_path):
        """Create a sample LC-3 program file for testing."""
        # This is a simple LC-3 program that adds 1 to R0 and halts
        # Origin: 0x3000
        # Instructions:
        # - ADD R0, R0, #1 (0x1020)
        # - HALT (0xF025)
        program_data = b"\x30\x00\x10\x20\xf0\x25"

        # Create a temporary file
        program_file = tmp_path / "test_program.obj"
        with open(program_file, "wb") as f:
            f.write(program_data)

        return program_file

    def test_load_program(self, sample_program_file):
        """Test loading a program from file."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file)],
        )

        assert returncode == 0
        assert "Loading program at address 0x3000" in stdout
        assert "Program loaded successfully" in stdout
        assert "Program execution completed" in stdout

    def test_interactive_mode_with_program(self, sample_program_file):
        """Test loading a program and entering interactive mode."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file), "-i"], input_data="reg\nquit\n"
        )

        assert returncode == 0
        assert "Loading program at address 0x3000" in stdout
        assert "Program loaded successfully" in stdout
        assert "LC-3 Simulator Interactive Mode" in stdout
        assert "=== LC-3 Simulator State ===" in stdout

    def test_step_command(self, sample_program_file):
        """Test the step command in interactive mode."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file), "-i"], input_data="step\nreg\nquit\n"
        )

        assert returncode == 0
        assert "LC-3 Simulator Interactive Mode" in stdout
        assert "=== LC-3 Simulator State ===" in stdout
        # After executing ADD R0, R0, #1, R0 should be 1
        assert "R0: 0x0001 (1)" in stdout

    def test_run_command(self, sample_program_file):
        """Test the run command in interactive mode."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file), "-i"], input_data="run\nquit\n"
        )

        assert returncode == 0
        assert "Running program..." in stdout
        assert "Program halted" in stdout
        assert "=== LC-3 Simulator State ===" in stdout

    def test_memory_command(self, sample_program_file):
        """Test the memory inspection command."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file), "-i"], input_data="mem 0x3000\nquit\n"
        )

        assert returncode == 0
        assert "Memory[0x3000] = 0x1020" in stdout

    def test_reset_command(self, sample_program_file):
        """Test the reset command."""
        returncode, stdout, _ = self.run_simulator(
            args=[str(sample_program_file), "-i"], input_data="step\nreset\nreg\nquit\n"
        )

        assert returncode == 0
        assert "Simulator reset" in stdout
        # After reset, PC should be back to 0x3000 and registers should be 0
        assert "PC: 0x3000" in stdout
        assert "R0: 0x0000 (0)" in stdout
