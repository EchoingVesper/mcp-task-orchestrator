#!/usr/bin/env python3
"""Check database access and try to fix issues."""

import os
import shutil
import sqlite3
from pathlib import Path

os.chdir(Path(__file__).parent)

print("🔍 Checking database access...")

# Try to copy the database file first
try:
    shutil.copy2("task_orchestrator.db", "task_orchestrator_backup.db")
    print("✅ Created backup: task_orchestrator_backup.db")
except Exception as e:
    print(f"❌ Failed to create backup: {e}")

# Try to create a new temporary database
try:
    test_conn = sqlite3.connect("test_db.db")
    test_conn.execute("CREATE TABLE test (id INTEGER)")
    test_conn.close()
    os.remove("test_db.db")
    print("✅ Can create new databases")
except Exception as e:
    print(f"❌ Cannot create new databases: {e}")

# Try to open the database in read-only mode
try:
    conn = sqlite3.connect("file:task_orchestrator.db?mode=ro", uri=True)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ Can read database - Tables: {[t[0] for t in tables]}")
    conn.close()
except Exception as e:
    print(f"❌ Cannot read database: {e}")

print("\n💡 Attempting to recreate database with schema...")

# If we can't access the original, create a fresh one
try:
    # Move the old one out of the way
    if os.path.exists("task_orchestrator.db"):
        os.rename("task_orchestrator.db", "task_orchestrator_old.db")
        print("📦 Moved old database to task_orchestrator_old.db")
    
    # Create new database with proper schema
    from mcp_task_orchestrator.db.models import Base
    from sqlalchemy import create_engine
    
    engine = create_engine('sqlite:///task_orchestrator.db')
    Base.metadata.create_all(engine)
    engine.dispose()
    
    print("✅ Created new database with proper schema!")
    
except Exception as e:
    print(f"❌ Failed to recreate database: {e}")