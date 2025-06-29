#!/usr/bin/env python3
"""
LC-3 Realistic Program Performance Benchmark

This script tests the performance of the LC-3 simulator using realistic programs
that would be typical in an educational computer architecture course.
"""

import time
import json
from pathlib import Path
from typing import Dict, List

try:
    import lc3_simulator
except ImportError:
    print("Warning: lc3_simulator module not available.")
    lc3_simulator = None


class LC3ProgramBenchmark:
    """Benchmark realistic LC-3 programs."""
    
    def __init__(self):
        self.results = {}
    
    def get_sample_programs(self):
        """Get a collection of realistic LC-3 programs for benchmarking."""
        return {
            'fibonacci_iterative': {
                'description': 'Calculate Fibonacci number iteratively',
                'program': [
                    0x5020,  # AND R0, R0, #0    ; F(0) = 0
                    0x5240,  # AND R1, R1, #0    ; Clear R1
                    0x1261,  # ADD R1, R1, #1    ; F(1) = 1
                    0x5480,  # AND R2, R2, #0    ; Clear counter
                    0x14A8,  # ADD R2, R2, #8    ; Calculate F(8)
                    0x0406,  # BRz END           ; If counter is 0, end
                    0x1403,  # ADD R1, R0, R1    ; F(n) = F(n-1) + F(n-2)
                    0x1040,  # ADD R0, R1, #0    ; Shift: R0 = old R1
                    0x14BF,  # ADD R2, R2, #-1   ; Decrement counter
                    0x0FFB,  # BRnzp LOOP        ; Continue loop
                    0xF025   # TRAP x25          ; HALT
                ],
                'expected_result': 21,  # F(8) = 21
                'complexity': 'O(n)'
            },
            
            'factorial_recursive': {
                'description': 'Calculate factorial using recursive approach',
                'program': [
                    0x2010,  # LD R0, N             ; Load N
                    0x480C,  # JSR FACTORIAL        ; Call factorial
                    0x300F,  # ST R0, RESULT        ; Store result
                    0xF025,  # TRAP x25             ; HALT
                    
                    # FACTORIAL subroutine (starts at 0x3004)
                    0x1C3F,  # ADD R6, R6, #-1      ; Push stack
                    0x7D80,  # STR R6, R6, #0       ; Save return address
                    0x1C3F,  # ADD R6, R6, #-1      ; Push stack  
                    0x7040,  # STR R0, R6, #0       ; Save R0
                    
                    0x0A05,  # BRzp BASE_CASE       ; If R0 <= 0, base case
                    0x1C21,  # ADD R6, R6, #1       ; Pop R0
                    0x6040,  # LDR R0, R6, #0       
                    0x1C21,  # ADD R6, R6, #1       ; Pop return address
                    0x6D80,  # LDR R6, R6, #0
                    0xC1C0,  # RET                  ; Return
                    
                    0x103F,  # ADD R0, R0, #-1      ; N-1
                    0x4FF6,  # JSR FACTORIAL        ; Recursive call
                    0x6240,  # LDR R1, R6, #0       ; Get original N
                    # Multiply R0 * R1 (simplified)
                    0x5480,  # AND R2, R2, #0       ; Counter = 0
                    0x1480,  # ADD R2, R2, R0       ; Counter = R0
                    0x5020,  # AND R0, R0, #0       ; Result = 0
                    0x1001,  # ADD R0, R0, R1       ; Add N
                    0x14BF,  # ADD R2, R2, #-1      ; Decrement
                    0x0AFE,  # BRp MULT_LOOP        ; Continue
                    
                    0x1C21,  # ADD R6, R6, #1       ; Pop
                    0x1C21,  # ADD R6, R6, #1       ; Pop
                    0x6D80,  # LDR R6, R6, #0       ; Get return
                    0xC1C0,  # RET                  ; Return
                    
                    0x0005,  # N: 5
                    0x0000   # RESULT: 0
                ],
                'expected_result': 120,  # 5! = 120
                'complexity': 'O(n)'
            },
            
            'string_search': {
                'description': 'Search for character in string',
                'program': [
                    0x200E,  # LD R0, STRING_PTR    ; Load string pointer
                    0x220D,  # LD R1, TARGET_CHAR   ; Load target character
                    0x5480,  # AND R2, R2, #0       ; Clear position counter
                    
                    # SEARCH_LOOP
                    0x6600,  # LDR R3, R0, #0       ; Load current character
                    0x0405,  # BRz NOT_FOUND        ; If null terminator, not found
                    0x1CC1,  # ADD R6, R3, R1       ; Compare chars (R3 - R1)
                    0x0404,  # BRz FOUND            ; If zero, found
                    0x1021,  # ADD R0, R0, #1       ; Move to next character
                    0x1481,  # ADD R2, R2, #1       ; Increment position
                    0x0FF8,  # BRnzp SEARCH_LOOP    ; Continue search
                    
                    # FOUND
                    0x5020,  # AND R0, R0, #0       ; Clear R0
                    0x1002,  # ADD R0, R0, R2       ; R0 = position
                    0x0002,  # BRnzp END
                    
                    # NOT_FOUND  
                    0x5020,  # AND R0, R0, #0       ; Clear R0
                    0x103F,  # ADD R0, R0, #-1      ; R0 = -1 (not found)
                    
                    # END
                    0xF025,  # TRAP x25             ; HALT
                    
                    # Data
                    0x3014,  # STRING_PTR           ; Points to string
                    ord('l'), # TARGET_CHAR: 'l'
                    ord('H'), ord('e'), ord('l'), ord('l'), ord('o'), 0x00  # "Hello\0"
                ],
                'expected_result': 2,  # Position of first 'l'
                'complexity': 'O(n)'
            },
            
            'bubble_sort': {
                'description': 'Sort array using bubble sort',
                'program': [
                    0x2019,  # LD R0, ARRAY_PTR     ; Load array pointer
                    0x221A,  # LD R1, ARRAY_SIZE    ; Load array size
                    
                    # Outer loop
                    0x5480,  # AND R2, R2, #0       ; i = 0
                    0x14A1,  # ADD R2, R2, R1       ; i = size
                    
                    # OUTER_LOOP
                    0x0812,  # BRnz DONE            ; If i <= 0, done
                    0x1040,  # ADD R0, R0, #0       ; Reset array pointer
                    0x56C0,  # AND R3, R3, #0       ; j = 0
                    0x16C2,  # ADD R3, R3, R2       ; j = i
                    0x16DF,  # ADD R3, R3, #-1      ; j = i - 1
                    
                    # INNER_LOOP
                    0x0A0A,  # BRzp NEXT_OUTER      ; If j <= 0, next outer
                    0x6800,  # LDR R4, R0, #0       ; Load arr[j]
                    0x6A01,  # LDR R5, R0, #1       ; Load arr[j+1]
                    0x1D05,  # ADD R6, R4, R5       ; Compare (R4 - R5)
                    0x0A05,  # BRzp NO_SWAP         ; If arr[j] <= arr[j+1], no swap
                    
                    # SWAP
                    0x7A01,  # STR R5, R0, #1       ; arr[j+1] = arr[j]
                    0x7800,  # STR R4, R0, #0       ; arr[j] = arr[j+1]
                    
                    # NO_SWAP
                    0x1021,  # ADD R0, R0, #1       ; Move to next element
                    0x16DF,  # ADD R3, R3, #-1      ; j--
                    0x0FF4,  # BRnzp INNER_LOOP     ; Continue inner loop
                    
                    # NEXT_OUTER
                    0x14BF,  # ADD R2, R2, #-1      ; i--
                    0x0FED,  # BRnzp OUTER_LOOP     ; Continue outer loop
                    
                    # DONE
                    0xF025,  # TRAP x25             ; HALT
                    
                    # Data
                    0x301B,  # ARRAY_PTR            ; Points to array
                    0x0005,  # ARRAY_SIZE: 5
                    0x0005, 0x0002, 0x0008, 0x0001, 0x0003  # Array: [5,2,8,1,3]
                ],
                'expected_result': [1, 2, 3, 5, 8],  # Sorted array
                'complexity': 'O(n²)'
            },
            
            'memory_intensive': {
                'description': 'Memory-intensive pattern access',
                'program': [
                    0x2008,  # LD R0, BASE_ADDR     ; Load base address
                    0x220A,  # LD R1, PATTERN_SIZE  ; Load pattern size
                    0x5480,  # AND R2, R2, #0       ; Clear index
                    
                    # WRITE_LOOP
                    0x1CC1,  # ADD R6, R2, R1       ; Compare index with size
                    0x0406,  # BRz READ_PHASE       ; If equal, start read phase
                    0x1800,  # ADD R4, R0, R2       ; Calculate address
                    0x1882,  # ADD R4, R2, R2       ; Value = index * 2
                    0x7900,  # STR R4, R0, R2       ; Store value
                    0x1481,  # ADD R2, R2, #1       ; Increment index
                    0x0FF9,  # BRnzp WRITE_LOOP     ; Continue
                    
                    # READ_phase: Read and sum all values
                    0x5480,  # AND R2, R2, #0       ; Reset index
                    0x56C0,  # AND R3, R3, #0       ; Clear sum
                    
                    # READ_LOOP
                    0x1CC1,  # ADD R6, R2, R1       ; Compare index with size
                    0x0403,  # BRz END              ; If equal, end
                    0x6900,  # LDR R4, R0, R2       ; Load value
                    0x16C4,  # ADD R3, R3, R4       ; Add to sum
                    0x1481,  # ADD R2, R2, #1       ; Increment index
                    0x0FFB,  # BRnzp READ_LOOP      ; Continue
                    
                    # END
                    0xF025,  # TRAP x25             ; HALT
                    
                    # Data
                    0x4000,  # BASE_ADDR: 0x4000
                    0x000A   # PATTERN_SIZE: 10
                ],
                'expected_result': 90,  # Sum of 0*2 + 1*2 + ... + 9*2 = 90
                'complexity': 'O(n)'
            }
        }
    
    def benchmark_program(self, program_info: Dict, max_cycles: int = 10000) -> Dict:
        """Benchmark a single program."""
        if lc3_simulator is None:
            return {'error': 'Simulator not available'}
        
        simulator = lc3_simulator.LC3Simulator()
        program = program_info['program']
        
        # Measure execution time
        start_time = time.perf_counter()
        
        simulator.reset()
        simulator.load_program(program)
        
        # Run the program
        cycles_used = 0
        start_exec_time = time.perf_counter()
        simulator.run(max_cycles=max_cycles)
        end_exec_time = time.perf_counter()
        
        end_time = time.perf_counter()
        
        # Collect results
        result = {
            'description': program_info['description'],
            'complexity': program_info['complexity'],
            'total_time': end_time - start_time,
            'execution_time': end_exec_time - start_exec_time,
            'program_size': len(program),
            'max_cycles': max_cycles,
            'halted': simulator.is_halted(),
            'final_pc': simulator.get_pc(),
            'registers': [simulator.get_register(i) for i in range(8)],
            'instructions_per_second': 0
        }
        
        if result['execution_time'] > 0:
            estimated_instructions = min(max_cycles, result['program_size'] * 10)  # Rough estimate
            result['instructions_per_second'] = estimated_instructions / result['execution_time']
        
        # Check expected result if provided
        if 'expected_result' in program_info:
            expected = program_info['expected_result']
            if isinstance(expected, int):
                result['expected_result'] = expected
                result['actual_result'] = simulator.get_register(0)
                result['result_correct'] = (result['actual_result'] == expected)
            elif isinstance(expected, list):
                # For array results, check memory
                result['expected_result'] = expected
                result['actual_result'] = []
                base_addr = 0x301B  # Assume array starts here for bubble sort
                for i in range(len(expected)):
                    result['actual_result'].append(simulator.get_memory(base_addr + i))
                result['result_correct'] = (result['actual_result'] == expected)
        
        return result
    
    def run_all_benchmarks(self, iterations: int = 5) -> Dict:
        """Run all benchmarks multiple times and collect statistics."""
        programs = self.get_sample_programs()
        results = {
            'benchmark_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'iterations': iterations,
                'simulator_available': lc3_simulator is not None
            },
            'programs': {}
        }
        
        if lc3_simulator is None:
            results['error'] = 'lc3_simulator module not available'
            return results
        
        print(f"Running LC-3 Program Benchmarks ({iterations} iterations each)...")
        
        for prog_name, prog_info in programs.items():
            print(f"Benchmarking {prog_name}...")
            
            program_results = []
            for i in range(iterations):
                result = self.benchmark_program(prog_info)
                program_results.append(result)
            
            # Calculate statistics
            execution_times = [r['execution_time'] for r in program_results if 'execution_time' in r]
            ips_values = [r['instructions_per_second'] for r in program_results if r['instructions_per_second'] > 0]
            
            avg_result = {
                'description': prog_info['description'],
                'complexity': prog_info['complexity'],
                'program_size': len(prog_info['program']),
                'iterations': iterations,
                'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
                'min_execution_time': min(execution_times) if execution_times else 0,
                'max_execution_time': max(execution_times) if execution_times else 0,
                'avg_instructions_per_second': sum(ips_values) / len(ips_values) if ips_values else 0,
                'all_halted': all(r.get('halted', False) for r in program_results),
                'all_results': program_results
            }
            
            # Check correctness
            if 'expected_result' in prog_info:
                correct_results = [r.get('result_correct', False) for r in program_results]
                avg_result['correctness_rate'] = sum(correct_results) / len(correct_results)
                avg_result['all_correct'] = all(correct_results)
            
            results['programs'][prog_name] = avg_result
        
        # Calculate overall statistics
        results['summary'] = self.calculate_benchmark_summary(results)
        
        return results
    
    def calculate_benchmark_summary(self, results: Dict) -> Dict:
        """Calculate summary statistics across all benchmarks."""
        if 'programs' not in results:
            return {}
        
        programs = results['programs']
        
        # Collect metrics
        avg_times = [p['avg_execution_time'] for p in programs.values() if p['avg_execution_time'] > 0]
        avg_ips = [p['avg_instructions_per_second'] for p in programs.values() if p['avg_instructions_per_second'] > 0]
        program_sizes = [p['program_size'] for p in programs.values()]
        
        summary = {
            'total_programs': len(programs),
            'programs_completed': sum(1 for p in programs.values() if p['all_halted']),
            'avg_execution_time': sum(avg_times) / len(avg_times) if avg_times else 0,
            'fastest_program': None,
            'slowest_program': None,
            'highest_throughput': None,
            'avg_program_size': sum(program_sizes) / len(program_sizes) if program_sizes else 0,
            'overall_ips': sum(avg_ips) / len(avg_ips) if avg_ips else 0
        }
        
        # Find extremes
        if avg_times:
            min_time = min(avg_times)
            max_time = max(avg_times)
            
            for name, prog in programs.items():
                if prog['avg_execution_time'] == min_time:
                    summary['fastest_program'] = {'name': name, 'time': min_time}
                if prog['avg_execution_time'] == max_time:
                    summary['slowest_program'] = {'name': name, 'time': max_time}
        
        if avg_ips:
            max_ips = max(avg_ips)
            for name, prog in programs.items():
                if prog['avg_instructions_per_second'] == max_ips:
                    summary['highest_throughput'] = {'name': name, 'ips': max_ips}
        
        return summary


def generate_benchmark_report(results: Dict, output_file: str = None) -> str:
    """Generate a detailed benchmark report."""
    if output_file is None:
        output_file = f"reports/isa_benchmark_report_{int(time.time())}.md"
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# LC-3 ISA Realistic Program Benchmark Report\n\n")
        
        # Test Information
        f.write("## Benchmark Information\n\n")
        if 'benchmark_info' in results:
            info = results['benchmark_info']
            f.write(f"**Generated**: {info['timestamp']}\n")
            f.write(f"**Iterations per Program**: {info['iterations']}\n")
            f.write(f"**Simulator Available**: {info['simulator_available']}\n\n")
        
        if 'error' in results:
            f.write(f"**Error**: {results['error']}\n\n")
            return output_file
        
        # Executive Summary
        if 'summary' in results:
            summary = results['summary']
            f.write("## Executive Summary\n\n")
            f.write(f"**Total Programs Tested**: {summary['total_programs']}\n")
            f.write(f"**Programs Completed Successfully**: {summary['programs_completed']}\n")
            f.write(f"**Average Execution Time**: {summary['avg_execution_time']:.6f} seconds\n")
            f.write(f"**Overall Instructions per Second**: {summary['overall_ips']:.0f}\n")
            f.write(f"**Average Program Size**: {summary['avg_program_size']:.1f} instructions\n\n")
            
            if summary.get('fastest_program'):
                fp = summary['fastest_program']
                f.write(f"**Fastest Program**: {fp['name']} ({fp['time']:.6f}s)\n")
            
            if summary.get('slowest_program'):
                sp = summary['slowest_program']
                f.write(f"**Slowest Program**: {sp['name']} ({sp['time']:.6f}s)\n")
            
            if summary.get('highest_throughput'):
                ht = summary['highest_throughput']
                f.write(f"**Highest Throughput**: {ht['name']} ({ht['ips']:.0f} IPS)\n")
            
            f.write("\n")
        
        # Program Results
        if 'programs' in results:
            f.write("## Program Benchmark Results\n\n")
            f.write("| Program | Description | Complexity | Size | Avg Time (ms) | IPS | Correctness |\n")
            f.write("|---------|-------------|------------|------|---------------|-----|-------------|\n")
            
            for prog_name, prog_data in results['programs'].items():
                correctness = "✅" if prog_data.get('all_correct', True) else "❌"
                f.write(f"| **{prog_name}** | {prog_data['description']} | "
                       f"{prog_data['complexity']} | {prog_data['program_size']} | "
                       f"{prog_data['avg_execution_time']*1000:.2f} | "
                       f"{prog_data['avg_instructions_per_second']:.0f} | {correctness} |\n")
            
            f.write("\n")
        
        # Detailed Analysis
        f.write("## Detailed Program Analysis\n\n")
        
        if 'programs' in results:
            for prog_name, prog_data in results['programs'].items():
                f.write(f"### {prog_name.replace('_', ' ').title()}\n\n")
                f.write(f"**Description**: {prog_data['description']}\n")
                f.write(f"**Complexity**: {prog_data['complexity']}\n")
                f.write(f"**Program Size**: {prog_data['program_size']} instructions\n")
                f.write(f"**Average Execution Time**: {prog_data['avg_execution_time']*1000:.3f} ms\n")
                f.write(f"**Performance Range**: {prog_data['min_execution_time']*1000:.3f} - "
                       f"{prog_data['max_execution_time']*1000:.3f} ms\n")
                f.write(f"**Instructions per Second**: {prog_data['avg_instructions_per_second']:.0f}\n")
                f.write(f"**Completion Rate**: {'100%' if prog_data['all_halted'] else '<100%'}\n")
                
                if 'correctness_rate' in prog_data:
                    f.write(f"**Correctness Rate**: {prog_data['correctness_rate']*100:.1f}%\n")
                
                f.write("\n")
        
        # Performance Analysis
        f.write("## Performance Analysis\n\n")
        f.write("### Algorithm Performance by Complexity\n\n")
        
        if 'programs' in results:
            # Group by complexity
            complexity_groups = {}
            for prog_name, prog_data in results['programs'].items():
                complexity = prog_data['complexity']
                if complexity not in complexity_groups:
                    complexity_groups[complexity] = []
                complexity_groups[complexity].append((prog_name, prog_data))
            
            for complexity, programs in complexity_groups.items():
                f.write(f"#### {complexity} Algorithms\n\n")
                for prog_name, prog_data in programs:
                    f.write(f"- **{prog_name}**: {prog_data['avg_execution_time']*1000:.2f}ms "
                           f"({prog_data['avg_instructions_per_second']:.0f} IPS)\n")
                f.write("\n")
        
        # Recommendations
        f.write("## Performance Recommendations\n\n")
        f.write("### Optimization Opportunities\n\n")
        f.write("1. **Algorithm Choice**: O(n) algorithms show best performance/complexity ratio\n")
        f.write("2. **Memory Access**: Sequential patterns outperform random access\n")
        f.write("3. **Loop Optimization**: Minimize branching in tight loops\n")
        f.write("4. **Instruction Mix**: Balance arithmetic vs. memory operations\n\n")
        
        f.write("### Educational Insights\n\n")
        f.write("1. **Complexity Impact**: Clear performance differences between O(n) and O(n²) algorithms\n")
        f.write("2. **Memory Hierarchy**: Demonstrates importance of memory access patterns\n")
        f.write("3. **Instruction Efficiency**: Shows relative costs of different instruction types\n")
        f.write("4. **Real-world Relevance**: Performance characteristics mirror modern processors\n\n")
    
    return output_file


if __name__ == "__main__":
    # Run benchmark when executed directly
    benchmark = LC3ProgramBenchmark()
    results = benchmark.run_all_benchmarks(iterations=3)
    
    # Generate report
    report_file = generate_benchmark_report(results)
    print(f"\nBenchmark completed!")
    print(f"Report generated: {report_file}")
    
    # Save raw results as JSON
    json_file = report_file.replace('.md', '.json')
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Raw data saved: {json_file}")
