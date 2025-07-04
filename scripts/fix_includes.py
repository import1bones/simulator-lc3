#!/usr/bin/env python3
"""
Script to fix include paths in source files after directory reorganization.
"""
import os
import sys
import re

def fix_includes(file_path):
    """Fix include paths in a source file."""
    with open(file_path, 'r') as file:
        content = file.read()

    # Fix memory includes
    content = re.sub(r'#include\s*["\']../mem/', '#include "../memory/', content)
    
    # Fix type includes
    content = re.sub(r'#include\s*["\']../type/', '#include "../types/', content)
    
    # Write changes back to the file
    with open(file_path, 'w') as file:
        file.write(content)
        
    print(f"Updated: {file_path}")

def process_directory(directory):
    """Process all source files in a directory."""
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(('.c', '.cpp', '.h')):
                file_path = os.path.join(root, filename)
                fix_includes(file_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
    
    print(f"Fixing includes in: {directory}")
    process_directory(directory)
    print("Done!")
