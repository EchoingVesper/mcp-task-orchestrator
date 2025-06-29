"""
SQLite implementation of SpecialistRepository.

This module provides a concrete SQLite implementation of the SpecialistRepository
interface defined in the domain layer.
"""

import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from ....domain.repositories.specialist_repository import SpecialistRepository
from ..connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class SQLiteSpecialistRepository(SpecialistRepository):
    """SQLite implementation of the SpecialistRepository interface."""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize the SQLite specialist repository.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required tables exist."""
        with self.connection_manager.transaction() as conn:
            # Create specialists table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS specialists (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    prompt_template TEXT,
                    configuration TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create specialist templates table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS specialist_templates (
                    name TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    template_data TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create specialist usage table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS specialist_usage (
                    id TEXT PRIMARY KEY,
                    specialist_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    usage_data TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (specialist_id) REFERENCES specialists(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specialists_name ON specialists(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specialists_category ON specialists(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_specialist ON specialist_usage(specialist_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_task ON specialist_usage(task_id)")
    
    def create_specialist(self, specialist_data: Dict[str, Any]) -> str:
        """Create a new specialist role."""
        specialist_id = specialist_data.get('id', str(uuid.uuid4()))
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            conn.execute("""
                INSERT INTO specialists (
                    id, name, category, description, prompt_template,
                    configuration, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                specialist_id,
                specialist_data['name'],
                specialist_data.get('category', 'general'),
                specialist_data.get('description'),
                specialist_data.get('prompt_template'),
                json.dumps(specialist_data.get('configuration', {})),
                1 if specialist_data.get('is_active', True) else 0,
                now,
                now
            ))
        
        return specialist_id
    
    def get_specialist(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specialist by ID."""
        row = self.connection_manager.execute_one(
            "SELECT * FROM specialists WHERE id = ?",
            (specialist_id,)
        )
        
        if row:
            specialist = dict(row)
            specialist['configuration'] = json.loads(specialist['configuration']) if specialist['configuration'] else {}
            specialist['is_active'] = bool(specialist['is_active'])
            return specialist
        return None
    
    def get_specialist_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specialist by name."""
        row = self.connection_manager.execute_one(
            "SELECT * FROM specialists WHERE name = ?",
            (name,)
        )
        
        if row:
            specialist = dict(row)
            specialist['configuration'] = json.loads(specialist['configuration']) if specialist['configuration'] else {}
            specialist['is_active'] = bool(specialist['is_active'])
            return specialist
        return None
    
    def update_specialist(self, specialist_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing specialist."""
        # Build update query dynamically
        allowed_fields = {'name', 'category', 'description', 'prompt_template', 'configuration', 'is_active'}
        update_fields = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                if field == 'configuration':
                    values.append(json.dumps(value))
                elif field == 'is_active':
                    values.append(1 if value else 0)
                else:
                    values.append(value)
        
        if not update_fields:
            return False
        
        # Always update updated_at
        update_fields.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(specialist_id)
        
        query = f"UPDATE specialists SET {', '.join(update_fields)} WHERE id = ?"
        
        with self.connection_manager.transaction() as conn:
            cursor = conn.execute(query, values)
            return cursor.rowcount > 0
    
    def delete_specialist(self, specialist_id: str) -> bool:
        """Delete a specialist."""
        with self.connection_manager.transaction() as conn:
            cursor = conn.execute("DELETE FROM specialists WHERE id = ?", (specialist_id,))
            return cursor.rowcount > 0
    
    def list_specialists(self, 
                        category: Optional[str] = None,
                        active_only: bool = True,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List specialists with optional filtering."""
        query = "SELECT * FROM specialists WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if active_only:
            query += " AND is_active = 1"
        
        query += " ORDER BY name"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        if offset:
            query += " OFFSET ?"
            params.append(offset)
        
        rows = self.connection_manager.execute(query, params)
        
        specialists = []
        for row in rows:
            specialist = dict(row)
            specialist['configuration'] = json.loads(specialist['configuration']) if specialist['configuration'] else {}
            specialist['is_active'] = bool(specialist['is_active'])
            specialists.append(specialist)
        
        return specialists
    
    def get_specialist_categories(self) -> List[str]:
        """Get all unique specialist categories."""
        rows = self.connection_manager.execute(
            "SELECT DISTINCT category FROM specialists ORDER BY category"
        )
        return [row['category'] for row in rows]
    
    def save_specialist_template(self, template_name: str, 
                               template_data: Dict[str, Any]) -> bool:
        """Save a specialist template for reuse."""
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            # Use INSERT OR REPLACE for upsert behavior
            conn.execute("""
                INSERT OR REPLACE INTO specialist_templates (
                    name, category, template_data, description,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM specialist_templates WHERE name = ?), ?),
                    ?)
            """, (
                template_name,
                template_data.get('category', 'general'),
                json.dumps(template_data),
                template_data.get('description'),
                template_name, now,
                now
            ))
        
        return True
    
    def get_specialist_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specialist template by name."""
        row = self.connection_manager.execute_one(
            "SELECT * FROM specialist_templates WHERE name = ?",
            (template_name,)
        )
        
        if row:
            template = dict(row)
            template['template_data'] = json.loads(template['template_data'])
            return template
        return None
    
    def list_specialist_templates(self) -> List[Dict[str, Any]]:
        """List all available specialist templates."""
        rows = self.connection_manager.execute(
            "SELECT * FROM specialist_templates ORDER BY name"
        )
        
        templates = []
        for row in rows:
            template = dict(row)
            template['template_data'] = json.loads(template['template_data'])
            templates.append(template)
        
        return templates
    
    def record_specialist_usage(self, specialist_id: str, task_id: str,
                              usage_data: Dict[str, Any]) -> bool:
        """Record usage of a specialist for analytics."""
        usage_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self.connection_manager.transaction() as conn:
            conn.execute("""
                INSERT INTO specialist_usage (
                    id, specialist_id, task_id, usage_data, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                usage_id, specialist_id, task_id,
                json.dumps(usage_data), now
            ))
        
        return True
    
    def get_specialist_metrics(self, specialist_id: Optional[str] = None) -> Dict[str, Any]:
        """Get usage metrics for specialists."""
        if specialist_id:
            # Get metrics for specific specialist
            usage_count_row = self.connection_manager.execute_one(
                "SELECT COUNT(*) as count FROM specialist_usage WHERE specialist_id = ?",
                (specialist_id,)
            )
            
            # Get recent usage
            recent_usage = self.connection_manager.execute(
                """SELECT * FROM specialist_usage 
                   WHERE specialist_id = ? 
                   ORDER BY created_at DESC 
                   LIMIT 10""",
                (specialist_id,)
            )
            
            return {
                'specialist_id': specialist_id,
                'total_usage_count': usage_count_row['count'] if usage_count_row else 0,
                'recent_usage': [dict(row) for row in recent_usage]
            }
        else:
            # Get overall metrics
            usage_by_specialist = self.connection_manager.execute("""
                SELECT s.id, s.name, s.category, COUNT(u.id) as usage_count
                FROM specialists s
                LEFT JOIN specialist_usage u ON s.id = u.specialist_id
                GROUP BY s.id, s.name, s.category
                ORDER BY usage_count DESC
            """)
            
            return {
                'specialists_usage': [dict(row) for row in usage_by_specialist]
            }
    
    def get_recommended_specialist(self, task_type: str, 
                                 task_context: Dict[str, Any]) -> Optional[str]:
        """Get a recommendation for which specialist to use."""
        # Simple implementation: find specialist by matching category to task_type
        # In a real implementation, this could use ML or more sophisticated matching
        
        # First try exact match
        row = self.connection_manager.execute_one(
            "SELECT id FROM specialists WHERE category = ? AND is_active = 1 LIMIT 1",
            (task_type,)
        )
        
        if row:
            return row['id']
        
        # Fall back to general category
        row = self.connection_manager.execute_one(
            "SELECT id FROM specialists WHERE category = 'general' AND is_active = 1 LIMIT 1"
        )
        
        return row['id'] if row else None