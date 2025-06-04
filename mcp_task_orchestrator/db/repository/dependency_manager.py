"""
Dependency Manager Module - Task dependency operations and cycle detection

This module manages task dependencies including:
- Adding and removing dependencies
- Checking dependency satisfaction
- Detecting and preventing dependency cycles
- Building dependency graphs
- Updating dependency statuses
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ...orchestrator.generic_models import (
    TaskDependency, TaskStatus, DependencyStatus, EventType, EventCategory
)
from .base import CycleDetectedError
from .converters import row_to_dependency


async def add_dependency(repo_instance, dependency: TaskDependency) -> TaskDependency:
    """Add a dependency between tasks.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        dependency: The dependency to add
        
    Returns:
        The created dependency
        
    Raises:
        ValueError: If dependency would create a cycle
    """
    async with repo_instance.get_session() as session:
        # Check for cycles
        if await would_create_cycle(
            session,
            dependency.dependent_task_id,
            dependency.prerequisite_task_id
        ):
            raise CycleDetectedError(
                f"Dependency from {dependency.prerequisite_task_id} to "
                f"{dependency.dependent_task_id} would create a cycle"
            )
        
        # Save dependency
        from .helpers import save_dependency, record_event
        await save_dependency(session, dependency)
        
        # Record event
        await record_event(
            session, dependency.dependent_task_id,
            EventType.DEPENDENCY_ADDED, EventCategory.DATA, "system",
            {
                "prerequisite_task_id": dependency.prerequisite_task_id,
                "dependency_type": dependency.dependency_type
            }
        )
        
        return dependency


async def check_dependencies(repo_instance, task_id: str) -> Tuple[bool, List[TaskDependency]]:
    """Check if a task's dependencies are satisfied.
    
    Args:
        repo_instance: Repository instance for accessing session
        task_id: The task to check
        
    Returns:
        Tuple of (all_satisfied, unsatisfied_dependencies)
    """
    async with repo_instance.get_session() as session:
        # Get all mandatory dependencies
        stmt = text("""
            SELECT d.*, t.status as prerequisite_status
            FROM task_dependencies d
            JOIN generic_tasks t ON d.prerequisite_task_id = t.task_id
            WHERE d.dependent_task_id = :task_id
            AND d.is_mandatory = 1
            AND d.dependency_status != 'satisfied'
            AND d.dependency_status != 'waived'
        """)
        
        result = await session.execute(stmt, {"task_id": task_id})
        unsatisfied = []
        
        for row in result:
            dep = row_to_dependency(dict(row))
            
            # Check if can be auto-satisfied
            if dep.auto_satisfy and dep.can_satisfy(TaskStatus(row['prerequisite_status'])):
                # Auto-satisfy the dependency
                await update_dependency_status(
                    session, dep.dependency_id,
                    DependencyStatus.SATISFIED
                )
            else:
                unsatisfied.append(dep)
        
        return len(unsatisfied) == 0, unsatisfied


async def get_dependency_graph(repo_instance, root_task_id: Optional[str] = None) -> Dict[str, List[str]]:
    """Get the dependency graph.
    
    Args:
        repo_instance: Repository instance for accessing session
        root_task_id: If provided, only include tasks in this subtree
        
    Returns:
        Dict mapping task_id to list of prerequisite task_ids
    """
    async with repo_instance.get_session() as session:
        query = """
            SELECT dependent_task_id, prerequisite_task_id
            FROM task_dependencies
            WHERE dependency_status != 'waived'
        """
        
        params = {}
        
        if root_task_id:
            # Filter to subtree
            query += """
                AND dependent_task_id IN (
                    SELECT task_id FROM generic_tasks
                    WHERE hierarchy_path LIKE :path_pattern
                )
            """
            root = await repo_instance.get_task(root_task_id)
            if root:
                params["path_pattern"] = f"{root.hierarchy_path}%"
        
        result = await session.execute(text(query), params)
        
        graph = {}
        for row in result:
            task_id = row['dependent_task_id']
            prereq = row['prerequisite_task_id']
            
            if task_id not in graph:
                graph[task_id] = []
            graph[task_id].append(prereq)
        
        return graph


async def would_create_cycle(session: AsyncSession,
                           dependent_id: str, prerequisite_id: str) -> bool:
    """Check if adding a dependency would create a cycle."""
    # Use recursive CTE to check for cycles
    stmt = text("""
        WITH RECURSIVE dep_chain(task_id) AS (
            SELECT :start_id
            UNION
            SELECT d.prerequisite_task_id
            FROM task_dependencies d
            JOIN dep_chain c ON d.dependent_task_id = c.task_id
            WHERE d.dependency_status != 'waived'
        )
        SELECT 1 FROM dep_chain WHERE task_id = :end_id
    """)
    
    result = await session.execute(stmt, {
        "start_id": prerequisite_id,
        "end_id": dependent_id
    })
    
    return result.fetchone() is not None


async def update_dependency_status(session: AsyncSession,
                                 dependency_id: int, status: DependencyStatus):
    """Update dependency status."""
    stmt = text("""
        UPDATE task_dependencies 
        SET dependency_status = :status, satisfied_at = :satisfied_at
        WHERE dependency_id = :dep_id
    """)
    
    await session.execute(stmt, {
        "dep_id": dependency_id,
        "status": status,
        "satisfied_at": datetime.now().isoformat() if status == DependencyStatus.SATISFIED else None
    })