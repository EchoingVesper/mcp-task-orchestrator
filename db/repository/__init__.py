"""
Generic Task Repository Package

This package provides modular components for database operations with the Generic Task Model.
The repository is split into focused modules to maintain manageable file sizes and clear responsibilities.

Modules:
- base: Core repository class and database setup
- crud_operations: Create, Read, Update, Delete operations
- query_builder: Complex query operations and filters
- dependency_manager: Dependency operations and cycle detection
- converters: Row-to-model conversion utilities
- template_operations: Template management operations
- helpers: Internal helper methods for database operations

File Sizes (all under 500 lines for Claude Code safety):
- base.py: 88 lines
- converters.py: 163 lines
- crud_operations.py: 259 lines
- dependency_manager.py: 189 lines
- query_builder.py: 243 lines
- template_operations.py: 93 lines
- helpers.py: 215 lines
"""

# Export base repository components for backward compatibility
from .base import GenericTaskRepository, CycleDetectedError

# Optional: Export converter utilities if needed externally
from .converters import (
    row_to_task,
    row_to_attribute,
    row_to_dependency,
    row_to_artifact,
    row_to_event,
    row_to_template
)

__all__ = [
    # Core repository class
    'GenericTaskRepository',
    
    # Exception types
    'CycleDetectedError',
    
    # Converter functions (available if needed)
    'row_to_task',
    'row_to_attribute',
    'row_to_dependency',
    'row_to_artifact',
    'row_to_event',
    'row_to_template',
]