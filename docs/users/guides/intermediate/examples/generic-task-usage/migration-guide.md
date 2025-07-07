

# Migration Guide

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > Migration Guide

#

# Overview

This guide helps you migrate from the legacy TaskBreakdown/SubTask system to the new Generic Task Model (v2.0). The migration preserves all existing data while providing enhanced flexibility and functionality.

#

# Migration Strategy

#

## 1. Preparation Phase

#

### Backup Existing Data

```bash

# Create backup of current database

python scripts/maintenance/backup_database.py --output backup_pre_migration.sql

# Export task data to JSON for safety

python scripts/maintenance/export_tasks.py --format json --output tasks_backup.json

```text

#

### Analyze Current Task Structure

```text
python
async def analyze_current_tasks():
    """Analyze existing task structure before migration."""
    
    

# Get all task breakdowns

    breakdowns = await get_all_task_breakdowns()
    
    analysis = {
        "total_breakdowns": len(breakdowns),
        "total_subtasks": 0,
        "complexity_distribution": {},
        "specialist_type_distribution": {},
        "dependency_patterns": []
    }
    
    for breakdown in breakdowns:
        subtasks = await get_subtasks_for_breakdown(breakdown.parent_task_id)
        analysis["total_subtasks"] += len(subtasks)
        
        

# Analyze complexity

        complexity = breakdown.complexity
        analysis["complexity_distribution"][complexity] = analysis["complexity_distribution"].get(complexity, 0) + 1
        
        

# Analyze specialist types

        for subtask in subtasks:
            specialist_type = subtask.specialist_type
            analysis["specialist_type_distribution"][specialist_type] = analysis["specialist_type_distribution"].get(specialist_type, 0) + 1
    
    return analysis

```text

#

## 2. Migration Execution

#

### Automated Migration Script

```text
python
"""
Automated migration script for converting legacy tasks to Generic Task Model.
"""

async def migrate_legacy_tasks_to_generic():
    """Convert existing TaskBreakdown and SubTask records to GenericTask model."""
    
    migration_log = {
        "start_time": datetime.utcnow(),
        "migrated_tasks": [],
        "failed_migrations": [],
        "summary": {}
    }
    
    try:
        

# Get all existing task breakdowns

        legacy_breakdowns = await get_all_legacy_task_breakdowns()
        
        for breakdown in legacy_breakdowns:
            try:
                

# Convert TaskBreakdown to root GenericTask

                root_task = GenericTask(
                    task_id=breakdown.parent_task_id,
                    task_type="breakdown",  

# Preserve legacy type

                    attributes={
                        "title": f"Task Breakdown: {breakdown.description[:50]}...",
                        "description": breakdown.description,
                        "complexity": breakdown.complexity,
                        "context": breakdown.context,
                        "legacy_migration": True,
                        "original_breakdown_id": breakdown.parent_task_id,
                        "migration_timestamp": datetime.utcnow().isoformat()
                    },
                    status=TaskStatus.ACTIVE,  

# Assume active for existing breakdowns

                    created_at=breakdown.created_at
                )
                
                

# Save root task

                await save_generic_task(root_task)
                migration_log["migrated_tasks"].append({
                    "type": "breakdown",
                    "original_id": breakdown.parent_task_id,
                    "new_id": root_task.task_id
                })
                
                

# Get and convert all subtasks for this breakdown

                legacy_subtasks = await get_subtasks_for_breakdown(breakdown.parent_task_id)
                
                for subtask in legacy_subtasks:
                    

# Convert SubTask to child GenericTask

                    child_task = GenericTask(
                        task_id=subtask.task_id,
                        task_type="specialist_task",  

# Convert to standard type

                        parent_task_id=breakdown.parent_task_id,  

# Link to parent

                        attributes={
                            "title": subtask.title,
                            "description": subtask.description,
                            "specialist_type": subtask.specialist_type,
                            "estimated_effort": subtask.estimated_effort,
                            "legacy_migration": True,
                            "legacy_subtask_id": subtask.task_id,
                            "original_status": subtask.status,
                            "migration_timestamp": datetime.utcnow().isoformat()
                        },
                        status=TaskStatus(subtask.status),
                        created_at=subtask.created_at,
                        updated_at=subtask.completed_at or subtask.created_at
                    )
                    
                    

# Convert legacy dependencies

                    if subtask.dependencies:
                        child_task.dependencies = [
                            TaskDependency(
                                dependency_task_id=dep_id,
                                dependency_type=DependencyType.COMPLETION,  

# Default to completion

                                description=f"Legacy dependency on {dep_id}"
                            ) for dep_id in subtask.dependencies
                        ]
                    
                    

# Preserve legacy results and artifacts

                    if subtask.results:
                        child_task.attributes["legacy_results"] = subtask.results
                    if subtask.artifacts:
                        child_task.attributes["legacy_artifacts"] = subtask.artifacts
                    if subtask.file_operations_count:
                        child_task.attributes["file_operations_count"] = subtask.file_operations_count
                    if subtask.verification_status:
                        child_task.attributes["verification_status"] = subtask.verification_status
                    
                    

# Save child task

                    await save_generic_task(child_task)
                    migration_log["migrated_tasks"].append({
                        "type": "subtask",
                        "original_id": subtask.task_id,
                        "new_id": child_task.task_id,
                        "parent_id": breakdown.parent_task_id
                    })
                
            except Exception as e:
                migration_log["failed_migrations"].append({
                    "breakdown_id": breakdown.parent_task_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        

# Generate migration summary

        migration_log["end_time"] = datetime.utcnow()
        migration_log["summary"] = {
            "total_breakdowns_processed": len(legacy_breakdowns),
            "successful_migrations": len([m for m in migration_log["migrated_tasks"] if m["type"] == "breakdown"]),
            "failed_migrations": len(migration_log["failed_migrations"]),
            "total_tasks_migrated": len(migration_log["migrated_tasks"]),
            "migration_duration": (migration_log["end_time"] - migration_log["start_time"]).total_seconds()
        }
        
        return migration_log
        
    except Exception as e:
        migration_log["fatal_error"] = str(e)
        migration_log["end_time"] = datetime.utcnow()
        return migration_log

```text

#

## 3. Post-Migration Validation

#

### Data Integrity Verification

```text
python
async def validate_migration_integrity():
    """Validate that migration preserved all data correctly."""
    
    validation_results = {
        "data_integrity": {},
        "functionality_tests": {},
        "performance_benchmarks": {}
    }
    
    

# 1. Count validation

    legacy_breakdown_count = await count_legacy_breakdowns()
    legacy_subtask_count = await count_legacy_subtasks()
    
    migrated_breakdown_count = await count_generic_tasks({"task_type": "breakdown"})
    migrated_subtask_count = await count_generic_tasks({"task_type": "specialist_task"})
    
    validation_results["data_integrity"]["count_match"] = {
        "breakdowns": legacy_breakdown_count == migrated_breakdown_count,
        "subtasks": legacy_subtask_count == migrated_subtask_count
    }
    
    

# 2. Sample data validation

    sample_breakdowns = await get_sample_legacy_breakdowns(5)
    for breakdown in sample_breakdowns:
        migrated_task = await get_generic_task(breakdown.parent_task_id)
        
        

# Validate key attributes preserved

        attributes_match = (
            migrated_task.attributes["description"] == breakdown.description and
            migrated_task.attributes["complexity"] == breakdown.complexity
        )
        
        validation_results["data_integrity"][f"breakdown_{breakdown.parent_task_id}"] = {
            "found": migrated_task is not None,
            "attributes_preserved": attributes_match
        }
    
    

# 3. Dependency validation

    dependency_validation = await validate_dependency_migration()
    validation_results["data_integrity"]["dependencies"] = dependency_validation
    
    

# 4. Functionality tests

    functionality_tests = await run_post_migration_functionality_tests()
    validation_results["functionality_tests"] = functionality_tests
    
    return validation_results

```text

#

### Performance Comparison

```text
python
async def compare_pre_post_migration_performance():
    """Compare system performance before and after migration."""
    
    performance_metrics = {}
    
    

# Query performance

    start_time = time.time()
    tasks = await query_generic_tasks({"limit": 100})
    query_time = time.time() - start_time
    performance_metrics["query_time_100_tasks"] = query_time
    
    

# Hierarchy loading performance

    start_time = time.time()
    sample_root_tasks = await get_sample_root_tasks(5)
    for root_task in sample_root_tasks:
        hierarchy = await get_task_hierarchy(root_task.task_id)
    hierarchy_time = time.time() - start_time
    performance_metrics["hierarchy_loading_time"] = hierarchy_time
    
    

# Task creation performance

    start_time = time.time()
    test_task = GenericTask(
        task_id="performance_test_task",
        task_type="test",
        attributes={"title": "Performance Test"}
    )
    await save_generic_task(test_task)
    await delete_generic_task("performance_test_task")
    creation_time = time.time() - start_time
    performance_metrics["task_creation_time"] = creation_time
    
    return performance_metrics

```text

#

## 4. Legacy System Cleanup

#

### Safe Legacy Data Archival

```text
python
async def archive_legacy_data():
    """Safely archive legacy data after successful migration."""
    
    archive_results = {
        "archived_tables": [],
        "backup_locations": [],
        "cleanup_summary": {}
    }
    
    

# Create archive tables

    archive_tables = [
        ("task_breakdowns", "task_breakdowns_legacy_archive"),
        ("subtasks", "subtasks_legacy_archive"),
        ("lock_tracking", "lock_tracking_legacy_archive")
    ]
    
    for source_table, archive_table in archive_tables:
        try:
            

# Create archive table with timestamp

            archive_table_name = f"{archive_table}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            

# Copy data to archive table

            await create_archive_table(source_table, archive_table_name)
            
            

# Verify archive data integrity

            source_count = await count_table_rows(source_table)
            archive_count = await count_table_rows(archive_table_name)
            
            if source_count == archive_count:
                archive_results["archived_tables"].append({
                    "source": source_table,
                    "archive": archive_table_name,
                    "row_count": source_count,
                    "status": "success"
                })
            else:
                raise ValueError(f"Row count mismatch: {source_count} vs {archive_count}")
                
        except Exception as e:
            archive_results["archived_tables"].append({
                "source": source_table,
                "status": "failed",
                "error": str(e)
            })
    
    return archive_results

```text

#

## 5. Code Migration

#

### Update Application Code

```text
python

# Before migration (legacy code)

async def legacy_create_task_breakdown(description: str, complexity: str):
    breakdown = TaskBreakdownModel(
        parent_task_id=generate_id(),
        description=description,
        complexity=complexity
    )
    await save_task_breakdown(breakdown)
    return breakdown

# After migration (new code)

async def create_epic_task(title: str, description: str, complexity: str):
    epic_task = GenericTask(
        task_id=generate_id(),
        task_type="epic",  

# Use appropriate task type

        attributes={
            "title": title,
            "description": description,
            "complexity": complexity
        }
    )
    await save_generic_task(epic_task)
    return epic_task

```text

#

### Update API Calls

```text
python

# Before migration

result = await mcp_call("orchestrator_plan_task", {
    "description": "Implement user authentication",
    "complexity": "moderate"
})

# After migration

result = await mcp_call("orchestrator_create_generic_task", {
    "task_type": "epic",
    "attributes": {
        "title": "User Authentication System",
        "description": "Implement user authentication",
        "complexity": "moderate"
    }
})

```text

#

## 6. Migration Rollback Plan

#

### Emergency Rollback Procedure

```text
python
async def emergency_rollback_migration():
    """Emergency rollback procedure if migration fails."""
    
    rollback_steps = []
    
    try:
        

# Step 1: Stop all task operations

        await pause_task_operations()
        rollback_steps.append("Task operations paused")
        
        

# Step 2: Backup current state

        await backup_current_database("rollback_backup.sql")
        rollback_steps.append("Current state backed up")
        
        

# Step 3: Restore from pre-migration backup

        await restore_database_from_backup("backup_pre_migration.sql")
        rollback_steps.append("Database restored from pre-migration backup")
        
        

# Step 4: Restart legacy services

        await restart_legacy_task_services()
        rollback_steps.append("Legacy services restarted")
        
        

# Step 5: Validate legacy system functionality

        validation_results = await validate_legacy_system()
        rollback_steps.append(f"Legacy system validation: {validation_results}")
        
        return {
            "status": "success",
            "rollback_steps": rollback_steps,
            "rollback_time": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "completed_steps": rollback_steps,
            "rollback_time": datetime.utcnow().isoformat()
        }
```text

#

# Migration Checklist

#

## Pre-Migration

- [ ] Create complete database backup

- [ ] Export task data to JSON format

- [ ] Analyze current task structure and patterns

- [ ] Test migration script on copy of production data

- [ ] Prepare rollback procedures

- [ ] Schedule maintenance window

- [ ] Notify all users of migration timeline

#

## During Migration

- [ ] Execute migration script

- [ ] Monitor migration progress

- [ ] Validate data integrity during migration

- [ ] Check for any errors or failures

- [ ] Verify system performance

#

## Post-Migration

- [ ] Run comprehensive validation tests

- [ ] Compare performance metrics

- [ ] Test all major functionality

- [ ] Validate API responses

- [ ] Check user interface functionality

- [ ] Archive legacy data safely

- [ ] Update documentation

- [ ] Train users on new features

- [ ] Monitor system for 48 hours

#

## Rollback Criteria

Execute rollback if any of the following occur:

- Data loss detected

- Critical functionality broken

- Performance degradation > 50%

- Migration taking longer than planned window

- Validation tests failing

- User-reported critical issues

#

# Post-Migration Benefits

#

## Enhanced Functionality

- Flexible attribute system for custom metadata

- Hierarchical task structure with unlimited depth

- Rich dependency relationships

- Template-based task creation

- Improved query capabilities

#

## Better Performance

- Optimized database schema

- Efficient hierarchy queries

- Batch operations support

- Caching improvements

#

## Developer Experience

- Unified API for all task operations

- Better error handling and validation

- Comprehensive documentation

- Enhanced debugging tools

---

**Related Documentation**:

- **Previous**: [API Quick Reference](../../../../referenceapi-reference.md)

- **Back to**: [Getting Started](getting-started.md)

- **See also**: [Troubleshooting](troubleshooting.md)
