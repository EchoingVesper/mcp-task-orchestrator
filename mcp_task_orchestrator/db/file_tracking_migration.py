"""
File Tracking Tables Migration

This module provides functionality to migrate the database schema to include
the new file tracking and verification tables required for the file persistence
verification system.
"""

import logging
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from .models import Base, FileOperationModel, FileVerificationModel

logger = logging.getLogger("mcp_task_orchestrator.db.file_tracking_migration")


class FileTrackingMigration:
    """Handles migration to add file tracking tables to existing database."""
    
    def __init__(self, db_url: str = None):
        """
        Initialize the file tracking migration.
        
        Args:
            db_url: SQLAlchemy database URL. If None, uses default SQLite database.
        """
        if db_url is None:
            db_url = "sqlite:///task_orchestrator.db"
        
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def check_tables_exist(self) -> bool:
        """Check if file tracking tables already exist."""
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        
        required_tables = ['file_operations', 'file_verifications']
        existing_tables = metadata.tables.keys()
        
        return all(table in existing_tables for table in required_tables)
    
    def create_file_tracking_tables(self) -> bool:
        """
        Create the file tracking tables in the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Creating file tracking tables...")
            
            # Check if tables already exist
            if self.check_tables_exist():
                logger.info("File tracking tables already exist. Skipping creation.")
                return True
            
            # Create only the new tables
            FileOperationModel.__table__.create(self.engine, checkfirst=True)
            FileVerificationModel.__table__.create(self.engine, checkfirst=True)
            
            logger.info("Successfully created file tracking tables")
            return True
            
        except Exception as e:
            logger.error(f"Error creating file tracking tables: {str(e)}")
            return False
    
    def add_file_tracking_columns_to_subtasks(self) -> bool:
        """
        Add file tracking columns to existing subtasks table.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Adding file tracking columns to subtasks table...")
            
            # Check if columns already exist
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            
            subtasks_table = metadata.tables.get('subtasks')
            if not subtasks_table:
                logger.error("Subtasks table not found")
                return False
            
            existing_columns = [col.name for col in subtasks_table.columns]
            
            # Add columns if they don't exist
            if 'file_operations_count' not in existing_columns:
                self.engine.execute("ALTER TABLE subtasks ADD COLUMN file_operations_count INTEGER DEFAULT 0")
                logger.info("Added file_operations_count column")
            
            if 'verification_status' not in existing_columns:
                self.engine.execute("ALTER TABLE subtasks ADD COLUMN verification_status VARCHAR DEFAULT 'pending'")
                logger.info("Added verification_status column")
            
            logger.info("Successfully added file tracking columns to subtasks table")
            return True
            
        except Exception as e:
            logger.error(f"Error adding columns to subtasks table: {str(e)}")
            return False
    
    def migrate_metadata_column_rename(self) -> bool:
        """
        Migrate the metadata column to file_metadata in file_operations table.
        
        This handles the rename from 'metadata' to 'file_metadata' to avoid
        SQLAlchemy reserved attribute name conflicts.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Migrating metadata column to file_metadata...")
            
            # Check if file_operations table exists
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            
            file_operations_table = metadata.tables.get('file_operations')
            if not file_operations_table:
                logger.info("file_operations table not found, skipping metadata column migration")
                return True
            
            existing_columns = [col.name for col in file_operations_table.columns]
            
            # Check if old 'metadata' column exists and new 'file_metadata' doesn't
            has_old_metadata = 'metadata' in existing_columns
            has_new_file_metadata = 'file_metadata' in existing_columns
            
            if has_old_metadata and not has_new_file_metadata:
                # Perform the column rename
                with self.engine.begin() as conn:
                    # SQLite doesn't support direct column rename, so we need to:
                    # 1. Add the new column
                    # 2. Copy data from old to new
                    # 3. Drop the old column (in SQLite, this requires table recreation)
                    
                    # For SQLite, we'll use a simpler approach: add new column and copy data
                    conn.execute(text("ALTER TABLE file_operations ADD COLUMN file_metadata JSON"))
                    conn.execute(text("UPDATE file_operations SET file_metadata = metadata"))
                    
                    # Note: In SQLite, we can't easily drop the old column without recreating the table
                    # For now, we'll leave the old column but mark this migration as successful
                    # The application code will use file_metadata going forward
                    
                logger.info("Successfully migrated metadata column to file_metadata")
                
            elif has_new_file_metadata:
                logger.info("file_metadata column already exists, skipping migration")
                
            else:
                logger.info("No metadata column found, skipping migration")
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrating metadata column: {str(e)}")
            return False
    
    def migrate(self) -> bool:
        """
        Run the complete file tracking migration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting file tracking migration...")
        
        success = True
        
        # Create new tables
        if not self.create_file_tracking_tables():
            success = False
        
        # Add columns to existing table
        if not self.add_file_tracking_columns_to_subtasks():
            success = False
        
        # Migrate metadata column rename
        if not self.migrate_metadata_column_rename():
            success = False
        
        if success:
            logger.info("File tracking migration completed successfully")
        else:
            logger.error("File tracking migration failed")
        
        return success


def migrate_file_tracking_tables(db_url: str = None) -> bool:
    """
    Convenience function to migrate database schema for file tracking.
    
    Args:
        db_url: SQLAlchemy database URL. If None, uses default SQLite database.
    
    Returns:
        bool: True if successful, False otherwise
    """
    migration = FileTrackingMigration(db_url)
    return migration.migrate()


def setup_file_tracking_schema(db_url: str = None) -> bool:
    """
    Set up complete file tracking schema for new installations.
    
    Args:
        db_url: SQLAlchemy database URL. If None, uses default SQLite database.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if db_url is None:
        db_url = "sqlite:///task_orchestrator.db"
    
    try:
        logger.info("Setting up complete file tracking schema...")
        
        engine = create_engine(db_url)
        
        # Create all tables including file tracking
        Base.metadata.create_all(bind=engine)
        
        logger.info("Successfully set up complete file tracking schema")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up file tracking schema: {str(e)}")
        return False