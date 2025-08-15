"""
Validation and verification management for the Universal Installer.

This module handles installation verification, health checks, issue detection,
and repair operations to ensure installation integrity.
"""

import os
import sys
import subprocess
import json
import shutil
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

from .models import (
    InstallerConfig,
    InstallationStatus,
    InstallationEnvironment,
    InstallationScope,
    ValidationError,
    InstallationError
)

logger = logging.getLogger(__name__)


class ValidationManager:
    """Manages installation validation and health checks."""
    
    def __init__(self, config: InstallerConfig, console=None):
        self.config = config
        self.console = console
    
    def validate_installation(self) -> None:
        """Validate that installation completed successfully."""
        if self.config.dry_run:
            self.console.print("[dim]Dry run: Would validate installation[/dim]")
            return
        
        issues = []
        
        # Test 1: Package import
        try:
            self._test_package_import()
        except Exception as e:
            issues.append(f"Package import failed: {e}")
        
        # Test 2: Entry points
        try:
            self._test_entry_points()
        except Exception as e:
            issues.append(f"Entry points test failed: {e}")
        
        # Test 3: Dependencies
        try:
            self._test_dependencies()
        except Exception as e:
            issues.append(f"Dependencies test failed: {e}")
        
        # Test 4: MCP server functionality
        try:
            self._test_mcp_server()
        except Exception as e:
            issues.append(f"MCP server test failed: {e}")
        
        if issues:
            error_msg = "Installation validation failed:\n" + "\n".join(f"  • {issue}" for issue in issues)
            raise ValidationError(error_msg)
        
        self.console.print("[green]✓ Installation validation passed[/green]")
    
    def comprehensive_validation(self) -> Dict[str, Any]:
        """Perform comprehensive validation and return detailed status."""
        status = {
            'overall_status': 'healthy',
            'tests': {},
            'issues': [],
            'warnings': []
        }
        
        # Test categories
        test_categories = [
            ('package_import', self._test_package_import),
            ('entry_points', self._test_entry_points),
            ('dependencies', self._test_dependencies),
            ('mcp_server', self._test_mcp_server),
            ('environment', self._test_environment),
            ('client_configs', self._test_client_configurations),
            ('permissions', self._test_permissions)
        ]
        
        for test_name, test_func in test_categories:
            try:
                result = test_func()
                status['tests'][test_name] = {
                    'status': 'passed',
                    'result': result
                }
            except Exception as e:
                status['tests'][test_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                status['issues'].append(f"{test_name}: {e}")
                status['overall_status'] = 'unhealthy'
        
        return status
    
    def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect specific issues that can be repaired."""
        issues = []
        
        # Check for common problems
        issues.extend(self._detect_import_issues())
        issues.extend(self._detect_environment_issues())
        issues.extend(self._detect_dependency_issues())
        issues.extend(self._detect_config_issues())
        
        return issues
    
    def repair_issue(self, issue: Dict[str, Any]) -> None:
        """Attempt to repair a specific issue."""
        issue_type = issue.get('type')
        
        if issue_type == 'missing_dependency':
            self._repair_missing_dependency(issue)
        elif issue_type == 'invalid_environment':
            self._repair_invalid_environment(issue)
        elif issue_type == 'corrupted_config':
            self._repair_corrupted_config(issue)
        elif issue_type == 'permission_issue':
            self._repair_permission_issue(issue)
        else:
            raise ValidationError(f"Cannot repair issue type: {issue_type}")
    
    def _test_package_import(self) -> Dict[str, Any]:
        """Test package import functionality."""
        python_exe = self._get_python_executable()
        
        # Test basic import
        result = subprocess.run(
            [str(python_exe), '-c', 'import mcp_task_orchestrator; print("IMPORT_OK")'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0 or "IMPORT_OK" not in result.stdout:
            raise ValidationError(f"Package import failed: {result.stderr}")
        
        # Test version access
        result = subprocess.run(
            [str(python_exe), '-c', 
             'import mcp_task_orchestrator; print(getattr(mcp_task_orchestrator, "__version__", "unknown"))'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        version = result.stdout.strip() if result.returncode == 0 else "unknown"
        
        return {
            'import_successful': True,
            'version': version
        }
    
    def _test_entry_points(self) -> Dict[str, Any]:
        """Test console script entry points."""
        results = {}
        
        # Test main entry points
        entry_points = [
            ('mcp-task-orchestrator', 'MCP server'),
            ('mcp-task-orchestrator-cli', 'CLI tool')
        ]
        
        for command, description in entry_points:
            try:
                # Check if command is available
                if shutil.which(command):
                    # Test command help (should not fail)
                    result = subprocess.run(
                        [command, '--help'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    results[command] = {
                        'available': True,
                        'help_works': result.returncode == 0,
                        'description': description
                    }
                else:
                    results[command] = {
                        'available': False,
                        'help_works': False,
                        'description': description
                    }
            except Exception as e:
                results[command] = {
                    'available': False,
                    'help_works': False,
                    'error': str(e),
                    'description': description
                }
        
        # Check if at least one entry point works or if this is a development install
        if not any(result.get('available', False) for result in results.values()):
            # For development installs, check if we can import the modules instead
            try:
                import mcp_task_orchestrator
                # If we can import, consider this acceptable for dev installs
                results['module_import'] = {
                    'available': True,
                    'description': 'Development install - module importable'
                }
            except ImportError:
                raise ValidationError("No entry points are available")
        
        return results
    
    def _test_dependencies(self) -> Dict[str, Any]:
        """Test that all required dependencies are available."""
        python_exe = self._get_python_executable()
        
        # Core dependencies from pyproject.toml
        # Note: pyyaml installs as 'yaml', not 'pyyaml'
        required_deps = [
            'mcp', 'pydantic', 'jinja2', 'yaml', 'aiofiles',
            'psutil', 'filelock', 'sqlalchemy', 'alembic', 'aiosqlite'
        ]
        
        # Optional dependencies
        optional_deps = ['typer', 'rich']
        
        dep_status = {}
        missing_required = []
        
        for dep in required_deps + optional_deps:
            try:
                result = subprocess.run(
                    [str(python_exe), '-c', f'import {dep}; print("OK")'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                dep_status[dep] = {
                    'available': result.returncode == 0,
                    'required': dep in required_deps
                }
                
                if dep in required_deps and result.returncode != 0:
                    missing_required.append(dep)
                    
            except Exception as e:
                dep_status[dep] = {
                    'available': False,
                    'required': dep in required_deps,
                    'error': str(e)
                }
                if dep in required_deps:
                    missing_required.append(dep)
        
        if missing_required:
            raise ValidationError(f"Missing required dependencies: {', '.join(missing_required)}")
        
        return dep_status
    
    def _test_mcp_server(self) -> Dict[str, Any]:
        """Test MCP server functionality."""
        python_exe = self._get_python_executable()
        
        # Test server module import
        result = subprocess.run(
            [str(python_exe), '-c', 
             'from mcp_task_orchestrator.server import main; print("SERVER_OK")'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise ValidationError(f"MCP server module test failed: {result.stderr}")
        
        # Test CLI import
        result = subprocess.run(
            [str(python_exe), '-c', 
             'from mcp_task_orchestrator_cli.cli import main; print("CLI_OK")'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        cli_ok = result.returncode == 0
        
        return {
            'server_module': True,
            'cli_module': cli_ok
        }
    
    def _test_environment(self) -> Dict[str, Any]:
        """Test environment health."""
        results = {}
        
        # Check virtual environment (if applicable)
        if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
            venv_path = self._get_venv_path()
            if venv_path:
                env = InstallationEnvironment.detect(venv_path)
                results['venv'] = {
                    'exists': env.exists,
                    'valid': env.is_valid,
                    'path': str(env.path)
                }
                
                if not env.is_valid and env.exists:
                    raise ValidationError(f"Virtual environment at {venv_path} is corrupted")
        
        # Check Python version
        results['python'] = {
            'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'executable': sys.executable
        }
        
        return results
    
    def _test_client_configurations(self) -> Dict[str, Any]:
        """Test MCP client configurations."""
        if not self.config.configure_clients:
            return {'skipped': True}
        
        # Import ClientManager to test configurations
        try:
            from .clients import ClientManager
            client_manager = ClientManager(self.config, self.console)
            detected_clients = client_manager.detect_mcp_clients()
            
            results = {}
            for client_id, client_info in detected_clients.items():
                config_valid = self._validate_client_config(client_id, client_info)
                results[client_id] = {
                    'detected': True,
                    'configured': config_valid,
                    'display_name': client_info['display_name']
                }
            
            return results
            
        except Exception as e:
            logger.warning(f"Could not test client configurations: {e}")
            return {'error': str(e)}
    
    def _test_permissions(self) -> Dict[str, Any]:
        """Test file permissions and access."""
        results = {}
        
        # Test write access to config directory
        config_dir = Path.home() / '.task_orchestrator'
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            test_file = config_dir / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            results['config_dir_writable'] = True
        except Exception as e:
            results['config_dir_writable'] = False
            results['config_dir_error'] = str(e)
        
        # Test installation directory permissions
        if self.config.scope == InstallationScope.PROJECT:
            try:
                venv_path = Path.cwd() / 'venv'
                if venv_path.exists():
                    test_file = venv_path / 'test_write.tmp'
                    test_file.write_text('test')
                    test_file.unlink()
                    results['install_dir_writable'] = True
            except Exception as e:
                results['install_dir_writable'] = False
                results['install_dir_error'] = str(e)
        
        return results
    
    def _validate_client_config(self, client_id: str, client_info: Dict[str, Any]) -> bool:
        """Validate that a client is properly configured."""
        try:
            if client_info['type'] == 'json_config':
                config_path = client_info['config_path']
                if not config_path.exists():
                    return False
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                server_key = client_info['server_key']
                return (server_key in config and 
                       'task-orchestrator' in config[server_key])
            else:
                # CLI clients - assume configured if command works
                return True
                
        except Exception:
            return False
    
    def _detect_import_issues(self) -> List[Dict[str, Any]]:
        """Detect package import issues."""
        issues = []
        
        try:
            self._test_package_import()
        except ValidationError as e:
            issues.append({
                'type': 'import_failure',
                'description': f"Package import failed: {e}",
                'severity': 'critical'
            })
        
        return issues
    
    def _detect_environment_issues(self) -> List[Dict[str, Any]]:
        """Detect environment-related issues."""
        issues = []
        
        if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
            venv_path = self._get_venv_path()
            if venv_path and venv_path.exists():
                env = InstallationEnvironment.detect(venv_path)
                if not env.is_valid:
                    issues.append({
                        'type': 'invalid_environment',
                        'description': f"Virtual environment at {venv_path} is corrupted",
                        'severity': 'high',
                        'path': str(venv_path)
                    })
        
        return issues
    
    def _detect_dependency_issues(self) -> List[Dict[str, Any]]:
        """Detect dependency-related issues."""
        issues = []
        
        try:
            self._test_dependencies()
        except ValidationError as e:
            issues.append({
                'type': 'missing_dependency',
                'description': str(e),
                'severity': 'high'
            })
        
        return issues
    
    def _detect_config_issues(self) -> List[Dict[str, Any]]:
        """Detect configuration-related issues."""
        issues = []
        
        # Check for corrupted client configurations
        if self.config.configure_clients:
            try:
                from .clients import ClientManager
                client_manager = ClientManager(self.config, self.console)
                detected_clients = client_manager.detect_mcp_clients()
                
                for client_id, client_info in detected_clients.items():
                    if client_info['type'] == 'json_config':
                        config_path = client_info['config_path']
                        if config_path.exists():
                            try:
                                with open(config_path, 'r', encoding='utf-8') as f:
                                    json.load(f)
                            except json.JSONDecodeError:
                                issues.append({
                                    'type': 'corrupted_config',
                                    'description': f"Corrupted JSON config: {config_path}",
                                    'severity': 'medium',
                                    'client_id': client_id,
                                    'config_path': str(config_path)
                                })
            except Exception:
                pass
        
        return issues
    
    def _repair_missing_dependency(self, issue: Dict[str, Any]) -> None:
        """Repair missing dependency issues."""
        python_exe = self._get_python_executable()
        
        # Try to reinstall package with dependencies
        cmd = [str(python_exe), '-m', 'pip', 'install', '--force-reinstall', 'mcp-task-orchestrator']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise ValidationError(f"Failed to repair dependencies: {result.stderr}")
    
    def _repair_invalid_environment(self, issue: Dict[str, Any]) -> None:
        """Repair invalid virtual environment."""
        venv_path = Path(issue['path'])
        
        # Remove corrupted environment
        if venv_path.exists():
            import shutil
            shutil.rmtree(venv_path)
        
        # Recreate environment
        result = subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise ValidationError(f"Failed to recreate environment: {result.stderr}")
    
    def _repair_corrupted_config(self, issue: Dict[str, Any]) -> None:
        """Repair corrupted configuration file."""
        config_path = Path(issue['config_path'])
        
        # Create backup of corrupted file
        backup_path = config_path.with_suffix('.corrupted')
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
        
        # Create minimal valid config
        minimal_config = {}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(minimal_config, f, indent=2)
    
    def _repair_permission_issue(self, issue: Dict[str, Any]) -> None:
        """Repair permission issues."""
        # This is platform-specific and may require user intervention
        raise ValidationError("Permission issues require manual intervention")
    
    def _get_python_executable(self) -> Path:
        """Get Python executable for current scope."""
        if self.config.scope in [InstallationScope.PROJECT, InstallationScope.CUSTOM]:
            venv_path = self._get_venv_path()
            if venv_path and venv_path.exists():
                if os.name == 'nt':
                    return venv_path / 'Scripts' / 'python.exe'
                else:
                    return venv_path / 'bin' / 'python'
        
        return Path(sys.executable)
    
    def _get_venv_path(self) -> Optional[Path]:
        """Get virtual environment path if applicable."""
        if self.config.scope == InstallationScope.PROJECT:
            return Path.cwd() / 'venv'
        elif self.config.scope == InstallationScope.CUSTOM:
            return self.config.custom_path
        return None