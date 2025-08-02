"""
Stage 3: Integration Test Validation

Executes comprehensive integration testing including MCP protocol compliance,
database integration, component interaction validation, and end-to-end
workflow testing across the Clean Architecture layers.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import time
import asyncio

from .base_stage import ValidationStageBase
from .models import ValidationIssue, SeverityLevel, StageMetrics


logger = logging.getLogger(__name__)


class IntegrationTestStage(ValidationStageBase):
    """Stage 3: Integration test execution with component interaction validation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            stage_id=3,
            stage_name="Integration Test Validation",
            config=config
        )
        self.test_timeout = config.get('test_timeout_minutes', 15)
        self.database_test_required = config.get('database_test_required', True)
        self.mcp_test_required = config.get('mcp_test_required', True)
        self.e2e_test_required = config.get('e2e_test_required', True)
    
    async def _execute_stage(self) -> None:
        """Execute integration test validation."""
        start_time = time.time()
        
        logger.info("Starting integration test validation")
        
        # 1. Run basic integration tests
        integration_result = await self._run_integration_tests()
        
        # 2. Test MCP protocol compliance and tool integration
        mcp_result = await self._test_mcp_integration()
        
        # 3. Test database integration and persistence
        db_result = await self._test_database_integration()
        
        # 4. Test security framework integration
        security_result = await self._test_security_integration()
        
        # 5. Test end-to-end workflows
        e2e_result = await self._test_end_to_end_workflows()
        
        # 6. Test component interaction boundaries
        component_result = await self._test_component_boundaries()
        
        # 7. Test error handling integration
        error_handling_result = await self._test_error_handling_integration()
        
        # Record metrics
        execution_time = timedelta(seconds=time.time() - start_time)
        
        total_tests = sum([
            integration_result.get('tests_run', 0),
            mcp_result.get('tests_run', 0),
            db_result.get('tests_run', 0),
            security_result.get('tests_run', 0),
            e2e_result.get('tests_run', 0)
        ])
        
        metrics = StageMetrics(
            execution_time=execution_time,
            tests_run=total_tests,
            files_processed=len(self._get_integration_test_files())
        )
        self._add_metric(metrics)
        
        # Store comprehensive results as artifacts
        self._add_artifact('integration_test_results', integration_result)
        self._add_artifact('mcp_integration_results', mcp_result)
        self._add_artifact('database_integration_results', db_result)
        self._add_artifact('security_integration_results', security_result)
        self._add_artifact('e2e_test_results', e2e_result)
        self._add_artifact('component_boundary_results', component_result)
        self._add_artifact('error_handling_results', error_handling_result)
        
        logger.info(f"Integration test validation completed in {execution_time.total_seconds():.2f}s")
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run basic integration tests."""
        logger.info("Running integration tests")
        
        cmd = [
            'pytest',
            'tests/integration/',
            '--tb=short',
            '--json-report',
            '--json-report-file=integration_test_results.json',
            '-v',
            '--durations=10',
            f'--timeout={self.test_timeout * 60}'
        ]
        
        result = await self._run_tool(cmd)
        
        test_results = {
            'success': result.success,
            'exit_code': result.exit_code,
            'execution_time': result.execution_time.total_seconds(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'output': result.output,
            'error_output': result.error_output
        }
        
        # Parse pytest JSON results if available
        json_report_path = self.project_root / 'integration_test_results.json'
        if json_report_path.exists():
            try:
                with open(json_report_path, 'r') as f:
                    pytest_data = json.load(f)
                
                test_results.update({
                    'tests_run': pytest_data.get('summary', {}).get('collected', 0),
                    'tests_passed': pytest_data.get('summary', {}).get('passed', 0),
                    'tests_failed': pytest_data.get('summary', {}).get('failed', 0),
                    'tests_skipped': pytest_data.get('summary', {}).get('skipped', 0),
                })
                
                # Add issues for failed tests
                for test in pytest_data.get('tests', []):
                    if test.get('outcome') == 'failed':
                        self._add_issue(
                            category="integration_test_failure",
                            severity=SeverityLevel.HIGH,
                            message=f"Integration test failed: {test.get('nodeid', 'unknown')}",
                            suggestion="Review integration test failure and fix component interactions"
                        )
                
            except Exception as e:
                logger.warning(f"Could not parse integration test JSON report: {e}")
        
        if not result.success:
            self._add_issue(
                category="integration_tests",
                severity=SeverityLevel.CRITICAL,
                message="Integration tests failed to execute successfully",
                suggestion="Check test output for specific failure details and component interaction issues"
            )
        
        return test_results
    
    async def _test_mcp_integration(self) -> Dict[str, Any]:
        """Test MCP protocol compliance and tool integration."""
        logger.info("Testing MCP integration")
        
        mcp_results = {
            'protocol_compliance': True,
            'tool_registration': True,
            'tool_execution': True,
            'error_handling': True,
            'tests_run': 0,
            'issues': []
        }
        
        if not self.mcp_test_required:
            logger.info("MCP testing skipped - not required")
            return mcp_results
        
        try:
            # 1. Test MCP server startup
            startup_result = await self._test_mcp_server_startup()
            mcp_results['server_startup'] = startup_result
            
            # 2. Test tool registration
            registration_result = await self._test_mcp_tool_registration()
            mcp_results['tool_registration'] = registration_result['success']
            
            # 3. Test individual MCP tools
            tools_result = await self._test_mcp_tools()
            mcp_results['tool_execution'] = tools_result['success']
            
            # 4. Test MCP error handling
            error_result = await self._test_mcp_error_handling()
            mcp_results['error_handling'] = error_result['success']
            
            # 5. Test MCP protocol compliance
            protocol_result = await self._test_mcp_protocol_compliance()
            mcp_results['protocol_compliance'] = protocol_result['success']
            
            mcp_results['tests_run'] = sum([
                startup_result.get('tests_run', 0),
                registration_result.get('tests_run', 0),
                tools_result.get('tests_run', 0),
                error_result.get('tests_run', 0),
                protocol_result.get('tests_run', 0)
            ])
            
        except Exception as e:
            logger.error(f"MCP integration testing failed: {e}")
            self._add_issue(
                category="mcp_integration",
                severity=SeverityLevel.CRITICAL,
                message=f"MCP integration testing failed: {str(e)}",
                suggestion="Check MCP server configuration and tool implementations"
            )
            mcp_results['protocol_compliance'] = False
        
        return mcp_results
    
    async def _test_mcp_server_startup(self) -> Dict[str, Any]:
        """Test MCP server startup and initialization."""
        logger.info("Testing MCP server startup")
        
        startup_test = {
            'success': False,
            'tests_run': 1,
            'startup_time': 0,
            'issues': []
        }
        
        try:
            # Test server startup by attempting to import and initialize
            cmd = [
                'python', '-c',
                'from mcp_task_orchestrator.server import main; '
                'import asyncio; '
                'print("MCP server import successful")'
            ]
            
            result = await self._run_tool(cmd)
            startup_test['success'] = result.success
            startup_test['startup_time'] = result.execution_time.total_seconds()
            
            if not result.success:
                self._add_issue(
                    category="mcp_startup",
                    severity=SeverityLevel.CRITICAL,
                    message="MCP server failed to start or import",
                    suggestion="Check server dependencies and configuration"
                )
            
        except Exception as e:
            logger.error(f"MCP server startup test failed: {e}")
            self._add_issue(
                category="mcp_startup",
                severity=SeverityLevel.CRITICAL,
                message=f"MCP server startup test failed: {str(e)}",
                suggestion="Check MCP server implementation and dependencies"
            )
        
        return startup_test
    
    async def _test_mcp_tool_registration(self) -> Dict[str, Any]:
        """Test MCP tool registration and discovery."""
        logger.info("Testing MCP tool registration")
        
        registration_test = {
            'success': False,
            'tests_run': 1,
            'tools_registered': 0,
            'missing_tools': []
        }
        
        try:
            # Test tool registration by checking the handlers file
            handlers_file = self.project_root / 'mcp_task_orchestrator' / 'mcp_request_handlers.py'
            
            if handlers_file.exists():
                with open(handlers_file, 'r') as f:
                    content = f.read()
                
                # Expected tools based on the orchestrator functionality
                expected_tools = [
                    'orchestrator_initialize',
                    'orchestrator_plan_task',
                    'orchestrator_execute_task',
                    'orchestrator_complete_task',
                    'orchestrator_get_status'
                ]
                
                registered_tools = 0
                for tool in expected_tools:
                    if tool in content:
                        registered_tools += 1
                    else:
                        registration_test['missing_tools'].append(tool)
                
                registration_test['tools_registered'] = registered_tools
                registration_test['success'] = len(registration_test['missing_tools']) == 0
                
                if registration_test['missing_tools']:
                    self._add_issue(
                        category="mcp_tools",
                        severity=SeverityLevel.HIGH,
                        message=f"Missing MCP tool registrations: {registration_test['missing_tools']}",
                        suggestion="Ensure all required MCP tools are properly registered"
                    )
            else:
                self._add_issue(
                    category="mcp_tools",
                    severity=SeverityLevel.CRITICAL,
                    message="MCP request handlers file not found",
                    suggestion="Create or restore the MCP request handlers file"
                )
            
        except Exception as e:
            logger.error(f"MCP tool registration test failed: {e}")
            self._add_issue(
                category="mcp_tools",
                severity=SeverityLevel.HIGH,
                message=f"MCP tool registration test failed: {str(e)}",
                suggestion="Check MCP tool registration implementation"
            )
        
        return registration_test
    
    async def _test_mcp_tools(self) -> Dict[str, Any]:
        """Test individual MCP tool execution."""
        logger.info("Testing MCP tools execution")
        
        # Run MCP tool tests if they exist
        mcp_test_path = self.project_root / 'tests' / 'integration' / 'test_mcp_tools.py'
        
        if mcp_test_path.exists():
            cmd = [
                'pytest',
                str(mcp_test_path),
                '--tb=short',
                '-v'
            ]
            
            result = await self._run_tool(cmd)
            
            return {
                'success': result.success,
                'tests_run': 1,
                'execution_time': result.execution_time.total_seconds(),
                'output': result.output
            }
        else:
            self._add_issue(
                category="mcp_tools",
                severity=SeverityLevel.MEDIUM,
                message="MCP tool integration tests not found",
                suggestion="Create integration tests for MCP tools"
            )
            
            return {
                'success': False,
                'tests_run': 0,
                'missing_tests': True
            }
    
    async def _test_mcp_error_handling(self) -> Dict[str, Any]:
        """Test MCP error handling and protocol compliance."""
        logger.info("Testing MCP error handling")
        
        # This would test error scenarios in MCP tools
        # For now, we'll check if error handling patterns exist in the code
        
        error_handling_patterns = [
            'try:',
            'except',
            'raise',
            'ValidationError',
            'AuthenticationError'
        ]
        
        handlers_file = self.project_root / 'mcp_task_orchestrator' / 'mcp_request_handlers.py'
        
        if handlers_file.exists():
            with open(handlers_file, 'r') as f:
                content = f.read()
            
            patterns_found = sum(1 for pattern in error_handling_patterns if pattern in content)
            success = patterns_found >= 3  # At least basic error handling
            
            if not success:
                self._add_issue(
                    category="mcp_error_handling",
                    severity=SeverityLevel.HIGH,
                    message="Insufficient error handling patterns in MCP handlers",
                    suggestion="Add comprehensive error handling to MCP tool implementations"
                )
            
            return {
                'success': success,
                'tests_run': 1,
                'patterns_found': patterns_found
            }
        
        return {'success': False, 'tests_run': 0}
    
    async def _test_mcp_protocol_compliance(self) -> Dict[str, Any]:
        """Test MCP protocol compliance."""
        logger.info("Testing MCP protocol compliance")
        
        # Check for JSON-RPC compliance patterns
        compliance_patterns = [
            'jsonrpc',
            'method',
            'params',
            'result',
            'error',
            'id'
        ]
        
        server_file = self.project_root / 'mcp_task_orchestrator' / 'server.py'
        
        if server_file.exists():
            with open(server_file, 'r') as f:
                content = f.read().lower()
            
            patterns_found = sum(1 for pattern in compliance_patterns if pattern in content)
            success = patterns_found >= 4  # Basic JSON-RPC compliance
            
            if not success:
                self._add_issue(
                    category="mcp_protocol",
                    severity=SeverityLevel.HIGH,
                    message="Insufficient MCP protocol compliance patterns",
                    suggestion="Ensure MCP server follows JSON-RPC protocol specifications"
                )
            
            return {
                'success': success,
                'tests_run': 1,
                'patterns_found': patterns_found
            }
        
        return {'success': False, 'tests_run': 0}
    
    async def _test_database_integration(self) -> Dict[str, Any]:
        """Test database integration and persistence."""
        logger.info("Testing database integration")
        
        db_results = {
            'connection_test': False,
            'migration_test': False,
            'crud_operations': False,
            'transaction_handling': False,
            'tests_run': 0
        }
        
        if not self.database_test_required:
            logger.info("Database testing skipped - not required")
            return db_results
        
        try:
            # Run database integration tests
            db_test_paths = [
                'tests/integration/test_database.py',
                'tests/integration/test_persistence.py',
                'tests/integration/test_db_integration.py'
            ]
            
            tests_run = 0
            for test_path in db_test_paths:
                full_path = self.project_root / test_path
                if full_path.exists():
                    cmd = [
                        'pytest',
                        str(full_path),
                        '--tb=short',
                        '-v'
                    ]
                    
                    result = await self._run_tool(cmd)
                    tests_run += 1
                    
                    if result.success:
                        # Parse specific test results based on test names
                        if 'connection' in test_path:
                            db_results['connection_test'] = True
                        elif 'migration' in test_path:
                            db_results['migration_test'] = True
                        elif 'persistence' in test_path or 'crud' in result.output.lower():
                            db_results['crud_operations'] = True
            
            db_results['tests_run'] = tests_run
            
            if tests_run == 0:
                self._add_issue(
                    category="database_integration",
                    severity=SeverityLevel.HIGH,
                    message="No database integration tests found",
                    suggestion="Create database integration tests for CRUD operations and connections"
                )
            
        except Exception as e:
            logger.error(f"Database integration testing failed: {e}")
            self._add_issue(
                category="database_integration",
                severity=SeverityLevel.HIGH,
                message=f"Database integration testing failed: {str(e)}",
                suggestion="Check database configuration and test implementation"
            )
        
        return db_results
    
    async def _test_security_integration(self) -> Dict[str, Any]:
        """Test security framework integration with all components."""
        logger.info("Testing security integration")
        
        security_results = {
            'authentication_integration': False,
            'authorization_integration': False,
            'input_validation_integration': False,
            'error_sanitization_integration': False,
            'tests_run': 0
        }
        
        try:
            # Check if security tests exist and run them
            security_test_paths = [
                'tests/security/',
                'tests/integration/test_security_integration.py'
            ]
            
            tests_run = 0
            for test_path in security_test_paths:
                full_path = self.project_root / test_path
                if full_path.exists():
                    if full_path.is_dir():
                        cmd = [
                            'pytest',
                            str(full_path),
                            '--tb=short',
                            '-k', 'integration',
                            '-v'
                        ]
                    else:
                        cmd = [
                            'pytest',
                            str(full_path),
                            '--tb=short',
                            '-v'
                        ]
                    
                    result = await self._run_tool(cmd)
                    tests_run += 1
                    
                    if result.success:
                        # Analyze output for security integration patterns
                        output_lower = result.output.lower()
                        if 'auth' in output_lower:
                            security_results['authentication_integration'] = True
                        if 'permission' in output_lower or 'authorization' in output_lower:
                            security_results['authorization_integration'] = True
                        if 'validation' in output_lower:
                            security_results['input_validation_integration'] = True
                        if 'sanitiz' in output_lower or 'error' in output_lower:
                            security_results['error_sanitization_integration'] = True
            
            security_results['tests_run'] = tests_run
            
            if tests_run == 0:
                self._add_issue(
                    category="security_integration",
                    severity=SeverityLevel.HIGH,
                    message="No security integration tests found",
                    suggestion="Create security integration tests for authentication, authorization, and validation"
                )
            
        except Exception as e:
            logger.error(f"Security integration testing failed: {e}")
            self._add_issue(
                category="security_integration",
                severity=SeverityLevel.HIGH,
                message=f"Security integration testing failed: {str(e)}",
                suggestion="Check security framework integration and test implementation"
            )
        
        return security_results
    
    async def _test_end_to_end_workflows(self) -> Dict[str, Any]:
        """Test complete end-to-end user workflows."""
        logger.info("Testing end-to-end workflows")
        
        e2e_results = {
            'task_creation_workflow': False,
            'task_execution_workflow': False,
            'task_completion_workflow': False,
            'error_recovery_workflow': False,
            'tests_run': 0
        }
        
        if not self.e2e_test_required:
            logger.info("E2E testing skipped - not required")
            return e2e_results
        
        try:
            # Look for E2E test files
            e2e_test_paths = [
                'tests/integration/test_e2e_workflow.py',
                'tests/integration/test_complete_workflow.py',
                'tests/e2e/'
            ]
            
            tests_run = 0
            for test_path in e2e_test_paths:
                full_path = self.project_root / test_path
                if full_path.exists():
                    if full_path.is_dir():
                        cmd = [
                            'pytest',
                            str(full_path),
                            '--tb=short',
                            '-v',
                            f'--timeout={self.test_timeout * 60}'
                        ]
                    else:
                        cmd = [
                            'pytest',
                            str(full_path),
                            '--tb=short',
                            '-v',
                            f'--timeout={self.test_timeout * 60}'
                        ]
                    
                    result = await self._run_tool(cmd)
                    tests_run += 1
                    
                    if result.success:
                        # Analyze output for workflow patterns
                        output_lower = result.output.lower()
                        if 'create' in output_lower and 'task' in output_lower:
                            e2e_results['task_creation_workflow'] = True
                        if 'execute' in output_lower and 'task' in output_lower:
                            e2e_results['task_execution_workflow'] = True
                        if 'complete' in output_lower and 'task' in output_lower:
                            e2e_results['task_completion_workflow'] = True
                        if 'error' in output_lower and 'recover' in output_lower:
                            e2e_results['error_recovery_workflow'] = True
            
            e2e_results['tests_run'] = tests_run
            
            if tests_run == 0:
                self._add_issue(
                    category="e2e_workflows",
                    severity=SeverityLevel.MEDIUM,
                    message="No end-to-end workflow tests found",
                    suggestion="Create E2E tests for complete user workflows"
                )
            
        except Exception as e:
            logger.error(f"E2E workflow testing failed: {e}")
            self._add_issue(
                category="e2e_workflows",
                severity=SeverityLevel.MEDIUM,
                message=f"E2E workflow testing failed: {str(e)}",
                suggestion="Check E2E test implementation and workflow coverage"
            )
        
        return e2e_results
    
    async def _test_component_boundaries(self) -> Dict[str, Any]:
        """Test Clean Architecture component boundary compliance."""
        logger.info("Testing component boundaries")
        
        boundary_results = {
            'dependency_direction': True,
            'layer_isolation': True,
            'interface_compliance': True,
            'violations': []
        }
        
        try:
            # Analyze import dependencies to check architecture compliance
            python_files = self._get_python_files()
            
            for file_path in python_files:
                relative_path = str(file_path.relative_to(self.project_root))
                
                # Check for dependency rule violations
                if '/domain/' in relative_path:
                    # Domain layer should not depend on outer layers
                    violations = await self._check_domain_dependencies(file_path)
                    if violations:
                        boundary_results['dependency_direction'] = False
                        boundary_results['violations'].extend(violations)
                
                elif '/application/' in relative_path:
                    # Application layer should not depend on infrastructure
                    violations = await self._check_application_dependencies(file_path)
                    if violations:
                        boundary_results['dependency_direction'] = False
                        boundary_results['violations'].extend(violations)
            
            if boundary_results['violations']:
                for violation in boundary_results['violations']:
                    self._add_issue(
                        category="architecture_boundary",
                        severity=SeverityLevel.HIGH,
                        message=violation['message'],
                        file_path=violation['file'],
                        suggestion="Refactor to follow Clean Architecture dependency rules"
                    )
        
        except Exception as e:
            logger.error(f"Component boundary testing failed: {e}")
            self._add_issue(
                category="architecture_boundary",
                severity=SeverityLevel.MEDIUM,
                message=f"Component boundary testing failed: {str(e)}",
                suggestion="Check architecture compliance and dependency analysis"
            )
        
        return boundary_results
    
    async def _check_domain_dependencies(self, file_path: Path) -> List[Dict[str, str]]:
        """Check domain layer dependencies for violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Domain should not import from infrastructure or presentation
            forbidden_imports = [
                'from mcp_task_orchestrator.infrastructure',
                'from mcp_task_orchestrator.presentation',
                'import mcp_task_orchestrator.infrastructure',
                'import mcp_task_orchestrator.presentation'
            ]
            
            for forbidden in forbidden_imports:
                if forbidden in content:
                    violations.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'message': f"Domain layer imports forbidden dependency: {forbidden}"
                    })
        
        except Exception as e:
            logger.warning(f"Could not check dependencies for {file_path}: {e}")
        
        return violations
    
    async def _check_application_dependencies(self, file_path: Path) -> List[Dict[str, str]]:
        """Check application layer dependencies for violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Application should not import from presentation (but can import infrastructure interfaces)
            forbidden_imports = [
                'from mcp_task_orchestrator.presentation',
                'import mcp_task_orchestrator.presentation'
            ]
            
            for forbidden in forbidden_imports:
                if forbidden in content:
                    violations.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'message': f"Application layer imports forbidden dependency: {forbidden}"
                    })
        
        except Exception as e:
            logger.warning(f"Could not check dependencies for {file_path}: {e}")
        
        return violations
    
    async def _test_error_handling_integration(self) -> Dict[str, Any]:
        """Test error handling integration across components."""
        logger.info("Testing error handling integration")
        
        error_handling_results = {
            'exception_handling': True,
            'error_propagation': True,
            'recovery_mechanisms': True,
            'error_logging': True,
            'issues': []
        }
        
        try:
            # Look for error handling integration tests
            error_test_paths = [
                'tests/integration/test_error_handling.py',
                'tests/error_handling/'
            ]
            
            tests_found = False
            for test_path in error_test_paths:
                full_path = self.project_root / test_path
                if full_path.exists():
                    tests_found = True
                    cmd = [
                        'pytest',
                        str(full_path),
                        '--tb=short',
                        '-v'
                    ]
                    
                    result = await self._run_tool(cmd)
                    
                    if not result.success:
                        error_handling_results['exception_handling'] = False
                        self._add_issue(
                            category="error_handling_integration",
                            severity=SeverityLevel.HIGH,
                            message="Error handling integration tests failed",
                            suggestion="Fix error handling integration issues"
                        )
            
            if not tests_found:
                self._add_issue(
                    category="error_handling_integration",
                    severity=SeverityLevel.MEDIUM,
                    message="No error handling integration tests found",
                    suggestion="Create integration tests for error handling and recovery"
                )
        
        except Exception as e:
            logger.error(f"Error handling integration testing failed: {e}")
            self._add_issue(
                category="error_handling_integration",
                severity=SeverityLevel.MEDIUM,
                message=f"Error handling integration testing failed: {str(e)}",
                suggestion="Check error handling test implementation"
            )
        
        return error_handling_results
    
    def _get_integration_test_files(self) -> List[Path]:
        """Get all integration test files."""
        integration_files = []
        integration_dirs = [
            self.project_root / 'tests' / 'integration',
            self.project_root / 'tests' / 'e2e'
        ]
        
        for test_dir in integration_dirs:
            if test_dir.exists():
                integration_files.extend(test_dir.glob('**/*.py'))
        
        return integration_files