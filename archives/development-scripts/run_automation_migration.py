#!/usr/bin/env python3
"""
Simple runner script for the automation maintenance database migration.
This script makes it easy to run the migration from the project root.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the migration
from scripts.migrations.migrate_automation_maintenance import main

if __name__ == "__main__":
    print("Running automation maintenance database migration...")
    print(f"Project root: {project_root}")
    print(f"Database location: {os.path.join(os.path.expanduser('~'), '.task_orchestrator', 'orchestrator.db')}")
    print("-" * 50)
    
    # Run the migration
    main()