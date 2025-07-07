"""
Database connection management.

This module provides centralized database connection management with
connection pooling, thread safety, and proper resource cleanup.
"""

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages SQLite database connections with thread safety."""
    
    def __init__(self, database_url: str, **connection_params):
        """
        Initialize the connection manager.
        
        Args:
            database_url: SQLite database URL (e.g., 'sqlite:///path/to/db.sqlite')
            **connection_params: Additional connection parameters
        """
        self.database_path = self._extract_path_from_url(database_url)
        self.connection_params = {
            'check_same_thread': False,
            'timeout': 30.0,
            **connection_params
        }
        self._local = threading.local()
        self._lock = threading.Lock()
        
        # Ensure database directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema if needed
        self._initialize_database()
    
    def _extract_path_from_url(self, database_url: str) -> Path:
        """Extract file path from SQLite URL."""
        if database_url.startswith('sqlite:///'):
            return Path(database_url[10:])
        elif database_url.startswith('sqlite://'):
            return Path(database_url[9:])
        else:
            return Path(database_url)
    
    def _initialize_database(self):
        """Initialize database with pragma settings."""
        with self.get_connection() as conn:
            # Set pragmas for better performance and reliability
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection for the current thread.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.database_path),
                **self.connection_params
            )
            # Enable row factory for dict-like access
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception as e:
            logger.error(f"Database error: {e}")
            if self._local.connection:
                self._local.connection.rollback()
            raise
        finally:
            # Note: We don't close the connection here to allow reuse
            # Connections are closed in close_all()
            pass
    
    @contextmanager
    def transaction(self):
        """
        Execute operations within a transaction.
        
        Yields:
            sqlite3.Connection: Database connection within transaction
        """
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or {})
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_one(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Execute a query and return single result.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Row dictionary or None
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or {})
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def close_connection(self):
        """Close the connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def close_all(self):
        """Close all connections (call during shutdown)."""
        with self._lock:
            # This is a simplified version - in production you'd track all connections
            self.close_connection()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connections are closed."""
        self.close_all()