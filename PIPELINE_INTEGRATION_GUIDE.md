# LC-3 Integrated Pipeline Extension

## Overview

The LC-3 simulator now includes **integrated pipeline functionality** that extends the core simulator with custom instruction pipeline configuration and performance analysis capabilities. This enhancement enables users to design, test, and analyze custom pipelines and instruction sets for ISA performance evaluation.

## Key Features

### 🚀 **Fully Integrated Design**
- Pipeline functionality is built directly into the LC-3 core (`mem/control_store.h/.c`)
- No separate modules or external dependencies
- Seamless integration with existing LC-3 state machine

### 📊 **Performance Analysis**
- Real-time CPI (Cycles Per Instruction) calculation
- IPC (Instructions Per Cycle) metrics
- Pipeline efficiency measurement
- Hazard detection and analysis
- Memory access statistics

### ⚙️ **Configurable Pipeline**
- Customizable pipeline depth and stages
- Forwarding enable/disable
- Branch prediction options
- Out-of-order execution support
- Configurable timing parameters

### 🔍 **Hazard Detection**
- Data hazards (RAW, WAW, WAR)
- Control hazards (branches, jumps)
- Structural hazards (resource conflicts)
- Automatic stall insertion when needed

## Usage

### Command Line Options

```bash
# Run with pipeline mode enabled
./simulator-lc3 --pipeline program.obj

# Interactive mode with pipeline
./simulator-lc3 --pipeline --interactive

# Verbose pipeline output
./simulator-lc3 --pipeline --verbose program.obj
```

### Interactive Commands

When pipeline mode is enabled, additional commands are available:

```
(lc3-sim) pipeline    # Show pipeline status
(lc3-sim) metrics     # Display performance metrics
(lc3-sim) config      # Show pipeline configuration
```

### Example Session

```
$ ./simulator-lc3 --pipeline --interactive
LC-3 Simulator v1.0
Pipeline mode enabled
Initializing...
Pipeline mode enabled: LC-3 Default Pipeline

(lc3-sim) pipeline
Pipeline Status:
  Enabled: Yes
  Configuration: LC-3 Default Pipeline
  Depth: 5 stages
  Current Cycle: 0
  Forwarding: Enabled
  Branch Prediction: Disabled

(lc3-sim) load hello.obj
Loading program at address 0x3000
Program loaded successfully

(lc3-sim) step
Pipeline Status:
  Total Instructions: 1
  Total Cycles: 5
  CPI: 5.000
  Pipeline Efficiency: 20.00%

(lc3-sim) metrics
Pipeline Performance Metrics:
  Total Cycles: 5
  Total Instructions: 1
  CPI (Cycles per Instruction): 5.000
  IPC (Instructions per Cycle): 0.200
  Pipeline Efficiency: 20.00%
  Stall Cycles: 0
  Data Hazards: 0
  Control Hazards: 0
  Structural Hazards: 0
```

## Architecture

### Pipeline Stages

The default pipeline implements a classic 5-stage RISC design:

1. **FETCH** - Instruction fetch from memory
2. **DECODE** - Instruction decode and register read
3. **EXECUTE** - ALU operations and effective address calculation
4. **MEMORY** - Memory access for loads/stores
5. **WRITEBACK** - Register writeback

### Data Structures

#### Pipeline Configuration (`lc3_pipeline_config_t`)
```c
typedef struct {
    char name[64];                    // Pipeline name
    lc3_pipeline_stage_t stages[8];   // Stage definitions
    uint8_t depth;                    // Number of stages
    bool forwarding_enabled;          // Data forwarding
    bool branch_prediction_enabled;   // Branch prediction
    bool out_of_order_execution;      // OoO execution
    uint32_t clock_frequency;         // Clock in MHz
    uint32_t memory_latency;          // Memory access time
    uint32_t branch_penalty;          // Branch miss penalty
    bool enable_detailed_metrics;     // Detailed statistics
    bool enable_pipeline_trace;       // Execution tracing
} lc3_pipeline_config_t;
```

#### Performance Metrics (`lc3_pipeline_metrics_t`)
```c
typedef struct {
    uint64_t total_cycles;           // Total simulation cycles
    uint64_t total_instructions;     // Instructions completed
    uint64_t stall_cycles;           // Cycles spent stalled
    double cpi;                      // Cycles per instruction
    double ipc;                      // Instructions per cycle
    double pipeline_efficiency;     // Performance ratio
    uint64_t data_hazards;           // Data dependency conflicts
    uint64_t control_hazards;        // Branch/jump hazards
    uint64_t structural_hazards;     // Resource conflicts
    uint64_t memory_reads;           // Memory read operations
    uint64_t memory_writes;          // Memory write operations
    uint64_t memory_stall_cycles;    // Memory-induced stalls
} lc3_pipeline_metrics_t;
```

### API Functions

#### Initialization
- `lc3_pipeline_init()` - Initialize pipeline with defaults
- `lc3_pipeline_reset()` - Reset pipeline state
- `lc3_pipeline_configure()` - Apply custom configuration

#### Execution
- `lc3_pipeline_cycle()` - Execute one pipeline cycle
- `lc3_pipeline_issue_instruction()` - Issue instruction to pipeline
- `lc3_pipeline_get_metrics()` - Retrieve performance statistics

## Integration Points

### State Machine Integration

The pipeline is integrated into the main LC-3 state machine (`state_machine/state_machine.cpp`):

```cpp
void state_machine(pointer_count_t &pc, word_t *mem, lc3_register_t *reg) {
    initialize_state_machine(pc);

    while (should_continue_execution()) {
        // Pipeline simulation integration
        if (lc3_pipeline_enabled) {
            if (current_state == FETCH1) {
                lc3_pipeline_issue_instruction(mem[pc], pc);
            }
            lc3_pipeline_cycle();
        }

        execute_current_state();
        current_state = get_next_state();

        if (check_halt_conditions(mem)) break;
    }

    finalize_state_machine(pc);
}
```

### Memory Integration

Pipeline state is managed in the control store module (`mem/control_store.h/.c`):

- Global pipeline configuration and metrics
- Instruction packet structures
- Pipeline management functions
- Hazard detection logic

## Performance Analysis Features

### Hazard Detection

The pipeline automatically detects and handles various types of hazards:

1. **Data Hazards**
   - RAW (Read After Write) - Most common
   - WAW (Write After Write) - Register reuse
   - WAR (Write After Read) - Anti-dependencies

2. **Control Hazards**
   - Branch instructions
   - Jump instructions
   - Configurable branch prediction

3. **Structural Hazards**
   - Resource conflicts
   - Pipeline stage collisions

### Metrics Collection

The system tracks comprehensive performance metrics:

- **Throughput**: Instructions per cycle (IPC)
- **Efficiency**: Pipeline utilization percentage
- **Latency**: Average cycles per instruction (CPI)
- **Stalls**: Cycles lost to hazards and conflicts
- **Memory**: Read/write operations and stalls

## Example Programs

### Basic Pipeline Test

```c
#include "mem/control_store.h"

int main() {
    // Initialize pipeline
    lc3_pipeline_init();

    // Issue some instructions
    lc3_pipeline_issue_instruction(0x1220, 0x3000);  // ADD R1, R0, #0
    lc3_pipeline_issue_instruction(0x1401, 0x3001);  // ADD R2, R0, #1

    // Run pipeline cycles
    for (int i = 0; i < 10; i++) {
        lc3_pipeline_cycle();
    }

    // Get metrics
    lc3_pipeline_metrics_t metrics;
    lc3_pipeline_get_metrics(&metrics);
    printf("CPI: %.3f, Efficiency: %.1f%%\n",
           metrics.cpi, metrics.pipeline_efficiency * 100.0);

    return 0;
}
```

### Hazard Analysis

```c
// Disable forwarding to see hazards
lc3_pipeline_config.forwarding_enabled = false;

// Issue dependent instructions
lc3_pipeline_issue_instruction(0x1220, 0x3000);  // ADD R1, R0, #0
lc3_pipeline_issue_instruction(0x1041, 0x3001);  // ADD R2, R1, #1  // RAW hazard!

// Check for stalls
lc3_pipeline_metrics_t metrics;
lc3_pipeline_get_metrics(&metrics);
printf("Data hazards: %llu, Stalls: %llu\n",
       metrics.data_hazards, metrics.stall_cycles);
```

## Custom Configuration

### Creating Custom Pipeline Configurations

```c
lc3_pipeline_config_t custom_config;
lc3_pipeline_config_init_default(&custom_config);

// Customize settings
strcpy(custom_config.name, "Custom High-Performance Pipeline");
custom_config.depth = 7;  // 7-stage pipeline
custom_config.forwarding_enabled = true;
custom_config.branch_prediction_enabled = true;
custom_config.clock_frequency = 200;  // 200 MHz
custom_config.branch_penalty = 1;     // Reduced penalty

// Apply configuration
lc3_pipeline_configure(&custom_config);
```

## Build Configuration

### CMake Integration

The pipeline functionality is automatically included in the build:

```cmake
# mem/CMakeLists.txt
add_library(mem
    control_store.c
)
target_include_directories(mem PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
```

### Compilation

No special flags or dependencies required - the pipeline is part of the core LC-3 build.

## Troubleshooting

### Common Issues

1. **Pipeline Not Enabled**
   - Use `--pipeline` command line flag
   - Check `lc3_pipeline_enabled` global variable

2. **No Metrics Showing**
   - Ensure instructions are being issued to pipeline
   - Call `lc3_pipeline_get_metrics()` after execution

3. **Unexpected Stalls**
   - Check if forwarding is disabled
   - Review instruction dependencies
   - Examine structural hazard conditions

### Debug Output

Enable verbose mode for detailed pipeline trace:

```bash
./simulator-lc3 --pipeline --verbose program.obj
```

## Future Enhancements

The integrated pipeline extension provides a foundation for advanced features:

- **Superscalar execution** - Multiple instruction issue
- **Out-of-order execution** - Dynamic instruction scheduling
- **Branch prediction** - Advanced prediction algorithms
- **Cache simulation** - Memory hierarchy modeling
- **Custom instruction sets** - User-defined instruction extensions

## Conclusion

The LC-3 pipeline extension successfully integrates advanced processor simulation capabilities directly into the core LC-3 simulator. This enables comprehensive ISA design exploration, performance analysis, and computer architecture education within a familiar and well-understood processor model.
