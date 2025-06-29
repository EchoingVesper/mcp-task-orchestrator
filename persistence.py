"""
Persistence management for the MCP Task Orchestrator.

This module is a compatibility wrapper that imports from the database persistence module.
The file-based persistence implementation has been deprecated in favor of the more
robust database-backed implementation to prevent task loss and timeout issues.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Import the database persistence manager for direct use
from .db.persistence import DatabasePersistenceManager as PersistenceManager

# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.persistence")

# Log a warning about the deprecated file-based persistence
logger.warning(
    "The file-based persistence implementation has been deprecated in favor of "
    "the database-backed implementation. All persistence operations now use SQLite."
)
