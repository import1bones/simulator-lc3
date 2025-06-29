#!/usr/bin/env python3
"""
LC-3 ISA Design Performance Analysis

This module provides comprehensive ISA design analysis focusing on:
- Instruction format efficiency 
- Addressing mode performance
- Pipeline characteristics
- Instruction mix analysis
- Memory hierarchy impact
- Architectural design trade-offs

Based on MIPS design principles and computer architecture metrics.
"""

import time
import sys
import statistics
import json
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Add the build directory to Python path for lc3_simulator
sys.path.insert(0, str(Path(__file__).parent / "build"))

try:
    import lc3_simulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("Warning: lc3_simulator module not available. Some tests will be skipped.")


@dataclass
class InstructionMetrics:
    """Metrics for individual instruction performance"""
    opcode: str
    format_type: str  # R-type, I-type, J-type equivalent
    cycles: int
    memory_accesses: int
    register_accesses: int
    execution_time: float
    throughput: float
    utilization: float


@dataclass
class ISADesignMetrics:
    """Overall ISA design performance metrics"""
    instruction_density: float  # Instructions per byte
    addressing_efficiency: float  # Effective addresses per instruction
    pipeline_efficiency: float  # Instructions per cycle potential
    memory_bandwidth_util: float  # Memory bandwidth utilization
    register_pressure: float  # Average register usage
    code_size_efficiency: float  # Code size vs functionality


class LC3ISAAnalyzer:
    """Comprehensive LC-3 ISA design analyzer"""
    
    def __init__(self):
        self.simulator = None
        if SIMULATOR_AVAILABLE:
            self.simulator = lc3_simulator.LC3Simulator()
        
        # LC-3 instruction format classification
        self.instruction_formats = {
            # R-type equivalent (register operations)
            'ADD_reg': 'R-type', 'AND_reg': 'R-type', 'NOT': 'R-type',
            # I-type equivalent (immediate/memory operations)
            'ADD_imm': 'I-type', 'AND_imm': 'I-type', 'LD': 'I-type', 'ST': 'I-type',
            'LDR': 'I-type', 'STR': 'I-type', 'LDI': 'I-type', 'STI': 'I-type',
            'LEA': 'I-type', 'BR': 'I-type', 'TRAP': 'I-type',
            # J-type equivalent (jump operations)
            'JMP': 'J-type', 'JSR': 'J-type', 'JSRR': 'J-type'
        }
        
        # Memory access patterns for each instruction
        self.memory_access_patterns = {
            'ADD_reg': 0, 'ADD_imm': 0, 'AND_reg': 0, 'AND_imm': 0, 'NOT': 0,
            'LD': 1, 'ST': 1, 'LDR': 1, 'STR': 1, 'LEA': 0,
            'LDI': 2, 'STI': 2,  # Indirect = 2 memory accesses
            'BR': 0, 'JMP': 0, 'JSR': 0, 'JSRR': 0,
            'TRAP': 1
        }
        
        # Addressing modes supported
        self.addressing_modes = {
            'immediate': ['ADD_imm', 'AND_imm'],
            'register': ['ADD_reg', 'AND_reg', 'NOT', 'JMP', 'JSRR'],
            'pc_relative': ['LD', 'ST', 'LEA', 'BR', 'JSR'],
            'base_offset': ['LDR', 'STR'],
            'indirect': ['LDI', 'STI'],
            'register_indirect': ['TRAP']
        }
        
        self.results = {}
        self.instruction_metrics = {}
        
    def run_instruction_format_analysis(self) -> Dict:
        """Analyze instruction format efficiency"""
        print("🔧 Running Instruction Format Analysis...")
        
        format_metrics = {
            'R-type': {'count': 0, 'total_time': 0, 'avg_complexity': 0},
            'I-type': {'count': 0, 'total_time': 0, 'avg_complexity': 0},
            'J-type': {'count': 0, 'total_time': 0, 'avg_complexity': 0}
        }
        
        # Test each instruction type
        test_instructions = {
            'ADD_reg': ([0x1001], 'R-type'),  # ADD R0, R0, R1
            'ADD_imm': ([0x1021], 'I-type'),  # ADD R0, R0, #1
            'AND_reg': ([0x5001], 'R-type'),  # AND R0, R0, R1
            'AND_imm': ([0x5020], 'I-type'),  # AND R0, R0, #0
            'NOT': ([0x903F], 'R-type'),      # NOT R0, R1
            'LD': ([0x2001, 0x1234], 'I-type'),  # LD R0, #1
            'ST': ([0x3001, 0x0000], 'I-type'),  # ST R0, #1
            'LDR': ([0x6040], 'I-type'),      # LDR R0, R1, #0
            'STR': ([0x7040], 'I-type'),      # STR R0, R1, #0
            'LEA': ([0xE001], 'I-type'),      # LEA R0, #1
            'BR': ([0x0001], 'I-type'),       # BR #1
            'JMP': ([0xC1C0], 'J-type'),      # JMP R7
            'JSR': ([0x4001], 'J-type'),      # JSR #1
            'TRAP': ([0xF025], 'I-type')      # TRAP x25
        }
        
        if not self.simulator:
            print("⚠️ Simulator not available, using estimated metrics")
            # Provide estimated metrics based on instruction complexity
            for inst_name, (_, format_type) in test_instructions.items():
                complexity = self._estimate_instruction_complexity(inst_name)
                format_metrics[format_type]['count'] += 1
                format_metrics[format_type]['total_time'] += complexity
                format_metrics[format_type]['avg_complexity'] += complexity
            
            # Calculate averages
            for format_type in format_metrics:
                if format_metrics[format_type]['count'] > 0:
                    format_metrics[format_type]['avg_time'] = \
                        format_metrics[format_type]['total_time'] / format_metrics[format_type]['count']
                    format_metrics[format_type]['avg_complexity'] /= format_metrics[format_type]['count']
        else:
            # Run actual performance tests
            for inst_name, (program, format_type) in test_instructions.items():
                times = []
                for _ in range(100):  # Multiple runs for accuracy
                    self.simulator.reset()
                    self.simulator.load_program(program)
                    
                    start_time = time.perf_counter()
                    self.simulator.step()
                    end_time = time.perf_counter()
                    
                    times.append(end_time - start_time)
                
                avg_time = statistics.mean(times)
                format_metrics[format_type]['count'] += 1
                format_metrics[format_type]['total_time'] += avg_time
                
                # Store individual instruction metrics
                self.instruction_metrics[inst_name] = InstructionMetrics(
                    opcode=inst_name,
                    format_type=format_type,
                    cycles=self._estimate_cycles(inst_name),
                    memory_accesses=self.memory_access_patterns.get(inst_name, 0),
                    register_accesses=self._estimate_register_accesses(inst_name),
                    execution_time=avg_time,
                    throughput=1.0 / avg_time if avg_time > 0 else 0,
                    utilization=self._estimate_utilization(inst_name)
                )
            
            # Calculate averages
            for format_type in format_metrics:
                if format_metrics[format_type]['count'] > 0:
                    format_metrics[format_type]['avg_time'] = \
                        format_metrics[format_type]['total_time'] / format_metrics[format_type]['count']
        
        return format_metrics
    
    def run_addressing_mode_analysis(self) -> Dict:
        """Analyze addressing mode efficiency"""
        print("📍 Running Addressing Mode Analysis...")
        
        addressing_results = {}
        
        # Test programs for each addressing mode
        test_programs = {
            'immediate': {
                'program': [0x1021, 0xF025],  # ADD R0, R0, #1; HALT
                'description': 'Immediate addressing - operand in instruction'
            },
            'register': {
                'program': [0x1001, 0xF025],  # ADD R0, R0, R1; HALT
                'description': 'Register addressing - operand in register'
            },
            'pc_relative': {
                'program': [0x2001, 0xF025, 0x1234],  # LD R0, #1; HALT; DATA
                'description': 'PC-relative - address relative to PC'
            },
            'base_offset': {
                'program': [0x6040, 0xF025],  # LDR R0, R1, #0; HALT
                'description': 'Base+offset - base register plus offset'
            },
            'indirect': {
                'program': [0xA001, 0xF025, 0x3004, 0x5678],  # LDI R0, #1; HALT; PTR; DATA
                'description': 'Indirect - address contains pointer to data'
            }
        }
        
        for mode_name, test_data in test_programs.items():
            if not self.simulator:
                # Estimated performance based on addressing complexity
                estimated_time = self._estimate_addressing_time(mode_name)
                addressing_results[mode_name] = {
                    'avg_time': estimated_time,
                    'description': test_data['description'],
                    'relative_performance': estimated_time / 50.0,  # Normalize to immediate
                    'memory_accesses': self._get_addressing_memory_accesses(mode_name),
                    'cycles_estimate': self._get_addressing_cycles(mode_name)
                }
            else:
                times = []
                for _ in range(50):
                    self.simulator.reset()
                    self.simulator.set_register(1, 0x3003)  # Set base register for base_offset
                    self.simulator.load_program(test_data['program'])
                    
                    start_time = time.perf_counter()
                    self.simulator.step()  # Execute first instruction
                    end_time = time.perf_counter()
                    
                    times.append(end_time - start_time)
                
                avg_time = statistics.mean(times)
                addressing_results[mode_name] = {
                    'avg_time': avg_time,
                    'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                    'description': test_data['description'],
                    'relative_performance': avg_time / addressing_results.get('immediate', {}).get('avg_time', avg_time),
                    'memory_accesses': self._get_addressing_memory_accesses(mode_name),
                    'cycles_estimate': self._get_addressing_cycles(mode_name)
                }
        
        return addressing_results
    
    def run_pipeline_analysis(self) -> Dict:
        """Analyze pipeline characteristics and potential"""
        print("⚡ Running Pipeline Analysis...")
        
        # LC-3 pipeline stages analysis
        pipeline_stages = {
            'fetch': 'Instruction fetch from memory',
            'decode': 'Instruction decode and register read',
            'execute': 'ALU operation or address calculation',
            'memory': 'Memory access (if needed)',
            'writeback': 'Write result to register'
        }
        
        # Instruction pipeline requirements
        instruction_pipeline_reqs = {
            'ADD_reg': ['fetch', 'decode', 'execute', 'writeback'],
            'ADD_imm': ['fetch', 'decode', 'execute', 'writeback'],
            'LD': ['fetch', 'decode', 'execute', 'memory', 'writeback'],
            'ST': ['fetch', 'decode', 'execute', 'memory'],
            'BR': ['fetch', 'decode', 'execute'],
            'JMP': ['fetch', 'decode', 'execute'],
        }
        
        # Calculate CPI (Cycles Per Instruction) for different scenarios
        cpi_analysis = {}
        
        # Without pipeline (current LC-3)
        base_cpi = {}
        for inst, stages in instruction_pipeline_reqs.items():
            base_cpi[inst] = len(stages)
        
        # With ideal 5-stage pipeline
        ideal_pipeline_cpi = 1.0  # Ideal case
        
        # With realistic pipeline (hazards, stalls)
        realistic_pipeline_cpi = {}
        for inst, stages in instruction_pipeline_reqs.items():
            # Add penalties for dependencies and hazards
            penalty = 0
            if 'memory' in stages:
                penalty += 1  # Memory access penalty
            if inst.startswith('BR') or inst.startswith('J'):
                penalty += 2  # Branch penalty
            
            realistic_pipeline_cpi[inst] = 1.0 + (penalty * 0.5)
        
        cpi_analysis = {
            'unpipelined': {
                'description': 'Current LC-3 implementation',
                'average_cpi': statistics.mean(base_cpi.values()),
                'instruction_cpi': base_cpi
            },
            'ideal_pipeline': {
                'description': 'Perfect 5-stage pipeline',
                'average_cpi': ideal_pipeline_cpi,
                'throughput_improvement': statistics.mean(base_cpi.values()) / ideal_pipeline_cpi
            },
            'realistic_pipeline': {
                'description': 'Realistic pipeline with hazards',
                'average_cpi': statistics.mean(realistic_pipeline_cpi.values()),
                'instruction_cpi': realistic_pipeline_cpi,
                'throughput_improvement': statistics.mean(base_cpi.values()) / statistics.mean(realistic_pipeline_cpi.values())
            }
        }
        
        return cpi_analysis
    
    def run_instruction_mix_analysis(self) -> Dict:
        """Analyze typical instruction mix and its impact"""
        print("📊 Running Instruction Mix Analysis...")
        
        # Typical instruction mixes for different program types
        instruction_mixes = {
            'scientific': {
                'arithmetic': 0.45,  # ADD, AND, NOT
                'memory': 0.25,      # LD, ST, LDR, STR
                'control': 0.20,     # BR, JMP, JSR
                'other': 0.10        # TRAP, etc.
            },
            'systems': {
                'arithmetic': 0.30,
                'memory': 0.40,
                'control': 0.25,
                'other': 0.05
            },
            'multimedia': {
                'arithmetic': 0.35,
                'memory': 0.35,
                'control': 0.15,
                'other': 0.15
            }
        }
        
        # Calculate weighted performance for each mix
        mix_performance = {}
        
        # Base instruction times (estimated or measured)
        if self.instruction_metrics:
            instruction_times = {
                'arithmetic': statistics.mean([
                    m.execution_time for m in self.instruction_metrics.values()
                    if m.opcode.startswith(('ADD', 'AND', 'NOT'))
                ]),
                'memory': statistics.mean([
                    m.execution_time for m in self.instruction_metrics.values()
                    if m.opcode.startswith(('LD', 'ST', 'LDR', 'STR', 'LDI', 'STI'))
                ]),
                'control': statistics.mean([
                    m.execution_time for m in self.instruction_metrics.values()
                    if m.opcode.startswith(('BR', 'JMP', 'JSR'))
                ]),
                'other': statistics.mean([
                    m.execution_time for m in self.instruction_metrics.values()
                    if m.opcode.startswith('TRAP')
                ])
            }
        else:
            # Estimated times (microseconds)
            instruction_times = {
                'arithmetic': 40.0,
                'memory': 60.0,
                'control': 45.0,
                'other': 50.0
            }
        
        for mix_name, mix_ratios in instruction_mixes.items():
            weighted_time = sum(
                instruction_times[inst_type] * ratio
                for inst_type, ratio in mix_ratios.items()
            )
            
            mix_performance[mix_name] = {
                'weighted_avg_time': weighted_time,
                'instructions_per_second': 1_000_000 / weighted_time,  # Convert μs to IPS
                'instruction_ratios': mix_ratios,
                'bottleneck': max(mix_ratios.items(), key=lambda x: x[1] * instruction_times[x[0]])[0]
            }
        
        return mix_performance
    
    def run_memory_hierarchy_analysis(self) -> Dict:
        """Analyze memory hierarchy impact on ISA performance"""
        print("🗄️ Running Memory Hierarchy Analysis...")
        
        # Memory access patterns and their costs
        memory_patterns = {
            'sequential_reads': {
                'description': 'Sequential memory reads (good cache locality)',
                'cache_hit_rate': 0.95,
                'avg_access_time': 1.2  # cycles
            },
            'random_reads': {
                'description': 'Random memory reads (poor cache locality)',
                'cache_hit_rate': 0.60,
                'avg_access_time': 3.5  # cycles
            },
            'instruction_fetch': {
                'description': 'Instruction fetches (predictable pattern)',
                'cache_hit_rate': 0.98,
                'avg_access_time': 1.1  # cycles
            },
            'stack_operations': {
                'description': 'Stack operations (temporal locality)',
                'cache_hit_rate': 0.90,
                'avg_access_time': 1.3  # cycles
            }
        }
        
        # Calculate impact on different instruction types
        memory_impact = {}
        
        for pattern_name, pattern_data in memory_patterns.items():
            # Calculate effective memory access time
            cache_hit_time = 1.0  # cycles
            cache_miss_penalty = 20.0  # cycles
            
            effective_time = (
                pattern_data['cache_hit_rate'] * cache_hit_time +
                (1 - pattern_data['cache_hit_rate']) * (cache_hit_time + cache_miss_penalty)
            )
            
            memory_impact[pattern_name] = {
                'effective_access_time': effective_time,
                'cache_hit_rate': pattern_data['cache_hit_rate'],
                'performance_ratio': cache_hit_time / effective_time,
                'description': pattern_data['description']
            }
        
        return memory_impact
    
    def run_isa_design_comparison(self) -> Dict:
        """Compare LC-3 ISA design with other architectures"""
        print("🏗️ Running ISA Design Comparison...")
        
        isa_comparison = {
            'LC-3': {
                'word_size': 16,
                'instruction_size': 16,
                'register_count': 8,
                'addressing_modes': 6,
                'instruction_formats': 3,
                'opcode_bits': 4,
                'max_immediate': 5,  # bits
                'design_philosophy': 'Educational simplicity'
            },
            'MIPS': {
                'word_size': 32,
                'instruction_size': 32,
                'register_count': 32,
                'addressing_modes': 3,
                'instruction_formats': 3,
                'opcode_bits': 6,
                'max_immediate': 16,  # bits
                'design_philosophy': 'RISC efficiency'
            },
            'x86': {
                'word_size': 32,  # or 64
                'instruction_size': 'variable',
                'register_count': 8,  # general purpose
                'addressing_modes': 12,
                'instruction_formats': 'many',
                'opcode_bits': 'variable',
                'max_immediate': 32,  # bits
                'design_philosophy': 'CISC compatibility'
            },
            'ARM': {
                'word_size': 32,
                'instruction_size': 32,  # or 16 for Thumb
                'register_count': 16,
                'addressing_modes': 9,
                'instruction_formats': 6,
                'opcode_bits': 4,
                'max_immediate': 12,  # bits
                'design_philosophy': 'Power efficiency'
            }
        }
        
        # Calculate design efficiency metrics
        design_metrics = {}
        
        for arch_name, arch_data in isa_comparison.items():
            if isinstance(arch_data['instruction_size'], int):
                instruction_density = arch_data['instruction_size'] / arch_data['word_size']
                code_density = 1.0 / (arch_data['instruction_size'] / 8)  # instructions per byte
            else:
                instruction_density = 1.0  # Variable size
                code_density = 0.8  # Estimated for variable length
            
            register_efficiency = arch_data['register_count'] / arch_data['word_size']
            addressing_flexibility = arch_data['addressing_modes'] / 10.0  # Normalized
            
            design_metrics[arch_name] = {
                'instruction_density': instruction_density,
                'code_density': code_density,
                'register_efficiency': register_efficiency,
                'addressing_flexibility': addressing_flexibility,
                'overall_score': (instruction_density + code_density + 
                                register_efficiency + addressing_flexibility) / 4,
                'characteristics': arch_data
            }
        
        return design_metrics
    
    def _estimate_instruction_complexity(self, instruction: str) -> float:
        """Estimate instruction complexity based on operations"""
        complexity_map = {
            'ADD_reg': 1.0, 'ADD_imm': 1.1,
            'AND_reg': 1.0, 'AND_imm': 1.1,
            'NOT': 0.9,
            'LD': 1.5, 'ST': 1.4,
            'LDR': 1.3, 'STR': 1.3,
            'LDI': 2.0, 'STI': 2.0,
            'LEA': 1.2,
            'BR': 1.1, 'JMP': 1.0, 'JSR': 1.3,
            'TRAP': 1.8
        }
        return complexity_map.get(instruction, 1.0)
    
    def _estimate_cycles(self, instruction: str) -> int:
        """Estimate cycle count for instruction"""
        cycle_map = {
            'ADD_reg': 1, 'ADD_imm': 1,
            'AND_reg': 1, 'AND_imm': 1,
            'NOT': 1,
            'LD': 3, 'ST': 3,
            'LDR': 2, 'STR': 2,
            'LDI': 4, 'STI': 4,
            'LEA': 1,
            'BR': 2, 'JMP': 1, 'JSR': 2,
            'TRAP': 3
        }
        return cycle_map.get(instruction, 1)
    
    def _estimate_register_accesses(self, instruction: str) -> int:
        """Estimate number of register accesses"""
        if instruction.endswith('_reg'):
            return 3  # Two source, one dest
        elif instruction.endswith('_imm'):
            return 2  # One source, one dest
        elif instruction in ['LD', 'ST', 'LEA']:
            return 1  # One register
        elif instruction in ['LDR', 'STR']:
            return 2  # Base + dest/source
        else:
            return 1
    
    def _estimate_utilization(self, instruction: str) -> float:
        """Estimate functional unit utilization"""
        if instruction.startswith(('ADD', 'AND', 'NOT')):
            return 0.8  # ALU utilization
        elif instruction.startswith(('LD', 'ST')):
            return 0.6  # Memory unit utilization
        else:
            return 0.5  # Other units
    
    def _estimate_addressing_time(self, mode: str) -> float:
        """Estimate addressing mode execution time"""
        time_map = {
            'immediate': 40.0,
            'register': 38.0,
            'pc_relative': 45.0,
            'base_offset': 42.0,
            'indirect': 65.0
        }
        return time_map.get(mode, 50.0)
    
    def _get_addressing_memory_accesses(self, mode: str) -> int:
        """Get memory accesses for addressing mode"""
        access_map = {
            'immediate': 0,
            'register': 0,
            'pc_relative': 1,
            'base_offset': 1,
            'indirect': 2
        }
        return access_map.get(mode, 1)
    
    def _get_addressing_cycles(self, mode: str) -> int:
        """Get cycle count for addressing mode"""
        cycle_map = {
            'immediate': 1,
            'register': 1,
            'pc_relative': 2,
            'base_offset': 2,
            'indirect': 3
        }
        return cycle_map.get(mode, 2)
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive ISA design analysis report"""
        
        # Run all analyses
        format_analysis = self.run_instruction_format_analysis()
        addressing_analysis = self.run_addressing_mode_analysis()
        pipeline_analysis = self.run_pipeline_analysis()
        mix_analysis = self.run_instruction_mix_analysis()
        memory_analysis = self.run_memory_hierarchy_analysis()
        design_comparison = self.run_isa_design_comparison()
        
        # Generate report
        report = []
        report.append("# LC-3 ISA Design Performance Analysis")
        report.append("## Computer Architecture & MIPS-Style Performance Metrics")
        report.append("")
        report.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Analysis Type**: Comprehensive ISA Design Evaluation")
        report.append(f"**Simulator Available**: {SIMULATOR_AVAILABLE}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        
        if format_analysis:
            avg_r_type = format_analysis['R-type']['avg_time'] if 'avg_time' in format_analysis['R-type'] else format_analysis['R-type']['avg_complexity']
            avg_i_type = format_analysis['I-type']['avg_time'] if 'avg_time' in format_analysis['I-type'] else format_analysis['I-type']['avg_complexity']
            avg_j_type = format_analysis['J-type']['avg_time'] if 'avg_time' in format_analysis['J-type'] else format_analysis['J-type']['avg_complexity']
            
            report.append(f"**Instruction Format Performance**:")
            report.append(f"- R-type (Register): {avg_r_type:.3f}μs average")
            report.append(f"- I-type (Immediate): {avg_i_type:.3f}μs average")
            report.append(f"- J-type (Jump): {avg_j_type:.3f}μs average")
        
        if pipeline_analysis:
            unpipelined_cpi = pipeline_analysis['unpipelined']['average_cpi']
            realistic_cpi = pipeline_analysis['realistic_pipeline']['average_cpi']
            speedup = pipeline_analysis['realistic_pipeline']['throughput_improvement']
            
            report.append(f"")
            report.append(f"**Pipeline Potential**:")
            report.append(f"- Current CPI: {unpipelined_cpi:.2f}")
            report.append(f"- Pipelined CPI: {realistic_cpi:.2f}")
            report.append(f"- Potential Speedup: {speedup:.2f}x")
        
        report.append("")
        
        # Instruction Format Analysis
        report.append("## 1. Instruction Format Analysis")
        report.append("")
        report.append("### MIPS-Style Format Classification")
        report.append("")
        report.append("| Format Type | Count | Avg Time (μs) | Relative Performance | Characteristics |")
        report.append("|-------------|-------|---------------|---------------------|-----------------|")
        
        for format_type, data in format_analysis.items():
            avg_time = data.get('avg_time', data.get('avg_complexity', 0))
            rel_perf = avg_time / format_analysis['R-type'].get('avg_time', format_analysis['R-type'].get('avg_complexity', 1))
            
            characteristics = {
                'R-type': 'Register-register operations',
                'I-type': 'Immediate/memory operations',
                'J-type': 'Jump/branch operations'
            }
            
            report.append(f"| **{format_type}** | {data['count']} | {avg_time:.3f} | {rel_perf:.2f}x | {characteristics[format_type]} |")
        
        report.append("")
        report.append("### Format Efficiency Analysis")
        report.append("")
        report.append("✅ **R-type Instructions**: Most efficient for register operations")
        report.append("⚠️ **I-type Instructions**: Moderate efficiency, handle immediates and memory")
        report.append("🔄 **J-type Instructions**: Specialized for control flow")
        report.append("")
        
        # Addressing Mode Analysis
        report.append("## 2. Addressing Mode Performance")
        report.append("")
        report.append("| Addressing Mode | Avg Time (μs) | Memory Accesses | Cycles | Relative Cost | Description |")
        report.append("|-----------------|---------------|-----------------|--------|---------------|-------------|")
        
        for mode, data in addressing_analysis.items():
            report.append(f"| **{mode.replace('_', ' ').title()}** | {data['avg_time']:.2f} | {data['memory_accesses']} | {data['cycles_estimate']} | {data['relative_performance']:.2f}x | {data['description']} |")
        
        report.append("")
        report.append("### Addressing Mode Efficiency")
        report.append("")
        
        fastest_mode = min(addressing_analysis.items(), key=lambda x: x[1]['avg_time'])
        slowest_mode = max(addressing_analysis.items(), key=lambda x: x[1]['avg_time'])
        
        report.append(f"🚀 **Fastest**: {fastest_mode[0].replace('_', ' ').title()} ({fastest_mode[1]['avg_time']:.2f}μs)")
        report.append(f"🐌 **Slowest**: {slowest_mode[0].replace('_', ' ').title()} ({slowest_mode[1]['avg_time']:.2f}μs)")
        report.append(f"📊 **Performance Range**: {slowest_mode[1]['avg_time'] / fastest_mode[1]['avg_time']:.2f}x variation")
        report.append("")
        
        # Pipeline Analysis
        report.append("## 3. Pipeline Analysis & CPI Metrics")
        report.append("")
        
        for pipeline_type, data in pipeline_analysis.items():
            report.append(f"### {pipeline_type.replace('_', ' ').title()}")
            report.append(f"**Description**: {data['description']}")
            report.append(f"**Average CPI**: {data['average_cpi']:.2f}")
            
            if 'throughput_improvement' in data:
                report.append(f"**Throughput Improvement**: {data['throughput_improvement']:.2f}x")
            
            if 'instruction_cpi' in data:
                report.append("")
                report.append("| Instruction | CPI | Performance Impact |")
                report.append("|-------------|-----|-------------------|")
                for inst, cpi in data['instruction_cpi'].items():
                    impact = "Low" if cpi <= 1.5 else "Medium" if cpi <= 3.0 else "High"
                    report.append(f"| {inst} | {cpi:.1f} | {impact} |")
            
            report.append("")
        
        # Instruction Mix Analysis
        report.append("## 4. Instruction Mix Analysis")
        report.append("")
        report.append("### Performance by Workload Type")
        report.append("")
        report.append("| Workload | Weighted Avg Time (μs) | Instructions/sec | Bottleneck | Optimization Focus |")
        report.append("|----------|------------------------|------------------|------------|-------------------|")
        
        for mix_name, data in mix_analysis.items():
            optimization_focus = {
                'arithmetic': 'ALU operations',
                'memory': 'Memory hierarchy',
                'control': 'Branch prediction',
                'other': 'System calls'
            }
            
            report.append(f"| **{mix_name.title()}** | {data['weighted_avg_time']:.2f} | {data['instructions_per_second']:,.0f} | {data['bottleneck'].title()} | {optimization_focus[data['bottleneck']]} |")
        
        report.append("")
        
        # Memory Hierarchy Analysis
        report.append("## 5. Memory Hierarchy Impact")
        report.append("")
        report.append("| Access Pattern | Cache Hit Rate | Effective Time (cycles) | Performance Ratio | Impact |")
        report.append("|----------------|----------------|------------------------|-------------------|--------|")
        
        for pattern, data in memory_analysis.items():
            impact = "Low" if data['performance_ratio'] > 0.8 else "Medium" if data['performance_ratio'] > 0.5 else "High"
            report.append(f"| **{pattern.replace('_', ' ').title()}** | {data['cache_hit_rate']:.1%} | {data['effective_access_time']:.1f} | {data['performance_ratio']:.2f} | {impact} |")
        
        report.append("")
        
        # ISA Design Comparison
        report.append("## 6. ISA Design Comparison")
        report.append("")
        report.append("| Architecture | Word Size | Instruction Size | Registers | Addressing Modes | Design Score |")
        report.append("|--------------|-----------|------------------|-----------|------------------|-------------|")
        
        for arch, data in design_comparison.items():
            chars = data['characteristics']
            inst_size = chars['instruction_size']
            inst_size_str = f"{inst_size}" if isinstance(inst_size, int) else inst_size
            
            report.append(f"| **{arch}** | {chars['word_size']}-bit | {inst_size_str}-bit | {chars['register_count']} | {chars['addressing_modes']} | {data['overall_score']:.2f} |")
        
        report.append("")
        
        # Design Recommendations
        report.append("## 7. ISA Design Recommendations")
        report.append("")
        report.append("### 🚀 Performance Optimizations")
        report.append("")
        
        # Based on analysis results
        if addressing_analysis:
            slowest_addressing = max(addressing_analysis.items(), key=lambda x: x[1]['avg_time'])
            report.append(f"1. **Optimize {slowest_addressing[0].replace('_', ' ')} addressing**: Currently {slowest_addressing[1]['relative_performance']:.1f}x slower than fastest mode")
        
        if pipeline_analysis:
            speedup = pipeline_analysis['realistic_pipeline']['throughput_improvement']
            report.append(f"2. **Implement pipelining**: Potential {speedup:.1f}x performance improvement")
        
        report.append("3. **Cache optimization**: Focus on instruction and data locality")
        report.append("")
        
        report.append("### 🏗️ Architectural Improvements")
        report.append("")
        report.append("1. **Increase register count**: More registers reduce memory traffic")
        report.append("2. **Add parallel execution units**: Multiple ALUs for superscalar execution")
        report.append("3. **Implement branch prediction**: Reduce control hazard penalties")
        report.append("4. **Add specialized instructions**: Vector or SIMD operations")
        report.append("")
        
        report.append("### 📊 MIPS Design Principles Applied")
        report.append("")
        report.append("1. **Regularity**: Consistent instruction formats reduce decode complexity")
        report.append("2. **Simplicity**: Simple operations enable higher clock frequencies")
        report.append("3. **Common case optimization**: Frequent operations should be fast")
        report.append("4. **Good design demands good compromises**: Balance simplicity vs. performance")
        report.append("")
        
        # Performance Summary
        report.append("## 8. Performance Summary")
        report.append("")
        
        if self.instruction_metrics:
            total_instructions = len(self.instruction_metrics)
            avg_execution_time = statistics.mean([m.execution_time for m in self.instruction_metrics.values()])
            avg_throughput = statistics.mean([m.throughput for m in self.instruction_metrics.values()])
            
            report.append(f"**Instructions Analyzed**: {total_instructions}")
            report.append(f"**Average Execution Time**: {avg_execution_time*1e6:.2f}μs")
            report.append(f"**Average Throughput**: {avg_throughput:,.0f} ops/sec")
        
        if pipeline_analysis:
            current_cpi = pipeline_analysis['unpipelined']['average_cpi']
            optimal_cpi = pipeline_analysis['realistic_pipeline']['average_cpi']
            
            report.append(f"**Current CPI**: {current_cpi:.2f}")
            report.append(f"**Optimized CPI**: {optimal_cpi:.2f}")
            report.append(f"**Performance Potential**: {current_cpi/optimal_cpi:.1f}x improvement")
        
        report.append("")
        report.append("### Overall Assessment")
        report.append("")
        
        lc3_score = design_comparison['LC-3']['overall_score']
        mips_score = design_comparison['MIPS']['overall_score']
        
        if lc3_score >= 0.8:
            assessment = "Excellent"
        elif lc3_score >= 0.6:
            assessment = "Good"
        elif lc3_score >= 0.4:
            assessment = "Adequate"
        else:
            assessment = "Needs Improvement"
        
        report.append(f"**LC-3 ISA Rating**: {assessment} ({lc3_score:.2f}/1.0)")
        report.append(f"**Comparison to MIPS**: {lc3_score/mips_score:.2f}x relative efficiency")
        report.append("")
        report.append("The LC-3 ISA demonstrates strong educational value with reasonable performance characteristics.")
        report.append("While optimized for simplicity over performance, it provides excellent learning opportunities")
        report.append("for understanding fundamental computer architecture concepts.")
        
        return "\n".join(report)


def main():
    """Main function to run ISA performance analysis"""
    print("🔬 LC-3 ISA Design Performance Analysis")
    print("=" * 50)
    
    analyzer = LC3ISAAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    # Save report
    timestamp = str(int(time.time()))
    report_file = Path(f"reports/isa_design_analysis_{timestamp}.md")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✅ ISA Design Analysis completed!")
    print(f"📄 Report saved to: {report_file}")
    
    # Also save as JSON for further analysis
    json_file = report_file.with_suffix('.json')
    
    analysis_data = {
        'timestamp': timestamp,
        'simulator_available': SIMULATOR_AVAILABLE,
        'instruction_metrics': {
            name: {
                'opcode': metrics.opcode,
                'format_type': metrics.format_type,
                'cycles': metrics.cycles,
                'memory_accesses': metrics.memory_accesses,
                'execution_time': metrics.execution_time,
                'throughput': metrics.throughput
            }
            for name, metrics in analyzer.instruction_metrics.items()
        }
    }
    
    with open(json_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"📊 Analysis data saved to: {json_file}")
    
    return report_file


if __name__ == "__main__":
    main()
