# LC-3 Pipeline Performance Testing Framework

## Overview

This extension to the LC-3 simulator provides comprehensive tools for custom instruction pipeline testing and ISA performance analysis. It enables researchers and engineers to:

- Design and test custom pipeline configurations
- Define and analyze custom instruction sets
- Compare ISA design trade-offs
- Optimize pipelines for specific workloads
- Generate detailed performance reports and visualizations

## Features

### 🔧 **Custom Pipeline Configuration**
- Configurable pipeline stages (fetch, decode, execute, memory, writeback, custom)
- Adjustable pipeline depth (1-8 stages)
- Forwarding and hazard detection controls
- Branch prediction simulation
- Out-of-order execution modeling
- Cache configuration and simulation

### 📊 **Performance Metrics**
- Cycles Per Instruction (CPI)
- Instructions Per Cycle (IPC)
- Pipeline efficiency analysis
- Hazard detection and counting (data, control, structural)
- Cache hit/miss statistics
- Branch prediction accuracy
- Memory bandwidth utilization

### 🧩 **Custom Instruction Support**
- Define custom instruction formats
- Specify execution requirements
- Model complex multi-cycle operations
- Support for specialized instruction classes:
  - SIMD/Vector operations
  - Digital Signal Processing (DSP)
  - Cryptographic instructions
  - Matrix operations

### 📈 **Analysis and Visualization**
- Comprehensive performance comparison reports
- Interactive performance charts
- Pipeline efficiency visualizations
- Instruction complexity heatmaps
- ISA trade-off analysis

## Directory Structure

```
pipeline/
├── pipeline_config.h          # Pipeline configuration structures
├── pipeline_simulator.h       # Pipeline simulator interface
├── pipeline_simulator.c       # Core pipeline simulation engine
├── pipeline_tester.py         # Python testing framework
├── isa_extension_analyzer.py  # ISA extension analysis tools
└── CMakeLists.txt             # Build configuration
```

## Quick Start

### 1. Build with Pipeline Extensions

```bash
# Configure with pipeline extensions enabled
cmake -S . -B build -DBUILD_PIPELINE_EXTENSIONS=ON -DBUILD_PYTHON_BINDINGS=ON

# Build the project
cmake --build build --config Debug
```

### 2. Run the Demo

```bash
# Install Python dependencies
pip install matplotlib numpy seaborn

# Run the comprehensive demonstration
python pipeline_demo.py
```

### 3. Basic Pipeline Testing

```python
from pipeline.pipeline_tester import PipelineTester, PipelineConfiguration

# Create tester
tester = PipelineTester()

# Define custom pipeline
config = PipelineConfiguration(
    name="My Custom Pipeline",
    stages=["FETCH", "DECODE", "EXECUTE", "MEMORY", "WRITEBACK"],
    depth=5,
    forwarding_enabled=True,
    branch_prediction_enabled=True,
    clock_frequency=200  # MHz
)

tester.add_configuration(config)

# Create test program
program = [
    0x1021,  # ADD R0, R0, #1
    0x1022,  # ADD R0, R0, #2
    0x2001,  # LD R1, #1
    0xF025   # HALT
]

# Run test
results = tester.run_benchmark_program(config, program)
print(f"CPI: {results.cpi:.3f}, IPC: {results.ipc:.3f}")
```

## Custom Instruction Definition

### SIMD Extension Example

```python
from pipeline.isa_extension_analyzer import CustomInstructionDef, ISAExtension

# Define vector add instruction
vadd = CustomInstructionDef(
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
)

# Create SIMD extension
simd_extension = ISAExtension(
    name="LC-3 SIMD",
    custom_instructions=[vadd],
    additional_registers=8,  # 8 vector registers
    vector_operations=True
)
```

## Performance Analysis

### Pipeline Configurations

The framework includes several predefined pipeline configurations:

1. **Single Cycle** - No pipelining (baseline)
2. **Classic 5-Stage** - Traditional RISC pipeline
3. **Branch Prediction** - 5-stage with branch prediction
4. **Deep Pipeline** - 7-stage for high frequency
5. **Out-of-Order** - Superscalar with OoO execution

### Benchmark Programs

Built-in benchmark programs test different aspects:

- **Arithmetic Heavy** - ALU operations and dependencies
- **Memory Intensive** - Load/store patterns
- **Control Flow** - Branches and jumps
- **Mixed Workload** - Realistic program mix

### Metrics Collected

- **Basic Performance**
  - Total cycles and instructions
  - CPI and IPC ratios
  - Pipeline efficiency percentage

- **Hazard Analysis**
  - Data hazards (RAW, WAW, WAR)
  - Control hazards (branches, jumps)
  - Structural hazards (resource conflicts)

- **Memory System**
  - Cache hit/miss rates
  - Memory access patterns
  - Bandwidth utilization

## Advanced Features

### Workload-Specific Optimization

The framework can optimize pipeline configurations for specific workloads:

```python
# Define workload characteristics
workload = {
    'branch_ratio': 0.3,      # 30% branch instructions
    'memory_ratio': 0.4,      # 40% memory operations
    'arithmetic_ratio': 0.3   # 30% arithmetic
}

# Get optimized configuration
config = optimize_for_workload(workload)
```

### Custom Instruction Performance Modeling

Model complex custom instructions:

```python
# Matrix multiplication instruction
matmul = CustomInstructionDef(
    name="MATMUL4x4",
    execution_stages=["FETCH", "DECODE"] + ["MATMUL"] * 16 + ["WRITEBACK"],
    base_cycles=18,
    memory_accesses=32,
    description="4x4 matrix multiplication in hardware"
)
```

### Visualization and Reporting

Generate comprehensive analysis reports:

```python
# Create performance comparison charts
tester.plot_performance_comparison("performance.png")

# Generate detailed report
report = tester.generate_comparison_report()
print(report)

# Export data for further analysis
tester.export_results_json("results.json")
```

## Use Cases

### 1. **Academic Research**
- Compare different pipeline architectures
- Analyze ISA design trade-offs
- Study the impact of custom instructions
- Generate data for research papers

### 2. **Processor Design**
- Evaluate pipeline design choices
- Optimize for specific application domains
- Analyze performance bottlenecks
- Compare with existing architectures

### 3. **Education**
- Teach computer architecture concepts
- Demonstrate pipeline behavior
- Show the impact of design decisions
- Provide hands-on experience

### 4. **Industry Applications**
- Prototype specialized processors
- Evaluate custom instruction benefits
- Optimize for specific workloads
- Support design space exploration

## Configuration Options

### Pipeline Configuration

```c
typedef struct {
    char name[64];                    // Configuration name
    stage_type_t stages[8];           // Pipeline stages
    uint8_t depth;                    // Number of stages
    bool forwarding_enabled;          // Data forwarding
    bool branch_prediction_enabled;   // Branch prediction
    bool out_of_order_execution;      // OoO execution
    uint32_t clock_frequency;         // Clock frequency (MHz)
    uint32_t memory_latency;          // Memory access latency
    uint32_t branch_penalty;          // Branch misprediction penalty
    cache_config_t icache, dcache;    // Cache configurations
} pipeline_config_t;
```

### Cache Configuration

```c
typedef struct {
    bool enabled;            // Enable cache simulation
    uint32_t size;          // Cache size in bytes
    uint32_t line_size;     // Cache line size
    uint8_t associativity;  // Set associativity
    uint32_t hit_latency;   // Hit latency in cycles
    uint32_t miss_penalty;  // Miss penalty in cycles
} cache_config_t;
```

## Output Examples

### Performance Report

```
=== Pipeline Performance Comparison Report ===

Program: arithmetic_heavy
Configuration         CPI      IPC      Efficiency   Hazards
Single Cycle         3.000    0.333    33.3%        0
Classic 5-Stage      1.200    0.833    83.3%        4
Branch Prediction    1.100    0.909    90.9%        2
Deep Pipeline        1.400    0.714    71.4%        8

Best CPI: Branch Prediction (1.100)
Best IPC: Branch Prediction (0.909)
Best Efficiency: Branch Prediction (90.9%)
```

### Custom Instruction Analysis

```
ISA Extension Analysis:
LC-3 SIMD:
  Instructions: 4
  Avg Cycles: 2.8
  Max Cycles: 4
  Memory Intensive: 2
  Complexity Score: 1.45

LC-3 DSP:
  Instructions: 3
  Avg Cycles: 8.7
  Max Cycles: 16
  Memory Intensive: 2
  Complexity Score: 2.34
```

## Dependencies

### C/C++ Components
- CMake 3.12+
- C11 compatible compiler
- Standard math library

### Python Components
- Python 3.7+
- matplotlib (visualization)
- numpy (numerical computing)
- seaborn (statistical plotting)

## Installation

1. **Build the simulator with pipeline extensions:**
   ```bash
   cmake -S . -B build -DBUILD_PIPELINE_EXTENSIONS=ON
   cmake --build build
   ```

2. **Install Python dependencies:**
   ```bash
   pip install matplotlib numpy seaborn
   ```

3. **Run the demonstration:**
   ```bash
   python pipeline_demo.py
   ```

## Contributing

To add new features:

1. **Custom Instructions**: Add definitions in `isa_extension_analyzer.py`
2. **Pipeline Stages**: Extend `stage_type_t` in `pipeline_config.h`
3. **Metrics**: Add new metrics to `pipeline_metrics_t`
4. **Visualizations**: Create new plotting functions
5. **Benchmarks**: Add programs to `create_benchmark_programs()`

## License

This extension maintains the same license as the base LC-3 simulator project.

## Support

For questions, issues, or contributions:
- Check the existing documentation
- Review the demo scripts
- Examine the test programs
- Refer to the comprehensive examples provided
