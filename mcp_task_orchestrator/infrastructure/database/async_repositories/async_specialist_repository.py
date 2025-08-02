"""
Async SQLite implementation of SpecialistRepository.

This module provides an async SQLite implementation of the SpecialistRepository
interface using the new database adapter system.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from ....domain.repositories.specialist_repository import SpecialistRepository
from ..base import OperationalDatabaseAdapter

logger = logging.getLogger(__name__)


class AsyncSQLiteSpecialistRepository(SpecialistRepository):
    """Async SQLite implementation of the SpecialistRepository interface."""
    
    def __init__(self, db_adapter: OperationalDatabaseAdapter):
        """
        Initialize the async SQLite specialist repository.
        
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
                -- Specialists table
                CREATE TABLE IF NOT EXISTS specialists (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    description TEXT,
                    capabilities TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                -- Specialist assignments table
                CREATE TABLE IF NOT EXISTS specialist_assignments (
                    id TEXT PRIMARY KEY,
                    specialist_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    session_id TEXT,
                    assigned_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL DEFAULT 'assigned',
                    result TEXT,
                    FOREIGN KEY (specialist_id) REFERENCES specialists(id),
                    UNIQUE(specialist_id, task_id)
                );
                
                -- Specialist performance metrics table
                CREATE TABLE IF NOT EXISTS specialist_metrics (
                    id TEXT PRIMARY KEY,
                    specialist_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    recorded_at TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (specialist_id) REFERENCES specialists(id)
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_specialists_role ON specialists(role);
                CREATE INDEX IF NOT EXISTS idx_specialists_status ON specialists(status);
                CREATE INDEX IF NOT EXISTS idx_assignments_specialist ON specialist_assignments(specialist_id);
                CREATE INDEX IF NOT EXISTS idx_assignments_task ON specialist_assignments(task_id);
                CREATE INDEX IF NOT EXISTS idx_assignments_status ON specialist_assignments(status);
                CREATE INDEX IF NOT EXISTS idx_metrics_specialist ON specialist_metrics(specialist_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_type ON specialist_metrics(metric_type);
            """
            
            if hasattr(self.db_adapter, 'create_tables'):
                await self.db_adapter.create_tables(schema)
            else:
                statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
                for statement in statements:
                    await self.db_adapter.execute(statement)
            
            self._tables_created = True
            logger.info("Specialist repository tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create specialist repository tables: {e}")
            raise
    
    async def create_specialist(self, specialist_data: Dict[str, Any]) -> str:
        """Create a new specialist asynchronously."""
        await self._ensure_tables()
        
        specialist_id = specialist_data.get('id', str(uuid.uuid4()))
        now = datetime.utcnow().isoformat()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT INTO specialists (
                        id, name, role, description, capabilities, status, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, {
                    'id': specialist_id,
                    'name': specialist_data.get('name'),
                    'role': specialist_data.get('role'),
                    'description': specialist_data.get('description'),
                    'capabilities': json.dumps(specialist_data.get('capabilities', [])),
                    'status': specialist_data.get('status', 'active'),
                    'metadata': json.dumps(specialist_data.get('metadata', {})),
                    'created_at': now,
                    'updated_at': now
                })
            
            logger.info(f"Created specialist {specialist_id}")
            return specialist_id
            
        except Exception as e:
            logger.error(f"Failed to create specialist: {e}")
            raise
    
    async def get_specialist(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        """Get a specialist by ID asynchronously."""
        await self._ensure_tables()
        
        try:
            result = await self.db_adapter.execute_one(
                "SELECT * FROM specialists WHERE id = ?",
                {'id': specialist_id}
            )
            
            if result:
                # Parse JSON fields
                if result['capabilities']:
                    result['capabilities'] = json.loads(result['capabilities'])
                else:
                    result['capabilities'] = []
                
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                else:
                    result['metadata'] = {}
                
                # Get recent assignments
                assignments = await self.db_adapter.execute("""
                    SELECT * FROM specialist_assignments 
                    WHERE specialist_id = ? 
                    ORDER BY assigned_at DESC 
                    LIMIT 10
                """, {'specialist_id': specialist_id})
                
                result['recent_assignments'] = assignments
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get specialist {specialist_id}: {e}")
            raise
    
    async def update_specialist(self, specialist_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a specialist asynchronously."""
        await self._ensure_tables()
        
        try:
            # Build update query dynamically
            update_fields = []
            params = {'specialist_id': specialist_id}
            
            for field in ['name', 'role', 'description', 'status']:
                if field in update_data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = update_data[field]
            
            if 'capabilities' in update_data:
                update_fields.append("capabilities = :capabilities")
                params['capabilities'] = json.dumps(update_data['capabilities'])
            
            if 'metadata' in update_data:
                update_fields.append("metadata = :metadata")
                params['metadata'] = json.dumps(update_data['metadata'])
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = :updated_at")
            params['updated_at'] = datetime.utcnow().isoformat()
            
            if len(update_fields) == 1:  # Only updated_at
                return False
            
            query = f"UPDATE specialists SET {', '.join(update_fields)} WHERE id = :specialist_id"
            
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute(query, params)
            
            logger.info(f"Updated specialist {specialist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update specialist {specialist_id}: {e}")
            raise
    
    async def delete_specialist(self, specialist_id: str) -> bool:
        """Delete a specialist asynchronously."""
        await self._ensure_tables()
        
        try:
            async with self.db_adapter.transaction() as tx:
                # Delete metrics
                await self.db_adapter.execute(
                    "DELETE FROM specialist_metrics WHERE specialist_id = ?",
                    {'specialist_id': specialist_id}
                )
                
                # Delete assignments
                await self.db_adapter.execute(
                    "DELETE FROM specialist_assignments WHERE specialist_id = ?",
                    {'specialist_id': specialist_id}
                )
                
                # Delete the specialist
                await self.db_adapter.execute(
                    "DELETE FROM specialists WHERE id = ?",
                    {'id': specialist_id}
                )
            
            logger.info(f"Deleted specialist {specialist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete specialist {specialist_id}: {e}")
            raise
    
    async def list_specialists(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List specialists with optional filtering asynchronously."""
        await self._ensure_tables()
        
        try:
            # Build query with filters
            where_clauses = []
            params = {}
            
            if role is not None:
                where_clauses.append("role = :role")
                params['role'] = role
            
            if status is not None:
                where_clauses.append("status = :status")
                params['status'] = status
            
            where_clause = ""
            if where_clauses:
                where_clause = f"WHERE {' AND '.join(where_clauses)}"
            
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            query = f"""
                SELECT * FROM specialists 
                {where_clause}
                ORDER BY created_at DESC
                {limit_clause}
            """
            
            results = await self.db_adapter.execute(query, params)
            
            # Parse JSON fields for each specialist
            for specialist in results:
                if specialist['capabilities']:
                    specialist['capabilities'] = json.loads(specialist['capabilities'])
                else:
                    specialist['capabilities'] = []
                
                if specialist['metadata']:
                    specialist['metadata'] = json.loads(specialist['metadata'])
                else:
                    specialist['metadata'] = {}
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list specialists: {e}")
            raise
    
    async def assign_specialist(self, specialist_id: str, task_id: str, session_id: Optional[str] = None) -> str:
        """Assign a specialist to a task asynchronously."""
        await self._ensure_tables()
        
        assignment_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT INTO specialist_assignments (
                        id, specialist_id, task_id, session_id, assigned_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, {
                    'id': assignment_id,
                    'specialist_id': specialist_id,
                    'task_id': task_id,
                    'session_id': session_id,
                    'assigned_at': now,
                    'status': 'assigned'
                })
            
            logger.info(f"Assigned specialist {specialist_id} to task {task_id}")
            return assignment_id
            
        except Exception as e:
            logger.error(f"Failed to assign specialist {specialist_id} to task {task_id}: {e}")
            raise
    
    async def complete_assignment(self, assignment_id: str, result: Optional[str] = None) -> bool:
        """Complete a specialist assignment asynchronously."""
        await self._ensure_tables()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    UPDATE specialist_assignments 
                    SET status = 'completed', completed_at = ?, result = ?
                    WHERE id = ?
                """, {
                    'completed_at': datetime.utcnow().isoformat(),
                    'result': result,
                    'id': assignment_id
                })
            
            logger.info(f"Completed assignment {assignment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete assignment {assignment_id}: {e}")
            raise
    
    async def record_metric(self, specialist_id: str, metric_type: str, metric_value: float, context: Optional[Dict[str, Any]] = None) -> str:
        """Record a performance metric for a specialist asynchronously."""
        await self._ensure_tables()
        
        metric_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT INTO specialist_metrics (
                        id, specialist_id, metric_type, metric_value, recorded_at, context
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, {
                    'id': metric_id,
                    'specialist_id': specialist_id,
                    'metric_type': metric_type,
                    'metric_value': metric_value,
                    'recorded_at': now,
                    'context': json.dumps(context or {})
                })
            
            logger.info(f"Recorded metric {metric_type} for specialist {specialist_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to record metric for specialist {specialist_id}: {e}")
            raise