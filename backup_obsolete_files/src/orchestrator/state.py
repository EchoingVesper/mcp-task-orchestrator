"""
State management for task orchestration using SQLite.
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import TaskBreakdown, SubTask, TaskStatus, SpecialistType


class StateManager:
    """Manages persistent state for tasks and orchestration data."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to a local database file
            db_path = Path(__file__).parent.parent.parent / "task_orchestrator.db"
        
        self.db_path = str(db_path)
        self.lock = asyncio.Lock()
        self._initialized = False
        
        # Initialize database synchronously
        self._initialize_database_sync()
    
    def _initialize_database_sync(self):
        """Initialize SQLite database with required tables (synchronous version)."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Create task_breakdowns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_breakdowns (
                    parent_task_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    complexity TEXT NOT NULL,
                    context TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create subtasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subtasks (
                    task_id TEXT PRIMARY KEY,
                    parent_task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    specialist_type TEXT NOT NULL,
                    dependencies TEXT,  -- JSON array
                    estimated_effort TEXT NOT NULL,
                    status TEXT NOT NULL,
                    results TEXT,
                    artifacts TEXT,  -- JSON array
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (parent_task_id) REFERENCES task_breakdowns (parent_task_id)
                )
            """)
            
            conn.commit()
            self._initialized = True
        finally:
            conn.close()
    
    async def store_task_breakdown(self, breakdown: TaskBreakdown):
        """Store a task breakdown and its subtasks."""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Store parent task
                conn.execute("""
                    INSERT OR REPLACE INTO task_breakdowns 
                    (parent_task_id, description, complexity, context, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    breakdown.parent_task_id,
                    breakdown.description,
                    breakdown.complexity.value,
                    breakdown.context,
                    breakdown.created_at.isoformat()
                ))
                
                # Store subtasks
                for subtask in breakdown.subtasks:
                    await self._store_subtask_internal(conn, subtask, breakdown.parent_task_id)
                
                conn.commit()
            finally:
                conn.close()
    
    async def _store_subtask_internal(self, conn: sqlite3.Connection, 
                                    subtask: SubTask, parent_task_id: str):
        """Internal method to store a subtask within an existing connection."""
        conn.execute("""
            INSERT OR REPLACE INTO subtasks 
            (task_id, parent_task_id, title, description, specialist_type, 
             dependencies, estimated_effort, status, results, artifacts, 
             created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subtask.task_id,
            parent_task_id,
            subtask.title,
            subtask.description,
            subtask.specialist_type.value,
            json.dumps(subtask.dependencies),
            subtask.estimated_effort,
            subtask.status.value,
            subtask.results,
            json.dumps(subtask.artifacts),
            subtask.created_at.isoformat(),
            subtask.completed_at.isoformat() if subtask.completed_at else None
        ))
    
    async def get_subtask(self, task_id: str) -> Optional[SubTask]:
        """Retrieve a specific subtask by ID."""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT task_id, title, description, specialist_type, dependencies,
                           estimated_effort, status, results, artifacts, created_at, completed_at
                    FROM subtasks WHERE task_id = ?
                """, (task_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return self._row_to_subtask(row)
            finally:
                conn.close()
    
    async def update_subtask(self, subtask: SubTask):
        """Update an existing subtask."""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("""
                    UPDATE subtasks SET
                        title = ?, description = ?, specialist_type = ?,
                        dependencies = ?, estimated_effort = ?, status = ?,
                        results = ?, artifacts = ?, completed_at = ?
                    WHERE task_id = ?
                """, (
                    subtask.title,
                    subtask.description,
                    subtask.specialist_type.value,
                    json.dumps(subtask.dependencies),
                    subtask.estimated_effort,
                    subtask.status.value,
                    subtask.results,
                    json.dumps(subtask.artifacts),
                    subtask.completed_at.isoformat() if subtask.completed_at else None,
                    subtask.task_id
                ))
                conn.commit()
            finally:
                conn.close()
    
    async def get_subtasks_for_parent(self, parent_task_id: str) -> List[SubTask]:
        """Get all subtasks for a given parent task."""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT task_id, title, description, specialist_type, dependencies,
                           estimated_effort, status, results, artifacts, created_at, completed_at
                    FROM subtasks WHERE parent_task_id = ?
                    ORDER BY created_at
                """, (parent_task_id,))
                
                return [self._row_to_subtask(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    async def get_all_tasks(self) -> List[SubTask]:
        """Get all tasks in the system."""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT task_id, title, description, specialist_type, dependencies,
                           estimated_effort, status, results, artifacts, created_at, completed_at
                    FROM subtasks
                    ORDER BY created_at DESC
                """)
                
                return [self._row_to_subtask(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def _row_to_subtask(self, row) -> SubTask:
        """Convert database row to SubTask object."""
        task_id, title, description, specialist_type, dependencies, \
        estimated_effort, status, results, artifacts, created_at, completed_at = row
        
        return SubTask(
            task_id=task_id,
            title=title,
            description=description,
            specialist_type=SpecialistType(specialist_type),
            dependencies=json.loads(dependencies) if dependencies else [],
            estimated_effort=estimated_effort,
            status=TaskStatus(status),
            results=results,
            artifacts=json.loads(artifacts) if artifacts else [],
            created_at=datetime.fromisoformat(created_at),
            completed_at=datetime.fromisoformat(completed_at) if completed_at else None
        )
