"""
SQLAlchemy models for the database-backed persistence mechanism.

This module defines the SQLAlchemy ORM models that map directly to the
task orchestrator's domain models for persistent storage in a database.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
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
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime)
    
    # Relationship to parent task (many-to-one)
    parent_task = relationship("TaskBreakdownModel", back_populates="subtasks")


class LockTrackingModel(Base):
    """SQLAlchemy model for lock tracking."""
    
    __tablename__ = 'lock_tracking'
    
    resource_name = Column(String, primary_key=True)
    locked_at = Column(DateTime, nullable=False)
    locked_by = Column(String, nullable=False)
