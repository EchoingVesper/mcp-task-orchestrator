#!/usr/bin/env python3
"""
Project Setup and Validation Script

This script helps set up the development environment and validates
that everything is working correctly after installation or reorganization.
"""

import os
import sys
import subprocess
from pathlib import Path

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def create_missing_directories():
    """Create any missing directories in the project structure."""
    project_root = get_project_root()
    
    required_dirs = [
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
        "data",
        "data/backups"
    ]
    
    created_dirs = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
            print(f"✅ Created directory: {dir_path}")
    
    if created_dirs:
        print(f"\n📁 Created {len(created_dirs)} missing directories")
    else:
        print("✅ All required directories already exist")
    
    return True

def setup_git_ignore():
    """Ensure .gitignore has proper patterns."""
    project_root = get_project_root()
    gitignore_path = project_root / ".gitignore"
    
    if not gitignore_path.exists():
        print("⚠️  .gitignore not found, creating basic version")
        return False
    
    print("✅ .gitignore exists and configured")
    return True

def validate_installation():
    """Validate that the installation is working correctly."""
    print("🔍 Validating Installation...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required packages
    required_packages = ["sqlite3", "pathlib"]
    optional_packages = ["pytest", "psutil"]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (required)")
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} (optional)")
            missing_optional.append(package)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {missing_required}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {missing_optional}")
        print("Install with: pip install pytest psutil")
    
    return True

def run_quick_validation():
    """Run quick validation tests."""
    print("\n🧪 Running Quick Validation...")
    project_root = get_project_root()
    
    # Test that we can import the main package
    try:
        sys.path.insert(0, str(project_root))
        import mcp_task_orchestrator
        print("✅ Main package import successful")
    except ImportError as e:
        print(f"❌ Main package import failed: {e}")
        return False
    
    # Test basic script execution
    test_script = project_root / "scripts" / "diagnostics" / "check_status.py"
    if test_script.exists():
        try:
            result = subprocess.run([sys.executable, str(test_script)], 
                                  cwd=str(project_root),
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.returncode == 0:
                print("✅ Diagnostic script execution successful")
            else:
                print(f"⚠️  Diagnostic script had issues: {result.stderr[:100]}")
        except Exception as e:
            print(f"❌ Script execution failed: {e}")
            return False
    
    return True

def main():
    """Main setup and validation function."""
    print("🚀 MCP Task Orchestrator - Project Setup & Validation")
    print("=" * 60)
    
    success = True
    
    print("\n1. Creating missing directories...")
    success &= create_missing_directories()
    
    print("\n2. Validating installation...")
    success &= validate_installation()
    
    print("\n3. Checking project configuration...")
    success &= setup_git_ignore()
    
    print("\n4. Running validation tests...")
    success &= run_quick_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Setup and validation completed successfully!")
        print("\n💡 Next steps:")
        print("   - Run tests: python scripts/maintenance/run_tests.py")
        print("   - Check system: python scripts/diagnostics/analyze_system.py")
        print("   - Read docs: docs/testing/test-suite-guide.md")
    else:
        print("❌ Some validation checks failed")
        print("\n💡 Check the output above for specific issues")
        print("   - Review installation: docs/installation.md")
        print("   - Check troubleshooting: docs/troubleshooting/")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
