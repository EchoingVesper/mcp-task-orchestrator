"""
SQLite implementation of StateRepository.

This module provides a concrete SQLite implementation of the StateRepository
interface defined in the domain layer.
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from ....domain.repositories.state_repository import StateRepository
from ..connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class SQLiteStateRepository(StateRepository):
    """SQLite implementation of the StateRepository interface."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize the SQLite state repository.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required tables exist."""
        with self.connection_manager.transaction() as conn:
            # Create sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            
            # Create contexts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_contexts (
                    session_id TEXT NOT NULL,
                    context_key TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (session_id, context_key),
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create workflow_states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_states (
                    session_id TEXT PRIMARY KEY,
                    state_data TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_workspace ON sessions(workspace_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON session_events(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON session_events(event_type)")
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save or update a session."""
        now = datetime.utcnow().isoformat()
        
        # Check if session exists
        existing = self.connection_manager.execute_one(
            "SELECT id FROM sessions WHERE id = ?",
            (session_id,)
        )
        
        with self.connection_manager.transaction() as conn:
            if existing:
                # Update existing session
                conn.execute("""
                    UPDATE sessions SET
                        workspace_id = ?,
                        status = ?,
                        metadata = ?,
                        updated_at = ?,
                        completed_at = ?
                    WHERE id = ?
                """, (
                    session_data.get('workspace_id'),
                    session_data.get('status', 'active'),
                    json.dumps(session_data.get('metadata', {})),
                    now,
                    session_data.get('completed_at'),
                    session_id
                ))
            else:
                # Insert new session
                conn.execute("""
                    INSERT INTO sessions (
                        id, workspace_id, status, metadata,
                        created_at, updated_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    session_data.get('workspace_id'),
                    session_data.get('status', 'active'),
                    json.dumps(session_data.get('metadata', {})),
                    session_data.get('created_at', now),
                    now,
                    session_data.get('completed_at')
                ))
        
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by ID."""
        row = self.connection_manager.execute_one(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        
        if row:
            session = dict(row)
            session['metadata'] = json.loads(session['metadata']) if session['metadata'] else {}
            return session
        return None
    
    def list_sessions(self, 
                     active_only: bool = False,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all sessions with optional filtering."""
        query = "SELECT * FROM sessions"
        params = []
        
        if active_only:
            query += " WHERE status = 'active'"
        
        query += " ORDER BY updated_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        if offset:
            query += " OFFSET ?"
            params.append(offset)
        
        rows = self.connection_manager.execute(query, params)
        
        sessions = []
        for row in rows:
            session = dict(row)
            session['metadata'] = json.loads(session['metadata']) if session['metadata'] else {}
            sessions.append(session)
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all associated data."""
        with self.connection_manager.transaction() as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0
    
    def save_context(self, session_id: str, context_key: str, 
                    context_data: Dict[str, Any]) -> bool:
        """Save context data for a session."""
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            # Use INSERT OR REPLACE for upsert behavior
            conn.execute("""
                INSERT OR REPLACE INTO session_contexts (
                    session_id, context_key, context_data,
                    created_at, updated_at
                ) VALUES (?, ?, ?, 
                    COALESCE((SELECT created_at FROM session_contexts 
                              WHERE session_id = ? AND context_key = ?), ?),
                    ?)
            """, (
                session_id, context_key, json.dumps(context_data),
                session_id, context_key, now,
                now
            ))
        
        return True
    
    def get_context(self, session_id: str, context_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve context data for a session."""
        row = self.connection_manager.execute_one(
            "SELECT context_data FROM session_contexts WHERE session_id = ? AND context_key = ?",
            (session_id, context_key)
        )
        
        if row:
            return json.loads(row['context_data'])
        return None
    
    def list_contexts(self, session_id: str) -> List[str]:
        """List all context keys for a session."""
        rows = self.connection_manager.execute(
            "SELECT context_key FROM session_contexts WHERE session_id = ?",
            (session_id,)
        )
        return [row['context_key'] for row in rows]
    
    def save_workflow_state(self, session_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Save the current workflow state for a session."""
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            # Use INSERT OR REPLACE for upsert behavior
            conn.execute("""
                INSERT OR REPLACE INTO workflow_states (
                    session_id, state_data, updated_at
                ) VALUES (?, ?, ?)
            """, (
                session_id, json.dumps(workflow_data), now
            ))
        
        return True
    
    def get_workflow_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current workflow state for a session."""
        row = self.connection_manager.execute_one(
            "SELECT state_data FROM workflow_states WHERE session_id = ?",
            (session_id,)
        )
        
        if row:
            return json.loads(row['state_data'])
        return None
    
    def record_event(self, session_id: str, event_type: str, 
                    event_data: Dict[str, Any]) -> bool:
        """Record an event in the session history."""
        event_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            conn.execute("""
                INSERT INTO session_events (
                    id, session_id, event_type, event_data, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                event_id, session_id, event_type, 
                json.dumps(event_data), now
            ))
        
        return True
    
    def get_session_events(self, session_id: str, 
                          event_type: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get events for a session."""
        query = "SELECT * FROM session_events WHERE session_id = ?"
        params = [session_id]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        rows = self.connection_manager.execute(query, params)
        
        events = []
        for row in rows:
            event = dict(row)
            event['event_data'] = json.loads(event['event_data']) if event['event_data'] else {}
            events.append(event)
        
        return events
    
    def cleanup_old_sessions(self, older_than: datetime, 
                           keep_active: bool = True) -> int:
        """Clean up old sessions."""
        query = "DELETE FROM sessions WHERE updated_at < ?"
        params = [older_than.isoformat()]
        
        if keep_active:
            query += " AND status != 'active'"
        
        with self.connection_manager.transaction() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get metrics about sessions."""
        # Get count by status
        status_rows = self.connection_manager.execute("""
            SELECT status, COUNT(*) as count 
            FROM sessions
            GROUP BY status
        """)
        
        status_counts = {row['status']: row['count'] for row in status_rows}
        
        # Get total count
        total_row = self.connection_manager.execute_one(
            "SELECT COUNT(*) as count FROM sessions"
        )
        
        # Get active sessions count
        active_row = self.connection_manager.execute_one(
            "SELECT COUNT(*) as count FROM sessions WHERE status = 'active'"
        )
        
        return {
            'total_count': total_row['count'] if total_row else 0,
            'active_count': active_row['count'] if active_row else 0,
            'status_breakdown': status_counts
        }