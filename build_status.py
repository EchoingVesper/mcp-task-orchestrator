#!/usr/bin/env python3
"""Check build status and provide validation report"""

import os
import sys
import re
from pathlib import Path

def check_build_status():
    """Check the current build status"""
    project_root = Path(__file__).parent
    
    print("🔍 MCP Task Orchestrator - Build Status Report")
    print("=" * 55)
    
    # Check version consistency
    print("\n📊 Version Check:")
    
    # Check setup.py version
    setup_file = project_root / 'setup.py'
    if setup_file.exists():
        with open(setup_file, 'r') as f:
            content = f.read()
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                setup_version = version_match.group(1)
                print(f"  setup.py: {setup_version}")
            else:
                print("  setup.py: ❌ Version not found")
                setup_version = None
    else:
        print("  setup.py: ❌ File not found")
        setup_version = None
    
    # Check __init__.py version
    init_file = project_root / 'mcp_task_orchestrator' / '__init__.py'
    if init_file.exists():
        with open(init_file, 'r') as f:
            content = f.read()
            version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                init_version = version_match.group(1)
                print(f"  __init__.py: {init_version}")
            else:
                print("  __init__.py: ❌ Version not found")
                init_version = None
    else:
        print("  __init__.py: ❌ File not found")
        init_version = None
    
    # Version consistency check
    if setup_version and init_version and setup_version == init_version:
        if setup_version == "1.6.0":
            print(f"  ✅ Version consistency: {setup_version}")
        else:
            print(f"  ⚠️  Version is {setup_version}, expected 1.6.0")
    else:
        print("  ❌ Version mismatch or missing")
    
    # Check package structure
    print("\n📂 Package Structure:")
    
    required_files = [
        'setup.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'mcp_task_orchestrator/__init__.py',
        'mcp_task_orchestrator/server.py',
        'mcp_task_orchestrator_cli/__init__.py',
        'mcp_task_orchestrator_cli/cli.py',
    ]
    
    new_features = [
        'mcp_task_orchestrator/db/auto_migration.py',
        'mcp_task_orchestrator/db/migration_manager.py',
        'mcp_task_orchestrator/server/reboot_tools.py',
        'mcp_task_orchestrator/server/restart_manager.py',
    ]
    
    missing_required = []
    missing_features = []
    
    for file_path in required_files:
        if (project_root / file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (CRITICAL)")
            missing_required.append(file_path)
    
    for file_path in new_features:
        if (project_root / file_path).exists():
            print(f"  ✅ {file_path} (NEW)")
        else:
            print(f"  ❌ {file_path} (NEW FEATURE)")
            missing_features.append(file_path)
    
    # Check build artifacts
    print("\n📦 Build Artifacts:")
    
    dist_dir = project_root / 'dist'
    if dist_dir.exists():
        files = list(dist_dir.iterdir())
        if files:
            print(f"  📁 Found {len(files)} files in dist/:")
            
            source_dists = [f for f in files if f.name.endswith('.tar.gz')]
            wheel_dists = [f for f in files if f.name.endswith('.whl')]
            
            for file in files:
                size_mb = file.stat().st_size / (1024 * 1024)
                file_type = ""
                if file.name.endswith('.tar.gz'):
                    file_type = " (source)"
                elif file.name.endswith('.whl'):
                    file_type = " (wheel)"
                
                # Check if version is correct
                version_ok = "1.6.0" in file.name
                version_indicator = " ✅" if version_ok else " ❌"
                
                print(f"    • {file.name} ({size_mb:.2f} MB){file_type}{version_indicator}")
            
            # Summary
            if source_dists and wheel_dists:
                print(f"  ✅ Both source ({len(source_dists)}) and wheel ({len(wheel_dists)}) distributions present")
            else:
                if not source_dists:
                    print("  ❌ No source distributions found")
                if not wheel_dists:
                    print("  ❌ No wheel distributions found")
                    
        else:
            print("  ❌ dist/ directory is empty")
    else:
        print("  ❌ No dist/ directory found")
    
    # Check for old build artifacts
    old_artifacts = []
    for dirname in ['build', 'mcp_task_orchestrator.egg-info']:
        if (project_root / dirname).exists():
            old_artifacts.append(dirname)
    
    if old_artifacts:
        print(f"\n⚠️  Old build artifacts present: {', '.join(old_artifacts)}")
        print("  Consider cleaning before final release")
    
    # Overall status
    print("\n📋 Overall Status:")
    
    issues = []
    if missing_required:
        issues.append(f"{len(missing_required)} critical files missing")
    if missing_features:
        issues.append(f"{len(missing_features)} new feature files missing")
    if setup_version != "1.6.0" or init_version != "1.6.0":
        issues.append("Version not set to 1.6.0")
    if not dist_dir.exists() or not list(dist_dir.iterdir()):
        issues.append("No distribution packages built")
    
    if issues:
        print("  ❌ Issues found:")
        for issue in issues:
            print(f"    • {issue}")
        print("\n🔧 Recommended actions:")
        if missing_required or missing_features:
            print("    • Verify all required files are present")
        if setup_version != "1.6.0" or init_version != "1.6.0":
            print("    • Update version numbers to 1.6.0")
        if not dist_dir.exists() or not list(dist_dir.iterdir()):
            print("    • Run: python setup.py sdist bdist_wheel")
    else:
        print("  ✅ Ready for PyPI release!")
        print("\n🚀 Next steps:")
        print("    • Test upload: python scripts/release/upload.py --test")
        print("    • Production upload: python scripts/release/upload.py")
    
    return len(issues) == 0

if __name__ == '__main__':
    success = check_build_status()
    sys.exit(0 if success else 1)