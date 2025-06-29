"""
Configuration schema for MCP Task Orchestrator.

This module defines Pydantic models for configuration validation and type safety.
All configuration is validated against these schemas to ensure consistency and
prevent runtime errors from invalid configuration values.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


class EnvironmentType(str, Enum):
    """Supported environment types."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Supported logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    url: str = Field(default="sqlite:///task_orchestrator.db", description="Database connection URL")
    echo: bool = Field(default=False, description="Enable SQL query logging")
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Maximum connection overflow")
    pool_timeout: int = Field(default=30, description="Connection pool timeout in seconds")
    
    class Config:
        extra = "forbid"


class ServerConfig(BaseModel):
    """MCP server configuration settings."""
    name: str = Field(default="mcp-task-orchestrator", description="Server name")
    version: str = Field(default="1.8.0", description="Server version")
    description: str = Field(default="A Model Context Protocol server for task orchestration", description="Server description")
    timeout: int = Field(default=300, description="Request timeout in seconds")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    
    class Config:
        extra = "forbid"


class SpecialistRole(BaseModel):
    """Individual specialist role configuration."""
    role_definition: str = Field(..., description="Role definition description")
    expertise: List[str] = Field(default_factory=list, description="Areas of expertise")
    approach: List[str] = Field(default_factory=list, description="Approach guidelines")
    output_format: str = Field(..., description="Expected output format")
    specialist_roles: Optional[Dict[str, str]] = Field(default=None, description="Sub-specialist roles")
    
    class Config:
        extra = "forbid"


class RolesConfig(BaseModel):
    """Specialist roles configuration."""
    roles: Dict[str, SpecialistRole] = Field(default_factory=dict, description="Available specialist roles")
    default_role: str = Field(default="implementer", description="Default specialist role")
    
    @validator('default_role')
    def validate_default_role(cls, v, values):
        if 'roles' in values and v not in values['roles']:
            raise ValueError(f"Default role '{v}' must be defined in roles")
        return v
    
    class Config:
        extra = "forbid"


class TaskConfig(BaseModel):
    """Task execution configuration."""
    max_subtasks: int = Field(default=50, description="Maximum number of subtasks per task")
    max_depth: int = Field(default=5, description="Maximum task nesting depth")
    default_timeout: int = Field(default=3600, description="Default task timeout in seconds")
    artifact_max_size: int = Field(default=10485760, description="Maximum artifact size in bytes (10MB)")
    cleanup_interval: int = Field(default=86400, description="Cleanup interval in seconds (24 hours)")
    
    class Config:
        extra = "forbid"


class PathConfig(BaseModel):
    """Path configuration settings."""
    workspace_dir: Optional[str] = Field(default=None, description="Workspace directory path")
    config_dir: Optional[str] = Field(default=None, description="Configuration directory path")
    data_dir: Optional[str] = Field(default=None, description="Data directory path")
    log_dir: Optional[str] = Field(default=None, description="Log directory path")
    temp_dir: Optional[str] = Field(default=None, description="Temporary directory path")
    
    class Config:
        extra = "forbid"


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: LogLevel = Field(default=LogLevel.INFO, description="Default logging level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file_enabled: bool = Field(default=True, description="Enable file logging")
    console_enabled: bool = Field(default=True, description="Enable console logging")
    max_file_size: int = Field(default=10485760, description="Maximum log file size in bytes (10MB)")
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    
    class Config:
        extra = "forbid"


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    enable_cors: bool = Field(default=True, description="Enable CORS headers")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    api_key_required: bool = Field(default=False, description="Require API key authentication")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")
    
    class Config:
        extra = "forbid"


class DevelopmentConfig(BaseModel):
    """Development-specific configuration."""
    debug: bool = Field(default=True, description="Enable debug mode")
    auto_reload: bool = Field(default=True, description="Enable auto-reload on file changes")
    profiling_enabled: bool = Field(default=False, description="Enable performance profiling")
    test_mode: bool = Field(default=False, description="Enable test mode")
    
    class Config:
        extra = "forbid"


class ProductionConfig(BaseModel):
    """Production-specific configuration."""
    debug: bool = Field(default=False, description="Disable debug mode in production")
    auto_reload: bool = Field(default=False, description="Disable auto-reload in production")
    profiling_enabled: bool = Field(default=False, description="Disable profiling in production")
    performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    error_reporting: bool = Field(default=True, description="Enable error reporting")
    
    class Config:
        extra = "forbid"


class MCPConfig(BaseModel):
    """Complete MCP Task Orchestrator configuration."""
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, description="Current environment")
    server: ServerConfig = Field(default_factory=ServerConfig, description="Server configuration")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    roles: RolesConfig = Field(default_factory=RolesConfig, description="Specialist roles configuration")
    tasks: TaskConfig = Field(default_factory=TaskConfig, description="Task execution configuration")
    paths: PathConfig = Field(default_factory=PathConfig, description="Path configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    development: Optional[DevelopmentConfig] = Field(default=None, description="Development-specific configuration")
    production: Optional[ProductionConfig] = Field(default=None, description="Production-specific configuration")
    
    @root_validator
    def validate_environment_config(cls, values):
        """Ensure environment-specific configuration is present when needed."""
        env = values.get('environment')
        if env == EnvironmentType.DEVELOPMENT and not values.get('development'):
            values['development'] = DevelopmentConfig()
        elif env == EnvironmentType.PRODUCTION and not values.get('production'):
            values['production'] = ProductionConfig()
        return values
    
    class Config:
        extra = "forbid"
        use_enum_values = True


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_config(config_dict: Dict[str, Any]) -> MCPConfig:
    """
    Validate configuration dictionary against schema.
    
    Args:
        config_dict: Configuration dictionary to validate
        
    Returns:
        MCPConfig: Validated configuration object
        
    Raises:
        ConfigValidationError: If validation fails
    """
    try:
        return MCPConfig(**config_dict)
    except Exception as e:
        raise ConfigValidationError(f"Configuration validation failed: {e}") from e