"""
Async SQLite implementation of StateRepository.

This module provides an async SQLite implementation of the StateRepository
interface using the new database adapter system.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ....domain.repositories.state_repository import StateRepository
from ..base import OperationalDatabaseAdapter

logger = logging.getLogger(__name__)


class AsyncSQLiteStateRepository(StateRepository):
    """Async SQLite implementation of the StateRepository interface."""
    
    def __init__(self, db_adapter: OperationalDatabaseAdapter):
        """
        Initialize the async SQLite state repository.
        
        Args:
            db_adapter: Operational database adapter instance
        """
        self.db_adapter = db_adapter
        self._tables_created = False
    
    async def _ensure_tables(self):
        """Ensure required tables exist."""
        if self._tables_created:
            return
        
        try:
            schema = """
                -- Orchestration state table
                CREATE TABLE IF NOT EXISTS orchestration_state (
                    session_id TEXT PRIMARY KEY,
                    current_task_id TEXT,
                    status TEXT NOT NULL,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                -- Session metadata table
                CREATE TABLE IF NOT EXISTS session_metadata (
                    session_id TEXT PRIMARY KEY,
                    workspace_path TEXT,
                    configuration TEXT,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES orchestration_state(session_id)
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_state_status ON orchestration_state(status);
                CREATE INDEX IF NOT EXISTS idx_state_updated ON orchestration_state(updated_at);
                CREATE INDEX IF NOT EXISTS idx_session_accessed ON session_metadata(last_accessed_at);
            """
            
            if hasattr(self.db_adapter, 'create_tables'):
                await self.db_adapter.create_tables(schema)
            else:
                statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
                for statement in statements:
                    await self.db_adapter.execute(statement)
            
            self._tables_created = True
            logger.info("State repository tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create state repository tables: {e}")
            raise
    
    async def save_state(self, session_id: str, state_data: Dict[str, Any]) -> bool:
        """Save orchestration state asynchronously."""
        await self._ensure_tables()
        
        try:
            now = datetime.utcnow().isoformat()
            
            async with self.db_adapter.transaction() as tx:
                # Upsert orchestration state
                await self.db_adapter.execute("""
                    INSERT OR REPLACE INTO orchestration_state (
                        session_id, current_task_id, status, context, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM orchestration_state WHERE session_id = ?), ?),
                        ?
                    )
                """, {
                    'session_id': session_id,
                    'current_task_id': state_data.get('current_task_id'),
                    'status': state_data.get('status', 'active'),
                    'context': json.dumps(state_data.get('context', {})),
                    'created_at_check': session_id,
                    'created_at': now,
                    'updated_at': now
                })
                
                # Update session metadata if provided
                if 'workspace_path' in state_data or 'configuration' in state_data:
                    await self.db_adapter.execute("""
                        INSERT OR REPLACE INTO session_metadata (
                            session_id, workspace_path, configuration, created_at, last_accessed_at
                        ) VALUES (?, ?, ?,
                            COALESCE((SELECT created_at FROM session_metadata WHERE session_id = ?), ?),
                            ?
                        )
                    """, {
                        'session_id': session_id,
                        'workspace_path': state_data.get('workspace_path'),
                        'configuration': json.dumps(state_data.get('configuration', {})),
                        'created_at_check': session_id,
                        'created_at': now,
                        'last_accessed_at': now
                    })
            
            logger.info(f"Saved state for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state for session {session_id}: {e}")
            raise
    
    async def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load orchestration state asynchronously."""
        await self._ensure_tables()
        
        try:
            # Get orchestration state
            state_result = await self.db_adapter.execute_one(
                "SELECT * FROM orchestration_state WHERE session_id = ?",
                {'session_id': session_id}
            )
            
            if not state_result:
                return None
            
            # Parse context JSON
            if state_result['context']:
                state_result['context'] = json.loads(state_result['context'])
            else:
                state_result['context'] = {}
            
            # Get session metadata
            metadata_result = await self.db_adapter.execute_one(
                "SELECT * FROM session_metadata WHERE session_id = ?",
                {'session_id': session_id}
            )
            
            if metadata_result:
                # Parse configuration JSON
                if metadata_result['configuration']:
                    metadata_result['configuration'] = json.loads(metadata_result['configuration'])
                else:
                    metadata_result['configuration'] = {}
                
                # Merge metadata into state
                state_result.update({
                    'workspace_path': metadata_result['workspace_path'],
                    'configuration': metadata_result['configuration']
                })
                
                # Update last accessed time
                await self.db_adapter.execute(
                    "UPDATE session_metadata SET last_accessed_at = ? WHERE session_id = ?",
                    {
                        'last_accessed_at': datetime.utcnow().isoformat(),
                        'session_id': session_id
                    }
                )
            
            return state_result
            
        except Exception as e:
            logger.error(f"Failed to load state for session {session_id}: {e}")
            raise
    
    async def delete_state(self, session_id: str) -> bool:
        """Delete orchestration state asynchronously."""
        await self._ensure_tables()
        
        try:
            async with self.db_adapter.transaction() as tx:
                # Delete session metadata
                await self.db_adapter.execute(
                    "DELETE FROM session_metadata WHERE session_id = ?",
                    {'session_id': session_id}
                )
                
                # Delete orchestration state
                await self.db_adapter.execute(
                    "DELETE FROM orchestration_state WHERE session_id = ?",
                    {'session_id': session_id}
                )
            
            logger.info(f"Deleted state for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete state for session {session_id}: {e}")
            raise
    
    async def list_sessions(self, limit: Optional[int] = None) -> list:
        """List all sessions asynchronously."""
        await self._ensure_tables()
        
        try:
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            query = f"""
                SELECT 
                    os.*,
                    sm.workspace_path,
                    sm.last_accessed_at
                FROM orchestration_state os
                LEFT JOIN session_metadata sm ON os.session_id = sm.session_id
                ORDER BY COALESCE(sm.last_accessed_at, os.updated_at) DESC
                {limit_clause}
            """
            
            results = await self.db_adapter.execute(query)
            
            # Parse context JSON for each session
            for session in results:
                if session['context']:
                    session['context'] = json.loads(session['context'])
                else:
                    session['context'] = {}
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            raise
    
    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old sessions asynchronously."""
        await self._ensure_tables()
        
        try:
            cutoff_date = datetime.utcnow()
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            # Get sessions to delete
            old_sessions = await self.db_adapter.execute("""
                SELECT session_id FROM orchestration_state os
                LEFT JOIN session_metadata sm ON os.session_id = sm.session_id
                WHERE COALESCE(sm.last_accessed_at, os.updated_at) < ?
            """, {'cutoff_date': cutoff_iso})
            
            if not old_sessions:
                return 0
            
            session_ids = [session['session_id'] for session in old_sessions]
            
            # Delete old sessions
            async with self.db_adapter.transaction() as tx:
                for session_id in session_ids:
                    await self.db_adapter.execute(
                        "DELETE FROM session_metadata WHERE session_id = ?",
                        {'session_id': session_id}
                    )
                    await self.db_adapter.execute(
                        "DELETE FROM orchestration_state WHERE session_id = ?",
                        {'session_id': session_id}
                    )
            
            logger.info(f"Cleaned up {len(session_ids)} old sessions")
            return len(session_ids)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            raise