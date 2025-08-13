"""
Multi-Stage Validation Pipeline Orchestrator

Manages the execution of all validation stages with proper error handling,
reporting, and remediation guidance. Each stage must pass completely before
the next stage executes.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import uuid

from .stage_1_syntax import SyntaxValidationStage
from .stage_2_unit import UnitTestStage
from .stage_3_integration import IntegrationTestStage
from .stage_4_security_performance import SecurityPerformanceStage
from .stage_5_production import ProductionReadinessStage
from .models import PipelineResult, ValidationResult, ValidationStatus, PipelineConfig


logger = logging.getLogger(__name__)


class ValidationPipelineOrchestrator:
    """
    Orchestrates the 5-stage validation pipeline with comprehensive
    error handling, reporting, and remediation guidance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.pipeline_id = str(uuid.uuid4())
        self.project_root = Path(self.config.get('project_root', '.')).resolve()
        
        # Initialize pipeline result
        self.pipeline_result = PipelineResult(
            pipeline_id=self.pipeline_id,
            start_time=datetime.now(),
            configuration=self.config,
            environment_info=self._collect_environment_info()
        )
        
        # Initialize stages
        self.stages = self._initialize_stages()
        
        # Pipeline state management
        self.pipeline_state = {
            'started_at': None,
            'current_stage': None,
            'completed_stages': [],
            'failed_stage': None,
            'total_duration': None,
            'stage_results': {},
            'can_resume': False,
            'resume_from_stage': None
        }
        
        # Reporting and output configuration
        self.output_directory = Path(self.config.get('output_directory', 'validation_results'))
        self.output_directory.mkdir(exist_ok=True)
        self.fail_fast = self.config.get('fail_fast', True)
        self.parallel_execution = self.config.get('parallel_execution', False)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default pipeline configuration."""
        return {
            'project_root': '.',
            'output_directory': 'validation_results',
            'fail_fast': True,
            'parallel_execution': False,
            'timeout_minutes': 30,
            
            # Stage-specific configurations
            'syntax_config': {
                'enabled': True,
                'timeout_minutes': 5,
                'fail_on_error': True
            },
            'unit_config': {
                'enabled': True,
                'timeout_minutes': 10,
                'min_coverage': 85,
                'fail_on_coverage': True,
                'coverage_targets': {
                    'overall_minimum': 85,
                    'security_components': 95,
                    'domain_layer': 90,
                    'mcp_handlers': 85
                }
            },
            'integration_config': {
                'enabled': True,
                'timeout_minutes': 15,
                'database_test_required': True,
                'mcp_test_required': True,
                'e2e_test_required': True
            },
            'security_performance_config': {
                'enabled': True,
                'timeout_minutes': 20,
                'attack_vector_tests': True,
                'performance_tests': True,
                'performance_targets': {
                    'api_key_validation_ms': 100,
                    'input_validation_ms': 50,
                    'database_operations_ms': 200,
                    'mcp_tool_execution_ms': 1000
                }
            },
            'production_config': {
                'enabled': True,
                'timeout_minutes': 10,
                'deployment_targets': ['docker', 'pip'],
                'monitoring_required': True,
                'security_audit_required': True,
                'production_environment': 'production'
            }
        }
    
    def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect environment information for reporting."""
        import platform
        import os
        
        env_info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'hostname': platform.node(),
            'user': os.getenv('USER', 'unknown'),
            'working_directory': str(Path.cwd()),
            'pipeline_version': '2.0.0'
        }
        
        # Try to get git information
        try:
            import subprocess
            
            # Get git branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                env_info['git_branch'] = result.stdout.strip()
            
            # Get git commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                env_info['git_commit'] = result.stdout.strip()[:8]
        
        except Exception:
            logger.debug("Could not collect git information")
        
        return env_info
    
    def _initialize_stages(self) -> List[Any]:
        """Initialize all validation stages with proper configuration."""
        return [
            SyntaxValidationStage(self.config['syntax_config']),
            UnitTestStage(self.config['unit_config']),
            IntegrationTestStage(self.config['integration_config']),
            SecurityPerformanceStage(self.config['security_performance_config']),
            ProductionReadinessStage(self.config['production_config'])
        ]
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Execute the complete 5-stage validation pipeline.
        
        Returns:
            Complete pipeline execution results with detailed reporting
        """
        logger.info(f"Starting validation pipeline {self.pipeline_id}")
        self.pipeline_state['started_at'] = datetime.now()
        self.pipeline_result.start_time = self.pipeline_state['started_at']
        
        try:
            # Execute all stages sequentially
            for stage_num, stage in enumerate(self.stages, 1):
                if not stage.enabled:
                    logger.info(f"Stage {stage_num} ({stage.stage_name}) is disabled - skipping")
                    continue
                
                self.pipeline_state['current_stage'] = stage_num
                logger.info(f"Executing Stage {stage_num}: {stage.stage_name}")
                
                # Execute stage with comprehensive error handling
                stage_result = await self._execute_stage(stage, stage_num)
                self.pipeline_result.stages.append(stage_result)
                
                # Check if stage passed
                if not stage_result.passed:
                    if self.fail_fast:
                        # Stage failed - stop pipeline and generate remediation
                        self.pipeline_state['failed_stage'] = stage_num
                        self.pipeline_result.overall_status = ValidationStatus.FAILED
                        return await self._handle_stage_failure(stage, stage_num, stage_result)
                    else:
                        # Continue to next stage even if this one failed
                        logger.warning(f"Stage {stage_num} failed but continuing due to fail_fast=False")
                
                # Stage passed or we're continuing despite failure
                self.pipeline_state['completed_stages'].append(stage_num)
                self.pipeline_state['stage_results'][stage_num] = stage_result.to_dict()
                
                logger.info(f"Stage {stage_num} completed with status: {stage_result.status}")
            
            # All stages completed - determine overall status
            self.pipeline_result.overall_status = self._determine_overall_status()
            return await self._generate_pipeline_report()
            
        except Exception as e:
            logger.exception(f"Pipeline execution failed with exception: {e}")
            return await self._handle_pipeline_exception(e)
        
        finally:
            self.pipeline_result.end_time = datetime.now()
            self.pipeline_state['total_duration'] = self.pipeline_result.duration
    
    async def run_single_stage(self, stage_number: int) -> Dict[str, Any]:
        """Run a single validation stage for debugging/development purposes."""
        if not 1 <= stage_number <= len(self.stages):
            raise ValueError(f"Invalid stage number: {stage_number}. Must be between 1 and {len(self.stages)}")
        
        logger.info(f"Running single stage {stage_number}")
        stage = self.stages[stage_number - 1]
        
        if not stage.enabled:
            return {
                'stage_number': stage_number,
                'status': 'skipped',
                'message': f"Stage {stage_number} is disabled"
            }
        
        # Execute the single stage
        stage_result = await self._execute_stage(stage, stage_number)
        
        # Generate report for single stage
        report = await self._generate_single_stage_report(stage_result, stage_number)
        
        return report
    
    async def run_from_stage(self, start_stage: int) -> Dict[str, Any]:
        """Resume pipeline execution from a specific stage."""
        if not 1 <= start_stage <= len(self.stages):
            raise ValueError(f"Invalid start stage: {start_stage}. Must be between 1 and {len(self.stages)}")
        
        logger.info(f"Resuming pipeline from stage {start_stage}")
        self.pipeline_state['resume_from_stage'] = start_stage
        
        # Mark previous stages as completed (assuming they passed previously)
        for i in range(1, start_stage):
            self.pipeline_state['completed_stages'].append(i)
        
        # Execute remaining stages
        for stage_num in range(start_stage, len(self.stages) + 1):
            stage = self.stages[stage_num - 1]
            
            if not stage.enabled:
                logger.info(f"Stage {stage_num} ({stage.stage_name}) is disabled - skipping")
                continue
            
            self.pipeline_state['current_stage'] = stage_num
            logger.info(f"Executing Stage {stage_num}: {stage.stage_name}")
            
            # Execute stage
            stage_result = await self._execute_stage(stage, stage_num)
            self.pipeline_result.stages.append(stage_result)
            
            # Check if stage passed
            if not stage_result.passed and self.fail_fast:
                self.pipeline_state['failed_stage'] = stage_num
                self.pipeline_result.overall_status = ValidationStatus.FAILED
                return await self._handle_stage_failure(stage, stage_num, stage_result)
            
            self.pipeline_state['completed_stages'].append(stage_num)
            self.pipeline_state['stage_results'][stage_num] = stage_result.to_dict()
        
        # All remaining stages completed
        self.pipeline_result.overall_status = self._determine_overall_status()
        return await self._generate_pipeline_report()
    
    async def _execute_stage(self, stage: Any, stage_number: int) -> ValidationResult:
        """Execute a single validation stage with error handling and timeout."""
        stage_start_time = time.time()
        
        try:
            logger.info(f"Starting Stage {stage_number}: {stage.stage_name}")
            
            # Execute the stage with timeout
            stage_result = await stage.run()
            
            # Log stage completion
            execution_time = time.time() - stage_start_time
            logger.info(f"Stage {stage_number} completed in {execution_time:.2f}s with status: {stage_result.status}")
            
            # Add execution metadata
            if stage_result.metrics:
                stage_result.metrics.execution_time = timedelta(seconds=execution_time)
            
            return stage_result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - stage_start_time
            logger.error(f"Stage {stage_number} timed out after {execution_time:.2f}s")
            
            # Create a failed result for timeout
            failed_result = ValidationResult(
                stage_id=stage_number,
                stage_name=stage.stage_name,
                status=ValidationStatus.ERROR,
                start_time=datetime.now() - timedelta(seconds=execution_time),
                end_time=datetime.now(),
                error_message=f"Stage timed out after {execution_time:.2f} seconds"
            )
            
            return failed_result
            
        except Exception as e:
            execution_time = time.time() - stage_start_time
            logger.exception(f"Stage {stage_number} failed with exception: {e}")
            
            # Create a failed result for exception
            failed_result = ValidationResult(
                stage_id=stage_number,
                stage_name=stage.stage_name,
                status=ValidationStatus.ERROR,
                start_time=datetime.now() - timedelta(seconds=execution_time),
                end_time=datetime.now(),
                error_message=f"Stage failed with exception: {str(e)}"
            )
            
            return failed_result
    
    def _determine_overall_status(self) -> ValidationStatus:
        """Determine the overall pipeline status based on stage results."""
        if not self.pipeline_result.stages:
            return ValidationStatus.PENDING
        
        # Check for any failed stages
        failed_stages = [stage for stage in self.pipeline_result.stages 
                        if stage.status in [ValidationStatus.FAILED, ValidationStatus.ERROR]]
        
        if failed_stages:
            return ValidationStatus.FAILED
        
        # Check for any stages with warnings
        warning_stages = [stage for stage in self.pipeline_result.stages 
                         if stage.status == ValidationStatus.WARNING]
        
        if warning_stages:
            return ValidationStatus.WARNING
        
        # All stages passed
        return ValidationStatus.PASSED
    
    async def _handle_stage_failure(self, stage: Any, stage_number: int, stage_result: ValidationResult) -> Dict[str, Any]:
        """Handle stage failure with remediation guidance."""
        logger.error(f"Stage {stage_number} ({stage.stage_name}) failed")
        
        failure_report = {
            'pipeline_id': self.pipeline_id,
            'status': 'FAILED',
            'failed_stage': stage_number,
            'failed_stage_name': stage.stage_name,
            'failure_time': datetime.now().isoformat(),
            'stage_result': stage_result.to_dict(),
            'remediation_guidance': await self._generate_remediation_guidance(stage_result),
            'resume_instructions': self._generate_resume_instructions(stage_number),
            'pipeline_state': self.pipeline_state
        }
        
        # Save failure report
        await self._save_pipeline_report(failure_report, 'failure_report.json')
        
        return failure_report
    
    async def _handle_pipeline_exception(self, exception: Exception) -> Dict[str, Any]:
        """Handle pipeline-level exceptions."""
        error_report = {
            'pipeline_id': self.pipeline_id,
            'status': 'ERROR',
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'error_time': datetime.now().isoformat(),
            'pipeline_state': self.pipeline_state,
            'completed_stages': self.pipeline_state['completed_stages'],
            'remediation_guidance': {
                'error_type': 'Pipeline Exception',
                'immediate_actions': [
                    'Check the error message above for specific details',
                    'Verify your environment and dependencies',
                    'Check project configuration and permissions',
                    'Try running individual stages to isolate the issue'
                ],
                'recovery_steps': [
                    'Fix the underlying issue causing the exception',
                    'Resume pipeline from the last successful stage',
                    'Run validation on fixed components'
                ]
            }
        }
        
        # Save error report
        await self._save_pipeline_report(error_report, 'error_report.json')
        
        return error_report
    
    async def _generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline execution report."""
        pipeline_report = {
            'pipeline_id': self.pipeline_id,
            'status': self.pipeline_result.overall_status.value,
            'started_at': self.pipeline_result.start_time.isoformat(),
            'completed_at': self.pipeline_result.end_time.isoformat() if self.pipeline_result.end_time else None,
            'total_duration_seconds': self.pipeline_result.duration.total_seconds() if self.pipeline_result.duration else None,
            'environment_info': self.pipeline_result.environment_info,
            'configuration': self.pipeline_result.configuration,
            
            # Stage summaries
            'stage_summary': {
                'total_stages': len(self.stages),
                'completed_stages': len([s for s in self.pipeline_result.stages if s.passed]),
                'failed_stages': len([s for s in self.pipeline_result.stages if not s.passed]),
                'total_issues': self.pipeline_result.total_issues,
                'critical_issues': self.pipeline_result.critical_issues_count
            },
            
            # Detailed stage results
            'stages': [stage.to_dict() for stage in self.pipeline_result.stages],
            
            # Overall results and recommendations
            'overall_results': await self._generate_overall_results(),
            'recommendations': await self._generate_recommendations(),
            'next_steps': await self._generate_next_steps()
        }
        
        # Save comprehensive report
        await self._save_pipeline_report(pipeline_report, 'pipeline_report.json')
        await self._save_pipeline_report(pipeline_report, f'pipeline_report_{self.pipeline_id[:8]}.json')
        
        return pipeline_report
    
    async def _generate_single_stage_report(self, stage_result: ValidationResult, stage_number: int) -> Dict[str, Any]:
        """Generate report for single stage execution."""
        stage_report = {
            'pipeline_id': self.pipeline_id,
            'stage_number': stage_number,
            'stage_name': stage_result.stage_name,
            'status': stage_result.status.value,
            'passed': stage_result.passed,
            'execution_time': stage_result.duration.total_seconds() if stage_result.duration else None,
            'started_at': stage_result.start_time.isoformat(),
            'completed_at': stage_result.end_time.isoformat() if stage_result.end_time else None,
            'issues_count': len(stage_result.issues),
            'critical_issues_count': len(stage_result.critical_issues),
            'high_issues_count': len(stage_result.high_issues),
            'detailed_results': stage_result.to_dict(),
            'environment_info': self.pipeline_result.environment_info
        }
        
        if not stage_result.passed:
            stage_report['remediation_guidance'] = await self._generate_remediation_guidance(stage_result)
        
        # Save single stage report
        await self._save_pipeline_report(stage_report, f'stage_{stage_number}_report.json')
        
        return stage_report
    
    async def _generate_remediation_guidance(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate specific remediation guidance based on stage failures."""
        guidance = {
            'stage_name': stage_result.stage_name,
            'stage_id': stage_result.stage_id,
            'failure_summary': f"Stage {stage_result.stage_id} failed with {len(stage_result.issues)} issues",
            'immediate_actions': [],
            'detailed_fixes': [],
            'prevention_measures': [],
            'estimated_fix_time': 'Unknown'
        }
        
        # Generate stage-specific remediation guidance
        if stage_result.stage_id == 1:  # Syntax Stage
            guidance.update(await self._get_syntax_remediation(stage_result))
        elif stage_result.stage_id == 2:  # Unit Test Stage
            guidance.update(await self._get_unit_test_remediation(stage_result))
        elif stage_result.stage_id == 3:  # Integration Stage
            guidance.update(await self._get_integration_remediation(stage_result))
        elif stage_result.stage_id == 4:  # Security & Performance Stage
            guidance.update(await self._get_security_performance_remediation(stage_result))
        elif stage_result.stage_id == 5:  # Production Readiness Stage
            guidance.update(await self._get_production_remediation(stage_result))
        
        return guidance
    
    async def _get_syntax_remediation(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate remediation guidance for syntax validation failures."""
        return {
            'immediate_actions': [
                'Fix all Python syntax errors',
                'Run ruff check . --fix to auto-fix linting issues',
                'Run mypy . to fix type hint issues',
                'Check import statements for missing dependencies'
            ],
            'detailed_fixes': [
                'Review syntax error details in the stage artifacts',
                'Use IDE/editor with Python syntax highlighting',
                'Run python -m py_compile <file> to check individual files'
            ],
            'prevention_measures': [
                'Set up pre-commit hooks with ruff and mypy',
                'Configure IDE with Python linting and type checking',
                'Add continuous integration checks for syntax'
            ],
            'estimated_fix_time': '30-60 minutes'
        }
    
    async def _get_unit_test_remediation(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate remediation guidance for unit test failures."""
        return {
            'immediate_actions': [
                'Fix failing unit tests',
                'Increase test coverage to meet targets',
                'Review test structure and organization',
                'Add missing test files for uncovered components'
            ],
            'detailed_fixes': [
                'Run pytest with -vvv for detailed test failure information',
                'Use pytest --cov to identify coverage gaps',
                'Review test quality issues identified in artifacts'
            ],
            'prevention_measures': [
                'Implement test-driven development practices',
                'Set up automated test coverage reporting',
                'Add coverage requirements to CI/CD pipeline'
            ],
            'estimated_fix_time': '2-4 hours'
        }
    
    async def _get_integration_remediation(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate remediation guidance for integration test failures."""
        return {
            'immediate_actions': [
                'Fix component integration issues',
                'Ensure MCP protocol compliance',
                'Verify database integration works correctly',
                'Test end-to-end workflows'
            ],
            'detailed_fixes': [
                'Review integration test failures in detail',
                'Check MCP tool registration and execution',
                'Verify database connections and operations',
                'Test component boundary compliance'
            ],
            'prevention_measures': [
                'Add comprehensive integration test suite',
                'Set up test environment automation',
                'Implement integration test CI/CD pipeline'
            ],
            'estimated_fix_time': '3-6 hours'
        }
    
    async def _get_security_performance_remediation(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate remediation guidance for security and performance failures."""
        return {
            'immediate_actions': [
                'Fix security vulnerabilities immediately',
                'Implement missing attack vector defenses',
                'Optimize performance bottlenecks',
                'Configure authentication and authorization properly'
            ],
            'detailed_fixes': [
                'Review security test failures and implement fixes',
                'Add input validation and sanitization',
                'Implement rate limiting and brute force protection',
                'Optimize database queries and API responses'
            ],
            'prevention_measures': [
                'Regular security audits and penetration testing',
                'Performance monitoring and alerting',
                'Security-focused code reviews',
                'Automated security testing in CI/CD'
            ],
            'estimated_fix_time': '4-8 hours'
        }
    
    async def _get_production_remediation(self, stage_result: ValidationResult) -> Dict[str, Any]:
        """Generate remediation guidance for production readiness failures."""
        return {
            'immediate_actions': [
                'Complete production configuration',
                'Set up monitoring and logging',
                'Configure deployment processes',
                'Complete documentation and backup procedures'
            ],
            'detailed_fixes': [
                'Set all required environment variables',
                'Configure production-grade logging',
                'Set up health checks and monitoring',
                'Create deployment and recovery documentation'
            ],
            'prevention_measures': [
                'Use infrastructure as code',
                'Implement automated deployment testing',
                'Regular disaster recovery testing',
                'Production readiness checklists'
            ],
            'estimated_fix_time': '2-6 hours'
        }
    
    def _generate_resume_instructions(self, failed_stage: int) -> Dict[str, Any]:
        """Generate instructions for resuming the pipeline."""
        return {
            'failed_stage': failed_stage,
            'resume_command': f'python -m tools.validation.pipeline_orchestrator --resume-from {failed_stage}',
            'alternative_commands': {
                'single_stage': f'python -m tools.validation.pipeline_orchestrator --stage {failed_stage}',
                'from_beginning': 'python -m tools.validation.pipeline_orchestrator --run-full'
            },
            'prerequisites': [
                'Fix all issues identified in the remediation guidance',
                'Verify fixes by running individual components',
                'Ensure all dependencies are properly installed'
            ]
        }
    
    async def _generate_overall_results(self) -> Dict[str, Any]:
        """Generate overall pipeline results summary."""
        total_stages = len(self.pipeline_result.stages)
        passed_stages = len([s for s in self.pipeline_result.stages if s.passed])
        
        return {
            'pipeline_passed': self.pipeline_result.passed,
            'overall_status': self.pipeline_result.overall_status.value,
            'stages_passed': passed_stages,
            'stages_total': total_stages,
            'success_rate': (passed_stages / total_stages) if total_stages > 0 else 0,
            'total_issues_found': self.pipeline_result.total_issues,
            'critical_issues_found': self.pipeline_result.critical_issues_count,
            'pipeline_quality_score': self._calculate_quality_score()
        }
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score based on pipeline results."""
        if not self.pipeline_result.stages:
            return 0.0
        
        # Base score from stage completion
        passed_stages = len([s for s in self.pipeline_result.stages if s.passed])
        total_stages = len(self.pipeline_result.stages)
        completion_score = (passed_stages / total_stages) * 100 if total_stages > 0 else 0
        
        # Penalty for issues
        total_issues = self.pipeline_result.total_issues
        critical_issues = self.pipeline_result.critical_issues_count
        
        issue_penalty = min(total_issues * 2 + critical_issues * 5, 50)  # Cap at 50 points
        
        quality_score = max(completion_score - issue_penalty, 0)
        
        return round(quality_score, 2)
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on pipeline results."""
        recommendations = []
        
        if self.pipeline_result.overall_status == ValidationStatus.PASSED:
            recommendations.extend([
                "✅ All validation stages passed successfully",
                "Consider setting up automated pipeline execution in CI/CD",
                "Review any warnings to further improve code quality",
                "Schedule regular validation runs to maintain quality"
            ])
        else:
            recommendations.extend([
                "❌ Pipeline validation failed - review failures before production deployment",
                "Fix all critical and high-severity issues immediately",
                "Consider implementing the remediation guidance provided",
                "Re-run the validation pipeline after fixes are implemented"
            ])
        
        # Add specific recommendations based on stage results
        for stage in self.pipeline_result.stages:
            if stage.critical_issues:
                recommendations.append(f"🚨 Critical issues in {stage.stage_name} require immediate attention")
        
        return recommendations
    
    async def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on pipeline results."""
        next_steps = []
        
        if self.pipeline_result.passed:
            next_steps.extend([
                "Pipeline validation successful - system is ready for production",
                "Deploy to production environment following deployment procedures",
                "Set up monitoring and alerting for production environment",
                "Schedule regular validation runs to maintain quality"
            ])
        else:
            failed_stages = self.pipeline_result.failed_stages
            if failed_stages:
                next_steps.extend([
                    f"Fix issues in failed stages: {', '.join([s.stage_name for s in failed_stages])}",
                    "Review detailed remediation guidance for each failed stage",
                    f"Resume pipeline validation from stage {failed_stages[0].stage_id}",
                    "Verify fixes before attempting production deployment"
                ])
        
        return next_steps
    
    async def _save_pipeline_report(self, report: Dict[str, Any], filename: str) -> None:
        """Save pipeline report to output directory."""
        try:
            report_path = self.output_directory / filename
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Pipeline report saved to {report_path}")
        
        except Exception as e:
            logger.error(f"Failed to save pipeline report {filename}: {e}")


# CLI interface for the pipeline orchestrator
async def main():
    """Main entry point for CLI execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Stage Validation Pipeline')
    parser.add_argument('--run-full', action='store_true', 
                       help='Run the complete validation pipeline')
    parser.add_argument('--stage', type=int, metavar='N',
                       help='Run a single stage (1-5)')
    parser.add_argument('--resume-from', type=int, metavar='N',
                       help='Resume pipeline from stage N')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    parser.add_argument('--output-dir', type=str, default='validation_results',
                       help='Output directory for reports')
    parser.add_argument('--fail-fast', action='store_true', default=True,
                       help='Stop on first stage failure (default: True)')
    parser.add_argument('--no-fail-fast', action='store_false', dest='fail_fast',
                       help='Continue pipeline even if stages fail')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override config with CLI arguments
    config['output_directory'] = args.output_dir
    config['fail_fast'] = args.fail_fast
    
    # Initialize orchestrator
    orchestrator = ValidationPipelineOrchestrator(config)
    
    try:
        # Execute based on arguments
        if args.run_full:
            logger.info("Starting full pipeline validation")
            result = await orchestrator.run_full_pipeline()
        elif args.stage:
            logger.info(f"Running single stage {args.stage}")
            result = await orchestrator.run_single_stage(args.stage)
        elif args.resume_from:
            logger.info(f"Resuming pipeline from stage {args.resume_from}")
            result = await orchestrator.run_from_stage(args.resume_from)
        else:
            # Default to full pipeline
            logger.info("No specific action specified, running full pipeline")
            result = await orchestrator.run_full_pipeline()
        
        # Print summary
        print("\n=== Pipeline Validation Summary ===")
        print(f"Status: {result.get('status', 'UNKNOWN')}")
        print(f"Pipeline ID: {result.get('pipeline_id', 'N/A')}")
        
        if 'stage_summary' in result:
            summary = result['stage_summary']
            print(f"Stages: {summary['completed_stages']}/{summary['total_stages']} passed")
            print(f"Issues: {summary['total_issues']} total, {summary['critical_issues']} critical")
        
        print(f"\nDetailed reports saved to: {orchestrator.output_directory}")
        
        # Return appropriate exit code
        if result.get('status') == 'PASSED':
            return 0
        else:
            return 1
    
    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")
        return 1


if __name__ == '__main__':
    import asyncio
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)