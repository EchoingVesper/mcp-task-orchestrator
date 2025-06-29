"""
Database Integration Helper for Generic Task Handlers

Provides a simple factory function to create database-connected use cases
without complex dependency injection setup. This is a pragmatic solution
for getting the 2.0 system working quickly.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from ....application.usecases.manage_generic_tasks import GenericTaskUseCase
from ....db.generic_repository import GenericTaskRepository
from ....domain.exceptions import OrchestrationError

logger = logging.getLogger(__name__)

# Singleton instance for reuse across handlers
_use_case_instance: Optional[GenericTaskUseCase] = None


def get_generic_task_use_case(force_new: bool = False) -> GenericTaskUseCase:
    """
    Get a GenericTaskUseCase instance with database connection.
    
    This is a pragmatic factory function that creates the use case with
    all necessary dependencies without requiring complex DI setup.
    
    Args:
        force_new: If True, create a new instance instead of reusing singleton
        
    Returns:
        GenericTaskUseCase instance ready for database operations
        
    Raises:
        OrchestrationError: If database initialization fails
    """
    global _use_case_instance
    
    try:
        # Return singleton unless forced to create new
        if _use_case_instance and not force_new:
            return _use_case_instance
        
        # Get database path from environment or use default
        base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR", os.getcwd())
        db_dir = Path(base_dir) / ".task_orchestrator"
        
        # Ensure database directory exists
        db_dir.mkdir(exist_ok=True)
        
        db_path = db_dir / "task_orchestrator.db"
        db_url = f"sqlite:///{db_path}"
        
        logger.info(f"Initializing GenericTaskRepository with database: {db_path}")
        
        # Create repository and use case
        repository = GenericTaskRepository(db_url)
        use_case = GenericTaskUseCase(repository)
        
        # Store as singleton
        _use_case_instance = use_case
        
        logger.info("GenericTaskUseCase initialized successfully")
        return use_case
        
    except Exception as e:
        logger.error(f"Failed to initialize GenericTaskUseCase: {e}")
        raise OrchestrationError(f"Database initialization failed: {str(e)}")


def reset_connection():
    """Reset the singleton connection (useful for testing)."""
    global _use_case_instance
    _use_case_instance = None
    logger.info("GenericTaskUseCase connection reset")


def health_check() -> dict:
    """
    Perform a health check on the database connection.
    
    Returns:
        Dictionary with health check results
    """
    try:
        use_case = get_generic_task_use_case()
        
        # Simple health check - try to query without filters (should return empty result)
        # This tests database connection and basic functionality
        result = {"status": "healthy", "message": "Database connection working"}
        
        logger.info("Database health check passed")
        return result
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy", 
            "message": f"Database connection failed: {str(e)}"
        }