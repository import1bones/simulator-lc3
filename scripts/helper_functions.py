"""
Helper functions for project validation and utilities.

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

import os
import subprocess
from pathlib import Path


def ensure_pybind11():
    """Check for and install pybind11 if needed."""
    try:
        import_cmd = ["python3", "-c", "import pybind11; print(pybind11.__version__)"]
        result = subprocess.run(
            import_cmd, capture_output=True, text=True, check=False
        )
        
        if result.returncode == 0:
            print(f"✅ pybind11 version {result.stdout.strip()} is installed")
            return True
        
        print("⚠️ pybind11 not found, attempting to install...")
        install_cmd = ["pip3", "install", "pybind11"]
        result = subprocess.run(
            install_cmd, capture_output=True, text=True, check=False
        )
        
        if result.returncode != 0:
            # Try with --user flag as fallback
            install_cmd = ["pip3", "install", "--user", "pybind11"]
            result = subprocess.run(
                install_cmd, capture_output=True, text=True, check=False
            )
            
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️ Error checking/installing pybind11: {e}")
        return False


def create_compatibility_makefile(project_root):
    """Create a compatibility Makefile that delegates to build.py."""
    makefile_path = project_root / "Makefile"
    if makefile_path.exists():
        return True
        
    try:
        makefile_content = """# Compatibility Makefile that delegates to build.py
.PHONY: all build clean test docs

all: build

build:
	./build.py build

build-with-python:
	./build.py build --with-python-bindings

test:
	./build.py test

clean:
	./build.py clean

docs:
	./build.py docs

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all              : Default target, builds the project"
	@echo "  build            : Build the project"
	@echo "  build-with-python: Build with Python bindings"
	@echo "  test             : Run tests"
	@echo "  clean            : Clean build artifacts"
	@echo "  docs             : Generate documentation"
"""
        with open(makefile_path, "w", encoding="utf-8") as f:
            f.write(makefile_content)
        print("📝 Created compatibility Makefile")
        return True
    except Exception as e:
        print(f"⚠️ Error creating Makefile: {e}")
        return False


def setup_python_paths(build_dir):
    """Set up Python paths for finding the bindings."""
    python_paths = [str(build_dir)]
    
    # Add specific subdirectories that might contain the bindings
    subdirs = ["python_bindings", "lib", "bin", "."]
    for subdir in subdirs:
        python_paths.append(str(build_dir / subdir))
    
    # Find the actual .so or .dylib files if they exist
    import glob
    for pattern in ["**/lc3_simulator*.so", "**/lc3_simulator*.dylib"]:
        for path in build_dir.glob(pattern):
            python_paths.append(str(path.parent))
    
    return python_paths
