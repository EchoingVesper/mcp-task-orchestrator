"""
ChromaDB adapter for vector storage.

This module provides a vector database adapter for ChromaDB,
enabling semantic search and RAG operations.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncIterator
import logging
from datetime import datetime

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

from ..base import VectorDatabaseAdapter

logger = logging.getLogger(__name__)


class ChromaDBAdapter(VectorDatabaseAdapter[Any]):
    """
    ChromaDB vector database adapter.
    
    This adapter provides vector storage and semantic search capabilities
    using ChromaDB for RAG operations in the task orchestrator.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the ChromaDB adapter.
        
        Args:
            connection_string: ChromaDB connection string (e.g., 'chromadb://localhost:8000')
            **kwargs: Additional configuration options:
                - persist_directory: Directory for persistent storage
                - client_settings: ChromaDB client settings
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is not installed. Install with: pip install chromadb")
        
        super().__init__(connection_string, **kwargs)
        
        # Configuration
        self.persist_directory = kwargs.get('persist_directory')
        self.client_settings = kwargs.get('client_settings', {})
        
        # Client management
        self._client = None
        self._collections = {}
    
    async def initialize(self) -> None:
        """Initialize the ChromaDB client."""
        if self._initialized:
            return
        
        try:
            # Create ChromaDB client
            if self.persist_directory:
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=self.client_settings
                )
            else:
                self._client = chromadb.Client(settings=self.client_settings)
            
            self._initialized = True
            logger.info("Initialized ChromaDB client")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def close(self) -> None:
        """Close the ChromaDB client."""
        if self._client:
            try:
                # ChromaDB doesn't require explicit closing
                self._collections.clear()
                self._client = None
                logger.info("Closed ChromaDB client")
            except Exception as e:
                logger.error(f"Error closing ChromaDB client: {e}")
            finally:
                self._initialized = False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on ChromaDB.
        
        Returns:
            Dict containing health status and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Test by listing collections
            collections = self._client.list_collections()
            
            return {
                "status": "healthy",
                "database_type": self.database_type.value,
                "collection_count": len(collections),
                "collections": [c.name for c in collections],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "database_type": self.database_type.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Any]:
        """
        Create a transaction context.
        
        Note: ChromaDB doesn't support traditional transactions,
        so this provides a context for batch operations.
        
        Yields:
            ChromaDB client for batch operations
        """
        if not self._initialized:
            await self.initialize()
        
        # ChromaDB doesn't have transactions, so we just yield the client
        try:
            yield self._client
        except Exception as e:
            logger.error(f"ChromaDB operation failed: {e}")
            raise
    
    async def upsert_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Insert or update embeddings in ChromaDB.
        
        Args:
            embeddings: List of embeddings with metadata
            namespace: Collection name (defaults to 'default')
            
        Returns:
            Operation result metadata
        """
        if not self._initialized:
            await self.initialize()
        
        collection_name = namespace or "default"
        
        try:
            # Get or create collection
            collection = self._client.get_or_create_collection(name=collection_name)
            
            # Prepare data for ChromaDB
            ids = [emb["id"] for emb in embeddings]
            vectors = [emb["vector"] for emb in embeddings]
            metadatas = [emb.get("metadata", {}) for emb in embeddings]
            documents = [emb.get("document", "") for emb in embeddings]
            
            # Upsert embeddings
            collection.upsert(
                ids=ids,
                embeddings=vectors,
                metadatas=metadatas,
                documents=documents
            )
            
            return {
                "status": "success",
                "collection": collection_name,
                "upserted_count": len(embeddings),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to upsert embeddings: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in ChromaDB.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter: Metadata filters (where clause)
            namespace: Collection name (defaults to 'default')
            
        Returns:
            List of similar items with scores
        """
        if not self._initialized:
            await self.initialize()
        
        collection_name = namespace or "default"
        
        try:
            # Get collection
            collection = self._client.get_collection(name=collection_name)
            
            # Perform search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter
            )
            
            # Format results
            search_results = []
            for i in range(len(results['ids'][0])):
                search_results.append({
                    "id": results['ids'][0][i],
                    "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
                    "document": results['documents'][0][i] if results['documents'][0] else ""
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def delete_embeddings(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete embeddings by ID from ChromaDB.
        
        Args:
            ids: List of embedding IDs to delete
            namespace: Collection name (defaults to 'default')
            
        Returns:
            Operation result metadata
        """
        if not self._initialized:
            await self.initialize()
        
        collection_name = namespace or "default"
        
        try:
            # Get collection
            collection = self._client.get_collection(name=collection_name)
            
            # Delete embeddings
            collection.delete(ids=ids)
            
            return {
                "status": "success",
                "collection": collection_name,
                "deleted_count": len(ids),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete embeddings: {e}")
            raise