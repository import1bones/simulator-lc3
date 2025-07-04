#!/bin/bash
# Script to bootstrap the build system

# Make build.py executable
chmod +x build.py

# Create a symbolic link for convenience
ln -sf build.py lc3-build

echo "LC-3 Simulator build system initialized."
echo "Use './build.py' or './lc3-build' to access the build system."
echo ""
echo "Example commands:"
echo "  ./build.py build          # Build the simulator"
echo "  ./build.py test           # Run tests"
echo "  ./build.py setup          # Set up the environment"
echo "  ./build.py ci             # Run the CI workflow locally"
echo ""
