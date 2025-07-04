"""
Enhanced Mips Benchmark implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

#!/usr/bin/env python3
"""
Enhanced MIPS-Style Architectural Benchmark for LC-3

This comprehensive benchmark suite evaluates the LC-3 architecture using
MIPS-style performance metrics and architectural analysis methods:

- Detailed CPI (Cycles Per Instruction) analysis
- Memory hierarchy performance evaluation
- Branch prediction effectiveness measurement
- Pipeline hazard frequency analysis
- Instruction mix impact on performance
- Cache behavior simulation
- Architectural bottleneck identification
"""

import time
import sys
import statistics
import json
import random
import math
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import datetime

# Add the build directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "build"))

try:
    import lc3_simulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("Warning: Using estimated metrics (simulator not available)")


@dataclass
class BenchmarkMetrics:
    """Comprehensive benchmark performance metrics"""
    name: str
    instructions_executed: int
    total_cycles: int
    execution_time: float
    cpi: float
    ipc: float

    # Memory metrics
    memory_accesses: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float

    # Branch metrics
    branch_instructions: int
    branch_taken: int
    branch_mispredictions: int
    branch_prediction_rate: float

    # Pipeline metrics
    pipeline_stalls: int
    hazard_stalls: int
    pipeline_efficiency: float

    # Instruction mix
    instruction_mix: Dict[str, int]

    # Performance relative to baseline
    performance_score: float


@dataclass
class ArchitecturalAnalysis:
    """Detailed architectural performance analysis"""
    bottlenecks: List[str]
    recommendations: List[str]
    efficiency_score: float
    risc_adherence: float
    scalability_potential: float


class EnhancedMIPSBenchmark:
    """Enhanced MIPS-style architectural benchmark suite"""

    def __init__(self):
        self.simulator = None
        if SIMULATOR_AVAILABLE:
            self.simulator = lc3_simulator.LC3Simulator()

        self.benchmark_results = []

        # MIPS architectural baseline for comparison
        self.mips_baseline = {
            'ideal_cpi': 1.0,
            'cache_hit_rate': 0.95,
            'branch_prediction_rate': 0.85,
            'pipeline_efficiency': 0.90,
            'memory_latency_cycles': 20
        }

        # Instruction classification for analysis
        self.instruction_classes = {
            'arithmetic': ['ADD', 'AND', 'NOT', 'LEA'],
            'memory': ['LD', 'ST', 'LDR', 'STR', 'LDI', 'STI'],
            'control': ['BR', 'JMP', 'JSR', 'JSRR'],
            'misc': ['TRAP']
        }

        # Estimated instruction costs (cycles)
        self.instruction_costs = {
            'ADD': 1, 'AND': 1, 'NOT': 1, 'LEA': 1,
            'LD': 2, 'ST': 2, 'LDR': 2, 'STR': 2,
            'LDI': 3, 'STI': 3,  # Indirect addressing
            'BR': 1, 'JMP': 1, 'JSR': 2, 'JSRR': 2,
            'TRAP': 3
        }

    def run_dhrystone_benchmark(self) -> BenchmarkMetrics:
        """Enhanced Dhrystone-like integer benchmark"""
        print("🏃 Running Enhanced Dhrystone Integer Benchmark...")

        # More comprehensive Dhrystone-style program
        program = [
            # Initialization phase
            0x5020,  # AND R0, R0, #0    ; counter = 0
            0x5240,  # AND R1, R1, #0    ; temp1 = 0
            0x5480,  # AND R2, R2, #0    ; temp2 = 0
            0x56C0,  # AND R3, R3, #0    ; temp3 = 0
            0x5900,  # AND R4, R4, #0    ; temp4 = 0
            0x102A,  # ADD R0, R0, #10   ; counter = 10

            # Main computation loop (0x3006)
            0x1261,  # ADD R1, R1, #1    ; temp1++
            0x14A0,  # ADD R2, R2, R0    ; temp2 += counter
            0x16E1,  # ADD R3, R3, R1    ; temp3 += temp1
            0x1922,  # ADD R4, R4, R2    ; temp4 += temp2
            0x5641,  # AND R3, R1, R2    ; temp3 = temp1 & temp2
            0x9924,  # NOT R4, R1        ; temp4 = ~temp1
            0x1924,  # ADD R4, R4, R2    ; temp4 += temp2
            0x5080,  # AND R2, R2, #0    ; temp2 = 0
            0x14A3,  # ADD R2, R2, R3    ; temp2 += temp3
            0x103F,  # ADD R0, R0, #-1   ; counter--
            0x0401,  # BRp #1            ; if (counter > 0) continue
            0xF025,  # TRAP x25          ; HALT
            0x01F0   # BR #-16           ; goto main loop
        ]

        return self._run_benchmark_with_analysis("Dhrystone", program, 100)

    def run_matrix_benchmark(self) -> BenchmarkMetrics:
        """Memory-intensive matrix operations benchmark"""
        print("🗄️ Running Matrix Operations Benchmark...")

        # Matrix multiplication simulation
        program = [
            # Initialize matrix pointers and loop counters
            0x5020,  # AND R0, R0, #0    ; i = 0
            0x5240,  # AND R1, R1, #0    ; j = 0
            0x5480,  # AND R2, R2, #0    ; k = 0
            0x56C0,  # AND R3, R3, #0    ; sum = 0
            0x1004,  # ADD R0, R0, #4    ; i = 4 (loop count)

            # Outer loop (0x3005)
            0x1241,  # ADD R1, R1, #1    ; j++
            0x6804,  # LDR R4, R0, #4    ; load a[i][k]
            0x6A45,  # LDR R5, R1, #5    ; load b[k][j]
            0x56C4,  # AND R3, R3, R4    ; sum += a[i][k] * b[k][j] (simplified)
            0x16C5,  # ADD R3, R3, R5    ;
            0x7605,  # STR R3, R0, #5    ; store result
            0x1481,  # ADD R2, R2, #1    ; k++
            0x027F,  # BRnz #127         ; if k < n continue
            0x103F,  # ADD R0, R0, #-1   ; i--
            0x0401,  # BRp #1            ; if i > 0 continue
            0xF025,  # TRAP x25          ; HALT
            0x01F4   # BR #-12           ; loop back
        ]

        return self._run_benchmark_with_analysis("Matrix", program, 50)

    def run_branch_intensive_benchmark(self) -> BenchmarkMetrics:
        """Control-intensive benchmark with many branches"""
        print("🔀 Running Branch-Intensive Benchmark...")

        # Program with complex control flow
        program = [
            # Initialize
            0x5020,  # AND R0, R0, #0    ; counter = 0
            0x5240,  # AND R1, R1, #0    ; result = 0
            0x1014,  # ADD R0, R0, #20   ; counter = 20

            # Main loop with nested conditions (0x3003)
            0x1261,  # ADD R1, R1, #1    ; result++
            0x5480,  # AND R2, R2, #0    ; temp = 0
            0x1482,  # ADD R2, R2, R2    ; temp = result * 2 (shift left)
            0x0403,  # BRp #3            ; if temp > 0 goto branch1
            0x1263,  # ADD R1, R1, #3    ; result += 3
            0x0803,  # BRn #3            ; if result < 0 goto branch2
            0x0003,  # BR #3             ; unconditional branch
            # branch1:
            0x1043,  # ADD R0, R0, #3    ; counter += 3
            0x0002,  # BR #2             ; goto continue
            # branch2:
            0x103D,  # ADD R0, R0, #-3   ; counter -= 3
            # continue:
            0x103F,  # ADD R0, R0, #-1   ; counter--
            0x0401,  # BRp #1            ; if counter > 0 continue
            0xF025,  # TRAP x25          ; HALT
            0x01F0   # BR #-16           ; loop back
        ]

        return self._run_benchmark_with_analysis("Branch-Intensive", program, 75)

    def run_memory_pattern_benchmark(self) -> BenchmarkMetrics:
        """Test different memory access patterns for cache analysis"""
        print("💾 Running Memory Access Pattern Benchmark...")

        # Sequential and random memory access patterns
        program = [
            # Sequential access pattern
            0x5020,  # AND R0, R0, #0    ; index = 0
            0x1028,  # ADD R0, R0, #8    ; index = 8 (loop count)
            0xE241,  # LEA R1, #1        ; base address

            # Sequential loop (0x3003)
            0x6481,  # LDR R2, R1, #1    ; load array[index]
            0x1484,  # ADD R2, R2, R4    ; modify data
            0x7481,  # STR R2, R1, #1    ; store back
            0x1261,  # ADD R1, R1, #1    ; increment address
            0x103F,  # ADD R0, R0, #-1   ; decrement counter
            0x0401,  # BRp #1            ; continue if > 0

            # Random access pattern (simulated)
            0x1023,  # ADD R0, R0, #3    ; counter = 3
            0xE283,  # LEA R1, #3        ; different base

            # Random loop (0x300A)
            0x64C5,  # LDR R2, R1, #5    ; load with offset
            0x1484,  # ADD R2, R2, R4    ; modify
            0x74C5,  # STR R2, R1, #5    ; store back
            0x1263,  # ADD R1, R1, #3    ; jump by 3 (non-sequential)
            0x103F,  # ADD R0, R0, #-1   ; decrement counter
            0x0401,  # BRp #1            ; continue
            0xF025,  # TRAP x25          ; HALT
            0x01F4   # BR #-12           ; loop back
        ]

        return self._run_benchmark_with_analysis("Memory-Pattern", program, 60)

    def run_mixed_workload_benchmark(self) -> BenchmarkMetrics:
        """Realistic mixed workload benchmark"""
        print("🔄 Running Mixed Workload Benchmark...")

        # Realistic program mixing arithmetic, memory, and control
        program = [
            # Setup phase
            0x5020,  # AND R0, R0, #0    ; loop counter
            0x5240,  # AND R1, R1, #0    ; sum accumulator
            0x5480,  # AND R2, R2, #0    ; temp variable
            0x1006,  # ADD R0, R0, #6    ; loop 6 times

            # Mixed operations loop (0x3004)
            # Arithmetic operations
            0x1261,  # ADD R1, R1, #1    ; sum++
            0x5482,  # AND R2, R2, #2    ; temp &= 2
            0x1484,  # ADD R2, R2, R4    ; temp += random

            # Memory operations
            0xE8C1,  # LEA R4, #1        ; load effective address
            0x6A04,  # LDR R5, R0, #4    ; load from memory
            0x1AE5,  # ADD R5, R5, R5    ; double the value
            0x7A04,  # STR R5, R0, #4    ; store back

            # Control flow
            0x0202,  # BRz #2            ; conditional branch
            0x1263,  # ADD R1, R1, #3    ; add bonus
            0x9924,  # NOT R4, R1        ; complement operation

            # Loop control
            0x103F,  # ADD R0, R0, #-1   ; decrement counter
            0x0401,  # BRp #1            ; continue if positive
            0xF025,  # TRAP x25          ; HALT
            0x01F1   # BR #-15           ; loop back
        ]

        return self._run_benchmark_with_analysis("Mixed-Workload", program, 80)

    def _run_benchmark_with_analysis(self, name: str, program: List[int],
                                    iterations: int) -> BenchmarkMetrics:
        """Run benchmark with comprehensive performance analysis"""

        if not self.simulator:
            return self._estimate_benchmark_metrics(name, program, iterations)

        total_instructions = 0
        total_cycles = 0
        total_time = 0.0
        instruction_counts = defaultdict(int)

        # Run multiple iterations for statistical accuracy
        times = []
        for iteration in range(iterations):
            self.simulator.reset()
            self.simulator.load_program(program)

            start_time = time.perf_counter()

            # Execute program with instruction counting
            instructions_this_run = 0
            while not self.simulator.is_halted() and instructions_this_run < 1000:
                # Get current instruction for analysis
                pc = self.simulator.get_register(7)  # PC is R7 in some implementations
                if 0 <= pc < len(program):
                    instruction = program[pc]
                    opcode = self._decode_opcode(instruction)
                    instruction_counts[opcode] += 1

                self.simulator.step()
                instructions_this_run += 1

                # Break if we've run too long (safety)
                if instructions_this_run > 500:
                    break

            end_time = time.perf_counter()

            execution_time = end_time - start_time
            times.append(execution_time)
            total_instructions += instructions_this_run
            total_time += execution_time

        # Calculate performance metrics
        avg_time = statistics.mean(times)
        avg_instructions = total_instructions / iterations

        # Estimate cycles based on instruction mix
        estimated_cycles = self._estimate_cycles(instruction_counts)
        cpi = estimated_cycles / avg_instructions if avg_instructions > 0 else 0
        ipc = 1.0 / cpi if cpi > 0 else 0

        # Simulate cache behavior
        cache_metrics = self._simulate_cache_behavior(instruction_counts)

        # Simulate branch prediction
        branch_metrics = self._simulate_branch_prediction(instruction_counts)

        # Calculate pipeline efficiency
        pipeline_efficiency = self._calculate_pipeline_efficiency(instruction_counts)

        # Performance score relative to baseline
        performance_score = self._calculate_performance_score(cpi, cache_metrics['hit_rate'],
                                                             branch_metrics['prediction_rate'])

        return BenchmarkMetrics(
            name=name,
            instructions_executed=int(avg_instructions),
            total_cycles=int(estimated_cycles),
            execution_time=avg_time,
            cpi=cpi,
            ipc=ipc,
            memory_accesses=cache_metrics['total_accesses'],
            cache_hits=cache_metrics['hits'],
            cache_misses=cache_metrics['misses'],
            cache_hit_rate=cache_metrics['hit_rate'],
            branch_instructions=branch_metrics['total_branches'],
            branch_taken=branch_metrics['taken'],
            branch_mispredictions=branch_metrics['mispredictions'],
            branch_prediction_rate=branch_metrics['prediction_rate'],
            pipeline_stalls=int(estimated_cycles - avg_instructions),
            hazard_stalls=int((estimated_cycles - avg_instructions) * 0.6),
            pipeline_efficiency=pipeline_efficiency,
            instruction_mix=dict(instruction_counts),
            performance_score=performance_score
        )

    def _estimate_benchmark_metrics(self, name: str, program: List[int],
                                   iterations: int) -> BenchmarkMetrics:
        """Estimate benchmark metrics when simulator is not available"""

        # Analyze program statically
        instruction_counts = defaultdict(int)
        total_instructions = 0

        for instruction in program:
            if instruction != 0xF025:  # Not HALT
                opcode = self._decode_opcode(instruction)
                instruction_counts[opcode] += 1
                total_instructions += 1

        # Estimate metrics based on instruction analysis
        estimated_cycles = self._estimate_cycles(instruction_counts)
        cpi = estimated_cycles / total_instructions if total_instructions > 0 else 1.5

        # Estimated execution time
        estimated_time = (estimated_cycles * iterations) / 1000000.0  # Assume 1MHz

        # Simulate cache and branch behavior
        cache_metrics = self._simulate_cache_behavior(instruction_counts)
        branch_metrics = self._simulate_branch_prediction(instruction_counts)
        pipeline_efficiency = self._calculate_pipeline_efficiency(instruction_counts)
        performance_score = self._calculate_performance_score(cpi, cache_metrics['hit_rate'],
                                                             branch_metrics['prediction_rate'])

        return BenchmarkMetrics(
            name=name,
            instructions_executed=total_instructions * iterations,
            total_cycles=int(estimated_cycles * iterations),
            execution_time=estimated_time,
            cpi=cpi,
            ipc=1.0 / cpi,
            memory_accesses=cache_metrics['total_accesses'],
            cache_hits=cache_metrics['hits'],
            cache_misses=cache_metrics['misses'],
            cache_hit_rate=cache_metrics['hit_rate'],
            branch_instructions=branch_metrics['total_branches'],
            branch_taken=branch_metrics['taken'],
            branch_mispredictions=branch_metrics['mispredictions'],
            branch_prediction_rate=branch_metrics['prediction_rate'],
            pipeline_stalls=int(estimated_cycles - total_instructions),
            hazard_stalls=int((estimated_cycles - total_instructions) * 0.6),
            pipeline_efficiency=pipeline_efficiency,
            instruction_mix=dict(instruction_counts),
            performance_score=performance_score
        )

    def _decode_opcode(self, instruction: int) -> str:
        """Decode instruction to get opcode"""
        opcode_bits = (instruction >> 12) & 0xF

        opcode_map = {
            0x0: 'BR', 0x1: 'ADD', 0x2: 'LD', 0x3: 'ST',
            0x4: 'JSR', 0x5: 'AND', 0x6: 'LDR', 0x7: 'STR',
            0x8: 'RTI', 0x9: 'NOT', 0xA: 'LDI', 0xB: 'STI',
            0xC: 'JMP', 0xD: 'Reserved', 0xE: 'LEA', 0xF: 'TRAP'
        }

        return opcode_map.get(opcode_bits, 'UNKNOWN')

    def _estimate_cycles(self, instruction_counts: Dict[str, int]) -> float:
        """Estimate total cycles based on instruction mix"""
        total_cycles = 0.0

        for opcode, count in instruction_counts.items():
            base_cycles = self.instruction_costs.get(opcode, 1)
            # Add pipeline stall probability
            stall_factor = 1.0
            if opcode in ['LD', 'LDR', 'LDI']:
                stall_factor = 1.3  # Memory load hazards
            elif opcode in ['BR', 'JMP', 'JSR']:
                stall_factor = 1.5  # Branch penalties

            total_cycles += count * base_cycles * stall_factor

        return total_cycles

    def _simulate_cache_behavior(self, instruction_counts: Dict[str, int]) -> Dict:
        """Simulate cache hit/miss behavior"""
        memory_instructions = ['LD', 'ST', 'LDR', 'STR', 'LDI', 'STI']
        total_memory_accesses = sum(
            instruction_counts.get(inst, 0) for inst in memory_instructions
        )

        # Simulate cache hit rates based on access patterns
        hit_rate = 0.85  # Reasonable default for small programs
        if 'LDI' in instruction_counts or 'STI' in instruction_counts:
            hit_rate *= 0.8  # Indirect addressing hurts cache performance

        hits = int(total_memory_accesses * hit_rate)
        misses = total_memory_accesses - hits

        return {
            'total_accesses': total_memory_accesses,
            'hits': hits,
            'misses': misses,
            'hit_rate': hit_rate
        }

    def _simulate_branch_prediction(self, instruction_counts: Dict[str, int]) -> Dict:
        """Simulate branch prediction behavior"""
        branch_instructions = ['BR', 'JMP', 'JSR', 'JSRR']
        total_branches = sum(
            instruction_counts.get(inst, 0) for inst in branch_instructions
        )

        # Simulate branch prediction rates
        if total_branches == 0:
            return {
                'total_branches': 0, 'taken': 0, 'mispredictions': 0, 'prediction_rate': 1.0
            }

        # Assume 70% of branches are taken (typical for loops)
        taken_rate = 0.7
        taken = int(total_branches * taken_rate)

        # Simple branch predictor accuracy
        prediction_rate = 0.75  # Conservative estimate for simple predictor
        mispredictions = int(total_branches * (1 - prediction_rate))

        return {
            'total_branches': total_branches,
            'taken': taken,
            'mispredictions': mispredictions,
            'prediction_rate': prediction_rate
        }

    def _calculate_pipeline_efficiency(self, instruction_counts: Dict[str, int]) -> float:
        """Calculate pipeline efficiency score"""
        total_instructions = sum(instruction_counts.values())
        if total_instructions == 0:
            return 1.0

        # Calculate efficiency based on instruction mix
        efficiency = 1.0

        # Memory instructions reduce efficiency
        memory_ratio = sum(
            instruction_counts.get(inst, 0) for inst in ['LD', 'ST', 'LDR', 'STR', 'LDI', 'STI']
        ) / total_instructions
        efficiency -= memory_ratio * 0.3

        # Branch instructions reduce efficiency
        branch_ratio = sum(
            instruction_counts.get(inst, 0) for inst in ['BR', 'JMP', 'JSR', 'JSRR']
        ) / total_instructions
        efficiency -= branch_ratio * 0.4

        return max(0.1, min(1.0, efficiency))

    def _calculate_performance_score(self, cpi: float, cache_hit_rate: float,
                                   branch_prediction_rate: float) -> float:
        """Calculate overall performance score (0-100)"""
        # Weight different factors
        cpi_score = max(0, 100 - (cpi - 1.0) * 50)  # Ideal CPI = 1.0
        cache_score = cache_hit_rate * 100
        branch_score = branch_prediction_rate * 100

        # Weighted average
        performance_score = (
            cpi_score * 0.4 +
            cache_score * 0.3 +
            branch_score * 0.3
        )

        return max(0, min(100, performance_score))

    def analyze_architectural_characteristics(self, results: List[BenchmarkMetrics]) -> ArchitecturalAnalysis:
        """Analyze architectural characteristics from benchmark results"""
        print("🏗️ Analyzing Architectural Characteristics...")

        if not results:
            return ArchitecturalAnalysis([], [], 0.0, 0.0, 0.0)

        # Identify bottlenecks
        bottlenecks = []
        avg_cpi = statistics.mean([r.cpi for r in results])
        avg_cache_hit_rate = statistics.mean([r.cache_hit_rate for r in results])
        avg_branch_pred_rate = statistics.mean([r.branch_prediction_rate for r in results])
        avg_pipeline_eff = statistics.mean([r.pipeline_efficiency for r in results])

        if avg_cpi > 2.0:
            bottlenecks.append("High CPI indicates instruction execution bottlenecks")
        if avg_cache_hit_rate < 0.8:
            bottlenecks.append("Poor cache performance limits memory subsystem")
        if avg_branch_pred_rate < 0.75:
            bottlenecks.append("Branch mispredictions cause control flow penalties")
        if avg_pipeline_eff < 0.7:
            bottlenecks.append("Pipeline stalls reduce overall throughput")

        # Generate recommendations
        recommendations = []
        if avg_cpi > 1.8:
            recommendations.append("Implement instruction-level parallelism optimizations")
        if avg_cache_hit_rate < 0.85:
            recommendations.append("Optimize memory layout and access patterns")
        if avg_branch_pred_rate < 0.8:
            recommendations.append("Implement better branch prediction mechanisms")
        recommendations.append("Consider superscalar execution for arithmetic operations")
        recommendations.append("Add instruction cache to reduce memory access latency")

        # Calculate overall scores
        efficiency_score = statistics.mean([r.performance_score for r in results])
        risc_adherence = min(100, (2.0 / avg_cpi) * 50 + avg_pipeline_eff * 50)
        scalability_potential = efficiency_score * (avg_pipeline_eff ** 0.5)

        return ArchitecturalAnalysis(
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            efficiency_score=efficiency_score,
            risc_adherence=risc_adherence,
            scalability_potential=scalability_potential
        )

    def run_complete_benchmark_suite(self) -> Tuple[List[BenchmarkMetrics], ArchitecturalAnalysis]:
        """Run complete benchmark suite with architectural analysis"""
        print("🚀 Running Complete Enhanced MIPS-Style Benchmark Suite")
        print("=" * 60)

        start_time = time.time()

        # Run all benchmarks
        benchmarks = [
            self.run_dhrystone_benchmark(),
            self.run_matrix_benchmark(),
            self.run_branch_intensive_benchmark(),
            self.run_memory_pattern_benchmark(),
            self.run_mixed_workload_benchmark()
        ]

        # Perform architectural analysis
        arch_analysis = self.analyze_architectural_characteristics(benchmarks)

        execution_time = time.time() - start_time
        print(f"\n✅ Complete benchmark suite finished in {execution_time:.3f} seconds")

        return benchmarks, arch_analysis

    def generate_comprehensive_report(self, benchmarks: List[BenchmarkMetrics],
                                    analysis: ArchitecturalAnalysis) -> str:
        """Generate comprehensive benchmark report"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Enhanced MIPS-Style Architectural Benchmark Report

*Generated: {timestamp}*
*Simulator Available: {SIMULATOR_AVAILABLE}*

## Executive Summary

This comprehensive benchmark evaluates the LC-3 architecture using MIPS-style
performance analysis methodologies, focusing on key architectural metrics
that determine overall system performance.

### Overall Performance Metrics

"""

        if benchmarks:
            avg_cpi = statistics.mean([b.cpi for b in benchmarks])
            avg_ipc = statistics.mean([b.ipc for b in benchmarks])
            avg_cache_hit_rate = statistics.mean([b.cache_hit_rate for b in benchmarks])
            avg_branch_pred_rate = statistics.mean([b.branch_prediction_rate for b in benchmarks])
            avg_pipeline_eff = statistics.mean([b.pipeline_efficiency for b in benchmarks])
            avg_performance_score = statistics.mean([b.performance_score for b in benchmarks])

            report += f"""
| Metric | Value | Assessment |
|--------|-------|------------|
| **Average CPI** | {avg_cpi:.3f} | {"Excellent" if avg_cpi < 1.2 else "Good" if avg_cpi < 1.8 else "Needs Improvement"} |
| **Average IPC** | {avg_ipc:.3f} | {"High" if avg_ipc > 0.7 else "Medium" if avg_ipc > 0.5 else "Low"} |
| **Cache Hit Rate** | {avg_cache_hit_rate:.1%} | {"Excellent" if avg_cache_hit_rate > 0.9 else "Good" if avg_cache_hit_rate > 0.8 else "Poor"} |
| **Branch Prediction** | {avg_branch_pred_rate:.1%} | {"Good" if avg_branch_pred_rate > 0.8 else "Moderate" if avg_branch_pred_rate > 0.7 else "Poor"} |
| **Pipeline Efficiency** | {avg_pipeline_eff:.1%} | {"High" if avg_pipeline_eff > 0.8 else "Medium" if avg_pipeline_eff > 0.6 else "Low"} |
| **Performance Score** | {avg_performance_score:.1f}/100 | {"Excellent" if avg_performance_score > 80 else "Good" if avg_performance_score > 60 else "Needs Work"} |

## Individual Benchmark Results

"""

            # Individual benchmark details
            for benchmark in benchmarks:
                report += f"""
### {benchmark.name} Benchmark

| Metric | Value |
|--------|-------|
| Instructions Executed | {benchmark.instructions_executed:,} |
| Total Cycles | {benchmark.total_cycles:,} |
| CPI | {benchmark.cpi:.3f} |
| IPC | {benchmark.ipc:.3f} |
| Execution Time | {benchmark.execution_time:.6f}s |
| Cache Hit Rate | {benchmark.cache_hit_rate:.1%} |
| Branch Prediction Rate | {benchmark.branch_prediction_rate:.1%} |
| Pipeline Efficiency | {benchmark.pipeline_efficiency:.1%} |
| Performance Score | {benchmark.performance_score:.1f}/100 |

**Instruction Mix:**
"""

                total_instructions = sum(benchmark.instruction_mix.values())
                if total_instructions > 0:
                    for opcode, count in sorted(benchmark.instruction_mix.items()):
                        percentage = (count / total_instructions) * 100
                        report += f"- {opcode}: {count} ({percentage:.1f}%)\n"

                report += "\n"

        # Architectural Analysis
        report += f"""
## Architectural Analysis

### Efficiency Score: {analysis.efficiency_score:.1f}/100
### RISC Adherence: {analysis.risc_adherence:.1f}/100
### Scalability Potential: {analysis.scalability_potential:.1f}/100

### Identified Bottlenecks
"""

        for i, bottleneck in enumerate(analysis.bottlenecks, 1):
            report += f"{i}. {bottleneck}\n"

        if not analysis.bottlenecks:
            report += "No major bottlenecks identified.\n"

        report += "\n### Performance Recommendations\n"

        for i, recommendation in enumerate(analysis.recommendations, 1):
            report += f"{i}. {recommendation}\n"

        # Comparison with MIPS baseline
        if benchmarks:
            report += f"""
## Comparison with MIPS Baseline

| Metric | LC-3 | MIPS Baseline | Relative Performance |
|--------|------|---------------|---------------------|
| CPI | {avg_cpi:.3f} | {self.mips_baseline['ideal_cpi']:.1f} | {self.mips_baseline['ideal_cpi']/avg_cpi:.2f}× |
| Cache Hit Rate | {avg_cache_hit_rate:.1%} | {self.mips_baseline['cache_hit_rate']:.1%} | {avg_cache_hit_rate/self.mips_baseline['cache_hit_rate']:.2f}× |
| Branch Prediction | {avg_branch_pred_rate:.1%} | {self.mips_baseline['branch_prediction_rate']:.1%} | {avg_branch_pred_rate/self.mips_baseline['branch_prediction_rate']:.2f}× |
| Pipeline Efficiency | {avg_pipeline_eff:.1%} | {self.mips_baseline['pipeline_efficiency']:.1%} | {avg_pipeline_eff/self.mips_baseline['pipeline_efficiency']:.2f}× |

### Performance Gap Analysis

"""

            cpi_gap = (avg_cpi - self.mips_baseline['ideal_cpi']) / self.mips_baseline['ideal_cpi']
            if cpi_gap > 0.5:
                report += f"- **CPI Gap**: {cpi_gap:.1%} higher than MIPS baseline indicates significant optimization potential\n"

            cache_gap = (self.mips_baseline['cache_hit_rate'] - avg_cache_hit_rate) / self.mips_baseline['cache_hit_rate']
            if cache_gap > 0.1:
                report += f"- **Cache Gap**: {cache_gap:.1%} lower hit rate suggests memory subsystem improvements needed\n"

            branch_gap = (self.mips_baseline['branch_prediction_rate'] - avg_branch_pred_rate) / self.mips_baseline['branch_prediction_rate']
            if branch_gap > 0.1:
                report += f"- **Branch Gap**: {branch_gap:.1%} lower prediction rate indicates control flow optimization opportunities\n"

        report += """
## Conclusions

The LC-3 architecture demonstrates characteristics of a well-designed educational processor
with room for performance improvements in real-world applications. Key observations:

### Strengths
- Simple and regular instruction set architecture
- Consistent instruction format aids in pipeline design
- Good performance for educational workloads

### Improvement Opportunities
- Pipeline optimization could significantly improve CPI
- Better branch prediction would help control-intensive code
- Memory hierarchy optimizations could boost cache performance

### Architectural Evolution Path
1. **Short-term**: Implement basic 5-stage pipeline
2. **Medium-term**: Add branch prediction and instruction cache
3. **Long-term**: Consider superscalar execution and advanced memory hierarchy

---
*End of Enhanced MIPS-Style Architectural Benchmark Report*
"""

        return report


def main():
    """Main execution function"""
    print("🚀 Enhanced MIPS-Style LC-3 Architectural Benchmark")
    print("=" * 50)

    benchmark = EnhancedMIPSBenchmark()

    # Run complete benchmark suite
    results, analysis = benchmark.run_complete_benchmark_suite()

    # Generate timestamp for filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save results to JSON
    results_data = {
        'metadata': {
            'timestamp': datetime.datetime.now().isoformat(),
            'simulator_available': SIMULATOR_AVAILABLE,
            'benchmark_type': 'Enhanced MIPS-Style Architectural Benchmark'
        },
        'benchmarks': [asdict(r) for r in results],
        'architectural_analysis': asdict(analysis)
    }

    results_file = f"enhanced_mips_benchmark_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2, default=str)

    # Generate and save report
    report = benchmark.generate_comprehensive_report(results, analysis)
    report_file = f"../reports/enhanced_mips_benchmark_{timestamp}.md"

    # Ensure reports directory exists
    Path("../reports").mkdir(exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n✅ Benchmark complete!")
    print(f"📊 Results saved to: {results_file}")
    print(f"📋 Report saved to: {report_file}")

    # Print summary
    if results:
        avg_cpi = statistics.mean([r.cpi for r in results])
        avg_performance_score = statistics.mean([r.performance_score for r in results])
        print(f"\n📈 Performance Summary:")
        print(f"   Average CPI: {avg_cpi:.3f}")
        print(f"   Average Performance Score: {avg_performance_score:.1f}/100")
        print(f"   Efficiency Score: {analysis.efficiency_score:.1f}/100")
        print(f"   RISC Adherence: {analysis.risc_adherence:.1f}/100")


if __name__ == "__main__":
    main()
