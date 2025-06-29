#!/usr/bin/env python3
"""
LC-3 ISA Performance Test Suite

This module provides comprehensive performance testing for the LC-3 instruction set architecture.
It measures execution time, throughput, and efficiency for all LC-3 instructions and instruction patterns.
"""

import time
import statistics
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pytest

try:
    import lc3_simulator
except ImportError:
    print("Warning: lc3_simulator module not available. Skipping performance tests.")
    lc3_simulator = None


class ISAPerformanceProfiler:
    """Performance profiler for LC-3 ISA operations."""
    
    def __init__(self):
        self.results = {}
        self.simulator = None
        
    def setup_simulator(self):
        """Initialize a fresh simulator instance."""
        if lc3_simulator is None:
            return None
        self.simulator = lc3_simulator.LC3Simulator()
        self.simulator.reset()
        return self.simulator
    
    def measure_execution_time(self, test_func, iterations=1000):
        """Measure execution time of a test function over multiple iterations."""
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            test_func()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            
        return {
            'mean_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'min_time': min(times),
            'max_time': max(times),
            'total_time': sum(times),
            'iterations': iterations
        }
    
    def test_arithmetic_instructions(self, iterations=1000):
        """Performance test for arithmetic instructions (ADD, AND, NOT)."""
        if not self.setup_simulator():
            return None
            
        def test_add_immediate():
            self.simulator.reset()
            self.simulator.set_register(0, 5)
            # ADD R0, R0, #1
            instruction = 0x1021
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_add_register():
            self.simulator.reset()
            self.simulator.set_register(0, 5)
            self.simulator.set_register(1, 3)
            # ADD R0, R0, R1
            instruction = 0x1001
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_and_immediate():
            self.simulator.reset()
            self.simulator.set_register(0, 0xFF)
            # AND R0, R0, #15
            instruction = 0x502F
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_not_instruction():
            self.simulator.reset()
            self.simulator.set_register(0, 0x5555)
            # NOT R0, R0
            instruction = 0x903F
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
        
        return {
            'ADD_immediate': self.measure_execution_time(test_add_immediate, iterations),
            'ADD_register': self.measure_execution_time(test_add_register, iterations),
            'AND_immediate': self.measure_execution_time(test_and_immediate, iterations),
            'NOT': self.measure_execution_time(test_not_instruction, iterations)
        }
    
    def test_memory_instructions(self, iterations=1000):
        """Performance test for memory instructions (LD, ST, LDR, STR, LDI, STI, LEA)."""
        if not self.setup_simulator():
            return None
            
        def test_ld_instruction():
            self.simulator.reset()
            self.simulator.set_memory(0x3005, 0x1234)
            # LD R0, #5
            instruction = 0x2005
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_st_instruction():
            self.simulator.reset()
            self.simulator.set_register(0, 0x5678)
            # ST R0, #5
            instruction = 0x3005
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_ldr_instruction():
            self.simulator.reset()
            self.simulator.set_register(1, 0x4000)
            self.simulator.set_memory(0x4005, 0xABCD)
            # LDR R0, R1, #5
            instruction = 0x6045
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_str_instruction():
            self.simulator.reset()
            self.simulator.set_register(0, 0xDEAD)
            self.simulator.set_register(1, 0x4000)
            # STR R0, R1, #5
            instruction = 0x7045
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_lea_instruction():
            self.simulator.reset()
            # LEA R0, #10
            instruction = 0xE00A
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        return {
            'LD': self.measure_execution_time(test_ld_instruction, iterations),
            'ST': self.measure_execution_time(test_st_instruction, iterations),
            'LDR': self.measure_execution_time(test_ldr_instruction, iterations),
            'STR': self.measure_execution_time(test_str_instruction, iterations),
            'LEA': self.measure_execution_time(test_lea_instruction, iterations)
        }
    
    def test_control_flow_instructions(self, iterations=1000):
        """Performance test for control flow instructions (BR, JMP, JSR, RET)."""
        if not self.setup_simulator():
            return None
            
        def test_branch_taken():
            self.simulator.reset()
            self.simulator.set_register(0, 1)  # Positive value
            # ADD R0, R0, #0 to set condition codes
            self.simulator.set_memory(0x3000, 0x1020)
            self.simulator.step()
            # BRp #2
            instruction = 0x0202
            self.simulator.set_memory(0x3001, instruction)
            self.simulator.set_pc(0x3001)
            self.simulator.step()
            
        def test_branch_not_taken():
            self.simulator.reset()
            self.simulator.set_register(0, 0)  # Zero value
            # ADD R0, R0, #0 to set condition codes
            self.simulator.set_memory(0x3000, 0x1020)
            self.simulator.step()
            # BRp #2
            instruction = 0x0202
            self.simulator.set_memory(0x3001, instruction)
            self.simulator.set_pc(0x3001)
            self.simulator.step()
            
        def test_jmp_instruction():
            self.simulator.reset()
            self.simulator.set_register(1, 0x4000)
            # JMP R1
            instruction = 0xC040
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_jsr_instruction():
            self.simulator.reset()
            # JSR #5
            instruction = 0x4805
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
        
        return {
            'BR_taken': self.measure_execution_time(test_branch_taken, iterations),
            'BR_not_taken': self.measure_execution_time(test_branch_not_taken, iterations),
            'JMP': self.measure_execution_time(test_jmp_instruction, iterations),
            'JSR': self.measure_execution_time(test_jsr_instruction, iterations)
        }
    
    def test_trap_instructions(self, iterations=500):
        """Performance test for TRAP instructions."""
        if not self.setup_simulator():
            return None
            
        def test_halt_trap():
            self.simulator.reset()
            # TRAP x25 (HALT)
            instruction = 0xF025
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
            
        def test_out_trap():
            self.simulator.reset()
            self.simulator.set_register(0, ord('A'))
            # TRAP x21 (OUT)
            instruction = 0xF021
            self.simulator.set_memory(0x3000, instruction)
            self.simulator.step()
        
        return {
            'HALT': self.measure_execution_time(test_halt_trap, iterations),
            'OUT': self.measure_execution_time(test_out_trap, iterations)
        }
    
    def test_instruction_throughput(self, num_instructions=10000):
        """Test overall instruction throughput."""
        if not self.setup_simulator():
            return None
            
        # Create a program with mixed instructions
        program = []
        for i in range(num_instructions):
            if i % 4 == 0:
                program.append(0x1021)  # ADD R0, R0, #1
            elif i % 4 == 1:
                program.append(0x5020)  # AND R0, R0, #0
            elif i % 4 == 2:
                program.append(0x1021)  # ADD R0, R0, #1
            else:
                program.append(0x903F)  # NOT R0, R0
        
        program.append(0xF025)  # HALT
        
        self.simulator.reset()
        self.simulator.load_program(program)
        
        start_time = time.perf_counter()
        self.simulator.run(max_cycles=num_instructions + 100)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        instructions_per_second = num_instructions / execution_time if execution_time > 0 else 0
        
        return {
            'total_instructions': num_instructions,
            'execution_time': execution_time,
            'instructions_per_second': instructions_per_second,
            'cycles_per_instruction': execution_time / num_instructions if num_instructions > 0 else 0
        }
    
    def test_memory_access_patterns(self, iterations=1000):
        """Test different memory access patterns."""
        if not self.setup_simulator():
            return None
            
        def test_sequential_access():
            self.simulator.reset()
            # Sequential memory reads
            for i in range(10):
                self.simulator.set_memory(0x4000 + i, i)
                self.simulator.set_register(1, 0x4000 + i)
                # LDR R0, R1, #0
                instruction = 0x6040
                self.simulator.set_memory(0x3000, instruction)
                self.simulator.step()
                self.simulator.reset()
                
        def test_random_access():
            self.simulator.reset()
            addresses = [0x4000, 0x5000, 0x4500, 0x6000, 0x4800]
            for addr in addresses:
                self.simulator.set_memory(addr, 0x1234)
                self.simulator.set_register(1, addr)
                # LDR R0, R1, #0
                instruction = 0x6040
                self.simulator.set_memory(0x3000, instruction)
                self.simulator.step()
                self.simulator.reset()
        
        return {
            'sequential_access': self.measure_execution_time(test_sequential_access, iterations // 10),
            'random_access': self.measure_execution_time(test_random_access, iterations // 10)
        }
    
    def run_comprehensive_performance_test(self):
        """Run all performance tests and return comprehensive results."""
        print("Starting LC-3 ISA Performance Test Suite...")
        
        results = {
            'test_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'simulator_available': lc3_simulator is not None
            }
        }
        
        if lc3_simulator is None:
            results['error'] = 'lc3_simulator module not available'
            return results
        
        # Run all test categories
        print("Testing arithmetic instructions...")
        results['arithmetic_instructions'] = self.test_arithmetic_instructions()
        
        print("Testing memory instructions...")
        results['memory_instructions'] = self.test_memory_instructions()
        
        print("Testing control flow instructions...")
        results['control_flow_instructions'] = self.test_control_flow_instructions()
        
        print("Testing TRAP instructions...")
        results['trap_instructions'] = self.test_trap_instructions()
        
        print("Testing instruction throughput...")
        results['throughput'] = self.test_instruction_throughput()
        
        print("Testing memory access patterns...")
        results['memory_patterns'] = self.test_memory_access_patterns()
        
        # Calculate summary statistics
        results['summary'] = self.calculate_summary_stats(results)
        
        return results
    
    def calculate_summary_stats(self, results):
        """Calculate summary statistics from test results."""
        summary = {
            'fastest_instruction': None,
            'slowest_instruction': None,
            'average_instruction_time': 0,
            'total_tests_run': 0
        }
        
        all_times = []
        instruction_times = {}
        
        # Collect all instruction times
        for category, tests in results.items():
            if isinstance(tests, dict) and category not in ['test_info', 'throughput', 'summary']:
                for instruction, timing_data in tests.items():
                    if isinstance(timing_data, dict) and 'mean_time' in timing_data:
                        mean_time = timing_data['mean_time']
                        all_times.append(mean_time)
                        instruction_times[f"{category}_{instruction}"] = mean_time
                        summary['total_tests_run'] += 1
        
        if all_times:
            summary['average_instruction_time'] = statistics.mean(all_times)
            
            # Find fastest and slowest
            min_time = min(instruction_times.values())
            max_time = max(instruction_times.values())
            
            for instr, time_val in instruction_times.items():
                if time_val == min_time:
                    summary['fastest_instruction'] = {'name': instr, 'time': time_val}
                if time_val == max_time:
                    summary['slowest_instruction'] = {'name': instr, 'time': time_val}
        
        return summary


@pytest.mark.performance
class TestISAPerformance:
    """Pytest class for ISA performance tests."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.profiler = ISAPerformanceProfiler()
    
    @pytest.mark.skipif(lc3_simulator is None, reason="lc3_simulator not available")
    def test_arithmetic_performance(self):
        """Test arithmetic instruction performance."""
        results = self.profiler.test_arithmetic_instructions()
        assert results is not None
        
        # Verify that ADD immediate is reasonably fast (< 1ms average)
        assert results['ADD_immediate']['mean_time'] < 0.001
        
        # Verify that all arithmetic operations complete
        for instruction, timing in results.items():
            assert timing['iterations'] > 0
            assert timing['mean_time'] > 0
    
    @pytest.mark.skipif(lc3_simulator is None, reason="lc3_simulator not available")
    def test_memory_performance(self):
        """Test memory instruction performance."""
        results = self.profiler.test_memory_instructions()
        assert results is not None
        
        # Memory operations should be reasonably fast
        for instruction, timing in results.items():
            assert timing['mean_time'] < 0.002  # Less than 2ms average
            assert timing['iterations'] > 0
    
    @pytest.mark.skipif(lc3_simulator is None, reason="lc3_simulator not available")
    def test_control_flow_performance(self):
        """Test control flow instruction performance."""
        results = self.profiler.test_control_flow_instructions()
        assert results is not None
        
        # Control flow should be fast
        for instruction, timing in results.items():
            assert timing['mean_time'] < 0.001
            assert timing['iterations'] > 0
    
    @pytest.mark.skipif(lc3_simulator is None, reason="lc3_simulator not available")
    def test_overall_throughput(self):
        """Test overall instruction throughput."""
        results = self.profiler.test_instruction_throughput()
        assert results is not None
        
        # Should achieve reasonable throughput (> 1000 instructions/second)
        assert results['instructions_per_second'] > 1000
        assert results['execution_time'] > 0


def generate_performance_report(results: Dict, output_file: str = None):
    """Generate a detailed performance report."""
    if output_file is None:
        output_file = f"reports/isa_performance_report_{int(time.time())}.md"
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# LC-3 ISA Performance Test Report\n\n")
        
        # Test Information
        f.write("## Test Information\n\n")
        if 'test_info' in results:
            f.write(f"**Generated**: {results['test_info']['timestamp']}\n")
            f.write(f"**Simulator Available**: {results['test_info']['simulator_available']}\n\n")
        
        if 'error' in results:
            f.write(f"**Error**: {results['error']}\n\n")
            return output_file
        
        # Summary
        if 'summary' in results:
            summary = results['summary']
            f.write("## Executive Summary\n\n")
            f.write(f"**Total Tests Run**: {summary['total_tests_run']}\n")
            f.write(f"**Average Instruction Time**: {summary['average_instruction_time']:.6f} seconds\n")
            
            if summary['fastest_instruction']:
                f.write(f"**Fastest Instruction**: {summary['fastest_instruction']['name']} ({summary['fastest_instruction']['time']:.6f}s)\n")
            
            if summary['slowest_instruction']:
                f.write(f"**Slowest Instruction**: {summary['slowest_instruction']['name']} ({summary['slowest_instruction']['time']:.6f}s)\n")
            
            f.write("\n")
        
        # Throughput Results
        if 'throughput' in results:
            throughput = results['throughput']
            f.write("## Overall Throughput\n\n")
            f.write(f"**Instructions Executed**: {throughput['total_instructions']}\n")
            f.write(f"**Total Execution Time**: {throughput['execution_time']:.6f} seconds\n")
            f.write(f"**Instructions per Second**: {throughput['instructions_per_second']:.0f}\n")
            f.write(f"**Cycles per Instruction**: {throughput['cycles_per_instruction']:.6f}\n\n")
        
        # Detailed Results by Category
        categories = ['arithmetic_instructions', 'memory_instructions', 'control_flow_instructions', 'trap_instructions']
        
        for category in categories:
            if category in results and results[category]:
                category_name = category.replace('_', ' ').title()
                f.write(f"## {category_name}\n\n")
                f.write("| Instruction | Mean Time (μs) | Median Time (μs) | Std Dev (μs) | Min Time (μs) | Max Time (μs) |\n")
                f.write("|-------------|---------------|-----------------|-------------|--------------|-------------|\n")
                
                for instruction, timing in results[category].items():
                    if isinstance(timing, dict):
                        f.write(f"| **{instruction}** | {timing['mean_time']*1e6:.2f} | "
                               f"{timing['median_time']*1e6:.2f} | {timing['std_dev']*1e6:.2f} | "
                               f"{timing['min_time']*1e6:.2f} | {timing['max_time']*1e6:.2f} |\n")
                
                f.write("\n")
        
        # Memory Access Patterns
        if 'memory_patterns' in results:
            f.write("## Memory Access Patterns\n\n")
            patterns = results['memory_patterns']
            f.write("| Pattern | Mean Time (μs) | Relative Performance |\n")
            f.write("|---------|---------------|--------------------|\n")
            
            sequential = patterns.get('sequential_access', {}).get('mean_time', 0)
            random = patterns.get('random_access', {}).get('mean_time', 0)
            
            f.write(f"| Sequential Access | {sequential*1e6:.2f} | Baseline |\n")
            if sequential > 0:
                ratio = random / sequential
                f.write(f"| Random Access | {random*1e6:.2f} | {ratio:.2f}x slower |\n")
            
            f.write("\n")
        
        # Performance Analysis
        f.write("## Performance Analysis\n\n")
        f.write("### Key Findings\n\n")
        
        if 'summary' in results:
            avg_time = results['summary']['average_instruction_time']
            if avg_time < 0.0001:
                f.write("✅ **Excellent Performance**: Average instruction time < 100μs\n")
            elif avg_time < 0.001:
                f.write("✅ **Good Performance**: Average instruction time < 1ms\n")
            else:
                f.write("⚠️ **Moderate Performance**: Average instruction time > 1ms\n")
        
        if 'throughput' in results:
            ips = results['throughput']['instructions_per_second']
            if ips > 10000:
                f.write("✅ **High Throughput**: > 10,000 instructions/second\n")
            elif ips > 1000:
                f.write("✅ **Good Throughput**: > 1,000 instructions/second\n")
            else:
                f.write("⚠️ **Low Throughput**: < 1,000 instructions/second\n")
        
        f.write("\n### Recommendations\n\n")
        f.write("1. **Optimization Opportunities**: Focus on slowest instructions\n")
        f.write("2. **Memory Access**: Sequential access patterns show best performance\n")
        f.write("3. **Instruction Mix**: Balance computation vs. memory operations\n")
        f.write("4. **Cache Efficiency**: Consider instruction and data locality\n")
    
    return output_file


if __name__ == "__main__":
    # Run performance tests when executed directly
    profiler = ISAPerformanceProfiler()
    results = profiler.run_comprehensive_performance_test()
    
    # Generate report
    report_file = generate_performance_report(results)
    print(f"\nPerformance test completed!")
    print(f"Report generated: {report_file}")
    
    # Save raw results as JSON
    json_file = report_file.replace('.md', '.json')
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw data saved: {json_file}")
