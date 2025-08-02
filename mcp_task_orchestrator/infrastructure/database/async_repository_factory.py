"""
Async repository factory using the new database adapter system.

This module provides an async-first repository factory that leverages
the unified database manager for multi-database operations.
"""

from typing import Dict, Any, Optional
import logging

from ...domain.repositories import (
    AsyncTaskRepository,
    StateRepository,
    SpecialistRepository
)
from .unified_manager import UnifiedDatabaseManager
from .async_repositories import (
    AsyncSQLiteTaskRepository,
    AsyncSQLiteStateRepository,
    AsyncSQLiteSpecialistRepository
)

logger = logging.getLogger(__name__)


class AsyncRepositoryFactory:
    """
    Async repository factory using the unified database manager.
    
    This factory creates async repositories that work with the new
    multi-database architecture while maintaining compatibility
    with existing domain interfaces.
    """
    
    def __init__(self, db_manager: UnifiedDatabaseManager):
        """
        Initialize the async repository factory.
        
        Args:
            db_manager: Unified database manager instance
        """
        self.db_manager = db_manager
        self._repositories = {}
    
    async def initialize(self) -> None:
        """Initialize the database manager."""
        await self.db_manager.initialize()
    
    async def close(self) -> None:
        """Close all resources."""
        await self.db_manager.close()
        self._repositories.clear()
    
    async def create_task_repository(self) -> AsyncTaskRepository:
        """
        Create an async task repository instance.
        
        Returns:
            Async TaskRepository implementation
        """
        if 'task' not in self._repositories:
            if not self.db_manager.operational:
                raise RuntimeError("Operational database not available")
            
            self._repositories['task'] = AsyncSQLiteTaskRepository(
                self.db_manager.operational
            )
        
        return self._repositories['task']
    
    async def create_state_repository(self) -> StateRepository:
        """
        Create an async state repository instance.
        
        Returns:
            Async StateRepository implementation
        """
        if 'state' not in self._repositories:
            if not self.db_manager.operational:
                raise RuntimeError("Operational database not available")
            
            self._repositories['state'] = AsyncSQLiteStateRepository(
                self.db_manager.operational
            )
        
        return self._repositories['state']
    
    async def create_specialist_repository(self) -> SpecialistRepository:
        """
        Create an async specialist repository instance.
        
        Returns:
            Async SpecialistRepository implementation
        """
        if 'specialist' not in self._repositories:
            if not self.db_manager.operational:
                raise RuntimeError("Operational database not available")
            
            self._repositories['specialist'] = AsyncSQLiteSpecialistRepository(
                self.db_manager.operational
            )
        
        return self._repositories['specialist']
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def create_async_repository_factory(config: Dict[str, Any]) -> AsyncRepositoryFactory:
    """
    Create an async repository factory from configuration.
    
    Args:
        config: Configuration dictionary with database settings
        Example:
        {
            "databases": {
                "operational": {
                    "url": "sqlite:///tasks.db",
                    "timeout": 30.0
                },
                "vector": {
                    "url": "chromadb://localhost:8000",
                    "persist_directory": "./chroma_db"
                },
                "graph": {
                    "url": "neo4j://localhost:7687",
                    "username": "neo4j",
                    "password": "password"
                }
            }
        }
        
    Returns:
        Configured AsyncRepositoryFactory
    """
    database_config = config.get('databases', {})
    
    # Ensure operational database configuration exists
    if 'operational' not in database_config:
        # Provide default SQLite configuration
        database_config['operational'] = {
            'url': 'sqlite:///task_orchestrator.db',
            'timeout': 30.0
        }
    
    # Create unified database manager
    db_manager = UnifiedDatabaseManager(database_config)
    
    # Create and return factory
    factory = AsyncRepositoryFactory(db_manager)
    return factory


class RepositoryConfiguration:
    """Configuration helper for repository setup."""
    
    @staticmethod
    def create_sqlite_config(
        database_path: str = "task_orchestrator.db",
        timeout: float = 30.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create SQLite configuration.
        
        Args:
            database_path: Path to SQLite database file
            timeout: Connection timeout in seconds
            **kwargs: Additional SQLite options
            
        Returns:
            Configuration dictionary
        """
        return {
            "databases": {
                "operational": {
                    "url": f"sqlite:///{database_path}",
                    "timeout": timeout,
                    **kwargs
                }
            }
        }
    
    @staticmethod
    def create_multi_db_config(
        sqlite_path: str = "task_orchestrator.db",
        chroma_persist_dir: Optional[str] = None,
        neo4j_uri: Optional[str] = None,
        neo4j_auth: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Create multi-database configuration.
        
        Args:
            sqlite_path: Path to SQLite database file
            chroma_persist_dir: ChromaDB persistence directory
            neo4j_uri: Neo4j connection URI
            neo4j_auth: Neo4j authentication tuple (username, password)
            
        Returns:
            Configuration dictionary
        """
        config = {
            "databases": {
                "operational": {
                    "url": f"sqlite:///{sqlite_path}",
                    "timeout": 30.0
                }
            }
        }
        
        if chroma_persist_dir:
            config["databases"]["vector"] = {
                "url": "chromadb://localhost",
                "persist_directory": chroma_persist_dir
            }
        
        if neo4j_uri and neo4j_auth:
            config["databases"]["graph"] = {
                "url": neo4j_uri,
                "username": neo4j_auth[0],
                "password": neo4j_auth[1]
            }
        
        return config