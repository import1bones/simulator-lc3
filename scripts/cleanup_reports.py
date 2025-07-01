#!/usr/bin/env python3
"""
Clean up unnecessary generated reports and files.
This script removes timestamped analysis reports that clutter the repository.
"""

import os
import sys
import glob
from pathlib import Path

def clean_reports():
    """Clean up generated reports and analysis files"""
    project_root = Path(__file__).parent
    files_removed = 0
    
    print("🧹 Cleaning up unnecessary generated reports...")
    
    # Patterns to clean up
    cleanup_patterns = [
        # Root directory timestamped files
        "enhanced_isa_analysis_*.json",
        "enhanced_isa_analysis_*.md",
        "enhanced_mips_benchmark_*.json", 
        "enhanced_mips_benchmark_*.md",
        "isa_design_analysis_*.json",
        "isa_design_analysis_*.md",
        "mips_style_benchmark_*.json",
        "mips_style_benchmark_*.md",
        
        # Reports directory timestamped files
        "reports/*_[0-9]*.md",
        "reports/*_[0-9]*.json",
        "reports/*_[0-9]*.html",
        "reports/isa_benchmark_report_*.md",
        "reports/isa_benchmark_report_*.json",
        "reports/isa_design_analysis_*.md", 
        "reports/isa_design_analysis_*.json",
        "reports/mips_style_benchmark_*.md",
        "reports/mips_style_benchmark_*.json",
        
        # Auto-docs directory
        "auto-docs/*",
        
        # Test summaries
        "test_summary.json",
    ]
    
    for pattern in cleanup_patterns:
        files = glob.glob(str(project_root / pattern), recursive=True)
        for file_path in files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"  🗑️ Removed: {os.path.relpath(file_path, project_root)}")
                    files_removed += 1
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"  🗑️ Removed directory: {os.path.relpath(file_path, project_root)}")
                    files_removed += 1
            except Exception as e:
                print(f"  ⚠️ Could not remove {file_path}: {e}")
    
    # Special handling for auto-docs directory
    auto_docs_dir = project_root / "auto-docs"
    if auto_docs_dir.exists():
        try:
            import shutil
            shutil.rmtree(auto_docs_dir)
            print(f"  🗑️ Removed directory: auto-docs")
            files_removed += 1
        except Exception as e:
            print(f"  ⚠️ Could not remove auto-docs directory: {e}")
    
    # Keep essential reports but clean timestamped ones
    essential_files = [
        "reports/README.md",
        "reports/COMPREHENSIVE_TEST_COVERAGE_REPORT.md",
        "reports/CONDITION_COVERAGE_ANALYSIS.md",
        "reports/COVERAGE_REPORT.md",
        "reports/ISA_COMPREHENSIVE_PERFORMANCE_REPORT.md"
    ]
    
    print(f"\n✅ Cleanup complete! Removed {files_removed} files.")
    print("📄 Essential reports preserved:")
    for essential in essential_files:
        if (project_root / essential).exists():
            print(f"  ✓ {essential}")

def main():
    """Main cleanup function"""
    print("LC-3 Simulator Report Cleanup")
    print("=" * 40)
    print()
    
    clean_reports()
    
    print()
    print("🎯 Recommendation: Add --quiet flag to analysis scripts during validation:")
    print("  python analysis/enhanced_isa_analysis.py --quiet")
    print("  python analysis/isa_design_analysis.py --quiet")
    print("  python analysis/mips_benchmark.py --quiet")

if __name__ == "__main__":
    main()
