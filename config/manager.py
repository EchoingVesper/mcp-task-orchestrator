"""Configuration Manager for MCP Task Orchestrator

This module provides a unified configuration management system that:
- Loads configurations from YAML files with environment-specific overrides
- Validates configurations using Pydantic schemas
- Provides auto-detection of workspace paths and project context
- Merges default and environment-specific configurations
- Supports environment variable overrides
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import ValidationError
import logging

from .schema import MCPConfig, Environment

logger = logging.getLogger(__name__)


class ConfigurationManager:
    """Manages configuration loading, validation, and access for MCP Task Orchestrator."""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None, environment: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files. Defaults to ./config
            environment: Environment name (development, production, testing). Defaults to ENVIRONMENT env var or 'development'
        """
        self.config_dir = Path(config_dir or "config").resolve()
        self.environment = Environment(environment or os.getenv("ENVIRONMENT", "development"))
        self._config: Optional[MCPConfig] = None
        self._workspace_dir: Optional[Path] = None
        
    def load_config(self) -> MCPConfig:
        """Load and validate configuration from YAML files.
        
        Returns:
            Validated MCPConfig instance
            
        Raises:
            FileNotFoundError: If required configuration files are missing
            ValidationError: If configuration validation fails
            yaml.YAMLError: If YAML parsing fails
        """
        if self._config is not None:
            return self._config
            
        try:
            # Load default configuration
            default_config = self._load_yaml_file("default.yaml")
            
            # Load environment-specific overrides
            env_config_file = f"{self.environment.value}.yaml"
            env_config = self._load_yaml_file(env_config_file, required=False)
            
            # Merge configurations (environment overrides default)
            merged_config = self._merge_configs(default_config, env_config or {})
            
            # Apply environment variable overrides
            merged_config = self._apply_env_overrides(merged_config)
            
            # Auto-detect workspace paths
            merged_config = self._auto_detect_paths(merged_config)
            
            # Validate configuration
            self._config = MCPConfig(**merged_config)
            
            logger.info(f"Configuration loaded successfully for environment: {self.environment.value}")
            return self._config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def get_config(self) -> MCPConfig:
        """Get the current configuration, loading if necessary.
        
        Returns:
            Current MCPConfig instance
        """
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> MCPConfig:
        """Reload configuration from files.
        
        Returns:
            Reloaded MCPConfig instance
        """
        self._config = None
        return self.load_config()
    
    def _load_yaml_file(self, filename: str, required: bool = True) -> Dict[str, Any]:
        """Load a YAML configuration file.
        
        Args:
            filename: Name of the YAML file to load
            required: Whether the file is required to exist
            
        Returns:
            Parsed YAML content as dictionary
            
        Raises:
            FileNotFoundError: If required file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            if required:
                raise FileNotFoundError(f"Required configuration file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
                logger.debug(f"Loaded configuration from {file_path}")
                return content
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {file_path}: {e}")
            raise
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        merged = base.copy()
        
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.
        
        Environment variables should be prefixed with MCP_ORCHESTRATOR_ and use underscores
        to separate nested keys. For example:
        - MCP_ORCHESTRATOR_DATABASE_URL
        - MCP_ORCHESTRATOR_SERVER_TIMEOUT
        
        Args:
            config: Configuration dictionary to apply overrides to
            
        Returns:
            Configuration with environment variable overrides applied
        """
        env_prefix = "MCP_ORCHESTRATOR_"
        
        for key, value in os.environ.items():
            if not key.startswith(env_prefix):
                continue
                
            # Remove prefix and convert to lowercase
            config_key = key[len(env_prefix):].lower()
            key_parts = config_key.split('_')
            
            # Navigate/create nested dictionary structure
            current = config
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Skip if intermediate key exists but isn't a dict
                    break
                current = current[part]
            else:
                # Set the final value (try to convert to appropriate type)
                final_key = key_parts[-1]
                current[final_key] = self._convert_env_value(value)
                logger.debug(f"Applied environment override: {key} -> {config_key}")
        
        return config
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate Python type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value (str, int, float, or bool)
        """
        # Handle boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _auto_detect_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-detect workspace and other paths based on project context.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with auto-detected paths
        """
        if 'paths' not in config:
            config['paths'] = {}
        
        paths = config['paths']
        
        # Auto-detect workspace directory
        if not paths.get('workspace_dir'):
            workspace_dir = self._detect_workspace_directory()
            if workspace_dir:
                paths['workspace_dir'] = str(workspace_dir)
                self._workspace_dir = workspace_dir
                logger.debug(f"Auto-detected workspace directory: {workspace_dir}")
        
        # Auto-detect other paths based on workspace
        workspace_path = Path(paths.get('workspace_dir', '.'))
        
        if not paths.get('config_dir'):
            paths['config_dir'] = str(workspace_path / 'config')
        
        if not paths.get('data_dir'):
            # Use .task_orchestrator directory in workspace for data
            paths['data_dir'] = str(workspace_path / '.task_orchestrator')
        
        if not paths.get('log_dir'):
            # Default log directory based on environment
            if self.environment == Environment.PRODUCTION:
                paths['log_dir'] = '/var/log/mcp-task-orchestrator'
            else:
                paths['log_dir'] = str(workspace_path / 'logs')
        
        if not paths.get('temp_dir'):
            # Default temp directory based on environment
            if self.environment == Environment.PRODUCTION:
                paths['temp_dir'] = '/tmp/mcp-task-orchestrator'
            else:
                paths['temp_dir'] = str(workspace_path / 'tmp')
        
        return config
    
    def _detect_workspace_directory(self) -> Optional[Path]:
        """Detect the project workspace directory.
        
        Looks for common project indicators like .git, package.json, pyproject.toml, etc.
        
        Returns:
            Path to detected workspace directory, or None if not found
        """
        current_dir = Path.cwd()
        
        # Common project indicators
        project_indicators = [
            '.git',
            'package.json',
            'pyproject.toml',
            'setup.py',
            'Cargo.toml',
            'go.mod',
            '.project',
            'Makefile',
            'requirements.txt'
        ]
        
        # Check current directory and parents
        for directory in [current_dir] + list(current_dir.parents):
            for indicator in project_indicators:
                if (directory / indicator).exists():
                    return directory
        
        # Fall back to current directory
        return current_dir
    
    def get_workspace_dir(self) -> Path:
        """Get the workspace directory.
        
        Returns:
            Path to the workspace directory
        """
        if self._workspace_dir is None:
            config = self.get_config()
            self._workspace_dir = Path(config.paths.workspace_dir)
        return self._workspace_dir
    
    def get_database_url(self) -> str:
        """Get the database URL with workspace-relative path resolution.
        
        Returns:
            Resolved database URL
        """
        config = self.get_config()
        db_url = config.database.url
        
        # Handle SQLite URLs with relative paths
        if db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
            # Relative SQLite path - resolve relative to workspace
            relative_path = db_url[10:]  # Remove 'sqlite:///'
            if not Path(relative_path).is_absolute():
                workspace_dir = self.get_workspace_dir()
                absolute_path = workspace_dir / relative_path
                db_url = f"sqlite:///{absolute_path}"
        
        return db_url


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_dir: Optional[Union[str, Path]] = None, 
                       environment: Optional[str] = None) -> ConfigurationManager:
    """Get or create the global configuration manager instance.
    
    Args:
        config_dir: Directory containing configuration files
        environment: Environment name
        
    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_dir, environment)
    
    return _config_manager


def get_config() -> MCPConfig:
    """Get the current configuration.
    
    Returns:
        Current MCPConfig instance
    """
    return get_config_manager().get_config()


def reload_config() -> MCPConfig:
    """Reload configuration from files.
    
    Returns:
        Reloaded MCPConfig instance
    """
    return get_config_manager().reload_config()