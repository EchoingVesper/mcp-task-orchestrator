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
# TODO: Re-enable when database implementations are fixed
# from .database import (
#     SQLiteTaskRepository,
#     SQLiteStateRepository, 
#     SQLiteSpecialistRepository,
#     DatabaseConnectionManager,
#     RepositoryFactory,
#     LegacyDatabaseAdapter
# )

# Dependency injection infrastructure
from .di import (
    ServiceContainer,
    ServiceRegistrar,
    get_container,
    set_container,
    get_service
)

# MCP protocol infrastructure
# TODO: Re-enable when MCP adapters are implemented
# from .mcp import (
#     MCPServerAdapter,
#     MCPRequestAdapter,
#     MCPResponseAdapter,
#     MCPErrorAdapter,
#     MCPToolHandler,
#     MCPResourceHandler
# )

# Configuration infrastructure
# TODO: Re-enable when config implementations are fixed
# from .config import (
#     ConfigurationManager,
#     ConfigValidator,
#     EnvironmentConfigLoader,
#     FileConfigLoader,
#     DefaultConfigLoader
# )

# Monitoring infrastructure
# TODO: Re-enable when monitoring implementations are fixed
# from .monitoring import (
#     HealthChecker,
#     MetricsCollector,
#     LoggingConfigurator
# )

# External services infrastructure
# TODO: Re-enable when external service implementations are fixed
# from .external import (
#     WebhookNotificationService,
#     EmailNotificationService,
#     HTTPApiClient,
#     FileSystemArtifactStorage
# )

__all__ = [
    # Dependency Injection (currently working)
    'ServiceContainer',
    'ServiceRegistrar',
    'get_container',
    'set_container',
    'get_service',
    
    # TODO: Add other modules as they are implemented and tested
]