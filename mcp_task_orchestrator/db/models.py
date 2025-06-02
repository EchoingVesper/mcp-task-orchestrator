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
    
    # Relationship to subtasks (one-to-many)
    subtasks = relationship("SubTaskModel", back_populates="parent_task", cascade="all, delete-orphan")


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
    
    # Relationship to parent task (many-to-one)
    parent_task = relationship("TaskBreakdownModel", back_populates="subtasks")


class LockTrackingModel(Base):
    """SQLAlchemy model for lock tracking."""
    
    __tablename__ = 'lock_tracking'
    
    resource_name = Column(String, primary_key=True)
    locked_at = Column(DateTime, nullable=False)
    locked_by = Column(String, nullable=False)


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
