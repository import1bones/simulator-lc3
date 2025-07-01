"""
Dependency Management for LC-3 Simulator Build System
=====================================================

This module provides comprehensive dependency management for both system
and Python dependencies across different platforms.
"""

import subprocess
import sys
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .core import (
    BuildPlatform, 
    BuildLogger, 
    BuildException,
    DependencyManager,
    PlatformDetector
)


class SystemDependencyManager(DependencyManager):
    """Manager for system-level dependencies (CMake, compilers, etc.)."""
    
    def __init__(self, logger: BuildLogger, platform: BuildPlatform):
        super().__init__(logger)
        self.platform = platform
        self._dependency_map = self._get_dependency_mapping()
    
    def check_dependency(self, name: str) -> bool:
        """Check if a system dependency is available."""
        # Map generic names to platform-specific executables
        exe_name = self._dependency_map.get(name, name)
        
        try:
            result = subprocess.run(
                [exe_name, "--version"], 
                capture_output=True, 
                check=True,
                timeout=10
            )
            self.logger.debug(f"Found {name}: {result.stdout.decode().split()[0] if result.stdout else 'installed'}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def install_dependency(self, name: str, version: Optional[str] = None) -> bool:
        """Install a system dependency using the platform's package manager."""
        self.logger.info(f"Attempting to install system dependency: {name}")
        
        if self.platform == BuildPlatform.WINDOWS:
            return self._install_windows(name, version)
        elif self.platform == BuildPlatform.LINUX:
            return self._install_linux(name, version)
        elif self.platform == BuildPlatform.MACOS:
            return self._install_macos(name, version)
        else:
            self.logger.error(f"Unsupported platform for automatic dependency installation: {self.platform}")
            return False
    
    def get_dependency_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a system dependency."""
        exe_name = self._dependency_map.get(name, name)
        
        try:
            result = subprocess.run(
                [exe_name, "--version"], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=10
            )
            
            version = self._parse_version(result.stdout)
            
            return {
                "name": name,
                "executable": exe_name,
                "available": True,
                "version": version,
                "type": "system",
                "platform": self.platform.value
            }
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return {
                "name": name,
                "executable": exe_name,
                "available": False,
                "version": None,
                "type": "system",
                "platform": self.platform.value
            }
    
    def _get_dependency_mapping(self) -> Dict[str, str]:
        """Get platform-specific dependency name mapping."""
        if self.platform == BuildPlatform.WINDOWS:
            return {
                "cmake": "cmake.exe",
                "git": "git.exe",
                "compiler": "cl.exe",  # MSVC
                "python": "python.exe"
            }
        else:
            return {
                "cmake": "cmake",
                "git": "git",
                "compiler": "gcc",
                "python": "python3"
            }
    
    def _parse_version(self, version_output: str) -> str:
        """Parse version from command output."""
        lines = version_output.strip().split('\n')
        if not lines:
            return "unknown"
        
        first_line = lines[0]
        # Common patterns: "name version", "name X.Y.Z", etc.
        parts = first_line.split()
        for part in parts:
            if any(c.isdigit() for c in part) and '.' in part:
                return part
        
        return first_line
    
    def _install_windows(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on Windows."""
        installers = [
            ("choco", self._chocolatey_install),
            ("winget", self._winget_install),
            ("scoop", self._scoop_install)
        ]
        
        for installer_name, installer_func in installers:
            if self.check_dependency(installer_name):
                try:
                    return installer_func(name, version)
                except Exception as e:
                    self.logger.warning(f"Failed to install {name} with {installer_name}: {e}")
                    continue
        
        self.logger.error(f"No suitable package manager found for Windows. Please install {name} manually.")
        return False
    
    def _chocolatey_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Chocolatey."""
        cmd = ["choco", "install", name, "-y"]
        if version:
            cmd.extend(["--version", version])
        
        subprocess.run(cmd, check=True)
        return True
    
    def _winget_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Windows Package Manager."""
        cmd = ["winget", "install", name]
        if version:
            cmd.extend(["--version", version])
        
        subprocess.run(cmd, check=True)
        return True
    
    def _scoop_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Scoop."""
        cmd = ["scoop", "install", name]
        
        subprocess.run(cmd, check=True)
        return True
    
    def _install_linux(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on Linux."""
        package_managers = [
            ("apt-get", self._apt_install),
            ("yum", self._yum_install),
            ("dnf", self._dnf_install),
            ("pacman", self._pacman_install),
            ("zypper", self._zypper_install)
        ]
        
        for pm_name, pm_func in package_managers:
            if self.check_dependency(pm_name):
                try:
                    return pm_func(name, version)
                except Exception as e:
                    self.logger.warning(f"Failed to install {name} with {pm_name}: {e}")
                    continue
        
        self.logger.error(f"No suitable package manager found for Linux. Please install {name} manually.")
        return False
    
    def _apt_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using APT (Debian/Ubuntu)."""
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        
        package = f"{name}={version}" if version else name
        subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True)
        return True
    
    def _yum_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using YUM (CentOS/RHEL)."""
        package = f"{name}-{version}" if version else name
        subprocess.run(["sudo", "yum", "install", "-y", package], check=True)
        return True
    
    def _dnf_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using DNF (Fedora)."""
        package = f"{name}-{version}" if version else name
        subprocess.run(["sudo", "dnf", "install", "-y", package], check=True)
        return True
    
    def _pacman_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Pacman (Arch Linux)."""
        subprocess.run(["sudo", "pacman", "-S", "--needed", name], check=True)
        return True
    
    def _zypper_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Zypper (openSUSE)."""
        package = f"{name}={version}" if version else name
        subprocess.run(["sudo", "zypper", "install", "-y", package], check=True)
        return True
    
    def _install_macos(self, name: str, version: Optional[str] = None) -> bool:
        """Install dependency on macOS."""
        installers = [
            ("brew", self._brew_install),
            ("port", self._macports_install)
        ]
        
        for installer_name, installer_func in installers:
            if self.check_dependency(installer_name):
                try:
                    return installer_func(name, version)
                except Exception as e:
                    self.logger.warning(f"Failed to install {name} with {installer_name}: {e}")
                    continue
        
        self.logger.error(f"No suitable package manager found for macOS. Please install {name} manually.")
        return False
    
    def _brew_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using Homebrew."""
        cmd = ["brew", "install", name]
        subprocess.run(cmd, check=True)
        return True
    
    def _macports_install(self, name: str, version: Optional[str] = None) -> bool:
        """Install using MacPorts."""
        subprocess.run(["sudo", "port", "install", name], check=True)
        return True


class PythonDependencyManager(DependencyManager):
    """Manager for Python package dependencies."""
    
    def __init__(self, logger: BuildLogger, python_exe: Optional[str] = None):
        super().__init__(logger)
        
        if python_exe is None:
            try:
                self.python_exe = PlatformDetector.get_python_executable()
            except BuildException:
                self.logger.error("No suitable Python executable found")
                raise
        else:
            self.python_exe = python_exe
    
    def check_dependency(self, name: str) -> bool:
        """Check if a Python package is available."""
        try:
            subprocess.run(
                [self.python_exe, "-c", f"import {name}"],
                capture_output=True,
                check=True,
                timeout=10
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    def install_dependency(self, name: str, version: Optional[str] = None) -> bool:
        """Install a Python package using pip."""
        try:
            package = f"{name}=={version}" if version else name
            self.logger.info(f"Installing Python package: {package}")
            
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", package],
                check=True,
                timeout=300  # 5 minutes timeout for installation
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Failed to install {package}: {e}")
            return False
    
    def install_requirements_file(self, requirements_file: Path) -> bool:
        """Install packages from a requirements file."""
        if not requirements_file.exists():
            self.logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        try:
            self.logger.info(f"Installing from requirements file: {requirements_file}")
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                timeout=600  # 10 minutes timeout
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"Failed to install from {requirements_file}: {e}")
            return False
    
    def get_dependency_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a Python package."""
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "show", name],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            info = {
                "name": name,
                "available": True,
                "type": "python",
                "python_executable": self.python_exe
            }
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace('-', '_')
                    value = value.strip()
                    
                    if key == "version":
                        info["version"] = value
                    elif key == "location":
                        info["location"] = value
                    elif key == "requires":
                        info["dependencies"] = [dep.strip() for dep in value.split(',') if dep.strip()]
            
            return info
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return {
                "name": name,
                "available": False,
                "version": None,
                "type": "python",
                "python_executable": self.python_exe
            }
    
    def list_installed_packages(self) -> List[Dict[str, str]]:
        """List all installed Python packages."""
        try:
            result = subprocess.run(
                [self.python_exe, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            import json
            packages = json.loads(result.stdout)
            return packages
            
        except Exception as e:
            self.logger.error(f"Failed to list packages: {e}")
            return []


class DependencyResolver:
    """High-level dependency resolver that coordinates system and Python dependencies."""
    
    def __init__(self, platform: BuildPlatform, logger: BuildLogger):
        self.platform = platform
        self.logger = logger
        
        self.system_manager = SystemDependencyManager(logger, platform)
        
        try:
            self.python_manager = PythonDependencyManager(logger)
        except BuildException:
            self.python_manager = None
            self.logger.warning("Python dependency manager not available")
    
    def resolve_all_dependencies(self, requirements_file: Optional[Path] = None) -> bool:
        """Resolve all required dependencies for the LC-3 simulator."""
        self.logger.info("Resolving all dependencies...")
        
        success = True
        
        # System dependencies
        if not self._resolve_system_dependencies():
            success = False
        
        # Python dependencies
        if self.python_manager and not self._resolve_python_dependencies(requirements_file):
            success = False
        
        return success
    
    def _resolve_system_dependencies(self) -> bool:
        """Resolve system dependencies."""
        required_deps = ["cmake", "git"]
        
        # Platform-specific dependencies
        if self.platform == BuildPlatform.WINDOWS:
            # Visual Studio Build Tools should be installed manually
            pass
        else:
            required_deps.append("compiler")
        
        missing_deps = []
        for dep in required_deps:
            if not self.system_manager.check_dependency(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            self.logger.warning(f"Missing system dependencies: {missing_deps}")
            # For now, just warn - automatic installation can be risky
            return True
        
        self.logger.info("All system dependencies satisfied")
        return True
    
    def _resolve_python_dependencies(self, requirements_file: Optional[Path] = None) -> bool:
        """Resolve Python dependencies."""
        if not self.python_manager:
            return False
        
        # Install from requirements file if provided
        if requirements_file:
            return self.python_manager.install_requirements_file(requirements_file)
        
        # Default required packages
        required_packages = [
            ("pytest", "7.0.0"),
            ("pytest-cov", "4.0.0"),
            ("pytest-html", "3.0.0"),
            ("pytest-xdist", "3.0.0"),
            ("pytest-benchmark", "4.0.0"),
            ("pybind11", "2.10.0"),
            ("numpy", "1.20.0")
        ]
        
        for package, min_version in required_packages:
            if not self.python_manager.check_dependency(package):
                self.logger.info(f"Installing {package}>={min_version}")
                if not self.python_manager.install_dependency(package, f">={min_version}"):
                    self.logger.error(f"Failed to install {package}")
                    return False
        
        return True
    
    def generate_dependency_report(self) -> Dict[str, Any]:
        """Generate a comprehensive dependency report."""
        report = {
            "platform": self.platform.value,
            "timestamp": str(__import__("datetime").datetime.now()),
            "system_dependencies": [],
            "python_dependencies": []
        }
        
        # System dependencies
        system_deps = ["cmake", "git", "compiler", "python"]
        for dep in system_deps:
            report["system_dependencies"].append(
                self.system_manager.get_dependency_info(dep)
            )
        
        # Python dependencies  
        if self.python_manager:
            python_deps = ["pytest", "pybind11", "numpy", "pytest-cov"]
            for dep in python_deps:
                report["python_dependencies"].append(
                    self.python_manager.get_dependency_info(dep)
                )
        
        return report
