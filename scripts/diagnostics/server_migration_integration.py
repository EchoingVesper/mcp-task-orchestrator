#!/usr/bin/env python3
"""
Server Migration Integration Guide

This file shows exactly what changes need to be made to integrate
the automatic migration system into the server startup sequence.
"""

# ==============================================================================
# STEP 1: Update server.py imports
# ==============================================================================

# Add this import at the top of server.py (around line 24)
from .db.auto_migration import execute_startup_migration

# ==============================================================================
# STEP 2: Add migration function to server.py
# ==============================================================================

def initialize_database_with_migration(base_dir: str = None, db_path: str = None) -> bool:
    """
    Initialize database with automatic migration support.
    
    This function should be called before any StateManager initialization
    to ensure the database schema is up to date.
    
    Args:
        base_dir: Base directory for the database (optional)
        db_path: Specific database path (optional)
        
    Returns:
        True if database initialization succeeded, False otherwise
    """
    import os
    from pathlib import Path
    
    try:
        # Determine database path (same logic as StateManager)
        if db_path is None:
            db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
            
            if not db_path:
                if base_dir is None:
                    base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
                    if not base_dir:
                        base_dir = os.getcwd()
                
                db_path = os.path.join(base_dir, ".task_orchestrator", "task_orchestrator.db")
        
        # Ensure database directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct database URL
        database_url = f"sqlite:///{db_path}"
        
        # Execute migration
        logger.info(f"Initializing database with migration check: {database_url}")
        result = execute_startup_migration(database_url)
        
        if result.success:
            if result.migration_needed:
                logger.info(f"Database migration completed successfully: "
                          f"{result.operations_executed} operations in {result.execution_time_ms}ms")
                
                if result.backup_created:
                    logger.info(f"Database backup created: {result.backup_info.backup_id}")
            else:
                logger.info("Database schema is up to date - no migration needed")
            
            return True
        else:
            logger.error(f"Database migration failed: {result.error_message}")
            if result.warnings:
                for warning in result.warnings:
                    logger.warning(f"Migration warning: {warning}")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# ==============================================================================
# STEP 3: Modify get_state_manager() function in server.py
# ==============================================================================

def get_state_manager() -> StateManager:
    """Get or create the StateManager singleton instance."""
    global _state_manager
    if _state_manager is None:
        # Get base directory for persistence
        base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
        if not base_dir:
            base_dir = os.getcwd()
        
        # MIGRATION INTEGRATION: Initialize database with migration
        migration_success = initialize_database_with_migration(base_dir=base_dir)
        if not migration_success:
            logger.error("Database migration failed - server may not function correctly")
            # You can choose to:
            # 1. Continue anyway (current approach)
            # 2. Raise an exception to prevent server startup
            # 3. Use a fallback database
        
        _state_manager = StateManager(base_dir=base_dir)
        logger.info(f"Initialized StateManager with persistence in {base_dir}/.task_orchestrator")
    
    return _state_manager

# ==============================================================================
# STEP 4: Alternative integration approaches
# ==============================================================================

# APPROACH 1: Early migration check (recommended)
# Add this to the very beginning of main() function in server.py

async def main():
    """Main server entry point with migration check."""
    
    # Early migration check before any other initialization
    base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR", os.getcwd())
    migration_success = initialize_database_with_migration(base_dir=base_dir)
    
    if not migration_success:
        logger.error("Critical: Database migration failed - exiting")
        return 1  # Exit with error code
    
    # Continue with normal server initialization...
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

# APPROACH 2: Environment variable control
# Add environment variable to control migration behavior

def get_migration_config():
    """Get migration configuration from environment variables."""
    return {
        'enabled': os.environ.get("MCP_TASK_ORCHESTRATOR_AUTO_MIGRATION", "true").lower() == "true",
        'backup_enabled': os.environ.get("MCP_TASK_ORCHESTRATOR_BACKUP", "true").lower() == "true",
        'max_execution_time_ms': int(os.environ.get("MCP_TASK_ORCHESTRATOR_MIGRATION_TIMEOUT", "15000")),
        'dry_run': os.environ.get("MCP_TASK_ORCHESTRATOR_MIGRATION_DRY_RUN", "false").lower() == "true"
    }

# APPROACH 3: Advanced integration with health monitoring
# Add migration health check tool

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    tools = [
        # ... existing tools ...
        
        types.Tool(
            name="orchestrator_database_health",
            description="Check database migration system health and status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        types.Tool(
            name="orchestrator_migration_status",
            description="Get database migration status and history",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls with migration system support."""
    
    if name == "orchestrator_database_health":
        try:
            from .db.auto_migration import AutoMigrationSystem
            
            # Get database URL from StateManager logic
            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR", os.getcwd())
            db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
            if not db_path:
                db_path = os.path.join(base_dir, ".task_orchestrator", "task_orchestrator.db")
            
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            health = migration_system.get_system_health()
            status = migration_system.check_migration_status()
            
            result = {
                "database_health": health,
                "migration_status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return [types.TextContent(
                type="text", 
                text=f"Error checking database health: {e}"
            )]
    
    elif name == "orchestrator_migration_status":
        try:
            from .db.auto_migration import AutoMigrationSystem
            
            # Same database URL logic as above
            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR", os.getcwd())
            db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
            if not db_path:
                db_path = os.path.join(base_dir, ".task_orchestrator", "task_orchestrator.db")
            
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Get migration history and statistics
            history = migration_system.history_manager.get_migration_history(limit=20)
            stats = migration_system.history_manager.get_migration_statistics()
            
            result = {
                "migration_history": history,
                "migration_statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Migration status check failed: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error checking migration status: {e}"
            )]
    
    # ... handle other existing tools ...

# ==============================================================================
# STEP 5: Environment configuration
# ==============================================================================

# Add these environment variables for migration control:

# MCP_TASK_ORCHESTRATOR_AUTO_MIGRATION=true    # Enable/disable auto migration
# MCP_TASK_ORCHESTRATOR_BACKUP=true            # Enable/disable automatic backups  
# MCP_TASK_ORCHESTRATOR_MIGRATION_TIMEOUT=15000 # Migration timeout in milliseconds
# MCP_TASK_ORCHESTRATOR_MIGRATION_DRY_RUN=false # Enable dry run mode for testing

# ==============================================================================
# STEP 6: Testing the integration
# ==============================================================================

def test_migration_integration():
    """Test function to validate migration integration."""
    import tempfile
    import shutil
    from pathlib import Path
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = Path(temp_dir) / "test.db"
        
        # Test migration with empty database
        print("Testing migration with empty database...")
        success = initialize_database_with_migration(db_path=str(test_db_path))
        print(f"Migration result: {'SUCCESS' if success else 'FAILED'}")
        
        # Test migration with existing database
        print("Testing migration with existing database...")
        success = initialize_database_with_migration(db_path=str(test_db_path))
        print(f"Second migration result: {'SUCCESS' if success else 'FAILED'}")
        
        return success

if __name__ == "__main__":
    # Test the integration
    test_migration_integration()