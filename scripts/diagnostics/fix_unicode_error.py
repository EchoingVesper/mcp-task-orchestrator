#!/usr/bin/env python3
"""Emergency fix for Unicode surrogate errors in task orchestrator database."""

import os
import shutil
import sqlite3
from datetime import datetime

def fix_unicode_errors():
    """Fix Unicode surrogate errors by creating fresh database."""
    
    # Paths
    db_dir = ".task_orchestrator"
    db_path = os.path.join(db_dir, "orchestrator_state.db")
    backup_path = os.path.join(db_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    print("🔧 Fixing Unicode surrogate errors in task orchestrator...")
    
    # Create directory if needed
    os.makedirs(db_dir, exist_ok=True)
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Created backup: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not backup database: {e}")
        
        # Remove corrupted database
        try:
            os.remove(db_path)
            print("✅ Removed corrupted database")
        except Exception as e:
            print(f"❌ Could not remove database: {e}")
            return False
    
    # Create fresh database with schema
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                parent_task_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                specialist_type TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                summary TEXT,
                estimated_effort TEXT,
                priority TEXT DEFAULT 'normal',
                task_type TEXT DEFAULT 'generic',
                FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # Create artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent_task ON tasks(parent_task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_artifacts ON artifacts(task_id)")
        
        conn.commit()
        conn.close()
        
        print("✅ Created fresh database with proper schema")
        print("✅ Task orchestrator should now work without Unicode errors")
        
        # Also clear any temporary files that might contain bad data
        temp_dir = os.path.join(db_dir, "temp")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("✅ Cleared temporary files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating fresh database: {e}")
        return False

if __name__ == "__main__":
    success = fix_unicode_errors()
    exit(0 if success else 1)