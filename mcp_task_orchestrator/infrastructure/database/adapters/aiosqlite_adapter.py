"""
Async SQLite adapter using aiosqlite.

This module provides an async implementation of the OperationalDatabaseAdapter
for SQLite databases, enabling non-blocking database operations.
"""

import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, AsyncIterator
import logging
import asyncio
from datetime import datetime

from ..base import OperationalDatabaseAdapter

logger = logging.getLogger(__name__)


class AioSQLiteAdapter(OperationalDatabaseAdapter[aiosqlite.Connection]):
    """
    Async SQLite database adapter using aiosqlite.
    
    This adapter provides async operations for SQLite databases,
    suitable for the operational data store in the task orchestrator.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize the AioSQLite adapter.
        
        Args:
            connection_string: SQLite connection string (e.g., 'sqlite:///path/to/db.sqlite')
            **kwargs: Additional configuration options:
                - timeout: Connection timeout in seconds (default: 30.0)
                - check_same_thread: SQLite thread checking (default: False)
                - journal_mode: Journal mode (default: 'WAL')
                - synchronous: Synchronous mode (default: 'NORMAL')
        """
        super().__init__(connection_string, **kwargs)
        
        # Extract database path from connection string
        self.database_path = self._extract_path_from_url(connection_string)
        
        # Configuration
        self.timeout = kwargs.get('timeout', 30.0)
        self.check_same_thread = kwargs.get('check_same_thread', False)
        self.journal_mode = kwargs.get('journal_mode', 'WAL')
        self.synchronous = kwargs.get('synchronous', 'NORMAL')
        
        # Connection pool settings
        self.pool_size = kwargs.get('pool_size', 5)
        self.max_overflow = kwargs.get('max_overflow', 10)
        
        # Connection management
        self._connection: Optional[aiosqlite.Connection] = None
        self._connection_lock = asyncio.Lock()
        self._transaction_depth = 0
    
    def _extract_path_from_url(self, connection_string: str) -> Path:
        """Extract file path from SQLite URL."""
        if connection_string.startswith('sqlite:///'):
            path = Path(connection_string[10:])
        elif connection_string.startswith('sqlite://'):
            path = Path(connection_string[9:])
        else:
            path = Path(connection_string)
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    async def initialize(self) -> None:
        """Initialize the database connection and set pragmas."""
        if self._initialized:
            return
        
        async with self._connection_lock:
            if self._initialized:
                return
            
            try:
                # Create connection
                self._connection = await aiosqlite.connect(
                    str(self.database_path),
                    timeout=self.timeout,
                    check_same_thread=self.check_same_thread
                )
                
                # Set row factory for dict-like access
                self._connection.row_factory = aiosqlite.Row
                
                # Set pragmas for performance and reliability
                await self._connection.execute(f"PRAGMA journal_mode={self.journal_mode}")
                await self._connection.execute(f"PRAGMA synchronous={self.synchronous}")
                await self._connection.execute("PRAGMA foreign_keys=ON")
                await self._connection.execute("PRAGMA temp_store=MEMORY")
                
                # Enable query optimization
                await self._connection.execute("PRAGMA optimize")
                
                await self._connection.commit()
                
                self._initialized = True
                logger.info(f"Initialized AioSQLite connection to {self.database_path}")
                
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                if self._connection:
                    await self._connection.close()
                    self._connection = None
                raise
    
    async def close(self) -> None:
        """Close the database connection."""
        async with self._connection_lock:
            if self._connection:
                try:
                    await self._connection.close()
                    logger.info("Closed AioSQLite connection")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
                finally:
                    self._connection = None
                    self._initialized = False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database.
        
        Returns:
            Dict containing health status and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Test query
            async with self._connection.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            
            # Get database stats
            async with self._connection.execute("PRAGMA page_count") as cursor:
                page_count = (await cursor.fetchone())[0]
            
            async with self._connection.execute("PRAGMA page_size") as cursor:
                page_size = (await cursor.fetchone())[0]
            
            size_bytes = page_count * page_size
            
            return {
                "status": "healthy",
                "database_type": self.database_type.value,
                "path": str(self.database_path),
                "size_bytes": size_bytes,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "journal_mode": self.journal_mode,
                "synchronous": self.synchronous,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "database_type": self.database_type.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[aiosqlite.Connection]:
        """
        Create a transaction context.
        
        aiosqlite automatically handles transactions, so we just provide
        a context where all operations are part of the same transaction.
        
        Yields:
            The database connection within a transaction
        """
        if not self._initialized:
            await self.initialize()
        
        async with self._connection_lock:
            self._transaction_depth += 1
            
            # For aiosqlite, we don't need explicit BEGIN/COMMIT
            # The connection automatically handles transactions
            try:
                yield self._connection
                # Commit happens automatically unless an exception occurs
                
            except Exception as e:
                # Rollback will happen automatically on exception
                logger.error(f"Transaction failed: {e}")
                raise
                
            finally:
                self._transaction_depth -= 1
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert named parameters to positional if using ? placeholders
            if params and '?' in query and ':' not in query:
                # Extract parameter values in order for positional parameters
                param_values = list(params.values())
                async with self._connection.execute(query, param_values) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                # Use named parameters
                async with self._connection.execute(query, params or {}) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return single result.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Single result dictionary or None
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert named parameters to positional if using ? placeholders
            if params and '?' in query and ':' not in query:
                # Extract parameter values in order for positional parameters
                param_values = list(params.values())
                async with self._connection.execute(query, param_values) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
            else:
                # Use named parameters
                async with self._connection.execute(query, params or {}) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter dictionaries
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Use executemany for efficiency
            await self._connection.executemany(query, params_list)
            await self._connection.commit()
            
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise
    
    async def create_tables(self, schema: str) -> None:
        """
        Create tables from a schema string.
        
        Args:
            schema: SQL schema definition
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            await self._connection.executescript(schema)
            await self._connection.commit()
            logger.info("Database schema created successfully")
            
        except Exception as e:
            logger.error(f"Schema creation failed: {e}")
            raise