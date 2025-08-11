"""
Generic Task Repository - Database operations for the Generic Task Model

This module provides a repository pattern implementation for managing Generic Tasks
with async database operations, efficient queries, and comprehensive error handling.

NOTE: This module is being refactored. The base class and imports have been moved to
repository/base.py to reduce file size and improve maintainability.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import logging

# Import base repository and common items from the new modular structure
from .repository.base import (
    CycleDetectedError, 
    asynccontextmanager, AsyncSession,
    select, delete, update, and_, or_, func,
    SQLAlchemyError, IntegrityError, text,
    selectinload, joinedload
)

# Import the abstract repository interface
from ..domain.repositories.task_repository import TaskRepository

# Import converter functions 
from .repository.converters import (
    row_to_task, row_to_attribute, row_to_dependency, 
    row_to_artifact, row_to_event, row_to_template
)

# Import models that are used throughout
from ..orchestrator.generic_models import (
    Task as GenericTask, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact,
    TaskTemplate, TemplateParameter
)
from ..domain.value_objects.enums import (
    TaskType, TaskStatus, LifecycleStage, DependencyType, DependencyStatus,
    EventType, EventCategory, AttributeType, ArtifactType
)

logger = logging.getLogger(__name__)


# Extend the base repository with all the methods
# (This is temporary during refactoring - methods will be moved to appropriate modules)
class GenericTaskRepository(TaskRepository):
    
    # ============================================
    # Task CRUD Operations (delegated to crud_operations)
    # ============================================
    
    async def create_task(self, task: GenericTask) -> GenericTask:
        """Create a new task in the database."""
        from .repository.crud_operations import create_task
        return await create_task(self, task)
    
    async def get_task(self, task_id: str, include_children: bool = False,
                       include_events: bool = False) -> Optional[GenericTask]:
        """Retrieve a task by ID."""
        from .repository.crud_operations import get_task
        return await get_task(self, task_id, include_children, include_events)
    
    async def update_task(self, task: GenericTask) -> GenericTask:
        """Update an existing task."""
        from .repository.crud_operations import update_task
        return await update_task(self, task)
    
    async def delete_task(self, task_id: str, hard_delete: bool = False) -> bool:
        """Delete a task (soft delete by default)."""
        from .repository.crud_operations import delete_task
        return await delete_task(self, task_id, hard_delete)
    
    # ============================================
    # Hierarchy Operations
    # ============================================
    
    async def get_subtree(self, task_id: str, max_depth: Optional[int] = None) -> List[GenericTask]:
        """Get all descendants of a task."""
        from .repository.query_builder import get_subtree
        return await get_subtree(self, task_id, max_depth)
    
    async def get_ancestors(self, task_id: str) -> List[GenericTask]:
        """Get all ancestors of a task."""
        from .repository.query_builder import get_ancestors
        return await get_ancestors(self, task_id)
    
    async def move_task(self, task_id: str, new_parent_id: Optional[str],
                       position: Optional[int] = None) -> GenericTask:
        """Move a task to a new parent.
        
        Args:
            task_id: The task to move
            new_parent_id: The new parent (None for root)
            position: Position among siblings (None for last)
            
        Returns:
            The updated task
            
        Raises:
            ValueError: If move would create a cycle
        """
        async with self.get_session() as session:
            # Get the task and its subtree
            task = await self.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Check for cycles
            if new_parent_id:
                ancestors = await self.get_ancestors(new_parent_id)
                if any(a.task_id == task_id for a in ancestors):
                    raise ValueError("Move would create a cycle")
            
            # Calculate new hierarchy path
            if new_parent_id:
                parent = await self.get_task(new_parent_id)
                if not parent:
                    raise ValueError(f"Parent task {new_parent_id} not found")
                new_path = f"{parent.hierarchy_path}/{task_id}"
                new_level = parent.hierarchy_level + 1
            else:
                new_path = f"/{task_id}"
                new_level = 0
            
            # Get old path for updating descendants
            old_path = task.hierarchy_path
            
            # Update the task
            update_task_stmt = text("""
                UPDATE generic_tasks SET
                    parent_task_id = :parent_id,
                    hierarchy_path = :new_path,
                    hierarchy_level = :new_level,
                    position_in_parent = :position,
                    updated_at = :updated_at
                WHERE task_id = :task_id
            """)
            
            await session.execute(update_task_stmt, {
                "task_id": task_id,
                "parent_id": new_parent_id,
                "new_path": new_path,
                "new_level": new_level,
                "position": position or 0,
                "updated_at": datetime.now().isoformat()
            })
            
            # Update all descendants
            update_descendants_stmt = text("""
                UPDATE generic_tasks SET
                    hierarchy_path = :new_prefix || substr(hierarchy_path, :old_prefix_len),
                    hierarchy_level = hierarchy_level + :level_diff,
                    updated_at = :updated_at
                WHERE hierarchy_path LIKE :old_pattern
                AND task_id != :task_id
            """)
            
            await session.execute(update_descendants_stmt, {
                "new_prefix": new_path,
                "old_prefix_len": len(old_path) + 1,
                "level_diff": new_level - task.hierarchy_level,
                "updated_at": datetime.now().isoformat(),
                "old_pattern": f"{old_path}/%",
                "task_id": task_id
            })
            
            logger.info(f"Moved task {task_id} to parent {new_parent_id}")
            
            # Return updated task
            return await self.get_task(task_id)
    
    # ============================================
    # Dependency Operations (delegated to dependency_manager)
    # ============================================
    
    async def add_dependency(self, dependency: TaskDependency) -> TaskDependency:
        """Add a dependency between tasks."""
        from .repository.dependency_manager import add_dependency
        return await add_dependency(self, dependency)
    
    async def check_dependencies(self, task_id: str) -> Tuple[bool, List[TaskDependency]]:
        """Check if a task's dependencies are satisfied."""
        from .repository.dependency_manager import check_dependencies
        return await check_dependencies(self, task_id)
    
    async def get_dependency_graph(self, root_task_id: Optional[str] = None) -> Dict[str, List[str]]:
        """Get the dependency graph."""
        from .repository.dependency_manager import get_dependency_graph
        return await get_dependency_graph(self, root_task_id)
    
    # ============================================
    # Query Operations
    # ============================================
    
    async def query_tasks(self, filters: Dict[str, Any], 
                         order_by: Optional[str] = None,
                         limit: Optional[int] = None,
                         offset: Optional[int] = None) -> List[GenericTask]:
        """Query tasks with flexible filtering."""
        from .repository.query_builder import query_tasks
        return await query_tasks(self, filters, order_by, limit, offset)
    
    async def search_by_attribute(self, attribute_name: str, 
                                 attribute_value: str,
                                 indexed_only: bool = True) -> List[GenericTask]:
        """Search tasks by attribute value."""
        from .repository.query_builder import search_by_attribute
        return await search_by_attribute(self, attribute_name, attribute_value, indexed_only)
    
    # ============================================
    # Template Operations
    # ============================================
    
    async def save_template(self, template: TaskTemplate) -> TaskTemplate:
        """Save a task template."""
        from .repository.template_operations import save_template
        return await save_template(self, template)
    
    async def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a template by ID."""
        from .repository.template_operations import get_template
        return await get_template(self, template_id)
    
    # ============================================
    # Helper Methods (Delegated to helpers module)
    # ============================================
    
    async def _save_attribute(self, session: AsyncSession, task_id: str, attr: TaskAttribute):
        """Save a task attribute."""
        from .repository.helpers import save_attribute
        return await save_attribute(session, task_id, attr)
    
    async def _save_dependency(self, session: AsyncSession, dep: TaskDependency):
        """Save a task dependency."""
        from .repository.helpers import save_dependency
        return await save_dependency(session, dep)
    
    async def _save_artifact(self, session: AsyncSession, artifact: TaskArtifact):
        """Save a task artifact."""
        from .repository.helpers import save_artifact
        return await save_artifact(session, artifact)
    
    async def _record_event(self, session: AsyncSession, task_id: str,
                           event_type: EventType, category: EventCategory,
                           triggered_by: str, data: Optional[Dict] = None):
        """Record a task event."""
        from .repository.helpers import record_event
        return await record_event(session, task_id, event_type, category, triggered_by, data)
    
    async def _load_attributes(self, session: AsyncSession, task_id: str) -> List[TaskAttribute]:
        """Load attributes for a task."""
        from .repository.helpers import load_attributes
        return await load_attributes(session, task_id)
    
    async def _load_dependencies(self, session: AsyncSession, task_id: str) -> List[TaskDependency]:
        """Load dependencies for a task."""
        from .repository.helpers import load_dependencies
        return await load_dependencies(session, task_id)
    
    async def _load_artifacts(self, session: AsyncSession, task_id: str) -> List[TaskArtifact]:
        """Load artifacts for a task."""
        from .repository.helpers import load_artifacts
        return await load_artifacts(session, task_id)
    
    async def _load_events(self, session: AsyncSession, task_id: str) -> List[TaskEvent]:
        """Load events for a task."""
        from .repository.helpers import load_events
        return await load_events(session, task_id)
    
    async def _load_children(self, session: AsyncSession, parent_id: str) -> List[GenericTask]:
        """Load child tasks."""
        from .repository.helpers import load_children
        return await load_children(self, session, parent_id)
    
    
    # ============================================
    # Abstract method implementations (sync wrappers)
    # ============================================
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task (sync wrapper)."""
        import uuid
        task_id = task_data.get('task_id') or str(uuid.uuid4())
        
        # Simple placeholder implementation
        # In a real implementation, this would persist to database
        logger.info(f"Creating task with ID: {task_id}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID (sync wrapper)."""
        # Simple placeholder implementation
        logger.info(f"Getting task with ID: {task_id}")
        return None  # Would return actual task data from database

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing task (sync wrapper)."""
        logger.info(f"Updating task {task_id} with {updates}")
        return True  # Would update actual task in database

    def delete_task(self, task_id: str) -> bool:
        """Delete a task (sync wrapper)."""
        logger.info(f"Deleting task with ID: {task_id}")
        return True  # Would delete actual task from database

    def list_tasks(self, 
                   session_id: Optional[str] = None,
                   parent_task_id: Optional[str] = None,
                   status: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List tasks with optional filtering (sync wrapper)."""
        logger.info(f"Listing tasks with filters: session_id={session_id}, parent_task_id={parent_task_id}, status={status}")
        return []  # Would return actual task list from database

    def get_subtasks(self, parent_task_id: str) -> List[Dict[str, Any]]:
        """Get all subtasks of a parent task (sync wrapper)."""
        logger.info(f"Getting subtasks for parent: {parent_task_id}")
        return []  # Would return subtasks from database

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update the status of a task (sync wrapper)."""
        logger.info(f"Updating task {task_id} status to: {status}")
        return True  # Would update status in database

    def add_task_artifact(self, task_id: str, artifact: Dict[str, Any]) -> bool:
        """Add an artifact to a task (sync wrapper)."""
        logger.info(f"Adding artifact to task {task_id}: {artifact.get('name', 'unnamed')}")
        return True  # Would add artifact to database

    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a task (sync wrapper)."""
        logger.info(f"Getting artifacts for task: {task_id}")
        return []  # Would return artifacts from database

    def search_tasks(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search tasks by text query (sync wrapper)."""
        logger.info(f"Searching tasks with query: {query}")
        return []  # Would return search results from database

    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get task IDs that this task depends on (sync wrapper)."""
        logger.info(f"Getting dependencies for task: {task_id}")
        return []  # Would return dependency IDs from database

    def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency between tasks (sync wrapper)."""
        logger.info(f"Adding dependency: {task_id} depends on {dependency_id}")
        return True  # Would add dependency to database

    def cleanup_old_tasks(self, older_than: datetime, 
                         exclude_sessions: Optional[List[str]] = None) -> int:
        """Clean up tasks older than a specified date (sync wrapper)."""
        logger.info(f"Cleaning up tasks older than: {older_than}")
        return 0  # Would return number of deleted tasks

    def get_task_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics about tasks (sync wrapper)."""
        logger.info(f"Getting task metrics for session: {session_id}")
        return {
            'total_tasks': 0,
            'status_counts': {},
            'type_counts': {},
            'session_id': session_id
        }  # Would return actual metrics from database

    async def dispose(self):
        """Clean up database connections."""
        if hasattr(self, 'async_engine'):
            await self.async_engine.dispose()