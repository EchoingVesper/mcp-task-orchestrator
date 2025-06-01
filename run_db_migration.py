#!/usr/bin/env python3
"""
Database Migration Script for MCP Task Orchestrator

This script fixes the missing file_operations_count column in the subtasks table.
"""

import os
import sys

# Add the project root to Python path
project_root = "/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator"
sys.path.insert(0, project_root)

# Change to project directory
os.chdir(project_root)

def main():
    try:
        print("Starting database migration for MCP Task Orchestrator...")
        
        # Import the migration function
        from file_tracking_migration import migrate_file_tracking_tables
        
        print("Running file tracking migration...")
        result = migrate_file_tracking_tables()
        
        if result:
            print("✅ Database migration completed successfully!")
            print("The missing file_operations_count column has been added to the subtasks table.")
        else:
            print("❌ Database migration failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
