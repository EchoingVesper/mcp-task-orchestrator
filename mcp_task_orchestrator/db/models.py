"""
SQLAlchemy models for the database-backed persistence mechanism.

This module defines the SQLAlchemy ORM models that map directly to the
task orchestrator's domain models for persistent storage in a database.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON, Integer, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class TaskBreakdownModel(Base):
    """SQLAlchemy model for task breakdowns."""
    
    __tablename__ = 'task_breakdowns'
    
    parent_task_id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    complexity = Column(String, nullable=False)
    context = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Workspace paradigm support
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=True)
    
    # Relationship to subtasks (one-to-many)
    subtasks = relationship("SubTaskModel", back_populates="parent_task", cascade="all, delete-orphan")
    # Relationship to workspace (many-to-one)
    workspace = relationship("WorkspaceModel", back_populates="task_breakdowns")


class SubTaskModel(Base):
    """SQLAlchemy model for subtasks."""
    
    __tablename__ = 'subtasks'
    
    task_id = Column(String, primary_key=True)
    parent_task_id = Column(String, ForeignKey('task_breakdowns.parent_task_id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    specialist_type = Column(String, nullable=False)
    dependencies = Column(JSON, default=list)
    estimated_effort = Column(String, nullable=False)
    status = Column(String, nullable=False)
    results = Column(Text)
    artifacts = Column(JSON, default=list)
    file_operations_count = Column(Integer, default=0)
    verification_status = Column(String, default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime)
    
    # Automation maintenance columns
    prerequisite_satisfaction_required = Column(Boolean, default=False)
    auto_maintenance_enabled = Column(Boolean, default=True)
    quality_gate_level = Column(String, default='standard')  # basic, standard, comprehensive
    
    # Workspace paradigm support
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=True)
    
    # Relationship to parent task (many-to-one)
    parent_task = relationship("TaskBreakdownModel", back_populates="subtasks")
    # Relationship to workspace (many-to-one)
    workspace = relationship("WorkspaceModel", back_populates="subtasks")


class LockTrackingModel(Base):
    """SQLAlchemy model for lock tracking."""
    
    __tablename__ = 'lock_tracking'
    
    resource_name = Column(String, primary_key=True)
    locked_at = Column(DateTime, nullable=False)
    locked_by = Column(String, nullable=False)
    
    # Workspace paradigm support
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=True)


class FileOperationModel(Base):
    """SQLAlchemy model for tracking file operations during subtask execution."""
    
    __tablename__ = 'file_operations'
    
    operation_id = Column(String, primary_key=True)
    subtask_id = Column(String, ForeignKey('subtasks.task_id'), nullable=False)
    session_id = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)  # CREATE, MODIFY, DELETE, READ, MOVE, COPY
    file_path = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    content_hash = Column(String(64))
    file_size = Column(Integer)
    file_metadata = Column(JSON, default=dict)
    verification_status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Workspace paradigm support
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=True)
    workspace_relative_path = Column(Text, nullable=True)  # Path relative to workspace root
    original_session_id = Column(String, nullable=True)  # For migration tracking
    
    # Relationship to subtask (many-to-one)
    subtask = relationship("SubTaskModel")
    
    # Relationship to verifications (one-to-many)
    verifications = relationship("FileVerificationModel", back_populates="operation", cascade="all, delete-orphan")


class FileVerificationModel(Base):
    """SQLAlchemy model for file operation verification results."""
    
    __tablename__ = 'file_verifications'
    
    verification_id = Column(String, primary_key=True)
    operation_id = Column(String, ForeignKey('file_operations.operation_id'), nullable=False)
    verification_timestamp = Column(DateTime, nullable=False, default=datetime.now)
    file_exists = Column(Boolean, nullable=False)
    content_matches = Column(Boolean)
    size_matches = Column(Boolean)
    permissions_correct = Column(Boolean)
    verification_status = Column(String, nullable=False)  # VERIFIED, FAILED, PARTIAL
    errors = Column(JSON, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationship to operation (many-to-one)
    operation = relationship("FileOperationModel", back_populates="verifications")


class ArchitecturalDecisionModel(Base):
    """SQLAlchemy model for architectural decision records (ADRs)."""
    
    __tablename__ = 'architectural_decisions'
    
    decision_id = Column(String, primary_key=True)
    decision_number = Column(Integer, nullable=False)
    subtask_id = Column(String, ForeignKey('subtasks.task_id'), nullable=False)
    session_id = Column(String, nullable=False)
    specialist_type = Column(String, nullable=False)
    
    # Decision Content
    title = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # ARCHITECTURE, IMPLEMENTATION, DESIGN, etc.
    impact_level = Column(String, nullable=False)  # HIGH, MEDIUM, LOW
    status = Column(String, nullable=False, default='proposed')  # PROPOSED, ACCEPTED, SUPERSEDED
    problem_statement = Column(Text)
    context = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    implementation_approach = Column(Text)
    
    # Relationships and Dependencies
    supersedes = Column(JSON, default=list)  # Array of decision IDs this replaces
    dependencies = Column(JSON, default=list)  # Array of decision IDs this depends on
    affected_files = Column(JSON, default=list)
    affected_components = Column(JSON, default=list)
    
    # Quality Aspects
    alternatives_considered = Column(JSON, default=list)
    trade_offs = Column(JSON, default=dict)
    risks = Column(JSON, default=list)
    mitigation_strategies = Column(JSON, default=list)
    success_criteria = Column(JSON, default=list)
    
    # Implementation Tracking
    implementation_status = Column(String, default='planned')  # PLANNED, IN_PROGRESS, COMPLETED, FAILED
    outcome_assessment = Column(Text)
    lessons_learned = Column(Text)
    review_schedule = Column(DateTime)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationship to subtask (many-to-one)
    subtask = relationship("SubTaskModel")


class DecisionEvolutionModel(Base):
    """SQLAlchemy model for tracking evolution and supersession of decisions."""
    
    __tablename__ = 'decision_evolution'
    
    evolution_id = Column(String, primary_key=True)
    original_decision_id = Column(String, ForeignKey('architectural_decisions.decision_id'), nullable=False)
    new_decision_id = Column(String, ForeignKey('architectural_decisions.decision_id'), nullable=False)
    evolution_type = Column(String, nullable=False)  # SUPERSEDED, REFINED, REVERSED, CLARIFIED
    evolution_reason = Column(Text)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    original_decision = relationship("ArchitecturalDecisionModel", foreign_keys=[original_decision_id])
    new_decision = relationship("ArchitecturalDecisionModel", foreign_keys=[new_decision_id])


class TaskPrerequisiteModel(Base):
    """SQLAlchemy model for task prerequisites and dependencies."""
    
    __tablename__ = 'task_prerequisites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_task_id = Column(String, ForeignKey('task_breakdowns.parent_task_id'), nullable=False)
    prerequisite_type = Column(String, nullable=False)  # completion_dependency, validation_requirement, file_dependency, quality_gate
    description = Column(Text, nullable=False)
    validation_criteria = Column(Text)
    is_auto_resolvable = Column(Boolean, default=False)
    is_satisfied = Column(Boolean, default=False)
    satisfied_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationship to parent task
    parent_task = relationship("TaskBreakdownModel")


class MaintenanceOperationModel(Base):
    """SQLAlchemy model for maintenance operations."""
    
    __tablename__ = 'maintenance_operations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_type = Column(String, nullable=False)  # file_cleanup, structure_validation, documentation_update, handover_preparation
    task_context = Column(Text)
    execution_status = Column(String, nullable=False, default='pending')  # pending, running, completed, failed
    results_summary = Column(Text)
    auto_resolution_attempted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime)


class ProjectHealthMetricModel(Base):
    """SQLAlchemy model for project health metrics."""
    
    __tablename__ = 'project_health_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String, nullable=False)  # file_count, documentation_coverage, character_limit_compliance, cross_reference_validity
    metric_value = Column(JSON)  # Using JSON to handle different metric types (numeric, boolean, etc.)
    threshold_value = Column(JSON)
    is_passing = Column(Boolean, nullable=False)
    details = Column(Text)
    measured_at = Column(DateTime, nullable=False, default=datetime.now)


class TaskArchiveModel(Base):
    """SQLAlchemy model for archived tasks."""
    
    __tablename__ = 'task_archives'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_task_id = Column(String, nullable=False)
    parent_task_id = Column(String, nullable=False)
    archive_reason = Column(String, nullable=False)  # stale, orphaned, completed, failed, etc.
    archived_data = Column(JSON, nullable=False)  # Complete task data as JSON
    artifacts_preserved = Column(Boolean, default=False)
    artifact_references = Column(JSON, default=list)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class StaleTaskTrackingModel(Base):
    """SQLAlchemy model for tracking stale tasks."""
    
    __tablename__ = 'stale_task_tracking'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, nullable=False, unique=True)
    last_activity_at = Column(DateTime, nullable=False)
    stale_indicators = Column(JSON, default=list)  # List of reasons why task is stale
    auto_cleanup_eligible = Column(Boolean, default=False)
    detection_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class TaskLifecycleModel(Base):
    """SQLAlchemy model for tracking task lifecycle transitions."""
    
    __tablename__ = 'task_lifecycle'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, nullable=False)
    lifecycle_stage = Column(String, nullable=False)  # created, active, completed, stale, archived, failed
    previous_stage = Column(String)
    transition_reason = Column(Text)
    automated_transition = Column(Boolean, default=False)
    transition_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


# ============================================
# Workspace Paradigm Models
# ============================================

class WorkspaceModel(Base):
    """SQLAlchemy model for workspace registry."""
    
    __tablename__ = 'workspaces'
    
    workspace_id = Column(String, primary_key=True)
    workspace_name = Column(String, nullable=False)
    workspace_path = Column(String, nullable=False, unique=True)
    detection_method = Column(String, nullable=False)  # git_root, project_marker, explicit, etc.
    detection_confidence = Column(Integer, nullable=False)  # 1-10 scale
    
    # Project Information
    project_type = Column(String)  # python, javascript, rust, etc.
    project_markers = Column(JSON)  # JSON array of detected markers
    git_root_path = Column(String)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    artifact_storage_policy = Column(String, default='workspace_relative')  # workspace_relative, absolute, hybrid
    
    # Security and Validation
    is_validated = Column(Boolean, default=False)
    is_writable = Column(Boolean, default=True)
    security_warnings = Column(JSON)  # JSON array of warnings
    
    # Statistics
    total_tasks = Column(Integer, default=0)
    active_tasks = Column(Integer, default=0)
    last_activity_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    last_accessed_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    task_breakdowns = relationship("TaskBreakdownModel", back_populates="workspace")
    subtasks = relationship("SubTaskModel", back_populates="workspace")
    workspace_tasks = relationship("WorkspaceTaskModel", back_populates="workspace", cascade="all, delete-orphan")
    workspace_artifacts = relationship("WorkspaceArtifactModel", back_populates="workspace", cascade="all, delete-orphan")
    workspace_configurations = relationship("WorkspaceConfigurationModel", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceTaskModel(Base):
    """SQLAlchemy model for workspace-task associations."""
    
    __tablename__ = 'workspace_tasks'
    
    association_id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=False)
    task_id = Column(String, ForeignKey('task_breakdowns.parent_task_id'), nullable=False)
    
    # Association metadata
    association_type = Column(String, default='primary')  # primary, reference, archived
    created_in_workspace = Column(Boolean, default=True)
    relative_artifact_paths = Column(JSON)  # JSON array of workspace-relative paths
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    workspace = relationship("WorkspaceModel", back_populates="workspace_tasks")
    task_breakdown = relationship("TaskBreakdownModel")


class WorkspaceArtifactModel(Base):
    """SQLAlchemy model for workspace artifact storage."""
    
    __tablename__ = 'workspace_artifacts'
    
    artifact_id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=False)
    task_id = Column(String, ForeignKey('subtasks.task_id'), nullable=True)
    
    # Storage Information
    relative_path = Column(String, nullable=False)  # Path relative to workspace root
    absolute_path = Column(String, nullable=False)  # Absolute path for verification
    artifact_type = Column(String, nullable=False)  # code, documentation, analysis, etc.
    storage_method = Column(String, default='file')  # file, embedded, external
    
    # Content and Metadata
    content_hash = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    content_preview = Column(Text)  # First few lines for quick display
    
    # Workspace Context
    created_by_task = Column(Boolean, default=True)
    is_persistent = Column(Boolean, default=True)  # Should survive task completion
    backup_available = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    last_verified_at = Column(DateTime)
    
    # Relationships
    workspace = relationship("WorkspaceModel", back_populates="workspace_artifacts")
    subtask = relationship("SubTaskModel")


class WorkspaceConfigurationModel(Base):
    """SQLAlchemy model for workspace configurations."""
    
    __tablename__ = 'workspace_configurations'
    
    config_id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey('workspaces.workspace_id'), nullable=False)
    
    # Configuration Categories
    config_category = Column(String, nullable=False)  # directories, artifacts, tools, security
    config_key = Column(String, nullable=False)
    config_value = Column(String, nullable=False)  # JSON value
    config_type = Column(String, nullable=False)  # string, number, boolean, array, object
    
    # Configuration Metadata
    is_user_defined = Column(Boolean, default=False)
    is_system_generated = Column(Boolean, default=True)
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    workspace = relationship("WorkspaceModel", back_populates="workspace_configurations")
