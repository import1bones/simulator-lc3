"""
Testing Framework for LC-3 Simulator Build System
==================================================

This module provides comprehensive testing capabilities including
test execution, coverage reporting, and result analysis.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .core import BuildLogger, BuildException, BuildPlatform
from .dependencies import PythonDependencyManager


class TestResult(Enum):
    """Test execution results."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestSuite:
    """Configuration for a test suite."""
    name: str
    path: Path
    pattern: str = "test_*.py"
    markers: List[str] = None
    timeout: int = 300
    parallel: bool = False
    coverage: bool = False
    
    def __post_init__(self):
        if self.markers is None:
            self.markers = []


@dataclass
class TestExecutionResult:
    """Results from test execution."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    exit_code: int
    output: str
    coverage_percentage: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100
    
    @property
    def overall_result(self) -> TestResult:
        """Get overall test result."""
        if self.errors > 0:
            return TestResult.ERROR
        elif self.failed > 0:
            return TestResult.FAILED
        elif self.passed > 0:
            return TestResult.PASSED
        else:
            return TestResult.SKIPPED


class TestRunner:
    """Comprehensive test runner for the LC-3 simulator."""
    
    def __init__(self, logger: BuildLogger, platform: BuildPlatform):
        self.logger = logger
        self.platform = platform
        self.project_root = Path.cwd()
        self.test_dir = self.project_root / "tests"
        
        # Initialize Python dependency manager for pytest
        try:
            self.python_manager = PythonDependencyManager(logger)
            self.python_exe = self.python_manager.python_exe
        except BuildException:
            self.logger.error("Failed to initialize Python environment for testing")
            raise
        
        # Define test suites
        self.test_suites = self._define_test_suites()
    
    def _define_test_suites(self) -> Dict[str, TestSuite]:
        """Define the available test suites."""
        suites = {}
        
        if self.test_dir.exists():
            # Basic functionality tests
            suites["basic"] = TestSuite(
                name="basic",
                path=self.test_dir,
                pattern="test_basic.py",
                markers=["not slow"],
                timeout=120
            )
            
            # Memory management tests
            suites["memory"] = TestSuite(
                name="memory", 
                path=self.test_dir,
                pattern="test_memory.py",
                timeout=180
            )
            
            # Instruction execution tests
            suites["instructions"] = TestSuite(
                name="instructions",
                path=self.test_dir,
                pattern="test_instructions.py",
                timeout=300
            )
            
            # Pipeline tests
            suites["pipeline"] = TestSuite(
                name="pipeline",
                path=self.test_dir,
                pattern="test_*pipeline*.py",
                timeout=240
            )
            
            # Integration tests
            suites["integration"] = TestSuite(
                name="integration",
                path=self.test_dir,
                pattern="test_integration*.py",
                timeout=600,
                markers=["integration"]
            )
            
            # I/O tests
            suites["io"] = TestSuite(
                name="io",
                path=self.test_dir,
                pattern="test_io.py",
                timeout=120
            )
            
            # Performance tests
            suites["performance"] = TestSuite(
                name="performance",
                path=self.test_dir,
                pattern="test_*performance*.py",
                markers=["performance"],
                timeout=900
            )
            
            # All tests
            suites["all"] = TestSuite(
                name="all",
                path=self.test_dir,
                pattern="test_*.py",
                timeout=1800,  # 30 minutes
                parallel=True,
                coverage=True
            )
        
        return suites
    
    def ensure_test_dependencies(self) -> bool:
        """Ensure all required testing dependencies are available."""
        self.logger.info("Checking test dependencies...")
        
        required_packages = [
            "pytest",
            "pytest-cov", 
            "pytest-html",
            "pytest-xdist",
            "pytest-benchmark"
        ]
        
        missing_packages = []
        for package in required_packages:
            if not self.python_manager.check_dependency(package):
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.info(f"Installing missing test dependencies: {missing_packages}")
            for package in missing_packages:
                if not self.python_manager.install_dependency(package):
                    self.logger.error(f"Failed to install {package}")
                    return False
        
        return True
    
    def run_suite(self, suite_name: str, **kwargs) -> TestExecutionResult:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise BuildException(f"Unknown test suite: {suite_name}")
        
        suite = self.test_suites[suite_name]
        self.logger.info(f"Running test suite: {suite_name}")
        
        # Override suite settings with kwargs
        coverage = kwargs.get('coverage', suite.coverage)
        parallel = kwargs.get('parallel', suite.parallel)
        verbose = kwargs.get('verbose', False)
        html_report = kwargs.get('html_report', False)
        
        # Build pytest command
        cmd = [self.python_exe, "-m", "pytest"]
        
        # Test pattern/path
        test_path = suite.path / suite.pattern
        cmd.append(str(test_path))
        
        # Verbosity
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Markers
        for marker in suite.markers:
            cmd.extend(["-m", marker])
        
        # Parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Coverage
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=term-missing",
                "--cov-report=json:coverage.json"
            ])
        
        # HTML report
        if html_report:
            report_file = self.project_root / f"test_report_{suite_name}.html"
            cmd.extend([
                "--html", str(report_file),
                "--self-contained-html"
            ])
        
        # JSON report for parsing
        json_report = self.project_root / f"test_results_{suite_name}.json"
        cmd.extend(["--json-report", f"--json-report-file={json_report}"])
        
        # Execute tests
        start_time = __import__("time").time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=suite.timeout
            )
            
            duration = __import__("time").time() - start_time
            
            # Parse results
            test_result = self._parse_test_results(
                suite_name, result, duration, json_report, coverage
            )
            
            self._log_test_results(test_result)
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = __import__("time").time() - start_time
            self.logger.error(f"Test suite {suite_name} timed out after {duration:.1f}s")
            
            return TestExecutionResult(
                suite_name=suite_name,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=duration,
                exit_code=-1,
                output="Test execution timed out"
            )
    
    def _parse_test_results(self, suite_name: str, result: subprocess.CompletedProcess,
                          duration: float, json_report: Path, coverage: bool) -> TestExecutionResult:
        """Parse test results from pytest output."""
        # Initialize with defaults
        total_tests = 0
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        coverage_percentage = None
        
        # Try to parse JSON report if available
        if json_report.exists():
            try:
                with open(json_report, 'r') as f:
                    json_data = json.load(f)
                
                summary = json_data.get('summary', {})
                total_tests = summary.get('total', 0)
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                skipped = summary.get('skipped', 0)
                errors = summary.get('error', 0)
                
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Failed to parse JSON test report: {e}")
        
        # Try to parse coverage if enabled
        if coverage:
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    coverage_percentage = coverage_data.get('totals', {}).get('percent_covered')
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # If JSON parsing failed, try to parse from stdout
        if total_tests == 0:
            total_tests, passed, failed, skipped, errors = self._parse_pytest_output(result.stdout)
        
        return TestExecutionResult(
            suite_name=suite_name,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            exit_code=result.returncode,
            output=result.stdout + "\n" + result.stderr,
            coverage_percentage=coverage_percentage
        )
    
    def _parse_pytest_output(self, output: str) -> tuple:
        """Parse pytest output to extract test counts."""
        total_tests = 0
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        
        # Look for summary line like "= 5 passed, 1 failed, 2 skipped in 1.23s ="
        for line in output.split('\n'):
            line = line.strip()
            if ' passed' in line or ' failed' in line or ' skipped' in line:
                # Extract numbers before keywords
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        count = int(part)
                        if i + 1 < len(parts):
                            keyword = parts[i + 1].lower()
                            if 'passed' in keyword:
                                passed = count
                            elif 'failed' in keyword:
                                failed = count
                            elif 'skipped' in keyword:
                                skipped = count
                            elif 'error' in keyword:
                                errors = count
        
        total_tests = passed + failed + skipped + errors
        return total_tests, passed, failed, skipped, errors
    
    def _log_test_results(self, result: TestExecutionResult):
        """Log test results in a readable format."""
        self.logger.info(f"Test suite '{result.suite_name}' completed in {result.duration:.1f}s")
        self.logger.info(f"  Total: {result.total_tests}, Passed: {result.passed}, "
                        f"Failed: {result.failed}, Skipped: {result.skipped}, Errors: {result.errors}")
        
        if result.coverage_percentage is not None:
            self.logger.info(f"  Coverage: {result.coverage_percentage:.1f}%")
        
        self.logger.info(f"  Success rate: {result.success_rate:.1f}%")
        
        if result.overall_result == TestResult.PASSED:
            self.logger.info(f"  Result: PASSED ✓")
        elif result.overall_result == TestResult.FAILED:
            self.logger.error(f"  Result: FAILED ✗")
        elif result.overall_result == TestResult.ERROR:
            self.logger.error(f"  Result: ERROR ✗")
        else:
            self.logger.warning(f"  Result: SKIPPED ⚠")
    
    def run_multiple_suites(self, suite_names: List[str], **kwargs) -> Dict[str, TestExecutionResult]:
        """Run multiple test suites."""
        results = {}
        
        for suite_name in suite_names:
            try:
                results[suite_name] = self.run_suite(suite_name, **kwargs)
            except Exception as e:
                self.logger.error(f"Failed to run test suite {suite_name}: {e}")
                results[suite_name] = TestExecutionResult(
                    suite_name=suite_name,
                    total_tests=0,
                    passed=0,
                    failed=0,
                    skipped=0,
                    errors=1,
                    duration=0.0,
                    exit_code=-1,
                    output=str(e)
                )
        
        return results
    
    def run_all_tests(self, **kwargs) -> Dict[str, TestExecutionResult]:
        """Run all available test suites."""
        self.logger.info("Running all test suites...")
        
        if not self.ensure_test_dependencies():
            raise BuildException("Failed to ensure test dependencies")
        
        # Run individual suites first for detailed reporting
        suite_names = [name for name in self.test_suites.keys() if name != "all"]
        results = self.run_multiple_suites(suite_names, **kwargs)
        
        # Then run the comprehensive "all" suite if requested
        if kwargs.get('comprehensive', False):
            results["all"] = self.run_suite("all", **kwargs)
        
        return results
    
    def get_available_suites(self) -> List[str]:
        """Get list of available test suites."""
        return list(self.test_suites.keys())


class CoverageReporter:
    """Generate and manage test coverage reports."""
    
    def __init__(self, logger: BuildLogger, project_root: Path):
        self.logger = logger
        self.project_root = project_root
        self.coverage_file = project_root / "coverage.json"
        self.html_dir = project_root / "htmlcov"
    
    def generate_html_report(self) -> bool:
        """Generate HTML coverage report."""
        if not self.coverage_file.exists():
            self.logger.error("No coverage data found. Run tests with --coverage first.")
            return False
        
        try:
            cmd = [sys.executable, "-m", "coverage", "html"]
            subprocess.run(cmd, cwd=self.project_root, check=True)
            self.logger.info(f"HTML coverage report generated in: {self.html_dir}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to generate HTML coverage report: {e}")
            return False
    
    def get_coverage_summary(self) -> Optional[Dict[str, Any]]:
        """Get coverage summary from JSON report."""
        if not self.coverage_file.exists():
            return None
        
        try:
            with open(self.coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            return coverage_data.get('totals', {})
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse coverage data: {e}")
            return None


class TestReportGenerator:
    """Generate comprehensive test reports."""
    
    def __init__(self, logger: BuildLogger, project_root: Path):
        self.logger = logger
        self.project_root = project_root
    
    def generate_summary_report(self, results: Dict[str, TestExecutionResult], 
                              output_file: Optional[Path] = None) -> bool:
        """Generate a summary report of all test results."""
        if output_file is None:
            output_file = self.project_root / "test_summary.json"
        
        # Calculate overall statistics
        total_suites = len(results)
        total_tests = sum(r.total_tests for r in results.values())
        total_passed = sum(r.passed for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        total_skipped = sum(r.skipped for r in results.values())
        total_errors = sum(r.errors for r in results.values())
        total_duration = sum(r.duration for r in results.values())
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Create summary
        summary = {
            "timestamp": str(__import__("datetime").datetime.now()),
            "overall_statistics": {
                "total_suites": total_suites,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_skipped": total_skipped,
                "total_errors": total_errors,
                "total_duration": total_duration,
                "success_rate": overall_success_rate
            },
            "suite_results": {}
        }
        
        # Add individual suite results
        for suite_name, result in results.items():
            summary["suite_results"][suite_name] = {
                "total_tests": result.total_tests,
                "passed": result.passed,
                "failed": result.failed,
                "skipped": result.skipped,
                "errors": result.errors,
                "duration": result.duration,
                "success_rate": result.success_rate,
                "overall_result": result.overall_result.value,
                "coverage_percentage": result.coverage_percentage
            }
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info(f"Test summary report saved to: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save test summary report: {e}")
            return False
    
    def print_summary(self, results: Dict[str, TestExecutionResult]):
        """Print a formatted summary to the console."""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        # Overall statistics
        total_tests = sum(r.total_tests for r in results.values())
        total_passed = sum(r.passed for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        total_skipped = sum(r.skipped for r in results.values())
        total_errors = sum(r.errors for r in results.values())
        total_duration = sum(r.duration for r in results.values())
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} | Failed: {total_failed} | Skipped: {total_skipped} | Errors: {total_errors}")
        print(f"Total Duration: {total_duration:.1f}s")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print("\nSuite Details:")
        print("-" * 80)
        
        for suite_name, result in results.items():
            status = "✓" if result.overall_result == TestResult.PASSED else "✗"
            print(f"{status} {suite_name:<20} {result.passed:>3}/{result.total_tests:<3} "
                  f"({result.success_rate:>5.1f}%) {result.duration:>6.1f}s")
        
        print("="*80)
