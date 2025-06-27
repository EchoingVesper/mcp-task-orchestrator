-- Generic Task Model Database Schema
-- Version 2.0 - Foundation for unified task management
-- Created: 2025-01-06
-- Purpose: Replace dual-model system (TaskBreakdown + SubTask) with unified GenericTask model

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================
-- Core Generic Task Table
-- ============================================
-- This is the main table that unifies task breakdowns and subtasks
CREATE TABLE IF NOT EXISTS generic_tasks (
    -- Primary identification
    task_id TEXT PRIMARY KEY,
    parent_task_id TEXT,
    
    -- Task metadata
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    task_type TEXT NOT NULL DEFAULT 'standard', -- standard, milestone, review, approval, etc.
    
    -- Hierarchy management
    hierarchy_path TEXT NOT NULL, -- e.g., "/root/parent1/parent2/task_id"
    hierarchy_level INTEGER NOT NULL DEFAULT 0,
    position_in_parent INTEGER DEFAULT 0, -- for ordered siblings
    
    -- Status and lifecycle
    status TEXT NOT NULL DEFAULT 'pending',
    lifecycle_stage TEXT NOT NULL DEFAULT 'created', -- created, planning, active, blocked, completed, failed, archived
    
    -- Complexity and effort estimation
    complexity TEXT DEFAULT 'moderate', -- simple, moderate, complex, very_complex
    estimated_effort TEXT, -- e.g., "2 days", "4 hours"
    actual_effort TEXT,
    
    -- Assignment and ownership
    specialist_type TEXT, -- architect, implementer, debugger, etc.
    assigned_to TEXT, -- future: user/agent assignment
    
    -- Context and configuration
    context TEXT, -- JSON field for additional context
    configuration TEXT, -- JSON field for task-specific config
    
    -- Results and artifacts
    results TEXT,
    summary TEXT,
    
    -- Quality and validation
    quality_gate_level TEXT DEFAULT 'standard', -- basic, standard, comprehensive
    verification_status TEXT DEFAULT 'pending',
    
    -- Automation flags
    auto_maintenance_enabled BOOLEAN DEFAULT TRUE,
    is_template BOOLEAN DEFAULT FALSE,
    template_id TEXT, -- reference to task_templates if instantiated from template
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date TIMESTAMP,
    
    -- Soft delete support
    deleted_at TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (parent_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES task_templates(template_id)
);

-- Indexes for performance optimization
CREATE INDEX idx_generic_tasks_parent ON generic_tasks(parent_task_id);
CREATE INDEX idx_generic_tasks_status ON generic_tasks(status);
CREATE INDEX idx_generic_tasks_lifecycle ON generic_tasks(lifecycle_stage);
CREATE INDEX idx_generic_tasks_hierarchy ON generic_tasks(hierarchy_path);
CREATE INDEX idx_generic_tasks_type ON generic_tasks(task_type);
CREATE INDEX idx_generic_tasks_specialist ON generic_tasks(specialist_type);
CREATE INDEX idx_generic_tasks_created ON generic_tasks(created_at);
CREATE INDEX idx_generic_tasks_deleted ON generic_tasks(deleted_at);

-- ============================================
-- Task Attributes (EAV Pattern)
-- ============================================
-- Extensible attributes system for task-specific properties
CREATE TABLE IF NOT EXISTS task_attributes (
    attribute_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    attribute_name TEXT NOT NULL,
    attribute_value TEXT NOT NULL,
    attribute_type TEXT NOT NULL, -- string, number, boolean, date, json
    attribute_category TEXT, -- grouping for related attributes
    is_indexed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    UNIQUE(task_id, attribute_name)
);

-- Indexes for EAV pattern optimization
CREATE INDEX idx_task_attributes_task ON task_attributes(task_id);
CREATE INDEX idx_task_attributes_name ON task_attributes(attribute_name);
CREATE INDEX idx_task_attributes_category ON task_attributes(attribute_category);
CREATE INDEX idx_task_attributes_indexed ON task_attributes(is_indexed, attribute_name) WHERE is_indexed = TRUE;

-- ============================================
-- Task Dependencies
-- ============================================
-- Rich dependency modeling with multiple dependency types
CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dependent_task_id TEXT NOT NULL,
    prerequisite_task_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL, -- completion, data, approval, prerequisite, blocks
    dependency_status TEXT NOT NULL DEFAULT 'pending', -- pending, satisfied, failed, waived
    
    -- Dependency configuration
    is_mandatory BOOLEAN DEFAULT TRUE,
    auto_satisfy BOOLEAN DEFAULT FALSE,
    satisfaction_criteria TEXT, -- JSON with specific criteria
    
    -- Data dependencies
    output_artifact_ref TEXT, -- reference to artifact from prerequisite
    input_parameter_name TEXT, -- parameter in dependent task
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    satisfied_at TIMESTAMP,
    waived_at TIMESTAMP,
    waived_by TEXT,
    waiver_reason TEXT,
    
    FOREIGN KEY (dependent_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    UNIQUE(dependent_task_id, prerequisite_task_id, dependency_type)
);

-- Indexes for dependency resolution
CREATE INDEX idx_dependencies_dependent ON task_dependencies(dependent_task_id);
CREATE INDEX idx_dependencies_prerequisite ON task_dependencies(prerequisite_task_id);
CREATE INDEX idx_dependencies_type ON task_dependencies(dependency_type);
CREATE INDEX idx_dependencies_status ON task_dependencies(dependency_status);

-- ============================================
-- Task Templates
-- ============================================
-- Reusable task patterns and workflows
CREATE TABLE IF NOT EXISTS task_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL UNIQUE,
    template_category TEXT NOT NULL, -- development, testing, deployment, documentation, etc.
    template_version INTEGER NOT NULL DEFAULT 1,
    
    -- Template content
    description TEXT NOT NULL,
    template_schema TEXT NOT NULL, -- JSON Schema for parameters
    default_values TEXT, -- JSON with default parameter values
    task_structure TEXT NOT NULL, -- JSON defining task hierarchy and relationships
    
    -- Template metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    created_by TEXT,
    tags TEXT, -- JSON array of tags
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deprecated_at TIMESTAMP
);

-- Indexes for template management
CREATE INDEX idx_templates_name ON task_templates(template_name);
CREATE INDEX idx_templates_category ON task_templates(template_category);
CREATE INDEX idx_templates_active ON task_templates(is_active);
CREATE INDEX idx_templates_usage ON task_templates(usage_count DESC);

-- ============================================
-- Task Events
-- ============================================
-- Comprehensive event tracking for lifecycle and changes
CREATE TABLE IF NOT EXISTS task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL, -- created, updated, status_changed, assigned, completed, failed, etc.
    event_category TEXT NOT NULL, -- lifecycle, data, system, user
    
    -- Event details
    event_data TEXT, -- JSON with event-specific data
    previous_value TEXT, -- for change events
    new_value TEXT, -- for change events
    
    -- Event metadata
    triggered_by TEXT, -- system, user, automation, dependency
    actor_id TEXT, -- who/what triggered the event
    session_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE
);

-- Indexes for event querying
CREATE INDEX idx_events_task ON task_events(task_id);
CREATE INDEX idx_events_type ON task_events(event_type);
CREATE INDEX idx_events_category ON task_events(event_category);
CREATE INDEX idx_events_created ON task_events(created_at);
CREATE INDEX idx_events_session ON task_events(session_id);

-- ============================================
-- Task Artifacts (Enhanced)
-- ============================================
-- Store task outputs and working artifacts
CREATE TABLE IF NOT EXISTS task_artifacts (
    artifact_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL, -- code, documentation, analysis, design, test, config, general
    artifact_name TEXT NOT NULL,
    
    -- Content storage
    content TEXT, -- for text artifacts
    content_hash TEXT,
    file_reference TEXT, -- for file-based artifacts
    file_size INTEGER,
    
    -- Metadata
    mime_type TEXT,
    encoding TEXT DEFAULT 'utf-8',
    is_primary BOOLEAN DEFAULT FALSE,
    visibility TEXT DEFAULT 'private', -- private, public, restricted
    
    -- Versioning
    version INTEGER DEFAULT 1,
    previous_version_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (previous_version_id) REFERENCES task_artifacts(artifact_id)
);

-- Indexes for artifact management
CREATE INDEX idx_artifacts_task ON task_artifacts(task_id);
CREATE INDEX idx_artifacts_type ON task_artifacts(artifact_type);
CREATE INDEX idx_artifacts_primary ON task_artifacts(is_primary);
CREATE INDEX idx_artifacts_visibility ON task_artifacts(visibility);

-- ============================================
-- Migration Support Tables
-- ============================================
-- Track migration from old schema to new
CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT NOT NULL UNIQUE,
    migration_type TEXT NOT NULL, -- schema, data, cleanup
    status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, rolled_back
    
    -- Migration details
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    rollback_sql TEXT, -- SQL to rollback this migration
    
    -- Statistics
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Legacy mapping table for migration
CREATE TABLE IF NOT EXISTS legacy_task_mapping (
    old_task_id TEXT PRIMARY KEY,
    new_task_id TEXT NOT NULL,
    old_task_type TEXT NOT NULL, -- task_breakdown, subtask
    migration_id INTEGER NOT NULL,
    mapped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (new_task_id) REFERENCES generic_tasks(task_id),
    FOREIGN KEY (migration_id) REFERENCES schema_migrations(migration_id)
);

-- ============================================
-- Views for Backward Compatibility
-- ============================================
-- Provide compatible views for existing code
CREATE VIEW IF NOT EXISTS task_breakdowns_compat AS
SELECT 
    task_id as parent_task_id,
    description,
    complexity,
    context,
    created_at
FROM generic_tasks
WHERE parent_task_id IS NULL;

CREATE VIEW IF NOT EXISTS subtasks_compat AS
SELECT 
    task_id,
    parent_task_id,
    title,
    description,
    specialist_type,
    '[]' as dependencies, -- will need computed from task_dependencies
    estimated_effort,
    status,
    results,
    '[]' as artifacts, -- will need computed from task_artifacts
    0 as file_operations_count,
    verification_status,
    created_at,
    completed_at,
    FALSE as prerequisite_satisfaction_required,
    auto_maintenance_enabled,
    quality_gate_level
FROM generic_tasks
WHERE parent_task_id IS NOT NULL;

-- ============================================
-- Triggers for Data Integrity
-- ============================================
-- Update timestamps automatically
CREATE TRIGGER update_generic_tasks_timestamp 
AFTER UPDATE ON generic_tasks
BEGIN
    UPDATE generic_tasks SET updated_at = CURRENT_TIMESTAMP WHERE task_id = NEW.task_id;
END;

CREATE TRIGGER update_task_attributes_timestamp 
AFTER UPDATE ON task_attributes
BEGIN
    UPDATE task_attributes SET updated_at = CURRENT_TIMESTAMP WHERE attribute_id = NEW.attribute_id;
END;

-- Update hierarchy path when parent changes
CREATE TRIGGER update_hierarchy_path
AFTER UPDATE OF parent_task_id ON generic_tasks
BEGIN
    -- This would need to be implemented in application logic due to SQLite limitations
    -- Just a placeholder to show the concept
    SELECT RAISE(IGNORE);
END;

-- Increment template usage count
CREATE TRIGGER increment_template_usage
AFTER INSERT ON generic_tasks
WHEN NEW.template_id IS NOT NULL
BEGIN
    UPDATE task_templates 
    SET usage_count = usage_count + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE template_id = NEW.template_id;
END;