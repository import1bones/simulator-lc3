#!/usr/bin/env python3
"""
Post-build script to fix Python bindings path on Windows.

This script ensures that Python bindings built in Release/Debug subdirectories
are copied to the expected location for the test runner.
"""

import sys
import shutil
from pathlib import Path
import glob


def fix_python_bindings(project_root=None):
    """Copy Python bindings from build subdirectories to expected location."""
    if project_root is None:
        project_root = Path(__file__).parent.parent
    else:
        project_root = Path(project_root)
    
    build_dir = project_root / "build" / "python_bindings"
    
    if not build_dir.exists():
        print("❌ Python bindings build directory not found")
        return False
    
    # Look for Python module files in subdirectories
    patterns = [
        "Release/*.pyd",   # Windows Release build
        "Debug/*.pyd",     # Windows Debug build  
        "Release/*.so",    # Linux Release build
        "Debug/*.so",      # Linux Debug build
        "*.so",            # Direct build (Linux/macOS)
        "*.pyd"            # Direct build (Windows)
    ]
    
    found_modules = []
    for pattern in patterns:
        matches = list(build_dir.glob(pattern))
        found_modules.extend(matches)
    
    if not found_modules:
        print("❌ No Python module files found in build directory")
        return False
    
    # Copy modules to the expected location
    copied = []
    for module_path in found_modules:
        target_path = build_dir / module_path.name
        
        if target_path.exists() and target_path.samefile(module_path):
            # Same file, skip
            continue
            
        try:
            shutil.copy2(module_path, target_path)
            copied.append(f"{module_path.name}")
            print(f"✅ Copied {module_path.name} to python_bindings/")
        except Exception as e:
            print(f"❌ Failed to copy {module_path.name}: {e}")
            return False
    
    if copied:
        print(f"✅ Fixed Python bindings path: {', '.join(copied)}")
    else:
        print("✅ Python bindings already in correct location")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = None
        
    success = fix_python_bindings(project_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
