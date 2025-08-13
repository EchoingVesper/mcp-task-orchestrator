#!/usr/bin/env python3
"""Create a fresh database with the correct schema."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.chdir(project_root)

print("🔧 Creating fresh database with correct schema...")

try:
    # Import the models to get the schema
    from mcp_task_orchestrator.db.models import Base
    from sqlalchemy import create_engine
    
    # Create a new database file with a different name
    db_path = "task_orchestrator_new.db"
    
    # Remove if exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database with schema
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    engine.dispose()
    
    print(f"✅ Created new database: {db_path}")
    
    # Verify the schema
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Tables created: {tables}")
    
    # Check subtasks schema
    cursor.execute("PRAGMA table_info(subtasks)")
    columns = cursor.fetchall()
    print("\n📊 Subtasks table columns:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")
    
    conn.close()
    
    print("\n✅ Database created successfully!")
    print("\n📋 Next steps:")
    print("1. Stop any running orchestrator processes")
    print("2. In Windows, rename task_orchestrator.db to task_orchestrator_old.db")
    print("3. Rename task_orchestrator_new.db to task_orchestrator.db")
    print("4. Restart the orchestrator")
    
except Exception as e:
    print(f"❌ Failed to create database: {e}")
    import traceback
    traceback.print_exc()