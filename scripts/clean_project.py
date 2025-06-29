#!/usr/bin/env python3
"""
Clean up auto-generated files from the LC-3 simulator project.

This script removes:
- Auto-generated analysis reports with timestamps
- Auto-generated data files with timestamps  
- Auto-documentation directories
- Build artifacts (optional)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def clean_generated_files(project_root, include_build=False):
    """Clean up generated files."""
    print("🧹 Cleaning up auto-generated files...")

    # Remove auto-generated files from various locations
    patterns_and_dirs = [
        # Reports with timestamps
        (project_root / "reports", ["enhanced_*_*.md", "enhanced_*_*.json", "*_[0-9]*.md", "*_[0-9]*.json"]),
        # Data files with timestamps
        (project_root / "data", ["enhanced_*_*.json", "*_[0-9]*.json", "*_[0-9]*.csv"]),
        # Auto-generated docs (but keep static ones)
        (project_root / "docs", ["COMPREHENSIVE_ANALYSIS_SUMMARY.md", "REPORTS_INDEX.md"]),
        # Root level generated files
        (project_root, ["enhanced_*_*.json", "enhanced_*_*.md"]),
    ]

    # Add build directory if requested
    if include_build:
        patterns_and_dirs.append((project_root, ["build"]))

    # Add auto-docs directory
    patterns_and_dirs.append((project_root, ["auto-docs"]))

    files_removed = 0
    dirs_removed = 0

    for base_dir, patterns in patterns_and_dirs:
        if not base_dir.exists():
            continue
            
        for pattern in patterns:
            if pattern in ["auto-docs", "build"]:
                # Handle directories
                target_dir = base_dir / pattern
                if target_dir.exists():
                    try:
                        shutil.rmtree(target_dir)
                        print(f"🗑️ Removed directory: {target_dir}")
                        dirs_removed += 1
                    except Exception as e:
                        print(f"⚠️ Could not remove directory {target_dir}: {e}")
            else:
                # Handle file patterns
                for file_path in base_dir.glob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            print(f"🗑️ Removed: {file_path}")
                            files_removed += 1
                        except Exception as e:
                            print(f"⚠️ Could not remove {file_path}: {e}")

    print(f"🧹 Cleanup completed! Removed {files_removed} files and {dirs_removed} directories.")
    return files_removed + dirs_removed > 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Clean auto-generated files from LC-3 simulator project")
    parser.add_argument("--include-build", action="store_true", 
                       help="Also remove build directory (forces rebuild)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be removed without actually removing")
    
    args = parser.parse_args()

    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print(f"📁 Working in project: {project_root}")

    if args.dry_run:
        print("🔍 DRY RUN MODE - no files will be removed")
        # For dry run, just show what would be removed
        print("Would remove auto-generated files matching these patterns:")
        patterns = [
            "reports/enhanced_*_*.md", "reports/enhanced_*_*.json", 
            "reports/*_[0-9]*.md", "reports/*_[0-9]*.json",
            "data/enhanced_*_*.json", "data/*_[0-9]*.json", "data/*_[0-9]*.csv",
            "docs/COMPREHENSIVE_ANALYSIS_SUMMARY.md", "docs/REPORTS_INDEX.md",
            "enhanced_*_*.json", "enhanced_*_*.md", "auto-docs/"
        ]
        if args.include_build:
            patterns.append("build/")
        
        for pattern in patterns:
            print(f"  - {pattern}")
        return 0

    # Actually clean files
    if clean_generated_files(project_root, args.include_build):
        print("✅ Project cleaned successfully!")
        return 0
    else:
        print("ℹ️ No files to clean.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
