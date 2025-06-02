"""
Migration script for moving from file-based persistence to database-backed persistence.

This module provides functionality to migrate existing task data from the
file-based persistence system to the new database-backed system.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

# Type hints for IDE support
if TYPE_CHECKING:
    from ..persistence import PersistenceManager
    from .persistence import DatabasePersistenceManager

# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.db.migration")


class PersistenceMigrator:
    """Handles migration from file-based to database-backed persistence."""
    
    def __init__(self, base_dir: Optional[str] = None, db_url: Optional[str] = None):
        """Initialize the persistence migrator.
        
        Args:
            base_dir: Base directory for the persistence storage.
                     If None, uses the current working directory.
            db_url: SQLAlchemy database URL. If None, uses a SQLite database
                   in the base directory.
        """
        self.base_dir = base_dir
        self.db_url = db_url
        
        # Import persistence managers here to avoid circular imports
        from ..persistence import PersistenceManager
        from .persistence import DatabasePersistenceManager
        
        # Initialize source and target persistence managers
        self.source = PersistenceManager(base_dir)
        self.target = DatabasePersistenceManager(base_dir, db_url)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging for the migration process."""
        log_file = self.target.persistence_dir / self.target.LOGS_DIR / "migration.log"
        
        # Add a file handler to the logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        
        logger.addHandler(file_handler)
        logger.info("Migration logging initialized")
    
    def migrate_active_tasks(self) -> int:
        """Migrate all active tasks from file-based to database-backed persistence.
        
        Returns:
            Number of tasks successfully migrated
        """
        # Get all active task IDs from file-based persistence
        active_task_ids = self.source.get_all_active_tasks()
        logger.info(f"Found {len(active_task_ids)} active tasks to migrate")
        
        # Counter for successful migrations
        success_count = 0
        
        # Migrate each task
        for task_id in active_task_ids:
            try:
                # Load task from file-based persistence
                breakdown = self.source.load_task_breakdown(task_id)
                
                if breakdown:
                    # Save task to database-backed persistence
                    self.target.save_task_breakdown(breakdown)
                    logger.info(f"Successfully migrated task {task_id}")
                    success_count += 1
                else:
                    logger.warning(f"Task {task_id} not found in file-based persistence")
            except Exception as e:
                logger.error(f"Error migrating task {task_id}: {str(e)}")
        
        logger.info(f"Migration completed: {success_count}/{len(active_task_ids)} tasks migrated successfully")
        return success_count
    
    def migrate_archived_tasks(self) -> int:
        """Migrate all archived tasks from file-based to database-backed persistence.
        
        Returns:
            Number of tasks successfully migrated
        """
        # Get all archived task IDs from file-based persistence
        archived_task_ids = self.source.get_all_archived_tasks()
        logger.info(f"Found {len(archived_task_ids)} archived tasks to migrate")
        
        # Counter for successful migrations
        success_count = 0
        
        # Migrate each task
        for task_id in archived_task_ids:
            try:
                # Load task from file-based persistence
                breakdown = self.source.load_task_breakdown(task_id)
                
                if breakdown:
                    # Save task to database-backed persistence
                    self.target.save_task_breakdown(breakdown)
                    logger.info(f"Successfully migrated archived task {task_id}")
                    success_count += 1
                else:
                    logger.warning(f"Archived task {task_id} not found in file-based persistence")
            except Exception as e:
                logger.error(f"Error migrating archived task {task_id}: {str(e)}")
        
        logger.info(f"Archive migration completed: {success_count}/{len(archived_task_ids)} tasks migrated successfully")
        return success_count
    
    def migrate_all(self) -> int:
        """Migrate all tasks (active and archived) from file-based to database-backed persistence.
        
        Returns:
            Total number of tasks successfully migrated
        """
        active_count = self.migrate_active_tasks()
        archived_count = self.migrate_archived_tasks()
        
        total_count = active_count + archived_count
        logger.info(f"Total migration completed: {total_count} tasks migrated successfully")
        
        return total_count


def migrate_persistence(base_dir: Optional[str] = None, db_url: Optional[str] = None) -> int:
    """Convenience function to migrate all tasks from file-based to database-backed persistence.
    
    Args:
        base_dir: Base directory for the persistence storage.
                 If None, uses the current working directory.
        db_url: SQLAlchemy database URL. If None, uses a SQLite database
               in the base directory.
    
    Returns:
        Total number of tasks successfully migrated
    """
    # Create a new instance of PersistenceMigrator directly
    # We don't need to import it since it's defined in this module
    migrator = PersistenceMigrator(base_dir, db_url)
    return migrator.migrate_all()
