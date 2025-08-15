

# Generic Task Model Database Architecture

**Version**: 2.0  
**Date**: 2025-01-06  
**Status**: Design Complete  
**Author**: System Architect

#

# Executive Summary

This document presents the comprehensive database schema design for the Generic Task Model, which will replace the current dual-model system (TaskBreakdown + SubTask) with a unified, extensible task management architecture. The design emphasizes scalability, flexibility, and zero-disruption migration.

#

# Design Principles

#

#

# 1. Unified Task Model

- Single `generic_tasks` table replaces both `task_breakdowns` and `subtasks`

- Hierarchical relationships through self-referencing foreign keys

- Task types differentiate between various task categories

#

#

# 2. Extensibility Through EAV Pattern

- `task_attributes` table enables custom properties without schema changes

- Type-safe attribute storage with validation support

- Indexed attributes for performance-critical queries

#

#

# 3. Rich Dependency Modeling

- Multiple dependency types (completion, data, approval, prerequisite, blocks)

- Automatic dependency satisfaction tracking

- Waiver support for exceptional cases

#

#

# 4. Template-Driven Workflows

- Reusable task patterns stored in `task_templates`

- JSON Schema validation for template parameters

- Version control and usage tracking

#

#

# 5. Comprehensive Event Tracking

- All task lifecycle changes recorded in `task_events`

- Support for event-driven architectures

- Audit trail for compliance and debugging

#

# Core Tables

#

#

# generic_tasks

The central table unifying all task types:

```sql

- task_id: Unique identifier

- parent_task_id: Self-referencing for hierarchy

- hierarchy_path: Materialized path for efficient tree queries

- task_type: Extensible task categorization

- lifecycle_stage: Rich state machine support

- specialist_type: Role-based assignment

```text

**Key Design Decisions:**

- Materialized path (`hierarchy_path`) enables efficient subtree queries

- Soft delete support via `deleted_at` timestamp

- JSON fields for flexible configuration and context

#

#

# task_attributes (EAV Pattern)

Enables extensible properties without schema modifications:

```text
sql

- attribute_name: Property identifier

- attribute_value: Stored as text, parsed by type

- attribute_type: Ensures type safety

- is_indexed: Performance optimization flag

```text

**Use Cases:**

- Custom fields for specific task types

- Integration-specific metadata

- User-defined properties

#

#

# task_dependencies

Models complex task relationships:

```text
sql

- dependency_type: completion|data|approval|prerequisite|blocks

- is_mandatory: Enforcement level

- auto_satisfy: Automatic resolution capability

- satisfaction_criteria: JSON-based rules

```text

**Advanced Features:**

- Data flow modeling (output → input connections)

- Waiver system for exceptional cases

- Cycle detection support

#

#

# task_templates

Enables reusable workflow patterns:

```text
sql

- template_schema: JSON Schema for parameters

- task_structure: Hierarchical task definition

- usage_count: Popularity tracking

- version control: Template evolution

```text

**Benefits:**

- Standardized workflows

- Reduced setup time

- Best practice enforcement

#

#

# task_events

Comprehensive activity tracking:

```text
sql

- event_type: Granular event categorization

- event_data: JSON payload for event details

- triggered_by: system|user|automation|dependency

- session_id: Correlation support

```text

**Capabilities:**

- Real-time event streaming

- Audit trail generation

- Performance analysis

#

# Performance Optimizations

#

#

# Indexing Strategy

```text
sql
-- Primary access patterns
CREATE INDEX idx_generic_tasks_parent ON generic_tasks(parent_task_id);
CREATE INDEX idx_generic_tasks_hierarchy ON generic_tasks(hierarchy_path);

-- Status and filtering
CREATE INDEX idx_generic_tasks_status ON generic_tasks(status);
CREATE INDEX idx_generic_tasks_lifecycle ON generic_tasks(lifecycle_stage);

-- EAV optimization
CREATE INDEX idx_task_attributes_indexed ON task_attributes(is_indexed, attribute_name) 
WHERE is_indexed = TRUE;

```text

#

#

# Query Optimization Patterns

#

#

#

# Efficient Subtree Queries

```text
sql
-- Get all descendants of a task
SELECT * FROM generic_tasks 
WHERE hierarchy_path LIKE '/root/parent/task123/%';

```text

#

#

#

# Fast Dependency Resolution

```text
sql
-- Check unsatisfied dependencies
SELECT * FROM task_dependencies 
WHERE dependent_task_id = ? 
AND dependency_status = 'pending' 
AND is_mandatory = TRUE;

```text

#

# Migration Strategy

#

#

# Backward Compatibility Views

```text
sql
-- Maintain API compatibility during transition
CREATE VIEW task_breakdowns_compat AS
SELECT task_id as parent_task_id, ...
FROM generic_tasks WHERE parent_task_id IS NULL;

CREATE VIEW subtasks_compat AS
SELECT task_id, parent_task_id, ...
FROM generic_tasks WHERE parent_task_id IS NOT NULL;

```text

#

#

# Migration Tracking

```text
sql
-- Track migration progress
schema_migrations: Migration execution history
legacy_task_mapping: Old ID → New ID mappings
```text

#

#

# Zero-Downtime Migration Path

1. Deploy new schema alongside existing

2. Create compatibility views

3. Migrate data in batches

4. Update application code incrementally

5. Deprecate old tables after validation

#

# Security Considerations

#

#

# Access Control Ready

- `visibility` field on artifacts for future ACL implementation

- `assigned_to` field prepared for user/role assignment

- Event tracking includes `actor_id` for accountability

#

#

# Data Integrity

- Foreign key constraints with appropriate CASCADE rules

- Unique constraints prevent duplicate dependencies

- Trigger-based timestamp management

#

# Future Extensibility

#

#

# Prepared for Advanced Features

1. **Multi-tenancy**: Add `tenant_id` to all tables

2. **Versioning**: `version` and `previous_version_id` in artifacts

3. **Workflow Engine**: `lifecycle_stage` supports state machines

4. **Analytics**: Event stream enables real-time metrics

5. **Search**: Indexed attributes support full-text search

#

#

# Plugin Architecture Support

- EAV pattern allows plugin-specific attributes

- Event system enables plugin hooks

- Template system supports custom task types

#

# Implementation Recommendations

#

#

# Phase 1: Core Schema

1. Deploy generic_tasks and dependencies

2. Implement basic CRUD operations

3. Validate performance with test data

#

#

# Phase 2: Migration Tools

1. Build data conversion utilities

2. Create compatibility layer

3. Test with production data samples

#

#

# Phase 3: Advanced Features

1. Implement template system

2. Enable event streaming

3. Add dependency auto-resolution

#

# Performance Benchmarks

#

#

# Expected Performance Characteristics

- Subtree queries: O(log n) with hierarchy_path index

- Dependency checks: O(1) with composite indexes

- Attribute lookups: O(1) for indexed attributes

- Event insertion: O(1) with minimal overhead

#

#

# Scalability Targets

- 1M+ tasks without performance degradation

- 10M+ events with efficient cleanup

- 100K+ concurrent dependency checks

- Sub-second template instantiation

#

# Conclusion

This database design provides a solid foundation for the next generation of the MCP Task Orchestrator. It balances flexibility with performance, ensures backward compatibility, and prepares for future enhancements while maintaining data integrity and operational efficiency.
