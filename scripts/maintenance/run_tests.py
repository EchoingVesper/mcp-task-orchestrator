#!/usr/bin/env python3
"""
Test Runner for MCP Task Orchestrator

This script provides a unified interface for running the test suite
with proper organization and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import time

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

def run_command(cmd, cwd=None, timeout=300):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def run_performance_tests():
    """Run performance tests."""
    print("🚀 Running Performance Tests...")
    project_root = get_project_root()
    
    # Run performance benchmarks
    performance_dir = project_root / "tests" / "performance"
    if not performance_dir.exists():
        print("❌ Performance test directory not found")
        return False
    
    success = True
    for test_file in performance_dir.glob("*.py"):
        print(f"  Running {test_file.name}...")
        cmd = f"python {test_file}"
        ok, stdout, stderr = run_command(cmd, cwd=project_root)
        
        if ok:
            print(f"  ✅ {test_file.name} - PASSED")
        else:
            print(f"  ❌ {test_file.name} - FAILED")
            if stderr:
                print(f"     Error: {stderr[:100]}...")
            success = False
    
    return success

def run_integration_tests():
    """Run integration tests."""
    print("🔗 Running Integration Tests...")
    project_root = get_project_root()
    
    cmd = "python -m pytest tests/integration/ -v"
    ok, stdout, stderr = run_command(cmd, cwd=project_root)
    
    if ok:
        print("✅ Integration tests - PASSED")
        return True
    else:
        print("❌ Integration tests - FAILED")
        if stderr:
            print(f"Error: {stderr[:200]}...")
        return False
    else:
        # Default: run all tests
        success = run_all_tests()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 50)
    if success:
        print(f"🎉 All tests completed successfully in {duration:.2f} seconds")
        sys.exit(0)
    else:
        print(f"❌ Some tests failed (runtime: {duration:.2f} seconds)")
        print("💡 Check the output above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
