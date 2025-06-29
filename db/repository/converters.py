"""
Converters Module - Database row to model conversion utilities

This module provides conversion functions to transform database rows
into domain model objects, handling:
- Task model conversion
- Attribute conversion with type handling
- Dependency relationship mapping
- Artifact and event conversion
- Template conversion
"""

import json
from datetime import datetime
from typing import Dict

from ...orchestrator.generic_models import (
    GenericTask, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact,
    TaskTemplate, TemplateParameter,
    TaskType, TaskStatus, LifecycleStage, DependencyType, DependencyStatus,
    EventType, EventCategory, AttributeType, ArtifactType
)


def row_to_task(row: Dict) -> GenericTask:
    """Convert database row to GenericTask."""
    # Parse JSON fields
    context = json.loads(row['context']) if row['context'] else {}
    config = json.loads(row['configuration']) if row['configuration'] else {}
    
    return GenericTask(
        task_id=row['task_id'],
        parent_task_id=row['parent_task_id'],
        title=row['title'],
        description=row['description'],
        task_type=TaskType(row['task_type']),
        hierarchy_path=row['hierarchy_path'],
        hierarchy_level=row['hierarchy_level'],
        position_in_parent=row['position_in_parent'],
        status=TaskStatus(row['status']),
        lifecycle_stage=LifecycleStage(row['lifecycle_stage']),
        complexity=row['complexity'],
        estimated_effort=row['estimated_effort'],
        actual_effort=row['actual_effort'],
        specialist_type=row['specialist_type'],
        assigned_to=row['assigned_to'],
        context=context,
        configuration=config,
        results=row['results'],
        summary=row['summary'],
        quality_gate_level=row['quality_gate_level'],
        verification_status=row['verification_status'],
        auto_maintenance_enabled=row['auto_maintenance_enabled'],
        is_template=row['is_template'],
        template_id=row['template_id'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
        completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
        due_date=datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
        deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
    )


def row_to_attribute(row: Dict) -> TaskAttribute:
    """Convert database row to TaskAttribute."""
    return TaskAttribute(
        attribute_name=row['attribute_name'],
        attribute_value=row['attribute_value'],
        attribute_type=AttributeType(row['attribute_type']),
        attribute_category=row['attribute_category'],
        is_indexed=row['is_indexed'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at'])
    )


def row_to_dependency(row: Dict) -> TaskDependency:
    """Convert database row to TaskDependency."""
    return TaskDependency(
        dependency_id=row.get('dependency_id'),
        dependent_task_id=row['dependent_task_id'],
        prerequisite_task_id=row['prerequisite_task_id'],
        dependency_type=DependencyType(row['dependency_type']),
        dependency_status=DependencyStatus(row['dependency_status']),
        is_mandatory=row['is_mandatory'],
        auto_satisfy=row['auto_satisfy'],
        satisfaction_criteria=json.loads(row['satisfaction_criteria']) if row['satisfaction_criteria'] else None,
        output_artifact_ref=row['output_artifact_ref'],
        input_parameter_name=row['input_parameter_name'],
        waived_at=datetime.fromisoformat(row['waived_at']) if row.get('waived_at') else None,
        waived_by=row.get('waived_by'),
        waiver_reason=row.get('waiver_reason'),
        created_at=datetime.fromisoformat(row['created_at']),
        satisfied_at=datetime.fromisoformat(row['satisfied_at']) if row.get('satisfied_at') else None
    )


def row_to_artifact(row: Dict) -> TaskArtifact:
    """Convert database row to TaskArtifact."""
    return TaskArtifact(
        artifact_id=row['artifact_id'],
        task_id=row['task_id'],
        artifact_type=ArtifactType(row['artifact_type']),
        artifact_name=row['artifact_name'],
        content=row['content'],
        content_hash=row['content_hash'],
        file_reference=row['file_reference'],
        file_size=row['file_size'],
        mime_type=row['mime_type'],
        encoding=row['encoding'],
        is_primary=row['is_primary'],
        visibility=row['visibility'],
        version=row['version'],
        previous_version_id=row['previous_version_id'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at'])
    )


def row_to_event(row: Dict) -> TaskEvent:
    """Convert database row to TaskEvent."""
    return TaskEvent(
        event_id=row.get('event_id'),
        task_id=row['task_id'],
        event_type=EventType(row['event_type']),
        event_category=EventCategory(row['event_category']),
        event_data=json.loads(row['event_data']) if row['event_data'] else {},
        previous_value=row.get('previous_value'),
        new_value=row.get('new_value'),
        triggered_by=row['triggered_by'],
        actor_id=row.get('actor_id'),
        session_id=row.get('session_id'),
        created_at=datetime.fromisoformat(row['created_at'])
    )


def row_to_template(row: Dict) -> TaskTemplate:
    """Convert database row to TaskTemplate."""
    # Parse parameters
    params = []
    if row['template_schema']:
        param_dicts = json.loads(row['template_schema'])
        for p in param_dicts:
            params.append(TemplateParameter(**p))
    
    return TaskTemplate(
        template_id=row['template_id'],
        template_name=row['template_name'],
        template_category=row['template_category'],
        template_version=row['template_version'],
        description=row['description'],
        parameters=params,
        task_structure=json.loads(row['task_structure']),
        is_active=row['is_active'],
        is_public=row['is_public'],
        created_by=row['created_by'],
        tags=json.loads(row['tags']) if row['tags'] else [],
        usage_count=row['usage_count'],
        last_used_at=datetime.fromisoformat(row['last_used_at']) if row['last_used_at'] else None,
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        deprecated_at=datetime.fromisoformat(row['deprecated_at']) if row['deprecated_at'] else None
    )