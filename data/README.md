# Data Directory

This directory contains generated data files from analysis tools and benchmarks.

## Files

### Analysis Results (JSON Format)
- **`enhanced_isa_analysis_[timestamp].json`** - Complete ISA design analysis results
- **`enhanced_mips_benchmark_[timestamp].json`** - MIPS-style benchmark performance data

## Data Structure

### ISA Analysis Data
```json
{
  "metadata": {
    "timestamp": "ISO 8601 timestamp",
    "simulator_available": boolean,
    "analysis_type": "Enhanced ISA Design Analysis"
  },
  "instruction_characteristics": {
    "instruction_name": {
      "opcode": "string",
      "instruction_class": "arithmetic|memory|control|misc",
      "format_type": "R-type|I-type|J-type",
      "cycles_unpipelined": integer,
      "cycles_pipelined": float,
      "memory_operations": integer,
      "register_dependencies": integer,
      "encoding_efficiency": float,
      "pipeline_stages": ["IF", "ID", "EX", "MEM", "WB"],
      "hazard_potential": integer,
      "throughput_factor": float
    }
  },
  "cpi_analysis": {
    "unpipelined": {"cpi": float, "ipc": float},
    "ideal_pipelined": {"cpi": float, "ipc": float, "speedup": float},
    "realistic_pipelined": {"cpi": float, "ipc": float, "speedup": float}
  },
  "encoding_efficiency": {
    "overall_efficiency": float,
    "format_summary": {...},
    "comparison_to_mips": {...}
  },
  "risc_adherence": {
    "overall_risc_score": float,
    "principle_scores": {...},
    "recommendations": [...]
  },
  "comprehensive_metrics": {
    "average_cpi_unpipelined": float,
    "average_cpi_pipelined": float,
    "ipc_potential": float,
    "instruction_density": float,
    "encoding_efficiency": float,
    "risc_score": float,
    "pipeline_efficiency": float,
    "hazard_frequency": float
  }
}
```

### Benchmark Data
```json
{
  "metadata": {
    "timestamp": "ISO 8601 timestamp",
    "simulator_available": boolean,
    "benchmark_type": "Enhanced MIPS-Style Architectural Benchmark"
  },
  "benchmarks": [
    {
      "name": "string",
      "instructions_executed": integer,
      "total_cycles": integer,
      "execution_time": float,
      "cpi": float,
      "ipc": float,
      "cache_hits": integer,
      "cache_misses": integer,
      "cache_hit_rate": float,
      "branch_instructions": integer,
      "branch_taken": integer,
      "branch_mispredictions": integer,
      "branch_prediction_rate": float,
      "pipeline_stalls": integer,
      "hazard_stalls": integer,
      "pipeline_efficiency": float,
      "instruction_mix": {...},
      "performance_score": float
    }
  ],
  "architectural_analysis": {
    "bottlenecks": [...],
    "recommendations": [...],
    "efficiency_score": float,
    "risc_adherence": float,
    "scalability_potential": float
  }
}
```

## Key Metrics Summary

### Current Performance Data (Latest Analysis)

#### ISA Design Metrics:
- **CPI (Unpipelined)**: 1.590
- **CPI (Pipelined)**: 1.339
- **IPC Potential**: 0.747
- **Encoding Efficiency**: 85.7%
- **RISC Score**: 68.2/100
- **Pipeline Efficiency**: 15.8%
- **Hazard Frequency**: 52.9%

#### Benchmark Performance:
- **Average CPI**: 1.243
- **Average IPC**: 0.812
- **Cache Hit Rate**: 85.0%
- **Branch Prediction**: 75.0%
- **Pipeline Efficiency**: 88.7%
- **Performance Score**: 83.1/100

## Data Usage

### Loading Data in Python
```python
import json

# Load ISA analysis data
with open('data/enhanced_isa_analysis_[timestamp].json', 'r') as f:
    isa_data = json.load(f)

# Load benchmark data
with open('data/enhanced_mips_benchmark_[timestamp].json', 'r') as f:
    benchmark_data = json.load(f)

# Access specific metrics
cpi = isa_data['comprehensive_metrics']['average_cpi_unpipelined']
performance_score = benchmark_data['benchmarks'][0]['performance_score']
```

### Data Analysis Examples
```python
# Calculate performance trends
timestamps = [extract_timestamp(f) for f in data_files]
cpi_values = [load_data(f)['comprehensive_metrics']['average_cpi_unpipelined']
              for f in data_files]

# Compare different analysis runs
efficiency_scores = [data['architectural_analysis']['efficiency_score']
                    for data in benchmark_results]
```

## File Naming Convention

- **Format**: `[analysis_type]_[YYYYMMDD]_[HHMMSS].json`
- **Example**: `enhanced_isa_analysis_20250629_171215.json`
- **Timestamp**: Local time when analysis was run

## Data Retention

- **Development**: Keep recent analysis data for comparison
- **Production**: Archive older data files periodically
- **Backup**: Include in project backups for reproducibility

## Related Files

- **Analysis Scripts**: `../analysis/` directory
- **Generated Reports**: `../reports/` directory
- **Source Code**: Changes tracked via Git for reproducibility
