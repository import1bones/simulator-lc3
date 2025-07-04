"""
Test Memory implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

"""
Tests for memory management and memory-related functionality.
"""
import pytest


class TestMemoryBasics:
    """Test basic memory operations."""
    
    def test_memory_initialization(self, simulator):
        """Test that memory is properly initialized."""
        # Check various memory locations are zero
        test_addresses = [0x0000, 0x3000, 0x8000, 0xFFFF]
        
        for addr in test_addresses:
            assert simulator.get_memory(addr) == 0
    
    def test_memory_write_read(self, simulator):
        """Test basic memory write and read operations."""
        test_cases = [
            (0x3000, 0x1234),
            (0x3001, 0xABCD),
            (0x8000, 0x0000),
            (0xFFFF, 0xFFFF)
        ]
        
        for addr, value in test_cases:
            simulator.set_memory(addr, value)
            assert simulator.get_memory(addr) == value
    
    def test_memory_isolation(self, simulator):
        """Test that memory locations are isolated."""
        # Write to adjacent memory locations
        simulator.set_memory(0x3000, 0x1111)
        simulator.set_memory(0x3001, 0x2222)
        simulator.set_memory(0x3002, 0x3333)
        
        # Verify each location has correct value
        assert simulator.get_memory(0x3000) == 0x1111
        assert simulator.get_memory(0x3001) == 0x2222
        assert simulator.get_memory(0x3002) == 0x3333
    
    def test_memory_boundary_values(self, simulator):
        """Test memory with boundary values."""
        boundary_values = [0x0000, 0x0001, 0x7FFF, 0x8000, 0xFFFE, 0xFFFF]
        
        for i, value in enumerate(boundary_values):
            addr = 0x3000 + i
            simulator.set_memory(addr, value)
            assert simulator.get_memory(addr) == value


class TestMemoryAddressing:
    """Test different memory addressing modes."""
    
    def test_pc_relative_addressing(self, simulator):
        """Test PC-relative addressing calculations."""
        # LD R0, #5 (PC-relative)
        instruction = 0x2000 | (0 << 9) | 5
        
        simulator.set_pc(0x3000)
        simulator.set_memory(0x3000, instruction)
        simulator.set_memory(0x3006, 0x1234)  # PC + 1 + 5
        
        simulator.step()
        assert simulator.get_register(0) == 0x1234
    
    def test_indirect_addressing(self, simulator):
        """Test indirect addressing."""
        # LDI R0, #3 (indirect addressing)
        instruction = 0xA000 | (0 << 9) | 3
        
        simulator.set_pc(0x3000)
        simulator.set_memory(0x3000, instruction)
        simulator.set_memory(0x3004, 0x4000)  # Pointer at PC + 1 + 3
        simulator.set_memory(0x4000, 0x5678)  # Actual data
        
        simulator.step()
        assert simulator.get_register(0) == 0x5678
    
    def test_base_plus_offset_addressing(self, simulator):
        """Test base + offset addressing."""
        # LDR R0, R1, #10
        instruction = 0x6000 | (0 << 9) | (1 << 6) | 10
        
        simulator.set_register(1, 0x4000)      # Base address
        simulator.set_memory(0x4000 + 10, 0x9ABC)  # Data at base + offset
        simulator.set_memory(0x3000, instruction)
        
        simulator.step()
        assert simulator.get_register(0) == 0x9ABC
    
    def test_negative_offset_addressing(self, simulator):
        """Test addressing with negative offsets."""
        # LDR R0, R1, #-5 (negative offset)
        # In 6-bit 2's complement, -5 is 0x3B (63 - 5 + 1)
        instruction = 0x6000 | (0 << 9) | (1 << 6) | 0x3B
        
        simulator.set_register(1, 0x4010)      # Base address
        simulator.set_memory(0x4010 - 5, 0xDEAD)   # Data at base - 5
        simulator.set_memory(0x3000, instruction)
        
        simulator.step()
        assert simulator.get_register(0) == 0xDEAD


class TestMemoryProtection:
    """Test memory protection and access validation."""
    
    def test_user_space_access(self, simulator):
        """Test access to user space memory."""
        # User space should be accessible
        user_addresses = [0x3000, 0x4000, 0x8000, 0xFDFF]
        
        for addr in user_addresses:
            simulator.set_memory(addr, 0x1234)
            assert simulator.get_memory(addr) == 0x1234
    
    def test_device_register_space(self, simulator):
        """Test access to device register space."""
        # Device registers should be accessible
        device_addresses = [0xFE00, 0xFE02, 0xFE04, 0xFE06, 0xFFFC, 0xFFFE]
        
        for addr in device_addresses:
            simulator.set_memory(addr, 0x5678)
            assert simulator.get_memory(addr) == 0x5678


class TestMemoryPatterns:
    """Test memory with various data patterns."""
    
    def test_alternating_pattern(self, simulator):
        """Test memory with alternating bit pattern."""
        pattern = 0xAAAA
        
        for addr in range(0x3000, 0x3010):
            simulator.set_memory(addr, pattern)
            assert simulator.get_memory(addr) == pattern
            pattern = ~pattern & 0xFFFF  # Flip all bits
    
    def test_sequential_pattern(self, simulator):
        """Test memory with sequential pattern."""
        base_addr = 0x3000
        
        for i in range(100):
            addr = base_addr + i
            value = i & 0xFFFF
            simulator.set_memory(addr, value)
            assert simulator.get_memory(addr) == value
    
    def test_random_pattern(self, simulator):
        """Test memory with pseudo-random pattern."""
        import random
        random.seed(42)  # For reproducible tests
        
        test_data = []
        for i in range(50):
            addr = 0x3000 + i
            value = random.randint(0, 0xFFFF)
            test_data.append((addr, value))
            simulator.set_memory(addr, value)
        
        # Verify all values
        for addr, expected_value in test_data:
            assert simulator.get_memory(addr) == expected_value


class TestMemoryInstructions:
    """Test memory-related instructions in detail."""
    
    def test_load_store_cycle(self, simulator):
        """Test loading and storing data."""
        # Store a value, then load it back
        original_value = 0x1234
        
        # ST R0, #5
        simulator.set_register(0, original_value)
        store_instruction = 0x3000 | (0 << 9) | 5
        simulator.set_memory(0x3000, store_instruction)
        simulator.step()
        
        # Clear register
        simulator.set_register(0, 0)
        
        # LD R0, #5 (load from same location)
        load_instruction = 0x2000 | (0 << 9) | 5
        simulator.set_memory(0x3001, load_instruction)
        simulator.set_pc(0x3001)
        simulator.step()
        
        assert simulator.get_register(0) == original_value
    
    def test_indirect_load_store(self, simulator):
        """Test indirect load and store operations."""
        test_value = 0xBEEF
        pointer_addr = 0x4000
        data_addr = 0x5000
        
        # Set up pointer
        simulator.set_memory(pointer_addr, data_addr)
        
        # STI R0, #offset (store indirectly)
        simulator.set_register(0, test_value)
        offset = pointer_addr - (0x3000 + 1)  # Calculate offset to pointer
        sti_instruction = 0xB000 | (0 << 9) | (offset & 0x1FF)
        simulator.set_memory(0x3000, sti_instruction)
        simulator.step()
        
        # Verify data was stored at final location
        assert simulator.get_memory(data_addr) == test_value
        
        # Clear register and load indirectly
        simulator.set_register(0, 0)
        ldi_instruction = 0xA000 | (0 << 9) | (offset & 0x1FF)
        simulator.set_memory(0x3001, ldi_instruction)
        simulator.set_pc(0x3001)
        simulator.step()
        
        assert simulator.get_register(0) == test_value
    
    def test_lea_instruction(self, simulator):
        """Test LEA (Load Effective Address) instruction."""
        # LEA R0, #20
        instruction = 0xE000 | (0 << 9) | 20
        
        simulator.set_pc(0x3000)
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        # R0 should contain the calculated address
        expected_addr = 0x3001 + 20  # PC after increment + offset
        assert simulator.get_register(0) == expected_addr
        
        # Condition codes should be set based on the address
        n, z, p = simulator.get_condition_codes()
        if expected_addr == 0:
            assert z == 1
        elif expected_addr & 0x8000:
            assert n == 1
        else:
            assert p == 1


class TestMemoryEdgeCases:
    """Test edge cases and boundary conditions for memory."""
    
    def test_memory_wrap_around(self, simulator):
        """Test behavior at memory boundaries."""
        # Test highest address
        simulator.set_memory(0xFFFF, 0x1234)
        assert simulator.get_memory(0xFFFF) == 0x1234
        
        # Test lowest address
        simulator.set_memory(0x0000, 0x5678)
        assert simulator.get_memory(0x0000) == 0x5678
    
    def test_pc_relative_boundary(self, simulator):
        """Test PC-relative addressing at boundaries."""
        # Test maximum positive offset
        max_offset = 0xFF  # 9-bit positive max
        
        simulator.set_pc(0x3000)
        target_addr = 0x3001 + max_offset
        simulator.set_memory(target_addr, 0xABCD)
        
        # LD R0, #max_offset
        instruction = 0x2000 | (0 << 9) | max_offset
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0xABCD
    
    def test_register_offset_boundary(self, simulator):
        """Test base+offset addressing at boundaries."""
        # Test maximum positive offset (6-bit)
        max_offset = 0x1F  # 6-bit positive max
        
        simulator.set_register(1, 0x4000)
        simulator.set_memory(0x4000 + max_offset, 0xDCBA)
        
        # LDR R0, R1, #max_offset
        instruction = 0x6000 | (0 << 9) | (1 << 6) | max_offset
        simulator.set_memory(0x3000, instruction)
        simulator.step()
        
        assert simulator.get_register(0) == 0xDCBA
