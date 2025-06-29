"""
CRUD Operations Module - Create, Read, Update, Delete operations for Generic Tasks

This module handles all basic CRUD operations for tasks, including:
- Creating new tasks with validation
- Reading tasks with optional relationship loading
- Updating existing tasks
- Soft and hard deletion of tasks
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from ...orchestrator.generic_models import GenericTask, EventType, EventCategory
from .converters import row_to_task

logger = logging.getLogger(__name__)


async def create_task(repo_instance, task: GenericTask) -> GenericTask:
    """Create a new task in the database.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task: The GenericTask to create
        
    Returns:
        The created task with any auto-generated fields
        
    Raises:
        IntegrityError: If task_id already exists
    """
    async with repo_instance.get_session() as session:
        try:
            # Convert to storage format
            task_data = task.to_dict_for_storage()
            
            # Execute insert
            stmt = text("""
                INSERT INTO generic_tasks (
                    task_id, parent_task_id, title, description, task_type,
                    hierarchy_path, hierarchy_level, position_in_parent,
                    status, lifecycle_stage, complexity, estimated_effort,
                    specialist_type, assigned_to, context, configuration,
                    results, summary, quality_gate_level, verification_status,
                    auto_maintenance_enabled, is_template, template_id,
                    created_at, updated_at, started_at, completed_at, due_date
                ) VALUES (
                    :task_id, :parent_task_id, :title, :description, :task_type,
                    :hierarchy_path, :hierarchy_level, :position_in_parent,
                    :status, :lifecycle_stage, :complexity, :estimated_effort,
                    :specialist_type, :assigned_to, :context, :configuration,
                    :results, :summary, :quality_gate_level, :verification_status,
                    :auto_maintenance_enabled, :is_template, :template_id,
                    :created_at, :updated_at, :started_at, :completed_at, :due_date
                )
            """)
            
            await session.execute(stmt, task_data)
            
            # Save related entities
            from .helpers import save_attribute, save_dependency, save_artifact, record_event
            
            # Save attributes
            for attr in task.attributes:
                await save_attribute(session, task.task_id, attr)
            
            # Save dependencies
            for dep in task.dependencies:
                await save_dependency(session, dep)
            
            # Save artifacts
            for artifact in task.artifacts:
                await save_artifact(session, artifact)
            
            # Record creation event
            await record_event(
                session, task.task_id, EventType.CREATED,
                EventCategory.LIFECYCLE, "system",
                {"task_type": task.task_type}
            )
            
            logger.info(f"Created task {task.task_id}")
            return task
            
        except IntegrityError as e:
            logger.error(f"Task {task.task_id} already exists: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating task {task.task_id}: {e}")
            raise


async def get_task(repo_instance, task_id: str, include_children: bool = False,
                  include_events: bool = False) -> Optional[GenericTask]:
    """Retrieve a task by ID.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task_id: The task ID to retrieve
        include_children: Whether to load child tasks
        include_events: Whether to load task events
        
    Returns:
        The task if found, None otherwise
    """
    async with repo_instance.get_session() as session:
        # Build base query
        stmt = text("""
            SELECT * FROM generic_tasks 
            WHERE task_id = :task_id AND deleted_at IS NULL
        """)
        
        result = await session.execute(stmt, {"task_id": task_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # Convert to GenericTask
        task = row_to_task(dict(row))
        
        # Load related entities
        from .helpers import load_attributes, load_dependencies, load_artifacts, load_events, load_children
        
        # Load attributes
        task.attributes = await load_attributes(session, task_id)
        
        # Load dependencies
        task.dependencies = await load_dependencies(session, task_id)
        
        # Load artifacts
        task.artifacts = await load_artifacts(session, task_id)
        
        # Load children if requested
        if include_children:
            task.children = await load_children(repo_instance, session, task_id)
        
        # Load events if requested
        if include_events:
            task.events = await load_events(session, task_id)
        
        return task


async def update_task(repo_instance, task: GenericTask) -> GenericTask:
    """Update an existing task.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task: The task with updated values
        
    Returns:
        The updated task
    """
    async with repo_instance.get_session() as session:
        # Check if task exists
        check_stmt = text("SELECT 1 FROM generic_tasks WHERE task_id = :task_id")
        result = await session.execute(check_stmt, {"task_id": task.task_id})
        
        if not result.fetchone():
            raise ValueError(f"Task {task.task_id} not found")
        
        # Update main task
        task_data = task.to_dict_for_storage()
        task_data['updated_at'] = datetime.now().isoformat()
        
        update_stmt = text("""
            UPDATE generic_tasks SET
                title = :title,
                description = :description,
                task_type = :task_type,
                status = :status,
                lifecycle_stage = :lifecycle_stage,
                complexity = :complexity,
                estimated_effort = :estimated_effort,
                actual_effort = :actual_effort,
                specialist_type = :specialist_type,
                assigned_to = :assigned_to,
                context = :context,
                configuration = :configuration,
                results = :results,
                summary = :summary,
                quality_gate_level = :quality_gate_level,
                verification_status = :verification_status,
                updated_at = :updated_at,
                started_at = :started_at,
                completed_at = :completed_at,
                due_date = :due_date
            WHERE task_id = :task_id
        """)
        
        await session.execute(update_stmt, task_data)
        
        # Update attributes (delete and recreate for simplicity)
        from .helpers import save_attribute, record_event
        
        await session.execute(
            text("DELETE FROM task_attributes WHERE task_id = :task_id"),
            {"task_id": task.task_id}
        )
        for attr in task.attributes:
            await save_attribute(session, task.task_id, attr)
        
        # Record update event
        await record_event(
            session, task.task_id, EventType.UPDATED,
            EventCategory.DATA, "system"
        )
        
        logger.info(f"Updated task {task.task_id}")
        return task


async def delete_task(repo_instance, task_id: str, hard_delete: bool = False) -> bool:
    """Delete a task (soft delete by default).
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task_id: The task ID to delete
        hard_delete: If True, permanently delete from database
        
    Returns:
        True if deleted, False if not found
    """
    async with repo_instance.get_session() as session:
        if hard_delete:
            # Cascading delete
            stmt = text("DELETE FROM generic_tasks WHERE task_id = :task_id")
            result = await session.execute(stmt, {"task_id": task_id})
        else:
            # Soft delete
            stmt = text("""
                UPDATE generic_tasks 
                SET deleted_at = :deleted_at, updated_at = :updated_at
                WHERE task_id = :task_id AND deleted_at IS NULL
            """)
            now = datetime.now().isoformat()
            result = await session.execute(stmt, {
                "task_id": task_id,
                "deleted_at": now,
                "updated_at": now
            })
        
        if result.rowcount > 0:
            from .helpers import record_event
            await record_event(
                session, task_id, EventType.DELETED,
                EventCategory.LIFECYCLE, "system",
                {"hard_delete": hard_delete}
            )
            logger.info(f"Deleted task {task_id} (hard={hard_delete})")
            return True
        
        return False