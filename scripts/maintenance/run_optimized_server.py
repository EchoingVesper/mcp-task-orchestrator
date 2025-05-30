#!/usr/bin/env python3
"""
Optimized MCP Task Orchestrator Server Runner

This script initializes the database and starts the MCP Task Orchestrator server
with the optimized database-backed persistence implementation.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_task_orchestrator_runner")

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize the database before importing the server
def initialize_database():
    """Initialize the database before starting the server."""
    try:
        logger.info("Initializing database...")
        
        # Set the environment variable to use the database persistence
        os.environ["MCP_TASK_ORCHESTRATOR_USE_DB"] = "true"
        
        # Import the database models and create the tables
        from mcp_task_orchestrator.db.models import Base
        from sqlalchemy import create_engine
        
        # Get the database path
        db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
        if not db_path:
            db_path = Path(__file__).parent / "task_orchestrator.db"
        
        # Create the database engine and tables
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        
        logger.info(f"Database initialized successfully at {db_path}")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        return False

# Start the server
async def start_server():
    """Start the MCP Task Orchestrator server."""
    try:
        # Import the server module
        from mcp_task_orchestrator.server import main
        
        # Start the server
        logger.info("Starting MCP Task Orchestrator server...")
        await main()
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Initialize the database first
    if initialize_database():
        # Then start the server
        asyncio.run(start_server())
    else:
        logger.error("Failed to initialize database, server not started")
        sys.exit(1)
