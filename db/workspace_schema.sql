-- Workspace Paradigm Database Schema
-- Version 1.0 - Transition from Session-based to Workspace-based paradigm
-- Created: 2025-06-08
-- Purpose: Support workspace-centric task orchestration with proper artifact location control

-- Enable foreign key constraints and WAL mode for better performance
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

/* ============================================ */
/* Workspace Registry */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    workspace_name TEXT NOT NULL,
    workspace_path TEXT NOT NULL UNIQUE,
    detection_method TEXT NOT NULL, -- git_root, project_marker, explicit, mcp_client_pwd, fallback
    detection_confidence INTEGER NOT NULL, -- 1-10 scale
    
    -- Project Information
    project_type TEXT, -- python, javascript, rust, go, java, cpp, dotnet, docker, etc.
    project_markers TEXT, -- JSON array of detected markers with metadata
    git_root_path TEXT,
    
    -- Configuration and Policies
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    artifact_storage_policy TEXT DEFAULT 'workspace_relative', -- workspace_relative, absolute, hybrid
    
    -- Security and Validation
    is_validated BOOLEAN DEFAULT FALSE,
    is_writable BOOLEAN DEFAULT TRUE,
    security_warnings TEXT, -- JSON array of security warnings
    
    -- Usage Statistics
    total_tasks INTEGER DEFAULT 0,
    active_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* ============================================ */
/* Workspace-Task Associations */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspace_tasks (
    association_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    
    -- Association Metadata
    association_type TEXT DEFAULT 'primary', -- primary, reference, archived, migrated
    created_in_workspace BOOLEAN DEFAULT TRUE,
    relative_artifact_paths TEXT, -- JSON array of workspace-relative artifact paths
    
    -- Task Context in Workspace
    task_working_directory TEXT, -- Relative to workspace root
    environment_variables TEXT, -- JSON object of workspace-specific env vars
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints (will be added during migration)
    -- FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    -- FOREIGN KEY (task_id) REFERENCES task_breakdowns(parent_task_id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate associations
    UNIQUE(workspace_id, task_id, association_type)
);

/* ============================================ */
/* Workspace Artifact Storage */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspace_artifacts (
    artifact_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    task_id TEXT, -- nullable for workspace-level artifacts
    
    -- Storage Information
    relative_path TEXT NOT NULL, -- Path relative to workspace root
    absolute_path TEXT NOT NULL, -- Absolute path for verification/fallback
    artifact_type TEXT NOT NULL, -- code, documentation, analysis, design, test, config, general
    storage_method TEXT DEFAULT 'file', -- file, embedded, external, symlink
    
    -- Content and Metadata
    content_hash TEXT,
    file_size INTEGER,
    mime_type TEXT,
    encoding TEXT DEFAULT 'utf-8',
    content_preview TEXT, -- First few lines/chars for quick display
    
    -- Workspace Context
    created_by_task BOOLEAN DEFAULT TRUE,
    is_persistent BOOLEAN DEFAULT TRUE, -- Should survive task completion
    is_tracked_by_git BOOLEAN DEFAULT FALSE, -- Is this file tracked by git?
    backup_available BOOLEAN DEFAULT FALSE,
    
    -- Version Control
    version INTEGER DEFAULT 1,
    previous_version_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP,
    last_modified_at TIMESTAMP
);

/* ============================================ */
/* Workspace Configuration */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspace_configurations (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    
    -- Configuration Identity
    config_category TEXT NOT NULL, -- directories, artifacts, tools, security, git, environment
    config_key TEXT NOT NULL,
    config_value TEXT NOT NULL, -- JSON-encoded value
    config_type TEXT NOT NULL, -- string, number, boolean, array, object
    
    -- Configuration Metadata
    is_user_defined BOOLEAN DEFAULT FALSE,
    is_system_generated BOOLEAN DEFAULT TRUE,
    is_inherited BOOLEAN DEFAULT FALSE, -- From parent workspace or global config
    description TEXT,
    validation_schema TEXT, -- JSON schema for value validation
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints (will be added during migration)
    -- FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    
    -- Unique constraint for config keys within workspace
    UNIQUE(workspace_id, config_category, config_key)
);

/* ============================================ */
/* Workspace File Operations (Enhanced) */
/* ============================================ */
-- CREATE VIEW IF NOT EXISTS workspace_file_operations AS
-- SELECT 
--     fo.*,
--     w.workspace_name,
--     w.workspace_path,
--     wa.relative_path as artifact_relative_path,
--     wa.artifact_type
-- FROM file_operations fo
-- LEFT JOIN workspaces w ON fo.workspace_id = w.workspace_id
-- LEFT JOIN workspace_artifacts wa ON fo.workspace_relative_path = wa.relative_path 
--     AND fo.workspace_id = wa.workspace_id;

/* ============================================ */
/* Workspace Relationships and Dependencies */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspace_relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_workspace_id TEXT NOT NULL,
    child_workspace_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL, -- subproject, dependency, reference, symlink
    
    -- Relationship Metadata
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    dependency_version TEXT, -- For dependency relationships
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints (will be added during migration)
    -- FOREIGN KEY (parent_workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    -- FOREIGN KEY (child_workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    
    -- Prevent self-references and duplicates
    CHECK (parent_workspace_id != child_workspace_id),
    UNIQUE(parent_workspace_id, child_workspace_id, relationship_type)
);

/* ============================================ */
/* Migration Tracking */
/* ============================================ */
CREATE TABLE IF NOT EXISTS workspace_migrations (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT NOT NULL UNIQUE,
    migration_type TEXT NOT NULL, -- schema, data, cleanup, validation
    status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, rolled_back
    
    -- Migration Details
    workspace_id TEXT, -- Target workspace for data migrations
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    rollback_sql TEXT, -- SQL to rollback this migration
    
    -- Statistics
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    migration_data TEXT, -- JSON with migration-specific data
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints (will be added during migration)
    -- FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON DELETE SET NULL
);

/* ============================================ */
/* Performance Indexes */
/* ============================================ */
CREATE INDEX IF NOT EXISTS idx_workspaces_path ON workspaces(workspace_path);
CREATE INDEX IF NOT EXISTS idx_workspaces_active ON workspaces(is_active);
CREATE INDEX IF NOT EXISTS idx_workspaces_default ON workspaces(is_default);
CREATE INDEX IF NOT EXISTS idx_workspaces_activity ON workspaces(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_workspaces_detection ON workspaces(detection_method, detection_confidence);

-- Workspace-Task association indexes
CREATE INDEX IF NOT EXISTS idx_workspace_tasks_workspace ON workspace_tasks(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_tasks_task ON workspace_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_workspace_tasks_type ON workspace_tasks(association_type);
CREATE INDEX IF NOT EXISTS idx_workspace_tasks_active ON workspace_tasks(workspace_id, association_type) 
    WHERE association_type = 'primary';

-- Workspace artifact indexes
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_workspace ON workspace_artifacts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_task ON workspace_artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_type ON workspace_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_path ON workspace_artifacts(relative_path);
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_persistent ON workspace_artifacts(workspace_id, is_persistent)
    WHERE is_persistent = TRUE;
CREATE INDEX IF NOT EXISTS idx_workspace_artifacts_content_hash ON workspace_artifacts(content_hash);

-- Workspace configuration indexes
CREATE INDEX IF NOT EXISTS idx_workspace_config_workspace ON workspace_configurations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_config_category ON workspace_configurations(config_category);
CREATE INDEX IF NOT EXISTS idx_workspace_config_key ON workspace_configurations(config_category, config_key);
CREATE INDEX IF NOT EXISTS idx_workspace_config_user ON workspace_configurations(is_user_defined);

-- Workspace relationship indexes
CREATE INDEX IF NOT EXISTS idx_workspace_rel_parent ON workspace_relationships(parent_workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_rel_child ON workspace_relationships(child_workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_rel_type ON workspace_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_workspace_rel_active ON workspace_relationships(is_active);

/* ============================================ */
/* Triggers for Data Integrity and Automation */
/* ============================================ */
CREATE TRIGGER IF NOT EXISTS update_workspace_timestamp 
AFTER UPDATE ON workspaces
BEGIN
    UPDATE workspaces SET updated_at = CURRENT_TIMESTAMP WHERE workspace_id = NEW.workspace_id;
END;

-- Update workspace activity when tasks are created/updated
CREATE TRIGGER IF NOT EXISTS update_workspace_activity_on_task
AFTER INSERT ON workspace_tasks
BEGIN
    UPDATE workspaces 
    SET last_activity_at = CURRENT_TIMESTAMP,
        total_tasks = total_tasks + 1,
        active_tasks = active_tasks + 1
    WHERE workspace_id = NEW.workspace_id;
END;

-- Update workspace task counts when task status changes (will be created during migration)
-- CREATE TRIGGER IF NOT EXISTS update_workspace_task_counts
-- AFTER UPDATE OF status ON subtasks
-- WHEN NEW.workspace_id IS NOT NULL
-- BEGIN
--     UPDATE workspaces 
--     SET active_tasks = (
--         SELECT COUNT(*) FROM subtasks 
--         WHERE workspace_id = NEW.workspace_id AND status IN ('pending', 'in_progress')
--     ),
--     completed_tasks = (
--         SELECT COUNT(*) FROM subtasks 
--         WHERE workspace_id = NEW.workspace_id AND status = 'completed'
--     ),
--     failed_tasks = (
--         SELECT COUNT(*) FROM subtasks 
--         WHERE workspace_id = NEW.workspace_id AND status = 'failed'
--     ),
--     last_activity_at = CURRENT_TIMESTAMP
--     WHERE workspace_id = NEW.workspace_id;
-- END;

-- Update workspace configuration timestamps
CREATE TRIGGER IF NOT EXISTS update_workspace_config_timestamp 
AFTER UPDATE ON workspace_configurations
BEGIN
    UPDATE workspace_configurations SET updated_at = CURRENT_TIMESTAMP 
    WHERE config_id = NEW.config_id;
END;

-- Update workspace artifact timestamps and workspace activity
CREATE TRIGGER IF NOT EXISTS update_workspace_artifact_activity
AFTER INSERT OR UPDATE ON workspace_artifacts
BEGIN
    UPDATE workspace_artifacts SET updated_at = CURRENT_TIMESTAMP 
    WHERE artifact_id = NEW.artifact_id;
    
    UPDATE workspaces SET last_activity_at = CURRENT_TIMESTAMP 
    WHERE workspace_id = NEW.workspace_id;
END;

/* ============================================ */
/* Backward Compatibility Views */
/* ============================================ */
-- These views will be created during migration when the referenced tables exist
-- CREATE VIEW IF NOT EXISTS session_workspace_mapping AS
-- SELECT 
--     fo.session_id,
--     fo.workspace_id,
--     w.workspace_path,
--     w.workspace_name,
--     COUNT(*) as operation_count,
--     MIN(fo.timestamp) as first_operation,
--     MAX(fo.timestamp) as last_operation
-- FROM file_operations fo
-- JOIN workspaces w ON fo.workspace_id = w.workspace_id
-- WHERE fo.session_id IS NOT NULL AND fo.workspace_id IS NOT NULL
-- GROUP BY fo.session_id, fo.workspace_id;

-- Legacy session view for backward compatibility
-- CREATE VIEW IF NOT EXISTS legacy_sessions AS
-- SELECT DISTINCT
--     session_id,
--     workspace_id,
--     'migrated' as session_status,
--     MIN(timestamp) as session_start,
--     MAX(timestamp) as session_end,
--     COUNT(*) as total_operations
-- FROM file_operations
-- WHERE session_id IS NOT NULL
-- GROUP BY session_id, workspace_id;

-- Workspace task summary view
-- CREATE VIEW IF NOT EXISTS workspace_task_summary AS
-- SELECT 
--     w.workspace_id,
--     w.workspace_name,
--     w.workspace_path,
--     COUNT(DISTINCT wt.task_id) as total_tasks,
--     COUNT(DISTINCT CASE WHEN s.status IN ('pending', 'in_progress') THEN wt.task_id END) as active_tasks,
--     COUNT(DISTINCT CASE WHEN s.status = 'completed' THEN wt.task_id END) as completed_tasks,
--     COUNT(DISTINCT CASE WHEN s.status = 'failed' THEN wt.task_id END) as failed_tasks,
--     MAX(COALESCE(s.completed_at, s.created_at)) as last_task_activity
-- FROM workspaces w
-- LEFT JOIN workspace_tasks wt ON w.workspace_id = wt.workspace_id
-- LEFT JOIN subtasks s ON wt.task_id = s.parent_task_id
-- GROUP BY w.workspace_id, w.workspace_name, w.workspace_path;

/* ============================================ */
/* Default Configuration Data */
/* ============================================ */
INSERT OR IGNORE INTO workspace_migrations (
    migration_name, 
    migration_type, 
    status, 
    migration_data,
    created_at
) VALUES (
    'workspace_schema_creation',
    'schema',
    'completed',
    '{"version": "1.0", "description": "Initial workspace paradigm schema creation"}',
    CURRENT_TIMESTAMP
);

-- Note: Default workspace and configuration data will be inserted by the migration script
-- to ensure proper workspace detection and setup based on the actual environment.