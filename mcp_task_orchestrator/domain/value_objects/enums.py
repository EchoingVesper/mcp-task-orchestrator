"""
Domain enums for the MCP Task Orchestrator.

This module contains all enum definitions extracted from generic_models.py
to improve modularity and reduce file size.
"""

from enum import Enum


class TaskType(str, Enum):
    """Types of tasks in the system."""
    STANDARD = "standard"
    BREAKDOWN = "breakdown"  # Root task that breaks down into subtasks
    MILESTONE = "milestone"
    REVIEW = "review"
    APPROVAL = "approval"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Current status of a task."""
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class LifecycleStage(str, Enum):
    """Lifecycle stage of a task."""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    ACTIVE = "active"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class DependencyType(str, Enum):
    """Types of dependencies between tasks."""
    COMPLETION = "completion"  # Task B starts after Task A completes
    DATA = "data"  # Task B needs output from Task A
    APPROVAL = "approval"  # Task B needs approval from Task A
    PREREQUISITE = "prerequisite"  # Task B requires Task A to exist
    BLOCKS = "blocks"  # Task A blocks Task B
    RELATED = "related"  # Informational relationship


class DependencyStatus(str, Enum):
    """Status of a dependency."""
    PENDING = "pending"
    SATISFIED = "satisfied"
    FAILED = "failed"
    WAIVED = "waived"
    CHECKING = "checking"


class QualityGateLevel(str, Enum):
    """Quality gate levels for task validation."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class EventType(str, Enum):
    """Types of task events."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    LIFECYCLE_CHANGED = "lifecycle_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNBLOCKED = "unblocked"
    ARCHIVED = "archived"
    DELETED = "deleted"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_SATISFIED = "dependency_satisfied"
    ATTRIBUTE_CHANGED = "attribute_changed"
    ARTIFACT_ADDED = "artifact_added"
    COMMENT_ADDED = "comment_added"
    MIGRATED = "migrated"


class EventCategory(str, Enum):
    """Categories of events."""
    LIFECYCLE = "lifecycle"
    DATA = "data"
    SYSTEM = "system"
    USER = "user"
    AUTOMATION = "automation"


class AttributeType(str, Enum):
    """Types for extensible attributes."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    JSON = "json"
    REFERENCE = "reference"  # Reference to another entity


class ArtifactType(str, Enum):
    """Types of artifacts."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    DESIGN = "design"
    TEST = "test"
    CONFIG = "config"
    DATA = "data"
    GENERAL = "general"