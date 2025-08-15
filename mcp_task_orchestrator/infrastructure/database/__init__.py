"""
Database infrastructure implementations.

This package contains concrete implementations of the repository interfaces
defined in the domain layer, along with database-specific utilities.

The database layer supports multiple storage backends:
- Operational databases (SQLite, PostgreSQL) for transactional data
- Vector databases (ChromaDB, Pinecone) for embeddings and semantic search
- Graph databases (Neo4j, ArangoDB) for relationships and knowledge graphs
"""

from .base import (
    DatabaseType,
    DatabaseAdapter,
    OperationalDatabaseAdapter,
    VectorDatabaseAdapter,
    GraphDatabaseAdapter,
    DatabaseAdapterFactory
)

from .unified_manager import UnifiedDatabaseManager, create_unified_manager

# Legacy imports for backward compatibility
from .connection_manager import DatabaseConnectionManager
from .repository_factory import RepositoryFactory, create_repository_factory

__all__ = [
    # Modern multi-database architecture
    'DatabaseType',
    'DatabaseAdapter',
    'OperationalDatabaseAdapter', 
    'VectorDatabaseAdapter',
    'GraphDatabaseAdapter',
    'DatabaseAdapterFactory',
    'UnifiedDatabaseManager',
    'create_unified_manager',
    
    # Legacy compatibility
    'DatabaseConnectionManager',
    'RepositoryFactory',
    'create_repository_factory',
]