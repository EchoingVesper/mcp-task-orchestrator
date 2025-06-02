#!/usr/bin/env python3
"""
Comprehensive System Diagnostic Tool for MCP Task Orchestrator

This script combines functionality from multiple diagnostic tools
and provides a unified health check and analysis system.
"""

import os
import sys
import sqlite3
import psutil
import time
import json
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def format_bytes(bytes_value):
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def check_system_resources():
    """Check system resource usage."""
    print("🖥️  System Resources")
    print("-" * 30)
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")
    
    # Memory usage
    memory = psutil.virtual_memory()
    print(f"Memory: {format_bytes(memory.used)}/{format_bytes(memory.total)} ({memory.percent}%)")
    
    # Disk usage
    project_root = get_project_root()
    disk_usage = psutil.disk_usage(str(project_root))
    print(f"Disk: {format_bytes(disk_usage.used)}/{format_bytes(disk_usage.total)} ({disk_usage.used/disk_usage.total*100:.1f}%)")
    
    print()

def check_database_status():
    """Check database health and status."""
    print("🗄️  Database Status")
    print("-" * 30)
    
    project_root = get_project_root()
    
    # Check main database
    main_db_path = project_root / "task_orchestrator.db"
    data_db_path = project_root / "data" / "task_orchestrator.db"
    
    db_path = None
    if main_db_path.exists():
        db_path = main_db_path
        print(f"✅ Database found: {main_db_path}")
    elif data_db_path.exists():
        db_path = data_db_path
        print(f"✅ Database found: {data_db_path}")
    else:
        print("❌ Database not found in expected locations")
        return False
    
    try:
        # Check database connectivity
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get database info
        file_size = db_path.stat().st_size
        print(f"📁 Size: {format_bytes(file_size)}")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables: {len(tables)} ({', '.join([t[0] for t in tables])})")
        
        # Check task counts
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        print(f"📋 Tasks: {task_count}")
        
        cursor.execute("SELECT COUNT(*) FROM subtasks")
        subtask_count = cursor.fetchone()[0]
        print(f"📝 Subtasks: {subtask_count}")
        
        # Check for locks
        cursor.execute("SELECT COUNT(*) FROM locks")
        lock_count = cursor.fetchone()[0]
        print(f"🔒 Active Locks: {lock_count}")
        
        conn.close()
        print("✅ Database connectivity: OK")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print()
    return True

def check_project_structure():
    """Verify project directory structure."""
    print("📁 Project Structure")
    print("-" * 30)
    
    project_root = get_project_root()
    expected_dirs = [
        "mcp_task_orchestrator",
        "tests/unit",
        "tests/integration", 
        "tests/performance",
        "tests/fixtures",
        "scripts/diagnostics",
        "scripts/maintenance",
        "scripts/migrations",
        "scripts/deployment",
        "docs/development",
        "docs/testing",
        "docs/troubleshooting",
        "logs",
        "data"
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  Missing directories: {len(missing_dirs)}")
        return False
    else:
        print("\n✅ Project structure: Complete")
        return True
    
    print()

def check_dependencies():
    """Check Python dependencies."""
    print("📦 Dependencies")
    print("-" * 30)
    
    try:
        import sqlite3
        print("✅ sqlite3")
    except ImportError:
        print("❌ sqlite3")
    
    try:
        import psutil
        print("✅ psutil")
    except ImportError:
        print("❌ psutil")
    
    try:
        import pytest
        print("✅ pytest")
    except ImportError:
        print("❌ pytest")
    
    print()

def run_quick_tests():
    """Run quick validation tests."""
    print("🧪 Quick Tests")
    print("-" * 30)
    
    project_root = get_project_root()
    
    # Test a simple performance test
    test_file = project_root / "tests" / "performance" / "simple_test.py"
    if test_file.exists():
        try:
            import subprocess
            result = subprocess.run([sys.executable, str(test_file)], 
                                  cwd=str(project_root), 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.returncode == 0:
                print("✅ Performance test: PASSED")
            else:
                print("❌ Performance test: FAILED")
                print(f"   Error: {result.stderr[:100]}...")
        except Exception as e:
            print(f"❌ Performance test: ERROR - {e}")
    else:
        print("⚠️  Performance test: File not found")
    
    print()

def generate_report():
    """Generate a comprehensive diagnostic report."""
    print("📋 Diagnostic Report")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"💻 Platform: {sys.platform}")
    print()
    
    checks = [
        ("System Resources", check_system_resources),
        ("Database Status", check_database_status),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Quick Tests", run_quick_tests)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result if isinstance(result, bool) else True
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results[name] = False
    
    # Summary
    print("📊 Summary")
    print("-" * 30)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System health: EXCELLENT")
        return True
    elif passed >= total * 0.8:
        print("⚠️  System health: GOOD (minor issues)")
        return True
    else:
        print("❌ System health: NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = generate_report()
    sys.exit(0 if success else 1)
