"""
Service registration for dependency injection.

This module provides mechanisms for registering services with the DI container,
including factory functions, implementation types, and configuration.
"""

from typing import Type, TypeVar, Callable, Any, Dict, Optional, Union, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
import inspect

from .lifetime_managers import LifetimeScope, LifetimeManager, create_lifetime_manager

T = TypeVar('T')
TInterface = TypeVar('TInterface')
TImplementation = TypeVar('TImplementation')


class ServiceFactory(Protocol):
    """Protocol for service factory functions."""
    
    def __call__(self, container: 'ServiceContainer') -> Any:
        """Create service instance using the container."""
        ...


@dataclass
class ServiceRegistration:
    """Registration information for a service."""
    
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[ServiceFactory] = None
    instance: Optional[Any] = None
    lifetime: LifetimeScope = LifetimeScope.TRANSIENT
    dependencies: Optional[Dict[str, Type]] = None
    
    def __post_init__(self):
        """Validate registration after initialization."""
        sources = sum([
            self.implementation_type is not None,
            self.factory is not None,
            self.instance is not None
        ])
        
        if sources != 1:
            raise ValueError(
                "Exactly one of implementation_type, factory, or instance must be provided"
            )
        
        if self.instance is not None and self.lifetime != LifetimeScope.SINGLETON:
            raise ValueError("Instance registration can only use singleton lifetime")


class ServiceRegistrar:
    """Helper class for fluent service registration."""
    
    def __init__(self, container: 'ServiceContainer'):
        """
        Initialize the registrar.
        
        Args:
            container: The service container to register with
        """
        self.container = container
        self._registrations: Dict[Type, ServiceRegistration] = {}
    
    def register_type(self, 
                     service_type: Type[TInterface], 
                     implementation_type: Type[TImplementation]) -> 'ServiceRegistrar':
        """
        Register a type with its implementation.
        
        Args:
            service_type: Interface or base type
            implementation_type: Concrete implementation type
            
        Returns:
            Self for method chaining
        """
        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type
        )
        self._registrations[service_type] = registration
        return self
    
    def register_factory(self, 
                        service_type: Type[T], 
                        factory: ServiceFactory) -> 'ServiceRegistrar':
        """
        Register a service with a factory function.
        
        Args:
            service_type: Service type
            factory: Factory function
            
        Returns:
            Self for method chaining
        """
        registration = ServiceRegistration(
            service_type=service_type,
            factory=factory
        )
        self._registrations[service_type] = registration
        return self
    
    def register_instance(self, 
                         service_type: Type[T], 
                         instance: T) -> 'ServiceRegistrar':
        """
        Register a service with a pre-created instance.
        
        Args:
            service_type: Service type
            instance: Service instance
            
        Returns:
            Self for method chaining
        """
        registration = ServiceRegistration(
            service_type=service_type,
            instance=instance,
            lifetime=LifetimeScope.SINGLETON
        )
        self._registrations[service_type] = registration
        return self
    
    def as_singleton(self) -> 'ServiceRegistrar':
        """Set the last registration to use singleton lifetime."""
        if not self._registrations:
            raise ValueError("No registrations to modify")
        
        last_key = list(self._registrations.keys())[-1]
        self._registrations[last_key].lifetime = LifetimeScope.SINGLETON
        return self
    
    def as_transient(self) -> 'ServiceRegistrar':
        """Set the last registration to use transient lifetime."""
        if not self._registrations:
            raise ValueError("No registrations to modify")
        
        last_key = list(self._registrations.keys())[-1]
        self._registrations[last_key].lifetime = LifetimeScope.TRANSIENT
        return self
    
    def as_scoped(self) -> 'ServiceRegistrar':
        """Set the last registration to use scoped lifetime."""
        if not self._registrations:
            raise ValueError("No registrations to modify")
        
        last_key = list(self._registrations.keys())[-1]
        self._registrations[last_key].lifetime = LifetimeScope.SCOPED
        return self
    
    def with_dependencies(self, **dependencies: Type) -> 'ServiceRegistrar':
        """
        Specify dependencies for the last registration.
        
        Args:
            **dependencies: Named dependencies
            
        Returns:
            Self for method chaining
        """
        if not self._registrations:
            raise ValueError("No registrations to modify")
        
        last_key = list(self._registrations.keys())[-1]
        self._registrations[last_key].dependencies = dependencies
        return self
    
    def build(self) -> None:
        """Apply all registrations to the container."""
        for service_type, registration in self._registrations.items():
            self.container._register_service(service_type, registration)
        self._registrations.clear()


class AutoRegistration:
    """Automatic service registration based on conventions."""
    
    @staticmethod
    def register_from_module(registrar: ServiceRegistrar, 
                           module: Any, 
                           interface_suffix: str = "Repository",
                           implementation_suffix: str = "Repository") -> ServiceRegistrar:
        """
        Auto-register services from a module based on naming conventions.
        
        Args:
            registrar: Service registrar
            module: Module to scan for services
            interface_suffix: Suffix for interface classes
            implementation_suffix: Suffix for implementation classes
            
        Returns:
            The registrar for chaining
        """
        # Get all classes from module
        classes = {}
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                classes[name] = obj
        
        # Find interface/implementation pairs
        for name, cls in classes.items():
            if name.endswith(interface_suffix):
                # Look for corresponding implementation
                impl_name = name.replace(interface_suffix, implementation_suffix)
                if impl_name in classes:
                    interface = cls
                    implementation = classes[impl_name]
                    
                    # Check if implementation actually implements interface
                    if issubclass(implementation, interface):
                        registrar.register_type(interface, implementation)
        
        return registrar
    
    @staticmethod
    def register_repositories(registrar: ServiceRegistrar,
                            repository_module: Any,
                            implementation_module: Any) -> ServiceRegistrar:
        """
        Auto-register repository interfaces with their implementations.
        
        Args:
            registrar: Service registrar
            repository_module: Module containing repository interfaces
            implementation_module: Module containing implementations
            
        Returns:
            The registrar for chaining
        """
        # Get repository interfaces
        interfaces = {}
        for name in dir(repository_module):
            obj = getattr(repository_module, name)
            if (inspect.isclass(obj) and 
                obj.__module__ == repository_module.__name__ and
                name.endswith('Repository')):
                interfaces[name] = obj
        
        # Get implementations
        implementations = {}
        for name in dir(implementation_module):
            obj = getattr(implementation_module, name)
            if (inspect.isclass(obj) and 
                obj.__module__ == implementation_module.__name__):
                implementations[name] = obj
        
        # Match and register
        for interface_name, interface_cls in interfaces.items():
            # Look for SQLite implementation
            impl_name = f"SQLite{interface_name}"
            if impl_name in implementations:
                impl_cls = implementations[impl_name]
                if issubclass(impl_cls, interface_cls):
                    registrar.register_type(interface_cls, impl_cls).as_singleton()
        
        return registrar


def create_factory_with_dependencies(implementation_type: Type[T], 
                                   dependencies: Optional[Dict[str, Type]] = None) -> ServiceFactory:
    """
    Create a factory function that resolves dependencies automatically.
    
    Args:
        implementation_type: Type to instantiate
        dependencies: Optional explicit dependencies
        
    Returns:
        Factory function
    """
    def factory(container: 'ServiceContainer') -> T:
        # Get constructor signature
        signature = inspect.signature(implementation_type.__init__)
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            # Use explicit dependency if provided
            if dependencies and param_name in dependencies:
                dependency_type = dependencies[param_name]
                kwargs[param_name] = container.get_service(dependency_type)
            
            # Try to resolve by type annotation
            elif param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = container.get_service(param.annotation)
                except Exception:
                    # If we can't resolve and no default, raise error
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(
                            f"Cannot resolve dependency '{param_name}' of type '{param.annotation}' "
                            f"for {implementation_type.__name__}"
                        )
        
        return implementation_type(**kwargs)
    
    return factory