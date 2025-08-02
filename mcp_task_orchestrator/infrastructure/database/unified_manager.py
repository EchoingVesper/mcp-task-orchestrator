"""
Unified database manager for multi-database orchestration.

This module provides a centralized interface for managing operational,
vector, and graph databases in the task orchestrator.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio

from .base import DatabaseAdapter, DatabaseType, OperationalDatabaseAdapter, VectorDatabaseAdapter, GraphDatabaseAdapter
from .adapters import DatabaseAdapterFactory

logger = logging.getLogger(__name__)


class UnifiedDatabaseManager:
    """
    Unified manager for multiple database types.
    
    This manager coordinates operational, vector, and graph databases,
    providing a single interface for complex operations that span
    multiple storage backends.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the unified database manager.
        
        Args:
            config: Configuration dictionary containing database settings
                Example:
                {
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
        """
        self.config = config
        self._adapters: Dict[DatabaseType, DatabaseAdapter] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all configured database adapters."""
        if self._initialized:
            return
        
        try:
            initialization_tasks = []
            
            # Initialize operational database (required)
            if "operational" in self.config:
                op_config = self.config["operational"]
                adapter = DatabaseAdapterFactory.create(
                    op_config["url"],
                    **{k: v for k, v in op_config.items() if k != "url"}
                )
                self._adapters[DatabaseType.OPERATIONAL] = adapter
                initialization_tasks.append(adapter.initialize())
            else:
                raise ValueError("Operational database configuration is required")
            
            # Initialize vector database (optional)
            if "vector" in self.config:
                vec_config = self.config["vector"]
                try:
                    adapter = DatabaseAdapterFactory.create(
                        vec_config["url"],
                        **{k: v for k, v in vec_config.items() if k != "url"}
                    )
                    self._adapters[DatabaseType.VECTOR] = adapter
                    initialization_tasks.append(adapter.initialize())
                except Exception as e:
                    logger.warning(f"Vector database initialization failed: {e}")
            
            # Initialize graph database (optional)
            if "graph" in self.config:
                graph_config = self.config["graph"]
                try:
                    adapter = DatabaseAdapterFactory.create(
                        graph_config["url"],
                        **{k: v for k, v in graph_config.items() if k != "url"}
                    )
                    self._adapters[DatabaseType.GRAPH] = adapter
                    initialization_tasks.append(adapter.initialize())
                except Exception as e:
                    logger.warning(f"Graph database initialization failed: {e}")
            
            # Initialize all adapters in parallel
            await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            self._initialized = True
            logger.info(f"Initialized {len(self._adapters)} database adapters")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            await self.close()
            raise
    
    async def close(self) -> None:
        """Close all database connections."""
        if not self._initialized:
            return
        
        close_tasks = []
        for adapter in self._adapters.values():
            close_tasks.append(adapter.close())
        
        await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self._adapters.clear()
        self._initialized = False
        logger.info("Closed all database connections")
    
    @property
    def operational(self) -> Optional[OperationalDatabaseAdapter]:
        """Get the operational database adapter."""
        return self._adapters.get(DatabaseType.OPERATIONAL)
    
    @property
    def vector(self) -> Optional[VectorDatabaseAdapter]:
        """Get the vector database adapter."""
        return self._adapters.get(DatabaseType.VECTOR)
    
    @property
    def graph(self) -> Optional[GraphDatabaseAdapter]:
        """Get the graph database adapter."""
        return self._adapters.get(DatabaseType.GRAPH)
    
    def has_database(self, db_type: DatabaseType) -> bool:
        """Check if a database type is available."""
        return db_type in self._adapters
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health checks on all databases.
        
        Returns:
            Dict containing health status for each database
        """
        if not self._initialized:
            await self.initialize()
        
        health_results = {}
        
        for db_type, adapter in self._adapters.items():
            try:
                health_results[db_type.value] = await adapter.health_check()
            except Exception as e:
                health_results[db_type.value] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Overall health status
        all_healthy = all(
            result.get("status") == "healthy" 
            for result in health_results.values()
        )
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "databases": health_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_task_with_embeddings(
        self,
        task_data: Dict[str, Any],
        embedding_data: Optional[Dict[str, Any]] = None,
        graph_relationships: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a task across multiple databases.
        
        This method demonstrates how to coordinate operations across
        operational, vector, and graph databases for a single business operation.
        
        Args:
            task_data: Task data for operational database
            embedding_data: Optional embedding data for vector database
            graph_relationships: Optional relationships for graph database
            
        Returns:
            Combined result from all database operations
        """
        if not self._initialized:
            await self.initialize()
        
        results = {}
        
        try:
            # Create task in operational database
            if self.operational:
                async with self.operational.transaction() as tx:
                    # This would be replaced with actual repository operations
                    task_id = task_data.get("id", "generated_task_id")
                    results["operational"] = {"task_id": task_id, "status": "created"}
            
            # Create embeddings in vector database
            if self.vector and embedding_data:
                embedding_data["id"] = results["operational"]["task_id"]
                vector_result = await self.vector.upsert_embeddings(
                    [embedding_data],
                    namespace="tasks"
                )
                results["vector"] = vector_result
            
            # Create relationships in graph database
            if self.graph and graph_relationships:
                graph_results = []
                for relationship in graph_relationships:
                    result = await self.graph.create_relationship(
                        relationship["from_id"],
                        relationship["to_id"],
                        relationship["type"],
                        relationship.get("properties", {})
                    )
                    graph_results.append(result)
                results["graph"] = graph_results
            
            return {
                "status": "success",
                "task_id": results["operational"]["task_id"],
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-database operation failed: {e}")
            # In a real implementation, you'd implement compensation/rollback logic
            raise
    
    async def search_similar_tasks(
        self,
        query_text: str,
        top_k: int = 10,
        include_graph_context: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for similar tasks using vector similarity and optional graph context.
        
        Args:
            query_text: Query text to search for
            top_k: Number of results to return
            include_graph_context: Whether to include graph relationships
            
        Returns:
            List of similar tasks with optional graph context
        """
        if not self._initialized:
            await self.initialize()
        
        results = []
        
        try:
            # Vector search (would need embedding generation in real implementation)
            if self.vector:
                # This is a placeholder - in reality you'd generate embeddings
                # from the query_text using an embedding model
                query_embedding = [0.1] * 384  # Placeholder embedding
                
                vector_results = await self.vector.search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    namespace="tasks"
                )
                
                # Enhance with operational data
                for result in vector_results:
                    task_id = result["id"]
                    
                    # Get full task data from operational database
                    if self.operational:
                        task_data = await self.operational.execute_one(
                            "SELECT * FROM tasks WHERE id = ?",
                            {"id": task_id}
                        )
                        result["task_data"] = task_data
                    
                    # Get graph context if requested
                    if include_graph_context and self.graph:
                        relationships = await self.graph.query(
                            "MATCH (t)-[r]-(related) WHERE t.task_id = $task_id RETURN r, related",
                            {"task_id": task_id}
                        )
                        result["relationships"] = relationships
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Similar task search failed: {e}")
            raise
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def create_unified_manager(config: Dict[str, Any]) -> UnifiedDatabaseManager:
    """
    Create a unified database manager from configuration.
    
    Args:
        config: Database configuration dictionary
        
    Returns:
        Configured UnifiedDatabaseManager
    """
    return UnifiedDatabaseManager(config)