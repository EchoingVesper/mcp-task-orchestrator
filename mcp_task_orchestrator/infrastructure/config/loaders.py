"""
Configuration loaders for different sources.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os
import json
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfigLoader:
    """
    Loads configuration from environment variables.
    
    Uses a consistent prefix pattern for all orchestrator settings.
    """
    
    PREFIX = "MCP_TASK_ORCHESTRATOR_"
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Database settings
        config.update(self._load_database_config())
        
        # Logging settings
        config.update(self._load_logging_config())
        
        # MCP settings
        config.update(self._load_mcp_config())
        
        # Orchestration settings
        config.update(self._load_orchestration_config())
        
        # Workspace settings
        config.update(self._load_workspace_config())
        
        # External service settings
        config.update(self._load_external_config())
        
        # Performance settings
        config.update(self._load_performance_config())
        
        return {k: v for k, v in config.items() if v is not None}
    
    def _get_env(self, key: str, default: Any = None) -> Any:
        """Get environment variable with prefix."""
        return os.environ.get(f"{self.PREFIX}{key}", default)
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = self._get_env(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        elif value in ("false", "0", "no", "off"):
            return False
        return default
    
    def _get_env_int(self, key: str, default: int = 0) -> Optional[int]:
        """Get integer environment variable."""
        value = self._get_env(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {self.PREFIX}{key}: {value}")
        return None
    
    def _load_database_config(self) -> Dict[str, Any]:
        """Load database configuration from environment."""
        return {
            "database_path": self._get_env("DATABASE_PATH"),
            "database_timeout": self._get_env_int("DATABASE_TIMEOUT"),
            "database_max_connections": self._get_env_int("DATABASE_MAX_CONNECTIONS")
        }
    
    def _load_logging_config(self) -> Dict[str, Any]:
        """Load logging configuration from environment."""
        return {
            "log_level": self._get_env("LOG_LEVEL"),
            "log_format": self._get_env("LOG_FORMAT"),
            "log_to_file": self._get_env_bool("LOG_TO_FILE") if self._get_env("LOG_TO_FILE") else None,
            "log_file_path": self._get_env("LOG_FILE_PATH")
        }
    
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration from environment."""
        return {
            "mcp_server_name": self._get_env("MCP_SERVER_NAME"),
            "mcp_timeout": self._get_env_int("MCP_TIMEOUT")
        }
    
    def _load_orchestration_config(self) -> Dict[str, Any]:
        """Load orchestration configuration from environment."""
        return {
            "max_concurrent_tasks": self._get_env_int("MAX_CONCURRENT_TASKS"),
            "default_task_timeout": self._get_env_int("DEFAULT_TASK_TIMEOUT"),
            "enable_dependency_injection": self._get_env_bool("USE_DI") if self._get_env("USE_DI") else None
        }
    
    def _load_workspace_config(self) -> Dict[str, Any]:
        """Load workspace configuration from environment."""
        return {
            "workspace_dir": self._get_env("WORKSPACE_DIR") or self._get_env("PROJECT_DIR"),
            "artifacts_dir": self._get_env("ARTIFACTS_DIR")
        }
    
    def _load_external_config(self) -> Dict[str, Any]:
        """Load external service configuration from environment."""
        return {
            "enable_notifications": self._get_env_bool("ENABLE_NOTIFICATIONS") if self._get_env("ENABLE_NOTIFICATIONS") else None,
            "notification_webhook_url": self._get_env("NOTIFICATION_WEBHOOK_URL")
        }
    
    def _load_performance_config(self) -> Dict[str, Any]:
        """Load performance configuration from environment."""
        return {
            "enable_metrics": self._get_env_bool("ENABLE_METRICS") if self._get_env("ENABLE_METRICS") else None,
            "metrics_collection_interval": self._get_env_int("METRICS_COLLECTION_INTERVAL")
        }


class FileConfigLoader:
    """
    Loads configuration from JSON or YAML files.
    """
    
    def load(self, file_path: Path) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            if not file_path.exists():
                logger.warning(f"Configuration file not found: {file_path}")
                return {}
            
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ('.yaml', '.yml'):
                    return self._load_yaml(f)
                elif file_path.suffix.lower() == '.json':
                    return self._load_json(f)
                else:
                    logger.warning(f"Unsupported config file format: {file_path.suffix}")
                    return {}
        
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
            return {}
    
    def _load_yaml(self, file_handle) -> Dict[str, Any]:
        """Load YAML configuration."""
        try:
            import yaml
            return yaml.safe_load(file_handle) or {}
        except ImportError:
            logger.error("PyYAML not installed, cannot load YAML configuration")
            return {}
    
    def _load_json(self, file_handle) -> Dict[str, Any]:
        """Load JSON configuration."""
        return json.load(file_handle) or {}


class DefaultConfigLoader:
    """
    Provides default configuration values.
    """
    
    def load(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            # Database defaults
            "database_timeout": 30,
            "database_max_connections": 10,
            
            # Logging defaults
            "log_level": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "log_to_file": False,
            
            # MCP defaults
            "mcp_server_name": "task-orchestrator",
            "mcp_timeout": 120,
            
            # Orchestration defaults
            "max_concurrent_tasks": 5,
            "default_task_timeout": 300,
            "enable_dependency_injection": True,
            
            # Workspace defaults
            "artifacts_dir": ".task_orchestrator/artifacts",
            
            # External service defaults
            "enable_notifications": False,
            
            # Performance defaults
            "enable_metrics": False,
            "metrics_collection_interval": 60
        }