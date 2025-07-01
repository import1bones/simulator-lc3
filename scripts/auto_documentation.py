#!/usr/bin/env python3
"""
Auto-documentation generator for GitHub Actions.

This script ensures that analysis scripts generate consistent output
for automated documentation generation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_comprehensive_analysis():
    """Run all analysis scripts and collect results."""
    print("🚀 Running comprehensive analysis for auto-documentation...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Create output directories
    (project_root / "auto-docs").mkdir(exist_ok=True)
    (project_root / "auto-docs" / "data").mkdir(exist_ok=True)
    (project_root / "auto-docs" / "reports").mkdir(exist_ok=True)

    # Run analysis scripts with quiet mode to avoid generating unnecessary files
    scripts = [
        "python analysis/enhanced_isa_analysis.py --quiet",
        "python analysis/isa_design_analysis.py --quiet",
        "python analysis/mips_benchmark.py --quiet",
    ]

    results = {}

    for script in scripts:
        print(f"📊 Running: {script}")
        try:
            result = subprocess.run(script.split(), capture_output=True, text=True, check=True)
            script_name = script.split("/")[-1].replace(".py", "")
            results[script_name] = {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            script_name = script.split("/")[-1].replace(".py", "")
            results[script_name] = {
                "status": "failed",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
            print(f"❌ Failed: {script}")

    return results


def generate_summary_doc():
    """Generate comprehensive summary documentation."""
    print("📋 Generating summary documentation...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Load latest analysis data
    data_dir = Path("data")
    reports_dir = Path("reports")

    isa_files = list(data_dir.glob("enhanced_isa_analysis_*.json"))
    mips_files = list(data_dir.glob("mips_benchmark_*.json"))

    summary = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "timestamp": timestamp,
            "date": date_str,
            "version": os.environ.get("GITHUB_REF_NAME", "main"),
            "commit": os.environ.get("GITHUB_SHA", "unknown")
        },
        "analysis_summary": {},
        "performance_metrics": {},
        "test_results": {},
        "project_stats": {}
    }

    # Load ISA analysis
    if isa_files:
        latest_isa = sorted(isa_files)[-1]
        with open(latest_isa, encoding='utf-8') as f:
            isa_data = json.load(f)
            summary["analysis_summary"]["isa"] = {
                "file": latest_isa.name,
                "metrics": isa_data.get("comprehensive_metrics", {}),
                "cpi_analysis": isa_data.get("cpi_analysis", {}),
                "risc_adherence": isa_data.get("risc_adherence", {})
            }

    # Load MIPS benchmark (traditional)
    if mips_files:
        latest_mips = sorted(mips_files)[-1]
        with open(latest_mips, encoding='utf-8') as f:
            mips_data = json.load(f)
            summary["analysis_summary"]["mips"] = {
                "file": latest_mips.name,
                "summary": mips_data.get("performance_summary", {}),
                "benchmarks": mips_data.get("benchmarks", {})
            }

    # Collect project statistics
    summary["project_stats"] = {
        "total_python_files": len(list(Path(".").rglob("*.py"))),
        "total_cpp_files": len(list(Path(".").rglob("*.cpp"))) + len(list(Path(".").rglob("*.h"))),
        "test_files": len(list(Path("tests").glob("*.py"))) if Path("tests").exists() else 0,
        "analysis_scripts": len(list(Path("analysis").glob("*.py"))) if Path("analysis").exists() else 0,
        "utility_scripts": len(list(Path("scripts").glob("*.py"))) if Path("scripts").exists() else 0,
        "report_files": len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0,
        "data_files": len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0
    }

    # Save summary
    summary_file = Path("auto-docs") / f"ANALYSIS_SUMMARY_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    # Generate markdown report
    md_report = generate_markdown_summary(summary)
    md_file = Path("auto-docs") / f"ANALYSIS_SUMMARY_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_report)

    print(f"✅ Summary saved to: {summary_file}")
    print(f"✅ Markdown report saved to: {md_file}")

    return summary_file, md_file


def generate_markdown_summary(summary):
    """Generate markdown summary report."""
    metadata = summary["metadata"]
    isa = summary["analysis_summary"].get("isa", {})
    mips = summary["analysis_summary"].get("mips", {})
    stats = summary["project_stats"]

    md = f"""# LC-3 Simulator Analysis Summary

**Generated:** {metadata["generated_at"]}
**Version:** {metadata["version"]}
**Commit:** {metadata["commit"][:8]}

## 📊 Performance Overview

### ISA Design Metrics
"""

    if isa.get("metrics"):
        metrics = isa["metrics"]
        md += f"""
| Metric | Value |
|--------|-------|
| Average CPI (Unpipelined) | {metrics.get("average_cpi_unpipelined", 0):.3f} |
| Average CPI (Pipelined) | {metrics.get("average_cpi_pipelined", 0):.3f} |
| IPC Potential | {metrics.get("ipc_potential", 0):.3f} |
| Encoding Efficiency | {metrics.get("encoding_efficiency", 0)*100:.1f}% |
| RISC Score | {metrics.get("risc_score", 0):.1f}/100 |
| Pipeline Efficiency | {metrics.get("pipeline_efficiency", 0)*100:.1f}% |
"""

    md += "\n### MIPS Benchmark Results\n"

    if mips.get("summary"):
        summary_data = mips["summary"]
        md += f"""
| Benchmark | Score |
|-----------|-------|
| Average CPI | {summary_data.get("average_cpi", 0):.3f} |
| Performance Score | {summary_data.get("average_performance_score", 0):.1f}/100 |
| Efficiency Score | {summary_data.get("efficiency_score", 0):.1f}/100 |
| RISC Adherence | {summary_data.get("risc_adherence_score", 0):.1f}/100 |
"""

    md += f"""
## 📁 Project Statistics

| Category | Count |
|----------|-------|
| Python Files | {stats["total_python_files"]} |
| C++ Files | {stats["total_cpp_files"]} |
| Test Files | {stats["test_files"]} |
| Analysis Scripts | {stats["analysis_scripts"]} |
| Utility Scripts | {stats["utility_scripts"]} |
| Report Files | {stats["report_files"]} |
| Data Files | {stats["data_files"]} |

## 🔗 Data Sources

### ISA Analysis
- **File:** {isa.get("file", "N/A")}

### MIPS Benchmark
- **File:** {mips.get("file", "N/A")}

## 📈 Key Insights

"""

    # Add automated insights based on metrics
    if isa.get("metrics"):
        metrics = isa["metrics"]

        if metrics.get("risc_score", 0) >= 80:
            md += "✅ **Excellent RISC adherence** - Design follows RISC principles well\n"
        elif metrics.get("risc_score", 0) >= 60:
            md += "⚠️ **Good RISC adherence** - Room for improvement in RISC design\n"
        else:
            md += "❌ **Poor RISC adherence** - Consider redesigning for better RISC compliance\n"

        if metrics.get("encoding_efficiency", 0) >= 0.9:
            md += "✅ **Excellent encoding efficiency** - Instruction formats are well-optimized\n"
        elif metrics.get("encoding_efficiency", 0) >= 0.7:
            md += "⚠️ **Good encoding efficiency** - Some optimization opportunities exist\n"
        else:
            md += "❌ **Poor encoding efficiency** - Significant optimization needed\n"

        if metrics.get("ipc_potential", 0) >= 0.8:
            md += "✅ **High IPC potential** - Good parallelization opportunities\n"
        elif metrics.get("ipc_potential", 0) >= 0.5:
            md += "⚠️ **Moderate IPC potential** - Limited parallelization opportunities\n"
        else:
            md += "❌ **Low IPC potential** - Consider pipeline improvements\n"

    md += f"""
---

*This summary was automatically generated on {metadata["date"]} by the LC-3 Simulator analysis system.*
"""

    return md


def update_index_files():
    """Update index files with latest results."""
    print("📋 Updating index files...")

    # Update main reports index
    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = sorted(reports_dir.glob("*.md"))

        index_content = """# LC-3 Simulator Reports Index

This directory contains comprehensive analysis reports for the LC-3 simulator.

## 📊 Latest Reports

"""

        for report_file in sorted(report_files, reverse=True)[:10]:  # Show latest 10
            mod_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            index_content += f"- [{report_file.name}]({report_file.name}) - *{mod_time.strftime('%Y-%m-%d %H:%M')}*\n"

        index_content += """
## 📁 Report Categories

### ISA Analysis Reports
- Enhanced ISA analysis with comprehensive metrics
- Traditional ISA design analysis
- Performance comparison reports

### MIPS Benchmark Reports
- Enhanced MIPS-style benchmarking
- Traditional MIPS comparison
- Performance trend analysis

### Test Coverage Reports
- Comprehensive test coverage analysis
- Code quality metrics
- Performance regression detection

---

*This index is automatically updated by the GitHub Actions workflow.*
"""

        with open(reports_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(index_content)

    # Update data directory index
    data_dir = Path("data")
    if data_dir.exists():
        data_files = sorted(data_dir.glob("*.json"))

        data_index = """# LC-3 Simulator Data Files

This directory contains raw analysis data in JSON format.

## 📊 Latest Data Files

"""

        for data_file in sorted(data_files, reverse=True)[:10]:
            mod_time = datetime.fromtimestamp(data_file.stat().st_mtime)
            size_kb = data_file.stat().st_size / 1024
            data_index += f"- [{data_file.name}]({data_file.name}) - *{mod_time.strftime('%Y-%m-%d %H:%M')}* ({size_kb:.1f} KB)\n"

        data_index += """
## 📁 Data Categories

### ISA Analysis Data
- `enhanced_isa_analysis_*.json` - Enhanced ISA metrics
- `isa_design_analysis_*.json` - Traditional ISA analysis

### MIPS Benchmark Data
- `enhanced_mips_benchmark_*.json` - Enhanced MIPS benchmarks
- `mips_benchmark_*.json` - Traditional MIPS analysis

---

*This index is automatically updated by the GitHub Actions workflow.*
"""

        with open(data_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(data_index)


def main():
    """Main execution function."""
    print("🚀 Auto-Documentation Generator")
    print("=" * 50)

    try:
        # Run comprehensive analysis
        analysis_results = run_comprehensive_analysis()

        # Generate summary documentation
        summary_file, md_file = generate_summary_doc()

        # Update index files
        update_index_files()

        # Set GitHub Actions outputs
        if os.environ.get("GITHUB_ACTIONS"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"summary-file={summary_file}\n")
                f.write(f"markdown-file={md_file}\n")
                f.write(f"timestamp={datetime.now().strftime('%Y%m%d_%H%M%S')}\n")

        print("\n✅ Auto-documentation generation completed successfully!")

        # Print summary
        print("\n📋 Summary:")
        for script, result in analysis_results.items():
            status = "✅" if result["status"] == "success" else "❌"
            print(f"  {status} {script}: {result['status']}")

        return 0

    except Exception as e:
        print(f"\n❌ Auto-documentation generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
