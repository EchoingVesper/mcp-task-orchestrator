---
feature_id: "ENHANCED_SESSION_MANAGEMENT_DATABASE"
version: "1.0.0"
status: "Research"
priority: "Critical"
category: "Infrastructure"
dependencies: ["ENHANCED_SESSION_MANAGEMENT_V1"]
size_lines: 285
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/research/enhanced-session-management/README.md"
  - "docs/developers/planning/features/research/enhanced-session-management/architecture-specification.md"
module_type: "specification"
modularized_from: "docs/developers/planning/features/research/[CRITICAL]_enhanced_session_management_architecture.md"
---

# Enhanced Database Schema Design

This document specifies the complete database schema for session-aware task orchestration.

#
# Core Design Principles

- **Session-First Design**: All operations occur within session context

- **Referential Integrity**: Proper foreign key constraints and cascading deletes

- **Performance Optimization**: Strategic indexing for common query patterns

- **Bi-directional Sync**: Support for database-markdown synchronization

- **Data Consistency**: Check constraints and validation rules

#
# Session Management Schema

#
## Sessions Table

Core session management with comprehensive metadata and lifecycle tracking.

```sql
-- =====================================================
-- SESSIONS TABLE: Core session management
-- =====================================================
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    session_type TEXT DEFAULT 'project',  -- project, maintenance, research, etc.
    mode_file TEXT,  -- Reference to .yaml role configuration
    status TEXT DEFAULT 'active',  -- active, paused, completed, archived
    
    -- Organizational metadata
    project_root_path TEXT,  -- Base directory for .task_orchestrator files
    markdown_file_path TEXT,  -- Path to human-readable session.md
    priority_level INTEGER DEFAULT 3,  -- 1=urgent, 2=high, 3=medium, 4=low, 5=someday
    
    -- Tracking and metrics
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    progress_percentage REAL DEFAULT 0.0,
    estimated_completion_date TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    archived_at TIMESTAMP,
    
    -- Constraints
    CHECK (priority_level BETWEEN 1 AND 5),
    CHECK (progress_percentage BETWEEN 0.0 AND 100.0)
);

```text

#
## Active Session Management

Singleton table enforcing single active session constraint.

```text
sql
-- =====================================================
-- ACTIVE SESSION MANAGEMENT: Only one active session
-- =====================================================
CREATE TABLE active_session (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton table
    session_id TEXT NOT NULL,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_data JSON,  -- Cached session context for performance
    
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
);

```text

#
# Task Management Schema

#
## Enhanced Tasks Table

Session-aware task management with hierarchical organization and comprehensive tracking.

```text
sql
-- =====================================================
-- ENHANCED TASKS TABLE: Session-aware task management
-- =====================================================
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,  -- All tasks belong to a session
    parent_task_id TEXT,
    root_task_id TEXT,
    
    -- Task organization
    task_group TEXT,  -- Logical grouping within session (e.g., 'frontend', 'backend')
    level INTEGER DEFAULT 0,
    hierarchy_path TEXT,  -- Materialized path: /session/group/task
    position_in_group INTEGER DEFAULT 0,  -- Ordering within group
    
    -- Task details
    title TEXT NOT NULL,
    description TEXT,
    specialist_type TEXT,
    complexity_level TEXT DEFAULT 'moderate',
    
    -- Status and progress
    status TEXT DEFAULT 'pending',
    progress_percentage REAL DEFAULT 0.0,
    estimated_effort INTEGER,  -- In hours
    actual_effort INTEGER,     -- In hours
    
    -- Dependencies and relationships
    depends_on JSON,  -- List of prerequisite task IDs
    blocks JSON,      -- List of dependent task IDs
    related_tasks JSON,  -- List of related task IDs
    
    -- Persistence tracking
    markdown_section TEXT,  -- Section in session markdown file
    file_operations_count INTEGER DEFAULT 0,
    verification_status TEXT DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys and constraints
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (root_task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    
    CHECK (level >= 0),
    CHECK (progress_percentage BETWEEN 0.0 AND 100.0),
    CHECK (estimated_effort >= 0),
    CHECK (actual_effort >= 0)
);

```text

#
## Task Groups

Logical organization of tasks within sessions.

```text
sql
-- =====================================================
-- TASK GROUPS: Logical organization within sessions
-- =====================================================
CREATE TABLE task_groups (
    group_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    group_name TEXT NOT NULL,
    description TEXT,
    
    -- Group organization
    parent_group_id TEXT,  -- Support nested groups
    group_level INTEGER DEFAULT 0,
    position_in_session INTEGER DEFAULT 0,
    
    -- Group metadata
    specialist_focus TEXT,  -- Primary specialist type for this group
    estimated_effort INTEGER DEFAULT 0,
    priority_level INTEGER DEFAULT 3,
    
    -- Progress tracking
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    progress_percentage REAL DEFAULT 0.0,
    
    -- Persistence
    markdown_section TEXT,  -- Section in session markdown
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys and constraints
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_group_id) REFERENCES task_groups (group_id) ON DELETE CASCADE,
    
    CHECK (group_level >= 0),
    CHECK (priority_level BETWEEN 1 AND 5),
    CHECK (progress_percentage BETWEEN 0.0 AND 100.0),
    UNIQUE (session_id, group_name)
);

```text

#
# Mode and Configuration Schema

#
## Session Modes

Role configuration system supporting session-specific behavior.

```text
sql
-- =====================================================
-- SESSION MODES: Role configuration system
-- =====================================================
CREATE TABLE session_modes (
    mode_id TEXT PRIMARY KEY,
    mode_name TEXT NOT NULL,
    yaml_file_path TEXT NOT NULL,
    yaml_content_hash TEXT,  -- For change detection
    
    -- Mode metadata
    description TEXT,
    specialist_roles JSON,  -- Available roles in this mode
    default_complexity TEXT DEFAULT 'moderate',
    auto_task_routing BOOLEAN DEFAULT FALSE,
    
    -- Validation
    is_valid BOOLEAN DEFAULT TRUE,
    last_validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_errors JSON,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (yaml_file_path)
);

```text

#
## Session-Mode Binding

Links sessions to specific modes for behavior customization.

```text
sql
-- =====================================================
-- SESSION-MODE BINDING: Link sessions to modes
-- =====================================================
CREATE TABLE session_mode_bindings (
    session_id TEXT NOT NULL,
    mode_id TEXT NOT NULL,
    bound_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    binding_context JSON,  -- Additional configuration for this binding
    
    PRIMARY KEY (session_id, mode_id),
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
    FOREIGN KEY (mode_id) REFERENCES session_modes (mode_id) ON DELETE CASCADE
);

```text

#
# Persistence and Synchronization Schema

#
## Markdown Sync State

Bi-directional persistence tracking between database and markdown files.

```text
sql
-- =====================================================
-- MARKDOWN SYNC: Bi-directional persistence tracking
-- =====================================================
CREATE TABLE markdown_sync_state (
    sync_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    markdown_file_path TEXT NOT NULL,
    
    -- Sync status
    last_db_to_md_sync TIMESTAMP,
    last_md_to_db_sync TIMESTAMP,
    sync_status TEXT DEFAULT 'synchronized',  -- synchronized, db_newer, md_newer, conflict
    
    -- Content tracking
    db_content_hash TEXT,
    md_content_hash TEXT,
    last_conflict_resolution TIMESTAMP,
    
    -- Change detection
    file_monitor_active BOOLEAN DEFAULT TRUE,
    last_file_modification TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
    UNIQUE (session_id, markdown_file_path)
);

```text

#
# Performance Optimization Indexes

Strategic indexing for common query patterns and performance optimization.

```text
sql
-- Performance optimization indexes
CREATE INDEX idx_sessions_status ON sessions (status);
CREATE INDEX idx_sessions_priority ON sessions (priority_level);
CREATE INDEX idx_sessions_activity ON sessions (last_activity_at);

CREATE INDEX idx_tasks_session ON tasks (session_id);
CREATE INDEX idx_tasks_hierarchy ON tasks (session_id, hierarchy_path);
CREATE INDEX idx_tasks_status ON tasks (session_id, status);
CREATE INDEX idx_tasks_group ON tasks (session_id, task_group);
CREATE INDEX idx_tasks_parent ON tasks (parent_task_id);

CREATE INDEX idx_task_groups_session ON task_groups (session_id);
CREATE INDEX idx_task_groups_parent ON task_groups (parent_group_id);

CREATE INDEX idx_markdown_sync_session ON markdown_sync_state (session_id);
CREATE INDEX idx_markdown_sync_status ON markdown_sync_state (sync_status);
```text

#
# Data Integrity Rules

- **Cascading Deletes**: Session deletion removes all related tasks, groups, and sync state

- **Check Constraints**: Validate percentage ranges, effort values, and priority levels

- **Unique Constraints**: Prevent duplicate session names and group names within sessions

- **Foreign Key Constraints**: Maintain referential integrity across all relationships

#
# Migration Considerations

- **Backward Compatibility**: Existing tasks table can be migrated by adding session_id

- **Data Preservation**: Migration scripts preserve all existing task data

- **Gradual Rollout**: New schema supports both session-aware and legacy operations

- **Performance Impact**: Indexes ensure query performance remains optimal during migration
