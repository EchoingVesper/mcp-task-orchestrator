"""
Base Repository Module - Core setup and configuration for Generic Task Repository

This module contains the base repository class, database connection setup,
and core configuration needed by all other repository modules.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import create_engine, event, select, delete, update, and_, or_, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import text

from ...orchestrator.generic_models import (
    GenericTask, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact,
    TaskTemplate, TemplateParameter,
    TaskType, TaskStatus, LifecycleStage, DependencyType, DependencyStatus,
    EventType, EventCategory, AttributeType, ArtifactType
)
from ..models import Base

logger = logging.getLogger(__name__)


class CycleDetectedError(Exception):
    """Raised when a cycle is detected in task dependencies."""
    pass


class GenericTaskRepository:
    """Repository for Generic Task database operations with async support."""
    
    def __init__(self, db_url: str, sync_mode: bool = False):
        """Initialize the repository with database connection.
        
        Args:
            db_url: Database connection URL
            sync_mode: If True, use synchronous operations (for migration)
        """
        self.db_url = db_url
        self.sync_mode = sync_mode
        
        if sync_mode:
            # Synchronous engine for migrations
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
        else:
            # Async engine for normal operations
            # Convert sqlite:// to sqlite+aiosqlite://
            if db_url.startswith("sqlite://"):
                async_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
            else:
                async_url = db_url
                
            self.async_engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            self.async_session_maker = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
    
    @asynccontextmanager
    async def get_session(self):
        """Get an async database session."""
        if self.sync_mode:
            raise RuntimeError("Cannot use async session in sync mode")
            
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()