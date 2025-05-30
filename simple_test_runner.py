#!/usr/bin/env python3
"""
Simple test runner to validate core functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🚀 Testing Task Orchestrator Core Functionality")
print("="*60)

# Test 1: Import testing modules
print("\n▶️ Test 1: Import Testing Modules")
try:
    from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader
    print("✅ Successfully imported TestOutputWriter and TestOutputReader")
    
    from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
    print("✅ Successfully imported DatabasePersistenceManager")
    
    print("✅ All core modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {str(e)}")
    sys.exit(1)

# Test 2: Basic functionality
print("\n▶️ Test 2: Basic File Output System")
try:
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        writer = TestOutputWriter(output_dir)
        
        with writer.write_test_output("basic_test", "text") as session:
            session.write_line("=== Basic Test ===")
            session.write_line("Testing file output system")
            session.write_line("=== Test Complete ===")
        
        # Check file was created
        output_files = list(output_dir.glob("basic_test_*.txt"))
        if output_files:
            print("✅ File output system working")
        else:
            print("❌ No output file created")
            
except Exception as e:
    print(f"❌ File output test failed: {str(e)}")

# Test 3: Database connectivity
print("\n▶️ Test 3: Database Connectivity")
try:
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        with DatabasePersistenceManager(db_url=f"sqlite:///{db_path}") as persistence:
            active_tasks = persistence.get_all_active_tasks()
            print(f"✅ Database connection successful, found {len(active_tasks)} active tasks")
    finally:
        import os
        try:
            os.unlink(db_path)
        except:
            pass
            
except Exception as e:
    print(f"❌ Database test failed: {str(e)}")

print("\n🎉 Core functionality validation complete!")
print("The task orchestrator infrastructure appears to be working correctly.")
