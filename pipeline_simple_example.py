#!/usr/bin/env python3
"""
Simple LC-3 Pipeline Testing Example

This script demonstrates how to use the extended LC-3 simulator
for basic pipeline performance testing.
"""

import sys
from pathlib import Path

# Add pipeline module to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pipeline.pipeline_tester import PipelineTester, PipelineConfiguration
except ImportError:
    print("Pipeline modules not found. Make sure to build with -DBUILD_PIPELINE_EXTENSIONS=ON")
    sys.exit(1)


def simple_pipeline_test():
    """Simple example of pipeline testing"""
    print("Simple Pipeline Performance Test")
    print("=" * 40)

    # Create a pipeline tester
    tester = PipelineTester()

    # Define two pipeline configurations to compare
    configs = [
        PipelineConfiguration(
            name="Basic 5-Stage",
            stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=5,
            forwarding_enabled=False,
            branch_prediction_enabled=False,
            clock_frequency=100
        ),
        PipelineConfiguration(
            name="Optimized 5-Stage",
            stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
            depth=5,
            forwarding_enabled=True,
            branch_prediction_enabled=True,
            clock_frequency=200
        )
    ]

    # Add configurations to tester
    for config in configs:
        tester.add_configuration(config)

    # Create a simple test program
    test_program = [
        0x1021,  # ADD R0, R0, #1
        0x1422,  # ADD R2, R0, #2  (depends on R0)
        0x1843,  # ADD R4, R2, #3  (depends on R2)
        0x0203,  # BRp #3          (branch)
        0x1021,  # ADD R0, R0, #1
        0x1021,  # ADD R0, R0, #1
        0xF025   # HALT
    ]

    print(f"Testing {len(configs)} configurations with {len(test_program)} instructions")
    print()

    # Test each configuration
    results = []
    for config in configs:
        result = tester.run_benchmark_program(config, test_program)
        results.append(result)

        print(f"Configuration: {config.name}")
        print(f"  CPI: {result.cpi:.3f}")
        print(f"  IPC: {result.ipc:.3f}")
        print(f"  Pipeline Efficiency: {result.pipeline_efficiency:.1%}")
        print(f"  Data Hazards: {result.data_hazards}")
        print(f"  Control Hazards: {result.control_hazards}")
        print()

    # Compare results
    basic_result = results[0]
    optimized_result = results[1]

    cpi_improvement = (basic_result.cpi - optimized_result.cpi) / basic_result.cpi
    ipc_improvement = (optimized_result.ipc - basic_result.ipc) / basic_result.ipc

    print("Performance Comparison:")
    print(f"  CPI improvement: {cpi_improvement:.1%}")
    print(f"  IPC improvement: {ipc_improvement:.1%}")
    print(f"  Hazard reduction: {basic_result.data_hazards - optimized_result.data_hazards} fewer data hazards")

    if cpi_improvement > 0:
        print(f"  → Optimized pipeline is {1/(1-cpi_improvement):.1f}x faster!")
    else:
        print("  → Basic pipeline performed better (unexpected)")


def custom_instruction_example():
    """Example of defining a custom instruction"""
    print("\nCustom Instruction Example")
    print("=" * 30)

    # Define a custom matrix multiply instruction
    custom_instruction = {
        'name': 'MATMUL2x2',
        'opcode': 0xD000,
        'description': '2x2 matrix multiplication',
        'cycles': 8,
        'memory_accesses': 8,
        'pipeline_stages': ['FETCH', 'DECODE', 'MATMUL1', 'MATMUL2', 'MATMUL3', 'WRITEBACK']
    }

    print(f"Custom Instruction: {custom_instruction['name']}")
    print(f"Description: {custom_instruction['description']}")
    print(f"Base cycles: {custom_instruction['cycles']}")
    print(f"Memory accesses: {custom_instruction['memory_accesses']}")
    print(f"Pipeline stages: {len(custom_instruction['pipeline_stages'])}")

    # Calculate theoretical performance improvement
    # Compare with equivalent LC-3 code sequence
    equivalent_lc3_instructions = 16  # Rough estimate for 2x2 matrix multiply
    equivalent_cycles = equivalent_lc3_instructions * 1.5  # Assume 1.5 CPI

    custom_cycles = custom_instruction['cycles']
    speedup = equivalent_cycles / custom_cycles

    print(f"\nPerformance Analysis:")
    print(f"Equivalent LC-3 sequence: ~{equivalent_lc3_instructions} instructions")
    print(f"Equivalent cycles: ~{equivalent_cycles:.0f}")
    print(f"Custom instruction cycles: {custom_cycles}")
    print(f"Theoretical speedup: {speedup:.1f}x")

    # Calculate area/complexity trade-off
    complexity_score = (custom_instruction['cycles'] * 0.1 +
                       custom_instruction['memory_accesses'] * 0.2 +
                       len(custom_instruction['pipeline_stages']) * 0.1)

    print(f"Complexity score: {complexity_score:.2f}")
    print(f"Performance/complexity ratio: {speedup/complexity_score:.2f}")


def workload_optimization_example():
    """Example of workload-specific optimization"""
    print("\nWorkload Optimization Example")
    print("=" * 35)

    # Define different workload characteristics
    workloads = {
        'Gaming': {
            'arithmetic': 0.6,  # Lots of graphics calculations
            'memory': 0.3,      # Texture/vertex data
            'control': 0.1,     # Game logic
            'recommended_config': 'Deep pipeline with multiple ALUs'
        },
        'Database': {
            'arithmetic': 0.2,  # Simple comparisons
            'memory': 0.7,      # Data access heavy
            'control': 0.1,     # Query logic
            'recommended_config': 'Wide memory interface, prefetching'
        },
        'AI/ML': {
            'arithmetic': 0.8,  # Matrix operations
            'memory': 0.15,     # Model parameters
            'control': 0.05,    # Simple control flow
            'recommended_config': 'Vector/SIMD units, specialized multiply-accumulate'
        }
    }

    print("Workload-Specific Optimization:")
    print("-" * 35)

    for workload_name, characteristics in workloads.items():
        print(f"\n{workload_name}:")
        print(f"  Arithmetic: {characteristics['arithmetic']:.0%}")
        print(f"  Memory: {characteristics['memory']:.0%}")
        print(f"  Control: {characteristics['control']:.0%}")
        print(f"  Recommendation: {characteristics['recommended_config']}")

        # Estimate optimal pipeline configuration
        if characteristics['arithmetic'] > 0.5:
            optimal_config = "Compute-optimized (multiple ALUs, deep pipeline)"
        elif characteristics['memory'] > 0.5:
            optimal_config = "Memory-optimized (wide memory bus, cache-friendly)"
        else:
            optimal_config = "Balanced (standard 5-stage with forwarding)"

        print(f"  Optimal pipeline: {optimal_config}")


def main():
    """Main function"""
    print("LC-3 Extended Pipeline Testing - Simple Examples")
    print("=" * 55)
    print()

    try:
        # Run simple pipeline test
        simple_pipeline_test()

        # Show custom instruction example
        custom_instruction_example()

        # Show workload optimization
        workload_optimization_example()

        print("\n" + "=" * 55)
        print("Examples complete!")
        print()
        print("Next steps:")
        print("• Run 'python pipeline_demo.py' for comprehensive testing")
        print("• Modify configurations in this script")
        print("• Create your own benchmark programs")
        print("• Experiment with custom instruction definitions")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the pipeline modules are properly built and installed.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
