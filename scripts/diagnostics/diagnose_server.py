#!/usr/bin/env python3
"""
Diagnostic script for the MCP Task Orchestrator server.

This script traces the execution flow of the server initialization process
to identify where it's hanging.
"""

import os
import sys
import time
import logging
import importlib
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server_diagnosis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("diagnose_server")

def log_step(step_name):
    """Log a step in the diagnosis process."""
    logger.info(f"STEP: {step_name}")
    return time.time()

def log_time(start_time, step_name):
    """Log the time taken for a step."""
    elapsed = time.time() - start_time
    logger.info(f"TIME: {step_name} took {elapsed:.2f} seconds")

def main():
    """Run the diagnosis."""
    try:
        # Step 1: Set environment variables
        t = log_step("Setting environment variables")
        os.environ["MCP_TASK_ORCHESTRATOR_USE_DB"] = "true"
        os.environ["MCP_TASK_ORCHESTRATOR_LOG_LEVEL"] = "DEBUG"
        log_time(t, "Setting environment variables")
        
        # Step 2: Add project to Python path
        t = log_step("Adding project to Python path")
        project_dir = Path(__file__).parent
        sys.path.insert(0, str(project_dir))
        log_time(t, "Adding project to Python path")
        
        # Step 3: Import and initialize database models
        t = log_step("Importing database models")
        from mcp_task_orchestrator.db.models import Base
        from sqlalchemy import create_engine
        log_time(t, "Importing database models")
        
        # Step 4: Initialize database
        t = log_step("Initializing database")
        db_path = project_dir / "task_orchestrator.db"
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        log_time(t, "Initializing database")
        
        # Step 5: Import persistence factory
        t = log_step("Importing persistence factory")
        from mcp_task_orchestrator.persistence_factory import create_persistence_manager
        log_time(t, "Importing persistence factory")
        
        # Step 6: Create persistence manager
        t = log_step("Creating persistence manager")
        persistence = create_persistence_manager(str(project_dir), db_url)
        log_time(t, "Creating persistence manager")
        
        # Step 7: Import state manager
        t = log_step("Importing state manager")
        from mcp_task_orchestrator.orchestrator.state import StateManager
        log_time(t, "Importing state manager")
        
        # Step 8: Create state manager
        t = log_step("Creating state manager")
        state_manager = StateManager(str(db_path), str(project_dir))
        log_time(t, "Creating state manager")
        
        # Step 9: Import specialist manager
        t = log_step("Importing specialist manager")
        from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
        log_time(t, "Importing specialist manager")
        
        # Step 10: Create specialist manager
        t = log_step("Creating specialist manager")
        specialist_manager = SpecialistManager()
        log_time(t, "Creating specialist manager")
        
        # Step 11: Import task orchestrator
        t = log_step("Importing task orchestrator")
        from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
        log_time(t, "Importing task orchestrator")
        
        # Step 12: Create task orchestrator
        t = log_step("Creating task orchestrator")
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        log_time(t, "Creating task orchestrator")
        
        # Step 13: Import MCP server components
        t = log_step("Importing MCP server components")
        from mcp import types
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        log_time(t, "Importing MCP server components")
        
        # Step 14: Create MCP server
        t = log_step("Creating MCP server")
        app = Server("task-orchestrator")
        log_time(t, "Creating MCP server")
        
        # Step 15: Import server module
        t = log_step("Importing server module")
        import mcp_task_orchestrator.server
        log_time(t, "Importing server module")
        
        logger.info("All components initialized successfully!")
        logger.info("Diagnosis complete. Check server_diagnosis.log for details.")
        
        return True
    except Exception as e:
        logger.error(f"Error during diagnosis: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
