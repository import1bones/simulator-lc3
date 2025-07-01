"""
Multi-Platform Build Architecture for LC-3 Simulator
====================================================

This module provides a comprehensive build system that supports:
- Cross-platform development (Windows, Linux, macOS)
- Multiple build configurations (Debug, Release, RelWithDebInfo)
- Dependency management
- Test execution
- Package generation
- CI/CD integration
"""

import os
import sys
import platform
import subprocess
import json
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum


class BuildPlatform(Enum):
    """Supported build platforms."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"
    UNKNOWN = "unknown"


class BuildType(Enum):
    """Build configuration types."""
    DEBUG = "Debug"
    RELEASE = "Release"
    RELWITHDEBINFO = "RelWithDebInfo"
    MINSIZEREL = "MinSizeRel"


class Architecture(Enum):
    """Target architectures."""
    X86_64 = "x86_64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM = "arm"


@dataclass
class BuildConfiguration:
    """Build configuration settings."""
    platform: BuildPlatform
    architecture: Architecture
    build_type: BuildType
    generator: Optional[str] = None
    toolchain: Optional[str] = None
    cmake_args: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default generator based on platform."""
        if self.generator is None:
            if self.platform == BuildPlatform.WINDOWS:
                self.generator = "Visual Studio 17 2022"
            else:
                self.generator = "Unix Makefiles"


@dataclass
class ProjectSettings:
    """Project-specific settings."""
    name: str = "LC3Simulator"
    version: str = "1.0.0"
    description: str = "LC-3 Computer Architecture Simulator"
    languages: List[str] = field(default_factory=lambda: ["C", "CXX"])
    cmake_min_version: str = "3.12"
    python_min_version: str = "3.8"
    
    # Feature flags
    build_python_bindings: bool = True
    build_tests: bool = True
    build_documentation: bool = False
    enable_coverage: bool = False
    enable_sanitizers: bool = False


class BuildLogger:
    """Centralized logging for build system."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, msg: str) -> None:
        self.logger.debug(msg)
    
    def info(self, msg: str) -> None:
        self.logger.info(msg)
    
    def warning(self, msg: str) -> None:
        self.logger.warning(msg)
    
    def error(self, msg: str) -> None:
        self.logger.error(msg)
    
    def critical(self, msg: str) -> None:
        self.logger.critical(msg)


class BuildException(Exception):
    """Custom exception for build system errors."""
    pass


class PlatformDetector:
    """Utility class for detecting platform information."""
    
    @staticmethod
    def get_platform() -> BuildPlatform:
        """Detect the current platform."""
        system = platform.system().lower()
        if system == "windows":
            return BuildPlatform.WINDOWS
        elif system == "linux":
            return BuildPlatform.LINUX
        elif system == "darwin":
            return BuildPlatform.MACOS
        else:
            return BuildPlatform.UNKNOWN
    
    @staticmethod
    def get_architecture() -> Architecture:
        """Detect the current architecture."""
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            return Architecture.X86_64
        elif machine in ["i386", "i686", "x86"]:
            return Architecture.X86
        elif machine in ["arm64", "aarch64"]:
            return Architecture.ARM64
        elif machine.startswith("arm"):
            return Architecture.ARM
        else:
            return Architecture.X86_64  # Default fallback
    
    @staticmethod
    def get_python_executable() -> str:
        """Find the best Python executable."""
        candidates = ["python3", "python", "python3.11", "python3.10", "python3.9"]
        
        for candidate in candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                version = result.stdout.strip()
                if "Python 3." in version:
                    return candidate
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise BuildException("Python 3.x not found")


class DependencyManager(ABC):
    """Abstract base class for managing dependencies."""
    
    def __init__(self, logger: BuildLogger):
        self.logger = logger
    
    @abstractmethod
    def check_dependency(self, name: str) -> bool:
        """Check if a dependency is available."""
        pass
    
    @abstractmethod
    def install_dependency(self, name: str, version: Optional[str] = None) -> bool:
        """Install a dependency."""
        pass
    
    @abstractmethod
    def get_dependency_info(self, name: str) -> Dict[str, Any]:
        """Get information about a dependency."""
        pass


class SystemDependencyManager(DependencyManager):
    """Manager for system-level dependencies."""
    
    def __init__(self, logger: BuildLogger, platform: BuildPlatform):
        super().__init__(logger)
        self.platform = platform
    
    def check_dependency(self, name: str) -> bool:
        """Check if a system dependency is available."""
        try:
            subprocess.run([name, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_dependency(self, name: str, version: Optional[str] = None) -> bool:
        """Install a system dependency using the platform's package manager."""
        if self.platform == BuildPlatform.WINDOWS:
            return self._install_windows(name, version)
        elif self.platform == BuildPlatform.LINUX:
            return self._install_linux(name, version)
        elif self.platform == BuildPlatform.MACOS:
            return self._install_macos(name, version)
        else:
            return False
    
    def get_dependency_info(self, name: str) -> Dict[str, Any]:
        """Get information about a system dependency."""
        try:
            result = subprocess.run(
                [name, "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return {
                "name": name,
                "available": True,
                "version": result.stdout.strip(),
                "type": "system"
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "name": name,
                "available": False,
                "version": None,
                "type": "system"
            }
    
    def _install_windows(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on Windows using chocolatey."""
        if not self.check_dependency("choco"):
            self.logger.warning("Chocolatey not found. Please install dependencies manually.")
            return False
        
        try:
            cmd = ["choco", "install", name, "-y"]
            if version:
                cmd.extend(["--version", version])
            
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_linux(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on Linux using appropriate package manager."""
        package_managers = [
            ("apt-get", ["sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y"]),
            ("yum", ["sudo", "yum", "install", "-y"]),
            ("dnf", ["sudo", "dnf", "install", "-y"]),
            ("pacman", ["sudo", "pacman", "-S", "--needed"])
        ]
        
        for pm_name, pm_cmd in package_managers:
            if self.check_dependency(pm_name):
                try:
                    cmd = pm_cmd + [name]
                    subprocess.run(cmd, check=True, shell=True)
                    return True
                except subprocess.CalledProcessError:
                    continue
        
        return False
    
    def _install_macos(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on macOS using homebrew."""
        if not self.check_dependency("brew"):
            self.logger.warning("Homebrew not found. Please install dependencies manually.")
            return False
        
        try:
            cmd = ["brew", "install", name]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False


class PythonDependencyManager(DependencyManager):
    """Manager for Python dependencies."""
    
    def __init__(self, logger: BuildLogger, python_exe: str):
        super().__init__(logger)
        self.python_exe = python_exe
    
    def check_dependency(self, name: str) -> bool:
        """Check if a Python package is available."""
        try:
            subprocess.run(
                [self.python_exe, "-c", f"import {name}"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install_dependency(self, name: str, version: Optional[str] = None) -> bool:
        """Install a Python package using pip."""
        try:
            package = f"{name}=={version}" if version else name
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", package],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_dependency_info(self, name: str) -> Dict[str, Any]:
        """Get information about a Python package."""
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", name],
                capture_output=True,
                text=True,
                check=True
            )
            
            info = {"name": name, "available": True, "type": "python"}
            for line in result.stdout.split('\n'):
                if line.startswith("Version:"):
                    info["version"] = line.split(":", 1)[1].strip()
                    break
            
            return info
        except subprocess.CalledProcessError:
            return {
                "name": name,
                "available": False,
                "version": None,
                "type": "python"
            }


class BuildEnvironment:
    """Manages the build environment and dependencies."""
    
    def __init__(self, config: BuildConfiguration, settings: ProjectSettings):
        self.config = config
        self.settings = settings
        self.logger = BuildLogger("BuildEnvironment")
        
        # Initialize dependency managers
        self.system_deps = SystemDependencyManager(self.logger, config.platform)
        
        try:
            python_exe = PlatformDetector.get_python_executable()
            self.python_deps = PythonDependencyManager(self.logger, python_exe)
        except BuildException as e:
            self.logger.error(f"Failed to initialize Python dependency manager: {e}")
            self.python_deps = None
    
    def setup_environment(self) -> bool:
        """Set up the complete build environment."""
        self.logger.info("Setting up build environment...")
        
        # Check system dependencies
        if not self._check_system_dependencies():
            return False
        
        # Set up Python environment
        if not self._setup_python_environment():
            return False
        
        # Set environment variables
        self._set_environment_variables()
        
        self.logger.info("Build environment setup complete")
        return True
    
    def _check_system_dependencies(self) -> bool:
        """Check and install system dependencies."""
        required_deps = ["cmake", "git"]
        
        if self.config.platform == BuildPlatform.WINDOWS:
            # Visual Studio Build Tools are required for Windows
            pass  # Usually handled by installer
        else:
            required_deps.extend(["gcc", "make"])
        
        missing_deps = []
        for dep in required_deps:
            if not self.system_deps.check_dependency(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            self.logger.warning(f"Missing system dependencies: {missing_deps}")
            return True  # Don't fail, just warn
        
        return True
    
    def _setup_python_environment(self) -> bool:
        """Set up Python environment and dependencies."""
        if not self.python_deps:
            return False
        
        required_packages = [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "pytest-html>=3.0.0",
            "pytest-xdist>=2.0.0",
            "pytest-benchmark>=3.4.0",
            "pybind11>=2.6.0",
            "numpy>=1.19.0"
        ]
        
        for package in required_packages:
            if ">" in package:
                name = package.split(">=")[0].split("==")[0]
                version = package.split(">=")[1] if ">=" in package else None
            else:
                name = package
                version = None
            
            if not self.python_deps.check_dependency(name):
                self.logger.info(f"Installing Python package: {package}")
                if not self.python_deps.install_dependency(name, version):
                    self.logger.warning(f"Failed to install {package}")
        
        return True
    
    def _set_environment_variables(self) -> None:
        """Set required environment variables."""
        for key, value in self.config.env_vars.items():
            os.environ[key] = value
            self.logger.debug(f"Set environment variable: {key}={value}")
    
    def get_dependency_report(self) -> Dict[str, Any]:
        """Generate a report of all dependencies."""
        report = {
            "system_dependencies": [],
            "python_dependencies": []
        }
        
        # System dependencies
        system_deps = ["cmake", "git", "gcc", "make"]
        for dep in system_deps:
            report["system_dependencies"].append(
                self.system_deps.get_dependency_info(dep)
            )
        
        # Python dependencies
        if self.python_deps:
            python_deps = ["pytest", "pybind11", "numpy"]
            for dep in python_deps:
                report["python_dependencies"].append(
                    self.python_deps.get_dependency_info(dep)
                )
        
        return report
