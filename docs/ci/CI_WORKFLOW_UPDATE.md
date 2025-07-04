# CI Workflow Update

This document outlines the updated CI workflow system for the LC-3 Simulator project.

## Overview

The CI workflow system has been unified to use the central build interface. This provides several key benefits:

1. **Maintainability**: All CI workflows use the same code as local development
2. **Consistency**: Builds and tests run the same way in CI as they do locally
3. **Centralization**: All build logic is in one place, reducing duplication
4. **Extensibility**: New CI tasks can be added easily by updating the command handlers

## CI Workflow Interface

The CI workflows are now managed through the central build system:

```bash
# Run a CI workflow locally
./build.py ci --workflow <workflow-name>

# Available workflows:
# - default: Standard CI build and test
# - nightly: Comprehensive build and test suite
# - cross-platform: Platform-specific build and tests
```

## CI Workflow Implementation

The CI workflows are implemented in `build_system/ci_commands.py` and provide the following functionality:

### Default Workflow

The default workflow:
1. Installs dependencies
1. Builds the simulator with Python bindings and pipeline extensions
2. Runs tests with code coverage reporting

### Nightly Workflow

The nightly workflow:
1. Performs a complete clean of all artifacts
2. Builds the simulator with all features enabled
3. Runs the complete test suite with coverage reporting
4. Runs ISA analysis and other comprehensive tests

### Cross-Platform Workflow

The cross-platform workflow:
1. Detects the current platform (Windows, macOS, Linux)
2. Configures platform-specific build settings
3. Builds the simulator with appropriate options
4. Runs a subset of platform-independent tests

## Script Running Interface

A new command has been added to run scripts with the proper environment configuration:

```bash
# Run a script with the build environment
./build.py run-script --script <script-path>
```

This ensures all scripts have access to the project modules, paths, and environment variables.

## GitHub Actions Integration

The GitHub Actions workflows have been updated to use the unified interface:

1. **ci.yml**: Uses `./build.py ci --workflow default`
2. **cross_platform_ci.yml**: Uses `./build.py ci --workflow cross-platform`
3. **nightly.yml**: Uses `./build.py ci --workflow nightly`

All analysis and utility scripts are now run through the `run-script` command to ensure consistent environment setup.

## Maintenance Guide

### Adding New CI Tasks

To add a new CI task:

1. Add the task implementation to the appropriate CI workflow function in `build_system/ci_commands.py`
2. If needed, update the GitHub Actions workflow files to call the new functionality

### Adding New Workflows

To add a new workflow:

1. Add a new workflow function in `build_system/ci_commands.py`
2. Update the `run_ci()` function to handle the new workflow
3. Create a new GitHub Actions workflow file if needed

### Debugging CI Issues

To debug CI issues:

1. Run the workflow locally: `./build.py ci --workflow <workflow-name>`
2. Check the output for errors
3. Modify the workflow implementation as needed
