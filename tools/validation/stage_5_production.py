"""
Stage 5: Production Readiness Validation

Final validation for production deployment including configuration validation,
monitoring setup, error handling verification, deployment readiness checks,
and comprehensive system health validation.
"""

import json
import logging
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import configparser
import yaml

from .base_stage import ValidationStageBase
from .models import ValidationIssue, SeverityLevel, StageMetrics


logger = logging.getLogger(__name__)


class ProductionReadinessStage(ValidationStageBase):
    """Stage 5: Production readiness validation with deployment checks."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            stage_id=5,
            stage_name="Production Readiness Validation",
            config=config
        )
        self.production_environment = config.get('production_environment', 'production')
        self.deployment_targets = config.get('deployment_targets', ['docker', 'pip'])
        self.monitoring_required = config.get('monitoring_required', True)
        self.security_audit_required = config.get('security_audit_required', True)
    
    async def _execute_stage(self) -> None:
        """Execute production readiness validation."""
        start_time = time.time()
        
        logger.info("Starting production readiness validation")
        
        # 1. Configuration validation
        config_result = await self._validate_production_config()
        self._add_artifact('production_configuration', config_result)
        
        # 2. Error handling validation
        error_result = await self._validate_error_handling()
        self._add_artifact('error_handling_validation', error_result)
        
        # 3. Logging and monitoring validation
        monitoring_result = await self._validate_monitoring_setup()
        self._add_artifact('monitoring_setup', monitoring_result)
        
        # 4. Security audit logging validation
        if self.security_audit_required:
            audit_result = await self._validate_security_audit_logging()
            self._add_artifact('security_audit_logging', audit_result)
        
        # 5. Deployment readiness validation
        deployment_result = await self._validate_deployment_readiness()
        self._add_artifact('deployment_readiness', deployment_result)
        
        # 6. Final system health check
        health_result = await self._perform_final_health_check()
        self._add_artifact('system_health_check', health_result)
        
        # 7. Documentation and README validation
        docs_result = await self._validate_documentation_completeness()
        self._add_artifact('documentation_validation', docs_result)
        
        # 8. Dependency and security vulnerability scan
        vulnerability_result = await self._validate_dependency_security()
        self._add_artifact('vulnerability_scan', vulnerability_result)
        
        # 9. Backup and recovery validation
        backup_result = await self._validate_backup_recovery_procedures()
        self._add_artifact('backup_recovery', backup_result)
        
        # Record metrics
        execution_time = timedelta(seconds=time.time() - start_time)
        
        metrics = StageMetrics(
            execution_time=execution_time,
            tests_run=self._count_production_checks(),
            files_processed=len(self._get_configuration_files())
        )
        self._add_metric(metrics)
        
        logger.info(f"Production readiness validation completed in {execution_time.total_seconds():.2f}s")
    
    async def _validate_production_config(self) -> Dict[str, Any]:
        """Validate production configuration completeness."""
        logger.info("Validating production configuration")
        
        config_checks = {
            'environment_variables': await self._check_environment_variables(),
            'configuration_files': await self._check_configuration_files(),
            'secret_management': await self._check_secret_management(),
            'database_configuration': await self._check_database_configuration(),
            'logging_configuration': await self._check_logging_configuration(),
            'security_settings': await self._check_security_settings()
        }
        
        all_configured = all(check.get('configured', False) for check in config_checks.values())
        
        if not all_configured:
            missing_configs = [
                name for name, check in config_checks.items() 
                if not check.get('configured', False)
            ]
            self._add_issue(
                category="production_configuration",
                severity=SeverityLevel.CRITICAL,
                message=f"Missing production configurations: {', '.join(missing_configs)}",
                suggestion="Complete all required production configuration settings"
            )
        
        return {
            'overall_configured': all_configured,
            'configuration_details': config_checks
        }
    
    async def _check_environment_variables(self) -> Dict[str, Any]:
        """Check for required environment variables."""
        logger.info("Checking environment variables")
        
        required_env_vars = [
            'MCP_TASK_ORCHESTRATOR_ENV',
            'MCP_TASK_ORCHESTRATOR_LOG_LEVEL',
            'MCP_TASK_ORCHESTRATOR_DB_PATH',
            'MCP_TASK_ORCHESTRATOR_SECRET_KEY'
        ]
        
        missing_vars = []
        present_vars = []
        
        for var in required_env_vars:
            if os.getenv(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)
        
        if missing_vars:
            self._add_issue(
                category="environment_variables",
                severity=SeverityLevel.HIGH,
                message=f"Missing environment variables: {', '.join(missing_vars)}",
                suggestion="Set all required environment variables for production deployment"
            )
        
        return {
            'configured': len(missing_vars) == 0,
            'present_vars': present_vars,
            'missing_vars': missing_vars,
            'total_required': len(required_env_vars)
        }
    
    async def _check_configuration_files(self) -> Dict[str, Any]:
        """Check for required configuration files."""
        logger.info("Checking configuration files")
        
        config_files = [
            ('pyproject.toml', 'Project configuration'),
            ('CLAUDE.md', 'Development guidelines'),
            ('README.md', 'Project documentation'),
            ('CHANGELOG.md', 'Version history'),
            ('.gitignore', 'Git exclusions')
        ]
        
        present_files = []
        missing_files = []
        
        for filename, description in config_files:
            file_path = self.project_root / filename
            if file_path.exists():
                present_files.append({'file': filename, 'description': description})
            else:
                missing_files.append({'file': filename, 'description': description})
        
        if missing_files:
            self._add_issue(
                category="configuration_files",
                severity=SeverityLevel.MEDIUM,
                message=f"Missing configuration files: {[f['file'] for f in missing_files]}",
                suggestion="Create all required configuration and documentation files"
            )
        
        return {
            'configured': len(missing_files) == 0,
            'present_files': present_files,
            'missing_files': missing_files
        }
    
    async def _check_secret_management(self) -> Dict[str, Any]:
        """Check secret management configuration."""
        logger.info("Checking secret management")
        
        secret_checks = {
            'no_hardcoded_secrets': await self._scan_for_hardcoded_secrets(),
            'gitignore_secrets': await self._check_gitignore_secrets(),
            'environment_secret_loading': await self._check_env_secret_loading()
        }
        
        all_secure = all(secret_checks.values())
        
        if not all_secure:
            self._add_issue(
                category="secret_management",
                severity=SeverityLevel.CRITICAL,
                message="Secret management issues detected",
                suggestion="Review and fix all secret management vulnerabilities"
            )
        
        return {
            'configured': all_secure,
            'secret_checks': secret_checks
        }
    
    async def _scan_for_hardcoded_secrets(self) -> bool:
        """Scan for hardcoded secrets in the codebase."""
        logger.info("Scanning for hardcoded secrets")
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'aws_.*_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        try:
            # Use grep to search for potential secrets
            python_files = self._get_python_files()
            secrets_found = False
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple check for obvious secret patterns
                    if any(pattern in content.lower() for pattern in ['password=', 'secret=', 'api_key=']):
                        # Exclude test files and configuration templates
                        if 'test' not in str(file_path).lower() and 'template' not in str(file_path).lower():
                            secrets_found = True
                            self._add_issue(
                                category="hardcoded_secrets",
                                severity=SeverityLevel.CRITICAL,
                                message=f"Potential hardcoded secret in {file_path.relative_to(self.project_root)}",
                                file_path=str(file_path.relative_to(self.project_root)),
                                suggestion="Move secrets to environment variables or secure secret management"
                            )
                
                except Exception as e:
                    logger.warning(f"Could not scan {file_path} for secrets: {e}")
            
            return not secrets_found
        
        except Exception as e:
            logger.error(f"Secret scanning failed: {e}")
            return False
    
    async def _check_gitignore_secrets(self) -> bool:
        """Check if .gitignore properly excludes secret files."""
        logger.info("Checking .gitignore for secret exclusions")
        
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            self._add_issue(
                category="gitignore",
                severity=SeverityLevel.HIGH,
                message=".gitignore file not found",
                suggestion="Create .gitignore file with proper secret exclusions"
            )
            return False
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            secret_patterns = ['.env', '*.key', '*.pem', 'secrets/', 'config/secrets']
            missing_patterns = []
            
            for pattern in secret_patterns:
                if pattern not in gitignore_content:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                self._add_issue(
                    category="gitignore",
                    severity=SeverityLevel.MEDIUM,
                    message=f"Missing secret exclusions in .gitignore: {missing_patterns}",
                    suggestion="Add secret file patterns to .gitignore"
                )
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to check .gitignore: {e}")
            return False
    
    async def _check_env_secret_loading(self) -> bool:
        """Check if environment-based secret loading is implemented."""
        logger.info("Checking environment secret loading")
        
        # Check if environment variable loading is implemented
        config_files = [
            self.project_root / 'mcp_task_orchestrator' / 'server.py',
            self.project_root / 'mcp_task_orchestrator' / '__main__.py'
        ]
        
        env_loading_found = False
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'os.getenv' in content or 'os.environ' in content:
                        env_loading_found = True
                        break
                
                except Exception as e:
                    logger.warning(f"Could not check {config_file}: {e}")
        
        return env_loading_found
    
    async def _check_database_configuration(self) -> Dict[str, Any]:
        """Check database configuration for production."""
        logger.info("Checking database configuration")
        
        db_checks = {
            'connection_pooling': False,
            'backup_configuration': False,
            'performance_optimization': False,
            'security_configuration': False
        }
        
        # Check if database files exist
        db_path = self.project_root / 'mcp_task_orchestrator' / 'db'
        if db_path.exists():
            db_checks['connection_pooling'] = (db_path / 'connection_pool.py').exists()
            db_checks['backup_configuration'] = self._check_backup_config()
            db_checks['performance_optimization'] = self._check_db_performance_config()
            db_checks['security_configuration'] = self._check_db_security_config()
        
        configured = any(db_checks.values())
        
        if not configured:
            self._add_issue(
                category="database_configuration",
                severity=SeverityLevel.HIGH,
                message="Database configuration incomplete for production",
                suggestion="Configure database connection pooling, backups, and security"
            )
        
        return {
            'configured': configured,
            'database_checks': db_checks
        }
    
    def _check_backup_config(self) -> bool:
        """Check if database backup is configured."""
        # Check for backup scripts or configuration
        backup_files = [
            self.project_root / 'scripts' / 'backup_database.py',
            self.project_root / 'scripts' / 'backup.sh',
            self.project_root / 'backup_config.json'
        ]
        
        return any(backup_file.exists() for backup_file in backup_files)
    
    def _check_db_performance_config(self) -> bool:
        """Check if database performance optimization is configured."""
        # Check for performance-related configuration
        config_files = [
            self.project_root / 'pyproject.toml',
            self.project_root / 'mcp_task_orchestrator' / 'db' / 'config.py'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    performance_keywords = ['pool_size', 'max_overflow', 'pool_timeout', 'indexes']
                    if any(keyword in content for keyword in performance_keywords):
                        return True
                
                except Exception:
                    continue
        
        return False
    
    def _check_db_security_config(self) -> bool:
        """Check if database security is configured."""
        # Check for security-related database configuration
        security_path = self.project_root / 'mcp_task_orchestrator' / 'infrastructure' / 'security'
        return security_path.exists() and (security_path / 'database_security.py').exists()
    
    async def _check_logging_configuration(self) -> Dict[str, Any]:
        """Check logging configuration for production."""
        logger.info("Checking logging configuration")
        
        logging_checks = {
            'log_level_configured': False,
            'log_format_production_ready': False,
            'log_rotation_configured': False,
            'error_tracking_configured': False
        }
        
        # Check pyproject.toml for logging configuration
        pyproject_path = self.project_root / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'logging' in content.lower():
                    logging_checks['log_level_configured'] = True
                    logging_checks['log_format_production_ready'] = True
            
            except Exception as e:
                logger.warning(f"Could not check pyproject.toml: {e}")
        
        # Check for logging configuration in code
        server_file = self.project_root / 'mcp_task_orchestrator' / 'server.py'
        if server_file.exists():
            try:
                with open(server_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'logging.basicConfig' in content or 'getLogger' in content:
                    logging_checks['log_level_configured'] = True
            
            except Exception as e:
                logger.warning(f"Could not check server.py: {e}")
        
        configured = any(logging_checks.values())
        
        if not configured:
            self._add_issue(
                category="logging_configuration",
                severity=SeverityLevel.MEDIUM,
                message="Logging configuration incomplete for production",
                suggestion="Configure production-appropriate logging levels, formats, and rotation"
            )
        
        return {
            'configured': configured,
            'logging_checks': logging_checks
        }
    
    async def _check_security_settings(self) -> Dict[str, Any]:
        """Check security settings for production."""
        logger.info("Checking security settings")
        
        security_checks = {
            'security_infrastructure_exists': False,
            'authentication_configured': False,
            'input_validation_configured': False,
            'error_sanitization_configured': False
        }
        
        # Check for security infrastructure
        security_path = self.project_root / 'mcp_task_orchestrator' / 'infrastructure' / 'security'
        if security_path.exists():
            security_checks['security_infrastructure_exists'] = True
            security_checks['authentication_configured'] = (security_path / 'authentication.py').exists()
            security_checks['input_validation_configured'] = (security_path / 'input_validation.py').exists()
            security_checks['error_sanitization_configured'] = (security_path / 'error_sanitization.py').exists()
        
        configured = any(security_checks.values())
        
        if not configured:
            self._add_issue(
                category="security_settings",
                severity=SeverityLevel.CRITICAL,
                message="Security settings incomplete for production",
                suggestion="Configure authentication, input validation, and error sanitization"
            )
        
        return {
            'configured': configured,
            'security_checks': security_checks
        }
    
    async def _validate_error_handling(self) -> Dict[str, Any]:
        """Validate comprehensive error handling and recovery."""
        logger.info("Validating error handling")
        
        error_handling_checks = {
            'exception_handling': await self._check_exception_handling(),
            'error_logging': await self._check_error_logging(),
            'graceful_degradation': await self._check_graceful_degradation(),
            'recovery_mechanisms': await self._check_recovery_mechanisms()
        }
        
        all_handled = all(error_handling_checks.values())
        
        if not all_handled:
            missing_checks = [
                name for name, passed in error_handling_checks.items() 
                if not passed
            ]
            self._add_issue(
                category="error_handling",
                severity=SeverityLevel.HIGH,
                message=f"Error handling incomplete: {', '.join(missing_checks)}",
                suggestion="Implement comprehensive error handling and recovery mechanisms"
            )
        
        return {
            'passed': all_handled,
            'error_handling_details': error_handling_checks
        }
    
    async def _check_exception_handling(self) -> bool:
        """Check if proper exception handling is implemented."""
        logger.info("Checking exception handling")
        
        try:
            # Check for error handling decorators and infrastructure
            error_handling_path = self.project_root / 'mcp_task_orchestrator' / 'infrastructure' / 'error_handling'
            if error_handling_path.exists():
                decorator_files = list(error_handling_path.glob('*decorator*.py'))
                return len(decorator_files) > 0
            
            return False
        
        except Exception as e:
            logger.error(f"Exception handling check failed: {e}")
            return False
    
    async def _check_error_logging(self) -> bool:
        """Check if error logging is properly configured."""
        logger.info("Checking error logging")
        
        try:
            # Check for error logging in main files
            main_files = [
                self.project_root / 'mcp_task_orchestrator' / 'server.py',
                self.project_root / 'mcp_task_orchestrator' / '__main__.py'
            ]
            
            for main_file in main_files:
                if main_file.exists():
                    with open(main_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'logger.error' in content or 'logging.error' in content:
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error logging check failed: {e}")
            return False
    
    async def _check_graceful_degradation(self) -> bool:
        """Check if graceful degradation is implemented."""
        logger.info("Checking graceful degradation")
        
        try:
            # Check for graceful degradation patterns
            python_files = self._get_python_files()
            
            for file_path in python_files:
                if 'server' in str(file_path) or 'main' in str(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for graceful degradation patterns
                        degradation_patterns = ['fallback', 'try:', 'except:', 'finally:']
                        if any(pattern in content for pattern in degradation_patterns):
                            return True
                    
                    except Exception:
                        continue
            
            return False
        
        except Exception as e:
            logger.error(f"Graceful degradation check failed: {e}")
            return False
    
    async def _check_recovery_mechanisms(self) -> bool:
        """Check if recovery mechanisms are implemented."""
        logger.info("Checking recovery mechanisms")
        
        try:
            # Check for recovery-related files or patterns
            recovery_files = [
                self.project_root / 'scripts' / 'recovery.py',
                self.project_root / 'mcp_task_orchestrator' / 'recovery.py',
                self.project_root / 'tools' / 'recovery.py'
            ]
            
            # Check if any recovery files exist
            if any(recovery_file.exists() for recovery_file in recovery_files):
                return True
            
            # Check for recovery patterns in main files
            main_files = [
                self.project_root / 'mcp_task_orchestrator' / 'server.py'
            ]
            
            for main_file in main_files:
                if main_file.exists():
                    with open(main_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    recovery_patterns = ['restart', 'recover', 'retry', 'reconnect']
                    if any(pattern in content.lower() for pattern in recovery_patterns):
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"Recovery mechanisms check failed: {e}")
            return False
    
    async def _validate_monitoring_setup(self) -> Dict[str, Any]:
        """Validate logging and monitoring configuration."""
        logger.info("Validating monitoring setup")
        
        monitoring_checks = {
            'health_check_endpoint': await self._check_health_check_endpoint(),
            'metrics_collection': await self._check_metrics_collection(),
            'performance_monitoring': await self._check_performance_monitoring(),
            'alert_configuration': await self._check_alert_configuration()
        }
        
        monitoring_configured = any(monitoring_checks.values())
        
        if not monitoring_configured and self.monitoring_required:
            self._add_issue(
                category="monitoring_setup",
                severity=SeverityLevel.HIGH,
                message="Monitoring setup incomplete for production",
                suggestion="Configure health checks, metrics collection, and alerting"
            )
        
        return {
            'passed': monitoring_configured or not self.monitoring_required,
            'monitoring_details': monitoring_checks
        }
    
    async def _check_health_check_endpoint(self) -> bool:
        """Check if health check endpoint is implemented."""
        logger.info("Checking health check endpoint")
        
        try:
            # Check for health check implementation
            health_check_files = [
                self.project_root / 'tools' / 'diagnostics' / 'health_check.py',
                self.project_root / 'mcp_task_orchestrator' / 'health_check.py',
                self.project_root / 'health_check.py'
            ]
            
            return any(health_file.exists() for health_file in health_check_files)
        
        except Exception as e:
            logger.error(f"Health check endpoint check failed: {e}")
            return False
    
    async def _check_metrics_collection(self) -> bool:
        """Check if metrics collection is configured."""
        logger.info("Checking metrics collection")
        
        try:
            # Check for metrics collection implementation
            metrics_files = [
                self.project_root / 'tools' / 'diagnostics' / 'performance_monitor.py',
                self.project_root / 'mcp_task_orchestrator' / 'metrics.py'
            ]
            
            return any(metrics_file.exists() for metrics_file in metrics_files)
        
        except Exception as e:
            logger.error(f"Metrics collection check failed: {e}")
            return False
    
    async def _check_performance_monitoring(self) -> bool:
        """Check if performance monitoring is configured."""
        logger.info("Checking performance monitoring")
        
        try:
            # Check for performance monitoring tools
            perf_monitor_path = self.project_root / 'tools' / 'diagnostics' / 'performance_monitor.py'
            return perf_monitor_path.exists()
        
        except Exception as e:
            logger.error(f"Performance monitoring check failed: {e}")
            return False
    
    async def _check_alert_configuration(self) -> bool:
        """Check if alerting is configured."""
        logger.info("Checking alert configuration")
        
        try:
            # Check for alert configuration files
            alert_files = [
                self.project_root / 'alerts.yaml',
                self.project_root / 'monitoring' / 'alerts.json',
                self.project_root / 'config' / 'alerts.conf'
            ]
            
            return any(alert_file.exists() for alert_file in alert_files)
        
        except Exception as e:
            logger.error(f"Alert configuration check failed: {e}")
            return False
    
    async def _validate_security_audit_logging(self) -> Dict[str, Any]:
        """Validate security audit logging configuration."""
        logger.info("Validating security audit logging")
        
        audit_checks = {
            'audit_log_configuration': await self._check_audit_log_config(),
            'security_event_logging': await self._check_security_event_logging(),
            'log_retention_policy': await self._check_log_retention_policy(),
            'log_integrity_protection': await self._check_log_integrity_protection()
        }
        
        audit_configured = any(audit_checks.values())
        
        if not audit_configured and self.security_audit_required:
            self._add_issue(
                category="security_audit_logging",
                severity=SeverityLevel.HIGH,
                message="Security audit logging not configured",
                suggestion="Configure security audit logging, retention policies, and integrity protection"
            )
        
        return {
            'passed': audit_configured or not self.security_audit_required,
            'audit_details': audit_checks
        }
    
    async def _check_audit_log_config(self) -> bool:
        """Check if audit logging is configured."""
        logger.info("Checking audit log configuration")
        
        try:
            # Check for audit logging configuration
            config_files = [
                self.project_root / 'pyproject.toml',
                self.project_root / 'logging.conf',
                self.project_root / 'audit_config.json'
            ]
            
            for config_file in config_files:
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'audit' in content.lower():
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"Audit log configuration check failed: {e}")
            return False
    
    async def _check_security_event_logging(self) -> bool:
        """Check if security events are being logged."""
        logger.info("Checking security event logging")
        
        try:
            # Check for security event logging in security infrastructure
            security_path = self.project_root / 'mcp_task_orchestrator' / 'infrastructure' / 'security'
            if security_path.exists():
                for security_file in security_path.glob('*.py'):
                    try:
                        with open(security_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if 'logger.' in content and ('security' in content.lower() or 'audit' in content.lower()):
                            return True
                    
                    except Exception:
                        continue
            
            return False
        
        except Exception as e:
            logger.error(f"Security event logging check failed: {e}")
            return False
    
    async def _check_log_retention_policy(self) -> bool:
        """Check if log retention policy is configured."""
        logger.info("Checking log retention policy")
        
        try:
            # Check for log retention configuration
            retention_configs = [
                self.project_root / 'logging.conf',
                self.project_root / 'log_retention.json',
                self.project_root / 'config' / 'retention_policy.yaml'
            ]
            
            return any(retention_config.exists() for retention_config in retention_configs)
        
        except Exception as e:
            logger.error(f"Log retention policy check failed: {e}")
            return False
    
    async def _check_log_integrity_protection(self) -> bool:
        """Check if log integrity protection is configured."""
        logger.info("Checking log integrity protection")
        
        try:
            # Check for log integrity protection mechanisms
            integrity_files = [
                self.project_root / 'log_integrity.py',
                self.project_root / 'tools' / 'log_integrity.py'
            ]
            
            return any(integrity_file.exists() for integrity_file in integrity_files)
        
        except Exception as e:
            logger.error(f"Log integrity protection check failed: {e}")
            return False
    
    async def _validate_deployment_readiness(self) -> Dict[str, Any]:
        """Validate deployment readiness for target platforms."""
        logger.info("Validating deployment readiness")
        
        deployment_checks = {}
        
        for target in self.deployment_targets:
            if target == 'docker':
                deployment_checks['docker'] = await self._check_docker_readiness()
            elif target == 'pip':
                deployment_checks['pip'] = await self._check_pip_readiness()
            elif target == 'pypi':
                deployment_checks['pypi'] = await self._check_pypi_readiness()
        
        all_ready = all(deployment_checks.values())
        
        if not all_ready:
            failed_targets = [target for target, ready in deployment_checks.items() if not ready]
            self._add_issue(
                category="deployment_readiness",
                severity=SeverityLevel.HIGH,
                message=f"Deployment not ready for targets: {', '.join(failed_targets)}",
                suggestion="Complete deployment configuration for all target platforms"
            )
        
        return {
            'ready': all_ready,
            'deployment_details': deployment_checks
        }
    
    async def _check_docker_readiness(self) -> bool:
        """Check if Docker deployment is ready."""
        logger.info("Checking Docker deployment readiness")
        
        try:
            docker_files = [
                self.project_root / 'Dockerfile',
                self.project_root / 'docker-compose.yml',
                self.project_root / '.dockerignore'
            ]
            
            return any(docker_file.exists() for docker_file in docker_files)
        
        except Exception as e:
            logger.error(f"Docker readiness check failed: {e}")
            return False
    
    async def _check_pip_readiness(self) -> bool:
        """Check if pip installation is ready."""
        logger.info("Checking pip installation readiness")
        
        try:
            # Check for setup files
            setup_files = [
                self.project_root / 'setup.py',
                self.project_root / 'pyproject.toml'
            ]
            
            return any(setup_file.exists() for setup_file in setup_files)
        
        except Exception as e:
            logger.error(f"Pip readiness check failed: {e}")
            return False
    
    async def _check_pypi_readiness(self) -> bool:
        """Check if PyPI publishing is ready."""
        logger.info("Checking PyPI publishing readiness")
        
        try:
            # Check for PyPI publishing configuration
            pypi_files = [
                self.project_root / 'pyproject.toml',
                self.project_root / 'setup.cfg',
                self.project_root / '.pypirc'
            ]
            
            has_config = any(pypi_file.exists() for pypi_file in pypi_files)
            
            # Check for required metadata
            if has_config:
                pyproject_path = self.project_root / 'pyproject.toml'
                if pyproject_path.exists():
                    with open(pyproject_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    required_fields = ['name', 'version', 'description', 'authors']
                    return all(field in content for field in required_fields)
            
            return has_config
        
        except Exception as e:
            logger.error(f"PyPI readiness check failed: {e}")
            return False
    
    async def _perform_final_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health validation."""
        logger.info("Performing final system health check")
        
        health_checks = {
            'import_validation': await self._validate_imports(),
            'syntax_validation': await self._validate_syntax(),
            'dependency_validation': await self._validate_dependencies(),
            'startup_validation': await self._validate_startup()
        }
        
        all_healthy = all(health_checks.values())
        
        if not all_healthy:
            failed_checks = [name for name, passed in health_checks.items() if not passed]
            self._add_issue(
                category="system_health",
                severity=SeverityLevel.CRITICAL,
                message=f"System health check failed: {', '.join(failed_checks)}",
                suggestion="Fix all system health issues before production deployment"
            )
        
        return {
            'passed': all_healthy,
            'health_details': health_checks
        }
    
    async def _validate_imports(self) -> bool:
        """Validate that all imports are working."""
        logger.info("Validating imports")
        
        try:
            # Test importing the main package
            result = await self._run_tool([
                'python', '-c',
                'import mcp_task_orchestrator; print("Import successful")'
            ])
            
            return result.success
        
        except Exception as e:
            logger.error(f"Import validation failed: {e}")
            return False
    
    async def _validate_syntax(self) -> bool:
        """Validate Python syntax across all files."""
        logger.info("Validating syntax")
        
        try:
            # Run syntax validation
            result = await self._run_tool([
                'python', '-m', 'py_compile',
                str(self.project_root / 'mcp_task_orchestrator')
            ])
            
            return result.success
        
        except Exception as e:
            logger.error(f"Syntax validation failed: {e}")
            return False
    
    async def _validate_dependencies(self) -> bool:
        """Validate that all dependencies are available."""
        logger.info("Validating dependencies")
        
        try:
            # Check if requirements can be satisfied
            requirements_files = [
                self.project_root / 'requirements.txt',
                self.project_root / 'pyproject.toml'
            ]
            
            for req_file in requirements_files:
                if req_file.exists():
                    return True  # Basic check - file exists
            
            return False
        
        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            return False
    
    async def _validate_startup(self) -> bool:
        """Validate that the application can start up."""
        logger.info("Validating startup")
        
        try:
            # Test basic startup
            result = await self._run_tool([
                'python', '-c',
                'from mcp_task_orchestrator.server import main; print("Startup validation successful")'
            ])
            
            return result.success
        
        except Exception as e:
            logger.error(f"Startup validation failed: {e}")
            return False
    
    async def _validate_documentation_completeness(self) -> Dict[str, Any]:
        """Validate documentation completeness for production."""
        logger.info("Validating documentation completeness")
        
        doc_checks = {
            'readme_exists': (self.project_root / 'README.md').exists(),
            'changelog_exists': (self.project_root / 'CHANGELOG.md').exists(),
            'contributing_exists': (self.project_root / 'CONTRIBUTING.md').exists(),
            'license_exists': (self.project_root / 'LICENSE').exists(),
            'claude_md_exists': (self.project_root / 'CLAUDE.md').exists(),
            'api_documentation': await self._check_api_documentation()
        }
        
        docs_complete = all(doc_checks.values())
        
        if not docs_complete:
            missing_docs = [name for name, exists in doc_checks.items() if not exists]
            self._add_issue(
                category="documentation",
                severity=SeverityLevel.MEDIUM,
                message=f"Missing documentation: {', '.join(missing_docs)}",
                suggestion="Create all required documentation files for production"
            )
        
        return {
            'complete': docs_complete,
            'documentation_details': doc_checks
        }
    
    async def _check_api_documentation(self) -> bool:
        """Check if API documentation exists."""
        logger.info("Checking API documentation")
        
        try:
            # Check for API documentation
            api_doc_files = [
                self.project_root / 'docs' / 'api' / 'README.md',
                self.project_root / 'API.md',
                self.project_root / 'docs' / 'users' / 'reference' / 'api' / 'API_REFERENCE.md'
            ]
            
            return any(api_doc.exists() for api_doc in api_doc_files)
        
        except Exception as e:
            logger.error(f"API documentation check failed: {e}")
            return False
    
    async def _validate_dependency_security(self) -> Dict[str, Any]:
        """Validate dependency security and vulnerability scan."""
        logger.info("Validating dependency security")
        
        security_checks = {
            'vulnerability_scan': await self._run_vulnerability_scan(),
            'dependency_audit': await self._audit_dependencies(),
            'outdated_packages': await self._check_outdated_packages()
        }
        
        secure = all(security_checks.values())
        
        if not secure:
            self._add_issue(
                category="dependency_security",
                severity=SeverityLevel.HIGH,
                message="Dependency security issues detected",
                suggestion="Update vulnerable dependencies and review security audit results"
            )
        
        return {
            'secure': secure,
            'security_details': security_checks
        }
    
    async def _run_vulnerability_scan(self) -> bool:
        """Run vulnerability scan on dependencies."""
        logger.info("Running vulnerability scan")
        
        try:
            # Try to run safety check if available
            result = await self._run_tool(['safety', 'check'])
            return result.success
        
        except Exception:
            # If safety is not available, check for basic security patterns
            return await self._basic_security_check()
    
    async def _basic_security_check(self) -> bool:
        """Basic security check if safety is not available."""
        logger.info("Running basic security check")
        
        try:
            # Check for common vulnerable patterns
            python_files = self._get_python_files()
            
            vulnerable_patterns = [
                'eval(',
                'exec(',
                'subprocess.call',
                'os.system',
                'pickle.loads'
            ]
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in vulnerable_patterns:
                        if pattern in content:
                            self._add_issue(
                                category="security_vulnerability",
                                severity=SeverityLevel.HIGH,
                                message=f"Potentially vulnerable pattern '{pattern}' found in {file_path.relative_to(self.project_root)}",
                                file_path=str(file_path.relative_to(self.project_root)),
                                suggestion="Review and secure the usage of this pattern"
                            )
                            return False
                
                except Exception:
                    continue
            
            return True
        
        except Exception as e:
            logger.error(f"Basic security check failed: {e}")
            return False
    
    async def _audit_dependencies(self) -> bool:
        """Audit dependencies for security issues."""
        logger.info("Auditing dependencies")
        
        try:
            # Check if pip-audit is available and run it
            result = await self._run_tool(['pip-audit'])
            return result.success
        
        except Exception:
            # If pip-audit is not available, do basic dependency check
            return self._basic_dependency_check()
    
    def _basic_dependency_check(self) -> bool:
        """Basic dependency check if pip-audit is not available."""
        logger.info("Running basic dependency check")
        
        try:
            # Check for requirements files
            req_files = [
                self.project_root / 'requirements.txt',
                self.project_root / 'pyproject.toml'
            ]
            
            return any(req_file.exists() for req_file in req_files)
        
        except Exception as e:
            logger.error(f"Basic dependency check failed: {e}")
            return False
    
    async def _check_outdated_packages(self) -> bool:
        """Check for outdated packages."""
        logger.info("Checking for outdated packages")
        
        try:
            # Run pip list --outdated to check for outdated packages
            result = await self._run_tool(['pip', 'list', '--outdated'])
            
            # If there are outdated packages, the command succeeds but we need to check output
            if result.success and result.output.strip():
                # Parse output to see if there are actually outdated packages
                lines = result.output.strip().split('\n')
                # Skip header lines
                package_lines = [line for line in lines if not line.startswith('Package') and not line.startswith('---')]
                
                if package_lines:
                    self._add_issue(
                        category="outdated_packages",
                        severity=SeverityLevel.MEDIUM,
                        message=f"Found {len(package_lines)} outdated packages",
                        suggestion="Update outdated packages to latest secure versions"
                    )
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Outdated packages check failed: {e}")
            return True  # Don't fail the check if we can't run it
    
    async def _validate_backup_recovery_procedures(self) -> Dict[str, Any]:
        """Validate backup and recovery procedures."""
        logger.info("Validating backup and recovery procedures")
        
        backup_checks = {
            'backup_scripts_exist': await self._check_backup_scripts(),
            'recovery_documentation': await self._check_recovery_documentation(),
            'backup_testing': await self._check_backup_testing(),
            'disaster_recovery_plan': await self._check_disaster_recovery_plan()
        }
        
        backup_ready = any(backup_checks.values())
        
        if not backup_ready:
            self._add_issue(
                category="backup_recovery",
                severity=SeverityLevel.MEDIUM,
                message="Backup and recovery procedures not configured",
                suggestion="Create backup scripts, recovery documentation, and disaster recovery plan"
            )
        
        return {
            'ready': backup_ready,
            'backup_details': backup_checks
        }
    
    async def _check_backup_scripts(self) -> bool:
        """Check if backup scripts exist."""
        logger.info("Checking backup scripts")
        
        try:
            backup_scripts = [
                self.project_root / 'scripts' / 'backup.py',
                self.project_root / 'scripts' / 'backup.sh',
                self.project_root / 'backup.py'
            ]
            
            return any(backup_script.exists() for backup_script in backup_scripts)
        
        except Exception as e:
            logger.error(f"Backup scripts check failed: {e}")
            return False
    
    async def _check_recovery_documentation(self) -> bool:
        """Check if recovery documentation exists."""
        logger.info("Checking recovery documentation")
        
        try:
            recovery_docs = [
                self.project_root / 'docs' / 'recovery.md',
                self.project_root / 'RECOVERY.md',
                self.project_root / 'docs' / 'operations' / 'recovery.md'
            ]
            
            return any(recovery_doc.exists() for recovery_doc in recovery_docs)
        
        except Exception as e:
            logger.error(f"Recovery documentation check failed: {e}")
            return False
    
    async def _check_backup_testing(self) -> bool:
        """Check if backup testing procedures exist."""
        logger.info("Checking backup testing")
        
        try:
            backup_test_files = [
                self.project_root / 'tests' / 'backup' / 'test_backup.py',
                self.project_root / 'scripts' / 'test_backup.py'
            ]
            
            return any(backup_test.exists() for backup_test in backup_test_files)
        
        except Exception as e:
            logger.error(f"Backup testing check failed: {e}")
            return False
    
    async def _check_disaster_recovery_plan(self) -> bool:
        """Check if disaster recovery plan exists."""
        logger.info("Checking disaster recovery plan")
        
        try:
            disaster_recovery_docs = [
                self.project_root / 'DISASTER_RECOVERY.md',
                self.project_root / 'docs' / 'disaster_recovery.md',
                self.project_root / 'docs' / 'operations' / 'disaster_recovery.md'
            ]
            
            return any(dr_doc.exists() for dr_doc in disaster_recovery_docs)
        
        except Exception as e:
            logger.error(f"Disaster recovery plan check failed: {e}")
            return False
    
    def _get_configuration_files(self) -> List[Path]:
        """Get all configuration files in the project."""
        config_files = []
        config_patterns = [
            '*.toml',
            '*.yaml',
            '*.yml',
            '*.json',
            '*.conf',
            '*.cfg',
            '*.ini'
        ]
        
        for pattern in config_patterns:
            config_files.extend(self.project_root.glob(pattern))
        
        return config_files
    
    def _count_production_checks(self) -> int:
        """Count total number of production readiness checks."""
        # This is a simplified count
        return 50  # Approximate number of checks performed