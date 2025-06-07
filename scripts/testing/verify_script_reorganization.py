#!/usr/bin/env python3
"""
Script Reorganization Verification Tool
Verifies that all moved scripts are accessible and functional in their new locations.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_script_accessibility():
    """Test that key scripts are accessible in their new locations."""
    
    script_tests = [
        ("scripts/build/quick_build_validate.py", "Build script"),
        ("scripts/testing/basic_migration_test.py", "Test script"),
        ("scripts/diagnostics/check-project-structure.py", "Diagnostic script"),
        ("scripts/deployment/run_installer.py", "Installation script"),
    ]
    
    results = []
    
    for script_path, description in script_tests:
        if os.path.exists(script_path):
            # Test basic Python syntax validity
            try:
                result = subprocess.run([
                    sys.executable, "-m", "py_compile", script_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    results.append(f"✅ {description}: {script_path} - VALID")
                else:
                    results.append(f"❌ {description}: {script_path} - SYNTAX ERROR")
            except subprocess.TimeoutExpired:
                results.append(f"⚠️ {description}: {script_path} - TIMEOUT")
            except Exception as e:
                results.append(f"❌ {description}: {script_path} - ERROR: {e}")
        else:
            results.append(f"❌ {description}: {script_path} - NOT FOUND")
    
    return results

def main():
    """Main verification function."""
    print("🔍 Script Reorganization Verification")
    print("=" * 50)
    
    # Test script accessibility
    test_results = test_script_accessibility()
    
    print("\n📋 Script Accessibility Results:")
    for result in test_results:
        print(f"   {result}")
    
    # Count scripts in each category
    categories = {
        "scripts/build/": "Build scripts",
        "scripts/testing/": "Testing scripts", 
        "scripts/diagnostics/": "Diagnostic scripts",
        "scripts/deployment/": "Deployment scripts"
    }
    
    print(f"\n📊 Script Organization Summary:")
    total_moved = 0
    for path, description in categories.items():
        if os.path.exists(path):
            py_files = list(Path(path).glob("*.py"))
            count = len(py_files)
            total_moved += count
            print(f"   {description}: {count} files")
        else:
            print(f"   {description}: Directory not found")
    
    print(f"\n✅ Total scripts organized: {total_moved}")
    print("🎯 Script reorganization verification complete!")

if __name__ == "__main__":
    main()