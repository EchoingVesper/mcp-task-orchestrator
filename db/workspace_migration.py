"""
Workspace Paradigm Migration System

This module handles the migration from session-based to workspace-based paradigm.
It includes database schema updates, data migration, and backward compatibility.
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, text, Column, String, DateTime, Text, JSON, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class WorkspaceMigration:
    """Handles migration from session-based to workspace-based paradigm."""
    
    def __init__(self, db_url: Optional[str] = None, base_dir: Optional[str] = None):
        """Initialize workspace migration.
        
        Args:
            db_url: Database URL (SQLAlchemy format)
            base_dir: Base directory for workspace detection and persistence
        """
        self.base_dir = Path(base_dir or os.getcwd())
        self.db_url = db_url or f"sqlite:///{self.base_dir / '.task_orchestrator' / 'workspace.db'}"
        
        # Setup database connection
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Migration status
        self.migration_status = {
            'started_at': None,
            'completed_at': None,
            'errors': [],
            'steps_completed': [],
            'total_steps': 8
        }
    
    def run_migration(self) -> Dict[str, Any]:
        """Run complete workspace paradigm migration.
        
        Returns:
            Dictionary with migration results and status
        """
        try:
            self.migration_status['started_at'] = datetime.now()
            logger.info("Starting workspace paradigm migration")
            
            # Step 1: Create workspace-specific tables
            self._create_workspace_tables()
            self.migration_status['steps_completed'].append('create_workspace_tables')
            
            # Step 2: Update existing tables to support workspace paradigm
            self._update_existing_tables()
            self.migration_status['steps_completed'].append('update_existing_tables')
            
            # Step 3: Migrate session data to workspace data
            self._migrate_session_to_workspace_data()
            self.migration_status['steps_completed'].append('migrate_session_data')
            
            # Step 4: Create workspace detection and association logic
            self._setup_workspace_detection()
            self.migration_status['steps_completed'].append('setup_workspace_detection')
            
            # Step 5: Update file operation paths to be workspace-relative
            self._update_file_operation_paths()
            self.migration_status['steps_completed'].append('update_file_paths')
            
            # Step 6: Create workspace configuration tables
            self._create_workspace_configuration()
            self.migration_status['steps_completed'].append('create_workspace_config')
            
            # Step 7: Update indexes for workspace-based queries
            self._update_indexes()
            self.migration_status['steps_completed'].append('update_indexes')
            
            # Step 8: Validate migration and create backward compatibility views
            self._create_compatibility_views()
            self.migration_status['steps_completed'].append('create_compatibility')
            
            self.migration_status['completed_at'] = datetime.now()
            logger.info("Workspace paradigm migration completed successfully")
            
            return {
                'success': True,
                'migration_status': self.migration_status,
                'message': 'Workspace paradigm migration completed successfully'
            }
            
        except Exception as e:
            error_msg = f"Migration failed: {str(e)}"
            logger.error(error_msg)
            self.migration_status['errors'].append(error_msg)
            
            return {
                'success': False,
                'migration_status': self.migration_status,
                'error': error_msg
            }
    
    def _create_workspace_tables(self):
        """Create new workspace-specific database tables."""
        logger.info("Creating workspace-specific tables")
        
        workspace_tables_sql = """
        -- Workspace Registry Table
        CREATE TABLE IF NOT EXISTS workspaces (
            workspace_id TEXT PRIMARY KEY,
            workspace_name TEXT NOT NULL,
            workspace_path TEXT NOT NULL UNIQUE,
            detection_method TEXT NOT NULL, -- git_root, project_marker, explicit, etc.
            detection_confidence INTEGER NOT NULL, -- 1-10 scale
            
            -- Project Information
            project_type TEXT, -- python, javascript, rust, etc.
            project_markers TEXT, -- JSON array of detected markers
            git_root_path TEXT,
            
            -- Configuration
            is_active BOOLEAN DEFAULT TRUE,
            is_default BOOLEAN DEFAULT FALSE,
            artifact_storage_policy TEXT DEFAULT 'workspace_relative', -- workspace_relative, absolute, hybrid
            
            -- Security and Validation
            is_validated BOOLEAN DEFAULT FALSE,
            is_writable BOOLEAN DEFAULT TRUE,
            security_warnings TEXT, -- JSON array of warnings
            
            -- Statistics
            total_tasks INTEGER DEFAULT 0,
            active_tasks INTEGER DEFAULT 0,
            last_activity_at DATETIME,
            
            -- Timestamps
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Workspace-Task Association Table
        CREATE TABLE IF NOT EXISTS workspace_tasks (
            association_id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            
            -- Association metadata
            association_type TEXT DEFAULT 'primary', -- primary, reference, archived
            created_in_workspace BOOLEAN DEFAULT TRUE,
            relative_artifact_paths TEXT, -- JSON array of workspace-relative paths
            
            -- Timestamps
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES task_breakdowns(parent_task_id) ON DELETE CASCADE,
            UNIQUE(workspace_id, task_id)
        );

        -- Workspace Artifact Storage Table
        CREATE TABLE IF NOT EXISTS workspace_artifacts (
            artifact_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            task_id TEXT,
            
            -- Storage Information
            relative_path TEXT NOT NULL, -- Path relative to workspace root
            absolute_path TEXT NOT NULL, -- Absolute path for verification
            artifact_type TEXT NOT NULL, -- code, documentation, analysis, etc.
            storage_method TEXT DEFAULT 'file', -- file, embedded, external
            
            -- Content and Metadata
            content_hash TEXT,
            file_size INTEGER,
            mime_type TEXT,
            content_preview TEXT, -- First few lines for quick display
            
            -- Workspace Context
            created_by_task BOOLEAN DEFAULT TRUE,
            is_persistent BOOLEAN DEFAULT TRUE, -- Should survive task completion
            backup_available BOOLEAN DEFAULT FALSE,
            
            -- Timestamps
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_verified_at DATETIME,
            
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES subtasks(task_id) ON DELETE SET NULL
        );

        -- Workspace Configuration Table
        CREATE TABLE IF NOT EXISTS workspace_configurations (
            config_id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT NOT NULL,
            
            -- Configuration Categories
            config_category TEXT NOT NULL, -- directories, artifacts, tools, security
            config_key TEXT NOT NULL,
            config_value TEXT NOT NULL, -- JSON value
            config_type TEXT NOT NULL, -- string, number, boolean, array, object
            
            -- Configuration Metadata
            is_user_defined BOOLEAN DEFAULT FALSE,
            is_system_generated BOOLEAN DEFAULT TRUE,
            description TEXT,
            
            -- Timestamps
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
            UNIQUE(workspace_id, config_category, config_key)
        );

        -- Create indexes for workspace tables
        CREATE INDEX IF NOT EXISTS idx_workspaces_path ON workspaces(workspace_path);
        CREATE INDEX IF NOT EXISTS idx_workspaces_active ON workspaces(is_active);
        CREATE INDEX IF NOT EXISTS idx_workspaces_activity ON workspaces(last_activity_at);
        
        CREATE INDEX IF NOT EXISTS idx_workspace_tasks_workspace ON workspace_tasks(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_workspace_tasks_task ON workspace_tasks(task_id);
        CREATE INDEX IF NOT EXISTS idx_workspace_tasks_type ON workspace_tasks(association_type);
        
        CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_workspace ON workspace_artifacts(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_task ON workspace_artifacts(task_id);
        CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_type ON workspace_artifacts(artifact_type);
        CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_path ON workspace_artifacts(relative_path);
        
        CREATE INDEX IF NOT EXISTS idx_workspace_config_workspace ON workspace_configurations(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_workspace_config_category ON workspace_configurations(config_category);
        """
        
        with self.engine.connect() as conn:
            for statement in workspace_tables_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
    
    def _update_existing_tables(self):
        """Update existing tables to support workspace paradigm."""
        logger.info("Updating existing tables for workspace support")
        
        update_sql = """
        -- Add workspace_id to existing tables
        ALTER TABLE task_breakdowns ADD COLUMN workspace_id TEXT;
        ALTER TABLE subtasks ADD COLUMN workspace_id TEXT;
        ALTER TABLE file_operations ADD COLUMN workspace_id TEXT;
        ALTER TABLE file_operations ADD COLUMN workspace_relative_path TEXT;
        ALTER TABLE architectural_decisions ADD COLUMN workspace_id TEXT;
        
        -- Update file_operations to track workspace context
        ALTER TABLE file_operations ADD COLUMN original_session_id TEXT;
        UPDATE file_operations SET original_session_id = session_id WHERE original_session_id IS NULL;
        
        -- Add workspace tracking to lock_tracking
        ALTER TABLE lock_tracking ADD COLUMN workspace_id TEXT;
        
        -- Create new indexes for workspace queries
        CREATE INDEX IF NOT EXISTS idx_task_breakdowns_workspace ON task_breakdowns(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_subtasks_workspace ON subtasks(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_file_operations_workspace ON file_operations(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_file_operations_workspace_path ON file_operations(workspace_relative_path);
        """
        
        with self.engine.connect() as conn:
            try:
                for statement in update_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                conn.commit()
            except SQLAlchemyError as e:
                # Some columns might already exist, continue with migration
                logger.warning(f"Some schema updates may have failed (likely already applied): {e}")
    
    def _migrate_session_to_workspace_data(self):
        """Migrate existing session-based data to workspace paradigm."""
        logger.info("Migrating session data to workspace paradigm")
        
        with self.SessionLocal() as session:
            try:
                # Create a default workspace for existing data
                default_workspace_id = "workspace_migration_default"
                workspace_path = str(self.base_dir)
                
                # Insert default workspace
                session.execute(text("""
                    INSERT OR IGNORE INTO workspaces (
                        workspace_id, workspace_name, workspace_path, detection_method, 
                        detection_confidence, is_default, created_at
                    ) VALUES (
                        :workspace_id, :name, :path, :method, :confidence, :is_default, :created_at
                    )
                """), {
                    'workspace_id': default_workspace_id,
                    'name': 'Legacy Session Data',
                    'path': workspace_path,
                    'method': 'migration_default',
                    'confidence': 5,
                    'is_default': True,
                    'created_at': datetime.now()
                })
                
                # Associate existing tasks with default workspace
                session.execute(text("""
                    UPDATE task_breakdowns 
                    SET workspace_id = :workspace_id 
                    WHERE workspace_id IS NULL
                """), {'workspace_id': default_workspace_id})
                
                session.execute(text("""
                    UPDATE subtasks 
                    SET workspace_id = :workspace_id 
                    WHERE workspace_id IS NULL
                """), {'workspace_id': default_workspace_id})
                
                # Create workspace-task associations
                session.execute(text("""
                    INSERT INTO workspace_tasks (workspace_id, task_id, association_type, created_in_workspace)
                    SELECT :workspace_id, parent_task_id, 'primary', FALSE
                    FROM task_breakdowns 
                    WHERE workspace_id = :workspace_id
                """), {'workspace_id': default_workspace_id})
                
                # Update file operations with workspace context
                session.execute(text("""
                    UPDATE file_operations 
                    SET workspace_id = :workspace_id,
                        workspace_relative_path = file_path
                    WHERE workspace_id IS NULL
                """), {'workspace_id': default_workspace_id})
                
                session.commit()
                logger.info("Successfully migrated session data to workspace paradigm")
                
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception(f"Failed to migrate session data: {e}")
    
    def _setup_workspace_detection(self):
        """Setup workspace detection configuration."""
        logger.info("Setting up workspace detection configuration")
        
        # Import the directory detection module
        try:
            from ..orchestrator.directory_detection import DirectoryDetector
            
            detector = DirectoryDetector(security_checks=True)
            result = detector.detect_project_root(starting_path=str(self.base_dir))
            
            # Update default workspace with detection results
            with self.SessionLocal() as session:
                update_data = {
                    'detection_method': result.method.value,
                    'detection_confidence': result.confidence,
                    'project_markers': json.dumps([{
                        'type': marker.marker_type,
                        'file': str(marker.file_path),
                        'confidence': marker.confidence,
                        'description': marker.description
                    } for marker in result.project_markers]),
                    'git_root_path': str(result.git_root) if result.git_root else None,
                    'is_validated': result.validation.is_valid,
                    'is_writable': result.validation.is_writable,
                    'security_warnings': json.dumps(result.validation.warnings or [])
                }
                
                session.execute(text("""
                    UPDATE workspaces 
                    SET detection_method = :detection_method,
                        detection_confidence = :detection_confidence,
                        project_markers = :project_markers,
                        git_root_path = :git_root_path,
                        is_validated = :is_validated,
                        is_writable = :is_writable,
                        security_warnings = :security_warnings,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE workspace_id = 'workspace_migration_default'
                """), update_data)
                
                session.commit()
                
        except ImportError as e:
            logger.warning(f"Could not import directory detection: {e}")
    
    def _update_file_operation_paths(self):
        """Update file operation paths to be workspace-relative."""
        logger.info("Updating file operation paths to workspace-relative format")
        
        with self.SessionLocal() as session:
            try:
                # Get workspace information
                workspace_result = session.execute(text("""
                    SELECT workspace_id, workspace_path FROM workspaces 
                    WHERE workspace_id = 'workspace_migration_default'
                """)).fetchone()
                
                if workspace_result:
                    workspace_id, workspace_path = workspace_result
                    workspace_path = Path(workspace_path)
                    
                    # Update file operations to use relative paths
                    file_ops = session.execute(text("""
                        SELECT operation_id, file_path FROM file_operations 
                        WHERE workspace_id = :workspace_id
                    """), {'workspace_id': workspace_id}).fetchall()
                    
                    for op_id, file_path in file_ops:
                        try:
                            abs_path = Path(file_path)
                            if abs_path.is_absolute():
                                # Try to make it relative to workspace
                                relative_path = abs_path.relative_to(workspace_path)
                                
                                session.execute(text("""
                                    UPDATE file_operations 
                                    SET workspace_relative_path = :relative_path
                                    WHERE operation_id = :op_id
                                """), {
                                    'relative_path': str(relative_path),
                                    'op_id': op_id
                                })
                        except ValueError:
                            # Path is outside workspace, keep as absolute
                            session.execute(text("""
                                UPDATE file_operations 
                                SET workspace_relative_path = :file_path
                                WHERE operation_id = :op_id
                            """), {
                                'file_path': file_path,
                                'op_id': op_id
                            })
                    
                    session.commit()
                    
            except SQLAlchemyError as e:
                session.rollback()
                raise Exception(f"Failed to update file operation paths: {e}")
    
    def _create_workspace_configuration(self):
        """Create default workspace configurations."""
        logger.info("Creating default workspace configurations")
        
        default_configs = [
            ('directories', 'artifact_base_dir', '.task_orchestrator/artifacts', 'string'),
            ('directories', 'logs_dir', '.task_orchestrator/logs', 'string'),
            ('directories', 'temp_dir', '.task_orchestrator/temp', 'string'),
            ('artifacts', 'storage_policy', 'workspace_relative', 'string'),
            ('artifacts', 'backup_enabled', 'true', 'boolean'),
            ('artifacts', 'max_file_size_mb', '50', 'number'),
            ('security', 'allow_outside_workspace', 'false', 'boolean'),
            ('security', 'validate_paths', 'true', 'boolean'),
            ('tools', 'auto_detect_project_type', 'true', 'boolean'),
            ('tools', 'workspace_persistence', 'true', 'boolean')
        ]
        
        with self.SessionLocal() as session:
            for category, key, value, config_type in default_configs:
                session.execute(text("""
                    INSERT OR IGNORE INTO workspace_configurations 
                    (workspace_id, config_category, config_key, config_value, config_type, is_system_generated)
                    VALUES ('workspace_migration_default', :category, :key, :value, :type, TRUE)
                """), {
                    'category': category,
                    'key': key,
                    'value': value,
                    'type': config_type
                })
            
            session.commit()
    
    def _update_indexes(self):
        """Create additional indexes for workspace-based queries."""
        logger.info("Creating workspace-optimized indexes")
        
        index_sql = """
        -- Composite indexes for common workspace queries
        CREATE INDEX IF NOT EXISTS idx_workspace_tasks_active ON workspace_tasks(workspace_id, association_type) 
            WHERE association_type = 'primary';
        
        CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_active ON workspace_artifacts(workspace_id, is_persistent)
            WHERE is_persistent = TRUE;
        
        -- Indexes for workspace activity tracking
        CREATE INDEX IF NOT EXISTS idx_subtasks_workspace_status ON subtasks(workspace_id, status);
        CREATE INDEX IF NOT EXISTS idx_file_operations_workspace_timestamp ON file_operations(workspace_id, timestamp);
        """
        
        with self.engine.connect() as conn:
            for statement in index_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
    
    def _create_compatibility_views(self):
        """Create views for backward compatibility with session-based code."""
        logger.info("Creating backward compatibility views")
        
        compatibility_views_sql = """
        -- Session-to-workspace mapping view
        CREATE VIEW IF NOT EXISTS session_workspace_mapping AS
        SELECT 
            fo.session_id,
            fo.workspace_id,
            w.workspace_path,
            w.workspace_name,
            COUNT(*) as operation_count,
            MIN(fo.timestamp) as first_operation,
            MAX(fo.timestamp) as last_operation
        FROM file_operations fo
        JOIN workspaces w ON fo.workspace_id = w.workspace_id
        WHERE fo.session_id IS NOT NULL
        GROUP BY fo.session_id, fo.workspace_id;

        -- Legacy session compatibility view
        CREATE VIEW IF NOT EXISTS legacy_sessions AS
        SELECT DISTINCT
            session_id,
            workspace_id,
            'migrated' as session_status,
            MIN(timestamp) as session_start,
            MAX(timestamp) as session_end
        FROM file_operations
        WHERE session_id IS NOT NULL
        GROUP BY session_id, workspace_id;
        """
        
        with self.engine.connect() as conn:
            for statement in compatibility_views_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        return self.migration_status.copy()
    
    def validate_migration(self) -> Dict[str, Any]:
        """Validate that migration completed successfully."""
        logger.info("Validating workspace migration")
        
        validation_results = {
            'tables_created': False,
            'data_migrated': False,
            'workspace_detected': False,
            'indexes_created': False,
            'total_workspaces': 0,
            'total_workspace_tasks': 0,
            'errors': []
        }
        
        try:
            with self.SessionLocal() as session:
                # Check if workspace tables exist
                tables = session.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'workspace%'
                """)).fetchall()
                validation_results['tables_created'] = len(tables) >= 4
                
                # Check if data was migrated
                workspace_count = session.execute(text("""
                    SELECT COUNT(*) FROM workspaces
                """)).scalar()
                validation_results['total_workspaces'] = workspace_count
                validation_results['data_migrated'] = workspace_count > 0
                
                # Check workspace-task associations
                task_associations = session.execute(text("""
                    SELECT COUNT(*) FROM workspace_tasks
                """)).scalar()
                validation_results['total_workspace_tasks'] = task_associations
                
                # Check if workspace was properly detected
                detection_result = session.execute(text("""
                    SELECT detection_method, detection_confidence 
                    FROM workspaces 
                    WHERE workspace_id = 'workspace_migration_default'
                """)).fetchone()
                
                if detection_result:
                    method, confidence = detection_result
                    validation_results['workspace_detected'] = (
                        method != 'migration_default' and confidence > 5
                    )
                
                # Check indexes
                indexes = session.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name LIKE '%workspace%'
                """)).fetchall()
                validation_results['indexes_created'] = len(indexes) >= 8
                
        except Exception as e:
            validation_results['errors'].append(str(e))
        
        return validation_results


def run_workspace_migration(db_url: Optional[str] = None, base_dir: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to run workspace paradigm migration.
    
    Args:
        db_url: Database URL (SQLAlchemy format)
        base_dir: Base directory for workspace detection
        
    Returns:
        Migration results dictionary
    """
    migration = WorkspaceMigration(db_url=db_url, base_dir=base_dir)
    return migration.run_migration()