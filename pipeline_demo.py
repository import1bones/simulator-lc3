#!/usr/bin/env python3
"""
LC-3 Pipeline Performance Demo

This script demonstrates the extended LC-3 simulator capabilities
for custom instruction pipeline testing and ISA performance analysis.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pipeline.pipeline_tester import PipelineTester, PipelineConfiguration, create_benchmark_programs
    from pipeline.isa_extension_analyzer import CustomISAAnalyzer
except ImportError as e:
    print(f"Error importing pipeline modules: {e}")
    print("Make sure the pipeline modules are in the correct location.")
    sys.exit(1)


def demo_basic_pipeline_testing():
    """Demonstrate basic pipeline configuration testing"""
    print("=" * 60)
    print("Basic Pipeline Configuration Testing Demo")
    print("=" * 60)

    # Create tester
    tester = PipelineTester()

    # Add some custom configurations
    custom_configs = [
        PipelineConfiguration(
            name="Aggressive Pipeline",
            stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=5,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=200,
            branch_penalty=1
        ),
        PipelineConfiguration(
            name="Conservative Pipeline",
            stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=5,
            forwarding_enabled=False,
            branch_prediction_enabled=False,
            clock_frequency=100,
            branch_penalty=3
        ),
        PipelineConfiguration(
            name="Deep Pipeline",
            stages=["FETCH1", "FETCH2", "DECODE1", "DECODE2", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=7,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=250,
            branch_penalty=4
        )
    ]

    for config in custom_configs:
        tester.add_configuration(config)

    # Create test programs
    programs = create_benchmark_programs()

    print(f"Testing {len(custom_configs)} pipeline configurations")
    print(f"With {len(programs)} benchmark programs")
    print()

    # Run tests
    results = tester.run_comprehensive_test(programs)

    # Generate report
    report = tester.generate_comparison_report()
    print(report)

    # Create visualizations
    print("Generating performance comparison chart...")
    tester.plot_performance_comparison("basic_pipeline_demo.png")
    print("Chart saved as 'basic_pipeline_demo.png'")

    return results


def demo_custom_isa_extensions():
    """Demonstrate custom ISA extension analysis"""
    print("\n" + "=" * 60)
    print("Custom ISA Extension Analysis Demo")
    print("=" * 60)

    # Create analyzer
    analyzer = CustomISAAnalyzer()

    # Run ISA comparison
    analysis_results = analyzer.run_isa_comparison()

    # Generate report
    report = analyzer.generate_comprehensive_report(analysis_results)
    print(report)

    # Create visualizations
    print("Generating ISA extension visualizations...")
    os.makedirs("demo_reports", exist_ok=True)
    analyzer.create_advanced_visualizations("demo_reports")
    print("Visualizations saved in 'demo_reports/' directory")

    return analysis_results


def demo_custom_instruction_design():
    """Demonstrate custom instruction design and testing"""
    print("\n" + "=" * 60)
    print("Custom Instruction Design Demo")
    print("=" * 60)

    # Define a custom matrix multiplication instruction
    print("Designing custom MATMUL instruction...")

    custom_instruction_spec = {
        'name': 'MATMUL',
        'opcode': 0xC000,
        'description': '4x4 Matrix multiplication in hardware',
        'execution_stages': ['FETCH', 'DECODE', 'MATMUL1', 'MATMUL2', 'MATMUL3', 'WRITEBACK'],
        'base_cycles': 16,
        'memory_accesses': 32,
        'register_usage': {'reads': 2, 'writes': 1},
        'pipeline_requirements': {
            'dedicated_multipliers': 4,
            'dedicated_memory_ports': 2,
            'register_file_ports': 3
        }
    }

    print(f"Instruction: {custom_instruction_spec['name']}")
    print(f"Description: {custom_instruction_spec['description']}")
    print(f"Execution cycles: {custom_instruction_spec['base_cycles']}")
    print(f"Memory accesses: {custom_instruction_spec['memory_accesses']}")
    print(f"Pipeline stages: {len(custom_instruction_spec['execution_stages'])}")

    # Estimate performance impact
    baseline_cpi = 1.5  # Typical LC-3 CPI
    matrix_heavy_program_ratio = 0.3  # 30% matrix operations

    # Without custom instruction (using standard LC-3)
    standard_cycles = 4 * 4 * 4 * 3  # 4x4 matrix, 4 ops per element, 3 cycles per op
    standard_cpi_weighted = baseline_cpi * (1 - matrix_heavy_program_ratio) + \
                           (standard_cycles / 1) * matrix_heavy_program_ratio

    # With custom instruction
    custom_cpi_weighted = baseline_cpi * (1 - matrix_heavy_program_ratio) + \
                         custom_instruction_spec['base_cycles'] * matrix_heavy_program_ratio

    speedup = standard_cpi_weighted / custom_cpi_weighted

    print(f"\nPerformance Analysis:")
    print(f"Standard LC-3 weighted CPI: {standard_cpi_weighted:.2f}")
    print(f"Custom instruction weighted CPI: {custom_cpi_weighted:.2f}")
    print(f"Estimated speedup: {speedup:.2f}x")

    # Pipeline impact analysis
    print(f"\nPipeline Impact:")
    print(f"Pipeline depth required: {len(custom_instruction_spec['execution_stages'])}")
    print(f"Memory bandwidth requirement: {custom_instruction_spec['memory_accesses']} accesses")
    print(f"Recommended clock frequency: {max(100, 200 - custom_instruction_spec['base_cycles'] * 5)} MHz")


def demo_workload_analysis():
    """Demonstrate workload-specific pipeline optimization"""
    print("\n" + "=" * 60)
    print("Workload-Specific Pipeline Optimization Demo")
    print("=" * 60)

    # Define different workload characteristics
    workloads = {
        'control_intensive': {
            'branch_ratio': 0.4,
            'memory_ratio': 0.2,
            'arithmetic_ratio': 0.4,
            'description': 'Control-flow heavy (OS kernel, decision trees)'
        },
        'memory_intensive': {
            'branch_ratio': 0.1,
            'memory_ratio': 0.7,
            'arithmetic_ratio': 0.2,
            'description': 'Memory-bound (databases, file systems)'
        },
        'compute_intensive': {
            'branch_ratio': 0.1,
            'memory_ratio': 0.2,
            'arithmetic_ratio': 0.7,
            'description': 'Compute-bound (scientific, graphics)'
        },
        'mixed_workload': {
            'branch_ratio': 0.25,
            'memory_ratio': 0.35,
            'arithmetic_ratio': 0.4,
            'description': 'Balanced general-purpose workload'
        }
    }

    # Define optimized pipeline configurations for each workload
    optimized_configs = {
        'control_intensive': PipelineConfiguration(
            name="Branch-Optimized",
            stages=["FETCH", "PREDICT", "DECODE", "EXECUTE", "WRITEBACK"],
            depth=5,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            branch_penalty=1,
            clock_frequency=200
        ),
        'memory_intensive': PipelineConfiguration(
            name="Memory-Optimized",
            stages=["FETCH", "DECODE", "EXECUTE", "MEM1", "MEM2", "WRITEBACK"],
            depth=6,
            forwarding_enabled=True,
            branch_prediction_enabled=False,
            memory_latency=2,
            clock_frequency=150
        ),
        'compute_intensive': PipelineConfiguration(
            name="Compute-Optimized",
            stages=["FETCH", "DECODE", "ALU1", "ALU2", "ALU3", "WRITEBACK"],
            depth=6,
            forwarding_enabled=True,
            branch_prediction_enabled=False,
            clock_frequency=300
        ),
        'mixed_workload': PipelineConfiguration(
            name="Balanced-Optimized",
            stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=5,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=200
        )
    }

    print("Workload Analysis:")
    print("-" * 40)

    for workload_name, characteristics in workloads.items():
        print(f"\n{workload_name.upper()}:")
        print(f"  Description: {characteristics['description']}")
        print(f"  Branch ratio: {characteristics['branch_ratio']:.1%}")
        print(f"  Memory ratio: {characteristics['memory_ratio']:.1%}")
        print(f"  Arithmetic ratio: {characteristics['arithmetic_ratio']:.1%}")

        # Get optimized configuration
        config = optimized_configs[workload_name]
        print(f"  Optimized configuration: {config.name}")
        print(f"  Pipeline depth: {config.depth}")
        print(f"  Clock frequency: {config.clock_frequency} MHz")
        print(f"  Branch prediction: {'Enabled' if config.branch_prediction_enabled else 'Disabled'}")

        # Estimate performance
        base_cpi = 1.0
        branch_penalty = config.branch_penalty if not config.branch_prediction_enabled else config.branch_penalty * 0.2
        memory_penalty = config.memory_latency * 0.5

        estimated_cpi = (base_cpi +
                        characteristics['branch_ratio'] * branch_penalty +
                        characteristics['memory_ratio'] * memory_penalty)

        estimated_ipc = 1.0 / estimated_cpi
        estimated_mips = (config.clock_frequency * estimated_ipc) / 1000  # MIPS

        print(f"  Estimated CPI: {estimated_cpi:.2f}")
        print(f"  Estimated IPC: {estimated_ipc:.2f}")
        print(f"  Estimated MIPS: {estimated_mips:.1f}")


def main():
    """Main demonstration function"""
    print("LC-3 Extended Pipeline Performance Analysis Framework")
    print("=" * 80)
    print()
    print("This demonstration shows the capabilities of the extended LC-3 simulator")
    print("for custom instruction pipeline testing and ISA performance analysis.")
    print()

    try:
        # Run all demonstrations
        demo_basic_pipeline_testing()
        demo_custom_isa_extensions()
        demo_custom_instruction_design()
        demo_workload_analysis()

        print("\n" + "=" * 80)
        print("Demonstration Complete!")
        print("=" * 80)
        print()
        print("Files generated:")
        print("• basic_pipeline_demo.png - Basic pipeline performance comparison")
        print("• demo_reports/ - Directory with ISA extension analysis charts")
        print("• isa_extension_analysis.json - Detailed analysis data")
        print()
        print("Next steps:")
        print("1. Modify pipeline configurations in pipeline_tester.py")
        print("2. Add custom instructions in isa_extension_analyzer.py")
        print("3. Create your own benchmark programs")
        print("4. Analyze results for your specific use case")

    except Exception as e:
        print(f"Error during demonstration: {e}")
        print("Make sure all required dependencies are installed:")
        print("• matplotlib")
        print("• numpy")
        print("• seaborn")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
