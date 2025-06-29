#!/usr/bin/env python3
"""
Database Migration for Automation Maintenance Enhancement
Version: 1.4.1
Created: June 1, 2025

This migration adds the automation maintenance columns to the subtasks table
and ensures all maintenance-related tables are properly created.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, Column, Boolean, String, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from mcp_task_orchestrator.db.models import Base, SubTaskModel, TaskPrerequisiteModel, MaintenanceOperationModel, ProjectHealthMetricModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationMaintenanceMigration:
    """Handles database migration for automation maintenance enhancement."""
    
    def __init__(self, db_path: str = None):
        """Initialize migration with database connection."""
        if db_path is None:
            db_path = os.path.join(
                os.path.expanduser("~"),
                ".task_orchestrator",
                "orchestrator.db"
            )
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        
    def check_column_exists(self, session, table_name: str, column_name: str) -> bool:
        """Check if a column exists in the table."""
        try:
            result = session.execute(text(f"PRAGMA table_info({table_name})"))
            columns = [row[1] for row in result]
            return column_name in columns
        except Exception as e:
            logger.error(f"Error checking column existence: {e}")
            return False
    
    def check_table_exists(self, session, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
                {"table_name": table_name}
            )
            return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def add_automation_columns(self, session) -> bool:
        """Add automation maintenance columns to subtasks table."""
        try:
            # Check which columns need to be added
            columns_to_add = [
                ("prerequisite_satisfaction_required", "BOOLEAN DEFAULT 0"),
                ("auto_maintenance_enabled", "BOOLEAN DEFAULT 1"),
                ("quality_gate_level", "TEXT DEFAULT 'standard'")
            ]
            
            added_columns = []
            for column_name, column_def in columns_to_add:
                if not self.check_column_exists(session, "subtasks", column_name):
                    logger.info(f"Adding column {column_name} to subtasks table")
                    session.execute(
                        text(f"ALTER TABLE subtasks ADD COLUMN {column_name} {column_def}")
                    )
                    added_columns.append(column_name)
                else:
                    logger.info(f"Column {column_name} already exists in subtasks table")
            
            if added_columns:
                logger.info(f"Successfully added columns: {', '.join(added_columns)}")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error adding automation columns: {e}")
            return False
    
    def create_maintenance_tables(self, session) -> bool:
        """Ensure all maintenance-related tables exist."""
        try:
            # List of maintenance tables to check/create
            maintenance_tables = [
                ("task_prerequisites", TaskPrerequisiteModel),
                ("maintenance_operations", MaintenanceOperationModel),
                ("project_health_metrics", ProjectHealthMetricModel)
            ]
            
            created_tables = []
            for table_name, model_class in maintenance_tables:
                if not self.check_table_exists(session, table_name):
                    logger.info(f"Creating table: {table_name}")
                    # Create the table using the model's metadata
                    model_class.__table__.create(self.engine, checkfirst=True)
                    created_tables.append(table_name)
                else:
                    logger.info(f"Table {table_name} already exists")
            
            if created_tables:
                logger.info(f"Successfully created tables: {', '.join(created_tables)}")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating maintenance tables: {e}")
            return False
    
    def update_existing_records(self, session) -> bool:
        """Update existing records with default values for new columns."""
        try:
            # Count existing subtasks
            result = session.execute(text("SELECT COUNT(*) FROM subtasks"))
            count = result.scalar()
            
            if count > 0:
                logger.info(f"Updating {count} existing subtask records with default values")
                
                # Update records that have NULL values for the new columns
                updates = [
                    ("prerequisite_satisfaction_required", False),
                    ("auto_maintenance_enabled", True),
                    ("quality_gate_level", "'standard'")
                ]
                
                for column_name, default_value in updates:
                    if self.check_column_exists(session, "subtasks", column_name):
                        session.execute(
                            text(f"""
                                UPDATE subtasks 
                                SET {column_name} = {default_value if isinstance(default_value, str) else int(default_value)}
                                WHERE {column_name} IS NULL
                            """)
                        )
                
                logger.info("Successfully updated existing records")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating existing records: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create a backup of the database before migration."""
        try:
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Use file operations to copy the database
            import shutil
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                logger.info(f"Created database backup at: {backup_path}")
                return True
            else:
                logger.warning("No existing database to backup")
                return True
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        logger.info("Starting automation maintenance database migration")
        
        # Create backup first
        if not self.create_backup():
            logger.error("Failed to create backup, aborting migration")
            return False
        
        session = self.Session()
        success = True
        
        try:
            # Start transaction
            session.begin()
            
            # Step 1: Add automation columns to subtasks
            if not self.add_automation_columns(session):
                success = False
                logger.error("Failed to add automation columns")
            
            # Step 2: Create maintenance tables
            if success and not self.create_maintenance_tables(session):
                success = False
                logger.error("Failed to create maintenance tables")
            
            # Step 3: Update existing records
            if success and not self.update_existing_records(session):
                success = False
                logger.error("Failed to update existing records")
            
            if success:
                # Commit the transaction
                session.commit()
                logger.info("Migration completed successfully!")
                
                # Log migration summary
                self.log_migration_summary(session)
            else:
                # Rollback on failure
                session.rollback()
                logger.error("Migration failed, changes rolled back")
            
            return success
            
        except Exception as e:
            session.rollback()
            logger.error(f"Migration error: {e}")
            return False
        finally:
            session.close()
    
    def log_migration_summary(self, session):
        """Log a summary of the migration results."""
        try:
            # Count records in each table
            tables = [
                "subtasks",
                "task_prerequisites",
                "maintenance_operations",
                "project_health_metrics"
            ]
            
            logger.info("\n=== Migration Summary ===")
            for table in tables:
                if self.check_table_exists(session, table):
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"{table}: {count} records")
                else:
                    logger.info(f"{table}: Table not found")
            
            # Check automation columns
            if self.check_table_exists(session, "subtasks"):
                automation_columns = [
                    "prerequisite_satisfaction_required",
                    "auto_maintenance_enabled",
                    "quality_gate_level"
                ]
                logger.info("\nAutomation columns in subtasks:")
                for col in automation_columns:
                    exists = self.check_column_exists(session, "subtasks", col)
                    logger.info(f"  {col}: {'✓' if exists else '✗'}")
            
        except Exception as e:
            logger.error(f"Error logging migration summary: {e}")
    
    def verify_migration(self) -> bool:
        """Verify that the migration was successful."""
        session = self.Session()
        try:
            # Check all required columns exist
            required_columns = [
                ("subtasks", "prerequisite_satisfaction_required"),
                ("subtasks", "auto_maintenance_enabled"),
                ("subtasks", "quality_gate_level")
            ]
            
            for table, column in required_columns:
                if not self.check_column_exists(session, table, column):
                    logger.error(f"Missing required column: {table}.{column}")
                    return False
            
            # Check all required tables exist
            required_tables = [
                "task_prerequisites",
                "maintenance_operations",
                "project_health_metrics"
            ]
            
            for table in required_tables:
                if not self.check_table_exists(session, table):
                    logger.error(f"Missing required table: {table}")
                    return False
            
            logger.info("Migration verification passed!")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
            return False
        finally:
            session.close()


def main():
    """Main entry point for the migration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run automation maintenance database migration")
    parser.add_argument(
        "--db-path",
        help="Path to the database file",
        default=None
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify migration without running it"
    )
    
    args = parser.parse_args()
    
    # Initialize migration
    migration = AutomationMaintenanceMigration(db_path=args.db_path)
    
    if args.verify_only:
        # Just verify the migration
        if migration.verify_migration():
            logger.info("Migration verification successful")
            sys.exit(0)
        else:
            logger.error("Migration verification failed")
            sys.exit(1)
    else:
        # Run the migration
        if migration.run_migration():
            logger.info("Migration completed successfully")
            sys.exit(0)
        else:
            logger.error("Migration failed")
            sys.exit(1)


if __name__ == "__main__":
    main()