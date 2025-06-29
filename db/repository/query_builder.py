"""
Query Builder Module - Complex query operations and filtering for Generic Tasks

This module provides advanced query capabilities including:
- Flexible task filtering with multiple criteria
- Subtree and ancestor queries
- Attribute-based searching
- Efficient pagination and result limiting
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.sql import text

from ...orchestrator.generic_models import GenericTask
from .converters import row_to_task


async def query_tasks(repo_instance, filters: Dict[str, Any], 
                     order_by: Optional[str] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> List[GenericTask]:
    """Query tasks with flexible filtering.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        filters: Dict of field names to values/conditions
        order_by: Field to order by (prefix with - for DESC)
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List of matching tasks
    """
    async with repo_instance.get_session() as session:
        # Build WHERE clause
        where_clauses = ["deleted_at IS NULL"]
        params = {}
        
        for field, value in filters.items():
            if field == "status":
                where_clauses.append("status = :status")
                params["status"] = value
            elif field == "lifecycle_stage":
                where_clauses.append("lifecycle_stage = :lifecycle_stage")
                params["lifecycle_stage"] = value
            elif field == "task_type":
                where_clauses.append("task_type = :task_type")
                params["task_type"] = value
            elif field == "specialist_type":
                where_clauses.append("specialist_type = :specialist_type")
                params["specialist_type"] = value
            elif field == "parent_task_id":
                if value is None:
                    where_clauses.append("parent_task_id IS NULL")
                else:
                    where_clauses.append("parent_task_id = :parent_task_id")
                    params["parent_task_id"] = value
            elif field == "created_after":
                where_clauses.append("created_at > :created_after")
                params["created_after"] = value
            elif field == "completed":
                if value:
                    where_clauses.append("status = 'completed'")
                else:
                    where_clauses.append("status != 'completed'")
        
        # Build query
        query = f"""
            SELECT * FROM generic_tasks
            WHERE {' AND '.join(where_clauses)}
        """
        
        # Add ORDER BY
        if order_by:
            if order_by.startswith('-'):
                query += f" ORDER BY {order_by[1:]} DESC"
            else:
                query += f" ORDER BY {order_by}"
        else:
            query += " ORDER BY created_at DESC"
        
        # Add LIMIT/OFFSET
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        result = await session.execute(text(query), params)
        
        from .helpers import load_attributes
        
        tasks = []
        for row in result:
            task = row_to_task(dict(row))
            # Load minimal related data
            task.attributes = await load_attributes(session, task.task_id)
            tasks.append(task)
        
        return tasks


async def search_by_attribute(repo_instance, attribute_name: str, 
                             attribute_value: str,
                             indexed_only: bool = True) -> List[GenericTask]:
    """Search tasks by attribute value.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        attribute_name: Name of the attribute
        attribute_value: Value to search for
        indexed_only: Only search indexed attributes
        
    Returns:
        List of tasks with matching attribute
    """
    async with repo_instance.get_session() as session:
        query = """
            SELECT DISTINCT t.*
            FROM generic_tasks t
            JOIN task_attributes a ON t.task_id = a.task_id
            WHERE a.attribute_name = :name
            AND a.attribute_value = :value
            AND t.deleted_at IS NULL
        """
        
        if indexed_only:
            query += " AND a.is_indexed = 1"
        
        result = await session.execute(text(query), {
            "name": attribute_name,
            "value": attribute_value
        })
        
        from .helpers import load_attributes
        
        tasks = []
        for row in result:
            task = row_to_task(dict(row))
            task.attributes = await load_attributes(session, task.task_id)
            tasks.append(task)
        
        return tasks


async def get_subtree(repo_instance, task_id: str, max_depth: Optional[int] = None) -> List[GenericTask]:
    """Get all descendants of a task.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task_id: The root task ID
        max_depth: Maximum depth to traverse (None for unlimited)
        
    Returns:
        List of tasks in the subtree
    """
    async with repo_instance.get_session() as session:
        # Get the root task's hierarchy path
        root_stmt = text("""
            SELECT hierarchy_path, hierarchy_level 
            FROM generic_tasks 
            WHERE task_id = :task_id AND deleted_at IS NULL
        """)
        
        result = await session.execute(root_stmt, {"task_id": task_id})
        root = result.fetchone()
        
        if not root:
            return []
        
        root_path = root['hierarchy_path']
        root_level = root['hierarchy_level']
        
        # Build query for descendants
        query = """
            SELECT * FROM generic_tasks 
            WHERE hierarchy_path LIKE :path_pattern 
            AND hierarchy_path != :root_path
            AND deleted_at IS NULL
        """
        
        params = {
            "path_pattern": f"{root_path}/%",
            "root_path": root_path
        }
        
        if max_depth is not None:
            query += " AND hierarchy_level <= :max_level"
            params["max_level"] = root_level + max_depth
        
        query += " ORDER BY hierarchy_level, position_in_parent"
        
        result = await session.execute(text(query), params)
        tasks = []
        
        from .helpers import load_attributes, load_dependencies
        
        for row in result:
            task = row_to_task(dict(row))
            # Load related data
            task.attributes = await load_attributes(session, task.task_id)
            task.dependencies = await load_dependencies(session, task.task_id)
            tasks.append(task)
        
        return tasks


async def get_ancestors(repo_instance, task_id: str) -> List[GenericTask]:
    """Get all ancestors of a task.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        task_id: The task ID
        
    Returns:
        List of ancestor tasks from root to parent
    """
    async with repo_instance.get_session() as session:
        # Get task's hierarchy path
        stmt = text("""
            SELECT hierarchy_path FROM generic_tasks 
            WHERE task_id = :task_id AND deleted_at IS NULL
        """)
        
        result = await session.execute(stmt, {"task_id": task_id})
        row = result.fetchone()
        
        if not row:
            return []
        
        # Parse hierarchy path to get ancestor IDs
        path_parts = row['hierarchy_path'].strip('/').split('/')
        if len(path_parts) <= 1:
            return []  # No ancestors
        
        # Remove the task itself
        ancestor_ids = path_parts[:-1]
        
        # Load ancestors
        ancestors = []
        for ancestor_id in ancestor_ids:
            task = await repo_instance.get_task(ancestor_id)
            if task:
                ancestors.append(task)
        
        return ancestors