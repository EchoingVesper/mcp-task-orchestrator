"""
Stage 2: Unit Test Validation

Executes comprehensive unit testing with coverage analysis, ensuring
all unit tests pass and coverage targets are met across all layers
of the Clean Architecture implementation.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import time

from .base_stage import ValidationStageBase
from .models import ValidationIssue, SeverityLevel, StageMetrics


logger = logging.getLogger(__name__)


class UnitTestStage(ValidationStageBase):
    """Stage 2: Unit Test execution with coverage analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            stage_id=2,
            stage_name="Unit Test Validation",
            config=config
        )
        self.min_coverage = config.get('min_coverage', 85)
        self.coverage_targets = config.get('coverage_targets', {
            'overall_minimum': 85,
            'security_components': 95,
            'domain_layer': 90,
            'mcp_handlers': 85
        })
        self.fail_on_coverage = config.get('fail_on_coverage', True)
    
    async def _execute_stage(self) -> None:
        """Execute unit test validation with coverage analysis."""
        start_time = time.time()
        
        logger.info("Starting unit test execution with coverage analysis")
        
        # 1. Run unit tests with coverage
        test_result = await self._run_unit_tests_with_coverage()
        
        # 2. Analyze coverage results
        coverage_result = await self._analyze_coverage_results()
        
        # 3. Run security-specific unit tests
        security_result = await self._run_security_unit_tests()
        
        # 4. Validate test structure and organization
        structure_result = await self._validate_test_structure()
        
        # 5. Check for test quality issues
        quality_result = await self._analyze_test_quality()
        
        # Record metrics
        execution_time = timedelta(seconds=time.time() - start_time)
        
        total_tests = (
            test_result.get('tests_collected', 0) +
            security_result.get('tests_collected', 0)
        )
        
        metrics = StageMetrics(
            execution_time=execution_time,
            tests_run=total_tests,
            files_processed=len(self._get_test_files())
        )
        self._add_metric(metrics)
        
        # Store comprehensive results as artifacts
        self._add_artifact('unit_test_results', test_result)
        self._add_artifact('coverage_analysis', coverage_result)
        self._add_artifact('security_test_results', security_result)
        self._add_artifact('test_structure_analysis', structure_result)
        self._add_artifact('test_quality_analysis', quality_result)
        
        logger.info(f"Unit test validation completed in {execution_time.total_seconds():.2f}s")
    
    async def _run_unit_tests_with_coverage(self) -> Dict[str, Any]:
        """Run pytest with comprehensive coverage measurement."""
        logger.info("Running unit tests with coverage")
        
        # Prepare pytest command with coverage
        cmd = [
            'pytest',
            'tests/unit/',
            '--cov=mcp_task_orchestrator',
            '--cov-report=json:coverage.json',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_results.json',
            '-v',
            '--strict-markers',
            '--durations=10'
        ]
        
        # Add specific coverage options
        cmd.extend([
            '--cov-branch',  # Enable branch coverage
            '--cov-fail-under', str(self.min_coverage)
        ])
        
        result = await self._run_tool(cmd)
        
        test_results = {
            'success': result.success,
            'exit_code': result.exit_code,
            'execution_time': result.execution_time.total_seconds(),
            'output': result.output,
            'error_output': result.error_output
        }
        
        # Parse pytest JSON results if available
        json_report_path = self.project_root / 'test_results.json'
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    pytest_data = json.load(f)
                
                test_results.update({
                    'tests_collected': pytest_data.get('summary', {}).get('collected', 0),
                    'tests_passed': pytest_data.get('summary', {}).get('passed', 0),
                    'tests_failed': pytest_data.get('summary', {}).get('failed', 0),
                    'tests_skipped': pytest_data.get('summary', {}).get('skipped', 0),
                    'test_duration': pytest_data.get('duration', 0),
                    'test_details': pytest_data.get('tests', [])
                })
                
                # Add issues for failed tests
                for test in pytest_data.get('tests', []):
                    if test.get('outcome') == 'failed':
                        self._add_issue(
                            category="unit_test_failure",
                            severity=SeverityLevel.HIGH,
                            message=f"Unit test failed: {test.get('nodeid', 'unknown')}",
                            file_path=test.get('setup', {}).get('outcome'),
                            suggestion="Review test failure and fix the underlying issue"
                        )
                
            except Exception as e:
                logger.warning(f"Could not parse pytest JSON report: {e}")
        
        if not result.success:
            self._add_issue(
                category="unit_tests",
                severity=SeverityLevel.CRITICAL,
                message="Unit tests failed to execute successfully",
                suggestion="Check test output for specific failure details"
            )
        
        return test_results
    
    async def _analyze_coverage_results(self) -> Dict[str, Any]:
        """Analyze test coverage results against targets."""
        logger.info("Analyzing coverage results")
        
        coverage_path = self.project_root / 'coverage.json'
        coverage_analysis = {
            'overall_coverage': 0,
            'meets_targets': False,
            'coverage_by_component': {},
            'missing_coverage': [],
            'issues': []
        }
        
        if not coverage_path.exists():
            self._add_issue(
                category="coverage",
                severity=SeverityLevel.HIGH,
                message="Coverage report not found - coverage analysis failed",
                suggestion="Ensure pytest-cov is installed and coverage is being collected"
            )
            return coverage_analysis
        
        try:
            with open(coverage_path, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract overall coverage
            overall_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
            coverage_analysis['overall_coverage'] = overall_coverage
            
            # Analyze coverage by component
            files = coverage_data.get('files', {})
            component_coverage = self._analyze_coverage_by_component(files)
            coverage_analysis['coverage_by_component'] = component_coverage
            
            # Check against targets
            targets_met = self._check_coverage_targets(overall_coverage, component_coverage)
            coverage_analysis['meets_targets'] = targets_met
            
            # Find files with low coverage
            missing_coverage = []
            for file_path, file_data in files.items():
                file_coverage = file_data.get('summary', {}).get('percent_covered', 0)
                if file_coverage < self.min_coverage:
                    missing_coverage.append({
                        'file': file_path,
                        'coverage': file_coverage,
                        'missing_lines': file_data.get('missing_lines', [])
                    })
            
            coverage_analysis['missing_coverage'] = missing_coverage
            
            # Add issues for low coverage
            if overall_coverage < self.min_coverage:
                severity = SeverityLevel.CRITICAL if self.fail_on_coverage else SeverityLevel.HIGH
                self._add_issue(
                    category="coverage",
                    severity=severity,
                    message=f"Overall coverage {overall_coverage:.1f}% below target {self.min_coverage}%",
                    suggestion="Add more unit tests to improve coverage"
                )
            
            # Add issues for component coverage
            for component, target in self.coverage_targets.items():
                if component in component_coverage:
                    actual = component_coverage[component]
                    if actual < target:
                        self._add_issue(
                            category="coverage",
                            severity=SeverityLevel.HIGH,
                            message=f"{component} coverage {actual:.1f}% below target {target}%",
                            suggestion=f"Add more unit tests for {component} components"
                        )
            
        except Exception as e:
            logger.error(f"Failed to analyze coverage: {e}")
            self._add_issue(
                category="coverage",
                severity=SeverityLevel.HIGH,
                message=f"Coverage analysis failed: {str(e)}",
                suggestion="Check coverage.json format and content"
            )
        
        return coverage_analysis
    
    def _analyze_coverage_by_component(self, files: Dict[str, Any]) -> Dict[str, float]:
        """Analyze coverage by architectural component."""
        component_coverage = {
            'domain': [],
            'application': [],
            'infrastructure': [],
            'security': [],
            'mcp_handlers': [],
            'other': []
        }
        
        for file_path, file_data in files.items():
            coverage = file_data.get('summary', {}).get('percent_covered', 0)
            
            # Categorize by component
            if '/domain/' in file_path:
                component_coverage['domain'].append(coverage)
            elif '/application/' in file_path:
                component_coverage['application'].append(coverage)
            elif '/infrastructure/' in file_path:
                component_coverage['infrastructure'].append(coverage)
            elif '/security/' in file_path:
                component_coverage['security'].append(coverage)
            elif 'mcp_request_handlers' in file_path or '/mcp/' in file_path:
                component_coverage['mcp_handlers'].append(coverage)
            else:
                component_coverage['other'].append(coverage)
        
        # Calculate averages
        averages = {}
        for component, coverages in component_coverage.items():
            if coverages:
                averages[component] = sum(coverages) / len(coverages)
            else:
                averages[component] = 0
        
        return averages
    
    def _check_coverage_targets(self, overall: float, component_coverage: Dict[str, float]) -> bool:
        """Check if coverage meets all targets."""
        if overall < self.min_coverage:
            return False
        
        for component, target in self.coverage_targets.items():
            if component == 'overall_minimum':
                continue
            
            # Map target names to component names
            component_map = {
                'security_components': 'security',
                'domain_layer': 'domain',
                'mcp_handlers': 'mcp_handlers'
            }
            
            actual_component = component_map.get(component, component)
            if actual_component in component_coverage:
                if component_coverage[actual_component] < target:
                    return False
        
        return True
    
    async def _run_security_unit_tests(self) -> Dict[str, Any]:
        """Run security-focused unit tests specifically."""
        logger.info("Running security unit tests")
        
        security_test_paths = [
            'tests/security/',
            'tests/unit/*security*',
            'tests/unit/*auth*'
        ]
        
        results = {
            'tests_collected': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'security_coverage': 0,
            'execution_time': 0
        }
        
        for test_path in security_test_paths:
            if (self.project_root / test_path.replace('*', '')).exists():
                cmd = [
                    'pytest',
                    test_path,
                    '--tb=short',
                    '-v',
                    '--json-report',
                    '--json-report-file=security_test_results.json'
                ]
                
                result = await self._run_tool(cmd)
                
                if not result.success:
                    self._add_issue(
                        category="security_tests",
                        severity=SeverityLevel.HIGH,
                        message=f"Security tests failed in {test_path}",
                        suggestion="Review security test failures and fix underlying issues"
                    )
        
        return results
    
    async def _validate_test_structure(self) -> Dict[str, Any]:
        """Validate test file structure and organization."""
        logger.info("Validating test structure")
        
        test_files = self._get_test_files()
        structure_analysis = {
            'total_test_files': len(test_files),
            'test_file_naming': [],
            'missing_test_coverage': [],
            'test_organization': 'good'
        }
        
        # Check test file naming conventions
        for test_file in test_files:
            if not test_file.name.startswith('test_'):
                self._add_issue(
                    category="test_structure",
                    severity=SeverityLevel.MEDIUM,
                    message=f"Test file doesn't follow naming convention: {test_file.name}",
                    file_path=str(test_file.relative_to(self.project_root)),
                    suggestion="Rename test files to start with 'test_'"
                )
        
        # Check for missing test files for major components
        source_files = self._get_python_files()
        for source_file in source_files:
            if (not str(source_file).startswith('test') and 
                'tests/' not in str(source_file) and
                '__pycache__' not in str(source_file)):
                
                # Check if corresponding test file exists
                relative_path = source_file.relative_to(self.project_root)
                expected_test_path = self.project_root / 'tests' / 'unit' / f"test_{relative_path.name}"
                
                if not expected_test_path.exists():
                    structure_analysis['missing_test_coverage'].append(str(relative_path))
        
        if structure_analysis['missing_test_coverage']:
            self._add_issue(
                category="test_structure",
                severity=SeverityLevel.MEDIUM,
                message=f"Found {len(structure_analysis['missing_test_coverage'])} source files without corresponding tests",
                suggestion="Create unit tests for all major components"
            )
        
        return structure_analysis
    
    async def _analyze_test_quality(self) -> Dict[str, Any]:
        """Analyze test quality and identify potential issues."""
        logger.info("Analyzing test quality")
        
        test_files = self._get_test_files()
        quality_analysis = {
            'total_test_files_analyzed': len(test_files),
            'test_quality_issues': 0,
            'empty_test_files': [],
            'large_test_files': [],
            'test_patterns': {}
        }
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                
                # Check for empty test files
                if len(non_empty_lines) < 10:
                    quality_analysis['empty_test_files'].append(str(test_file.relative_to(self.project_root)))
                    self._add_issue(
                        category="test_quality",
                        severity=SeverityLevel.MEDIUM,
                        message=f"Test file appears to be empty or minimal: {test_file.name}",
                        file_path=str(test_file.relative_to(self.project_root)),
                        suggestion="Add meaningful test cases or remove empty test file"
                    )
                
                # Check for very large test files
                if len(lines) > 500:
                    quality_analysis['large_test_files'].append({
                        'file': str(test_file.relative_to(self.project_root)),
                        'lines': len(lines)
                    })
                    self._add_issue(
                        category="test_quality",
                        severity=SeverityLevel.LOW,
                        message=f"Test file is very large ({len(lines)} lines): {test_file.name}",
                        file_path=str(test_file.relative_to(self.project_root)),
                        suggestion="Consider breaking large test files into smaller, focused modules"
                    )
                
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
        
        return quality_analysis
    
    def _get_test_files(self) -> List[Path]:
        """Get all test files in the project."""
        test_files = []
        test_directories = [
            self.project_root / 'tests',
            self.project_root / 'test'
        ]
        
        for test_dir in test_directories:
            if test_dir.exists():
                test_files.extend(test_dir.glob('**/*test*.py'))
                test_files.extend(test_dir.glob('**/test_*.py'))
        
        return test_files