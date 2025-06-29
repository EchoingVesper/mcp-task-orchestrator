"""
Helper Methods Module - Internal database operations for Generic Tasks

This module contains internal helper methods used by the repository for:
- Saving related entities (attributes, dependencies, artifacts, events)
- Loading related entities for tasks
- Database row operations
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ...orchestrator.generic_models import (
    GenericTask, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact,
    EventType, EventCategory
)
from .converters import (
    row_to_task, row_to_attribute, row_to_dependency, 
    row_to_artifact, row_to_event
)

logger = logging.getLogger(__name__)


async def save_attribute(session: AsyncSession, task_id: str, attr: TaskAttribute):
    """Save a task attribute."""
    stmt = text("""
        INSERT INTO task_attributes (
            task_id, attribute_name, attribute_value,
            attribute_type, attribute_category, is_indexed,
            created_at, updated_at
        ) VALUES (
            :task_id, :name, :value, :type, :category, :indexed,
            :created_at, :updated_at
        )
    """)
    
    await session.execute(stmt, {
        "task_id": task_id,
        "name": attr.attribute_name,
        "value": attr.attribute_value,
        "type": attr.attribute_type,
        "category": attr.attribute_category,
        "indexed": attr.is_indexed,
        "created_at": attr.created_at.isoformat(),
        "updated_at": attr.updated_at.isoformat()
    })


async def save_dependency(session: AsyncSession, dep: TaskDependency):
    """Save a task dependency."""
    stmt = text("""
        INSERT INTO task_dependencies (
            dependent_task_id, prerequisite_task_id, dependency_type,
            dependency_status, is_mandatory, auto_satisfy,
            satisfaction_criteria, output_artifact_ref, input_parameter_name,
            created_at
        ) VALUES (
            :dependent_id, :prerequisite_id, :dep_type, :status,
            :mandatory, :auto_satisfy, :criteria, :output_ref, :input_param,
            :created_at
        )
    """)
    
    await session.execute(stmt, {
        "dependent_id": dep.dependent_task_id,
        "prerequisite_id": dep.prerequisite_task_id,
        "dep_type": dep.dependency_type,
        "status": dep.dependency_status,
        "mandatory": dep.is_mandatory,
        "auto_satisfy": dep.auto_satisfy,
        "criteria": json.dumps(dep.satisfaction_criteria) if dep.satisfaction_criteria else None,
        "output_ref": dep.output_artifact_ref,
        "input_param": dep.input_parameter_name,
        "created_at": dep.created_at.isoformat()
    })


async def save_artifact(session: AsyncSession, artifact: TaskArtifact):
    """Save a task artifact."""
    stmt = text("""
        INSERT INTO task_artifacts (
            artifact_id, task_id, artifact_type, artifact_name,
            content, content_hash, file_reference, file_size,
            mime_type, encoding, is_primary, visibility,
            version, previous_version_id, created_at, updated_at
        ) VALUES (
            :artifact_id, :task_id, :type, :name,
            :content, :hash, :file_ref, :size,
            :mime, :encoding, :primary, :visibility,
            :version, :prev_version, :created_at, :updated_at
        )
    """)
    
    await session.execute(stmt, {
        "artifact_id": artifact.artifact_id,
        "task_id": artifact.task_id,
        "type": artifact.artifact_type,
        "name": artifact.artifact_name,
        "content": artifact.content,
        "hash": artifact.content_hash,
        "file_ref": artifact.file_reference,
        "size": artifact.file_size,
        "mime": artifact.mime_type,
        "encoding": artifact.encoding,
        "primary": artifact.is_primary,
        "visibility": artifact.visibility,
        "version": artifact.version,
        "prev_version": artifact.previous_version_id,
        "created_at": artifact.created_at.isoformat(),
        "updated_at": artifact.updated_at.isoformat()
    })


async def record_event(session: AsyncSession, task_id: str,
                      event_type: EventType, category: EventCategory,
                      triggered_by: str, data: Optional[Dict] = None):
    """Record a task event."""
    stmt = text("""
        INSERT INTO task_events (
            task_id, event_type, event_category,
            event_data, triggered_by, created_at
        ) VALUES (
            :task_id, :type, :category, :data, :triggered_by, :created_at
        )
    """)
    
    await session.execute(stmt, {
        "task_id": task_id,
        "type": event_type,
        "category": category,
        "data": json.dumps(data) if data else None,
        "triggered_by": triggered_by,
        "created_at": datetime.now().isoformat()
    })


async def load_attributes(session: AsyncSession, task_id: str) -> List[TaskAttribute]:
    """Load attributes for a task."""
    stmt = text("""
        SELECT * FROM task_attributes 
        WHERE task_id = :task_id
        ORDER BY attribute_name
    """)
    
    result = await session.execute(stmt, {"task_id": task_id})
    return [row_to_attribute(dict(row)) for row in result]


async def load_dependencies(session: AsyncSession, task_id: str) -> List[TaskDependency]:
    """Load dependencies for a task."""
    stmt = text("""
        SELECT * FROM task_dependencies 
        WHERE dependent_task_id = :task_id
        ORDER BY created_at
    """)
    
    result = await session.execute(stmt, {"task_id": task_id})
    return [row_to_dependency(dict(row)) for row in result]


async def load_artifacts(session: AsyncSession, task_id: str) -> List[TaskArtifact]:
    """Load artifacts for a task."""
    stmt = text("""
        SELECT * FROM task_artifacts 
        WHERE task_id = :task_id
        ORDER BY is_primary DESC, created_at
    """)
    
    result = await session.execute(stmt, {"task_id": task_id})
    return [row_to_artifact(dict(row)) for row in result]


async def load_events(session: AsyncSession, task_id: str) -> List[TaskEvent]:
    """Load events for a task."""
    stmt = text("""
        SELECT * FROM task_events 
        WHERE task_id = :task_id
        ORDER BY created_at DESC
        LIMIT 100
    """)
    
    result = await session.execute(stmt, {"task_id": task_id})
    return [row_to_event(dict(row)) for row in result]


async def load_children(repo_instance, session: AsyncSession, parent_id: str) -> List[GenericTask]:
    """Load child tasks.
    
    Note: This function needs the repo_instance to call load_attributes
    """
    stmt = text("""
        SELECT * FROM generic_tasks 
        WHERE parent_task_id = :parent_id 
        AND deleted_at IS NULL
        ORDER BY position_in_parent
    """)
    
    result = await session.execute(stmt, {"parent_id": parent_id})
    children = []
    
    for row in result:
        child = row_to_task(dict(row))
        # Load minimal data for children
        child.attributes = await load_attributes(session, child.task_id)
        children.append(child)
    
    return children