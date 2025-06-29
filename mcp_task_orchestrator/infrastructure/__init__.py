"""
Infrastructure layer for MCP Task Orchestrator.

This layer contains all the technical implementation details including:
- Database implementations
- External service integrations
- Framework-specific code
- Technical utilities

The infrastructure layer implements the interfaces defined in the domain layer.
"""

# Database infrastructure
from .database import (
    SQLiteTaskRepository,
    SQLiteStateRepository, 
    SQLiteSpecialistRepository,
    DatabaseConnectionManager,
    RepositoryFactory,
    LegacyDatabaseAdapter
)

# Dependency injection infrastructure
from .di import (
    ServiceContainer,
    ServiceRegistrar,
    get_container,
    set_container,
    get_service
)

# MCP protocol infrastructure
from .mcp import (
    MCPServerAdapter,
    MCPRequestAdapter,
    MCPResponseAdapter,
    MCPErrorAdapter,
    MCPToolHandler,
    MCPResourceHandler
)

# Configuration infrastructure
from .config import (
    ConfigurationManager,
    ConfigValidator,
    EnvironmentConfigLoader,
    FileConfigLoader,
    DefaultConfigLoader
)

# Monitoring infrastructure
from .monitoring import (
    HealthChecker,
    MetricsCollector,
    LoggingConfigurator
)

# External services infrastructure
from .external import (
    WebhookNotificationService,
    EmailNotificationService,
    HTTPApiClient,
    FileSystemArtifactStorage
)

__all__ = [
    # Database
    'SQLiteTaskRepository',
    'SQLiteStateRepository',
    'SQLiteSpecialistRepository', 
    'DatabaseConnectionManager',
    'RepositoryFactory',
    'LegacyDatabaseAdapter',
    
    # Dependency Injection
    'ServiceContainer',
    'ServiceRegistrar',
    'get_container',
    'set_container',
    'get_service',
    
    # MCP Protocol
    'MCPServerAdapter',
    'MCPRequestAdapter',
    'MCPResponseAdapter',
    'MCPErrorAdapter',
    'MCPToolHandler',
    'MCPResourceHandler',
    
    # Configuration
    'ConfigurationManager',
    'ConfigValidator',
    'EnvironmentConfigLoader',
    'FileConfigLoader',
    'DefaultConfigLoader',
    
    # Monitoring
    'HealthChecker',
    'MetricsCollector',
    'LoggingConfigurator',
    
    # External Services
    'WebhookNotificationService',
    'EmailNotificationService',
    'HTTPApiClient',
    'FileSystemArtifactStorage'
]