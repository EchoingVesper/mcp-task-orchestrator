"""
Abstract base classes for database adapters.

This module provides the foundation for supporting multiple database types
(operational, vector, graph) with a unified interface.
"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncIterator, TypeVar, Generic
from enum import Enum
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseType(Enum):
    """Supported database types."""
    OPERATIONAL = "operational"  # SQLite/PostgreSQL for transactional data
    VECTOR = "vector"           # Pinecone/Weaviate/ChromaDB for embeddings
    GRAPH = "graph"             # Neo4j/ArangoDB for relationships


class DatabaseAdapter(ABC, Generic[T]):
    """
    Abstract base class for database adapters.
    
    Each database type (operational, vector, graph) must implement this interface
    to ensure consistent behavior across different storage backends.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the database adapter.
        
        Args:
            connection_string: Database-specific connection string
            **kwargs: Additional database-specific configuration
        """
        self.connection_string = connection_string
        self.config = kwargs
        self._initialized = False
    
    @property
    @abstractmethod
    def database_type(self) -> DatabaseType:
        """Return the type of database this adapter handles."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the database connection and perform any setup.
        
        This method should be idempotent.
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close all database connections and clean up resources."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database.
        
        Returns:
            Dict containing health status and metadata
        """
        pass
    
    @asynccontextmanager
    @abstractmethod
    async def transaction(self) -> AsyncIterator[T]:
        """
        Create a transaction context.
        
        Yields:
            Transaction object appropriate for the database type
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class OperationalDatabaseAdapter(DatabaseAdapter[T]):
    """
    Abstract base for operational databases (SQLite, PostgreSQL, etc).
    
    These databases handle transactional data, task management, and state.
    """
    
    @property
    def database_type(self) -> DatabaseType:
        return DatabaseType.OPERATIONAL
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        pass
    
    @abstractmethod
    async def execute_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return single result.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Single result dictionary or None
        """
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter dictionaries
        """
        pass


class VectorDatabaseAdapter(DatabaseAdapter[T]):
    """
    Abstract base for vector databases (Pinecone, Weaviate, ChromaDB, etc).
    
    These databases handle embeddings, semantic search, and RAG operations.
    """
    
    @property
    def database_type(self) -> DatabaseType:
        return DatabaseType.VECTOR
    
    @abstractmethod
    async def upsert_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert or update embeddings.
        
        Args:
            embeddings: List of embeddings with metadata
            namespace: Optional namespace/collection
            
        Returns:
            Operation result metadata
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter: Metadata filters
            namespace: Optional namespace/collection
            
        Returns:
            List of similar items with scores
        """
        pass
    
    @abstractmethod
    async def delete_embeddings(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete embeddings by ID.
        
        Args:
            ids: List of embedding IDs to delete
            namespace: Optional namespace/collection
            
        Returns:
            Operation result metadata
        """
        pass


class GraphDatabaseAdapter(DatabaseAdapter[T]):
    """
    Abstract base for graph databases (Neo4j, ArangoDB, Neptune, etc).
    
    These databases handle relationships, dependencies, and knowledge graphs.
    """
    
    @property
    def database_type(self) -> DatabaseType:
        return DatabaseType.GRAPH
    
    @abstractmethod
    async def create_node(
        self,
        labels: List[str],
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a node in the graph.
        
        Args:
            labels: Node labels/types
            properties: Node properties
            
        Returns:
            Created node with ID
        """
        pass
    
    @abstractmethod
    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between nodes.
        
        Args:
            from_node_id: Source node ID
            to_node_id: Target node ID
            relationship_type: Type of relationship
            properties: Optional relationship properties
            
        Returns:
            Created relationship with ID
        """
        pass
    
    @abstractmethod
    async def query(
        self,
        cypher: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a graph query (Cypher or similar).
        
        Args:
            cypher: Query in graph query language
            params: Query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    async def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 5,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find paths between nodes.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Ending node ID
            max_depth: Maximum path length
            relationship_types: Optional filter for relationship types
            
        Returns:
            List of paths with nodes and relationships
        """
        pass


class DatabaseAdapterFactory:
    """Factory for creating database adapters based on connection strings."""
    
    _adapters: Dict[str, type[DatabaseAdapter]] = {}
    
    @classmethod
    def register(cls, scheme: str, adapter_class: type[DatabaseAdapter]) -> None:
        """
        Register a database adapter for a connection scheme.
        
        Args:
            scheme: Connection string scheme (e.g., 'sqlite', 'postgresql', 'neo4j')
            adapter_class: Adapter class to use for this scheme
        """
        cls._adapters[scheme] = adapter_class
    
    @classmethod
    def create(cls, connection_string: str, **kwargs) -> DatabaseAdapter:
        """
        Create a database adapter from a connection string.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional configuration
            
        Returns:
            Configured database adapter
            
        Raises:
            ValueError: If no adapter is registered for the scheme
        """
        scheme = connection_string.split('://')[0].lower()
        
        if scheme not in cls._adapters:
            raise ValueError(f"No adapter registered for scheme: {scheme}")
        
        adapter_class = cls._adapters[scheme]
        return adapter_class(connection_string, **kwargs)
    
    @classmethod
    def list_schemes(cls) -> List[str]:
        """List all registered connection schemes."""
        return list(cls._adapters.keys())