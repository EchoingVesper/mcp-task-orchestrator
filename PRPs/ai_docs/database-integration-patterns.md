
# Database Integration Patterns

**Purpose**: Essential patterns for async database operations with SQLite/aiosqlite, focusing on the repository pattern, clean architecture integration, and reliable connection management.

#
# Core Principles

#
## Database Architecture Standards

- **Always use async/await** for database operations to maintain non-blocking execution

- **Repository Pattern**: Abstract data access behind repository interfaces

- **Clean Architecture**: Domain entities should not depend on database implementation details

- **Connection Management**: Always use context managers for proper resource cleanup

- **Migration Safety**: Automatic migrations with rollback capabilities

#
# Connection Management Patterns

#
## Pattern: Async Database Connection Setup

```python

# PATTERN: Async database engine setup with proper configuration

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

class TaskRepository:
    """Repository with proper async connection management."""
    
    def __init__(self, db_url: str):
        """Initialize repository with async engine."""
        
# CRITICAL: Convert sqlite:// to sqlite+aiosqlite:// for async support
        if db_url.startswith("sqlite://"):
            async_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            async_url = db_url
            
        self.async_engine = create_async_engine(
            async_url,
            pool_pre_ping=True,    
# Validate connections before use
            pool_recycle=3600,     
# Recycle connections every hour
            echo=False             
# Set to True for SQL logging during development
        )
        
        self.async_session_maker = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False  
# Keep objects accessible after commit
        )

```text

#
## Pattern: Safe Session Context Management

```text
python

# PATTERN: Async context manager for database sessions

@asynccontextmanager
async def get_session(self):
    """Get an async database session with automatic cleanup."""
    async with self.async_session_maker() as session:
        try:
            yield session
            await session.commit()  
# Commit if no exceptions
        except Exception:
            await session.rollback()  
# Rollback on any error
            raise
        finally:
            await session.close()  
# Always close session

# USAGE: Always use context manager for database operations

async def create_task(self, task: Task) -> Task:
    """Create a new task with proper session management."""
    async with self.get_session() as session:
        
# Database operations here
        session.add(task_record)
        await session.commit()
        return task

```text

#
# Repository Pattern Implementation

#
## Pattern: Clean Architecture Repository Interface

```text
python

# PATTERN: Abstract repository interface in domain layer

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.task import Task

class TaskRepository(ABC):
    """Abstract repository interface for task operations."""
    
    @abstractmethod
    async def create_task(self, task: Task) -> Task:
        """Create a new task."""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        pass
    
    @abstractmethod
    async def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: str, hard_delete: bool = False) -> bool:
        """Delete a task (soft delete by default)."""
        pass
    
    @abstractmethod
    async def query_tasks(self, filters: Dict[str, Any]) -> List[Task]:
        """Query tasks with filters."""
        pass

```text

#
## Pattern: SQLite Repository Implementation

```text
python

# PATTERN: Concrete repository implementation in infrastructure layer

from sqlalchemy import select, update, delete, and_, or_
from ...domain.repositories.task_repository import TaskRepository
from ..models import TaskModel

class SQLiteTaskRepository(TaskRepository):
    """SQLite implementation of task repository."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._setup_async_engine()
    
    async def create_task(self, task: Task) -> Task:
        """Create a new task with validation and error handling."""
        try:
            async with self.get_session() as session:
                
# PATTERN: Convert domain entity to database model
                task_record = TaskModel(
                    task_id=task.task_id,
                    title=task.title,
                    description=task.description,
                    status=task.status.value,
                    created_at=task.created_at,
                    
# ... other fields
                )
                
                session.add(task_record)
                await session.flush()  
# Get the ID without committing
                
                
# PATTERN: Convert back to domain entity
                return self._record_to_domain(task_record)
                
        except IntegrityError as e:
            logger.error(f"Integrity constraint violation creating task: {e}")
            raise DomainError(f"Task creation failed: {e}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating task: {e}")
            raise DatabaseError(f"Database operation failed: {e}")

```text

#
# Query Patterns

#
## Pattern: Safe Query Building

```text
python

# PATTERN: Type-safe query building with proper error handling

async def query_tasks(self, filters: Dict[str, Any]) -> List[Task]:
    """Query tasks with flexible filtering."""
    try:
        async with self.get_session() as session:
            query = select(TaskModel)
            
            
# PATTERN: Safe filter application
            if 'status' in filters:
                query = query.where(TaskModel.status == filters['status'])
            
            if 'parent_task_id' in filters:
                parent_id = filters['parent_task_id']
                if parent_id is None:
                    query = query.where(TaskModel.parent_task_id.is_(None))
                else:
                    query = query.where(TaskModel.parent_task_id == parent_id)
            
            if 'created_after' in filters:
                query = query.where(TaskModel.created_at >= filters['created_after'])
            
            
# PATTERN: Execute query with error handling
            result = await session.execute(query)
            records = result.scalars().all()
            
            
# PATTERN: Convert to domain entities
            return [self._record_to_domain(record) for record in records]
            
    except SQLAlchemyError as e:
        logger.error(f"Database error querying tasks: {e}")
        raise DatabaseError(f"Query failed: {e}")

# PATTERN: Complex query with joins and aggregations

async def get_task_with_dependencies(self, task_id: str) -> Optional[Task]:
    """Get task with all its dependencies loaded."""
    try:
        async with self.get_session() as session:
            query = (
                select(TaskModel)
                .options(
                    selectinload(TaskModel.dependencies),  
# Eager load dependencies
                    selectinload(TaskModel.children)       
# Eager load child tasks
                )
                .where(TaskModel.task_id == task_id)
            )
            
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            
            if record is None:
                return None
                
            return self._record_to_domain_with_relations(record)
            
    except SQLAlchemyError as e:
        logger.error(f"Database error loading task with dependencies: {e}")
        raise DatabaseError(f"Failed to load task: {e}")

```text

#
## Pattern: Batch Operations

```text
python

# PATTERN: Efficient batch operations

async def create_tasks_batch(self, tasks: List[Task]) -> List[Task]:
    """Create multiple tasks efficiently in a single transaction."""
    if not tasks:
        return []
    
    try:
        async with self.get_session() as session:
            task_records = []
            
            for task in tasks:
                record = TaskModel(
                    task_id=task.task_id,
                    title=task.title,
                    
# ... other fields
                )
                task_records.append(record)
            
            
# PATTERN: Batch insert
            session.add_all(task_records)
            await session.flush()  
# Get IDs without committing
            
            
# PATTERN: Return domain entities
            return [self._record_to_domain(record) for record in task_records]
            
    except SQLAlchemyError as e:
        logger.error(f"Batch task creation failed: {e}")
        raise DatabaseError(f"Batch operation failed: {e}")

# PATTERN: Bulk update operations

async def update_tasks_status(self, task_ids: List[str], new_status: TaskStatus) -> int:
    """Update status for multiple tasks efficiently."""
    try:
        async with self.get_session() as session:
            query = (
                update(TaskModel)
                .where(TaskModel.task_id.in_(task_ids))
                .values(
                    status=new_status.value,
                    updated_at=datetime.utcnow()
                )
            )
            
            result = await session.execute(query)
            return result.rowcount  
# Number of updated rows
            
    except SQLAlchemyError as e:
        logger.error(f"Bulk status update failed: {e}")
        raise DatabaseError(f"Bulk update failed: {e}")

```text

#
# Migration Patterns

#
## Pattern: Safe Database Migrations

```text
python

# PATTERN: Migration with rollback capability

class MigrationManager:
    """Manages database migrations with rollback support."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.sync_engine = create_engine(db_url)  
# Sync engine for migrations
    
    async def run_migrations(self) -> bool:
        """Run pending migrations safely."""
        try:
            
# PATTERN: Check current schema version
            current_version = await self.get_schema_version()
            target_version = self.get_target_version()
            
            if current_version >= target_version:
                logger.info(f"Database is up to date (version {current_version})")
                return True
            
            
# PATTERN: Create backup before migration
            backup_path = await self.create_backup()
            
            try:
                
# PATTERN: Run migrations in order
                for version in range(current_version + 1, target_version + 1):
                    await self.run_migration(version)
                    await self.update_schema_version(version)
                
                logger.info(f"Successfully migrated to version {target_version}")
                return True
                
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                await self.rollback_from_backup(backup_path)
                raise
                
        except Exception as e:
            logger.error(f"Migration process failed: {e}")
            return False

```text

#
## Pattern: Workspace-aware Database Management

```text
python

# PATTERN: Multi-workspace database management

class WorkspaceManager:
    """Manages database instances per workspace."""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        self._repositories: Dict[str, TaskRepository] = {}
    
    def get_repository(self, workspace_path: str) -> TaskRepository:
        """Get repository for specific workspace."""
        workspace_key = str(Path(workspace_path).resolve())
        
        if workspace_key not in self._repositories:
            
# PATTERN: Workspace-specific database location
            db_path = Path(workspace_path) / ".task_orchestrator" / "tasks.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            db_url = f"sqlite:///{db_path}"
            repository = SQLiteTaskRepository(db_url)
            
            self._repositories[workspace_key] = repository
        
        return self._repositories[workspace_key]
    
    async def initialize_workspace(self, workspace_path: str) -> bool:
        """Initialize database for a workspace."""
        try:
            repository = self.get_repository(workspace_path)
            
            
# PATTERN: Ensure database schema exists
            migration_manager = MigrationManager(repository.db_url)
            success = await migration_manager.run_migrations()
            
            if success:
                logger.info(f"Workspace initialized: {workspace_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace {workspace_path}: {e}")
            return False

```text

#
# Error Handling Patterns

#
## Pattern: Database Exception Management

```text
python

# PATTERN: Comprehensive database error handling

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

async def safe_database_operation(self, operation_func, *args, **kwargs):
    """Execute database operation with comprehensive error handling."""
    try:
        return await operation_func(*args, **kwargs)
        
    except IntegrityError as e:
        
# PATTERN: Handle constraint violations
        if "UNIQUE constraint failed" in str(e):
            raise DomainError("Resource already exists")
        elif "FOREIGN KEY constraint failed" in str(e):
            raise DomainError("Referenced resource not found")
        else:
            logger.error(f"Integrity constraint violation: {e}")
            raise DomainError(f"Data integrity error: {e}")
    
    except OperationalError as e:
        
# PATTERN: Handle connection and operational issues
        if "database is locked" in str(e):
            logger.warning("Database locked, retrying...")
            await asyncio.sleep(0.1)  
# Brief delay before retry
            return await self.safe_database_operation(operation_func, *args, **kwargs)
        else:
            logger.error(f"Database operational error: {e}")
            raise DatabaseError(f"Database unavailable: {e}")
    
    except SQLAlchemyError as e:
        
# PATTERN: Generic SQLAlchemy error handling
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Database operation failed: {e}")
    
    except Exception as e:
        
# PATTERN: Unexpected error handling
        logger.exception(f"Unexpected error in database operation: {e}")
        raise DatabaseError(f"Unexpected database error: {e}")

```text

#
## Pattern: Connection Pool Management

```text
python

# PATTERN: Connection pool monitoring and management

class PoolMonitor:
    """Monitor and manage database connection pool."""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.engine = repository.async_engine
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status."""
        pool = self.engine.pool
        
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "invalid": pool.invalid(),
            "overflow": pool.overflow(),
        }
    
    async def validate_connections(self) -> bool:
        """Validate all connections in the pool."""
        try:
            async with self.repository.get_session() as session:
                
# Simple query to test connection
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False

```text

#
# Testing Patterns

#
## Pattern: Database Testing with Fixtures

```text
python

# PATTERN: Test database setup with proper isolation

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
import tempfile
import os

@pytest.fixture
async def test_repository():
    """Create isolated test database."""
    
# PATTERN: Use temporary database for tests
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        db_url = f"sqlite:///{temp_db.name}"
        
        repository = SQLiteTaskRepository(db_url)
        
        
# PATTERN: Initialize test schema
        migration_manager = MigrationManager(db_url)
        await migration_manager.run_migrations()
        
        yield repository
        
        
# PATTERN: Cleanup test database
        await repository.async_engine.dispose()
        os.unlink(temp_db.name)

@pytest.mark.asyncio
async def test_task_creation(test_repository):
    """Test task creation with proper isolation."""
    task = Task(
        task_id="test-123",
        title="Test Task",
        description="Test Description"
    )
    
    created_task = await test_repository.create_task(task)
    
    assert created_task.task_id == "test-123"
    assert created_task.title == "Test Task"
    
    
# PATTERN: Verify persistence
    retrieved_task = await test_repository.get_task("test-123")
    assert retrieved_task is not None
    assert retrieved_task.title == "Test Task"

```text

#
# Performance Patterns

#
## Pattern: Query Optimization

```text
python

# PATTERN: Optimized queries with proper indexing

async def get_user_tasks_optimized(self, user_id: str, limit: int = 100) -> List[Task]:
    """Get user tasks with optimized query."""
    try:
        async with self.get_session() as session:
            
# PATTERN: Use indexes and limit results
            query = (
                select(TaskModel)
                .where(TaskModel.assigned_user_id == user_id)
                .order_by(TaskModel.created_at.desc())  
# Use indexed column for ordering
                .limit(limit)
            )
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            return [self._record_to_domain(record) for record in records]
            
    except SQLAlchemyError as e:
        logger.error(f"Optimized query failed: {e}")
        raise DatabaseError(f"Query optimization error: {e}")

# PATTERN: Pagination for large datasets

async def get_tasks_paginated(self, page: int, page_size: int = 50) -> Tuple[List[Task], int]:
    """Get tasks with pagination."""
    try:
        async with self.get_session() as session:
            
# PATTERN: Count total records
            count_query = select(func.count(TaskModel.task_id))
            count_result = await session.execute(count_query)
            total_count = count_result.scalar()
            
            
# PATTERN: Get page of results
            offset = (page - 1) * page_size
            query = (
                select(TaskModel)
                .order_by(TaskModel.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            tasks = [self._record_to_domain(record) for record in records]
            
            return tasks, total_count
            
    except SQLAlchemyError as e:
        logger.error(f"Pagination query failed: {e}")
        raise DatabaseError(f"Pagination error: {e}")

```text

#
# Common Gotchas

#
## Database Connection Issues

```text
python

# ❌ WRONG: Not using context managers

async def bad_database_operation():
    session = async_session_maker()
    result = await session.execute(query)
    
# Missing: await session.close() - causes resource leaks

# ✅ CORRECT: Always use context managers

async def good_database_operation():
    async with self.get_session() as session:
        result = await session.execute(query)
        return result  
# Session automatically closed

# ❌ WRONG: Mixing sync and async operations

def mixed_operation():
    
# This will fail - can't use async session in sync context
    session = async_session_maker()
    result = session.execute(query)  
# Should be await session.execute

# ✅ CORRECT: Consistent async usage

async def async_operation():
    async with self.get_session() as session:
        result = await session.execute(query)
        return result

```text

#
## Error Handling Mistakes

```text
python

# ❌ WRONG: Catching all exceptions generically

try:
    result = await database_operation()
except Exception as e:
    print(f"Error: {e}")  
# Too generic, loses important error information

# ✅ CORRECT: Specific exception handling

try:
    result = await database_operation()
except IntegrityError as e:
    logger.error(f"Data integrity violation: {e}")
    raise DomainError("Resource conflict")
except OperationalError as e:
    logger.error(f"Database operational error: {e}")
    raise DatabaseError("Database unavailable")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise DatabaseError("Database operation failed")
```text

#
# Best Practices Summary

1. **Connection Management**: Always use async context managers for database sessions

2. **Repository Pattern**: Abstract database access behind repository interfaces  

3. **Error Handling**: Catch specific database exceptions and convert to domain errors

4. **Resource Cleanup**: Use context managers to ensure proper resource disposal

5. **Migration Safety**: Always backup before migrations and support rollback

6. **Query Optimization**: Use proper indexing and pagination for large datasets

7. **Testing Isolation**: Use temporary databases for tests with proper cleanup

8. **Workspace Separation**: Maintain separate database instances per workspace

#
# Related Documentation

- [MCP Protocol Patterns](./mcp-protocol-patterns.md)

- [Security Patterns](./security-patterns.md)

- [Context Engineering Guide](./context-engineering-guide.md)

- [Clean Architecture Guide](../../docs/developers/architecture/clean-architecture-guide.md)
