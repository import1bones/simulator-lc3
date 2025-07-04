"""
Test configuration and fixtures for LC-3 Simulator tests.
"""
import pytest
import sys
import os
from pathlib import Path

# Import test environment setup
from test_environment_setup import setup_test_environment, verify_test_environment

# Set up the test environment
setup_test_environment()

# Check if the simulator module is available
simulator_available = False
try:
    import lc3_simulator
    simulator_available = True
except ImportError as e:
    # More informative error message
    error_msg = (
        "LC-3 Simulator module not available. "
        "This usually means the C++ simulator hasn't been built yet.\n\n"
        "To build the simulator:\n"
        "1. Run: ./build.py build --python-bindings\n"
        "2. Or manually: cd build && cmake -DBUILD_PYTHON_BINDINGS=ON .. && cmake --build .\n\n"
        "In CI environments, ensure the build step runs before tests.\n"
        f"Import error: {e}"
    )
    
    # Skip all tests if running in pytest context
    pytest.skip(error_msg, allow_module_level=True)


@pytest.fixture
def simulator():
    """Create a fresh LC-3 simulator instance for each test."""
    sim = lc3_simulator.LC3Simulator()
    sim.reset()
    return sim


@pytest.fixture
def loaded_simulator():
    """Create a simulator with a simple test program loaded."""
    sim = lc3_simulator.LC3Simulator()
    sim.reset()

    # Simple test program: ADD R0, R0, #1; HALT
    program = [
        0x1021,  # ADD R0, R0, #1
        0xF025   # TRAP x25 (HALT)
    ]
    sim.load_program(program)
    return sim


@pytest.fixture
def sample_programs():
    """Dictionary of sample LC-3 programs for testing."""
    return {
        'simple_add': [
            0x1021,  # ADD R0, R0, #1
            0xF025   # TRAP x25 (HALT)
        ],
        'loop_counter': [
            0x2002,  # LD R0, DATA (PC-relative: when PC=0x3001, PC+offset=0x3001+2=0x3003, so data is at 0x3004)
            0x1021,  # ADD R0, R0, #1
            0x3001,  # ST R0, DATA (PC-relative: when PC=0x3002, PC+offset=0x3002+1=0x3003, so data is at 0x3004)
            0xF025,  # TRAP x25 (HALT)
            0x0005   # DATA: 5 (at address 0x3004)
        ],
        'conditional_branch': [
            0x5020,  # AND R0, R0, #0 (clear R0)
            0x1021,  # ADD R0, R0, #1
            0x0402,  # BRz +2 (should not branch)
            0x1021,  # ADD R0, R0, #1
            0xF025   # TRAP x25 (HALT)
        ],
        'subroutine_call': [
            0x4801,  # JSR SUBROUTINE (PC-relative: PC=0x3000, PC+1+1=0x3002, subroutine at 0x3002)
            0xF025,  # TRAP x25 (HALT)
            0x1021,  # SUBROUTINE: ADD R0, R0, #1 (at address 0x3002)
            0xC1C0   # RET (JMP R7) (at address 0x3003)
        ]
    }


@pytest.fixture
def instruction_encodings():
    """Dictionary of instruction encodings for testing."""
    return {
        'ADD_immediate': 0x1000 | (0 << 9) | (0 << 6) | 0x20 | 1,  # ADD R0, R0, #1
        'ADD_register': 0x1000 | (0 << 9) | (0 << 6) | 1,          # ADD R0, R0, R1
        'AND_immediate': 0x5000 | (0 << 9) | (0 << 6) | 0x20 | 0,  # AND R0, R0, #0
        'AND_register': 0x5000 | (0 << 9) | (0 << 6) | 1,          # AND R0, R0, R1
        'BR_unconditional': 0x0000 | 0x0E00 | 0,                   # BR #0
        'BRz': 0x0000 | 0x0400 | 0,                                # BRz #0
        'BRn': 0x0000 | 0x0800 | 0,                                # BRn #0
        'BRp': 0x0000 | 0x0200 | 0,                                # BRp #0
        'JMP': 0xC000 | (0 << 6),                                  # JMP R0
        'JSR': 0x4000 | 0x800 | 0,                                 # JSR #0
        'JSRR': 0x4000 | (0 << 6),                                 # JSRR R0
        'LD': 0x2000 | (0 << 9) | 0,                               # LD R0, #0
        'LDI': 0xA000 | (0 << 9) | 0,                              # LDI R0, #0
        'LDR': 0x6000 | (0 << 9) | (0 << 6) | 0,                   # LDR R0, R0, #0
        'LEA': 0xE000 | (0 << 9) | 0,                              # LEA R0, #0
        'NOT': 0x9000 | (0 << 9) | (0 << 6) | 0x3F,                # NOT R0, R0
        'ST': 0x3000 | (0 << 9) | 0,                               # ST R0, #0
        'STI': 0xB000 | (0 << 9) | 0,                              # STI R0, #0
        'STR': 0x7000 | (0 << 9) | (0 << 6) | 0,                   # STR R0, R0, #0
        'TRAP_HALT': 0xF000 | 0x25,                                # TRAP x25
        'TRAP_OUT': 0xF000 | 0x21,                                 # TRAP x21
        'TRAP_GETC': 0xF000 | 0x20,                                # TRAP x20
        'TRAP_PUTS': 0xF000 | 0x22,                                # TRAP x22
    }


@pytest.fixture(scope="session")
def build_simulator():
    """Build the simulator if it hasn't been built yet."""
    import subprocess
    import os

    # Check if build directory exists
    build_dir = os.path.join(os.path.dirname(__file__), '..', 'build')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # Run cmake and build
    try:
        subprocess.run(['cmake', '..'], cwd=build_dir, check=True)
        subprocess.run(['cmake', '--build', '.'], cwd=build_dir, check=True)
    except subprocess.CalledProcessError:
        pytest.skip("Failed to build LC-3 Simulator", allow_module_level=True)


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names."""
    for item in items:
        # Add markers based on test file names
        if "test_instructions" in item.nodeid:
            item.add_marker(pytest.mark.instruction)
        elif "test_memory" in item.nodeid:
            item.add_marker(pytest.mark.memory)
        elif "test_registers" in item.nodeid:
            item.add_marker(pytest.mark.register)
        elif "test_io" in item.nodeid:
            item.add_marker(pytest.mark.io)
        elif "test_trap" in item.nodeid:
            item.add_marker(pytest.mark.trap)

        # Add unit/integration markers based on test names
        if item.name.startswith("test_unit"):
            item.add_marker(pytest.mark.unit)
        elif item.name.startswith("test_integration"):
            item.add_marker(pytest.mark.integration)
        elif item.name.startswith("test_functional"):
            item.add_marker(pytest.mark.functional)

        # Mark slow tests
        if "slow" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)
