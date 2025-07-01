"""
Packaging and Distribution for LC-3 Simulator
==============================================

This module provides packaging capabilities for distributing
the LC-3 simulator across different platforms.
"""

import os
import shutil
import zipfile
import tarfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .core import (
    BuildPlatform,
    BuildConfiguration, 
    ProjectSettings,
    BuildLogger,
    BuildException
)


class PackageFormat(Enum):
    """Supported package formats."""
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    TAR_XZ = "tar.xz"
    WHEEL = "wheel"
    MSI = "msi"
    DEB = "deb"
    RPM = "rpm"
    DMG = "dmg"


@dataclass
class PackageSpec:
    """Specification for a package."""
    name: str
    version: str
    format: PackageFormat
    include_files: List[str]
    exclude_patterns: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.metadata is None:
            self.metadata = {}


class PackageManager:
    """Manages packaging operations for the LC-3 simulator."""
    
    def __init__(self, config: BuildConfiguration, project: ProjectSettings, logger: BuildLogger):
        self.config = config
        self.project = project
        self.logger = logger
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        # Ensure dist directory exists
        self.dist_dir.mkdir(exist_ok=True)
    
    def create_binary_package(self, spec: Optional[PackageSpec] = None) -> Path:
        """Create a binary package of the built simulator."""
        if spec is None:
            spec = self._get_default_binary_spec()
        
        self.logger.info(f"Creating binary package: {spec.name}")
        
        # Determine package filename
        platform_suffix = self._get_platform_suffix()
        package_name = f"{spec.name}-{spec.version}-{platform_suffix}"
        
        if spec.format == PackageFormat.ZIP:
            return self._create_zip_package(spec, package_name)
        elif spec.format == PackageFormat.TAR_GZ:
            return self._create_tar_package(spec, package_name, "gz")
        elif spec.format == PackageFormat.TAR_XZ:
            return self._create_tar_package(spec, package_name, "xz")
        else:
            raise BuildException(f"Unsupported package format: {spec.format}")
    
    def create_source_package(self, spec: Optional[PackageSpec] = None) -> Path:
        """Create a source package of the project."""
        if spec is None:
            spec = self._get_default_source_spec()
        
        self.logger.info(f"Creating source package: {spec.name}")
        
        package_name = f"{spec.name}-{spec.version}-src"
        
        if spec.format == PackageFormat.ZIP:
            return self._create_zip_package(spec, package_name)
        elif spec.format in [PackageFormat.TAR_GZ, PackageFormat.TAR_XZ]:
            compression = "gz" if spec.format == PackageFormat.TAR_GZ else "xz"
            return self._create_tar_package(spec, package_name, compression)
        else:
            raise BuildException(f"Unsupported source package format: {spec.format}")
    
    def create_python_wheel(self) -> Optional[Path]:
        """Create a Python wheel package."""
        if not self.project.build_python_bindings:
            self.logger.warning("Python bindings not enabled, skipping wheel creation")
            return None
        
        self.logger.info("Creating Python wheel package...")
        
        # Check if wheel is available
        try:
            subprocess.run(
                [self._get_python_exe(), "-c", "import wheel"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            self.logger.error("wheel package not found. Install with: pip install wheel")
            return None
        
        # Build wheel
        try:
            result = subprocess.run(
                [self._get_python_exe(), "setup.py", "bdist_wheel"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Find the created wheel
            wheel_files = list(self.dist_dir.glob("*.whl"))
            if wheel_files:
                wheel_file = wheel_files[-1]  # Get the most recent
                self.logger.info(f"Created wheel: {wheel_file.name}")
                return wheel_file
            else:
                self.logger.error("No wheel file found after build")
                return None
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create wheel: {e}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            return None
    
    def _get_default_binary_spec(self) -> PackageSpec:
        """Get default binary package specification."""
        include_files = [
            "build/simulator-lc3*",  # Main executable
            "*.md",  # Documentation
            "LICENSE*",
            "requirements.txt",
            "test_programs/**/*"
        ]
        
        # Add Python bindings if built
        if self.project.build_python_bindings:
            include_files.extend([
                "*.pyd",
                "*.so",
                "python_bindings/**/*"
            ])
        
        exclude_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/.pytest_cache/**",
            "**/htmlcov/**"
        ]
        
        # Choose format based on platform
        format_choice = PackageFormat.ZIP if self.config.platform == BuildPlatform.WINDOWS else PackageFormat.TAR_GZ
        
        return PackageSpec(
            name=self.project.name,
            version=self.project.version,
            format=format_choice,
            include_files=include_files,
            exclude_patterns=exclude_patterns,
            metadata={
                "description": self.project.description,
                "platform": self.config.platform.value,
                "architecture": self.config.architecture.value,
                "build_type": self.config.build_type.value
            }
        )
    
    def _get_default_source_spec(self) -> PackageSpec:
        """Get default source package specification."""
        include_files = [
            "**/*.cpp",
            "**/*.h",
            "**/*.py", 
            "**/*.cmake",
            "CMakeLists.txt",
            "Makefile",
            "*.md",
            "*.txt",
            "*.toml",
            "*.ini",
            "LICENSE*",
            "test_programs/**/*",
            "tests/**/*",
            "docs/**/*",
            "scripts/**/*"
        ]
        
        exclude_patterns = [
            "**/build/**",
            "**/dist/**",
            "**/__pycache__/**",
            "**/*.pyc",
            "**/.git/**",
            "**/.pytest_cache/**",
            "**/htmlcov/**",
            "**/*.pyd",
            "**/*.so",
            "**/coverage.json",
            "**/test_results_*.json",
            "**/test_report_*.html"
        ]
        
        return PackageSpec(
            name=self.project.name,
            version=self.project.version,
            format=PackageFormat.TAR_GZ,
            include_files=include_files,
            exclude_patterns=exclude_patterns,
            metadata={
                "description": self.project.description,
                "type": "source"
            }
        )
    
    def _create_zip_package(self, spec: PackageSpec, package_name: str) -> Path:
        """Create a ZIP package."""
        package_file = self.dist_dir / f"{package_name}.zip"
        
        with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            files_to_include = self._collect_files(spec.include_files, spec.exclude_patterns)
            
            for file_path in files_to_include:
                # Calculate archive name (relative to project root)
                archive_name = file_path.relative_to(self.project_root)
                zf.write(file_path, archive_name)
                self.logger.debug(f"Added to ZIP: {archive_name}")
        
        self.logger.info(f"Created ZIP package: {package_file}")
        return package_file
    
    def _create_tar_package(self, spec: PackageSpec, package_name: str, compression: str) -> Path:
        """Create a TAR package with optional compression."""
        if compression == "gz":
            package_file = self.dist_dir / f"{package_name}.tar.gz"
            mode = "w:gz"
        elif compression == "xz":
            package_file = self.dist_dir / f"{package_name}.tar.xz"
            mode = "w:xz"
        else:
            package_file = self.dist_dir / f"{package_name}.tar"
            mode = "w"
        
        with tarfile.open(package_file, mode) as tf:
            files_to_include = self._collect_files(spec.include_files, spec.exclude_patterns)
            
            for file_path in files_to_include:
                # Calculate archive name (relative to project root)
                archive_name = package_name / file_path.relative_to(self.project_root)
                tf.add(file_path, archive_name)
                self.logger.debug(f"Added to TAR: {archive_name}")
        
        self.logger.info(f"Created TAR package: {package_file}")
        return package_file
    
    def _collect_files(self, include_patterns: List[str], exclude_patterns: List[str]) -> List[Path]:
        """Collect files based on include and exclude patterns."""
        included_files = set()
        
        # Collect included files
        for pattern in include_patterns:
            pattern_path = Path(pattern)
            
            if pattern_path.is_absolute():
                # Absolute pattern
                for file_path in Path().glob(pattern):
                    if file_path.is_file():
                        included_files.add(file_path)
            else:
                # Relative pattern from project root
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file():
                        included_files.add(file_path)
        
        # Filter out excluded files
        filtered_files = []
        for file_path in included_files:
            relative_path = file_path.relative_to(self.project_root)
            
            # Check against exclude patterns
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if relative_path.match(exclude_pattern):
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    def _get_platform_suffix(self) -> str:
        """Get platform-specific suffix for package names."""
        platform_map = {
            BuildPlatform.WINDOWS: "win",
            BuildPlatform.LINUX: "linux", 
            BuildPlatform.MACOS: "macos"
        }
        
        platform_name = platform_map.get(self.config.platform, "unknown")
        arch_name = self.config.architecture.value
        
        return f"{platform_name}-{arch_name}"
    
    def _get_python_exe(self) -> str:
        """Get Python executable path."""
        from .core import PlatformDetector
        try:
            return PlatformDetector.get_python_executable()
        except BuildException:
            return "python"


class DistributionBuilder:
    """Builds complete distribution packages with installers."""
    
    def __init__(self, package_manager: PackageManager, logger: BuildLogger):
        self.package_manager = package_manager
        self.logger = logger
        self.project_root = self.package_manager.project_root
        self.dist_dir = self.package_manager.dist_dir
    
    def create_release_distribution(self, version: Optional[str] = None) -> Dict[str, Path]:
        """Create a complete release distribution with all package types."""
        if version:
            self.package_manager.project.version = version
        
        self.logger.info(f"Creating release distribution for version {self.package_manager.project.version}")
        
        packages = {}
        
        try:
            # Binary package
            binary_package = self.package_manager.create_binary_package()
            packages["binary"] = binary_package
            
            # Source package
            source_package = self.package_manager.create_source_package()
            packages["source"] = source_package
            
            # Python wheel (if applicable)
            wheel_package = self.package_manager.create_python_wheel()
            if wheel_package:
                packages["wheel"] = wheel_package
            
            # Create checksums
            self._create_checksums(packages)
            
            # Create release notes
            self._create_release_notes(packages)
            
            self.logger.info("Release distribution created successfully")
            return packages
            
        except Exception as e:
            self.logger.error(f"Failed to create release distribution: {e}")
            raise
    
    def _create_checksums(self, packages: Dict[str, Path]):
        """Create checksum files for all packages."""
        checksums_file = self.dist_dir / "checksums.txt"
        
        with open(checksums_file, 'w') as f:
            f.write(f"# Checksums for {self.package_manager.project.name} v{self.package_manager.project.version}\n")
            f.write(f"# Generated on {__import__('datetime').datetime.now()}\n\n")
            
            for package_type, package_path in packages.items():
                if package_path and package_path.exists():
                    checksum = self._calculate_sha256(package_path)
                    f.write(f"{checksum}  {package_path.name}\n")
        
        self.logger.info(f"Created checksums file: {checksums_file}")
    
    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        import hashlib
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _create_release_notes(self, packages: Dict[str, Path]):
        """Create release notes file."""
        release_notes_file = self.dist_dir / "RELEASE_NOTES.md"
        
        with open(release_notes_file, 'w') as f:
            f.write(f"# {self.package_manager.project.name} v{self.package_manager.project.version}\n\n")
            f.write(f"{self.package_manager.project.description}\n\n")
            
            f.write("## Package Contents\n\n")
            for package_type, package_path in packages.items():
                if package_path and package_path.exists():
                    size_mb = package_path.stat().st_size / (1024 * 1024)
                    f.write(f"- **{package_type.title()}**: `{package_path.name}` ({size_mb:.1f} MB)\n")
            
            f.write("\n## Installation\n\n")
            f.write("### Binary Package\n")
            f.write("1. Download the binary package for your platform\n")
            f.write("2. Extract the archive\n")
            f.write("3. Run the simulator executable\n\n")
            
            if "wheel" in packages:
                f.write("### Python Package\n")
                f.write("```bash\n")
                f.write(f"pip install {packages['wheel'].name}\n")
                f.write("```\n\n")
            
            f.write("### Source Package\n")
            f.write("1. Download the source package\n")
            f.write("2. Extract the archive\n")
            f.write("3. Follow build instructions in README.md\n\n")
            
            f.write("## System Requirements\n\n")
            f.write("- Operating System: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.15+\n")
            f.write("- Architecture: x86_64\n")
            f.write("- Python: 3.8+ (for Python bindings)\n")
            f.write("- CMake: 3.12+ (for building from source)\n\n")
        
        self.logger.info(f"Created release notes: {release_notes_file}")
    
    def clean_dist_directory(self):
        """Clean the distribution directory."""
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            self.dist_dir.mkdir()
            self.logger.info("Distribution directory cleaned")
    
    def list_distributions(self) -> List[Path]:
        """List all files in the distribution directory."""
        if not self.dist_dir.exists():
            return []
        
        return [f for f in self.dist_dir.iterdir() if f.is_file()]
