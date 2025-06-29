#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
sys.path.append('./build/python_bindings')

try:
    import lc3_simulator
    
    simulator = lc3_simulator.LC3Simulator()
    
    # Load the loop_counter program
    program = [0x2001, 0x1021, 0x3001, 0xF025, 0x0005]
    simulator.load_program(program)
    
    print("Program loaded. Initial state:")
    print(f"PC: 0x{simulator.get_pc():04X}")
    print(f"R0: 0x{simulator.get_register(0):04X}")
    print(f"Memory at 0x3004 (DATA): 0x{simulator.get_memory(0x3004):04X}")
    print(f"Memory at 0x3002: 0x{simulator.get_memory(0x3002):04X}")
    print()
    
    # Step through each instruction
    for i in range(4):
        print(f"Step {i+1}:")
        print(f"  Before: PC=0x{simulator.get_pc():04X}, R0=0x{simulator.get_register(0):04X}")
        simulator.step()
        print(f"  After:  PC=0x{simulator.get_pc():04X}, R0=0x{simulator.get_register(0):04X}")
        print(f"  Halted: {simulator.is_halted()}")
        print()
        
        if simulator.is_halted():
            break
    
    print("Final state:")
    print(f"PC: 0x{simulator.get_pc():04X}")
    print(f"R0: 0x{simulator.get_register(0):04X}")
    print(f"Memory at 0x3004 (DATA): 0x{simulator.get_memory(0x3004):04X}")
    print(f"Halted: {simulator.is_halted()}")
    
except ImportError as e:
    print(f"Error importing lc3_simulator: {e}")
    print("Make sure the Python bindings are built.")
