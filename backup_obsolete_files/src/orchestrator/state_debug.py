"""
State management for task orchestration using SQLite - Debug Version

Safer database initialization with better error handling.
"""

import sqlite3
import json
import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import TaskBreakdown, SubTask, TaskStatus, SpecialistType


class StateManager:
    """Manages persistent state for tasks and orchestration data."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use a safer database location - system temp directory
            temp_dir = Path(tempfile.gettempdir())
            db_path = temp_dir / "mcp_task_orchestrator.db"
        
        self.db_path = str(db_path)
        self.lock = asyncio.Lock()
        self._initialized = False
        
        # Initialize database synchronously with better error handling
        try:
            self._initialize_database_sync()
            print(f"Database initialized successfully at: {self.db_path}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}. Using in-memory fallback.", file=sys.stderr)
            # Fallback to in-memory database
            self.db_path = ":memory:"
            self._initialize_database_sync()
    
    def _initialize_database_sync(self):
        """Initialize SQLite database with required tables (synchronous version)."""
        # Ensure directory exists
        if self.db_path != ":memory:":
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        
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
                    specialist_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    dependencies TEXT,
                    estimated_effort TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (parent_task_id) REFERENCES task_breakdowns (parent_task_id)
                )
            """)
            
            # Create task_results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    task_id TEXT PRIMARY KEY,
                    results TEXT NOT NULL,
                    artifacts TEXT,
                    next_action TEXT NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES subtasks (task_id)
                )
            """)
            
            conn.commit()
            self._initialized = True
            
        finally:
            conn.close()
    
    async def initialize_database(self):
        """Async database initialization (if needed)."""
        if not self._initialized:
            await asyncio.get_event_loop().run_in_executor(
                None, self._initialize_database_sync
            )
    
    async def store_task_breakdown(self, breakdown: TaskBreakdown):
        """Store a task breakdown in the database."""
        async with self.lock:
            def _store():
                conn = sqlite3.connect(self.db_path)
                try:
                    # Store main task breakdown
                    conn.execute(
                        """INSERT OR REPLACE INTO task_breakdowns 
                           (parent_task_id, description, complexity, context, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (breakdown.parent_task_id, breakdown.description, 
                         breakdown.complexity.value, breakdown.context, datetime.now())
                    )
                    
                    # Store subtasks
                    for subtask in breakdown.subtasks:
                        conn.execute(
                            """INSERT OR REPLACE INTO subtasks 
                               (task_id, parent_task_id, title, specialist_type, description,
                                dependencies, estimated_effort, status, created_at, updated_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (subtask.task_id, breakdown.parent_task_id, subtask.title,
                             subtask.specialist_type.value, subtask.description,
                             json.dumps(subtask.dependencies), subtask.estimated_effort,
                             subtask.status.value, datetime.now(), datetime.now())
                        )
                    
                    conn.commit()
                finally:
                    conn.close()
            
            await asyncio.get_event_loop().run_in_executor(None, _store)
    
    async def get_task_breakdown(self, parent_task_id: str) -> Optional[TaskBreakdown]:
        """Retrieve a task breakdown from the database."""
        async with self.lock:
            def _get():
                conn = sqlite3.connect(self.db_path)
                try:
                    # Get main task
                    cursor = conn.execute(
                        "SELECT description, complexity, context FROM task_breakdowns WHERE parent_task_id = ?",
                        (parent_task_id,)
                    )
                    task_row = cursor.fetchone()
                    if not task_row:
                        return None
                    
                    # Get subtasks
                    cursor = conn.execute(
                        """SELECT task_id, title, specialist_type, description, dependencies, 
                                  estimated_effort, status FROM subtasks WHERE parent_task_id = ?""",
                        (parent_task_id,)
                    )
                    subtask_rows = cursor.fetchall()
                    
                    return {
                        'task': task_row,
                        'subtasks': subtask_rows
                    }
                finally:
                    conn.close()
            
            result = await asyncio.get_event_loop().run_in_executor(None, _get)
            if not result:
                return None
            
            # Convert to TaskBreakdown object (simplified for debug)
            return {
                'parent_task_id': parent_task_id,
                'description': result['task'][0],
                'complexity': result['task'][1],
                'context': result['task'][2],
                'subtasks': result['subtasks']
            }
    
    async def get_all_tasks(self, include_completed: bool = False) -> Dict[str, Any]:
        """Get status of all tasks."""
        async with self.lock:
            def _get_all():
                conn = sqlite3.connect(self.db_path)
                try:
                    query = """
                        SELECT t.parent_task_id, t.description, t.complexity,
                               COUNT(s.task_id) as total_subtasks,
                               SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) as completed_subtasks
                        FROM task_breakdowns t
                        LEFT JOIN subtasks s ON t.parent_task_id = s.parent_task_id
                        GROUP BY t.parent_task_id, t.description, t.complexity
                    """
                    
                    cursor = conn.execute(query)
                    return cursor.fetchall()
                finally:
                    conn.close()
            
            rows = await asyncio.get_event_loop().run_in_executor(None, _get_all)
            
            return {
                'active_tasks': len(rows),
                'tasks': [
                    {
                        'task_id': row[0],
                        'description': row[1],
                        'complexity': row[2],
                        'progress': f"{row[4]}/{row[3]} completed"
                    }
                    for row in rows
                ]
            }
