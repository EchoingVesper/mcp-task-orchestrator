"""Configuration Package for MCP Task Orchestrator

This package provides a unified configuration management system with:
- Environment-aware configuration loading (development, production, testing)
- Pydantic validation for type safety and validation
- Auto-detection of workspace paths and project context
- YAML-based configuration with environment variable overrides
- Centralized configuration access throughout the application

Usage:
    from config import get_config, get_config_manager
    
    # Get current configuration
    config = get_config()
    
    # Access configuration properties
    db_url = config.database.url
    server_name = config.server.name
    log_level = config.logging.level
    
    # Get configuration manager for advanced operations
    manager = get_config_manager()
    workspace_dir = manager.get_workspace_dir()
"""

from .schema import (
    MCPConfig,
    Environment,
    DatabaseConfig,
    ServerConfig,
    TaskConfig,
    PathConfig,
    LoggingConfig,
    SecurityConfig,
    RoleConfig,
    SpecialistRole
)

from .manager import (
    ConfigurationManager,
    get_config_manager,
    get_config,
    reload_config
)

__all__ = [
    # Schema classes
    'MCPConfig',
    'Environment',
    'DatabaseConfig',
    'ServerConfig',
    'TaskConfig',
    'PathConfig',
    'LoggingConfig',
    'SecurityConfig',
    'RoleConfig',
    'SpecialistRole',
    
    # Manager classes and functions
    'ConfigurationManager',
    'get_config_manager',
    'get_config',
    'reload_config'
]

# Version information
__version__ = "1.8.0"
__author__ = "MCP Task Orchestrator Team"
__description__ = "Unified configuration management system for MCP Task Orchestrator"