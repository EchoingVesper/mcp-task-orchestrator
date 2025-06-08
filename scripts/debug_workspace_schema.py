#!/usr/bin/env python3
"""Debug script to find SQL syntax errors in workspace schema."""

import sqlite3
import tempfile
import os
from pathlib import Path

def test_sql_section(section_name, sql_content):
    """Test a section of SQL code."""
    print(f"Testing section: {section_name}")
    
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.executescript(sql_content)
        print(f"  ✓ {section_name} - OK")
        return True
        
    except sqlite3.Error as e:
        print(f"  ✗ {section_name} - Error: {e}")
        return False
    finally:
        conn.close()
        os.unlink(db_path)

def main():
    """Main function to debug workspace schema."""
    project_root = Path(__file__).parent.parent
    schema_file = project_root / 'mcp_task_orchestrator' / 'db' / 'workspace_schema.sql'
    
    if not schema_file.exists():
        print(f"Schema file not found: {schema_file}")
        return
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test basic setup
    basic_sql = """
    PRAGMA foreign_keys = ON;
    PRAGMA journal_mode = WAL;
    """
    test_sql_section("Basic setup", basic_sql)
    
    # Test workspace table creation
    workspace_table_sql = """
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE IF NOT EXISTS workspaces (
        workspace_id TEXT PRIMARY KEY,
        workspace_name TEXT NOT NULL,
        workspace_path TEXT NOT NULL UNIQUE,
        detection_method TEXT NOT NULL,
        detection_confidence INTEGER NOT NULL,
        
        project_type TEXT,
        project_markers TEXT,
        git_root_path TEXT,
        
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        artifact_storage_policy TEXT DEFAULT 'workspace_relative',
        
        is_validated BOOLEAN DEFAULT FALSE,
        is_writable BOOLEAN DEFAULT TRUE,
        security_warnings TEXT,
        
        total_tasks INTEGER DEFAULT 0,
        active_tasks INTEGER DEFAULT 0,
        completed_tasks INTEGER DEFAULT 0,
        failed_tasks INTEGER DEFAULT 0,
        last_activity_at TIMESTAMP,
        
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    test_sql_section("Workspace table", workspace_table_sql)
    
    # Test workspace_tasks table
    workspace_tasks_sql = """
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE IF NOT EXISTS workspaces (
        workspace_id TEXT PRIMARY KEY,
        workspace_name TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS workspace_tasks (
        association_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        
        association_type TEXT DEFAULT 'primary',
        created_in_workspace BOOLEAN DEFAULT TRUE,
        relative_artifact_paths TEXT,
        
        task_working_directory TEXT,
        environment_variables TEXT,
        
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(workspace_id, task_id, association_type)
    );
    """
    test_sql_section("Workspace tasks table", workspace_tasks_sql)
    
    # Test workspace_artifacts table
    workspace_artifacts_sql = """
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE IF NOT EXISTS workspaces (
        workspace_id TEXT PRIMARY KEY,
        workspace_name TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS workspace_artifacts (
        artifact_id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        task_id TEXT,
        
        relative_path TEXT NOT NULL,
        absolute_path TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        storage_method TEXT DEFAULT 'file',
        
        content_hash TEXT,
        file_size INTEGER,
        mime_type TEXT,
        encoding TEXT DEFAULT 'utf-8',
        content_preview TEXT,
        
        created_by_task BOOLEAN DEFAULT TRUE,
        is_persistent BOOLEAN DEFAULT TRUE,
        is_tracked_by_git BOOLEAN DEFAULT FALSE,
        backup_available BOOLEAN DEFAULT FALSE,
        
        version INTEGER DEFAULT 1,
        previous_version_id TEXT,
        
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_verified_at TIMESTAMP,
        last_modified_at TIMESTAMP
    );
    """
    test_sql_section("Workspace artifacts table", workspace_artifacts_sql)
    
    # Test entire schema in smaller chunks
    print("\nTesting complete schema in chunks...")
    
    # Split by sections and test each
    sections = content.split('/* ============================================ */')
    for i, section in enumerate(sections):
        if section.strip():
            section_sql = f"PRAGMA foreign_keys = ON;\n{section}"
            success = test_sql_section(f"Section {i+1}", section_sql)
            if not success:
                print(f"Failed section content preview:")
                print(section[:200] + "..." if len(section) > 200 else section)
                break

if __name__ == "__main__":
    main()