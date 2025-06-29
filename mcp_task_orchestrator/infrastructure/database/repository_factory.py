"""
Repository Factory for dependency injection.

This module provides factory functions to create repository instances,
enabling easy switching between different implementations and supporting
dependency injection patterns.
"""

from typing import Dict, Any, Protocol
from pathlib import Path

from ...domain.repositories import (
    TaskRepository,
    StateRepository,
    SpecialistRepository
)
from .connection_manager import DatabaseConnectionManager
from .sqlite import (
    SQLiteTaskRepository,
    SQLiteStateRepository,
    SQLiteSpecialistRepository
)


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    def __init__(self, database_url: str, **connection_params):
        """
        Initialize the repository factory.
        
        Args:
            database_url: Database connection URL
            **connection_params: Additional connection parameters
        """
        self.database_url = database_url
        self.connection_params = connection_params
        self._connection_manager = None
    
    @property
    def connection_manager(self) -> DatabaseConnectionManager:
        """Get or create the connection manager."""
        if self._connection_manager is None:
            self._connection_manager = DatabaseConnectionManager(
                self.database_url,
                **self.connection_params
            )
        return self._connection_manager
    
    def create_task_repository(self) -> TaskRepository:
        """
        Create a task repository instance.
        
        Returns:
            TaskRepository implementation
        """
        return SQLiteTaskRepository(self.connection_manager)
    
    def create_state_repository(self) -> StateRepository:
        """
        Create a state repository instance.
        
        Returns:
            StateRepository implementation
        """
        return SQLiteStateRepository(self.connection_manager)
    
    def create_specialist_repository(self) -> SpecialistRepository:
        """
        Create a specialist repository instance.
        
        Returns:
            SpecialistRepository implementation
        """
        return SQLiteSpecialistRepository(self.connection_manager)
    
    def close(self):
        """Close all connections and clean up resources."""
        if self._connection_manager:
            self._connection_manager.close_all()
            self._connection_manager = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        self.close()


def create_repository_factory(config: Dict[str, Any]) -> RepositoryFactory:
    """
    Create a repository factory from configuration.
    
    Args:
        config: Configuration dictionary with database settings
        
    Returns:
        Configured RepositoryFactory instance
    """
    database_config = config.get('database', {})
    database_url = database_config.get('url', 'sqlite:///task_orchestrator.db')
    
    # Extract connection parameters
    connection_params = {
        'timeout': database_config.get('timeout', 30.0),
        'check_same_thread': database_config.get('check_same_thread', False)
    }
    
    return RepositoryFactory(database_url, **connection_params)