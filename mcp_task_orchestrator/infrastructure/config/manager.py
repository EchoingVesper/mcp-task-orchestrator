"""
Configuration manager for infrastructure layer.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import os
import logging

from .validators import ConfigValidator
from .loaders import (
    EnvironmentConfigLoader,
    FileConfigLoader,
    DefaultConfigLoader
)

logger = logging.getLogger(__name__)


@dataclass
class ConfigurationSettings:
    """Configuration settings for the orchestrator."""
    
    # Database settings
    database_path: Optional[str] = None
    database_timeout: int = 30
    database_max_connections: int = 10
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = False
    log_file_path: Optional[str] = None
    
    # MCP settings
    mcp_server_name: str = "task-orchestrator"
    mcp_timeout: int = 120
    
    # Orchestration settings
    max_concurrent_tasks: int = 5
    default_task_timeout: int = 300
    enable_dependency_injection: bool = True
    
    # Workspace settings
    workspace_dir: Optional[str] = None
    artifacts_dir: str = ".task_orchestrator/artifacts"
    
    # External service settings
    enable_notifications: bool = False
    notification_webhook_url: Optional[str] = None
    
    # Performance settings
    enable_metrics: bool = False
    metrics_collection_interval: int = 60


class ConfigurationManager:
    """
    Manages configuration loading and validation from multiple sources.
    
    Priority order:
    1. Environment variables
    2. Configuration files (YAML/JSON)
    3. Default values
    """
    
    def __init__(self, config_file_path: Optional[Path] = None):
        self.config_file_path = config_file_path
        self.validator = ConfigValidator()
        self._settings: Optional[ConfigurationSettings] = None
        
        # Initialize loaders
        self.env_loader = EnvironmentConfigLoader()
        self.file_loader = FileConfigLoader()
        self.default_loader = DefaultConfigLoader()
    
    def load_configuration(self) -> ConfigurationSettings:
        """
        Load configuration from all sources with proper precedence.
        
        Returns:
            ConfigurationSettings with merged configuration
        """
        try:
            # Start with defaults
            config_dict = self.default_loader.load()
            
            # Override with file configuration if available
            if self.config_file_path and self.config_file_path.exists():
                file_config = self.file_loader.load(self.config_file_path)
                config_dict.update(file_config)
                logger.info(f"Loaded configuration from {self.config_file_path}")
            
            # Override with environment variables
            env_config = self.env_loader.load()
            config_dict.update({k: v for k, v in env_config.items() if v is not None})
            
            # Validate configuration
            validation_errors = self.validator.validate(config_dict)
            if validation_errors:
                logger.warning(f"Configuration validation warnings: {validation_errors}")
            
            # Create settings object
            self._settings = ConfigurationSettings(**config_dict)
            
            logger.info("Configuration loaded successfully")
            return self._settings
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Return default configuration as fallback
            return ConfigurationSettings()
    
    def get_settings(self) -> ConfigurationSettings:
        """Get current configuration settings, loading if necessary."""
        if self._settings is None:
            self._settings = self.load_configuration()
        return self._settings
    
    def reload_configuration(self) -> ConfigurationSettings:
        """Force reload configuration from all sources."""
        self._settings = None
        return self.load_configuration()
    
    def get_database_url(self) -> str:
        """Get database connection URL."""
        settings = self.get_settings()
        
        if settings.database_path:
            return f"sqlite:///{settings.database_path}"
        
        # Default to workspace-relative path
        workspace = settings.workspace_dir or os.getcwd()
        db_path = Path(workspace) / ".task_orchestrator" / "orchestrator.db"
        return f"sqlite:///{db_path}"
    
    def get_workspace_directory(self) -> Path:
        """Get workspace directory path."""
        settings = self.get_settings()
        
        if settings.workspace_dir:
            return Path(settings.workspace_dir)
        
        # Try to detect workspace from environment
        workspace = (
            os.environ.get("VSCODE_CWD") or
            os.environ.get("CURSOR_CWD") or  
            os.environ.get("WINDSURF_CWD") or
            os.getcwd()
        )
        
        return Path(workspace)
    
    def get_artifacts_directory(self) -> Path:
        """Get artifacts directory path."""
        settings = self.get_settings()
        workspace = self.get_workspace_directory()
        return workspace / settings.artifacts_dir
    
    def is_dependency_injection_enabled(self) -> bool:
        """Check if dependency injection is enabled."""
        settings = self.get_settings()
        
        # Environment variable can override setting
        env_value = os.environ.get("MCP_TASK_ORCHESTRATOR_USE_DI", "").lower()
        if env_value in ("true", "1", "yes"):
            return True
        elif env_value in ("false", "0", "no"):
            return False
        
        return settings.enable_dependency_injection
    
    def get_log_configuration(self) -> Dict[str, Any]:
        """Get logging configuration."""
        settings = self.get_settings()
        
        config = {
            "level": getattr(logging, settings.log_level.upper()),
            "format": settings.log_format
        }
        
        if settings.log_to_file and settings.log_file_path:
            config["filename"] = settings.log_file_path
        
        return config