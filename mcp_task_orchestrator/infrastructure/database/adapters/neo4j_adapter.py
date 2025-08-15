"""
Neo4j adapter for graph storage.

This module provides a graph database adapter for Neo4j,
enabling relationship management and knowledge graph operations.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncIterator
import logging
from datetime import datetime

try:
    from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    AsyncGraphDatabase = None
    AsyncDriver = None
    AsyncSession = None

from ..base import GraphDatabaseAdapter

logger = logging.getLogger(__name__)


class Neo4jAdapter(GraphDatabaseAdapter[AsyncSession]):
    """
    Neo4j graph database adapter.
    
    This adapter provides graph storage and relationship management
    using Neo4j for complex queries and knowledge graphs.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the Neo4j adapter.
        
        Args:
            connection_string: Neo4j connection string (e.g., 'neo4j://localhost:7687')
            **kwargs: Additional configuration options:
                - username: Neo4j username
                - password: Neo4j password
                - database: Database name (default: 'neo4j')
                - max_connection_lifetime: Connection lifetime in seconds
                - max_connection_pool_size: Maximum pool size
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver is not installed. Install with: pip install neo4j")
        
        super().__init__(connection_string, **kwargs)
        
        # Authentication
        self.username = kwargs.get('username', 'neo4j')
        self.password = kwargs.get('password')
        self.database = kwargs.get('database', 'neo4j')
        
        # Connection pool settings
        self.max_connection_lifetime = kwargs.get('max_connection_lifetime', 3600)
        self.max_connection_pool_size = kwargs.get('max_connection_pool_size', 100)
        
        # Driver management
        self._driver: Optional[AsyncDriver] = None
    
    async def initialize(self) -> None:
        """Initialize the Neo4j driver."""
        if self._initialized:
            return
        
        try:
            # Create Neo4j driver
            auth = (self.username, self.password) if self.password else None
            
            self._driver = AsyncGraphDatabase.driver(
                self.connection_string,
                auth=auth,
                max_connection_lifetime=self.max_connection_lifetime,
                max_connection_pool_size=self.max_connection_pool_size
            )
            
            # Verify connectivity
            await self._driver.verify_connectivity()
            
            self._initialized = True
            logger.info(f"Initialized Neo4j driver for {self.connection_string}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            if self._driver:
                await self._driver.close()
                self._driver = None
            raise
    
    async def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver:
            try:
                await self._driver.close()
                logger.info("Closed Neo4j driver")
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")
            finally:
                self._driver = None
                self._initialized = False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on Neo4j.
        
        Returns:
            Dict containing health status and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            async with self._driver.session(database=self.database) as session:
                # Test query
                result = await session.run("RETURN 1 as test")
                await result.single()
                
                # Get database info
                info_result = await session.run("CALL dbms.components() YIELD name, versions")
                components = await info_result.data()
                
                return {
                    "status": "healthy",
                    "database_type": self.database_type.value,
                    "database": self.database,
                    "components": components,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return {
                "status": "unhealthy",
                "database_type": self.database_type.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """
        Create a transaction context.
        
        Yields:
            Neo4j session within a transaction
        """
        if not self._initialized:
            await self.initialize()
        
        async with self._driver.session(database=self.database) as session:
            async with session.begin_transaction() as tx:
                # Create a wrapper that provides the session interface
                # but uses the transaction for queries
                class TransactionSession:
                    def __init__(self, transaction):
                        self._tx = transaction
                    
                    async def run(self, query, parameters=None):
                        return await self._tx.run(query, parameters)
                
                try:
                    yield TransactionSession(tx)
                except Exception as e:
                    logger.error(f"Transaction failed: {e}")
                    raise
    
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
        if not self._initialized:
            await self.initialize()
        
        try:
            labels_str = ":".join(labels)
            query = f"CREATE (n:{labels_str} $properties) RETURN id(n) as node_id, n"
            
            async with self._driver.session(database=self.database) as session:
                result = await session.run(query, {"properties": properties})
                record = await result.single()
                
                node_data = dict(record["n"])
                node_data["id"] = record["node_id"]
                
                return node_data
                
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            raise
    
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
        if not self._initialized:
            await self.initialize()
        
        try:
            props_clause = "$properties" if properties else "{}"
            query = f"""
            MATCH (a), (b)
            WHERE id(a) = $from_id AND id(b) = $to_id
            CREATE (a)-[r:{relationship_type} {props_clause}]->(b)
            RETURN id(r) as rel_id, r
            """
            
            params = {
                "from_id": int(from_node_id),
                "to_id": int(to_node_id)
            }
            if properties:
                params["properties"] = properties
            
            async with self._driver.session(database=self.database) as session:
                result = await session.run(query, params)
                record = await result.single()
                
                rel_data = dict(record["r"])
                rel_data["id"] = record["rel_id"]
                
                return rel_data
                
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            raise
    
    async def query(
        self,
        cypher: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            cypher: Cypher query
            params: Query parameters
            
        Returns:
            Query results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            async with self._driver.session(database=self.database) as session:
                result = await session.run(cypher, params or {})
                return await result.data()
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
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
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build relationship type filter
            rel_filter = ""
            if relationship_types:
                rel_types = "|".join(relationship_types)
                rel_filter = f":{rel_types}"
            
            query = f"""
            MATCH path = (start)-[{rel_filter}*1..{max_depth}]-(end)
            WHERE id(start) = $start_id AND id(end) = $end_id
            RETURN path,
                   [node in nodes(path) | {{id: id(node), labels: labels(node), properties: properties(node)}}] as nodes,
                   [rel in relationships(path) | {{id: id(rel), type: type(rel), properties: properties(rel)}}] as relationships,
                   length(path) as path_length
            ORDER BY path_length
            """
            
            params = {
                "start_id": int(start_node_id),
                "end_id": int(end_node_id)
            }
            
            async with self._driver.session(database=self.database) as session:
                result = await session.run(query, params)
                return await result.data()
                
        except Exception as e:
            logger.error(f"Path finding failed: {e}")
            raise