#!/usr/bin/env python3
"""
Database testing utilities to ensure proper connection cleanup.

This module provides utilities for managing database connections in tests
to prevent ResourceWarning issues about unclosed connections.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from pathlib import Path

logger = logging.getLogger("test_db_utils")


@contextmanager
def managed_sqlite_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for SQLite connections that ensures proper cleanup.
    
    Args:
        db_path: Path to the SQLite database file
        
    Yields:
        sqlite3.Connection: The database connection
        
    Example:
        with managed_sqlite_connection("test.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
            # Connection is automatically closed when exiting the context
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        logger.debug(f"Opened SQLite connection to {db_path}")
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Error in SQLite connection, rolled back: {str(e)}")
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.debug(f"Closed SQLite connection to {db_path}")
            except Exception as e:
                logger.warning(f"Error closing SQLite connection: {str(e)}")


@contextmanager  
def managed_persistence_manager(base_dir: Optional[str] = None, db_url: Optional[str] = None):
    """
    Context manager for DatabasePersistenceManager that ensures proper cleanup.
    
    Args:
        base_dir: Base directory for persistence storage
        db_url: SQLAlchemy database URL
        
    Yields:
        DatabasePersistenceManager: The persistence manager instance
        
    Example:
        with managed_persistence_manager() as persistence:
            tasks = persistence.get_all_active_tasks()
            # Database connections are automatically cleaned up
    """
    from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
    
    persistence = None
    try:
        persistence = DatabasePersistenceManager(base_dir=base_dir, db_url=db_url)
        logger.debug("Created DatabasePersistenceManager")
        yield persistence
    except Exception as e:
        logger.error(f"Error in persistence manager: {str(e)}")
        raise
    finally:
        if persistence:
            try:
                persistence.dispose()
                logger.debug("Disposed DatabasePersistenceManager")
            except Exception as e:
                logger.warning(f"Error disposing persistence manager: {str(e)}")


class DatabaseTestCase:
    """
    Base class for database test cases that provides automatic cleanup.
    
    This class can be used as a mixin or base class for test cases that need
    database connections to ensure proper resource cleanup.
    """
    
    def __init__(self):
        self._db_connections = []
        self._persistence_managers = []
    
    def get_managed_connection(self, db_path: str) -> sqlite3.Connection:
        """
        Get a managed SQLite connection that will be automatically cleaned up.
        
        Args:
            db_path: Path to the SQLite database file
            
        Returns:
            sqlite3.Connection: The database connection
        """
        conn = sqlite3.connect(db_path)
        self._db_connections.append(conn)
        logger.debug(f"Added managed connection to {db_path}")
        return conn
    
    def get_managed_persistence(self, base_dir: Optional[str] = None, 
                              db_url: Optional[str] = None):
        """
        Get a managed persistence manager that will be automatically cleaned up.
        
        Args:
            base_dir: Base directory for persistence storage
            db_url: SQLAlchemy database URL
            
        Returns:
            DatabasePersistenceManager: The persistence manager
        """
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        persistence = DatabasePersistenceManager(base_dir=base_dir, db_url=db_url)
        self._persistence_managers.append(persistence)
        logger.debug("Added managed persistence manager")
        return persistence
    
    def cleanup_db_resources(self):
        """
        Clean up all managed database resources.
        
        This method should be called in test teardown or finally blocks.
        """
        # Close SQLite connections
        for conn in self._db_connections:
            try:
                if conn:
                    conn.close()
                    logger.debug("Closed managed SQLite connection")
            except Exception as e:
                logger.warning(f"Error closing SQLite connection: {str(e)}")
        
        # Dispose persistence managers
        for persistence in self._persistence_managers:
            try:
                if persistence:
                    persistence.dispose()
                    logger.debug("Disposed managed persistence manager")
            except Exception as e:
                logger.warning(f"Error disposing persistence manager: {str(e)}")
        
        # Clear the lists
        self._db_connections.clear()
        self._persistence_managers.clear()
        logger.debug("Cleared all managed database resources")
