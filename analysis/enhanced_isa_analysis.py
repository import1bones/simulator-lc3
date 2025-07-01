#!/usr/bin/env python3
"""
Enhanced LC-3 ISA Design Analysis with MIPS-Style Metrics

This module provides comprehensive ISA design analysis with focus on:
- MIPS-style architectural metrics (CPI, IPC, throughput)
- Instruction set efficiency and design trade-offs
- Pipeline performance potential analysis
- Memory hierarchy impact assessment
- Instruction encoding efficiency
- Comparative analysis with RISC architectures
"""

import time
import sys
import statistics
import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import datetime

# Add the build directory to Python path for lc3_simulator
sys.path.insert(0, str(Path(__file__).parent.parent / "build"))

try:
    import lc3_simulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("Warning: lc3_simulator module not available. Using estimated metrics.")


@dataclass
class InstructionAnalysis:
    """Detailed analysis of individual instruction characteristics"""
    opcode: str
    instruction_class: str  # arithmetic, memory, control, misc
    format_type: str  # R-type, I-type, J-type
    cycles_unpipelined: int
    cycles_pipelined: float
    memory_operations: int
    register_dependencies: int
    encoding_efficiency: float  # bits utilized / total bits
    pipeline_stages: List[str]
    hazard_potential: int  # 0-5 scale
    throughput_factor: float


@dataclass
class ISAMetrics:
    """Comprehensive ISA design metrics"""
    # Performance metrics
    average_cpi_unpipelined: float
    average_cpi_pipelined: float
    ipc_potential: float  # Instructions per cycle potential
    throughput_efficiency: float

    # Instruction set characteristics
    instruction_density: float  # instructions per byte
    encoding_efficiency: float  # average utilization of instruction bits
    orthogonality_score: float  # measure of instruction set regularity

    # Memory hierarchy metrics
    memory_bandwidth_utilization: float
    locality_friendliness: float

    # Pipeline characteristics
    pipeline_efficiency: float
    hazard_frequency: float
    branch_penalty: float

    # RISC principles adherence
    risc_score: float  # 0-100, how well it follows RISC principles


class EnhancedLC3Analyzer:
    """Enhanced LC-3 ISA analyzer with MIPS-style metrics"""

    def __init__(self):
        self.simulator = None
        if SIMULATOR_AVAILABLE:
            self.simulator = lc3_simulator.LC3Simulator()

        # Enhanced instruction classification
        self.instruction_database = {
            'ADD_reg': {
                'class': 'arithmetic', 'format': 'R-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 3, 'encoding_eff': 0.875,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'ADD_imm': {
                'class': 'arithmetic', 'format': 'I-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 2, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'AND_reg': {
                'class': 'arithmetic', 'format': 'R-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 3, 'encoding_eff': 0.875,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'AND_imm': {
                'class': 'arithmetic', 'format': 'I-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 2, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'NOT': {
                'class': 'arithmetic', 'format': 'R-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 2, 'encoding_eff': 0.625,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'LD': {
                'class': 'memory', 'format': 'I-type', 'cycles': 2,
                'memory_ops': 1, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM', 'WB'], 'hazard': 3
            },
            'ST': {
                'class': 'memory', 'format': 'I-type', 'cycles': 2,
                'memory_ops': 1, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM'], 'hazard': 2
            },
            'LDR': {
                'class': 'memory', 'format': 'I-type', 'cycles': 2,
                'memory_ops': 1, 'reg_deps': 2, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM', 'WB'], 'hazard': 3
            },
            'STR': {
                'class': 'memory', 'format': 'I-type', 'cycles': 2,
                'memory_ops': 1, 'reg_deps': 2, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM'], 'hazard': 2
            },
            'LDI': {
                'class': 'memory', 'format': 'I-type', 'cycles': 3,
                'memory_ops': 2, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM', 'MEM2', 'WB'], 'hazard': 4
            },
            'STI': {
                'class': 'memory', 'format': 'I-type', 'cycles': 3,
                'memory_ops': 2, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'MEM', 'MEM2'], 'hazard': 3
            },
            'LEA': {
                'class': 'arithmetic', 'format': 'I-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 1
            },
            'BR': {
                'class': 'control', 'format': 'I-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 0, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX'], 'hazard': 4
            },
            'JMP': {
                'class': 'control', 'format': 'J-type', 'cycles': 1,
                'memory_ops': 0, 'reg_deps': 1, 'encoding_eff': 0.5625,
                'stages': ['IF', 'ID', 'EX'], 'hazard': 5
            },
            'JSR': {
                'class': 'control', 'format': 'J-type', 'cycles': 2,
                'memory_ops': 0, 'reg_deps': 1, 'encoding_eff': 0.9375,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 5
            },
            'JSRR': {
                'class': 'control', 'format': 'J-type', 'cycles': 2,
                'memory_ops': 0, 'reg_deps': 2, 'encoding_eff': 0.5625,
                'stages': ['IF', 'ID', 'EX', 'WB'], 'hazard': 5
            },
            'TRAP': {
                'class': 'misc', 'format': 'I-type', 'cycles': 3,
                'memory_ops': 1, 'reg_deps': 1, 'encoding_eff': 0.75,
                'stages': ['IF', 'ID', 'EX', 'MEM', 'WB'], 'hazard': 3
            }
        }

        # MIPS comparison baseline
        self.mips_baseline = {
            'cpi': 1.0,
            'encoding_efficiency': 1.0,  # 32 bits fully utilized
            'pipeline_stages': 5,
            'hazard_frequency': 0.15,
            'risc_score': 95
        }

        self.analysis_results = {}

    def analyze_instruction_characteristics(self) -> Dict[str, InstructionAnalysis]:
        """Detailed analysis of each instruction type"""
        print("🔍 Analyzing Instruction Characteristics...")

        instruction_analyses = {}

        for opcode, info in self.instruction_database.items():
            # Calculate pipelined cycles (with hazard considerations)
            pipelined_cycles = 1.0 + (info['hazard'] * 0.2)  # Base + hazard penalty

            # Calculate throughput factor
            throughput_factor = info['cycles'] / pipelined_cycles

            analysis = InstructionAnalysis(
                opcode=opcode,
                instruction_class=info['class'],
                format_type=info['format'],
                cycles_unpipelined=info['cycles'],
                cycles_pipelined=pipelined_cycles,
                memory_operations=info['memory_ops'],
                register_dependencies=info['reg_deps'],
                encoding_efficiency=info['encoding_eff'],
                pipeline_stages=info['stages'],
                hazard_potential=info['hazard'],
                throughput_factor=throughput_factor
            )

            instruction_analyses[opcode] = analysis

        return instruction_analyses

    def calculate_cpi_analysis(self, instruction_mix: Dict[str, float] = None) -> Dict:
        """Calculate CPI for different scenarios"""
        print("⚡ Calculating CPI Analysis...")

        if instruction_mix is None:
            # Default realistic instruction mix
            instruction_mix = {
                'ADD_reg': 0.12, 'ADD_imm': 0.08, 'AND_reg': 0.06, 'AND_imm': 0.04,
                'NOT': 0.03, 'LD': 0.15, 'ST': 0.12, 'LDR': 0.08, 'STR': 0.07,
                'LDI': 0.03, 'STI': 0.02, 'LEA': 0.04, 'BR': 0.12, 'JMP': 0.02,
                'JSR': 0.02, 'JSRR': 0.01, 'TRAP': 0.01
            }

        # Unpipelined CPI
        unpipelined_cpi = sum(
            self.instruction_database[inst]['cycles'] * freq
            for inst, freq in instruction_mix.items()
            if inst in self.instruction_database
        )

        # Pipelined CPI (ideal)
        ideal_pipelined_cpi = 1.0

        # Realistic pipelined CPI (with hazards)
        hazard_penalties = {
            1: 0.1,   # Low hazard
            2: 0.2,   # Medium-low hazard
            3: 0.4,   # Medium hazard
            4: 0.6,   # High hazard
            5: 1.0    # Very high hazard (branches)
        }

        realistic_pipelined_cpi = sum(
            (1.0 + hazard_penalties[self.instruction_database[inst]['hazard']]) * freq
            for inst, freq in instruction_mix.items()
            if inst in self.instruction_database
        )

        return {
            'unpipelined': {
                'cpi': unpipelined_cpi,
                'ipc': 1.0 / unpipelined_cpi,
                'description': 'Current LC-3 implementation'
            },
            'ideal_pipelined': {
                'cpi': ideal_pipelined_cpi,
                'ipc': 1.0 / ideal_pipelined_cpi,
                'speedup': unpipelined_cpi / ideal_pipelined_cpi,
                'description': 'Perfect pipeline with no hazards'
            },
            'realistic_pipelined': {
                'cpi': realistic_pipelined_cpi,
                'ipc': 1.0 / realistic_pipelined_cpi,
                'speedup': unpipelined_cpi / realistic_pipelined_cpi,
                'description': 'Realistic pipeline with hazards and stalls'
            }
        }

    def analyze_encoding_efficiency(self) -> Dict:
        """Analyze instruction encoding efficiency"""
        print("🔢 Analyzing Instruction Encoding Efficiency...")

        # LC-3 uses 16-bit instructions
        total_bits = 16

        encoding_analysis = {}
        format_efficiency = defaultdict(list)

        for opcode, info in self.instruction_database.items():
            utilized_bits = info['encoding_eff'] * total_bits
            efficiency = info['encoding_eff']

            encoding_analysis[opcode] = {
                'total_bits': total_bits,
                'utilized_bits': utilized_bits,
                'efficiency': efficiency,
                'wasted_bits': total_bits - utilized_bits
            }

            format_efficiency[info['format']].append(efficiency)

        # Calculate format-wise efficiency
        format_summary = {}
        for format_type, efficiencies in format_efficiency.items():
            format_summary[format_type] = {
                'average_efficiency': statistics.mean(efficiencies),
                'min_efficiency': min(efficiencies),
                'max_efficiency': max(efficiencies),
                'count': len(efficiencies)
            }

        overall_efficiency = statistics.mean([
            info['encoding_eff'] for info in self.instruction_database.values()
        ])

        return {
            'overall_efficiency': overall_efficiency,
            'instruction_analysis': encoding_analysis,
            'format_summary': format_summary,
            'comparison_to_mips': {
                'lc3_efficiency': overall_efficiency,
                'mips_efficiency': self.mips_baseline['encoding_efficiency'],
                'relative_efficiency': overall_efficiency / self.mips_baseline['encoding_efficiency']
            }
        }

    def analyze_risc_adherence(self) -> Dict:
        """Analyze adherence to RISC design principles"""
        print("🏗️ Analyzing RISC Design Principles Adherence...")

        risc_metrics = {
            'simple_instructions': 0,
            'uniform_instruction_size': 100,  # LC-3 has uniform 16-bit instructions
            'few_addressing_modes': 75,      # Limited addressing modes
            'load_store_architecture': 85,   # Mostly load/store with some exceptions
            'large_register_file': 40,       # Only 8 registers
            'fixed_instruction_format': 60,  # 3 main formats but some variation
            'pipeline_friendly': 70,         # Reasonable pipeline characteristics
            'orthogonal_instruction_set': 80 # Good orthogonality
        }

        # Calculate simple instructions percentage
        simple_ops = ['ADD_reg', 'ADD_imm', 'AND_reg', 'AND_imm', 'NOT', 'LEA']
        total_ops = len(self.instruction_database)
        risc_metrics['simple_instructions'] = (len(simple_ops) / total_ops) * 100

        # Overall RISC score
        risc_score = statistics.mean(risc_metrics.values())

        return {
            'overall_risc_score': risc_score,
            'principle_scores': risc_metrics,
            'comparison_to_mips': {
                'lc3_risc_score': risc_score,
                'mips_risc_score': self.mips_baseline['risc_score'],
                'relative_score': risc_score / self.mips_baseline['risc_score']
            },
            'recommendations': self._generate_risc_recommendations(risc_metrics)
        }

    def analyze_memory_hierarchy_impact(self) -> Dict:
        """Analyze memory hierarchy characteristics"""
        print("🗃️ Analyzing Memory Hierarchy Impact...")

        memory_analysis = {
            'instruction_classes': {},
            'addressing_modes': {},
            'cache_impact': {},
            'bandwidth_utilization': {}
        }

        # Analyze by instruction class
        for class_name in ['arithmetic', 'memory', 'control', 'misc']:
            class_instructions = [
                inst for inst, info in self.instruction_database.items()
                if info['class'] == class_name
            ]

            if class_instructions:
                avg_memory_ops = statistics.mean([
                    self.instruction_database[inst]['memory_ops']
                    for inst in class_instructions
                ])

                memory_analysis['instruction_classes'][class_name] = {
                    'instruction_count': len(class_instructions),
                    'avg_memory_operations': avg_memory_ops,
                    'memory_intensity': avg_memory_ops / max(1, len(class_instructions))
                }

        # Addressing mode analysis
        addressing_modes = {
            'immediate': ['ADD_imm', 'AND_imm'],
            'register': ['ADD_reg', 'AND_reg', 'NOT', 'JMP', 'JSRR'],
            'pc_relative': ['LD', 'ST', 'LEA', 'BR', 'JSR'],
            'base_offset': ['LDR', 'STR'],
            'indirect': ['LDI', 'STI']
        }

        for mode, instructions in addressing_modes.items():
            if instructions:
                avg_cycles = statistics.mean([
                    self.instruction_database[inst]['cycles']
                    for inst in instructions
                    if inst in self.instruction_database
                ])

                memory_analysis['addressing_modes'][mode] = {
                    'instruction_count': len(instructions),
                    'avg_cycles': avg_cycles,
                    'cache_friendliness': self._estimate_cache_friendliness(mode)
                }

        return memory_analysis

    def _estimate_cache_friendliness(self, addressing_mode: str) -> float:
        """Estimate cache friendliness of addressing mode (0-1 scale)"""
        friendliness_scores = {
            'immediate': 1.0,     # No memory access
            'register': 1.0,      # No memory access
            'pc_relative': 0.8,   # Good locality
            'base_offset': 0.7,   # Reasonable locality
            'indirect': 0.4       # Poor locality due to indirection
        }
        return friendliness_scores.get(addressing_mode, 0.5)

    def _generate_risc_recommendations(self, risc_metrics: Dict) -> List[str]:
        """Generate recommendations for improving RISC adherence"""
        recommendations = []

        if risc_metrics['large_register_file'] < 60:
            recommendations.append("Consider expanding register file (currently 8 registers)")

        if risc_metrics['few_addressing_modes'] < 80:
            recommendations.append("Simplify addressing modes for better RISC adherence")

        if risc_metrics['pipeline_friendly'] < 80:
            recommendations.append("Optimize instructions for pipeline efficiency")

        if risc_metrics['simple_instructions'] < 70:
            recommendations.append("Increase proportion of simple arithmetic instructions")

        return recommendations

    def generate_comprehensive_isa_metrics(self) -> ISAMetrics:
        """Generate comprehensive ISA design metrics"""
        print("📈 Generating Comprehensive ISA Metrics...")

        # Run all analyses
        instruction_analyses = self.analyze_instruction_characteristics()
        cpi_analysis = self.calculate_cpi_analysis()
        encoding_analysis = self.analyze_encoding_efficiency()
        risc_analysis = self.analyze_risc_adherence()
        memory_analysis = self.analyze_memory_hierarchy_impact()

        # Calculate aggregate metrics
        avg_cpi_unpipelined = cpi_analysis['unpipelined']['cpi']
        avg_cpi_pipelined = cpi_analysis['realistic_pipelined']['cpi']
        ipc_potential = 1.0 / avg_cpi_pipelined

        # Instruction density (instructions per byte)
        instruction_density = 1.0 / 2.0  # 16-bit instructions = 2 bytes per instruction

        # Encoding efficiency
        encoding_efficiency = encoding_analysis['overall_efficiency']

        # Orthogonality score (from RISC analysis)
        orthogonality_score = risc_analysis['principle_scores']['orthogonal_instruction_set']

        # Memory bandwidth utilization
        memory_ops_per_inst = statistics.mean([
            info['memory_ops'] for info in self.instruction_database.values()
        ])
        memory_bandwidth_utilization = memory_ops_per_inst / 2.0  # Normalize

        # Pipeline efficiency
        pipeline_efficiency = (avg_cpi_unpipelined - avg_cpi_pipelined) / avg_cpi_unpipelined

        # Hazard frequency
        hazard_frequency = statistics.mean([
            info['hazard'] / 5.0 for info in self.instruction_database.values()
        ])

        return ISAMetrics(
            average_cpi_unpipelined=avg_cpi_unpipelined,
            average_cpi_pipelined=avg_cpi_pipelined,
            ipc_potential=ipc_potential,
            throughput_efficiency=pipeline_efficiency,
            instruction_density=instruction_density,
            encoding_efficiency=encoding_efficiency,
            orthogonality_score=orthogonality_score / 100.0,
            memory_bandwidth_utilization=memory_bandwidth_utilization,
            locality_friendliness=0.7,  # Estimated based on addressing modes
            pipeline_efficiency=pipeline_efficiency,
            hazard_frequency=hazard_frequency,
            branch_penalty=2.0,  # Estimated branch penalty in cycles
            risc_score=risc_analysis['overall_risc_score']
        )

    def run_complete_analysis(self) -> Dict:
        """Run complete ISA design analysis"""
        print("🚀 Running Complete Enhanced ISA Design Analysis...")
        print("=" * 60)

        start_time = time.time()

        # Run all analyses
        results = {
            'metadata': {
                'timestamp': datetime.datetime.now().isoformat(),
                'simulator_available': SIMULATOR_AVAILABLE,
                'analysis_type': 'Enhanced ISA Design Analysis'
            },
            'instruction_characteristics': self.analyze_instruction_characteristics(),
            'cpi_analysis': self.calculate_cpi_analysis(),
            'encoding_efficiency': self.analyze_encoding_efficiency(),
            'risc_adherence': self.analyze_risc_adherence(),
            'memory_hierarchy': self.analyze_memory_hierarchy_impact(),
            'comprehensive_metrics': self.generate_comprehensive_isa_metrics()
        }

        execution_time = time.time() - start_time
        results['metadata']['execution_time_seconds'] = execution_time

        print(f"✅ Analysis completed in {execution_time:.3f} seconds")
        return results

    def generate_markdown_report(self, results: Dict) -> str:
        """Generate comprehensive markdown report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        report = f"""# Enhanced LC-3 ISA Design Analysis Report

*Generated on: {results['metadata']['timestamp']}*
*Analysis Type: {results['metadata']['analysis_type']}*
*Execution Time: {results['metadata']['execution_time_seconds']:.3f} seconds*

## Executive Summary

This report provides a comprehensive analysis of the LC-3 Instruction Set Architecture (ISA)
design from a MIPS-style architectural perspective, focusing on performance metrics,
instruction efficiency, and design trade-offs.

### Key Findings

"""

        # Add comprehensive metrics summary
        metrics = results['comprehensive_metrics']
        report += f"""
| Metric | Value | Assessment |
|--------|-------|------------|
| **CPI (Unpipelined)** | {metrics.average_cpi_unpipelined:.3f} | {"Good" if metrics.average_cpi_unpipelined < 2.0 else "Needs Improvement"} |
| **CPI (Pipelined)** | {metrics.average_cpi_pipelined:.3f} | {"Excellent" if metrics.average_cpi_pipelined < 1.5 else "Good" if metrics.average_cpi_pipelined < 2.0 else "Poor"} |
| **IPC Potential** | {metrics.ipc_potential:.3f} | {"High" if metrics.ipc_potential > 0.7 else "Medium" if metrics.ipc_potential > 0.5 else "Low"} |
| **Instruction Density** | {metrics.instruction_density:.3f} inst/byte | {"Efficient" if metrics.instruction_density > 0.4 else "Moderate"} |
| **Encoding Efficiency** | {metrics.encoding_efficiency:.1%} | {"Good" if metrics.encoding_efficiency > 0.8 else "Moderate"} |
| **RISC Score** | {metrics.risc_score:.1f}/100 | {"Excellent" if metrics.risc_score > 80 else "Good" if metrics.risc_score > 60 else "Poor"} |
| **Pipeline Efficiency** | {metrics.pipeline_efficiency:.1%} | {"High" if metrics.pipeline_efficiency > 0.4 else "Moderate"} |
| **Hazard Frequency** | {metrics.hazard_frequency:.1%} | {"Low" if metrics.hazard_frequency < 0.3 else "Moderate" if metrics.hazard_frequency < 0.5 else "High"} |

"""

        # CPI Analysis Section
        cpi_data = results['cpi_analysis']
        report += f"""
## CPI (Cycles Per Instruction) Analysis

### Performance Comparison

| Implementation | CPI | IPC | Speedup | Description |
|----------------|-----|-----|---------|-------------|
| **Unpipelined** | {cpi_data['unpipelined']['cpi']:.3f} | {cpi_data['unpipelined']['ipc']:.3f} | 1.0× | {cpi_data['unpipelined']['description']} |
| **Ideal Pipelined** | {cpi_data['ideal_pipelined']['cpi']:.3f} | {cpi_data['ideal_pipelined']['ipc']:.3f} | {cpi_data['ideal_pipelined']['speedup']:.2f}× | {cpi_data['ideal_pipelined']['description']} |
| **Realistic Pipelined** | {cpi_data['realistic_pipelined']['cpi']:.3f} | {cpi_data['realistic_pipelined']['ipc']:.3f} | {cpi_data['realistic_pipelined']['speedup']:.2f}× | {cpi_data['realistic_pipelined']['description']} |

### Analysis
- **Pipeline Potential**: The LC-3 could achieve up to {cpi_data['ideal_pipelined']['speedup']:.2f}× speedup with perfect pipelining
- **Realistic Gains**: With hazards and stalls, expected speedup is {cpi_data['realistic_pipelined']['speedup']:.2f}×
- **Bottlenecks**: {"Memory operations and branch instructions limit pipeline efficiency" if cpi_data['realistic_pipelined']['speedup'] < 1.5 else "Good pipeline characteristics with manageable hazards"}

"""

        # Instruction Characteristics
        inst_chars = results['instruction_characteristics']
        report += """
## Instruction Characteristics Analysis

### Instruction Format Distribution

"""

        format_counts = Counter(char.format_type for char in inst_chars.values())
        for format_type, count in format_counts.items():
            percentage = (count / len(inst_chars)) * 100
            report += f"- **{format_type}**: {count} instructions ({percentage:.1f}%)\n"

        report += """
### Performance by Instruction Class

| Instruction | Class | Format | Cycles (Unpipelined) | Cycles (Pipelined) | Hazard Risk | Encoding Efficiency |
|-------------|-------|--------|---------------------|-------------------|-------------|-------------------|
"""

        for opcode, char in sorted(inst_chars.items()):
            hazard_desc = ["Very Low", "Low", "Medium", "High", "Very High"][min(char.hazard_potential, 4)]
            report += f"| {opcode} | {char.instruction_class} | {char.format_type} | {char.cycles_unpipelined} | {char.cycles_pipelined:.2f} | {hazard_desc} | {char.encoding_efficiency:.1%} |\n"

        # Encoding Efficiency Analysis
        encoding_data = results['encoding_efficiency']
        report += f"""
## Instruction Encoding Efficiency

### Overall Efficiency: {encoding_data['overall_efficiency']:.1%}

The LC-3 uses 16-bit instructions with the following efficiency characteristics:

"""

        for format_type, data in encoding_data['format_summary'].items():
            report += f"""
### {format_type} Format
- **Average Efficiency**: {data['average_efficiency']:.1%}
- **Range**: {data['min_efficiency']:.1%} - {data['max_efficiency']:.1%}
- **Instruction Count**: {data['count']}
"""

        # RISC Adherence Analysis
        risc_data = results['risc_adherence']
        report += f"""
## RISC Design Principles Adherence

### Overall RISC Score: {risc_data['overall_risc_score']:.1f}/100

| Principle | Score | Assessment |
|-----------|-------|------------|
"""

        for principle, score in risc_data['principle_scores'].items():
            assessment = "Excellent" if score > 80 else "Good" if score > 60 else "Needs Improvement"
            formatted_principle = principle.replace('_', ' ').title()
            report += f"| {formatted_principle} | {score:.1f} | {assessment} |\n"

        if risc_data['recommendations']:
            report += "\n### Recommendations for RISC Improvement\n\n"
            for i, rec in enumerate(risc_data['recommendations'], 1):
                report += f"{i}. {rec}\n"

        # Memory Hierarchy Analysis
        memory_data = results['memory_hierarchy']
        report += """
## Memory Hierarchy Impact Analysis

### Instruction Class Memory Characteristics

| Class | Instructions | Avg Memory Ops | Memory Intensity |
|-------|-------------|----------------|------------------|
"""

        for class_name, data in memory_data['instruction_classes'].items():
            report += f"| {class_name.title()} | {data['instruction_count']} | {data['avg_memory_operations']:.2f} | {data['memory_intensity']:.2f} |\n"

        report += """
### Addressing Mode Analysis

| Addressing Mode | Instructions | Avg Cycles | Cache Friendliness |
|----------------|-------------|------------|-------------------|
"""

        for mode, data in memory_data['addressing_modes'].items():
            friendliness = "High" if data['cache_friendliness'] > 0.7 else "Medium" if data['cache_friendliness'] > 0.5 else "Low"
            report += f"| {mode.replace('_', ' ').title()} | {data['instruction_count']} | {data['avg_cycles']:.1f} | {friendliness} |\n"

        # Comparison with MIPS
        report += f"""
## Comparison with MIPS Architecture

| Metric | LC-3 | MIPS (Baseline) | Relative Performance |
|--------|------|----------------|---------------------|
| RISC Score | {risc_data['overall_risc_score']:.1f} | {risc_data['comparison_to_mips']['mips_risc_score']} | {risc_data['comparison_to_mips']['relative_score']:.2f}× |
| Encoding Efficiency | {encoding_data['overall_efficiency']:.1%} | {encoding_data['comparison_to_mips']['mips_efficiency']:.1%} | {encoding_data['comparison_to_mips']['relative_efficiency']:.2f}× |
| Pipeline Stages | 5 (estimated) | 5 (classic MIPS) | Equal |
| Register File Size | 8 | 32 | 0.25× |

## Conclusions and Recommendations

### Strengths
1. **Uniform Instruction Size**: 16-bit instructions provide good code density
2. **Simple Pipeline**: Straightforward pipeline implementation possible
3. **Orthogonal Design**: Most instructions follow consistent patterns

### Areas for Improvement
1. **Register File**: Limited 8-register file constrains performance
2. **Addressing Modes**: Some complex modes (indirect) hurt pipeline efficiency
3. **Instruction Mix**: More arithmetic instructions would improve RISC characteristics

### Performance Potential
- **Current Performance**: CPI of {metrics.average_cpi_unpipelined:.2f} (unpipelined)
- **Pipeline Potential**: Could achieve {cpi_data['realistic_pipelined']['speedup']:.2f}× speedup with realistic pipelining
- **RISC Score**: {metrics.risc_score:.1f}/100 indicates {"good" if metrics.risc_score > 60 else "moderate"} RISC adherence

### Recommendations
1. Consider expanding register file to 16 or 32 registers
2. Simplify or optimize indirect addressing mode
3. Add more simple arithmetic operations
4. Implement branch prediction for control hazards
5. Consider cache-friendly instruction scheduling

---
*End of Enhanced LC-3 ISA Design Analysis Report*
"""

        return report


def main():
    """Main execution function"""
    print("🚀 Enhanced LC-3 ISA Design Analysis")
    print("=" * 50)

    analyzer = EnhancedLC3Analyzer()

    # Run complete analysis
    results = analyzer.run_complete_analysis()

    # Generate timestamp for unique filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save results to JSON
    results_file = f"enhanced_isa_analysis_{timestamp}.json"
    # Convert dataclass objects to dictionaries for JSON serialization
    json_results = {}
    for key, value in results.items():
        if key == 'instruction_characteristics':
            json_results[key] = {k: asdict(v) for k, v in value.items()}
        elif key == 'comprehensive_metrics':
            json_results[key] = asdict(value)
        else:
            json_results[key] = value

    with open(results_file, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)

    # Generate and save markdown report
    report = analyzer.generate_markdown_report(results)
    report_file = f"../reports/enhanced_isa_analysis_{timestamp}.md"

    # Ensure reports directory exists
    Path("../reports").mkdir(exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n✅ Analysis complete!")
    print(f"📊 Results saved to: {results_file}")
    print(f"📋 Report saved to: {report_file}")

    # Print summary
    metrics = results['comprehensive_metrics']
    print(f"\n📈 Key Metrics Summary:")
    print(f"   CPI (Current): {metrics.average_cpi_unpipelined:.3f}")
    print(f"   CPI (Pipelined): {metrics.average_cpi_pipelined:.3f}")
    print(f"   IPC Potential: {metrics.ipc_potential:.3f}")
    print(f"   RISC Score: {metrics.risc_score:.1f}/100")
    print(f"   Encoding Efficiency: {metrics.encoding_efficiency:.1%}")


if __name__ == "__main__":
    main()
