#!/usr/bin/env python3
"""
Cross-platform build and test script for LC-3 Simulator
Supports Windows, Linux, and macOS

This script provides backward compatibility while migrating to the new
modular build system. It will delegate to the new system when available.
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
import json
from pathlib import Path
import tempfile

# Try to use the new build system if available
try:
    from build_system import create_builder, BuildLogger
    NEW_BUILD_SYSTEM_AVAILABLE = True
except ImportError:
    NEW_BUILD_SYSTEM_AVAILABLE = False


class CrossPlatformBuilder:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.build_dir = self.project_root / "build"
        self.is_windows = self.platform == "windows"
        self.is_linux = self.platform == "linux"
        self.is_macos = self.platform == "darwin"
        
        # Use new build system if available
        if NEW_BUILD_SYSTEM_AVAILABLE:
            self.logger = BuildLogger("CrossPlatformBuilder")
            self.new_builder = create_builder(logger=self.logger)
            self.logger.info("Using new modular build system")
        else:
            self.new_builder = None
        
        # Platform-specific configurations
        self.config = self._get_platform_config()
        
    def _get_platform_config(self):
        """Get platform-specific build configuration."""
        config = {
            "cmake_generator": None,
            "cmake_config": "Debug",
            "python_exe": sys.executable,
            "build_parallel": "4",
            "lib_extension": ".so",
            "exe_extension": "",
        }
        
        if self.is_windows:
            config.update({
                "cmake_generator": "Visual Studio 17 2022",
                "cmake_platform": "x64",
                "lib_extension": ".dll",
                "exe_extension": ".exe",
                "pyd_pattern": "*.cp*-win_amd64.pyd"
            })
        elif self.is_linux:
            config.update({
                "cmake_generator": "Unix Makefiles",
                "lib_extension": ".so",
                "pyd_pattern": "*.cpython-*-linux-*.so"
            })
        elif self.is_macos:
            config.update({
                "cmake_generator": "Unix Makefiles",
                "lib_extension": ".dylib",
                "pyd_pattern": "*.cpython-*-darwin.so"
            })
        
        return config
    
    def log(self, message, level="INFO"):
        """Log a message with timestamp."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd, cwd=None, check=True, capture_output=False):
        """Run a command with proper error handling."""
        if isinstance(cmd, list):
            cmd_str = " ".join(cmd)
        else:
            cmd_str = cmd
            
        self.log(f"Running: {cmd_str}")
        
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, cwd=cwd, check=check, shell=True,
                    capture_output=True, text=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(cmd, cwd=cwd, check=check, shell=True)
                return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if capture_output and e.stdout:
                self.log(f"STDOUT: {e.stdout}", "ERROR")
            if capture_output and e.stderr:
                self.log(f"STDERR: {e.stderr}", "ERROR")
            raise
    
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        self.log("Checking dependencies...")
        
        dependencies = {
            "cmake": ["cmake", "--version"],
            "python": [self.config["python_exe"], "--version"],
            "git": ["git", "--version"]
        }
        
        missing = []
        for dep, cmd in dependencies.items():
            try:
                version = self.run_command(cmd, capture_output=True)
                self.log(f"{dep}: {version.split()[2] if len(version.split()) > 2 else 'installed'}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(dep)
                self.log(f"{dep}: NOT FOUND", "ERROR")
        
        if missing:
            self.log(f"Missing dependencies: {', '.join(missing)}", "ERROR")
            return False
        
        # Check Python packages
        python_deps = ["pytest", "pybind11"]
        for dep in python_deps:
            try:
                self.run_command([self.config["python_exe"], "-c", f"import {dep}"], capture_output=True)
                self.log(f"Python package {dep}: installed")
            except subprocess.CalledProcessError:
                self.log(f"Python package {dep}: NOT FOUND - installing...", "WARN")
                self.install_python_dependencies()
                break
        
        return True
    
    def install_python_dependencies(self):
        """Install required Python dependencies."""
        self.log("Installing Python dependencies...")
        
        requirements = [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "pytest-html>=3.0.0",
            "pytest-xdist>=2.0.0",
            "pytest-benchmark>=3.4.0",
            "pybind11>=2.6.0",
            "numpy>=1.19.0"
        ]
        
        for req in requirements:
            try:
                self.run_command([self.config["python_exe"], "-m", "pip", "install", req])
            except subprocess.CalledProcessError:
                self.log(f"Failed to install {req}", "ERROR")
                raise
    
    def clean_build(self):
        """Clean the build directory."""
        self.log("Cleaning build directory...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)
    
    def configure_cmake(self, build_python_bindings=True, build_type="Debug"):
        """Configure CMake with appropriate settings."""
        self.log(f"Configuring CMake for {self.platform}...")
        
        cmake_cmd = [
            "cmake",
            "-S", str(self.project_root),
            "-B", str(self.build_dir),
            f"-DCMAKE_BUILD_TYPE={build_type}"
        ]
        
        if build_python_bindings:
            cmake_cmd.append("-DBUILD_PYTHON_BINDINGS=ON")
        
        # Platform-specific generator
        if self.config["cmake_generator"]:
            cmake_cmd.extend(["-G", self.config["cmake_generator"]])
        
        if self.is_windows and "cmake_platform" in self.config:
            cmake_cmd.extend(["-A", self.config["cmake_platform"]])
        
        self.run_command(cmake_cmd)
    
    def build_project(self, target=None, parallel=True):
        """Build the project."""
        self.log("Building project...")
        
        cmake_cmd = [
            "cmake", "--build", str(self.build_dir),
            "--config", self.config["cmake_config"]
        ]
        
        if target:
            cmake_cmd.extend(["--target", target])
        
        if parallel:
            cmake_cmd.extend(["-j", self.config["build_parallel"]])
        
        self.run_command(cmake_cmd)
    
    def find_python_module(self):
        """Find the built Python module."""
        self.log("Locating Python module...")
        
        search_patterns = [
            self.config["pyd_pattern"],
            "lc3_simulator*.so",
            "lc3_simulator*.dll",
            "lc3_simulator*.pyd"
        ]
        
        for pattern in search_patterns:
            files = list(self.build_dir.rglob(pattern))
            if files:
                return files[0]
        
        self.log("Python module not found", "ERROR")
        return None
    
    def install_python_module(self):
        """Install/copy the Python module to the project root."""
        module_file = self.find_python_module()
        if not module_file:
            return False
        
        # Copy to project root with standard name
        dest = self.project_root / "lc3_simulator.pyd" if self.is_windows else self.project_root / "lc3_simulator.so"
        shutil.copy2(module_file, dest)
        self.log(f"Python module copied to {dest}")
        return True
    
    def run_tests(self, test_categories=None, coverage=False, html_report=False, parallel=False, verbose=False):
        """Run the test suite."""
        self.log("Running tests...")
        
        # Ensure we can import the module
        test_import_cmd = [
            self.config["python_exe"], "-c",
            "import lc3_simulator; print('Module import successful')"
        ]
        
        try:
            self.run_command(test_import_cmd, cwd=self.project_root)
        except subprocess.CalledProcessError:
            self.log("Failed to import lc3_simulator module", "ERROR")
            return False
        
        # Build pytest command
        pytest_cmd = [self.config["python_exe"], "-m", "pytest", "tests/"]
        
        if verbose:
            pytest_cmd.append("-v")
        
        if coverage:
            pytest_cmd.extend(["--cov=lc3_simulator", "--cov-report=term-missing"])
            if html_report:
                pytest_cmd.append("--cov-report=html:reports/coverage")
        
        if html_report:
            pytest_cmd.extend(["--html=reports/test_report.html", "--self-contained-html"])
        
        if parallel:
            pytest_cmd.extend(["-n", "auto"])
        
        # Add test categories
        if test_categories:
            if isinstance(test_categories, str):
                test_categories = [test_categories]
            
            category_map = {
                "basic": "tests/test_basic.py",
                "instructions": "tests/test_instructions.py", 
                "memory": "tests/test_memory.py",
                "io": "tests/test_io.py",
                "integration": "tests/test_integration.py",
                "pipeline": "tests/test_pipeline.py"
            }
            
            test_files = []
            for category in test_categories:
                if category in category_map:
                    test_files.append(category_map[category])
                else:
                    test_files.append(category)
            
            pytest_cmd = [self.config["python_exe"], "-m", "pytest"] + test_files
            if verbose:
                pytest_cmd.append("-v")
        
        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        try:
            self.run_command(pytest_cmd, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError:
            self.log("Some tests failed", "WARN")
            return False
    
    def generate_build_info(self):
        """Generate build information file."""
        self.log("Generating build information...")
        
        build_info = {
            "platform": self.platform,
            "architecture": self.architecture,
            "python_version": platform.python_version(),
            "cmake_generator": self.config["cmake_generator"],
            "build_type": self.config["cmake_config"],
            "timestamp": str(datetime.datetime.now()),
            "project_root": str(self.project_root),
            "build_dir": str(self.build_dir)
        }
        
        with open(self.project_root / "build_info.json", "w") as f:
            json.dump(build_info, f, indent=2)
    
    def full_build_and_test(self, clean=True, test_categories=None, coverage=False, 
                           html_report=False, parallel=False, verbose=False):
        """Perform complete build and test cycle."""
        # Use new build system if available
        if self.new_builder:
            self.logger.info("Using new build system for full build and test")
            try:
                # Clean if requested
                if clean:
                    self.new_builder.clean()
                
                # Full build
                if not self.new_builder.full_build(clean_first=False):
                    return False
                
                # Run tests if categories specified
                if test_categories:
                    from build_system.testing import TestRunner
                    test_runner = TestRunner(self.logger, self.new_builder.config.platform)
                    
                    kwargs = {
                        'coverage': coverage,
                        'parallel': parallel,
                        'verbose': verbose,
                        'html_report': html_report
                    }
                    
                    results = test_runner.run_multiple_suites(test_categories, **kwargs)
                    
                    # Check if any tests failed
                    total_failed = sum(r.failed + r.errors for r in results.values())
                    if total_failed > 0:
                        self.logger.error(f"Tests failed: {total_failed} failures/errors")
                        return False
                
                return True
            except Exception as e:
                self.logger.error(f"New build system failed, falling back to legacy: {e}")
                # Fall through to legacy system
        
        # Legacy build system (existing implementation)
        self.log(f"Starting full build and test on {self.platform}")
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Clean build if requested
            if clean:
                self.clean_build()
            
            # Configure and build
            self.configure_cmake()
            self.build_project()
            
            # Install Python module
            if not self.install_python_module():
                return False
            
            # Run tests
            test_success = self.run_tests(
                test_categories=test_categories,
                coverage=coverage,
                html_report=html_report,
                parallel=parallel,
                verbose=verbose
            )
            
            # Generate build info
            self.generate_build_info()
            
            if test_success:
                self.log("Build and test completed successfully!", "SUCCESS")
            else:
                self.log("Build completed but some tests failed", "WARN")
            
            return test_success
            
        except Exception as e:
            self.log(f"Build and test failed: {e}", "ERROR")
            return False


def main():
    parser = argparse.ArgumentParser(description="Cross-platform LC-3 Simulator build and test script")
    
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    parser.add_argument("--no-test", action="store_true", help="Build only, skip tests")
    parser.add_argument("--test-only", action="store_true", help="Run tests only, skip build")
    parser.add_argument("--categories", nargs="+", help="Test categories to run")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--install-deps", action="store_true", help="Install Python dependencies")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    
    args = parser.parse_args()
    
    builder = CrossPlatformBuilder()
    
    if args.check_deps:
        return 0 if builder.check_dependencies() else 1
    
    if args.install_deps:
        builder.install_python_dependencies()
        return 0
    
    if args.test_only:
        success = builder.run_tests(
            test_categories=args.categories,
            coverage=args.coverage,
            html_report=args.html_report,
            parallel=args.parallel,
            verbose=args.verbose
        )
        return 0 if success else 1
    
    if args.no_test:
        try:
            if args.clean:
                builder.clean_build()
            builder.configure_cmake()
            builder.build_project()
            builder.install_python_module()
            return 0
        except Exception:
            return 1
    
    # Full build and test
    success = builder.full_build_and_test(
        clean=args.clean,
        test_categories=args.categories,
        coverage=args.coverage,
        html_report=args.html_report,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    import datetime
    sys.exit(main())
