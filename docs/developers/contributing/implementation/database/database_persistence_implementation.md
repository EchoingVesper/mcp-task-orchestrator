

# MCP Task Orchestrator: Database-Backed Persistence Implementation

#

# Overview

Implement a robust database-backed persistence mechanism for the MCP Task Orchestrator to replace the current file-based system. This will eliminate lock contention issues and provide proper transaction support.

#

# Requirements

1. **Database Selection**: Use SQLAlchemy with SQLite as the backend

- SQLAlchemy provides a robust ORM with transaction support

- SQLite is lightweight, requires no server setup, and is perfect for this use case

- Both are well-established, well-documented, and widely used

2. **Implementation Goals**

- Replace file-based persistence with database transactions

- Maintain the same API for backward compatibility

- Eliminate lock contention issues

- Provide proper error handling and recovery

- Support concurrent access safely

3. **Migration Strategy**

- Create a migration script to move existing tasks to the new database

- Maintain backward compatibility during transition

#

# Implementation Details

#

## 1. Update Dependencies

Add to requirements.txt:

```dependencies
sqlalchemy>=2.0.0
alembic>=1.10.0  

# For database migrations

```text

#

## 2. Database Models

Create models that map directly to the current data structures:

- `TaskBreakdown` model with one-to-many relationship to `SubTask` models

- Use SQLAlchemy's declarative base for model definitions

- Include proper indexes for efficient querying

#

## 3. Connection Management

- Implement connection pooling for efficient resource usage

- Use context managers for automatic connection cleanup

- Implement proper transaction boundaries with commit/rollback

#

## 4. API Compatibility

- Maintain the same method signatures in the `PersistenceManager` class

- Replace file operations with equivalent database operations

- Use transactions for operations that modify multiple records

#

## 5. Error Handling

- Implement proper exception handling with specific error types

- Add retry logic for transient database errors

- Log detailed error information for troubleshooting

#

# Example Implementation Structure

```text
python

# models.py

from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TaskBreakdownModel(Base):
    __tablename__ = 'task_breakdowns'
    
    parent_task_id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    complexity = Column(String, nullable=False)
    context = Column(Text)
    created_at = Column(DateTime, nullable=False)
    
    subtasks = relationship("SubTaskModel", back_populates="parent_task", cascade="all, delete-orphan")

class SubTaskModel(Base):
    __tablename__ = 'subtasks'
    
    task_id = Column(String, primary_key=True)
    parent_task_id = Column(String, ForeignKey('task_breakdowns.parent_task_id'), nullable=False)
    

# ... other fields ...

    
    parent_task = relationship("TaskBreakdownModel", back_populates="subtasks")

```text

```text
python

# db_persistence.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

class DatabasePersistenceManager:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = "sqlite:///task_orchestrator.db"
        
        self.engine = create_engine(db_url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
            
    def save_task_breakdown(self, breakdown):
        """Save a task breakdown to the database."""
        with self.session_scope() as session:
            

# Convert domain model to DB model

            db_breakdown = convert_to_db_model(breakdown)
            session.merge(db_breakdown)
            

# No need for explicit commit - handled by context manager

```text

#

# Migration Plan

1. Create a migration script that:

- Sets up the new database schema

- Reads all existing task files

- Converts and inserts them into the database

- Validates the migration was successful

2. Update the `StateManager` to use the new `DatabasePersistenceManager`

3. Add a compatibility layer that allows reading from both systems during transition

#

# Testing Strategy

1. Create unit tests for the new database persistence layer

2. Test concurrent access scenarios to verify lock contention is resolved

3. Benchmark performance compared to the file-based approach

4. Test error recovery scenarios

This approach will provide a robust, transaction-based persistence mechanism that eliminates the current file locking issues while maintaining compatibility with the existing codebase.
