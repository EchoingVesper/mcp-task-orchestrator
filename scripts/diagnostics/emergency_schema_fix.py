#!/usr/bin/env python3
"""
Emergency database schema repair script.

This script identifies and fixes the schema mismatch between the database model
definitions and the actual database schema, restoring orchestrator functionality.
"""

import sqlite3
import sys
import os
from pathlib import Path

def get_db_path():
    """Get the path to the database file."""
    return Path("task_orchestrator.db")

def check_table_schema(cursor, table_name):
    """Check the actual schema of a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return {col[1]: col[2] for col in columns}  # {column_name: type}

def check_database_exists():
    """Check if the database exists."""
    db_path = get_db_path()
    return db_path.exists()

def analyze_schema_mismatch():
    """Analyze the schema mismatch and provide repair commands."""
    
    if not check_database_exists():
        print("❌ Database file does not exist: task_orchestrator.db")
        return False
    
    try:
        conn = sqlite3.connect("task_orchestrator.db")
        cursor = conn.cursor()
        
        print("🔍 Analyzing database schema...")
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Found tables: {tables}")
        
        if 'subtasks' not in tables:
            print("❌ Critical: 'subtasks' table does not exist!")
            return False
            
        # Check subtasks table schema
        actual_schema = check_table_schema(cursor, 'subtasks')
        print("📊 Current subtasks table schema:")
        for col, dtype in actual_schema.items():
            print(f"  - {col}: {dtype}")
        
        # Expected columns based on the model
        expected_columns = {
            'task_id': 'STRING',
            'parent_task_id': 'STRING', 
            'title': 'STRING',
            'description': 'TEXT',
            'specialist_type': 'STRING',
            'dependencies': 'JSON',
            'estimated_effort': 'STRING',
            'status': 'STRING',
            'results': 'TEXT',
            'artifacts': 'JSON',
            'file_operations_count': 'INTEGER',
            'verification_status': 'STRING',
            'created_at': 'DATETIME',
            'completed_at': 'DATETIME',
            'prerequisite_satisfaction_required': 'BOOLEAN',
            'auto_maintenance_enabled': 'BOOLEAN',
            'quality_gate_level': 'STRING'
        }
        
        print("\n🎯 Expected columns:")
        for col, dtype in expected_columns.items():
            print(f"  - {col}: {dtype}")
        
        # Find missing columns
        missing_columns = []
        for col in expected_columns:
            if col not in actual_schema:
                missing_columns.append(col)
        
        if missing_columns:
            print("\n❌ Missing columns in subtasks table:")
            for col in missing_columns:
                print(f"  - {col}: {expected_columns[col]}")
            
            print("\n🔧 Generating repair SQL...")
            repair_sql = []
            
            for col in missing_columns:
                dtype = expected_columns[col]
                default_value = ""
                
                if dtype == 'BOOLEAN':
                    default_value = " DEFAULT 0"
                elif dtype == 'INTEGER':
                    default_value = " DEFAULT 0"
                elif dtype == 'STRING' and col == 'verification_status':
                    default_value = " DEFAULT 'pending'"
                elif dtype == 'STRING' and col == 'quality_gate_level':
                    default_value = " DEFAULT 'standard'"
                
                sql = f"ALTER TABLE subtasks ADD COLUMN {col} {dtype}{default_value};"
                repair_sql.append(sql)
            
            print("\n📝 Repair SQL commands:")
            for sql in repair_sql:
                print(f"  {sql}")
            
            return repair_sql
        else:
            print("\n✅ All expected columns are present!")
            return True
            
    except Exception as e:
        print(f"❌ Error analyzing schema: {e}")
        return False
    finally:
        conn.close()

def apply_schema_fixes(repair_sql):
    """Apply the schema fixes to the database."""
    try:
        conn = sqlite3.connect("task_orchestrator.db")
        cursor = conn.cursor()
        
        print("\n🔧 Applying schema fixes...")
        
        for sql in repair_sql:
            print(f"  Executing: {sql}")
            cursor.execute(sql)
        
        conn.commit()
        print("✅ Schema fixes applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema fixes: {e}")
        return False
    finally:
        conn.close()

def test_orchestrator_tools():
    """Test if the orchestrator tools are working after the fix."""
    try:
        print("\n🧪 Testing orchestrator functionality...")
        
        # Try importing the core modules
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        from .orchestrator.task_orchestration_service import TaskOrchestrator
        
        # Try creating a persistence manager
        persistence = DatabasePersistenceManager()
        
        # Try basic operations
        active_tasks = persistence.get_all_active_tasks()
        print(f"✅ Successfully retrieved {len(active_tasks)} active tasks")
        
        persistence.dispose()
        
        print("✅ Orchestrator tools appear to be working!")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator tools still not working: {e}")
        return False

def main():
    """Main function to run the emergency schema fix."""
    print("🚨 Emergency Database Schema Repair")
    print("=" * 50)
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Analyze the schema
    repair_result = analyze_schema_mismatch()
    
    if repair_result is True:
        print("\n✅ No schema repairs needed!")
    elif repair_result is False:
        print("\n❌ Unable to analyze or critical issues found!")
        return 1
    else:
        # We have repair SQL to apply
        repair_sql = repair_result
        
        print("\n❓ Apply these schema fixes? (y/n): ", end="")
        response = input().lower().strip()
        
        if response == 'y' or response == 'yes':
            if apply_schema_fixes(repair_sql):
                print("\n🧪 Testing orchestrator functionality...")
                if test_orchestrator_tools():
                    print("\n🎉 Emergency repair completed successfully!")
                    print("\n📋 Next steps:")
                    print("1. Restart Claude Desktop to clear any cached states")
                    print("2. Test the orchestration tools")
                    print("3. If working, proceed with Phase 2: orchestrated migration system")
                    return 0
                else:
                    print("\n⚠️ Schema fixed but orchestrator still not working")
                    print("Additional investigation may be needed")
                    return 1
            else:
                print("\n❌ Failed to apply schema fixes")
                return 1
        else:
            print("\n❌ Schema fixes not applied")
            return 1

if __name__ == "__main__":
    sys.exit(main())
