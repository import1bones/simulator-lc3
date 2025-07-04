#!/usr/bin/env python3
"""
Script to add license headers to source files.

This script adds the MIT license header to all source files in the project
that don't already have it.
"""

import os
import re
import sys
from pathlib import Path

# File types to process
SOURCE_EXTENSIONS = [".h", ".hpp", ".c", ".cpp", ".py"]

# License header template
LICENSE_HEADER = """/**
 * @file {filename}
 * @brief {brief_description}
 *
 * LC-3 Simulator with Pipeline Extensions
 *
 * MIT License
 * Copyright (c) 2025 LC-3 Simulator Project Contributors
 */

"""

PYTHON_LICENSE_HEADER = '''"""
{brief_description}

LC-3 Simulator with Pipeline Extensions

MIT License
Copyright (c) 2025 LC-3 Simulator Project Contributors
"""

'''

# Directories to skip
SKIP_DIRS = [
    "build",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
]


def has_license_header(content):
    """Check if file already has a license header."""
    return "MIT License" in content or "Copyright" in content


def generate_brief_description(filepath):
    """Generate a brief description based on the filename."""
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]

    # Convert snake_case or camelCase to words
    words = re.sub(r"([a-z])([A-Z])", r"\1 \2", name_without_ext)
    words = words.replace("_", " ")
    words = words.title()

    return f"{words} implementation"


def add_header_to_file(filepath):
    """Add license header to a file if it doesn't have one."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if has_license_header(content):
        print(f"Skipping {filepath} (already has license)")
        return False

    filename = os.path.basename(filepath)
    brief = generate_brief_description(filepath)

    if filepath.endswith(".py"):
        header = PYTHON_LICENSE_HEADER.format(brief_description=brief)
    else:
        header = LICENSE_HEADER.format(filename=filename, brief_description=brief)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)

    print(f"Added license to {filepath}")
    return True


def process_directory(directory):
    """Process all source files in a directory and its subdirectories."""
    count = 0

    for root, dirs, files in os.walk(directory):
        # Skip directories in the skip list
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in SOURCE_EXTENSIONS:
                filepath = os.path.join(root, file)
                if add_header_to_file(filepath):
                    count += 1

    return count


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.join(directory, "..")  # Go up one level to project root
        directory = os.path.abspath(directory)

    print(f"Adding license headers to source files in {directory}")
    count = process_directory(directory)
    print(f"Added license headers to {count} files")


if __name__ == "__main__":
    main()
