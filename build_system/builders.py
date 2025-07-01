"""
Build System Builders for LC-3 Simulator
=========================================

This module provides specialized builders for different components
of the LC-3 simulator build process.
"""

import os
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from .core import (
    BuildConfiguration,
    ProjectSettings,
    BuildLogger,
    BuildException,
    BuildPlatform,
    BuildType
)
from .dependencies import DependencyResolver


class BaseBuilder(ABC):
    """Abstract base class for all builders."""
    
    def __init__(self, config: BuildConfiguration, project: ProjectSettings, logger: BuildLogger):
        self.config = config
        self.project = project
        self.logger = logger
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "build"
    
    @abstractmethod
    def configure(self) -> bool:
        """Configure the build."""
        pass
    
    @abstractmethod
    def build(self) -> bool:
        """Execute the build."""
        pass
    
    @abstractmethod
    def clean(self) -> bool:
        """Clean build artifacts."""
        pass
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = False, timeout: int = 300) -> Any:
        """Run a command with proper error handling and logging."""
        cmd_str = " ".join(str(arg) for arg in cmd)
        self.logger.debug(f"Running command: {cmd_str}")
        
        if cwd is None:
            cwd = self.project_root
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            if capture_output:
                return result.stdout.strip()
            else:
                return True
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {cmd_str}")
            if capture_output and e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if capture_output and e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            raise BuildException(f"Command failed: {cmd_str}") from e
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {cmd_str}")
            raise BuildException(f"Command timed out: {cmd_str}")


class CMakeBuilder(BaseBuilder):
    """Builder for CMake-based C++ projects."""
    
    def __init__(self, config: BuildConfiguration, project: ProjectSettings, logger: BuildLogger):
        super().__init__(config, project, logger)
        self.cmake_cache_file = self.build_dir / "CMakeCache.txt"
    
    def configure(self) -> bool:
        """Configure CMake build."""
        self.logger.info("Configuring CMake build...")
        
        # Create build directory
        self.build_dir.mkdir(exist_ok=True)
        
        # Prepare CMake arguments
        cmake_args = [
            "cmake",
            "-S", str(self.project_root),
            "-B", str(self.build_dir),
            f"-DCMAKE_BUILD_TYPE={self.config.build_type.value}"
        ]
        
        # Add generator if specified
        if self.config.generator:
            cmake_args.extend(["-G", self.config.generator])
        
        # Add platform for Visual Studio
        if (self.config.platform == BuildPlatform.WINDOWS and 
            "Visual Studio" in self.config.generator):
            cmake_args.extend(["-A", "x64"])
        
        # Project-specific options
        if self.project.build_python_bindings:
            cmake_args.append("-DBUILD_PYTHON_BINDINGS=ON")
        
        if self.project.build_tests:
            cmake_args.append("-DBUILD_TESTING=ON")
        
        if self.project.enable_coverage:
            cmake_args.append("-DENABLE_COVERAGE=ON")
        
        # Add custom CMake arguments
        cmake_args.extend(self.config.cmake_args)
        
        try:
            self.run_command(cmake_args)
            self.logger.info("CMake configuration completed successfully")
            return True
        except BuildException as e:
            # Check if this is a compiler not found error
            error_msg = str(e).lower()
            if "cmake_c_compiler not set" in error_msg or "cmake_cxx_compiler not set" in error_msg:
                self.logger.error("CMake configuration failed: C++ compiler not found")
                self._suggest_compiler_installation()
            else:
                self.logger.error("CMake configuration failed")
            return False
    
    def _suggest_compiler_installation(self):
        """Suggest how to install a C++ compiler based on the platform."""
        from .core import BuildPlatform
        
        if self.config.platform == BuildPlatform.WINDOWS:
            self.logger.info("To fix this issue, install one of the following:")
            self.logger.info("1. Visual Studio Community (recommended): https://visualstudio.microsoft.com/vs/community/")
            self.logger.info("2. Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
            self.logger.info("3. MinGW-w64: https://www.mingw-w64.org/downloads/")
            self.logger.info("4. MSYS2 (includes MinGW): https://www.msys2.org/")
        elif self.config.platform == BuildPlatform.LINUX:
            self.logger.info("To fix this issue, install build tools:")
            self.logger.info("Ubuntu/Debian: sudo apt install build-essential")
            self.logger.info("CentOS/RHEL: sudo yum groupinstall 'Development Tools'")
            self.logger.info("Fedora: sudo dnf groupinstall 'Development Tools'")
        elif self.config.platform == BuildPlatform.MACOS:
            self.logger.info("To fix this issue, install Xcode Command Line Tools:")
            self.logger.info("xcode-select --install")
    
    def build(self) -> bool:
        """Build the CMake project."""
        self.logger.info("Building CMake project...")
        
        if not self.cmake_cache_file.exists():
            self.logger.error("CMake not configured. Run configure() first.")
            return False
        
        # Prepare build command
        build_args = [
            "cmake",
            "--build", str(self.build_dir),
            "--config", self.config.build_type.value
        ]
        
        # Add parallel build flag
        if self.config.platform != BuildPlatform.WINDOWS:
            # For Unix makefiles
            build_args.extend(["-j", "4"])
        else:
            # For Visual Studio
            build_args.extend(["/m:4"])
        
        try:
            self.run_command(build_args, timeout=600)  # 10 minutes timeout
            self.logger.info("CMake build completed successfully")
            return True
        except BuildException:
            self.logger.error("CMake build failed")
            return False
    
    def clean(self) -> bool:
        """Clean CMake build artifacts."""
        self.logger.info("Cleaning CMake build...")
        
        if self.build_dir.exists():
            try:
                shutil.rmtree(self.build_dir)
                self.logger.info("Build directory cleaned")
                return True
            except OSError as e:
                self.logger.error(f"Failed to clean build directory: {e}")
                return False
        
        return True
    
    def install(self, install_dir: Optional[Path] = None) -> bool:
        """Install the built project."""
        self.logger.info("Installing CMake project...")
        
        install_args = ["cmake", "--install", str(self.build_dir)]
        
        if install_dir:
            install_args.extend(["--prefix", str(install_dir)])
        
        try:
            self.run_command(install_args)
            self.logger.info("Installation completed successfully")
            return True
        except BuildException:
            self.logger.error("Installation failed")
            return False
    
    def get_build_info(self) -> Dict[str, Any]:
        """Get information about the CMake build."""
        info = {
            "configured": self.cmake_cache_file.exists(),
            "build_type": self.config.build_type.value,
            "generator": self.config.generator,
            "platform": self.config.platform.value,
            "build_dir": str(self.build_dir)
        }
        
        if self.cmake_cache_file.exists():
            # Read some info from CMake cache
            try:
                with open(self.cmake_cache_file, 'r') as f:
                    cache_content = f.read()
                    
                # Extract compiler info
                for line in cache_content.split('\n'):
                    if 'CMAKE_CXX_COMPILER:' in line and '=' in line:
                        info['cxx_compiler'] = line.split('=', 1)[1]
                    elif 'CMAKE_C_COMPILER:' in line and '=' in line:
                        info['c_compiler'] = line.split('=', 1)[1]
            except Exception:
                pass
        
        return info


class PythonBuilder(BaseBuilder):
    """Builder for Python components (bindings, tests, etc.)."""
    
    def __init__(self, config: BuildConfiguration, project: ProjectSettings, logger: BuildLogger):
        super().__init__(config, project, logger)
        self.python_exe = self._find_python_executable()
        self.pybind_build_dir = self.build_dir / "python_bindings"
    
    def _find_python_executable(self) -> str:
        """Find the appropriate Python executable."""
        from .core import PlatformDetector
        try:
            return PlatformDetector.get_python_executable()
        except BuildException:
            return "python"
    
    def configure(self) -> bool:
        """Configure Python build environment."""
        self.logger.info("Configuring Python build environment...")
        
        # Verify Python version
        try:
            version_output = self.run_command(
                [self.python_exe, "--version"], 
                capture_output=True
            )
            self.logger.info(f"Using Python: {version_output}")
        except BuildException:
            self.logger.error("Failed to get Python version")
            return False
        
        # Check if pybind11 is available
        try:
            self.run_command(
                [self.python_exe, "-c", "import pybind11; print(pybind11.__version__)"],
                capture_output=True
            )
        except BuildException:
            self.logger.error("pybind11 not found. Install it with: pip install pybind11")
            return False
        
        return True
    
    def build(self) -> bool:
        """Build Python components."""
        self.logger.info("Building Python components...")
        
        if not self.project.build_python_bindings:
            self.logger.info("Python bindings disabled, skipping...")
            return True
        
        # Build Python bindings using CMake
        return self._build_python_bindings()
    
    def _build_python_bindings(self) -> bool:
        """Build Python bindings specifically."""
        self.logger.info("Building Python bindings...")
        
        # The bindings are built as part of the CMake build
        # We just need to ensure they're available in the right location
        
        # Find the built Python module
        built_modules = []
        if self.build_dir.exists():
            # Look for .pyd files (Windows) or .so files (Unix)
            patterns = ["*.pyd", "*.so"]
            for pattern in patterns:
                built_modules.extend(self.build_dir.rglob(pattern))
        
        if not built_modules:
            self.logger.error("No Python modules found after build")
            return False
        
        # Copy to project root for easy import
        for module in built_modules:
            if "lc3_simulator" in module.name:
                dest = self.project_root / module.name
                try:
                    shutil.copy2(module, dest)
                    self.logger.info(f"Copied Python module: {module.name}")
                except OSError as e:
                    self.logger.warning(f"Failed to copy {module.name}: {e}")
        
        return True
    
    def clean(self) -> bool:
        """Clean Python build artifacts."""
        self.logger.info("Cleaning Python build artifacts...")
        
        # Remove built modules from project root
        patterns = ["*.pyd", "*.so"]
        for pattern in patterns:
            for file in self.project_root.glob(pattern):
                if "lc3_simulator" in file.name:
                    try:
                        file.unlink()
                        self.logger.debug(f"Removed: {file}")
                    except OSError:
                        pass
        
        # Remove __pycache__ directories
        for pycache in self.project_root.rglob("__pycache__"):
            try:
                shutil.rmtree(pycache)
            except OSError:
                pass
        
        return True
    
    def test_import(self) -> bool:
        """Test if the Python module can be imported."""
        self.logger.info("Testing Python module import...")
        
        try:
            self.run_command(
                [self.python_exe, "-c", "import lc3_simulator; print('Import successful')"],
                capture_output=True
            )
            self.logger.info("Python module import test successful")
            return True
        except BuildException:
            self.logger.error("Failed to import Python module")
            return False


class LC3Builder(BaseBuilder):
    """High-level builder that orchestrates the complete LC-3 simulator build."""
    
    def __init__(self, config: BuildConfiguration, project: ProjectSettings, logger: BuildLogger):
        super().__init__(config, project, logger)
        
        self.cmake_builder = CMakeBuilder(config, project, logger)
        self.python_builder = PythonBuilder(config, project, logger)
        self.dependency_resolver = DependencyResolver(config.platform, logger)
    
    def configure(self) -> bool:
        """Configure the complete LC-3 build."""
        self.logger.info("Configuring LC-3 simulator build...")
        
        # Resolve dependencies
        requirements_file = self.project_root / "requirements.txt"
        if not self.dependency_resolver.resolve_all_dependencies(
            requirements_file if requirements_file.exists() else None
        ):
            self.logger.warning("Some dependencies could not be resolved")
        
        # Configure CMake
        if not self.cmake_builder.configure():
            return False
        
        # Configure Python environment
        if self.project.build_python_bindings:
            if not self.python_builder.configure():
                return False
        
        self.logger.info("LC-3 simulator configuration completed")
        return True
    
    def build(self) -> bool:
        """Build the complete LC-3 simulator."""
        self.logger.info("Building LC-3 simulator...")
        
        # Build C++ components with CMake
        if not self.cmake_builder.build():
            return False
        
        # Build Python components
        if self.project.build_python_bindings:
            if not self.python_builder.build():
                return False
            
            # Test Python module import
            if not self.python_builder.test_import():
                self.logger.warning("Python module import test failed")
        
        self.logger.info("LC-3 simulator build completed successfully")
        return True
    
    def clean(self) -> bool:
        """Clean all build artifacts."""
        self.logger.info("Cleaning LC-3 simulator build artifacts...")
        
        success = True
        
        if not self.cmake_builder.clean():
            success = False
        
        if not self.python_builder.clean():
            success = False
        
        if success:
            self.logger.info("Clean completed successfully")
        else:
            self.logger.warning("Some clean operations failed")
        
        return success
    
    def full_build(self, clean_first: bool = True) -> bool:
        """Perform a complete build from scratch."""
        self.logger.info("Starting full LC-3 simulator build...")
        
        if clean_first:
            self.clean()
        
        if not self.configure():
            return False
        
        if not self.build():
            return False
        
        self.logger.info("Full build completed successfully")
        return True
    
    def generate_build_report(self) -> Dict[str, Any]:
        """Generate a comprehensive build report."""
        report = {
            "project": {
                "name": self.project.name,
                "version": self.project.version,
                "description": self.project.description
            },
            "configuration": {
                "platform": self.config.platform.value,
                "architecture": self.config.architecture.value,
                "build_type": self.config.build_type.value,
                "generator": self.config.generator
            },
            "features": {
                "python_bindings": self.project.build_python_bindings,
                "tests": self.project.build_tests,
                "documentation": self.project.build_documentation,
                "coverage": self.project.enable_coverage
            },
            "cmake_info": self.cmake_builder.get_build_info(),
            "dependencies": self.dependency_resolver.generate_dependency_report(),
            "timestamp": str(__import__("datetime").datetime.now())
        }
        
        return report
    
    def save_build_report(self, output_file: Optional[Path] = None) -> bool:
        """Save build report to a file."""
        if output_file is None:
            output_file = self.project_root / "build_report.json"
        
        try:
            report = self.generate_build_report()
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Build report saved to: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save build report: {e}")
            return False
