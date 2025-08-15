#!/usr/bin/env python3
"""
Test script to verify the dependency check functionality works correctly.
"""

import sys
from pathlib import Path

def test_dependency_logic():
    """Test the dependency checking logic without CLI dependencies."""
    print("🧪 Testing Dependency Check Logic...")
    
    # Required dependencies for workspace paradigm
    required_deps = [
        "mcp", "pydantic", "jinja2", "pyyaml", "aiofiles", 
        "psutil", "filelock", "sqlalchemy", "alembic"
    ]
    
    missing_deps = []
    available_deps = []
    
    for dep_name in required_deps:
        try:
            import importlib
            module = importlib.import_module(dep_name.replace("-", "_"))
            if hasattr(module, "__version__"):
                version = module.__version__
                print(f"  ✅ {dep_name}: {version}")
                available_deps.append((dep_name, version))
            else:
                print(f"  ✅ {dep_name}: installed")
                available_deps.append((dep_name, "unknown"))
        except ImportError:
            print(f"  ❌ {dep_name}: missing")
            missing_deps.append(dep_name)
    
    print("\n📊 Dependency Status:")
    print(f"  Available: {len(available_deps)}/{len(required_deps)}")
    print(f"  Missing: {len(missing_deps)}/{len(required_deps)}")
    
    if missing_deps:
        print("\n🚨 Missing Dependencies:")
        for dep in missing_deps:
            print(f"    - {dep}")
        
        print("\n💡 Installation Command:")
        if Path("requirements.txt").exists():
            print("    pip install -r requirements.txt")
        else:
            print(f"    pip install {' '.join(missing_deps)}")
        
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

def test_workspace_detection_dependency():
    """Test if workspace detection can work with available dependencies."""
    print("\n🎯 Testing Workspace Detection Dependency...")
    
    try:
        import pydantic
        print(f"  ✅ pydantic available: {pydantic.__version__}")
        print("  ✅ Workspace paradigm should work correctly")
        return True
    except ImportError:
        print("  ❌ pydantic missing: Workspace detection may fail")
        print("  ⚠️ This explains the 80% test success rate")
        return False

if __name__ == "__main__":
    print("🔍 MCP Task Orchestrator Dependency Analysis")
    print("=" * 50)
    
    deps_ok = test_dependency_logic()
    workspace_ok = test_workspace_detection_dependency()
    
    print("\n🎯 Analysis Results:")
    print(f"  Dependencies: {'✅ OK' if deps_ok else '❌ Missing'}")
    print(f"  Workspace Detection: {'✅ Ready' if workspace_ok else '❌ Needs pydantic'}")
    
    if not deps_ok:
        print("\n🔧 Required Action: Install missing dependencies before creating PR")
        sys.exit(1)
    else:
        print("\n✅ Ready for PR: All core dependencies available")
        sys.exit(0)