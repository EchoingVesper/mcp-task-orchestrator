#!/usr/bin/env python3
"""
Windows-compatible database schema fix for MCP Task Orchestrator
Run this from Windows Command Prompt in the project directory
"""

import sqlite3
import os
import sys

def fix_database():
    """Add missing columns to the subtasks table"""
    
    # Use Windows path
    db_path = r"E:\My Work\Programming\MCP Servers\mcp-task-orchestrator\task_orchestrator.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        print(f"🔧 Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(subtasks)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"📋 Existing columns in subtasks table: {existing_columns}")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("file_operations_count", "INTEGER DEFAULT 0"),
            ("verification_status", "VARCHAR DEFAULT 'pending'")
        ]
        
        changes_made = False
        for col_name, col_definition in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE subtasks ADD COLUMN {col_name} {col_definition}")
                changes_made = True
            else:
                print(f"✅ Column {col_name} already exists")
        
        if changes_made:
            conn.commit()
            print("💾 Changes committed to database")
        
        conn.close()
        
        print("✅ Database migration completed successfully!")
        print("🔄 Please restart Claude Desktop to see the changes")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== MCP Task Orchestrator Database Fix ===")
    print("This script will add missing columns to the subtasks table")
    print()
    
    success = fix_database()
    
    if success:
        print()
        print("✅ NEXT STEPS:")
        print("1. Restart Claude Desktop")
        print("2. Try the orchestrator again")
        print("3. The error should be resolved")
    else:
        print()
        print("❌ MANUAL FIX REQUIRED:")
        print("Use DB Browser for SQLite or sqlite3 command line:")
        print("1. Open: E:\\My Work\\Programming\\MCP Servers\\mcp-task-orchestrator\\task_orchestrator.db")
        print("2. Run: ALTER TABLE subtasks ADD COLUMN file_operations_count INTEGER DEFAULT 0;")
        print("3. Run: ALTER TABLE subtasks ADD COLUMN verification_status VARCHAR DEFAULT 'pending';")
    
    input("Press Enter to exit...")
    sys.exit(0 if success else 1)
