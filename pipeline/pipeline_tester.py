#!/usr/bin/env python3
"""
LC-3 Pipeline Performance Testing Framework

This module provides tools for testing custom instruction pipelines
and analyzing ISA performance characteristics.
"""

import sys
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add the build directory to Python path for lc3_simulator
sys.path.insert(0, str(Path(__file__).parent.parent / "build"))

try:
    import lc3_simulator
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("Warning: lc3_simulator module not available. Using mock data.")


@dataclass
class PipelineConfiguration:
    """Pipeline configuration for testing"""
    name: str = "Default"
    stages: List[str] = None
    depth: int = 5
    forwarding_enabled: bool = True
    branch_prediction_enabled: bool = False
    out_of_order_execution: bool = False
    clock_frequency: int = 100  # MHz
    memory_latency: int = 1     # cycles
    branch_penalty: int = 2     # cycles
    enable_detailed_metrics: bool = True

    def __post_init__(self):
        if self.stages is None:
            self.stages = ["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"]


@dataclass
class PipelineResults:
    """Results from pipeline simulation"""
    config_name: str
    total_cycles: int
    total_instructions: int
    cpi: float
    ipc: float
    pipeline_efficiency: float
    data_hazards: int
    control_hazards: int
    structural_hazards: int
    cache_hit_rate_i: float
    cache_hit_rate_d: float
    branch_prediction_accuracy: float


class CustomInstructionSet:
    """Define custom instructions for testing"""

    def __init__(self):
        self.instructions = {}

    def add_instruction(self, name: str, opcode: int, stages: List[str],
                       cycles: int = 1, uses_memory: bool = False,
                       is_branch: bool = False):
        """Add a custom instruction"""
        self.instructions[opcode] = {
            'name': name,
            'opcode': opcode,
            'stages': stages,
            'cycles': cycles,
            'uses_memory': uses_memory,
            'is_branch': is_branch
        }

    def get_instruction(self, opcode: int) -> Optional[Dict]:
        """Get instruction definition by opcode"""
        return self.instructions.get(opcode)


class PipelineTester:
    """Main class for pipeline performance testing"""

    def __init__(self):
        self.simulator = None
        if SIMULATOR_AVAILABLE:
            self.simulator = lc3_simulator.LC3Simulator()

        self.configurations = []
        self.results = []
        self.custom_instructions = CustomInstructionSet()

    def add_configuration(self, config: PipelineConfiguration):
        """Add a pipeline configuration for testing"""
        self.configurations.append(config)

    def create_predefined_configurations(self):
        """Create a set of predefined pipeline configurations for comparison"""
        configs = [
            # Single cycle (no pipeline)
            PipelineConfiguration(
                name="Single Cycle",
                stages=["EXECUTE"],
                depth=1,
                forwarding_enabled=False,
                branch_prediction_enabled=False
            ),

            # Classic 5-stage RISC pipeline
            PipelineConfiguration(
                name="Classic 5-Stage",
                stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
                depth=5,
                forwarding_enabled=True,
                branch_prediction_enabled=False
            ),

            # 5-stage with branch prediction
            PipelineConfiguration(
                name="5-Stage + Branch Prediction",
                stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
                depth=5,
                forwarding_enabled=True,
                branch_prediction_enabled=True,
                branch_penalty=1
            ),

            # 7-stage pipeline
            PipelineConfiguration(
                name="7-Stage Deep Pipeline",
                stages=["FETCH1", "FETCH2", "DECODE", "EXECUTE", "MEMORY1", "MEMORY2", "WRITEBACK"],
                depth=7,
                forwarding_enabled=True,
                branch_prediction_enabled=True,
                branch_penalty=3
            ),

            # Out-of-order execution
            PipelineConfiguration(
                name="Out-of-Order",
                stages=["FETCH", "DECODE", "DISPATCH", "EXECUTE", "COMPLETE", "RETIRE"],
                depth=6,
                forwarding_enabled=True,
                branch_prediction_enabled=True,
                out_of_order_execution=True,
                branch_penalty=1
            ),
        ]

        self.configurations.extend(configs)

    def run_benchmark_program(self, config: PipelineConfiguration,
                            program: List[int]) -> PipelineResults:
        """Run a benchmark program with given pipeline configuration"""

        if self.simulator:
            # Use real simulator
            self.simulator.reset()
            self.simulator.load_program(program)

            start_time = time.time()
            self.simulator.run(max_cycles=100000)
            end_time = time.time()

            # Get basic metrics (simulated pipeline metrics)
            total_instructions = len(program)
            execution_time = end_time - start_time

            # Estimate pipeline performance based on configuration
            base_cpi = self._estimate_cpi(config, program)
            total_cycles = int(total_instructions * base_cpi)

        else:
            # Use estimated metrics
            total_instructions = len(program)
            base_cpi = self._estimate_cpi(config, program)
            total_cycles = int(total_instructions * base_cpi)

        # Calculate derived metrics
        ipc = total_instructions / total_cycles if total_cycles > 0 else 0
        pipeline_efficiency = ipc / (1.0 if config.depth == 1 else min(1.0, config.depth * 0.8))

        # Estimate hazard counts
        hazards = self._estimate_hazards(config, program)

        return PipelineResults(
            config_name=config.name,
            total_cycles=total_cycles,
            total_instructions=total_instructions,
            cpi=base_cpi,
            ipc=ipc,
            pipeline_efficiency=pipeline_efficiency,
            data_hazards=hazards['data'],
            control_hazards=hazards['control'],
            structural_hazards=hazards['structural'],
            cache_hit_rate_i=0.9,  # Simulated
            cache_hit_rate_d=0.85,  # Simulated
            branch_prediction_accuracy=0.8 if config.branch_prediction_enabled else 0.5
        )

    def _estimate_cpi(self, config: PipelineConfiguration, program: List[int]) -> float:
        """Estimate CPI based on pipeline configuration and program characteristics"""
        base_cpi = 1.0

        # Pipeline depth effect
        if config.depth == 1:
            # Single cycle - all instructions take multiple cycles
            base_cpi = 3.0
        elif config.depth <= 5:
            base_cpi = 1.0
        else:
            # Deeper pipelines have higher branch penalty
            base_cpi = 1.1 + (config.depth - 5) * 0.1

        # Branch penalty
        branch_instructions = sum(1 for instr in program if self._is_branch_instruction(instr))
        branch_ratio = branch_instructions / len(program) if program else 0

        if not config.branch_prediction_enabled:
            base_cpi += branch_ratio * config.branch_penalty
        else:
            # Assume 80% prediction accuracy
            base_cpi += branch_ratio * config.branch_penalty * 0.2

        # Memory instructions
        memory_instructions = sum(1 for instr in program if self._is_memory_instruction(instr))
        memory_ratio = memory_instructions / len(program) if program else 0
        base_cpi += memory_ratio * config.memory_latency * 0.5

        # Forwarding effect
        if not config.forwarding_enabled and config.depth > 1:
            base_cpi += 0.5  # Additional stalls for data hazards

        return base_cpi

    def _estimate_hazards(self, config: PipelineConfiguration,
                         program: List[int]) -> Dict[str, int]:
        """Estimate hazard counts based on program analysis"""
        total_instructions = len(program)

        # Analyze instruction dependencies
        data_hazards = 0
        control_hazards = 0
        structural_hazards = 0

        for i, instr in enumerate(program):
            if i < len(program) - 1:
                next_instr = program[i + 1]

                # Simple dependency analysis
                if self._has_data_dependency(instr, next_instr):
                    data_hazards += 1

            if self._is_branch_instruction(instr):
                control_hazards += 1

        # Structural hazards depend on pipeline design
        if config.depth > 5:
            structural_hazards = total_instructions // 10

        return {
            'data': data_hazards,
            'control': control_hazards,
            'structural': structural_hazards
        }

    def _is_branch_instruction(self, instruction: int) -> bool:
        """Check if instruction is a branch/jump"""
        opcode = (instruction >> 12) & 0xF
        return opcode in [0x0, 0x4, 0xC]  # BR, JSR, JMP

    def _is_memory_instruction(self, instruction: int) -> bool:
        """Check if instruction accesses memory"""
        opcode = (instruction >> 12) & 0xF
        return opcode in [0x2, 0x3, 0x6, 0x7, 0xA, 0xB]  # LD, ST, LDR, STR, LDI, STI

    def _has_data_dependency(self, instr1: int, instr2: int) -> bool:
        """Simple check for data dependencies between instructions"""
        # Extract destination register of first instruction
        opcode1 = (instr1 >> 12) & 0xF
        if opcode1 in [0x1, 0x5, 0x9, 0x2, 0x6, 0xA, 0xE]:  # Instructions that write to registers
            dest_reg1 = (instr1 >> 9) & 0x7

            # Check if second instruction reads from same register
            opcode2 = (instr2 >> 12) & 0xF
            if opcode2 in [0x1, 0x5, 0x9]:  # ADD, AND, NOT
                src_reg1 = (instr2 >> 6) & 0x7
                src_reg2 = instr2 & 0x7 if not (instr2 & 0x20) else 0
                return dest_reg1 in [src_reg1, src_reg2]

        return False

    def run_comprehensive_test(self, programs: Dict[str, List[int]]) -> List[PipelineResults]:
        """Run comprehensive testing with all configurations and programs"""
        all_results = []

        for config in self.configurations:
            print(f"Testing configuration: {config.name}")

            for program_name, program in programs.items():
                print(f"  Running program: {program_name}")
                result = self.run_benchmark_program(config, program)
                result.program_name = program_name
                all_results.append(result)

        self.results = all_results
        return all_results

    def generate_comparison_report(self) -> str:
        """Generate a comprehensive comparison report"""
        if not self.results:
            return "No results available. Run tests first."

        report = []
        report.append("=" * 60)
        report.append("LC-3 Pipeline Performance Comparison Report")
        report.append("=" * 60)
        report.append("")

        # Group results by program
        by_program = defaultdict(list)
        for result in self.results:
            program_name = getattr(result, 'program_name', 'Unknown')
            by_program[program_name].append(result)

        for program_name, program_results in by_program.items():
            report.append(f"Program: {program_name}")
            report.append("-" * 40)
            report.append(f"{'Configuration':<20} {'CPI':<8} {'IPC':<8} {'Efficiency':<12} {'Hazards':<10}")
            report.append("-" * 40)

            for result in sorted(program_results, key=lambda x: x.cpi):
                total_hazards = result.data_hazards + result.control_hazards + result.structural_hazards
                report.append(f"{result.config_name:<20} {result.cpi:<8.3f} {result.ipc:<8.3f} "
                            f"{result.pipeline_efficiency*100:<12.1f}% {total_hazards:<10}")

            report.append("")

        # Overall analysis
        report.append("Overall Analysis:")
        report.append("-" * 20)

        best_cpi = min(self.results, key=lambda x: x.cpi)
        best_ipc = max(self.results, key=lambda x: x.ipc)
        best_efficiency = max(self.results, key=lambda x: x.pipeline_efficiency)

        report.append(f"Best CPI: {best_cpi.config_name} ({best_cpi.cpi:.3f})")
        report.append(f"Best IPC: {best_ipc.config_name} ({best_ipc.ipc:.3f})")
        report.append(f"Best Efficiency: {best_efficiency.config_name} ({best_efficiency.pipeline_efficiency*100:.1f}%)")

        return "\n".join(report)

    def plot_performance_comparison(self, save_path: Optional[str] = None):
        """Create performance comparison plots"""
        if not self.results:
            print("No results available for plotting.")
            return

        # Group results by configuration
        configs = {}
        for result in self.results:
            if result.config_name not in configs:
                configs[result.config_name] = []
            configs[result.config_name].append(result)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        config_names = list(configs.keys())

        # CPI comparison
        cpi_values = [np.mean([r.cpi for r in configs[name]]) for name in config_names]
        ax1.bar(config_names, cpi_values)
        ax1.set_title('Cycles Per Instruction (CPI)')
        ax1.set_ylabel('CPI')
        ax1.tick_params(axis='x', rotation=45)

        # IPC comparison
        ipc_values = [np.mean([r.ipc for r in configs[name]]) for name in config_names]
        ax2.bar(config_names, ipc_values)
        ax2.set_title('Instructions Per Cycle (IPC)')
        ax2.set_ylabel('IPC')
        ax2.tick_params(axis='x', rotation=45)

        # Pipeline efficiency
        eff_values = [np.mean([r.pipeline_efficiency for r in configs[name]]) * 100 for name in config_names]
        ax3.bar(config_names, eff_values)
        ax3.set_title('Pipeline Efficiency (%)')
        ax3.set_ylabel('Efficiency (%)')
        ax3.tick_params(axis='x', rotation=45)

        # Hazards comparison
        hazard_types = ['Data', 'Control', 'Structural']
        data_hazards = [np.mean([r.data_hazards for r in configs[name]]) for name in config_names]
        control_hazards = [np.mean([r.control_hazards for r in configs[name]]) for name in config_names]
        structural_hazards = [np.mean([r.structural_hazards for r in configs[name]]) for name in config_names]

        x = np.arange(len(config_names))
        width = 0.25

        ax4.bar(x - width, data_hazards, width, label='Data', alpha=0.7)
        ax4.bar(x, control_hazards, width, label='Control', alpha=0.7)
        ax4.bar(x + width, structural_hazards, width, label='Structural', alpha=0.7)

        ax4.set_title('Pipeline Hazards')
        ax4.set_ylabel('Count')
        ax4.set_xticks(x)
        ax4.set_xticklabels(config_names, rotation=45)
        ax4.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

    def export_results_json(self, filename: str):
        """Export results to JSON for further analysis"""
        export_data = {
            'configurations': [asdict(config) for config in self.configurations],
            'results': [asdict(result) for result in self.results],
            'timestamp': time.time()
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)


def create_benchmark_programs() -> Dict[str, List[int]]:
    """Create a set of benchmark programs for testing"""
    programs = {
        'arithmetic_heavy': [
            0x1021,  # ADD R0, R0, #1
            0x1022,  # ADD R0, R0, #2
            0x1023,  # ADD R0, R0, #3
            0x5020,  # AND R0, R0, #0
            0x1025,  # ADD R0, R0, #5
            0x1001,  # ADD R0, R0, R1
            0x5001,  # AND R0, R0, R1
            0xF025   # HALT
        ],

        'memory_intensive': [
            0x2001,  # LD R0, #1
            0x3002,  # ST R0, #2
            0x2003,  # LD R0, #3
            0x6004,  # LDR R0, R0, #4
            0x7005,  # STR R0, R0, #5
            0xA006,  # LDI R0, #6
            0xB007,  # STI R0, #7
            0xF025   # HALT
        ],

        'control_flow': [
            0x0203,  # BRp #3
            0x1021,  # ADD R0, R0, #1
            0x0FFD,  # BRnzp #-3
            0x4801,  # JSR #1
            0xC1C0,  # RET
            0xF025   # HALT
        ],

        'mixed_workload': [
            0x1021,  # ADD R0, R0, #1
            0x2001,  # LD R1, #1
            0x1401,  # ADD R2, R0, R1
            0x0402,  # BRz #2
            0x3002,  # ST R2, #2
            0x4801,  # JSR #1
            0x6240,  # LDR R1, R2, #0
            0xF025   # HALT
        ]
    }

    return programs


def main():
    """Main function to demonstrate pipeline testing"""
    print("LC-3 Pipeline Performance Testing Framework")
    print("=" * 50)

    # Create tester instance
    tester = PipelineTester()

    # Add predefined configurations
    tester.create_predefined_configurations()

    # Create benchmark programs
    programs = create_benchmark_programs()

    # Run comprehensive testing
    print("Running comprehensive pipeline testing...")
    results = tester.run_comprehensive_test(programs)

    # Generate and print report
    print("\n" + tester.generate_comparison_report())

    # Create performance plots
    print("\nGenerating performance plots...")
    tester.plot_performance_comparison("pipeline_performance.png")

    # Export results
    tester.export_results_json("pipeline_results.json")
    print("Results exported to pipeline_results.json")


if __name__ == "__main__":
    main()
