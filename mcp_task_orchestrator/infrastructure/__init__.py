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
    DatabaseType,
    DatabaseAdapter,
    OperationalDatabaseAdapter,
    VectorDatabaseAdapter,
    GraphDatabaseAdapter,
    DatabaseAdapterFactory,
    UnifiedDatabaseManager,
    create_unified_manager,
    DatabaseConnectionManager,
    RepositoryFactory,
    create_repository_factory
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
    MCPErrorAdapter
    # Note: MCPToolHandler and MCPResourceHandler temporarily disabled due to import conflicts
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
    PerformanceTracker,
    SystemMonitor,
    DiagnosticRunner
)

# External services infrastructure
from .external import (
    WebhookNotificationService,
    EmailNotificationService,
    HTTPApiClient,
    FileSystemArtifactStorage
)

__all__ = [
    # Database infrastructure
    'DatabaseType',
    'DatabaseAdapter',
    'OperationalDatabaseAdapter',
    'VectorDatabaseAdapter',
    'GraphDatabaseAdapter',
    'DatabaseAdapterFactory',
    'UnifiedDatabaseManager',
    'create_unified_manager',
    'DatabaseConnectionManager',
    'RepositoryFactory',
    'create_repository_factory',
    
    # Dependency Injection
    'ServiceContainer',
    'ServiceRegistrar',
    'get_container',
    'set_container',
    'get_service',
    
    # MCP protocol infrastructure
    'MCPServerAdapter',
    'MCPRequestAdapter',
    'MCPResponseAdapter',
    'MCPErrorAdapter',
    
    # Configuration infrastructure
    'ConfigurationManager',
    'ConfigValidator',
    'EnvironmentConfigLoader',
    'FileConfigLoader',
    'DefaultConfigLoader',
    
    # Monitoring infrastructure
    'HealthChecker',
    'MetricsCollector',
    'PerformanceTracker',
    'SystemMonitor',
    'DiagnosticRunner',
    
    # External services infrastructure
    'WebhookNotificationService',
    'EmailNotificationService',
    'HTTPApiClient',
    'FileSystemArtifactStorage'
]