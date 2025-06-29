"""
Dependency Injection infrastructure.

This package provides a complete dependency injection system with
lifetime management, service registration, and automatic resolution.
"""

from .container import (
    ServiceContainer, 
    ServiceResolutionError, 
    CircularDependencyError,
    get_container,
    set_container,
    reset_container,
    register_services,
    get_service,
    auto_register_repositories
)

from .registration import (
    ServiceRegistration,
    ServiceRegistrar,
    AutoRegistration,
    ServiceFactory
)

from .lifetime_managers import (
    LifetimeScope,
    LifetimeManager,
    SingletonLifetimeManager,
    TransientLifetimeManager,
    ScopedLifetimeManager,
    ServiceScope
)

__all__ = [
    # Container
    'ServiceContainer',
    'ServiceResolutionError',
    'CircularDependencyError',
    'get_container',
    'set_container',
    'reset_container',
    'register_services',
    'get_service',
    'auto_register_repositories',
    
    # Registration
    'ServiceRegistration',
    'ServiceRegistrar',
    'AutoRegistration',
    'ServiceFactory',
    
    # Lifetime Management
    'LifetimeScope',
    'LifetimeManager',
    'SingletonLifetimeManager',
    'TransientLifetimeManager', 
    'ScopedLifetimeManager',
    'ServiceScope'
]