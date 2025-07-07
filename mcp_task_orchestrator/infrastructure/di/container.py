"""
Dependency Injection Container.

This module provides the main DI container for managing service dependencies,
lifetimes, and resolution throughout the application.
"""

from typing import Type, TypeVar, Dict, Any, Optional, cast, Union
import threading
import logging
from contextlib import contextmanager

from .lifetime_managers import (
    LifetimeManager, LifetimeScope, create_lifetime_manager, 
    ServiceScope, DisposableTracker
)
from .registration import (
    ServiceRegistration, ServiceRegistrar, create_factory_with_dependencies,
    AutoRegistration
)

T = TypeVar('T')
logger = logging.getLogger(__name__)


class ServiceResolutionError(Exception):
    """Exception raised when service resolution fails."""
    pass


class CircularDependencyError(ServiceResolutionError):
    """Exception raised when circular dependencies are detected."""
    pass


class ServiceContainer:
    """
    Main dependency injection container.
    
    Manages service registration, resolution, and lifetime management.
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._services: Dict[Type, LifetimeManager] = {}
        self._resolving_stack: set = set()
        self._lock = threading.RLock()
        self._disposable_tracker = DisposableTracker()
        self._current_scope_context: Optional[Dict[str, Any]] = None
        
        # Register self
        self._services[ServiceContainer] = create_lifetime_manager(
            lambda: self,
            LifetimeScope.SINGLETON
        )
    
    def register(self) -> ServiceRegistrar:
        """
        Get a service registrar for fluent registration.
        
        Returns:
            ServiceRegistrar instance for chaining registrations
        """
        return ServiceRegistrar(self)
    
    def get_service(self, service_type: Type[T]) -> T:
        """
        Resolve and return a service instance.
        
        Args:
            service_type: Type of service to resolve
            
        Returns:
            Service instance
            
        Raises:
            ServiceResolutionError: If service cannot be resolved
            CircularDependencyError: If circular dependency detected
        """
        with self._lock:
            # Check for circular dependencies
            if service_type in self._resolving_stack:
                chain = " -> ".join(str(t.__name__) for t in self._resolving_stack)
                raise CircularDependencyError(
                    f"Circular dependency detected: {chain} -> {service_type.__name__}"
                )
            
            # Check if service is registered
            if service_type not in self._services:
                raise ServiceResolutionError(
                    f"Service of type '{service_type.__name__}' is not registered"
                )
            
            try:
                # Add to resolving stack
                self._resolving_stack.add(service_type)
                
                # Get service from lifetime manager
                manager = self._services[service_type]
                instance = manager.get_instance(self._current_scope_context)
                
                # Track for disposal if needed
                self._disposable_tracker.track(instance)
                
                logger.debug(f"Resolved service: {service_type.__name__}")
                return cast(T, instance)
                
            finally:
                # Remove from resolving stack
                self._resolving_stack.discard(service_type)
    
    def try_get_service(self, service_type: Type[T]) -> Optional[T]:
        """
        Try to resolve a service, returning None if it fails.
        
        Args:
            service_type: Type of service to resolve
            
        Returns:
            Service instance or None if resolution fails
        """
        try:
            return self.get_service(service_type)
        except (ServiceResolutionError, CircularDependencyError):
            return None
    
    def get_services(self, service_type: Type[T]) -> list[T]:
        """
        Get all registered services of a given type.
        
        Args:
            service_type: Type of services to resolve
            
        Returns:
            List of service instances
        """
        # For now, we only support single registrations per type
        # In a more advanced implementation, we could support multiple
        service = self.try_get_service(service_type)
        return [service] if service is not None else []
    
    def is_registered(self, service_type: Type) -> bool:
        """
        Check if a service type is registered.
        
        Args:
            service_type: Type to check
            
        Returns:
            True if registered, False otherwise
        """
        return service_type in self._services
    
    def _register_service(self, service_type: Type, registration: ServiceRegistration):
        """
        Register a service with the container.
        
        Args:
            service_type: Service type
            registration: Registration information
        """
        with self._lock:
            # Create factory function
            if registration.factory:
                factory = registration.factory
            elif registration.instance:
                factory = lambda: registration.instance
            elif registration.implementation_type:
                factory = create_factory_with_dependencies(
                    registration.implementation_type,
                    registration.dependencies
                )
            else:
                raise ValueError("Invalid registration: no implementation specified")
            
            # Wrap factory to use container
            def container_factory():
                return factory(self)
            
            # Create lifetime manager
            manager = create_lifetime_manager(container_factory, registration.lifetime)
            
            # Register
            self._services[service_type] = manager
            
            logger.debug(
                f"Registered service: {service_type.__name__} "
                f"(lifetime: {registration.lifetime.value})"
            )
    
    @contextmanager
    def create_scope(self, scope_context: Optional[Dict[str, Any]] = None):
        """
        Create a service scope for scoped lifetime management.
        
        Args:
            scope_context: Optional context for the scope
            
        Yields:
            ServiceScope context manager
        """
        scope = ServiceScope(self, scope_context)
        try:
            with scope:
                yield scope
        except Exception:
            raise
    
    def dispose(self):
        """Dispose of all managed services and cleanup resources."""
        with self._lock:
            try:
                # Dispose all lifetime managers
                for manager in self._services.values():
                    try:
                        manager.dispose()
                    except Exception as e:
                        logger.warning(f"Error disposing manager: {e}")
                
                # Dispose tracked objects
                self._disposable_tracker.dispose_all()
                
            finally:
                self._services.clear()
                self._resolving_stack.clear()
                self._current_scope_context = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - dispose resources."""
        self.dispose()


# Global container instance (can be replaced with proper DI setup)
_global_container: Optional[ServiceContainer] = None
_container_lock = threading.Lock()


def get_container() -> ServiceContainer:
    """
    Get the global service container.
    
    Returns:
        Global ServiceContainer instance
    """
    global _global_container
    
    if _global_container is None:
        with _container_lock:
            if _global_container is None:
                _global_container = ServiceContainer()
    
    return _global_container


def set_container(container: ServiceContainer):
    """
    Set the global service container.
    
    Args:
        container: Container instance to set as global
    """
    global _global_container
    
    with _container_lock:
        if _global_container is not None:
            _global_container.dispose()
        _global_container = container


def reset_container():
    """Reset the global container (useful for testing)."""
    global _global_container
    
    with _container_lock:
        if _global_container is not None:
            _global_container.dispose()
        _global_container = None


# Convenience functions
def register_services(configuration_func):
    """
    Decorator/function to configure services.
    
    Args:
        configuration_func: Function that takes a ServiceRegistrar
    """
    container = get_container()
    registrar = container.register()
    configuration_func(registrar)
    registrar.build()


def get_service(service_type: Type[T]) -> T:
    """
    Convenience function to get a service from the global container.
    
    Args:
        service_type: Type of service to resolve
        
    Returns:
        Service instance
    """
    return get_container().get_service(service_type)


def auto_register_repositories(repository_module, implementation_module):
    """
    Auto-register repositories with their implementations.
    
    Args:
        repository_module: Module containing repository interfaces
        implementation_module: Module containing implementations
    """
    container = get_container()
    registrar = container.register()
    AutoRegistration.register_repositories(
        registrar,
        repository_module,
        implementation_module
    )
    registrar.build()