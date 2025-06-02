#!/usr/bin/env python3
"""
Test script to check if our new code can be imported without errors.
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    import mcp_task_orchestrator.server
    print("✅ Server module imports successfully")
    
    # Test our new models
    from mcp_task_orchestrator.db.models import TaskPrerequisiteModel, MaintenanceOperationModel, ProjectHealthMetricModel
    print("✅ New database models import successfully")
    
    # Test maintenance coordinator
    from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
    print("✅ Maintenance coordinator imports successfully")
    
    print("\n🎉 All imports successful - no syntax errors in new code!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
except Exception as e:
    print(f"❌ Other Error: {e}")
