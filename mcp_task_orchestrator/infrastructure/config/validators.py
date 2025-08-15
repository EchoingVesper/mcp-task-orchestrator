"""
Configuration validators.
"""

from typing import Dict, Any, List
from pathlib import Path
import os


class ConfigValidator:
    """
    Validates configuration values for correctness and consistency.
    """
    
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate database settings
        errors.extend(self._validate_database_config(config))
        
        # Validate logging settings
        errors.extend(self._validate_logging_config(config))
        
        # Validate workspace settings
        errors.extend(self._validate_workspace_config(config))
        
        # Validate performance settings
        errors.extend(self._validate_performance_config(config))
        
        return errors
    
    def _validate_database_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate database configuration."""
        errors = []
        
        # Check database path
        if config.get('database_path'):
            db_path = Path(config['database_path'])
            parent_dir = db_path.parent
            
            if not parent_dir.exists():
                errors.append(f"Database directory does not exist: {parent_dir}")
            elif not os.access(parent_dir, os.W_OK):
                errors.append(f"Database directory is not writable: {parent_dir}")
        
        # Check timeout values
        timeout = config.get('database_timeout', 30)
        if not isinstance(timeout, int) or timeout <= 0:
            errors.append("database_timeout must be a positive integer")
        
        # Check max connections
        max_conn = config.get('database_max_connections', 10)
        if not isinstance(max_conn, int) or max_conn <= 0:
            errors.append("database_max_connections must be a positive integer")
        
        return errors
    
    def _validate_logging_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate logging configuration."""
        errors = []
        
        # Check log level
        log_level = config.get('log_level', 'INFO').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            errors.append(f"Invalid log_level: {log_level}. Must be one of {valid_levels}")
        
        # Check log file path if logging to file
        if config.get('log_to_file') and config.get('log_file_path'):
            log_path = Path(config['log_file_path'])
            parent_dir = log_path.parent
            
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create log directory {parent_dir}: {e}")
            elif not os.access(parent_dir, os.W_OK):
                errors.append(f"Log directory is not writable: {parent_dir}")
        
        return errors
    
    def _validate_workspace_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate workspace configuration."""
        errors = []
        
        # Check workspace directory
        if config.get('workspace_dir'):
            workspace = Path(config['workspace_dir'])
            if not workspace.exists():
                errors.append(f"Workspace directory does not exist: {workspace}")
            elif not workspace.is_dir():
                errors.append(f"Workspace path is not a directory: {workspace}")
            elif not os.access(workspace, os.R_OK | os.W_OK):
                errors.append(f"Workspace directory is not readable/writable: {workspace}")
        
        # Check artifacts directory
        artifacts_dir = config.get('artifacts_dir', '.task_orchestrator/artifacts')
        if not artifacts_dir:
            errors.append("artifacts_dir cannot be empty")
        
        return errors
    
    def _validate_performance_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        # Check max concurrent tasks
        max_tasks = config.get('max_concurrent_tasks', 5)
        if not isinstance(max_tasks, int) or max_tasks <= 0:
            errors.append("max_concurrent_tasks must be a positive integer")
        elif max_tasks > 50:
            errors.append("max_concurrent_tasks should not exceed 50 for performance reasons")
        
        # Check default task timeout
        task_timeout = config.get('default_task_timeout', 300)
        if not isinstance(task_timeout, int) or task_timeout <= 0:
            errors.append("default_task_timeout must be a positive integer")
        
        # Check MCP timeout
        mcp_timeout = config.get('mcp_timeout', 120)
        if not isinstance(mcp_timeout, int) or mcp_timeout <= 0:
            errors.append("mcp_timeout must be a positive integer")
        
        return errors