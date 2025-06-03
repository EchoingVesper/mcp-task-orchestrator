#!/usr/bin/env python3
"""Test script to verify that the import issue in maintenance.py is fixed."""

import sys

def test_models_import():
    """Test that all models can be imported."""
    try:
        from mcp_task_orchestrator.db.models import (
            TaskBreakdownModel, SubTaskModel, MaintenanceOperationModel,
            TaskLifecycleModel, StaleTaskTrackingModel, TaskArchiveModel
        )
        print("✓ All database models imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import database models: {e}")
        return False

def test_maintenance_import():
    """Test that maintenance module can be imported."""
    try:
        from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
        print("✓ MaintenanceCoordinator imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import MaintenanceCoordinator: {e}")
        return False

def test_lifecycle_import():
    """Test that task lifecycle module can be imported."""
    try:
        from mcp_task_orchestrator.orchestrator.task_lifecycle import TaskLifecycleManager
        print("✓ TaskLifecycleManager imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import TaskLifecycleManager: {e}")
        return False

def main():
    """Run all import tests."""
    print("Testing import fixes for maintenance.py...")
    print("-" * 50)
    
    all_passed = True
    
    # Test database models
    if not test_models_import():
        all_passed = False
    
    # Test maintenance module
    if not test_maintenance_import():
        all_passed = False
    
    # Test task lifecycle module
    if not test_lifecycle_import():
        all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("✓ All imports fixed successfully!")
        return 0
    else:
        print("✗ Some imports still have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())