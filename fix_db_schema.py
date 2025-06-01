#!/usr/bin/env python3
"""
Simple database fix for missing file_operations_count column
"""

import sqlite3
import os

def fix_database():
    """Add missing columns to the subtasks table"""
    
    # Database path
    db_path = "/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator/task_orchestrator.db"
    
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
        
        for col_name, col_definition in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE subtasks ADD COLUMN {col_name} {col_definition}")
            else:
                print(f"✅ Column {col_name} already exists")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_database()
    exit(0 if success else 1)
