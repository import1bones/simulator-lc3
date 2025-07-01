#!/usr/bin/env python3
"""
LC-3 Simulator Build System CLI
===============================

Comprehensive command-line interface for building, testing, and packaging
the LC-3 simulator across multiple platforms.

This script provides a unified interface to all build system functionality
and can replace the legacy shell scripts.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

# Add build_system to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from build_system import (
        create_builder,
        BuildPlatform,
        BuildType,
        Architecture,
        BuildConfiguration,
        ProjectSettings,
        BuildLogger,
        TestRunner,
        CoverageReporter,
        TestReportGenerator,
        PackageManager,
        DistributionBuilder,
        DependencyResolver,
        CI_AVAILABLE
    )
    
    # Import CI components if available
    if CI_AVAILABLE:
        from build_system.ci import CIPlatform, create_ci_configuration
    else:
        CIPlatform = None
        create_ci_configuration = None
        
except ImportError as e:
    print(f"Error importing build system: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)


class LC3BuildCLI:
    """Command-line interface for the LC-3 build system."""
    
    def __init__(self):
        self.logger = BuildLogger("LC3BuildCLI")
        self.project_root = Path.cwd()
        
        # Create default configuration
        self.config = BuildConfiguration(
            platform=BuildPlatform.WINDOWS if sys.platform.startswith('win') else 
                     BuildPlatform.MACOS if sys.platform == 'darwin' else BuildPlatform.LINUX,
            architecture=Architecture.X86_64,
            build_type=BuildType.DEBUG
        )
        
        self.project = ProjectSettings()
        self.builder = create_builder(config=self.config, project=self.project, logger=self.logger)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            description="LC-3 Simulator Build System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s build                          # Build the project
  %(prog)s build --clean --release        # Clean build in Release mode
  %(prog)s test                           # Run all tests
  %(prog)s test --categories basic memory # Run specific test categories
  %(prog)s test --coverage --html-report  # Run tests with coverage and HTML report
  %(prog)s package                        # Create distribution packages
  %(prog)s ci-setup github                # Set up GitHub Actions CI
  %(prog)s deps --check                   # Check dependencies
  %(prog)s full-build --clean --test      # Complete build and test cycle
            """
        )
        
        # Global options
        parser.add_argument(
            "--platform", 
            choices=[p.value for p in BuildPlatform], 
            help="Target platform (auto-detected if not specified)"
        )
        parser.add_argument(
            "--architecture",
            choices=[a.value for a in Architecture],
            default="x86_64",
            help="Target architecture"
        )
        parser.add_argument(
            "--build-type",
            choices=[bt.value for bt in BuildType],
            default="Debug",
            help="Build configuration type"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        parser.add_argument(
            "--quiet", "-q",
            action="store_true", 
            help="Suppress non-essential output"
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Build command
        self._add_build_parser(subparsers)
        
        # Test command
        self._add_test_parser(subparsers)
        
        # Package command
        self._add_package_parser(subparsers)
        
        # Dependencies command
        self._add_deps_parser(subparsers)
        
        # CI setup command
        self._add_ci_parser(subparsers)
        
        # Full build command
        self._add_full_build_parser(subparsers)
        
        # Clean command
        self._add_clean_parser(subparsers)
        
        # Info command
        self._add_info_parser(subparsers)
        
        return parser
    
    def _add_build_parser(self, subparsers):
        """Add build command parser."""
        build_parser = subparsers.add_parser("build", help="Build the project")
        build_parser.add_argument("--clean", action="store_true", help="Clean before building")
        build_parser.add_argument("--configure-only", action="store_true", help="Only configure, don't build")
        build_parser.add_argument("--parallel", "-j", type=int, default=4, help="Number of parallel jobs")
        build_parser.add_argument("--generator", help="CMake generator to use")
        build_parser.add_argument("--no-python", action="store_true", help="Disable Python bindings")
        build_parser.add_argument("--cmake-args", nargs="*", help="Additional CMake arguments")
    
    def _add_test_parser(self, subparsers):
        """Add test command parser."""
        test_parser = subparsers.add_parser("test", help="Run tests")
        test_parser.add_argument(
            "--categories", 
            nargs="+", 
            choices=["basic", "memory", "instructions", "pipeline", "integration", "io", "performance", "all"],
            default=["basic", "memory", "instructions"],
            help="Test categories to run"
        )
        test_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
        test_parser.add_argument("--html-report", action="store_true", help="Generate HTML test report")
        test_parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
        test_parser.add_argument("--timeout", type=int, default=300, help="Test timeout in seconds")
        test_parser.add_argument("--no-deps-check", action="store_true", help="Skip dependency check")
    
    def _add_package_parser(self, subparsers):
        """Add package command parser."""
        package_parser = subparsers.add_parser("package", help="Create distribution packages")
        package_parser.add_argument("--binary", action="store_true", help="Create binary package")
        package_parser.add_argument("--source", action="store_true", help="Create source package") 
        package_parser.add_argument("--wheel", action="store_true", help="Create Python wheel")
        package_parser.add_argument("--all", action="store_true", help="Create all package types")
        package_parser.add_argument("--version", help="Override version for packages")
        package_parser.add_argument("--output-dir", type=Path, help="Output directory for packages")
    
    def _add_deps_parser(self, subparsers):
        """Add dependencies command parser."""
        deps_parser = subparsers.add_parser("deps", help="Manage dependencies")
        deps_parser.add_argument("--check", action="store_true", help="Check all dependencies")
        deps_parser.add_argument("--install", action="store_true", help="Install missing dependencies")
        deps_parser.add_argument("--report", action="store_true", help="Generate dependency report")
        deps_parser.add_argument("--requirements", type=Path, help="Requirements file to install")
    
    def _add_ci_parser(self, subparsers):
        """Add CI setup command parser."""
        if not CI_AVAILABLE:
            return  # Skip CI parser if not available
            
        ci_parser = subparsers.add_parser("ci-setup", help="Set up CI/CD configuration")
        ci_parser.add_argument(
            "platform",
            choices=["github", "gitlab"],
            help="CI platform to configure"
        )
        ci_parser.add_argument("--matrix-platforms", nargs="+", help="Platforms for build matrix")
        ci_parser.add_argument("--python-versions", nargs="+", default=["3.8", "3.9", "3.10", "3.11"])
        ci_parser.add_argument("--no-coverage", action="store_true", help="Disable coverage in CI")
        ci_parser.add_argument("--no-performance", action="store_true", help="Disable performance tests in CI")
    
    def _add_full_build_parser(self, subparsers):
        """Add full build command parser."""
        full_parser = subparsers.add_parser("full-build", help="Complete build and test cycle")
        full_parser.add_argument("--clean", action="store_true", help="Clean before building")
        full_parser.add_argument("--test", action="store_true", help="Run tests after building")
        full_parser.add_argument("--package", action="store_true", help="Create packages after testing")
        full_parser.add_argument("--test-categories", nargs="+", help="Test categories to run")
        full_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    def _add_clean_parser(self, subparsers):
        """Add clean command parser."""
        clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
        clean_parser.add_argument("--all", action="store_true", help="Clean everything including dependencies")
        clean_parser.add_argument("--build", action="store_true", help="Clean build directory")
        clean_parser.add_argument("--python", action="store_true", help="Clean Python artifacts")
        clean_parser.add_argument("--dist", action="store_true", help="Clean distribution packages")
    
    def _add_info_parser(self, subparsers):
        """Add info command parser."""
        info_parser = subparsers.add_parser("info", help="Show build system information")
        info_parser.add_argument("--config", action="store_true", help="Show build configuration")
        info_parser.add_argument("--dependencies", action="store_true", help="Show dependency status")
        info_parser.add_argument("--system", action="store_true", help="Show system information")
        info_parser.add_argument("--all", action="store_true", help="Show all information")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Configure logging level
        if parsed_args.verbose:
            self.logger.logger.setLevel("DEBUG")
        elif parsed_args.quiet:
            self.logger.logger.setLevel("WARNING")
        
        # Update configuration from arguments
        self._update_config_from_args(parsed_args)
        
        # Execute command
        try:
            if parsed_args.command == "build":
                return self._cmd_build(parsed_args)
            elif parsed_args.command == "test":
                return self._cmd_test(parsed_args)
            elif parsed_args.command == "package":
                return self._cmd_package(parsed_args)
            elif parsed_args.command == "deps":
                return self._cmd_deps(parsed_args)
            elif parsed_args.command == "ci-setup":
                return self._cmd_ci_setup(parsed_args)
            elif parsed_args.command == "full-build":
                return self._cmd_full_build(parsed_args)
            elif parsed_args.command == "clean":
                return self._cmd_clean(parsed_args)
            elif parsed_args.command == "info":
                return self._cmd_info(parsed_args)
            else:
                parser.print_help()
                return 1
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _update_config_from_args(self, args):
        """Update configuration from command line arguments."""
        if args.platform:
            self.config.platform = BuildPlatform(args.platform)
        
        if args.architecture:
            self.config.architecture = Architecture(args.architecture)
        
        if args.build_type:
            self.config.build_type = BuildType(args.build_type)
        
        # Recreate builder with updated config
        self.builder = create_builder(config=self.config, project=self.project, logger=self.logger)
    
    def _cmd_build(self, args) -> int:
        """Execute build command."""
        self.logger.info("Starting build...")
        
        # Handle generator override
        if args.generator:
            self.config.generator = args.generator
        
        # Handle CMake args
        if args.cmake_args:
            self.config.cmake_args.extend(args.cmake_args)
        
        # Handle Python bindings
        if args.no_python:
            self.project.build_python_bindings = False
        
        # Clean if requested
        if args.clean:
            if not self.builder.clean():
                return 1
        
        # Configure
        if not self.builder.configure():
            return 1
        
        # Build if not configure-only
        if not args.configure_only:
            if not self.builder.build():
                return 1
        
        self.logger.info("Build completed successfully")
        return 0
    
    def _cmd_test(self, args) -> int:
        """Execute test command."""
        self.logger.info("Starting tests...")
        
        # Create test runner
        test_runner = TestRunner(self.logger, self.config.platform)
        
        # Check dependencies unless skipped
        if not args.no_deps_check:
            if not test_runner.ensure_test_dependencies():
                return 1
        
        # Run tests
        kwargs = {
            'coverage': args.coverage,
            'parallel': args.parallel,
            'verbose': args.verbose,
            'html_report': args.html_report
        }
        
        results = {}
        for category in args.categories:
            try:
                result = test_runner.run_suite(category, **kwargs)
                results[category] = result
            except Exception as e:
                self.logger.error(f"Failed to run test suite {category}: {e}")
                return 1
        
        # Generate reports
        report_generator = TestReportGenerator(self.logger, self.project_root)
        report_generator.print_summary(results)
        report_generator.generate_summary_report(results)
        
        # Check if any tests failed
        total_failed = sum(r.failed + r.errors for r in results.values())
        if total_failed > 0:
            self.logger.error(f"Tests failed: {total_failed} failures/errors")
            return 1
        
        self.logger.info("All tests passed")
        return 0
    
    def _cmd_package(self, args) -> int:
        """Execute package command."""
        self.logger.info("Creating packages...")
        
        # Override version if specified
        if args.version:
            self.project.version = args.version
        
        package_manager = PackageManager(self.config, self.project, self.logger)
        dist_builder = DistributionBuilder(package_manager, self.logger)
        
        packages = {}
        
        try:
            if args.all or args.binary:
                packages["binary"] = package_manager.create_binary_package()
            
            if args.all or args.source:
                packages["source"] = package_manager.create_source_package()
            
            if (args.all or args.wheel) and self.project.build_python_bindings:
                wheel = package_manager.create_python_wheel()
                if wheel:
                    packages["wheel"] = wheel
            
            if args.all:
                # Create complete distribution
                all_packages = dist_builder.create_release_distribution(args.version)
                packages.update(all_packages)
            
            # Report created packages
            for pkg_type, pkg_path in packages.items():
                if pkg_path:
                    size_mb = pkg_path.stat().st_size / (1024 * 1024)
                    self.logger.info(f"Created {pkg_type} package: {pkg_path.name} ({size_mb:.1f} MB)")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Package creation failed: {e}")
            return 1
    
    def _cmd_deps(self, args) -> int:
        """Execute dependencies command."""
        dependency_resolver = DependencyResolver(self.config.platform, self.logger)
        
        if args.check or args.report:
            report = dependency_resolver.generate_dependency_report()
            
            if args.report:
                # Save report to file
                report_file = self.project_root / "dependency_report.json"
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                self.logger.info(f"Dependency report saved to: {report_file}")
            
            # Print summary
            print("\nDependency Status:")
            print("="*50)
            
            for dep in report.get("system_dependencies", []):
                status = "✓" if dep["available"] else "✗"
                version = dep.get("version", "unknown") if dep["available"] else "not found"
                print(f"{status} {dep['name']:<15} {version}")
            
            for dep in report.get("python_dependencies", []):
                status = "✓" if dep["available"] else "✗" 
                version = dep.get("version", "unknown") if dep["available"] else "not found"
                print(f"{status} {dep['name']:<15} {version}")
        
        if args.install:
            requirements_file = args.requirements or (self.project_root / "requirements.txt")
            if not dependency_resolver.resolve_all_dependencies(requirements_file):
                return 1
        
        return 0
    
    def _cmd_ci_setup(self, args) -> int:
        """Execute CI setup command."""
        if not CI_AVAILABLE:
            self.logger.error("CI setup requires PyYAML. Install with: pip install PyYAML")
            return 1
            
        self.logger.info(f"Setting up {args.platform} CI/CD...")
        
        platform_map = {
            "github": CIPlatform.GITHUB_ACTIONS,
            "gitlab": CIPlatform.GITLAB_CI
        }
        
        ci_platform = platform_map[args.platform]
        
        # Configure build matrix
        build_matrix_kwargs = {
            "include_coverage": not args.no_coverage,
            "include_performance_tests": not args.no_performance
        }
        
        if args.matrix_platforms:
            platform_map = {
                "windows": BuildPlatform.WINDOWS,
                "linux": BuildPlatform.LINUX,
                "macos": BuildPlatform.MACOS
            }
            build_matrix_kwargs["platforms"] = [platform_map[p] for p in args.matrix_platforms]
        
        if args.python_versions:
            build_matrix_kwargs["python_versions"] = args.python_versions
        
        try:
            config_file = create_ci_configuration(
                ci_platform,
                self.project.name,
                build_matrix=build_matrix_kwargs
            )
            self.logger.info(f"CI configuration created: {config_file}")
            return 0
        except Exception as e:
            self.logger.error(f"Failed to create CI configuration: {e}")
            return 1
    
    def _cmd_full_build(self, args) -> int:
        """Execute full build command."""
        self.logger.info("Starting full build cycle...")
        
        # Build
        if not self.builder.full_build(clean_first=args.clean):
            return 1
        
        # Test if requested
        if args.test:
            test_runner = TestRunner(self.logger, self.config.platform)
            
            categories = args.test_categories or ["basic", "memory", "instructions"]
            kwargs = {
                'coverage': args.coverage,
                'verbose': args.verbose
            }
            
            results = test_runner.run_multiple_suites(categories, **kwargs)
            
            # Check results
            total_failed = sum(r.failed + r.errors for r in results.values())
            if total_failed > 0:
                self.logger.error("Tests failed during full build")
                return 1
        
        # Package if requested
        if args.package:
            package_manager = PackageManager(self.config, self.project, self.logger)
            package_manager.create_binary_package()
        
        self.logger.info("Full build cycle completed successfully")
        return 0
    
    def _cmd_clean(self, args) -> int:
        """Execute clean command."""
        success = True
        
        if args.all or args.build:
            if not self.builder.cmake_builder.clean():
                success = False
        
        if args.all or args.python:
            if not self.builder.python_builder.clean():
                success = False
        
        if args.all or args.dist:
            dist_dir = self.project_root / "dist"
            if dist_dir.exists():
                import shutil
                shutil.rmtree(dist_dir)
                self.logger.info("Distribution directory cleaned")
        
        if success:
            self.logger.info("Clean completed successfully")
            return 0
        else:
            self.logger.error("Some clean operations failed")
            return 1
    
    def _cmd_info(self, args) -> int:
        """Execute info command."""
        if args.all or args.config:
            print("\nBuild Configuration:")
            print("="*50)
            print(f"Platform: {self.config.platform.value}")
            print(f"Architecture: {self.config.architecture.value}")
            print(f"Build Type: {self.config.build_type.value}")
            print(f"Generator: {self.config.generator}")
            print(f"Python Bindings: {self.project.build_python_bindings}")
            print(f"Tests: {self.project.build_tests}")
        
        if args.all or args.system:
            import platform
            print("\nSystem Information:")
            print("="*50)
            print(f"OS: {platform.system()} {platform.release()}")
            print(f"Machine: {platform.machine()}")
            print(f"Python: {platform.python_version()}")
            print(f"Working Directory: {self.project_root}")
        
        if args.all or args.dependencies:
            dependency_resolver = DependencyResolver(self.config.platform, self.logger)
            report = dependency_resolver.generate_dependency_report()
            
            print("\nDependency Status:")
            print("="*50)
            
            for dep in report.get("system_dependencies", []):
                status = "Available" if dep["available"] else "Missing"
                version = f" ({dep.get('version', 'unknown')})" if dep["available"] else ""
                print(f"{dep['name']}: {status}{version}")
        
        return 0


def main():
    """Main entry point."""
    cli = LC3BuildCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
