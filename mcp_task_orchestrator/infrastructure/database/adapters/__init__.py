"""
Database adapters for different storage backends.

This module provides implementations of the database adapter interfaces
for various database types (operational, vector, graph).
"""

from .aiosqlite_adapter import AioSQLiteAdapter
from ..base import DatabaseAdapterFactory

# Register operational database adapters
DatabaseAdapterFactory.register('sqlite', AioSQLiteAdapter)

# Register vector database adapters (optional dependencies)
try:
    from .chromadb_adapter import ChromaDBAdapter
    DatabaseAdapterFactory.register('chromadb', ChromaDBAdapter)
except ImportError:
    ChromaDBAdapter = None

# Register graph database adapters (optional dependencies)
try:
    from .neo4j_adapter import Neo4jAdapter
    DatabaseAdapterFactory.register('neo4j', Neo4jAdapter)
except ImportError:
    Neo4jAdapter = None

__all__ = [
    'AioSQLiteAdapter',
    'DatabaseAdapterFactory',
]

# Add optional adapters to exports if available
if ChromaDBAdapter:
    __all__.append('ChromaDBAdapter')
if Neo4jAdapter:
    __all__.append('Neo4jAdapter')