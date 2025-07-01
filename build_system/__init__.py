"""
LC-3 Simulator Build System
===========================

A comprehensive, cross-platform build architecture for the LC-3 simulator.

This package provides:
- Cross-platform build support (Windows, Linux, macOS)
- Dependency management
- Test execution and reporting
- CI/CD integration
- Package generation
"""

from .core import (
    BuildPlatform,
    BuildType,
    Architecture,
    BuildConfiguration,
    ProjectSettings,
    BuildLogger,
    BuildException,
    PlatformDetector
)

from .dependencies import (
    SystemDependencyManager,
    PythonDependencyManager,
    DependencyResolver
)

from .builders import (
    CMakeBuilder,
    PythonBuilder,
    LC3Builder
)

from .testing import (
    TestRunner,
    CoverageReporter,
    TestReportGenerator
)

from .packaging import (
    PackageManager,
    DistributionBuilder
)

# Optional CI module (requires PyYAML)
try:
    from .ci import (
        CIConfig,
        GitHubActionsGenerator,
        BuildMatrix
    )
    CI_AVAILABLE = True
except ImportError:
    CI_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "LC-3 Simulator Team"

# Default configurations for common use cases
DEFAULT_CONFIG = BuildConfiguration(
    platform=PlatformDetector.get_platform(),
    architecture=PlatformDetector.get_architecture(),
    build_type=BuildType.DEBUG
)

DEFAULT_PROJECT = ProjectSettings()

# Convenience function for quick setup
def create_builder(**kwargs):
    """Create a complete LC-3 builder with default settings."""
    from .builders import LC3Builder
    
    config = kwargs.get('config', DEFAULT_CONFIG)
    project = kwargs.get('project', DEFAULT_PROJECT)
    logger = kwargs.get('logger', BuildLogger('LC3BuildSystem'))
    
    return LC3Builder(config, project, logger)
