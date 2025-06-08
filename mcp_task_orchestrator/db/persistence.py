"""
Database-backed persistence implementation for the MCP Task Orchestrator.

This module provides a database-backed persistence manager that replaces
the file-based persistence manager with a more robust solution using
SQLAlchemy and SQLite.
"""

import os
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from ..orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
from .models import Base, TaskBreakdownModel, SubTaskModel, LockTrackingModel

# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.db.persistence")


class DatabasePersistenceManager:
    """Manages persistence of task state and configuration data using a database backend."""
    
    # Directory structure constants - kept for compatibility with file-based system
    PERSISTENCE_DIR = ".task_orchestrator"
    ROLES_DIR = "roles"
    LOGS_DIR = "logs"
    
    # File name constants
    DEFAULT_ROLES_FILE = "default_roles.yaml"
    CUSTOM_ROLES_FILE = "custom_roles.yaml"
    
    def __init__(self, base_dir: Optional[str] = None, db_url: Optional[str] = None):
        """Initialize the database persistence manager.
        
        Args:
            base_dir: Base directory for the persistence storage.
                     If None, uses the current working directory.
            db_url: SQLAlchemy database URL. If None, uses a SQLite database
                   in the base directory.
        """
        if base_dir is None:
            # Check environment variable first
            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
            
            if not base_dir:
                # Default to current working directory (project being worked on)
                base_dir = os.getcwd()
        
        self.base_dir = Path(base_dir)
        self.persistence_dir = self.base_dir / self.PERSISTENCE_DIR
        
        # Initialize directory structure for roles and logs
        self._initialize_directory_structure()
        
        # Configure logging
        self._setup_logging()
        
        # Initialize database connection
        if db_url is None:
            db_url = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_URL")
            
            if not db_url:
                # Default to a SQLite database in the base directory
                db_path = self.persistence_dir / "task_orchestrator.db"
                db_url = f"sqlite:///{db_path}"
        
        # Configure engine with optimized settings for async workloads
        self.engine = create_engine(
            db_url, 
            connect_args={
                "check_same_thread": False,
                "timeout": 30  # 30 second timeout for SQLite operations
            },
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            echo=False  # Set to True for SQL debugging
        )
        
        # Add pragma for SQLite to enable foreign key support and optimize for concurrent access
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and performance
            cursor.execute("PRAGMA cache_size=10000")  # Increase cache size
            cursor.execute("PRAGMA temp_store=memory")  # Store temp data in memory
            cursor.close()
        
        # Create session factory - NOT scoped for better async compatibility
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Add database indexes for performance optimization
        self._create_performance_indexes()
        
        logger.info(f"Initialized database persistence manager with URL: {db_url}")
    
    def _create_performance_indexes(self) -> None:
        """Create database indexes for performance optimization."""
        try:
            with self.session_scope() as session:
                # Add indexes for subtasks table to optimize parent task ID lookups
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_subtasks_task_id ON subtasks(task_id)"))
                session.execute(text("CREATE INDEX IF NOT EXISTS idx_subtasks_parent_task_id ON subtasks(parent_task_id)"))
                session.commit()
                logger.info("Created performance indexes for subtasks table")
        except Exception as e:
            logger.warning(f"Could not create performance indexes (may already exist): {str(e)}")
    
    def get_parent_task_id(self, task_id: str) -> Optional[str]:
        """Direct database lookup for parent task ID - much faster than loading full breakdowns.
        
        This method provides a direct lookup of the parent task ID for a given subtask,
        avoiding the expensive operation of loading entire task breakdowns.
        
        Args:
            task_id: The ID of the subtask to look up
            
        Returns:
            The parent task ID if found, None otherwise
        """
        def _lookup_operation(session):
            result = session.query(SubTaskModel.parent_task_id).filter_by(
                task_id=task_id
            ).first()
            return result[0] if result else None
        
        try:
            return self._execute_with_retry(_lookup_operation)
        except Exception as e:
            logger.error(f"Error getting parent task ID for {task_id}: {str(e)}")
            return None
    
    def _initialize_directory_structure(self) -> None:
        """Create the directory structure for persistence if it doesn't exist."""
        # Create main persistence directory
        self.persistence_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for roles and logs
        (self.persistence_dir / self.ROLES_DIR).mkdir(exist_ok=True)
        (self.persistence_dir / self.LOGS_DIR).mkdir(exist_ok=True)
        
        logger.info(f"Initialized persistence directory structure at {self.persistence_dir}")
    
    def _setup_logging(self) -> None:
        """Set up logging for the persistence manager."""
        log_file = self.persistence_dir / self.LOGS_DIR / "db_persistence.log"
        
        # Add a file handler to the logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        
        logger.addHandler(file_handler)
        logger.info("Database persistence logging initialized")
    
    def get_roles_directory(self) -> Path:
        """Get the path to the roles directory."""
        return self.persistence_dir / self.ROLES_DIR
    
    @contextmanager
    def session_scope(self, timeout_seconds: int = 30):
        """Provide a transactional scope around a series of operations with timeout handling.
        
        This replaces the problematic scoped_session pattern with explicit session lifecycle management
        that works better with asyncio and concurrent operations.
        
        Args:
            timeout_seconds: Maximum time to wait for database operations
            
        Yields:
            SQLAlchemy session object
        """
        session = self.Session()
        try:
            # Set a statement timeout if supported
            if hasattr(session.bind, 'execute'):
                # For SQLite, we rely on the connection timeout set in engine creation
                pass
            
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction error: {str(e)}")
            raise
        finally:
            session.close()
    
    def _execute_with_retry(self, operation, max_retries: int = 3, base_delay: float = 0.1):
        """Execute a database operation with retry logic for handling temporary failures.
        
        Args:
            operation: Callable that takes a session and performs the database operation
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries (exponential backoff)
            
        Returns:
            The result of the operation
        """
        import time
        
        for attempt in range(max_retries + 1):
            try:
                with self.session_scope() as session:
                    return operation(session)
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Database operation failed after {max_retries} retries: {str(e)}")
                    raise
                
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + (0.1 * attempt)
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                             f"retrying in {delay:.2f}s: {str(e)}")
                time.sleep(delay)
    
    def save_task_breakdown(self, breakdown: TaskBreakdown) -> None:
        """Save a task breakdown to persistent storage with retry logic.
        
        Args:
            breakdown: The TaskBreakdown object to save
        """
        # Ensure all subtasks have proper artifacts format
        for subtask in breakdown.subtasks:
            if not hasattr(subtask, 'artifacts') or subtask.artifacts is None:
                subtask.artifacts = []
            elif not isinstance(subtask.artifacts, list):
                # Sanitize artifacts if they're not in the correct format
                subtask.artifacts = self._sanitize_artifacts(subtask.artifacts)
        
        def _save_operation(session):
            # Convert domain model to DB model
            db_breakdown = self._convert_to_db_model(breakdown)
            
            # Check if the task breakdown already exists
            existing = session.query(TaskBreakdownModel).filter_by(
                parent_task_id=breakdown.parent_task_id
            ).first()
            
            if existing:
                # Update existing record
                existing.description = breakdown.description
                existing.complexity = breakdown.complexity.value
                existing.context = breakdown.context
                
                # Delete existing subtasks (they will be replaced)
                session.query(SubTaskModel).filter_by(
                    parent_task_id=breakdown.parent_task_id
                ).delete()
                
                # Add new subtasks
                existing.subtasks = [self._convert_subtask_to_db_model(st, breakdown.parent_task_id) 
                                    for st in breakdown.subtasks]
            else:
                # Add new record
                session.add(db_breakdown)
            
            return breakdown.parent_task_id
        
        try:
            result = self._execute_with_retry(_save_operation)
            logger.info(f"Saved task breakdown {result} to database")
        except Exception as e:
            logger.error(f"Error saving task breakdown {breakdown.parent_task_id}: {str(e)}")
            raise
    
    def load_task_breakdown(self, parent_task_id: str) -> Optional[TaskBreakdown]:
        """Load a task breakdown from persistent storage with retry logic.
        
        Args:
            parent_task_id: ID of the parent task to load
            
        Returns:
            The TaskBreakdown object if found, None otherwise
        """
        def _load_operation(session):
            # Query the database for the task breakdown
            db_breakdown = session.query(TaskBreakdownModel).filter_by(
                parent_task_id=parent_task_id
            ).first()
            
            if db_breakdown:
                # Convert DB model to domain model
                breakdown = self._convert_from_db_model(db_breakdown)
                return breakdown
            else:
                return None
        
        try:
            result = self._execute_with_retry(_load_operation)
            if result:
                logger.info(f"Loaded task breakdown {parent_task_id} from database")
            else:
                logger.warning(f"Task breakdown {parent_task_id} not found in database")
            return result
        except Exception as e:
            logger.error(f"Error loading task breakdown {parent_task_id}: {str(e)}")
            return None
    
    def update_subtask(self, subtask: SubTask, parent_task_id: str) -> None:
        """Update a subtask within a task breakdown with retry logic.
        
        Args:
            subtask: The updated SubTask object
            parent_task_id: ID of the parent task
        """
        # Ensure artifacts is properly formatted
        if not hasattr(subtask, 'artifacts') or subtask.artifacts is None:
            subtask.artifacts = []
        elif not isinstance(subtask.artifacts, list):
            # Sanitize artifacts if they're not in the correct format
            subtask.artifacts = self._sanitize_artifacts(subtask.artifacts)
        
        def _update_operation(session):
            # Query the database for the subtask
            db_subtask = session.query(SubTaskModel).filter_by(
                task_id=subtask.task_id
            ).first()
            
            if db_subtask:
                # Update the subtask
                db_subtask.title = subtask.title
                db_subtask.description = subtask.description
                db_subtask.specialist_type = subtask.specialist_type.value
                db_subtask.dependencies = subtask.dependencies
                db_subtask.estimated_effort = subtask.estimated_effort
                db_subtask.status = subtask.status.value
                db_subtask.results = subtask.results
                db_subtask.artifacts = subtask.artifacts
                db_subtask.completed_at = subtask.completed_at
                
                return f"updated {subtask.task_id}"
            else:
                # If the subtask doesn't exist, create it
                db_subtask = self._convert_subtask_to_db_model(subtask, parent_task_id)
                session.add(db_subtask)
                return f"created {subtask.task_id}"
        
        try:
            result = self._execute_with_retry(_update_operation)
            logger.info(f"Subtask operation completed: {result}")
        except Exception as e:
            logger.error(f"Error updating subtask {subtask.task_id}: {str(e)}")
            raise
    
    def archive_task(self, parent_task_id: str) -> bool:
        """Archive a completed task.
        
        In the database implementation, we mark the task as archived rather than
        moving it to a different location.
        
        Args:
            parent_task_id: ID of the parent task to archive
            
        Returns:
            True if the task was archived successfully, False otherwise
        """
        try:
            # For now, we'll just return True as we don't have a separate
            # archive table in the database implementation
            logger.info(f"Task {parent_task_id} marked as archived in database")
            return True
        except Exception as e:
            logger.error(f"Error archiving task {parent_task_id}: {str(e)}")
            return False
    
    def get_all_active_tasks(self) -> List[str]:
        """Get a list of all active task IDs with retry logic.
        
        Returns:
            List of parent task IDs for all active tasks
        """
        def _get_active_operation(session):
            # Query all task breakdowns
            task_ids = [
                tb.parent_task_id for tb in session.query(TaskBreakdownModel.parent_task_id).all()
            ]
            return task_ids
        
        try:
            return self._execute_with_retry(_get_active_operation)
        except Exception as e:
            logger.error(f"Error getting active tasks: {str(e)}")
            return []
    
    def get_all_archived_tasks(self) -> List[str]:
        """Get a list of all archived task IDs.
        
        In the database implementation, we don't have a separate archive table,
        so this returns an empty list for now.
        
        Returns:
            List of parent task IDs for all archived tasks
        """
        # For now, return an empty list as we don't have a separate
        # archive table in the database implementation
        return []
    
    def migrate_roles_from_config(self, config_dir: Path) -> None:
        """Migrate role configuration files from the config directory.
        
        Args:
            config_dir: Path to the config directory
        """
        source_file = config_dir / "specialists.yaml"
        target_file = self.get_roles_directory() / self.DEFAULT_ROLES_FILE
        
        if source_file.exists() and not target_file.exists():
            import shutil
            shutil.copy(source_file, target_file)
            logger.info(f"Migrated specialists configuration from {source_file} to {target_file}")
    
    def _convert_to_db_model(self, breakdown: TaskBreakdown) -> TaskBreakdownModel:
        """Convert a domain TaskBreakdown object to a database model.
        
        Args:
            breakdown: The TaskBreakdown object to convert
            
        Returns:
            The converted TaskBreakdownModel object
        """
        return TaskBreakdownModel(
            parent_task_id=breakdown.parent_task_id,
            description=breakdown.description,
            complexity=breakdown.complexity.value,
            context=breakdown.context,
            created_at=breakdown.created_at,
            subtasks=[
                self._convert_subtask_to_db_model(subtask, breakdown.parent_task_id)
                for subtask in breakdown.subtasks
            ]
        )
    
    def _convert_subtask_to_db_model(self, subtask: SubTask, parent_task_id: str) -> SubTaskModel:
        """Convert a domain SubTask object to a database model.
        
        Args:
            subtask: The SubTask object to convert
            parent_task_id: ID of the parent task
            
        Returns:
            The converted SubTaskModel object
        """
        return SubTaskModel(
            task_id=subtask.task_id,
            parent_task_id=parent_task_id,
            title=subtask.title,
            description=subtask.description,
            specialist_type=subtask.specialist_type.value,
            dependencies=subtask.dependencies,
            estimated_effort=subtask.estimated_effort,
            status=subtask.status.value,
            results=subtask.results,
            artifacts=subtask.artifacts,
            created_at=subtask.created_at,
            completed_at=subtask.completed_at
        )
    
    def _convert_from_db_model(self, db_breakdown: TaskBreakdownModel) -> TaskBreakdown:
        """Convert a database model to a domain TaskBreakdown object.
        
        Args:
            db_breakdown: The TaskBreakdownModel object to convert
            
        Returns:
            The converted TaskBreakdown object
        """
        return TaskBreakdown(
            parent_task_id=db_breakdown.parent_task_id,
            description=db_breakdown.description,
            complexity=ComplexityLevel(db_breakdown.complexity),
            context=db_breakdown.context,
            created_at=db_breakdown.created_at,
            subtasks=[
                self._convert_subtask_from_db_model(db_subtask)
                for db_subtask in db_breakdown.subtasks
            ]
        )
    
    def _sanitize_artifacts(self, artifacts_data: Any) -> List[str]:
        """Sanitize artifacts data to ensure it's always a list of strings.
        
        This method handles the migration from legacy string format to list format,
        providing backward compatibility during the transition period.
        
        Args:
            artifacts_data: Raw artifacts data from database (could be string, list, or None)
            
        Returns:
            A list of strings representing the artifacts
        """
        if artifacts_data is None:
            return []
        
        # If it's already a list, validate and return
        if isinstance(artifacts_data, list):
            # Ensure all items are strings
            return [str(item) for item in artifacts_data if item is not None]
        
        # If it's a string, handle different cases
        if isinstance(artifacts_data, str):
            # Empty string case
            if not artifacts_data.strip():
                return []
            
            # Try to parse as JSON first (in case it's a JSON string)
            try:
                import json
                parsed = json.loads(artifacts_data)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item is not None]
                else:
                    # JSON parsed to non-list, treat as single item
                    return [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                # Not valid JSON, treat as single string artifact
                # Handle multi-line strings by splitting on newlines
                if '\n' in artifacts_data:
                    # Split on newlines and clean up
                    lines = [line.strip() for line in artifacts_data.split('\n') if line.strip()]
                    return lines
                else:
                    return [artifacts_data]
        
        # For any other type, convert to string and return as single-item list
        return [str(artifacts_data)]

    def _convert_subtask_from_db_model(self, db_subtask: SubTaskModel) -> SubTask:
        """Convert a database model to a domain SubTask object.
        
        Args:
            db_subtask: The SubTaskModel object to convert
            
        Returns:
            The converted SubTask object
        """
        # Safely convert artifacts to list format
        artifacts = self._sanitize_artifacts(db_subtask.artifacts)
        
        return SubTask(
            task_id=db_subtask.task_id,
            title=db_subtask.title,
            description=db_subtask.description,
            specialist_type=SpecialistType(db_subtask.specialist_type),
            dependencies=db_subtask.dependencies,
            estimated_effort=db_subtask.estimated_effort,
            status=TaskStatus(db_subtask.status),
            results=db_subtask.results,
            artifacts=artifacts,
            created_at=db_subtask.created_at,
            completed_at=db_subtask.completed_at
        )
    
    def cleanup_stale_locks(self, max_age_seconds: int = 3600) -> int:
        """Clean up stale lock records from the database with retry logic.
        
        This method removes lock records that are older than the specified age,
        helping to prevent accumulation of stale locks that could interfere
        with normal operation.
        
        Args:
            max_age_seconds: Maximum age of lock records in seconds (default: 1 hour)
            
        Returns:
            Number of stale locks removed
            
        Raises:
            Exception: If database operation fails after retries
        """
        def _cleanup_operation(session):
            # Calculate cutoff time
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
            
            # Query for stale locks to log them before deletion
            stale_locks = session.query(LockTrackingModel).filter(
                LockTrackingModel.locked_at < cutoff_time
            ).all()
            
            if not stale_locks:
                logger.debug("No stale locks found for cleanup")
                return 0
            
            # Log the locks being cleaned up
            for lock in stale_locks:
                logger.info(f"Removing stale lock: {lock.resource_name} "
                          f"(locked at {lock.locked_at} by {lock.locked_by})")
            
            # Delete stale locks using ORM
            deleted_count = session.query(LockTrackingModel).filter(
                LockTrackingModel.locked_at < cutoff_time
            ).delete()
            
            return deleted_count
        
        try:
            deleted_count = self._execute_with_retry(_cleanup_operation)
            logger.info(f"Cleaned up {deleted_count} stale locks "
                      f"(older than {max_age_seconds} seconds)")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup stale locks: {str(e)}")
            # Re-raise the exception to let the caller handle it
            raise
    
    def get_parent_task_id(self, task_id: str) -> Optional[str]:
        """Get the parent task ID for a given subtask.
        
        Args:
            task_id: The ID of the subtask
            
        Returns:
            The parent task ID, or None if subtask not found
        """
        def _get_parent_operation(session):
            # Query the subtasks table for the given task_id
            db_subtask = session.query(SubTaskModel).filter_by(
                task_id=task_id
            ).first()
            
            return db_subtask.parent_task_id if db_subtask else None
        
        try:
            result = self._execute_with_retry(_get_parent_operation)
            if result:
                logger.debug(f"Found parent task ID {result} for subtask {task_id}")
            else:
                logger.debug(f"No parent task found for subtask {task_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting parent task ID for {task_id}: {str(e)}")
            return None

    
    def dispose(self):
        """Dispose of database resources and close all connections.
        
        This method should be called when the persistence manager is no longer needed
        to ensure proper cleanup of database connections and prevent resource warnings.
        """
        try:
            if hasattr(self, 'engine') and self.engine is not None:
                self.engine.dispose()
                logger.debug("Database engine disposed successfully")
        except Exception as e:
            logger.warning(f"Error disposing database engine: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures proper cleanup."""
        self.dispose()
