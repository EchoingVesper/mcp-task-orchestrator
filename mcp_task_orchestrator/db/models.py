"""
SQLAlchemy Base Model for Task Orchestrator.

This module provides compatibility layers for legacy code during the clean architecture migration.
All legacy SQLAlchemy models are replaced with placeholder classes to allow imports to succeed
while the codebase transitions to clean architecture with domain entities and repositories.
"""

from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Create the declarative base for all models
Base = declarative_base()

# Compatibility layer for legacy model imports during refactoring
# TODO: Replace all usage with clean architecture domain entities and use cases

class TaskStatus(Enum):
    """Placeholder task status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskBreakdownModel:
    """Placeholder for legacy TaskBreakdownModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.status = kwargs.get('status', TaskStatus.PENDING)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

class SubTaskModel:
    """Placeholder for legacy SubTaskModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.parent_id = kwargs.get('parent_id')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.status = kwargs.get('status', TaskStatus.PENDING)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

class MaintenanceOperationModel:
    """Placeholder for legacy MaintenanceOperationModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.operation_type = kwargs.get('operation_type', '')
        self.status = kwargs.get('status', 'pending')
        self.created_at = kwargs.get('created_at', datetime.now())

class TaskLifecycleModel:
    """Placeholder for legacy TaskLifecycleModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.stage = kwargs.get('stage', '')
        self.timestamp = kwargs.get('timestamp', datetime.now())

class StaleTaskTrackingModel:
    """Placeholder for legacy StaleTaskTrackingModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.detected_at = kwargs.get('detected_at', datetime.now())
        self.reason = kwargs.get('reason', '')

class TaskArchiveModel:
    """Placeholder for legacy TaskArchiveModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.archived_at = kwargs.get('archived_at', datetime.now())
        self.archive_reason = kwargs.get('archive_reason', '')

class LockTrackingModel:
    """Placeholder for legacy LockTrackingModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.resource_id = kwargs.get('resource_id')
        self.locked_at = kwargs.get('locked_at', datetime.now())
        self.lock_type = kwargs.get('lock_type', '')

class TaskEventModel:
    """Placeholder for legacy TaskEventModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.event_type = kwargs.get('event_type', '')
        self.timestamp = kwargs.get('timestamp', datetime.now())

class TaskAttributeModel:
    """Placeholder for legacy TaskAttributeModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.attribute_name = kwargs.get('attribute_name', '')
        self.attribute_value = kwargs.get('attribute_value', '')

class TaskPrerequisiteModel:
    """Placeholder for legacy TaskPrerequisiteModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.task_id = kwargs.get('task_id')
        self.prerequisite_id = kwargs.get('prerequisite_id')

class ProjectHealthMetricModel:
    """Placeholder for legacy ProjectHealthMetricModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.metric_name = kwargs.get('metric_name', '')
        self.metric_value = kwargs.get('metric_value', 0)
        self.recorded_at = kwargs.get('recorded_at', datetime.now())

class ArchitecturalDecisionModel:
    """Placeholder for legacy ArchitecturalDecisionModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.decision_title = kwargs.get('decision_title', '')
        self.decision_content = kwargs.get('decision_content', '')
        self.created_at = kwargs.get('created_at', datetime.now())

class DecisionEvolutionModel:
    """Placeholder for legacy DecisionEvolutionModel during clean architecture migration"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.decision_id = kwargs.get('decision_id')
        self.evolution_type = kwargs.get('evolution_type', '')
        self.timestamp = kwargs.get('timestamp', datetime.now())