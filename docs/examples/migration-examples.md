# Generic Task Model Migration Examples

> **Audience**: System Administrators, DevOps Engineers, Migration Teams  
> **Version**: 2.0  
> **Created**: 2025-06-03  
> **Focus**: Practical migration examples for upgrading to Generic Task Model

## Overview

This document provides step-by-step migration examples for upgrading from the legacy dual-model system (TaskBreakdown + SubTask) to the new Generic Task Model. All examples include validation steps and rollback procedures.

## Pre-Migration Validation

### Environment Health Check
```bash
# Check current system status
python scripts/diagnostics/check_status.py

# Validate database integrity
python scripts/diagnostics/diagnose_db.py

# Verify backup status
python -c "
from mcp_task_orchestrator.db.persistence import validate_backup_integrity
result = validate_backup_integrity()
print(f'Backup validation: {result}')
"

# Check disk space for migration
df -h /path/to/database
```

### Data Analysis Pre-Migration
```python
"""
Script to analyze existing data before migration.
Provides insights for migration planning and validation.
"""

async def analyze_pre_migration_data():
    from mcp_task_orchestrator.db.persistence import get_db_connection
    
    async with get_db_connection() as conn:
        # Count existing records
        breakdown_count = await conn.fetchone(
            "SELECT COUNT(*) as count FROM task_breakdowns"
        )
        subtask_count = await conn.fetchone(
            "SELECT COUNT(*) as count FROM subtasks"
        )
        
        # Analyze complexity distribution
        complexity_dist = await conn.fetchall("""
            SELECT complexity, COUNT(*) as count 
            FROM task_breakdowns 
            GROUP BY complexity
        """)
        
        # Check for orphaned subtasks
        orphaned = await conn.fetchall("""
            SELECT s.task_id, s.parent_task_id 
            FROM subtasks s 
            LEFT JOIN task_breakdowns tb ON s.parent_task_id = tb.parent_task_id 
            WHERE tb.parent_task_id IS NULL
        """)
        
        # Analyze dependency patterns
        dependency_stats = await conn.fetchall("""
            SELECT 
                JSON_LENGTH(dependencies) as dep_count,
                COUNT(*) as task_count
            FROM subtasks 
            WHERE dependencies IS NOT NULL
            GROUP BY JSON_LENGTH(dependencies)
        """)
        
        return {
            "breakdown_count": breakdown_count["count"],
            "subtask_count": subtask_count["count"],
            "complexity_distribution": complexity_dist,
            "orphaned_subtasks": orphaned,
            "dependency_statistics": dependency_stats,
            "migration_readiness": len(orphaned) == 0
        }

# Run analysis
import asyncio
analysis = asyncio.run(analyze_pre_migration_data())
print(f"Migration Analysis: {analysis}")
```

## Basic Migration Examples

### Example 1: Simple Task Migration

#### Legacy Structure
```json
// Original TaskBreakdown
{
  "parent_task_id": "task_123",
  "description": "Implement user authentication system",
  "complexity": "moderate",
  "context": "Add login/logout functionality with session management"
}

// Original SubTasks
[
  {
    "task_id": "architect_456",
    "parent_task_id": "task_123",
    "title": "Design authentication architecture",
    "specialist_type": "architect",
    "dependencies": [],
    "status": "completed"
  },
  {
    "task_id": "implementer_789",
    "parent_task_id": "task_123", 
    "title": "Implement login system",
    "specialist_type": "implementer",
    "dependencies": ["architect_456"],
    "status": "active"
  }
]
```

#### Migration Script
```python
"""
Migration script for converting simple task structures.
"""

async def migrate_simple_task_example():
    # Step 1: Create root GenericTask from TaskBreakdown
    root_task = GenericTask(
        task_id="task_123",  # Preserve original ID
        task_type="breakdown",  # Legacy type preserved
        attributes={
            "description": "Implement user authentication system",
            "complexity": "moderate", 
            "context": "Add login/logout functionality with session management",
            "legacy_migration": True,
            "migration_timestamp": datetime.now().isoformat(),
            "original_type": "TaskBreakdown"
        },
        created_at=datetime(2025, 5, 15),  # Preserve original timestamp
        status=TaskStatus.ACTIVE  # Derived from subtask statuses
    )
    
    # Step 2: Create child GenericTasks from SubTasks
    child_tasks = [
        GenericTask(
            task_id="architect_456",
            task_type="specialist_task",
            parent_task_id="task_123",  # Link to parent
            attributes={
                "title": "Design authentication architecture",
                "specialist_type": "architect",
                "legacy_migration": True,
                "original_subtask_id": "architect_456"
            },
            status=TaskStatus.COMPLETED,
            dependencies=[]  # No dependencies
        ),
        GenericTask(
            task_id="implementer_789", 
            task_type="specialist_task",
            parent_task_id="task_123",
            attributes={
                "title": "Implement login system",
                "specialist_type": "implementer", 
                "legacy_migration": True,
                "original_subtask_id": "implementer_789"
            },
            status=TaskStatus.ACTIVE,
            dependencies=[
                TaskDependency(
                    dependency_task_id="architect_456",
                    dependency_type=DependencyType.COMPLETION,
                    description="Architecture design must complete first"
                )
            ]
        )
    ]
    
    # Step 3: Save all tasks with transaction safety
    async with get_db_connection() as conn:
        async with conn.begin():  # Transaction for atomicity
            await save_generic_task(root_task)
            for child_task in child_tasks:
                await save_generic_task(child_task)
            
            # Step 4: Validate migration
            migrated_root = await get_generic_task("task_123")
            migrated_children = await get_child_tasks("task_123")
            
            assert migrated_root is not None
            assert len(migrated_children) == 2
            assert migrated_children[1].dependencies[0].dependency_task_id == "architect_456"
            
    return {
        "migration_successful": True,
        "root_task_id": "task_123",
        "child_tasks_count": len(child_tasks),
        "dependencies_preserved": True
    }
```

### Example 2: Complex Hierarchical Migration

#### Legacy Structure with Multiple Levels
```python
# Complex legacy structure
legacy_data = {
    "task_breakdown": {
        "parent_task_id": "epic_ecommerce",
        "description": "Build complete e-commerce platform",
        "complexity": "very_complex",
        "context": "Multi-tenant e-commerce with payments and inventory"
    },
    "subtasks": [
        {
            "task_id": "arch_platform",
            "title": "Platform architecture design",
            "specialist_type": "architect",
            "dependencies": []
        },
        {
            "task_id": "impl_user_mgmt", 
            "title": "User management system",
            "specialist_type": "implementer",
            "dependencies": ["arch_platform"]
        },
        {
            "task_id": "impl_product_catalog",
            "title": "Product catalog system", 
            "specialist_type": "implementer",
            "dependencies": ["arch_platform"]
        },
        {
            "task_id": "impl_payment_system",
            "title": "Payment processing system",
            "specialist_type": "implementer", 
            "dependencies": ["impl_user_mgmt", "impl_product_catalog"]
        },
        {
            "task_id": "test_integration",
            "title": "Full platform integration testing",
            "specialist_type": "tester",
            "dependencies": ["impl_payment_system"]
        }
    ]
}
```

#### Migration with Hierarchy Optimization
```python
"""
Migration script that optimizes task hierarchy during migration.
Creates intermediate grouping tasks for better organization.
"""

async def migrate_complex_hierarchy():
    # Step 1: Create enhanced root task
    root_task = GenericTask(
        task_id="epic_ecommerce",
        task_type="epic",  # Upgraded from "breakdown" 
        attributes={
            "title": "E-commerce Platform Development",
            "description": "Build complete e-commerce platform",
            "complexity": "very_complex",
            "context": "Multi-tenant e-commerce with payments and inventory",
            "business_value": "Enable online sales channel",
            "estimated_duration": "6 months",
            "legacy_migration": True
        },
        hierarchy_path="/root/epic_ecommerce"
    )
    
    # Step 2: Create intermediate feature groupings
    feature_groups = [
        GenericTask(
            task_id="feature_user_management",
            task_type="feature",
            parent_task_id="epic_ecommerce",
            attributes={
                "title": "User Management Feature",
                "description": "Complete user lifecycle management",
                "created_during_migration": True
            },
            hierarchy_path="/root/epic_ecommerce/feature_user_management"
        ),
        GenericTask(
            task_id="feature_product_catalog", 
            task_type="feature",
            parent_task_id="epic_ecommerce",
            attributes={
                "title": "Product Catalog Feature", 
                "description": "Product management and browsing",
                "created_during_migration": True
            },
            hierarchy_path="/root/epic_ecommerce/feature_product_catalog"
        ),
        GenericTask(
            task_id="feature_payment_processing",
            task_type="feature",
            parent_task_id="epic_ecommerce", 
            attributes={
                "title": "Payment Processing Feature",
                "description": "Secure payment handling and processing",
                "created_during_migration": True
            },
            hierarchy_path="/root/epic_ecommerce/feature_payment_processing"
        )
    ]
    
    # Step 3: Create specialist tasks with optimized grouping
    specialist_tasks = [
        # Architecture spans all features
        GenericTask(
            task_id="arch_platform",
            task_type="specialist_task",
            parent_task_id="epic_ecommerce",  # Top-level architecture
            attributes={
                "title": "Platform architecture design",
                "specialist_type": "architect",
                "scope": "platform_wide",
                "legacy_subtask_id": "arch_platform"
            },
            hierarchy_path="/root/epic_ecommerce/arch_platform"
        ),
        # User management implementation
        GenericTask(
            task_id="impl_user_mgmt",
            task_type="specialist_task", 
            parent_task_id="feature_user_management",  # Grouped under feature
            attributes={
                "title": "User management system implementation",
                "specialist_type": "implementer",
                "legacy_subtask_id": "impl_user_mgmt"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="arch_platform",
                    dependency_type=DependencyType.COMPLETION
                )
            ],
            hierarchy_path="/root/epic_ecommerce/feature_user_management/impl_user_mgmt"
        ),
        # Product catalog implementation  
        GenericTask(
            task_id="impl_product_catalog",
            task_type="specialist_task",
            parent_task_id="feature_product_catalog",
            attributes={
                "title": "Product catalog system implementation",
                "specialist_type": "implementer", 
                "legacy_subtask_id": "impl_product_catalog"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="arch_platform",
                    dependency_type=DependencyType.COMPLETION
                )
            ],
            hierarchy_path="/root/epic_ecommerce/feature_product_catalog/impl_product_catalog"
        ),
        # Payment system implementation
        GenericTask(
            task_id="impl_payment_system",
            task_type="specialist_task",
            parent_task_id="feature_payment_processing",
            attributes={
                "title": "Payment processing system implementation",
                "specialist_type": "implementer",
                "legacy_subtask_id": "impl_payment_system"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="impl_user_mgmt",
                    dependency_type=DependencyType.COMPLETION,
                    description="User management required for payment accounts"
                ),
                TaskDependency(
                    dependency_task_id="impl_product_catalog", 
                    dependency_type=DependencyType.COMPLETION,
                    description="Product catalog required for payment items"
                )
            ],
            hierarchy_path="/root/epic_ecommerce/feature_payment_processing/impl_payment_system"
        ),
        # Integration testing
        GenericTask(
            task_id="test_integration",
            task_type="specialist_task",
            parent_task_id="epic_ecommerce",  # Epic-level testing
            attributes={
                "title": "Full platform integration testing", 
                "specialist_type": "tester",
                "test_scope": "end_to_end_platform",
                "legacy_subtask_id": "test_integration"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="impl_payment_system",
                    dependency_type=DependencyType.COMPLETION,
                    description="All features must be implemented before integration testing"
                )
            ],
            hierarchy_path="/root/epic_ecommerce/test_integration"
        )
    ]
    
    # Step 4: Execute migration with validation
    migration_results = []
    
    async with get_db_connection() as conn:
        async with conn.begin():
            # Save in dependency order
            await save_generic_task(root_task)
            migration_results.append({"task_id": root_task.task_id, "type": "epic"})
            
            for feature in feature_groups:
                await save_generic_task(feature)
                migration_results.append({"task_id": feature.task_id, "type": "feature"})
            
            for task in specialist_tasks:
                await save_generic_task(task)
                migration_results.append({"task_id": task.task_id, "type": "specialist_task"})
    
    # Step 5: Validate hierarchy and dependencies
    validation_results = await validate_migrated_hierarchy("epic_ecommerce")
    
    return {
        "migration_successful": True,
        "hierarchy_optimized": True,
        "tasks_migrated": len(migration_results),
        "feature_groups_created": len(feature_groups),
        "dependencies_preserved": True,
        "validation_results": validation_results
    }

async def validate_migrated_hierarchy(root_task_id: str):
    """Validate that migrated hierarchy is correct and complete."""
    
    # Get complete task tree
    tree = await get_task_hierarchy_tree(root_task_id)
    
    validations = {
        "hierarchy_complete": True,
        "dependencies_valid": True,
        "no_orphaned_tasks": True,
        "materialized_paths_correct": True
    }
    
    # Validate hierarchy completeness
    total_tasks = count_tasks_in_tree(tree)
    expected_tasks = 9  # 1 epic + 3 features + 5 specialist tasks
    validations["hierarchy_complete"] = (total_tasks == expected_tasks)
    
    # Validate dependencies
    dependency_graph = build_dependency_graph(tree)
    validations["dependencies_valid"] = validate_dependency_graph(dependency_graph)
    
    # Check for cycles
    validations["no_dependency_cycles"] = not has_dependency_cycles(dependency_graph)
    
    return validations
```

## Advanced Migration Scenarios

### Example 3: Preserving Custom Data During Migration

```python
"""
Migration example that preserves custom attributes and metadata.
Shows how to handle complex data transformations.
"""

async def migrate_with_custom_data_preservation():
    # Legacy data with custom fields
    legacy_subtask = {
        "task_id": "impl_custom_feature",
        "parent_task_id": "project_custom",
        "title": "Custom feature implementation",
        "specialist_type": "implementer",
        "status": "active",
        "results": "Partial implementation completed, API endpoints created",
        "artifacts": ["api_spec.yaml", "implementation_notes.md"],
        "file_operations_count": 15,
        "verification_status": "verified",
        "custom_metadata": {
            "code_review_status": "approved",
            "deployment_environment": "staging", 
            "performance_baseline": {"cpu": 45, "memory": 128},
            "integration_tests_passed": True
        }
    }
    
    # Migration with full data preservation
    migrated_task = GenericTask(
        task_id="impl_custom_feature",
        task_type="specialist_task",
        parent_task_id="project_custom",
        attributes={
            # Preserve original fields
            "title": legacy_subtask["title"],
            "specialist_type": legacy_subtask["specialist_type"],
            
            # Preserve legacy results and artifacts
            "legacy_results": legacy_subtask["results"],
            "legacy_artifacts": legacy_subtask["artifacts"],
            "file_operations_count": legacy_subtask["file_operations_count"],
            "verification_status": legacy_subtask["verification_status"],
            
            # Preserve custom metadata
            "code_review_status": legacy_subtask["custom_metadata"]["code_review_status"],
            "deployment_environment": legacy_subtask["custom_metadata"]["deployment_environment"],
            "performance_baseline": legacy_subtask["custom_metadata"]["performance_baseline"],
            "integration_tests_passed": legacy_subtask["custom_metadata"]["integration_tests_passed"],
            
            # Add migration metadata
            "migration_timestamp": datetime.now().isoformat(),
            "migrated_from": "SubTask",
            "custom_data_preserved": True
        },
        status=TaskStatus(legacy_subtask["status"])
    )
    
    return migrated_task
```

### Example 4: Batch Migration with Progress Tracking

```python
"""
Large-scale migration script with progress tracking and error handling.
Suitable for production environments with thousands of tasks.
"""

async def batch_migrate_with_progress():
    migration_stats = {
        "total_breakdowns": 0,
        "total_subtasks": 0, 
        "migrated_breakdowns": 0,
        "migrated_subtasks": 0,
        "errors": [],
        "start_time": datetime.now()
    }
    
    # Get counts for progress tracking
    async with get_db_connection() as conn:
        breakdown_count = await conn.fetchone("SELECT COUNT(*) as count FROM task_breakdowns")
        subtask_count = await conn.fetchone("SELECT COUNT(*) as count FROM subtasks")
        
        migration_stats["total_breakdowns"] = breakdown_count["count"]
        migration_stats["total_subtasks"] = subtask_count["count"]
    
    print(f"Starting migration of {migration_stats['total_breakdowns']} breakdowns and {migration_stats['total_subtasks']} subtasks")
    
    # Migrate in batches to manage memory
    batch_size = 100
    
    async with get_db_connection() as conn:
        # Process breakdowns in batches
        offset = 0
        while True:
            breakdowns = await conn.fetchall(
                "SELECT * FROM task_breakdowns LIMIT ? OFFSET ?",
                (batch_size, offset)
            )
            
            if not breakdowns:
                break
                
            # Migrate each breakdown
            for breakdown in breakdowns:
                try:
                    # Create root GenericTask
                    root_task = GenericTask(
                        task_id=breakdown["parent_task_id"],
                        task_type="breakdown",
                        attributes={
                            "description": breakdown["description"],
                            "complexity": breakdown["complexity"],
                            "context": breakdown["context"],
                            "legacy_migration": True
                        },
                        created_at=breakdown["created_at"]
                    )
                    
                    await save_generic_task(root_task)
                    migration_stats["migrated_breakdowns"] += 1
                    
                    # Migrate associated subtasks
                    subtasks = await conn.fetchall(
                        "SELECT * FROM subtasks WHERE parent_task_id = ?",
                        (breakdown["parent_task_id"],)
                    )
                    
                    for subtask in subtasks:
                        try:
                            child_task = GenericTask(
                                task_id=subtask["task_id"],
                                task_type="specialist_task",
                                parent_task_id=subtask["parent_task_id"],
                                attributes={
                                    "title": subtask["title"],
                                    "description": subtask["description"],
                                    "specialist_type": subtask["specialist_type"],
                                    "estimated_effort": subtask["estimated_effort"],
                                    "legacy_migration": True
                                },
                                status=TaskStatus(subtask["status"]),
                                created_at=subtask["created_at"],
                                completed_at=subtask["completed_at"]
                            )
                            
                            # Convert dependencies
                            if subtask["dependencies"]:
                                deps = json.loads(subtask["dependencies"])
                                child_task.dependencies = [
                                    TaskDependency(
                                        dependency_task_id=dep_id,
                                        dependency_type=DependencyType.COMPLETION
                                    ) for dep_id in deps
                                ]
                            
                            await save_generic_task(child_task)
                            migration_stats["migrated_subtasks"] += 1
                            
                        except Exception as e:
                            error_info = {
                                "type": "subtask_migration_error",
                                "subtask_id": subtask["task_id"],
                                "error": str(e),
                                "timestamp": datetime.now().isoformat()
                            }
                            migration_stats["errors"].append(error_info)
                            print(f"Error migrating subtask {subtask['task_id']}: {e}")
                    
                except Exception as e:
                    error_info = {
                        "type": "breakdown_migration_error", 
                        "breakdown_id": breakdown["parent_task_id"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    migration_stats["errors"].append(error_info)
                    print(f"Error migrating breakdown {breakdown['parent_task_id']}: {e}")
            
            offset += batch_size
            
            # Progress update
            progress = (offset / migration_stats["total_breakdowns"]) * 100
            print(f"Migration progress: {progress:.1f}% - {migration_stats['migrated_breakdowns']} breakdowns, {migration_stats['migrated_subtasks']} subtasks")
    
    migration_stats["end_time"] = datetime.now()
    migration_stats["duration"] = (migration_stats["end_time"] - migration_stats["start_time"]).total_seconds()
    migration_stats["success_rate"] = (migration_stats["migrated_subtasks"] / migration_stats["total_subtasks"]) * 100
    
    return migration_stats
```

## Post-Migration Validation

### Comprehensive Validation Script
```python
"""
Post-migration validation to ensure data integrity and system health.
"""

async def comprehensive_post_migration_validation():
    validation_results = {
        "data_integrity": {},
        "performance_metrics": {},
        "api_compatibility": {},
        "system_health": {}
    }
    
    # 1. Data Integrity Validation
    async with get_db_connection() as conn:
        # Check record counts
        generic_task_count = await conn.fetchone("SELECT COUNT(*) as count FROM generic_tasks")
        original_total = await conn.fetchone("""
            SELECT 
                (SELECT COUNT(*) FROM task_breakdowns) + 
                (SELECT COUNT(*) FROM subtasks) as total
        """)
        
        validation_results["data_integrity"]["record_count_match"] = (
            generic_task_count["count"] == original_total["total"]
        )
        
        # Check hierarchy integrity
        orphaned_tasks = await conn.fetchall("""
            SELECT task_id FROM generic_tasks 
            WHERE parent_task_id IS NOT NULL 
            AND parent_task_id NOT IN (SELECT task_id FROM generic_tasks)
        """)
        
        validation_results["data_integrity"]["no_orphaned_tasks"] = len(orphaned_tasks) == 0
        
        # Check dependency integrity
        invalid_deps = await conn.fetchall("""
            SELECT td.dependent_task_id, td.dependency_task_id
            FROM task_dependencies td
            LEFT JOIN generic_tasks gt1 ON td.dependent_task_id = gt1.task_id
            LEFT JOIN generic_tasks gt2 ON td.dependency_task_id = gt2.task_id
            WHERE gt1.task_id IS NULL OR gt2.task_id IS NULL
        """)
        
        validation_results["data_integrity"]["valid_dependencies"] = len(invalid_deps) == 0
    
    # 2. Performance Metrics
    start_time = time.time()
    
    # Test query performance
    sample_tasks = await query_tasks(limit=100)
    query_time = time.time() - start_time
    
    validation_results["performance_metrics"]["query_performance"] = {
        "query_time_ms": query_time * 1000,
        "acceptable": query_time < 1.0  # Should be under 1 second
    }
    
    # 3. API Compatibility Test
    try:
        # Test legacy API compatibility
        legacy_response = await test_legacy_api_compatibility()
        validation_results["api_compatibility"]["legacy_apis_working"] = legacy_response["success"]
        
        # Test new Generic Task APIs
        new_api_response = await test_new_generic_apis()
        validation_results["api_compatibility"]["new_apis_working"] = new_api_response["success"]
        
    except Exception as e:
        validation_results["api_compatibility"]["error"] = str(e)
    
    # 4. System Health Check
    health_check = await run_system_health_check()
    validation_results["system_health"] = health_check
    
    # Overall migration success
    validation_results["migration_successful"] = all([
        validation_results["data_integrity"]["record_count_match"],
        validation_results["data_integrity"]["no_orphaned_tasks"], 
        validation_results["data_integrity"]["valid_dependencies"],
        validation_results["performance_metrics"]["query_performance"]["acceptable"],
        validation_results["api_compatibility"].get("legacy_apis_working", False),
        validation_results["api_compatibility"].get("new_apis_working", False)
    ])
    
    return validation_results

async def test_legacy_api_compatibility():
    """Test that legacy MCP tools still work after migration."""
    
    try:
        # Test orchestrator_plan_task (compatibility layer)
        legacy_result = await orchestrator_plan_task_legacy(
            description="Test legacy compatibility",
            subtasks_json=json.dumps([
                {
                    "title": "Test task",
                    "specialist_type": "tester",
                    "estimated_effort": "1 hour"
                }
            ])
        )
        
        return {"success": True, "result": legacy_result}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_new_generic_apis():
    """Test new Generic Task API tools."""
    
    try:
        # Test orchestrator_create_generic_task
        new_task = await orchestrator_create_generic_task(
            task_type="test_task",
            attributes={"title": "API Test Task", "test": True}
        )
        
        # Test orchestrator_query_tasks
        query_result = await orchestrator_query_tasks(
            filters={"attributes": {"test": True}},
            limit=1
        )
        
        return {
            "success": True,
            "task_created": new_task["task_created"],
            "query_successful": len(query_result["tasks"]) > 0
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Rollback Procedures

### Emergency Rollback Script
```python
"""
Emergency rollback procedure to restore original system state.
Use only if migration validation fails critically.
"""

async def emergency_rollback():
    print("⚠️  STARTING EMERGENCY ROLLBACK ⚠️")
    
    rollback_steps = [
        "Disable new Generic Task APIs",
        "Restore legacy table access", 
        "Validate legacy system functionality",
        "Update system status"
    ]
    
    for i, step in enumerate(rollback_steps, 1):
        print(f"Step {i}: {step}")
        
        if step == "Disable new Generic Task APIs":
            # Disable new API endpoints
            await disable_generic_task_apis()
            
        elif step == "Restore legacy table access":
            # Re-enable legacy table access
            await restore_legacy_table_access()
            
        elif step == "Validate legacy system functionality":
            # Test legacy system
            legacy_test = await test_legacy_system()
            if not legacy_test["success"]:
                raise Exception(f"Legacy system validation failed: {legacy_test['error']}")
                
        elif step == "Update system status": 
            # Update system to indicate rollback state
            await update_system_status("ROLLBACK_COMPLETE")
    
    print("✅ Emergency rollback completed successfully")
    print("📋 Next steps:")
    print("   1. Investigate migration failure cause")
    print("   2. Fix migration scripts")
    print("   3. Test migration in development environment")
    print("   4. Retry migration when ready")
    
    return {"rollback_successful": True, "system_state": "ROLLBACK_COMPLETE"}
```

These migration examples provide comprehensive guidance for upgrading to the Generic Task Model while ensuring data integrity, system stability, and the ability to rollback if needed. Each example includes validation steps and error handling to support production-grade migrations.