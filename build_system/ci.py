"""
Continuous Integration Support for LC-3 Simulator
==================================================

This module provides CI/CD configuration generation and management
for various platforms including GitHub Actions, GitLab CI, and more.
"""

import json
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .core import BuildPlatform, BuildType, BuildLogger, BuildException


class CIPlatform(Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    AZURE_PIPELINES = "azure_pipelines"
    JENKINS = "jenkins"


@dataclass
class BuildMatrix:
    """Configuration for build matrix across platforms."""
    platforms: List[BuildPlatform] = field(default_factory=lambda: [
        BuildPlatform.WINDOWS,
        BuildPlatform.LINUX,
        BuildPlatform.MACOS
    ])
    python_versions: List[str] = field(default_factory=lambda: ["3.8", "3.9", "3.10", "3.11"])
    build_types: List[BuildType] = field(default_factory=lambda: [BuildType.DEBUG, BuildType.RELEASE])
    include_coverage: bool = True
    include_performance_tests: bool = True
    parallel_jobs: int = 4


@dataclass
class CIConfig:
    """CI/CD configuration settings."""
    project_name: str
    platforms: List[CIPlatform]
    build_matrix: BuildMatrix
    artifacts_retention_days: int = 30
    cache_enabled: bool = True
    notifications_enabled: bool = True
    deploy_on_tag: bool = True
    
    # Secrets and environment variables
    required_secrets: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)


class GitHubActionsGenerator:
    """Generate GitHub Actions workflow configurations."""
    
    def __init__(self, config: CIConfig, logger: BuildLogger):
        self.config = config
        self.logger = logger
        self.project_root = Path.cwd()
        self.workflows_dir = self.project_root / ".github" / "workflows"
    
    def generate_main_workflow(self) -> Path:
        """Generate the main CI/CD workflow."""
        if not YAML_AVAILABLE:
            raise BuildException("PyYAML is required for CI configuration generation. Install with: pip install PyYAML")
        
        workflow = {
            "name": f"{self.config.project_name} CI/CD",
            "on": {
                "push": {
                    "branches": ["main", "develop"],
                    "tags": ["v*"]
                },
                "pull_request": {
                    "branches": ["main", "develop"]
                },
                "schedule": [
                    {"cron": "0 2 * * 1"}  # Weekly on Monday at 2 AM
                ]
            },
            "env": self.config.environment_variables,
            "jobs": self._generate_jobs()
        }
        
        # Ensure workflows directory exists
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Write workflow file
        workflow_file = self.workflows_dir / "ci.yml"
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"Generated GitHub Actions workflow: {workflow_file}")
        return workflow_file
    
    def _generate_jobs(self) -> Dict[str, Any]:
        """Generate all CI jobs."""
        jobs = {}
        
        # Build and test matrix job
        jobs["build-and-test"] = self._generate_build_test_job()
        
        # Coverage job (Linux only for simplicity)
        jobs["coverage"] = self._generate_coverage_job()
        
        # Performance testing job
        if self.config.build_matrix.include_performance_tests:
            jobs["performance"] = self._generate_performance_job()
        
        # Package job (on tags)
        jobs["package"] = self._generate_package_job()
        
        # Deploy job (on tags)
        if self.config.deploy_on_tag:
            jobs["deploy"] = self._generate_deploy_job()
        
        return jobs
    
    def _generate_build_test_job(self) -> Dict[str, Any]:
        """Generate the main build and test job with matrix."""
        # Convert enums to strings for matrix
        matrix_platforms = []
        for platform in self.config.build_matrix.platforms:
            if platform == BuildPlatform.WINDOWS:
                matrix_platforms.append({
                    "os": "windows-latest",
                    "platform": "windows",
                    "shell": "pwsh"
                })
            elif platform == BuildPlatform.LINUX:
                matrix_platforms.append({
                    "os": "ubuntu-latest", 
                    "platform": "linux",
                    "shell": "bash"
                })
            elif platform == BuildPlatform.MACOS:
                matrix_platforms.append({
                    "os": "macos-latest",
                    "platform": "macos", 
                    "shell": "bash"
                })
        
        return {
            "name": "Build and Test",
            "runs-on": "${{ matrix.os }}",
            "strategy": {
                "fail-fast": False,
                "matrix": {
                    "include": matrix_platforms,
                    "python-version": self.config.build_matrix.python_versions,
                    "build-type": [bt.value for bt in self.config.build_matrix.build_types]
                }
            },
            "defaults": {
                "run": {
                    "shell": "${{ matrix.shell }}"
                }
            },
            "steps": [
                {
                    "name": "Checkout code",
                    "uses": "actions/checkout@v4",
                    "with": {
                        "fetch-depth": 0
                    }
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {
                        "python-version": "${{ matrix.python-version }}"
                    }
                },
                {
                    "name": "Install system dependencies (Ubuntu)",
                    "if": "matrix.platform == 'linux'",
                    "run": [
                        "sudo apt-get update",
                        "sudo apt-get install -y cmake build-essential"
                    ]
                },
                {
                    "name": "Install system dependencies (macOS)",
                    "if": "matrix.platform == 'macos'",
                    "run": [
                        "brew install cmake"
                    ]
                },
                {
                    "name": "Setup MSVC (Windows)",
                    "if": "matrix.platform == 'windows'",
                    "uses": "microsoft/setup-msbuild@v1.3"
                },
                {
                    "name": "Cache Python dependencies",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "~/.cache/pip",
                        "key": "${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}",
                        "restore-keys": "${{ runner.os }}-pip-"
                    }
                },
                {
                    "name": "Cache CMake build",
                    "uses": "actions/cache@v3",
                    "with": {
                        "path": "build",
                        "key": "${{ runner.os }}-cmake-${{ matrix.build-type }}-${{ hashFiles('CMakeLists.txt', '**/CMakeLists.txt') }}",
                        "restore-keys": "${{ runner.os }}-cmake-${{ matrix.build-type }}-"
                    }
                },
                {
                    "name": "Install Python dependencies",
                    "run": [
                        "python -m pip install --upgrade pip",
                        "pip install -r requirements.txt"
                    ]
                },
                {
                    "name": "Configure CMake",
                    "run": [
                        f"cmake -B build -DCMAKE_BUILD_TYPE=${{{{ matrix.build-type }}}} -DBUILD_PYTHON_BINDINGS=ON"
                    ]
                },
                {
                    "name": "Build project",
                    "run": [
                        "cmake --build build --config ${{ matrix.build-type }} --parallel ${{ matrix.parallel-jobs || 4 }}"
                    ]
                },
                {
                    "name": "Run tests",
                    "run": [
                        "python build_and_test.py --test-only --verbose"
                    ]
                },
                {
                    "name": "Upload test results",
                    "uses": "actions/upload-artifact@v3",
                    "if": "always()",
                    "with": {
                        "name": "test-results-${{ matrix.platform }}-${{ matrix.python-version }}-${{ matrix.build-type }}",
                        "path": [
                            "test_results_*.json",
                            "test_report_*.html",
                            "htmlcov/"
                        ],
                        "retention-days": self.config.artifacts_retention_days
                    }
                },
                {
                    "name": "Upload build artifacts",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "build-artifacts-${{ matrix.platform }}-${{ matrix.build-type }}",
                        "path": [
                            "build/simulator-lc3*",
                            "build/**/*.dll",
                            "build/**/*.so",
                            "build/**/*.dylib",
                            "*.pyd",
                            "*.so"
                        ],
                        "retention-days": self.config.artifacts_retention_days
                    }
                }
            ]
        }
    
    def _generate_coverage_job(self) -> Dict[str, Any]:
        """Generate coverage reporting job."""
        return {
            "name": "Coverage Report",
            "runs-on": "ubuntu-latest",
            "needs": "build-and-test",
            "if": "github.event_name == 'push' && github.ref == 'refs/heads/main'",
            "steps": [
                {
                    "name": "Checkout code",
                    "uses": "actions/checkout@v4"
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {
                        "python-version": "3.11"
                    }
                },
                {
                    "name": "Install dependencies",
                    "run": [
                        "sudo apt-get update",
                        "sudo apt-get install -y cmake build-essential",
                        "python -m pip install --upgrade pip",
                        "pip install -r requirements.txt"
                    ]
                },
                {
                    "name": "Build and test with coverage",
                    "run": [
                        "python build_and_test.py --coverage --html-report"
                    ]
                },
                {
                    "name": "Upload coverage to Codecov",
                    "uses": "codecov/codecov-action@v3",
                    "with": {
                        "file": "coverage.json",
                        "flags": "unittests",
                        "name": "codecov-umbrella"
                    }
                },
                {
                    "name": "Upload coverage report",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "coverage-report",
                        "path": [
                            "htmlcov/",
                            "coverage.json"
                        ],
                        "retention-days": self.config.artifacts_retention_days
                    }
                }
            ]
        }
    
    def _generate_performance_job(self) -> Dict[str, Any]:
        """Generate performance testing job."""
        return {
            "name": "Performance Testing",
            "runs-on": "ubuntu-latest",
            "needs": "build-and-test",
            "if": "github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/'))",
            "steps": [
                {
                    "name": "Checkout code",
                    "uses": "actions/checkout@v4"
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {
                        "python-version": "3.11"
                    }
                },
                {
                    "name": "Install dependencies",
                    "run": [
                        "sudo apt-get update",
                        "sudo apt-get install -y cmake build-essential",
                        "python -m pip install --upgrade pip",
                        "pip install -r requirements.txt"
                    ]
                },
                {
                    "name": "Build project",
                    "run": [
                        "python build_and_test.py --no-test"
                    ]
                },
                {
                    "name": "Run performance tests",
                    "run": [
                        "python build_and_test.py --test-only --categories performance"
                    ]
                },
                {
                    "name": "Upload performance results",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "performance-results",
                        "path": [
                            "test_results_performance.json",
                            "benchmark_*.json"
                        ],
                        "retention-days": self.config.artifacts_retention_days
                    }
                }
            ]
        }
    
    def _generate_package_job(self) -> Dict[str, Any]:
        """Generate packaging job."""
        return {
            "name": "Create Packages",
            "needs": ["build-and-test", "coverage"],
            "if": "startsWith(github.ref, 'refs/tags/v')",
            "strategy": {
                "matrix": {
                    "os": ["ubuntu-latest", "windows-latest", "macos-latest"]
                }
            },
            "runs-on": "${{ matrix.os }}",
            "steps": [
                {
                    "name": "Checkout code",
                    "uses": "actions/checkout@v4"
                },
                {
                    "name": "Set up Python",
                    "uses": "actions/setup-python@v4",
                    "with": {
                        "python-version": "3.11"
                    }
                },
                {
                    "name": "Install dependencies and build",
                    "run": [
                        "python build_and_test.py --no-test"
                    ]
                },
                {
                    "name": "Create packages",
                    "run": [
                        "python -c \"from build_system import create_builder; builder = create_builder(); builder.package_manager.create_binary_package()\""
                    ]
                },
                {
                    "name": "Upload packages",
                    "uses": "actions/upload-artifact@v3",
                    "with": {
                        "name": "packages-${{ runner.os }}",
                        "path": "dist/*",
                        "retention-days": 90
                    }
                }
            ]
        }
    
    def _generate_deploy_job(self) -> Dict[str, Any]:
        """Generate deployment job."""
        return {
            "name": "Deploy Release",
            "needs": "package",
            "if": "startsWith(github.ref, 'refs/tags/v')",
            "runs-on": "ubuntu-latest",
            "steps": [
                {
                    "name": "Download all packages",
                    "uses": "actions/download-artifact@v3",
                    "with": {
                        "pattern": "packages-*",
                        "merge-multiple": True,
                        "path": "dist/"
                    }
                },
                {
                    "name": "Create GitHub Release",
                    "uses": "softprops/action-gh-release@v1",
                    "with": {
                        "files": "dist/*",
                        "generate_release_notes": True,
                        "draft": False,
                        "prerelease": False
                    },
                    "env": {
                        "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                    }
                }
            ]
        }
    
    def generate_dependabot_config(self) -> Path:
        """Generate Dependabot configuration for dependency updates."""
        dependabot_config = {
            "version": 2,
            "updates": [
                {
                    "package-ecosystem": "pip",
                    "directory": "/",
                    "schedule": {
                        "interval": "weekly",
                        "day": "monday"
                    },
                    "reviewers": ["@maintainers"],
                    "assignees": ["@maintainers"],
                    "commit-message": {
                        "prefix": "deps",
                        "include": "scope"
                    }
                },
                {
                    "package-ecosystem": "github-actions",
                    "directory": "/",
                    "schedule": {
                        "interval": "weekly",
                        "day": "monday"
                    },
                    "reviewers": ["@maintainers"],
                    "assignees": ["@maintainers"]
                }
            ]
        }
        
        dependabot_dir = self.project_root / ".github"
        dependabot_dir.mkdir(parents=True, exist_ok=True)
        
        dependabot_file = dependabot_dir / "dependabot.yml"
        with open(dependabot_file, 'w') as f:
            yaml.dump(dependabot_config, f, default_flow_style=False)
        
        self.logger.info(f"Generated Dependabot configuration: {dependabot_file}")
        return dependabot_file


class GitLabCIGenerator:
    """Generate GitLab CI/CD configurations."""
    
    def __init__(self, config: CIConfig, logger: BuildLogger):
        self.config = config
        self.logger = logger
        self.project_root = Path.cwd()
    
    def generate_gitlab_ci(self) -> Path:
        """Generate .gitlab-ci.yml configuration."""
        if not YAML_AVAILABLE:
            raise BuildException("PyYAML is required for CI configuration generation. Install with: pip install PyYAML")
        
        gitlab_config = {
            "stages": ["build", "test", "package", "deploy"],
            "variables": {
                "CMAKE_BUILD_TYPE": "Release",
                "BUILD_PYTHON_BINDINGS": "ON",
                **self.config.environment_variables
            },
            "cache": {
                "paths": ["build/", ".cache/pip/"]
            } if self.config.cache_enabled else {},
            **self._generate_gitlab_jobs()
        }
        
        gitlab_file = self.project_root / ".gitlab-ci.yml"
        with open(gitlab_file, 'w') as f:
            yaml.dump(gitlab_config, f, default_flow_style=False)
        
        self.logger.info(f"Generated GitLab CI configuration: {gitlab_file}")
        return gitlab_file
    
    def _generate_gitlab_jobs(self) -> Dict[str, Any]:
        """Generate GitLab CI jobs."""
        jobs = {}
        
        # Build jobs for each platform
        for platform in self.config.build_matrix.platforms:
            platform_name = platform.value
            
            if platform == BuildPlatform.LINUX:
                jobs[f"build-{platform_name}"] = {
                    "stage": "build",
                    "image": "ubuntu:latest",
                    "before_script": [
                        "apt-get update",
                        "apt-get install -y cmake build-essential python3 python3-pip",
                        "pip3 install -r requirements.txt"
                    ],
                    "script": [
                        "python3 build_and_test.py --no-test"
                    ],
                    "artifacts": {
                        "paths": ["build/", "*.so"],
                        "expire_in": "1 week"
                    }
                }
                
                jobs[f"test-{platform_name}"] = {
                    "stage": "test",
                    "image": "ubuntu:latest", 
                    "dependencies": [f"build-{platform_name}"],
                    "script": [
                        "python3 build_and_test.py --test-only --coverage"
                    ],
                    "artifacts": {
                        "reports": {
                            "coverage_report": {
                                "coverage_format": "cobertura",
                                "path": "coverage.xml"
                            }
                        },
                        "paths": ["htmlcov/", "test_results_*.json"],
                        "expire_in": "1 week"
                    },
                    "coverage": "/TOTAL.+ (\\d+%)/"
                }
        
        return jobs


def create_ci_configuration(platform: CIPlatform, project_name: str, **kwargs) -> Path:
    """Convenience function to create CI configuration."""
    logger = BuildLogger("CIGenerator")
    
    # Create default build matrix
    build_matrix = BuildMatrix(**kwargs.get('build_matrix', {}))
    
    # Create CI config
    ci_config = CIConfig(
        project_name=project_name,
        platforms=[platform],
        build_matrix=build_matrix,
        **kwargs
    )
    
    if platform == CIPlatform.GITHUB_ACTIONS:
        generator = GitHubActionsGenerator(ci_config, logger)
        return generator.generate_main_workflow()
    elif platform == CIPlatform.GITLAB_CI:
        generator = GitLabCIGenerator(ci_config, logger)
        return generator.generate_gitlab_ci()
    else:
        raise ValueError(f"Unsupported CI platform: {platform}")
