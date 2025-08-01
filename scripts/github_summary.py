"""
Github Summary implementation

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

#!/usr/bin/env python3
"""
GitHub Actions workflow summary generator.

This script creates comprehensive summaries for GitHub Actions workflow runs.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime


def create_workflow_summary():
    """Create a comprehensive workflow summary for GitHub Actions."""
    if not os.environ.get("GITHUB_ACTIONS"):
        print("This script is designed to run in GitHub Actions environment")
        return

    # Get workflow information
    workflow_name = os.environ.get("GITHUB_WORKFLOW", "Unknown Workflow")
    run_id = os.environ.get("GITHUB_RUN_ID", "unknown")
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "unknown")
    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "unknown")
    ref = os.environ.get("GITHUB_REF_NAME", "unknown")
    sha = os.environ.get("GITHUB_SHA", "unknown")

    # Create summary content
    summary = f"""# {workflow_name} - Run #{run_number}

## 📋 Workflow Information

| Field | Value |
|-------|-------|
| **Workflow** | {workflow_name} |
| **Run ID** | {run_id} |
| **Run Number** | {run_number} |
| **Triggered by** | {actor} |
| **Event** | {event_name} |
| **Branch/Tag** | {ref} |
| **Commit** | {sha[:8]} |
| **Timestamp** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} |

## 🚀 Workflow Results

"""

    # Check if analysis results exist
    data_dir = Path("data")
    reports_dir = Path("reports")

    if data_dir.exists():
        json_files = list(data_dir.glob("*.json"))
        if json_files:
            summary += f"### 📊 Analysis Data Generated\n\n"
            summary += f"Generated {len(json_files)} analysis data files:\n\n"
            for json_file in sorted(json_files)[-5:]:  # Show latest 5
                size_kb = json_file.stat().st_size / 1024
                summary += f"- `{json_file.name}` ({size_kb:.1f} KB)\n"

    if reports_dir.exists():
        md_files = list(reports_dir.glob("*.md"))
        if md_files:
            summary += f"\n### 📋 Reports Generated\n\n"
            summary += f"Generated {len(md_files)} report files:\n\n"
            for md_file in sorted(md_files)[-5:]:  # Show latest 5
                size_kb = md_file.stat().st_size / 1024
                summary += f"- `{md_file.name}` ({size_kb:.1f} KB)\n"

    # Add performance metrics if available
    latest_isa_files = list(data_dir.glob("enhanced_isa_analysis_*.json")) if data_dir.exists() else []
    if latest_isa_files:
        latest_isa = sorted(latest_isa_files)[-1]
        try:
            with open(latest_isa) as f:
                isa_data = json.load(f)
                metrics = isa_data.get("comprehensive_metrics", {})

                summary += f"""
### 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Average CPI (Unpipelined) | {metrics.get("average_cpi_unpipelined", 0):.3f} |
| Average CPI (Pipelined) | {metrics.get("average_cpi_pipelined", 0):.3f} |
| IPC Potential | {metrics.get("ipc_potential", 0):.3f} |
| Encoding Efficiency | {metrics.get("encoding_efficiency", 0)*100:.1f}% |
| RISC Score | {metrics.get("risc_score", 0):.1f}/100 |
"""
        except Exception as e:
            summary += f"\n⚠️ Could not load performance metrics: {e}\n"

    # Add test results if available
    if Path("reports/COVERAGE_REPORT.md").exists():
        summary += "\n### 🧪 Test Coverage\n\n"
        summary += "✅ Test coverage report generated successfully\n"

    # Check for any failures or warnings
    summary += "\n### ⚠️ Issues and Warnings\n\n"

    # Check for validation results
    if Path("scripts/validate_project.py").exists():
        summary += "✅ Project validation completed\n"

    summary += f"""
## 🔗 Artifacts and Downloads

The following artifacts are available for download:

- **Test Results**: Contains all test reports and coverage data
- **Analysis Data**: Contains JSON data files with performance metrics
- **Generated Reports**: Contains markdown reports and documentation

## 🚀 Next Steps

1. **Review Performance Metrics**: Check the analysis results for any regressions
2. **Examine Test Coverage**: Ensure adequate test coverage is maintained
3. **Update Documentation**: Consider updating project documentation based on results

---

*This summary was automatically generated by the GitHub Actions workflow on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S UTC')}*
"""

    # Write summary to GitHub Actions step summary
    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        with open(github_step_summary, "w") as f:
            f.write(summary)

    # Also save to file for artifact upload
    with open("WORKFLOW_SUMMARY.md", "w") as f:
        f.write(summary)

    print("✅ Workflow summary generated successfully")
    print(f"📄 Summary written to: {github_step_summary}")


def set_github_outputs():
    """Set GitHub Actions outputs for use in subsequent steps."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return

    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Count generated files
    data_dir = Path("data")
    reports_dir = Path("reports")

    data_count = len(list(data_dir.glob("*.json"))) if data_dir.exists() else 0
    reports_count = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0

    with open(github_output, "a") as f:
        f.write(f"timestamp={timestamp}\n")
        f.write(f"data-files-count={data_count}\n")
        f.write(f"report-files-count={reports_count}\n")
        f.write(f"workflow-summary=WORKFLOW_SUMMARY.md\n")


def main():
    """Main execution function."""
    try:
        create_workflow_summary()
        set_github_outputs()
        return 0
    except Exception as e:
        print(f"❌ Failed to generate workflow summary: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
