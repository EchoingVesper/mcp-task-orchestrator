"""
Lifetime managers for dependency injection.

This module provides different lifetime management strategies for services
in the dependency injection container.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
import threading
import weakref
from enum import Enum

T = TypeVar('T')


class LifetimeScope(Enum):
    """Service lifetime scopes."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class LifetimeManager(ABC, Generic[T]):
    """Abstract base class for managing service lifetimes."""
    
    def __init__(self, factory: Callable[[], T]):
        """
        Initialize the lifetime manager.
        
        Args:
            factory: Factory function to create service instances
        """
        self.factory = factory
    
    @abstractmethod
    def get_instance(self, scope_context: Optional[Dict[str, Any]] = None) -> T:
        """
        Get a service instance.
        
        Args:
            scope_context: Optional scope context for scoped services
            
        Returns:
            Service instance
        """
        pass
    
    @abstractmethod
    def dispose(self):
        """Dispose of managed instances."""
        pass


class SingletonLifetimeManager(LifetimeManager[T]):
    """Manages singleton service instances."""
    
    def __init__(self, factory: Callable[[], T]):
        super().__init__(factory)
        self._instance: Optional[T] = None
        self._lock = threading.Lock()
    
    def get_instance(self, scope_context: Optional[Dict[str, Any]] = None) -> T:
        """Get the singleton instance, creating it if necessary."""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self.factory()
        return self._instance
    
    def dispose(self):
        """Dispose of the singleton instance."""
        with self._lock:
            if self._instance is not None:
                if hasattr(self._instance, 'dispose'):
                    self._instance.dispose()
                elif hasattr(self._instance, 'close'):
                    self._instance.close()
                self._instance = None


class TransientLifetimeManager(LifetimeManager[T]):
    """Manages transient service instances (new instance every time)."""
    
    def get_instance(self, scope_context: Optional[Dict[str, Any]] = None) -> T:
        """Create a new instance every time."""
        return self.factory()
    
    def dispose(self):
        """Nothing to dispose for transient instances."""
        pass


class ScopedLifetimeManager(LifetimeManager[T]):
    """Manages scoped service instances (one per scope)."""
    
    def __init__(self, factory: Callable[[], T]):
        super().__init__(factory)
        self._instances: Dict[str, T] = {}
        self._lock = threading.Lock()
    
    def get_instance(self, scope_context: Optional[Dict[str, Any]] = None) -> T:
        """Get instance for the current scope."""
        scope_id = self._get_scope_id(scope_context)
        
        if scope_id not in self._instances:
            with self._lock:
                if scope_id not in self._instances:
                    self._instances[scope_id] = self.factory()
        
        return self._instances[scope_id]
    
    def dispose_scope(self, scope_context: Optional[Dict[str, Any]] = None):
        """Dispose of instances in a specific scope."""
        scope_id = self._get_scope_id(scope_context)
        
        with self._lock:
            if scope_id in self._instances:
                instance = self._instances.pop(scope_id)
                if hasattr(instance, 'dispose'):
                    instance.dispose()
                elif hasattr(instance, 'close'):
                    instance.close()
    
    def dispose(self):
        """Dispose of all scoped instances."""
        with self._lock:
            for instance in self._instances.values():
                if hasattr(instance, 'dispose'):
                    instance.dispose()
                elif hasattr(instance, 'close'):
                    instance.close()
            self._instances.clear()
    
    def _get_scope_id(self, scope_context: Optional[Dict[str, Any]]) -> str:
        """Get scope identifier from context."""
        if scope_context is None:
            return "default"
        
        # Use session_id if available, otherwise thread_id
        if 'session_id' in scope_context:
            return f"session_{scope_context['session_id']}"
        
        return f"thread_{threading.current_thread().ident}"


class DisposableTracker:
    """Tracks disposable objects for cleanup."""
    
    def __init__(self):
        self._disposables: Dict[int, Any] = {}
        self._lock = threading.Lock()
    
    def track(self, obj: Any):
        """Track a disposable object."""
        if hasattr(obj, 'dispose') or hasattr(obj, 'close'):
            with self._lock:
                self._disposables[id(obj)] = weakref.ref(obj, self._cleanup_ref)
    
    def dispose_all(self):
        """Dispose of all tracked objects."""
        with self._lock:
            for obj_ref in list(self._disposables.values()):
                obj = obj_ref()
                if obj is not None:
                    try:
                        if hasattr(obj, 'dispose'):
                            obj.dispose()
                        elif hasattr(obj, 'close'):
                            obj.close()
                    except Exception:
                        pass  # Ignore disposal errors
            self._disposables.clear()
    
    def _cleanup_ref(self, ref):
        """Remove weak reference when object is garbage collected."""
        with self._lock:
            # Find and remove the reference
            to_remove = None
            for obj_id, obj_ref in self._disposables.items():
                if obj_ref is ref:
                    to_remove = obj_id
                    break
            
            if to_remove is not None:
                del self._disposables[to_remove]


def create_lifetime_manager(factory: Callable[[], T], 
                          lifetime: LifetimeScope) -> LifetimeManager[T]:
    """
    Create appropriate lifetime manager for the given scope.
    
    Args:
        factory: Factory function for creating instances
        lifetime: Desired lifetime scope
        
    Returns:
        Appropriate lifetime manager
    """
    if lifetime == LifetimeScope.SINGLETON:
        return SingletonLifetimeManager(factory)
    elif lifetime == LifetimeScope.TRANSIENT:
        return TransientLifetimeManager(factory)
    elif lifetime == LifetimeScope.SCOPED:
        return ScopedLifetimeManager(factory)
    else:
        raise ValueError(f"Unknown lifetime scope: {lifetime}")


# Context manager for scoped services
class ServiceScope:
    """Context manager for scoped service lifetimes."""
    
    def __init__(self, container, scope_context: Optional[Dict[str, Any]] = None):
        """
        Initialize service scope.
        
        Args:
            container: DI container
            scope_context: Optional scope context
        """
        self.container = container
        self.scope_context = scope_context or {}
        self._original_context = None
    
    def __enter__(self):
        """Enter the scope."""
        self._original_context = getattr(self.container, '_current_scope_context', None)
        self.container._current_scope_context = self.scope_context
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the scope and dispose scoped services."""
        try:
            # Dispose scoped services
            for service_key, manager in self.container._services.items():
                if isinstance(manager, ScopedLifetimeManager):
                    manager.dispose_scope(self.scope_context)
        finally:
            # Restore original context
            self.container._current_scope_context = self._original_context