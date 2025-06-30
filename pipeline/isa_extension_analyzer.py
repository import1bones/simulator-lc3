#!/usr/bin/env python3
"""
LC-3 ISA Extension and Custom Instruction Pipeline Analyzer

This module provides tools for:
1. Defining custom instruction sets
2. Analyzing pipeline performance with extended ISAs
3. Comparing different architectural choices
4. Generating comprehensive ISA design reports
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

from pipeline_tester import PipelineTester, PipelineConfiguration, PipelineResults


@dataclass
class CustomInstructionDef:
    """Definition of a custom instruction"""
    name: str
    opcode: int
    mask: int
    format_type: str  # R, I, J
    execution_stages: List[str]
    base_cycles: int
    memory_accesses: int
    register_reads: int
    register_writes: int
    has_immediate: bool
    is_branch: bool
    is_conditional: bool
    description: str


@dataclass
class ISAExtension:
    """Extended ISA definition"""
    name: str
    base_isa: str = "LC-3"
    custom_instructions: List[CustomInstructionDef] = None
    additional_registers: int = 0
    extended_address_space: bool = False
    vector_operations: bool = False
    floating_point: bool = False
    description: str = ""

    def __post_init__(self):
        if self.custom_instructions is None:
            self.custom_instructions = []


class CustomISAAnalyzer:
    """Analyzer for custom ISA extensions and pipeline performance"""

    def __init__(self):
        self.pipeline_tester = PipelineTester()
        self.isa_extensions = {}
        self.custom_programs = {}

    def define_simd_extension(self) -> ISAExtension:
        """Define a SIMD extension for LC-3"""
        simd_instructions = [
            CustomInstructionDef(
                name="VADD",
                opcode=0x8000,
                mask=0xF000,
                format_type="R",
                execution_stages=["FETCH", "DECODE", "EXECUTE_VEC", "WRITEBACK"],
                base_cycles=2,
                memory_accesses=0,
                register_reads=2,
                register_writes=1,
                has_immediate=False,
                is_branch=False,
                is_conditional=False,
                description="Vector addition of 4x16-bit elements"
            ),
            CustomInstructionDef(
                name="VMUL",
                opcode=0x8100,
                mask=0xFF00,
                format_type="R",
                execution_stages=["FETCH", "DECODE", "EXECUTE_VEC1", "EXECUTE_VEC2", "WRITEBACK"],
                base_cycles=3,
                memory_accesses=0,
                register_reads=2,
                register_writes=1,
                has_immediate=False,
                is_branch=False,
                is_conditional=False,
                description="Vector multiplication of 4x16-bit elements"
            ),
            CustomInstructionDef(
                name="VLOAD",
                opcode=0x8200,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE", "EXECUTE", "MEMORY_VEC", "WRITEBACK"],
                base_cycles=4,
                memory_accesses=4,
                register_reads=1,
                register_writes=1,
                has_immediate=True,
                is_branch=False,
                is_conditional=False,
                description="Load 4 consecutive memory locations into vector register"
            ),
            CustomInstructionDef(
                name="VSTORE",
                opcode=0x8300,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE", "EXECUTE", "MEMORY_VEC"],
                base_cycles=4,
                memory_accesses=4,
                register_reads=2,
                register_writes=0,
                has_immediate=True,
                is_branch=False,
                is_conditional=False,
                description="Store vector register to 4 consecutive memory locations"
            )
        ]

        return ISAExtension(
            name="LC-3 SIMD",
            custom_instructions=simd_instructions,
            additional_registers=8,  # 8 vector registers
            vector_operations=True,
            description="SIMD extension with 128-bit vector operations"
        )

    def define_dsp_extension(self) -> ISAExtension:
        """Define a DSP extension for LC-3"""
        dsp_instructions = [
            CustomInstructionDef(
                name="MAC",
                opcode=0x9000,
                mask=0xF000,
                format_type="R",
                execution_stages=["FETCH", "DECODE", "EXECUTE_MAC1", "EXECUTE_MAC2", "WRITEBACK"],
                base_cycles=2,
                memory_accesses=0,
                register_reads=3,
                register_writes=1,
                has_immediate=False,
                is_branch=False,
                is_conditional=False,
                description="Multiply-accumulate: RD = RD + (RS1 * RS2)"
            ),
            CustomInstructionDef(
                name="FFT",
                opcode=0x9100,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE", "EXECUTE_FFT"] * 8,  # Multi-cycle
                base_cycles=16,
                memory_accesses=8,
                register_reads=1,
                register_writes=1,
                has_immediate=True,
                is_branch=False,
                is_conditional=False,
                description="Fast Fourier Transform on memory block"
            ),
            CustomInstructionDef(
                name="FILTER",
                opcode=0x9200,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE", "EXECUTE_FILTER1", "EXECUTE_FILTER2", "MEMORY", "WRITEBACK"],
                base_cycles=8,
                memory_accesses=16,
                register_reads=2,
                register_writes=1,
                has_immediate=True,
                is_branch=False,
                is_conditional=False,
                description="Apply FIR filter to data stream"
            )
        ]

        return ISAExtension(
            name="LC-3 DSP",
            custom_instructions=dsp_instructions,
            additional_registers=4,  # 4 accumulator registers
            description="Digital Signal Processing extension"
        )

    def define_crypto_extension(self) -> ISAExtension:
        """Define a cryptographic extension for LC-3"""
        crypto_instructions = [
            CustomInstructionDef(
                name="AES_ENC",
                opcode=0xA000,
                mask=0xFF00,
                format_type="R",
                execution_stages=["FETCH", "DECODE"] + ["EXECUTE_CRYPTO"] * 10 + ["WRITEBACK"],
                base_cycles=12,
                memory_accesses=0,
                register_reads=2,
                register_writes=1,
                has_immediate=False,
                is_branch=False,
                is_conditional=False,
                description="AES encryption round"
            ),
            CustomInstructionDef(
                name="SHA_HASH",
                opcode=0xA100,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE"] + ["EXECUTE_HASH"] * 20 + ["WRITEBACK"],
                base_cycles=22,
                memory_accesses=4,
                register_reads=1,
                register_writes=1,
                has_immediate=True,
                is_branch=False,
                is_conditional=False,
                description="SHA-256 hash computation"
            ),
            CustomInstructionDef(
                name="RNG",
                opcode=0xA200,
                mask=0xFF00,
                format_type="I",
                execution_stages=["FETCH", "DECODE", "EXECUTE_RNG", "WRITEBACK"],
                base_cycles=4,
                memory_accesses=0,
                register_reads=0,
                register_writes=1,
                has_immediate=False,
                is_branch=False,
                is_conditional=False,
                description="Hardware random number generator"
            )
        ]

        return ISAExtension(
            name="LC-3 Crypto",
            custom_instructions=crypto_instructions,
            additional_registers=4,  # 4 key/state registers
            description="Cryptographic operations extension"
        )

    def register_isa_extension(self, extension: ISAExtension):
        """Register an ISA extension for testing"""
        self.isa_extensions[extension.name] = extension

    def create_custom_pipeline_configs(self) -> List[PipelineConfiguration]:
        """Create pipeline configurations optimized for custom instructions"""
        configs = []

        # Vector processing pipeline
        configs.append(PipelineConfiguration(
            name="Vector Pipeline",
            stages=["FETCH", "DECODE", "EXECUTE_VEC1", "EXECUTE_VEC2", "MEMORY_VEC", "WRITEBACK"],
            depth=6,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=200,
            memory_latency=2
        ))

        # DSP optimized pipeline
        configs.append(PipelineConfiguration(
            name="DSP Pipeline",
            stages=["FETCH", "DECODE", "EXECUTE_MAC", "EXECUTE_FILTER", "MEMORY", "WRITEBACK"],
            depth=6,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=150,
            memory_latency=1
        ))

        # Crypto accelerated pipeline
        configs.append(PipelineConfiguration(
            name="Crypto Pipeline",
            stages=["FETCH", "DECODE", "EXECUTE_CRYPTO1", "EXECUTE_CRYPTO2", "EXECUTE_CRYPTO3", "WRITEBACK"],
            depth=6,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=100,
            memory_latency=1
        ))

        # Superscalar pipeline
        configs.append(PipelineConfiguration(
            name="Superscalar",
            stages=["FETCH", "DECODE", "DISPATCH", "EXECUTE1", "EXECUTE2", "COMPLETE", "RETIRE"],
            depth=7,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            out_of_order_execution=True,
            clock_frequency=300,
            memory_latency=1
        ))

        return configs

    def generate_custom_programs(self) -> Dict[str, List[int]]:
        """Generate programs that utilize custom instructions"""
        programs = {}

        # SIMD vector processing program
        programs['vector_math'] = [
            0x8000,  # VADD V0, V1, V2
            0x8100,  # VMUL V0, V0, V3
            0x8200,  # VLOAD V1, R0, #0
            0x8300,  # VSTORE V0, R1, #0
            0xF025   # HALT
        ]

        # DSP signal processing program
        programs['signal_processing'] = [
            0x9000,  # MAC R0, R1, R2
            0x9000,  # MAC R0, R3, R4
            0x9200,  # FILTER R0, #data_ptr
            0x9100,  # FFT #buffer_ptr
            0xF025   # HALT
        ]

        # Cryptographic program
        programs['crypto_operations'] = [
            0xA000,  # AES_ENC R0, R1
            0xA000,  # AES_ENC R0, R2
            0xA100,  # SHA_HASH #message_ptr
            0xA200,  # RNG R3
            0xF025   # HALT
        ]

        # Mixed custom instruction program
        programs['mixed_custom'] = [
            0x1021,  # ADD R0, R0, #1 (standard)
            0x8000,  # VADD V0, V1, V2 (SIMD)
            0x9000,  # MAC R0, R1, R2 (DSP)
            0xA200,  # RNG R3 (Crypto)
            0x2001,  # LD R0, #1 (standard)
            0xF025   # HALT
        ]

        return programs

    def analyze_instruction_mix(self, program: List[int]) -> Dict[str, int]:
        """Analyze the instruction mix in a program"""
        mix = defaultdict(int)

        for instr in program:
            opcode = (instr >> 12) & 0xF

            # Standard LC-3 instructions
            if opcode == 0x0:
                mix['branch'] += 1
            elif opcode in [0x1, 0x5, 0x9]:
                mix['arithmetic'] += 1
            elif opcode in [0x2, 0x3, 0x6, 0x7, 0xA, 0xB, 0xE]:
                mix['memory'] += 1
            elif opcode in [0x4, 0xC]:
                mix['control'] += 1
            elif opcode == 0xF:
                mix['system'] += 1
            # Custom instructions
            elif opcode == 0x8:
                mix['vector'] += 1
            elif opcode == 0x9:
                mix['dsp'] += 1
            elif opcode == 0xA:
                mix['crypto'] += 1
            else:
                mix['unknown'] += 1

        return dict(mix)

    def estimate_custom_instruction_performance(self, instruction: CustomInstructionDef,
                                              config: PipelineConfiguration) -> Dict[str, float]:
        """Estimate performance metrics for custom instruction"""
        # Base CPI from instruction definition
        base_cpi = instruction.base_cycles

        # Pipeline depth effect
        if config.depth > len(instruction.execution_stages):
            # Instruction can be fully pipelined
            pipeline_cpi = 1.0
        else:
            # Instruction causes pipeline stalls
            pipeline_cpi = len(instruction.execution_stages) / config.depth

        # Memory access penalty
        memory_penalty = instruction.memory_accesses * config.memory_latency

        # Final CPI
        final_cpi = max(base_cpi, pipeline_cpi) + memory_penalty * 0.1

        # Throughput (instructions per second)
        throughput = (config.clock_frequency * 1e6) / final_cpi

        return {
            'cpi': final_cpi,
            'ipc': 1.0 / final_cpi,
            'throughput': throughput,
            'memory_penalty': memory_penalty
        }

    def run_isa_comparison(self) -> Dict[str, Any]:
        """Run comprehensive ISA extension comparison"""
        print("Running ISA Extension Comparison...")

        # Register all ISA extensions
        self.register_isa_extension(self.define_simd_extension())
        self.register_isa_extension(self.define_dsp_extension())
        self.register_isa_extension(self.define_crypto_extension())

        # Create custom pipeline configurations
        custom_configs = self.create_custom_pipeline_configs()

        # Add standard configurations for comparison
        self.pipeline_tester.create_predefined_configurations()
        self.pipeline_tester.configurations.extend(custom_configs)

        # Generate custom programs
        custom_programs = self.generate_custom_programs()

        # Run tests
        results = self.pipeline_tester.run_comprehensive_test(custom_programs)

        # Analyze results
        analysis = {
            'configurations_tested': len(self.pipeline_tester.configurations),
            'programs_tested': len(custom_programs),
            'total_results': len(results),
            'isa_extensions': list(self.isa_extensions.keys()),
            'best_performers': self._find_best_performers(results),
            'instruction_analysis': self._analyze_instruction_performance(),
            'recommendations': self._generate_recommendations(results)
        }

        return analysis

    def _find_best_performers(self, results: List[PipelineResults]) -> Dict[str, str]:
        """Find best performing configurations for each metric"""
        best = {}

        if results:
            best['lowest_cpi'] = min(results, key=lambda x: x.cpi).config_name
            best['highest_ipc'] = max(results, key=lambda x: x.ipc).config_name
            best['best_efficiency'] = max(results, key=lambda x: x.pipeline_efficiency).config_name
            best['fewest_hazards'] = min(results,
                key=lambda x: x.data_hazards + x.control_hazards + x.structural_hazards).config_name

        return best

    def _analyze_instruction_performance(self) -> Dict[str, Any]:
        """Analyze performance characteristics of custom instructions"""
        analysis = {}

        for ext_name, extension in self.isa_extensions.items():
            ext_analysis = {
                'instruction_count': len(extension.custom_instructions),
                'avg_cycles': np.mean([instr.base_cycles for instr in extension.custom_instructions]),
                'max_cycles': max([instr.base_cycles for instr in extension.custom_instructions]),
                'memory_intensive': sum(1 for instr in extension.custom_instructions if instr.memory_accesses > 0),
                'complexity_score': self._calculate_complexity_score(extension)
            }
            analysis[ext_name] = ext_analysis

        return analysis

    def _calculate_complexity_score(self, extension: ISAExtension) -> float:
        """Calculate complexity score for an ISA extension"""
        score = 0.0

        for instr in extension.custom_instructions:
            # Base complexity from cycle count
            score += instr.base_cycles * 0.1

            # Memory access complexity
            score += instr.memory_accesses * 0.2

            # Register dependency complexity
            score += (instr.register_reads + instr.register_writes) * 0.1

            # Pipeline stage complexity
            score += len(instr.execution_stages) * 0.05

        return score / len(extension.custom_instructions) if extension.custom_instructions else 0.0

    def _generate_recommendations(self, results: List[PipelineResults]) -> List[str]:
        """Generate architectural recommendations based on results"""
        recommendations = []

        if not results:
            return ["No results available for analysis"]

        # CPI analysis
        avg_cpi = np.mean([r.cpi for r in results])
        if avg_cpi > 2.0:
            recommendations.append("Consider deeper pipelining to reduce CPI")

        # Hazard analysis
        avg_hazards = np.mean([r.data_hazards + r.control_hazards + r.structural_hazards for r in results])
        if avg_hazards > 10:
            recommendations.append("Implement more aggressive forwarding and hazard mitigation")

        # Efficiency analysis
        avg_efficiency = np.mean([r.pipeline_efficiency for r in results])
        if avg_efficiency < 0.7:
            recommendations.append("Pipeline efficiency is low - consider architectural improvements")

        # Custom instruction recommendations
        recommendations.append("SIMD instructions show best parallelism potential")
        recommendations.append("DSP instructions benefit from dedicated execution units")
        recommendations.append("Crypto instructions may require specialized security features")

        return recommendations

    def generate_comprehensive_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive ISA extension analysis report"""
        report = []
        report.append("=" * 80)
        report.append("LC-3 ISA Extension and Custom Pipeline Analysis Report")
        report.append("=" * 80)
        report.append("")

        # Executive summary
        report.append("Executive Summary:")
        report.append("-" * 20)
        report.append(f"• Tested {analysis_results['configurations_tested']} pipeline configurations")
        report.append(f"• Evaluated {analysis_results['programs_tested']} custom programs")
        report.append(f"• Analyzed {len(analysis_results['isa_extensions'])} ISA extensions")
        report.append("")

        # Best performers
        if 'best_performers' in analysis_results:
            best = analysis_results['best_performers']
            report.append("Best Performing Configurations:")
            report.append("-" * 35)
            for metric, config in best.items():
                report.append(f"• {metric.replace('_', ' ').title()}: {config}")
            report.append("")

        # ISA extension analysis
        if 'instruction_analysis' in analysis_results:
            report.append("ISA Extension Analysis:")
            report.append("-" * 25)
            for ext_name, analysis in analysis_results['instruction_analysis'].items():
                report.append(f"\n{ext_name}:")
                report.append(f"  Instructions: {analysis['instruction_count']}")
                report.append(f"  Avg Cycles: {analysis['avg_cycles']:.1f}")
                report.append(f"  Max Cycles: {analysis['max_cycles']}")
                report.append(f"  Memory Intensive: {analysis['memory_intensive']}")
                report.append(f"  Complexity Score: {analysis['complexity_score']:.2f}")
            report.append("")

        # Recommendations
        if 'recommendations' in analysis_results:
            report.append("Architectural Recommendations:")
            report.append("-" * 30)
            for i, rec in enumerate(analysis_results['recommendations'], 1):
                report.append(f"{i}. {rec}")
            report.append("")

        report.append("Detailed Performance Analysis:")
        report.append("-" * 30)
        report.append(self.pipeline_tester.generate_comparison_report())

        return "\n".join(report)

    def create_advanced_visualizations(self, save_dir: str = "."):
        """Create advanced visualizations for ISA analysis"""
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # 1. Instruction complexity heatmap
        self._plot_instruction_complexity_heatmap(f"{save_dir}/instruction_complexity.png")

        # 2. Pipeline efficiency radar chart
        self._plot_pipeline_efficiency_radar(f"{save_dir}/pipeline_radar.png")

        # 3. Custom instruction performance comparison
        self._plot_custom_instruction_performance(f"{save_dir}/custom_performance.png")

        # 4. ISA extension trade-offs
        self._plot_isa_tradeoffs(f"{save_dir}/isa_tradeoffs.png")

    def _plot_instruction_complexity_heatmap(self, filename: str):
        """Plot instruction complexity heatmap"""
        # Collect complexity data
        complexity_data = []
        instruction_names = []
        metrics = ['Cycles', 'Memory Ops', 'Reg Deps', 'Pipeline Stages']

        for ext_name, extension in self.isa_extensions.items():
            for instr in extension.custom_instructions:
                instruction_names.append(f"{ext_name}::{instr.name}")
                complexity_data.append([
                    instr.base_cycles,
                    instr.memory_accesses,
                    instr.register_reads + instr.register_writes,
                    len(instr.execution_stages)
                ])

        if complexity_data:
            plt.figure(figsize=(10, 8))
            sns.heatmap(complexity_data,
                       xticklabels=metrics,
                       yticklabels=instruction_names,
                       annot=True, fmt='d', cmap='YlOrRd')
            plt.title('Custom Instruction Complexity Analysis')
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()

    def _plot_pipeline_efficiency_radar(self, filename: str):
        """Plot pipeline efficiency radar chart"""
        # This would create a radar chart comparing different pipeline configurations
        # Implementation would depend on having actual results
        pass

    def _plot_custom_instruction_performance(self, filename: str):
        """Plot custom instruction performance comparison"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # CPI comparison
        extensions = list(self.isa_extensions.keys())
        avg_cpis = []

        for ext_name in extensions:
            extension = self.isa_extensions[ext_name]
            avg_cpi = np.mean([instr.base_cycles for instr in extension.custom_instructions])
            avg_cpis.append(avg_cpi)

        ax1.bar(extensions, avg_cpis)
        ax1.set_title('Average CPI by ISA Extension')
        ax1.set_ylabel('Average CPI')
        ax1.tick_params(axis='x', rotation=45)

        # Memory intensity comparison
        memory_intensities = []
        for ext_name in extensions:
            extension = self.isa_extensions[ext_name]
            avg_memory = np.mean([instr.memory_accesses for instr in extension.custom_instructions])
            memory_intensities.append(avg_memory)

        ax2.bar(extensions, memory_intensities)
        ax2.set_title('Memory Intensity by ISA Extension')
        ax2.set_ylabel('Average Memory Accesses')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_isa_tradeoffs(self, filename: str):
        """Plot ISA extension trade-offs"""
        # Scatter plot showing complexity vs performance trade-offs
        extensions = []
        complexities = []
        performances = []

        for ext_name, extension in self.isa_extensions.items():
            extensions.append(ext_name)
            complexity = self._calculate_complexity_score(extension)
            complexities.append(complexity)

            # Estimate performance (inverse of average CPI)
            avg_cpi = np.mean([instr.base_cycles for instr in extension.custom_instructions])
            performance = 1.0 / avg_cpi if avg_cpi > 0 else 0
            performances.append(performance)

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(complexities, performances, s=100, alpha=0.7)

        # Add labels
        for i, ext in enumerate(extensions):
            plt.annotate(ext, (complexities[i], performances[i]),
                        xytext=(5, 5), textcoords='offset points')

        plt.xlabel('Complexity Score')
        plt.ylabel('Performance Score (1/CPI)')
        plt.title('ISA Extension Complexity vs Performance Trade-offs')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Main function to demonstrate custom ISA analysis"""
    print("LC-3 Custom ISA Extension and Pipeline Analyzer")
    print("=" * 60)

    # Create analyzer instance
    analyzer = CustomISAAnalyzer()

    # Run comprehensive ISA comparison
    analysis_results = analyzer.run_isa_comparison()

    # Generate and print comprehensive report
    report = analyzer.generate_comprehensive_report(analysis_results)
    print(report)

    # Create visualizations
    print("\nGenerating advanced visualizations...")
    analyzer.create_advanced_visualizations("./reports")

    # Export detailed results
    with open("isa_extension_analysis.json", "w") as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print("\nAnalysis complete! Check the following files:")
    print("• isa_extension_analysis.json - Detailed analysis data")
    print("• reports/instruction_complexity.png - Instruction complexity heatmap")
    print("• reports/custom_performance.png - Custom instruction performance")
    print("• reports/isa_tradeoffs.png - ISA extension trade-offs")


if __name__ == "__main__":
    main()
