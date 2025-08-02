"""
Async SQLite implementation of TaskRepository.

This module provides an async SQLite implementation of the TaskRepository
interface using the new database adapter system.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from ....domain.repositories.async_task_repository import AsyncTaskRepository
from ..base import OperationalDatabaseAdapter

logger = logging.getLogger(__name__)


class AsyncSQLiteTaskRepository(AsyncTaskRepository):
    """Async SQLite implementation of the TaskRepository interface."""
    
    def __init__(self, db_adapter: OperationalDatabaseAdapter):
        """
        Initialize the async SQLite task repository.
        
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
                -- Tasks table
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    parent_task_id TEXT,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
                );
                
                -- Task artifacts table
                CREATE TABLE IF NOT EXISTS task_artifacts (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                );
                
                -- Task dependencies table
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    task_id TEXT NOT NULL,
                    dependency_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (task_id, dependency_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (dependency_id) REFERENCES tasks(id) ON DELETE CASCADE
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_tasks_session ON tasks(session_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_task_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at);
                CREATE INDEX IF NOT EXISTS idx_artifacts_task ON task_artifacts(task_id);
                CREATE INDEX IF NOT EXISTS idx_dependencies_task ON task_dependencies(task_id);
            """
            
            # Use the adapter's create_tables method if available, otherwise execute directly
            if hasattr(self.db_adapter, 'create_tables'):
                await self.db_adapter.create_tables(schema)
            else:
                # Execute each statement separately for compatibility
                statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
                for statement in statements:
                    await self.db_adapter.execute(statement)
            
            self._tables_created = True
            logger.info("Task repository tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create task repository tables: {e}")
            raise
    
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task asynchronously."""
        await self._ensure_tables()
        
        task_id = task_data.get('id', str(uuid.uuid4()))
        now = datetime.utcnow().isoformat()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT INTO tasks (
                        id, session_id, parent_task_id, type, status,
                        title, description, metadata, created_at, updated_at
                    ) VALUES (:id, :session_id, :parent_task_id, :type, :status, :title, :description, :metadata, :created_at, :updated_at)
                """, {
                    'id': task_id,
                    'session_id': task_data.get('session_id'),
                    'parent_task_id': task_data.get('parent_task_id'),
                    'type': task_data.get('type', 'generic'),
                    'status': task_data.get('status', 'pending'),
                    'title': task_data.get('title', ''),
                    'description': task_data.get('description', ''),
                    'metadata': json.dumps(task_data.get('metadata', {})),
                    'created_at': now,
                    'updated_at': now
                })
            
            logger.info(f"Created task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID asynchronously."""
        await self._ensure_tables()
        
        try:
            result = await self.db_adapter.execute_one(
                "SELECT * FROM tasks WHERE id = :id",
                {'id': task_id}
            )
            
            if result:
                # Parse metadata JSON
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                else:
                    result['metadata'] = {}
                
                # Get artifacts
                artifacts = await self.db_adapter.execute(
                    "SELECT * FROM task_artifacts WHERE task_id = ? ORDER BY created_at",
                    {'task_id': task_id}
                )
                
                # Parse artifact metadata
                for artifact in artifacts:
                    if artifact['metadata']:
                        artifact['metadata'] = json.loads(artifact['metadata'])
                    else:
                        artifact['metadata'] = {}
                
                result['artifacts'] = artifacts
                
                # Get dependencies
                dependencies = await self.db_adapter.execute(
                    "SELECT dependency_id FROM task_dependencies WHERE task_id = ?",
                    {'task_id': task_id}
                )
                result['dependencies'] = [dep['dependency_id'] for dep in dependencies]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a task asynchronously."""
        await self._ensure_tables()
        
        try:
            # Build update query dynamically
            update_fields = []
            params = {'task_id': task_id}
            
            for field in ['session_id', 'parent_task_id', 'type', 'status', 'title', 'description']:
                if field in update_data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = update_data[field]
            
            if 'metadata' in update_data:
                update_fields.append("metadata = :metadata")
                params['metadata'] = json.dumps(update_data['metadata'])
            
            if 'completed_at' in update_data:
                update_fields.append("completed_at = :completed_at")
                params['completed_at'] = update_data['completed_at']
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = :updated_at")
            params['updated_at'] = datetime.utcnow().isoformat()
            
            if not update_fields:
                return False
            
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = :task_id"
            
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute(query, params)
            
            logger.info(f"Updated task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task asynchronously."""
        await self._ensure_tables()
        
        try:
            async with self.db_adapter.transaction() as tx:
                # Delete dependencies first
                await self.db_adapter.execute(
                    "DELETE FROM task_dependencies WHERE task_id = ? OR dependency_id = ?",
                    {'task_id': task_id, 'dependency_id': task_id}
                )
                
                # Delete artifacts (CASCADE should handle this, but explicit is better)
                await self.db_adapter.execute(
                    "DELETE FROM task_artifacts WHERE task_id = ?",
                    {'task_id': task_id}
                )
                
                # Delete the task
                await self.db_adapter.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    {'id': task_id}
                )
            
            logger.info(f"Deleted task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise
    
    async def list_tasks(
        self,
        session_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering asynchronously."""
        await self._ensure_tables()
        
        try:
            # Build query with filters
            where_clauses = []
            params = {}
            
            if session_id is not None:
                where_clauses.append("session_id = :session_id")
                params['session_id'] = session_id
            
            if parent_task_id is not None:
                where_clauses.append("parent_task_id = :parent_task_id")
                params['parent_task_id'] = parent_task_id
            
            if status is not None:
                where_clauses.append("status = :status")
                params['status'] = status
            
            where_clause = ""
            if where_clauses:
                where_clause = f"WHERE {' AND '.join(where_clauses)}"
            
            limit_clause = ""
            if limit is not None:
                limit_clause = f"LIMIT {limit}"
                if offset is not None:
                    limit_clause += f" OFFSET {offset}"
            
            query = f"""
                SELECT * FROM tasks 
                {where_clause}
                ORDER BY created_at DESC
                {limit_clause}
            """
            
            results = await self.db_adapter.execute(query, params)
            
            # Parse metadata for each task
            for task in results:
                if task['metadata']:
                    task['metadata'] = json.loads(task['metadata'])
                else:
                    task['metadata'] = {}
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise
    
    async def add_artifact(self, task_id: str, artifact_data: Dict[str, Any]) -> str:
        """Add an artifact to a task asynchronously."""
        await self._ensure_tables()
        
        artifact_id = artifact_data.get('id', str(uuid.uuid4()))
        now = datetime.utcnow().isoformat()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT INTO task_artifacts (
                        id, task_id, type, name, content, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, {
                    'id': artifact_id,
                    'task_id': task_id,
                    'type': artifact_data.get('type', 'file'),
                    'name': artifact_data.get('name'),
                    'content': artifact_data.get('content'),
                    'metadata': json.dumps(artifact_data.get('metadata', {})),
                    'created_at': now
                })
            
            logger.info(f"Added artifact {artifact_id} to task {task_id}")
            return artifact_id
            
        except Exception as e:
            logger.error(f"Failed to add artifact to task {task_id}: {e}")
            raise
    
    async def add_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency between tasks asynchronously."""
        await self._ensure_tables()
        
        try:
            async with self.db_adapter.transaction() as tx:
                await self.db_adapter.execute("""
                    INSERT OR IGNORE INTO task_dependencies (
                        task_id, dependency_id, created_at
                    ) VALUES (?, ?, ?)
                """, {
                    'task_id': task_id,
                    'dependency_id': dependency_id,
                    'created_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Added dependency {dependency_id} to task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add dependency to task {task_id}: {e}")
            raise
    
    async def get_task_hierarchy(self, root_task_id: str) -> List[Dict[str, Any]]:
        """Get task hierarchy starting from a root task asynchronously."""
        await self._ensure_tables()
        
        try:
            # Recursive CTE to get task hierarchy
            query = """
                WITH RECURSIVE task_hierarchy AS (
                    -- Base case: root task
                    SELECT id, parent_task_id, title, status, type, 0 as level
                    FROM tasks 
                    WHERE id = :root_task_id
                    
                    UNION ALL
                    
                    -- Recursive case: child tasks
                    SELECT t.id, t.parent_task_id, t.title, t.status, t.type, th.level + 1
                    FROM tasks t
                    INNER JOIN task_hierarchy th ON t.parent_task_id = th.id
                )
                SELECT * FROM task_hierarchy ORDER BY level, id
            """
            
            results = await self.db_adapter.execute(query, {'root_task_id': root_task_id})
            return results
            
        except Exception as e:
            logger.error(f"Failed to get task hierarchy for {root_task_id}: {e}")
            raise
    
    async def get_subtasks(self, parent_task_id: str) -> List[Dict[str, Any]]:
        """Get all subtasks of a parent task asynchronously."""
        return await self.list_tasks(parent_task_id=parent_task_id)
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update the status of a task asynchronously."""
        return await self.update_task(task_id, {'status': status})
    
    async def add_task_artifact(self, task_id: str, artifact: Dict[str, Any]) -> bool:
        """Add an artifact to a task asynchronously."""
        try:
            await self.add_artifact(task_id, artifact)
            return True
        except Exception:
            return False
    
    async def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a task asynchronously."""
        await self._ensure_tables()
        
        try:
            artifacts = await self.db_adapter.execute(
                "SELECT * FROM task_artifacts WHERE task_id = :task_id ORDER BY created_at",
                {'task_id': task_id}
            )
            
            # Parse artifact metadata
            for artifact in artifacts:
                if artifact['metadata']:
                    artifact['metadata'] = json.loads(artifact['metadata'])
                else:
                    artifact['metadata'] = {}
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Failed to get artifacts for task {task_id}: {e}")
            raise
    
    async def search_tasks(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search tasks by text query asynchronously."""
        await self._ensure_tables()
        
        try:
            # Simple text search in title and description
            search_fields = fields or ['title', 'description']
            
            where_clauses = []
            params = {}
            
            for i, field in enumerate(search_fields):
                if field in ['title', 'description']:
                    where_clauses.append(f"{field} LIKE :query_{i}")
                    params[f'query_{i}'] = f'%{query}%'
            
            if not where_clauses:
                return []
            
            where_clause = f"WHERE {' OR '.join(where_clauses)}"
            
            sql = f"""
                SELECT * FROM tasks 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            results = await self.db_adapter.execute(sql, params)
            
            # Parse metadata for each task
            for task in results:
                if task['metadata']:
                    task['metadata'] = json.loads(task['metadata'])
                else:
                    task['metadata'] = {}
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search tasks: {e}")
            raise
    
    async def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get task IDs that this task depends on asynchronously."""
        await self._ensure_tables()
        
        try:
            dependencies = await self.db_adapter.execute(
                "SELECT dependency_id FROM task_dependencies WHERE task_id = :task_id",
                {'task_id': task_id}
            )
            return [dep['dependency_id'] for dep in dependencies]
            
        except Exception as e:
            logger.error(f"Failed to get dependencies for task {task_id}: {e}")
            raise
    
    async def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency between tasks asynchronously."""
        try:
            await self.add_dependency(task_id, dependency_id)
            return True
        except Exception:
            return False
    
    async def cleanup_old_tasks(self, older_than: datetime, exclude_sessions: Optional[List[str]] = None) -> int:
        """Clean up tasks older than a specified date asynchronously."""
        await self._ensure_tables()
        
        try:
            # Build exclusion clause
            exclude_clause = ""
            params = {'older_than': older_than.isoformat()}
            
            if exclude_sessions:
                placeholders = ', '.join([f':session_{i}' for i in range(len(exclude_sessions))])
                exclude_clause = f"AND session_id NOT IN ({placeholders})"
                for i, session in enumerate(exclude_sessions):
                    params[f'session_{i}'] = session
            
            # Get tasks to delete
            old_tasks = await self.db_adapter.execute(f"""
                SELECT id FROM tasks 
                WHERE created_at < :older_than 
                {exclude_clause}
            """, params)
            
            if not old_tasks:
                return 0
            
            task_ids = [task['id'] for task in old_tasks]
            
            # Delete tasks and related data
            async with self.db_adapter.transaction() as tx:
                for task_id in task_ids:
                    await self.delete_task(task_id)
            
            logger.info(f"Cleaned up {len(task_ids)} old tasks")
            return len(task_ids)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")
            raise
    
    async def get_task_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics about tasks asynchronously."""
        await self._ensure_tables()
        
        try:
            where_clause = ""
            params = {}
            
            if session_id:
                where_clause = "WHERE session_id = :session_id"
                params['session_id'] = session_id
            
            # Get basic counts
            counts_result = await self.db_adapter.execute(f"""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM tasks 
                {where_clause}
                GROUP BY status
            """, params)
            
            status_counts = {row['status']: row['count'] for row in counts_result}
            
            # Get total count
            total_result = await self.db_adapter.execute_one(f"""
                SELECT COUNT(*) as total FROM tasks {where_clause}
            """, params)
            
            total_count = total_result['total'] if total_result else 0
            
            # Get date range
            date_range_result = await self.db_adapter.execute_one(f"""
                SELECT 
                    MIN(created_at) as earliest,
                    MAX(created_at) as latest
                FROM tasks 
                {where_clause}
            """, params)
            
            return {
                'total_tasks': total_count,
                'status_counts': status_counts,
                'date_range': {
                    'earliest': date_range_result['earliest'] if date_range_result else None,
                    'latest': date_range_result['latest'] if date_range_result else None
                },
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get task metrics: {e}")
            raise

    async def query_tasks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query tasks with advanced filtering and pagination asynchronously.
        
        This method implements comprehensive task querying with support for:
        - Multiple filter criteria (status, type, complexity, dates, etc.)
        - Text search across title and description
        - Pagination with configurable page size
        - Sorting by various fields
        - Inclusion/exclusion of archived tasks and subtasks
        """
        await self._ensure_tables()
        
        try:
            # Extract pagination parameters
            page = max(1, filters.get('page', 1))
            page_size = min(100, max(1, filters.get('page_size', 20)))  # Max 100, min 1
            offset = (page - 1) * page_size
            
            # Extract sorting parameters
            sort_by = filters.get('sort_by', 'created_at')
            sort_order = filters.get('sort_order', 'desc').upper()
            
            # Validate sort parameters
            valid_sort_fields = ['created_at', 'updated_at', 'title', 'status', 'type']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'
            if sort_order not in ['ASC', 'DESC']:
                sort_order = 'DESC'
            
            # Build WHERE clause and parameters
            where_clauses = []
            params = {}
            
            # Basic filters
            if filters.get('status'):
                where_clauses.append("status = :status")
                params['status'] = filters['status']
            
            if filters.get('task_type') or filters.get('type'):
                task_type = filters.get('task_type') or filters.get('type')
                where_clauses.append("type = :type")
                params['type'] = task_type
            
            if filters.get('session_id'):
                where_clauses.append("session_id = :session_id")
                params['session_id'] = filters['session_id']
            
            if filters.get('parent_task_id'):
                where_clauses.append("parent_task_id = :parent_task_id")
                params['parent_task_id'] = filters['parent_task_id']
            
            # Date filters
            if filters.get('created_after'):
                where_clauses.append("created_at >= :created_after")
                params['created_after'] = filters['created_after']
            
            if filters.get('created_before'):
                where_clauses.append("created_at <= :created_before")
                params['created_before'] = filters['created_before']
            
            if filters.get('updated_after'):
                where_clauses.append("updated_at >= :updated_after")
                params['updated_after'] = filters['updated_after']
            
            if filters.get('updated_before'):
                where_clauses.append("updated_at <= :updated_before")
                params['updated_before'] = filters['updated_before']
            
            # Text search across title and description
            if filters.get('search_query'):
                search_query = f"%{filters['search_query']}%"
                where_clauses.append("(title LIKE :search_query OR description LIKE :search_query)")
                params['search_query'] = search_query
            
            # Task ID filter (for specific task lookup)
            if filters.get('task_id'):
                where_clauses.append("id = :task_id")
                params['task_id'] = filters['task_id']
            
            # Dependency filters
            if filters.get('dependency_ids'):
                dependency_ids = filters['dependency_ids']
                if isinstance(dependency_ids, str):
                    dependency_ids = [dependency_ids]
                
                if dependency_ids:
                    placeholders = ', '.join([f':dep_{i}' for i in range(len(dependency_ids))])
                    where_clauses.append(f"""
                        id IN (
                            SELECT task_id FROM task_dependencies 
                            WHERE dependency_id IN ({placeholders})
                        )
                    """)
                    for i, dep_id in enumerate(dependency_ids):
                        params[f'dep_{i}'] = dep_id
            
            # Build complete WHERE clause
            where_clause = ""
            if where_clauses:
                where_clause = f"WHERE {' AND '.join(where_clauses)}"
            
            # Build ORDER BY clause
            order_clause = f"ORDER BY {sort_by} {sort_order}"
            
            # Build LIMIT clause
            limit_clause = f"LIMIT {page_size} OFFSET {offset}"
            
            # Execute count query for pagination
            count_query = f"SELECT COUNT(*) as total FROM tasks {where_clause}"
            count_result = await self.db_adapter.execute_one(count_query, params)
            total_count = count_result['total'] if count_result else 0
            
            # Calculate pagination info
            page_count = (total_count + page_size - 1) // page_size  # Ceiling division
            
            # Execute main query
            main_query = f"""
                SELECT * FROM tasks 
                {where_clause}
                {order_clause}
                {limit_clause}
            """
            
            results = await self.db_adapter.execute(main_query, params)
            
            # Parse metadata for each task
            for task in results:
                if task['metadata']:
                    try:
                        task['metadata'] = json.loads(task['metadata'])
                    except (json.JSONDecodeError, TypeError):
                        task['metadata'] = {}
                else:
                    task['metadata'] = {}
                
                # Get artifacts if requested
                if filters.get('include_artifacts', False):
                    artifacts = await self.get_task_artifacts(task['id'])
                    task['artifacts'] = artifacts
                else:
                    task['artifacts'] = []
                
                # Get dependencies if requested
                if filters.get('include_dependencies', False):
                    dependencies = await self.get_task_dependencies(task['id'])
                    task['dependencies'] = dependencies
                else:
                    task['dependencies'] = []
            
            # Build filters_applied summary
            filters_applied = {k: v for k, v in filters.items() 
                             if k not in ['page', 'page_size', 'sort_by', 'sort_order'] and v is not None}
            
            return {
                'tasks': results,
                'pagination': {
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'page_count': page_count,
                    'has_next': page < page_count,
                    'has_previous': page > 1
                },
                'filters_applied': filters_applied,
                'sorting': {
                    'sort_by': sort_by,
                    'sort_order': sort_order.lower()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to query tasks: {e}")
            raise