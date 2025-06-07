#!/usr/bin/env python3
"""
MCP Task Orchestrator - Project Structure Validator

Validates that the project organization follows established standards and
identifies potential issues with file placement and structure.

Usage:
    python3 scripts/diagnostics/check-project-structure.py
    # OR (if python-is-python3 installed):
    python scripts/diagnostics/check-project-structure.py
    # OR (from activated venv):
    source venv_mcp/bin/activate && python scripts/diagnostics/check-project-structure.py

Returns:
    Exit code 0: All checks passed
    Exit code 1: Issues found that need attention

Requirements:
    - Python 3.8+ (system-wide or in activated virtual environment)
    - No additional dependencies required
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def check_python_setup():
    """Check Python setup and provide guidance if needed."""
    print(f"🐍 Python version: {sys.version}")
    print(f"📍 Python executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("ℹ️  Running with system Python")
    
    print()


def check_root_files() -> List[str]:
    """Check root directory file count and types."""
    root = Path(".")
    files = [f for f in root.iterdir() if f.is_file() and not f.name.startswith('.')]
    issues = []
    
    # Check total file count
    if len(files) > 15:
        issues.append(f"❌ Too many root files: {len(files)} (should be ≤15)")
    
    # Check for misplaced scripts
    misplaced_scripts = [f for f in files if f.name.startswith(('test_', 'build_', 'validate_', 'execute_', 'run_', 'simple_', 'comprehensive_', 'final_', 'quick_', 'manual_', 'standalone_', 'server_', 'migration_'))]
    if misplaced_scripts:
        issues.append(f"❌ Misplaced scripts in root: {[f.name for f in misplaced_scripts]}")
    
    # Check for misplaced documentation
    allowed_docs = ['README.md', 'CONTRIBUTING.md', 'TROUBLESHOOTING.md', 'QUICK_START.md', 'CHANGELOG.md']
    misplaced_docs = [f for f in files if f.suffix == '.md' and f.name not in allowed_docs]
    if misplaced_docs:
        issues.append(f"❌ Misplaced documentation in root: {[f.name for f in misplaced_docs]}")
    
    # Check for temporary files
    temp_patterns = ['temp', 'tmp', 'session', 'debug', 'test-', 'backup']
    temp_files = [f for f in files if any(pattern in f.name.lower() for pattern in temp_patterns)]
    if temp_files:
        issues.append(f"❌ Temporary files in root: {[f.name for f in temp_files]}")
    
    if not issues:
        print(f"✅ Root directory: {len(files)} files (within limits)")
    
    return issues


def check_directory_structure() -> List[str]:
    """Verify expected directory structure exists."""
    expected_dirs = [
        'docs',
        'docs/development',
        'docs/testing', 
        'docs/releases',
        'docs/user-guide',
        'scripts',
        'scripts/build',
        'scripts/testing',
        'scripts/diagnostics',
        'mcp_task_orchestrator',
        'tests'
    ]
    
    issues = []
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            issues.append(f"❌ Missing directory: {dir_path}")
    
    if not issues:
        print("✅ Directory structure: All expected directories present")
    
    return issues


def check_virtual_environments() -> List[str]:
    """Check for multiple virtual environments."""
    root = Path(".")
    venvs = [d for d in root.iterdir() if d.is_dir() and d.name.startswith('venv')]
    issues = []
    
    if len(venvs) > 1:
        issues.append(f"❌ Multiple virtual environments: {[v.name for v in venvs]} (should be 1)")
    elif len(venvs) == 0:
        issues.append("⚠️  No virtual environment found (consider creating venv_mcp/)")
    else:
        print(f"✅ Virtual environment: {venvs[0].name} (single env)")
    
    return issues


def check_build_artifacts() -> List[str]:
    """Check for build artifacts that should be cleaned."""
    artifacts = ['build', 'dist']
    egg_info = list(Path(".").glob("*.egg-info"))
    
    issues = []
    for artifact in artifacts:
        if Path(artifact).exists():
            issues.append(f"❌ Build artifact exists: {artifact}/ (should be cleaned)")
    
    if egg_info:
        issues.append(f"❌ Egg-info artifacts: {[d.name for d in egg_info]} (should be cleaned)")
    
    if not issues:
        print("✅ Build artifacts: Clean (no build artifacts)")
    
    return issues


def check_file_organization() -> List[str]:
    """Check that files are properly organized by type."""
    issues = []
    
    # Check docs organization
    docs_path = Path("docs")
    if docs_path.exists():
        # Find any .md files in wrong locations
        for subdir in ['development', 'testing', 'releases']:
            subdir_path = docs_path / subdir
            if subdir_path.exists():
                md_files = list(subdir_path.glob("*.md"))
                # Check for files that might belong elsewhere
                for md_file in md_files:
                    if 'COMPREHENSIVE' in md_file.name.upper() and subdir != 'testing':
                        issues.append(f"⚠️  Possible misplaced file: {md_file} (comprehensive reports usually go in testing/)")
    
    # Check scripts organization
    scripts_path = Path("scripts")
    if scripts_path.exists():
        for subdir in ['build', 'testing', 'diagnostics']:
            subdir_path = scripts_path / subdir
            if subdir_path.exists():
                py_files = list(subdir_path.glob("*.py"))
                # Check for potential misplacements
                for py_file in py_files:
                    if 'test' in py_file.name.lower() and subdir != 'testing':
                        issues.append(f"⚠️  Possible misplaced file: {py_file} (test scripts usually go in testing/)")
                    elif any(term in py_file.name.lower() for term in ['build', 'package', 'release']) and subdir != 'build':
                        issues.append(f"⚠️  Possible misplaced file: {py_file} (build scripts usually go in build/)")
    
    if not issues:
        print("✅ File organization: Files appear properly organized")
    
    return issues


def check_gitignore_completeness() -> List[str]:
    """Check that .gitignore covers common patterns."""
    gitignore_path = Path(".gitignore")
    issues = []
    
    if not gitignore_path.exists():
        issues.append("❌ No .gitignore file found")
        return issues
    
    try:
        gitignore_content = gitignore_path.read_text()
    except Exception as e:
        issues.append(f"❌ Could not read .gitignore: {e}")
        return issues
    
    # Check for essential patterns
    essential_patterns = [
        '__pycache__',
        '*.egg-info',
        'build/',
        'dist/',
        '.pytest_cache',
        'venv',
        '.env'
    ]
    
    missing_patterns = []
    for pattern in essential_patterns:
        if pattern not in gitignore_content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        issues.append(f"⚠️  Missing .gitignore patterns: {missing_patterns}")
    
    # Check for Claude Code specific patterns
    claude_patterns = ['.claude/', '.tools/', 'temp/', '*-session.md']
    missing_claude = []
    for pattern in claude_patterns:
        if pattern not in gitignore_content:
            missing_claude.append(pattern)
    
    if missing_claude:
        issues.append(f"⚠️  Missing Claude Code patterns in .gitignore: {missing_claude}")
    
    if not issues:
        print("✅ .gitignore: Contains essential patterns")
    
    return issues


def generate_summary_report() -> Dict[str, any]:
    """Generate a summary report of project structure health."""
    root = Path(".")
    
    # Count files by type
    file_counts = {
        'root_files': len([f for f in root.iterdir() if f.is_file() and not f.name.startswith('.')]),
        'docs_files': len(list(Path("docs").rglob("*.md"))) if Path("docs").exists() else 0,
        'script_files': len(list(Path("scripts").rglob("*.py"))) if Path("scripts").exists() else 0,
        'test_files': len(list(Path("tests").rglob("*.py"))) if Path("tests").exists() else 0,
        'virtual_envs': len([d for d in root.iterdir() if d.is_dir() and d.name.startswith('venv')]),
    }
    
    # Calculate health score (0-100)
    score = 100
    if file_counts['root_files'] > 15:
        score -= min(30, (file_counts['root_files'] - 15) * 2)
    if file_counts['virtual_envs'] > 1:
        score -= (file_counts['virtual_envs'] - 1) * 10
    if Path("build").exists() or Path("dist").exists():
        score -= 10
    
    return {
        'file_counts': file_counts,
        'health_score': max(0, score),
        'timestamp': Path().absolute().name
    }


def provide_setup_guidance():
    """Provide guidance for Python setup issues."""
    print("🔧 Python Setup Options:")
    print()
    print("   1. Quick fix - Use python3:")
    print("      python3 scripts/diagnostics/check-project-structure.py")
    print()
    print("   2. WSL recommended - Install python-is-python3:")
    print("      sudo apt update")
    print("      sudo apt install python-is-python3")
    print()
    print("   3. Use project virtual environment:")
    print("      source venv_mcp/bin/activate")
    print("      python scripts/diagnostics/check-project-structure.py")
    print()
    print("   4. System-wide Python (if needed):")
    print("      sudo apt install python3 python3-pip")
    print()


def main():
    """Run all structure checks and generate report."""
    print("🔍 MCP Task Orchestrator - Project Structure Validator")
    print("=" * 55)
    print()
    
    # Check Python setup first
    check_python_setup()
    
    all_issues = []
    
    try:
        # Run all checks
        all_issues.extend(check_root_files())
        all_issues.extend(check_directory_structure())
        all_issues.extend(check_virtual_environments())
        all_issues.extend(check_build_artifacts())
        all_issues.extend(check_file_organization())
        all_issues.extend(check_gitignore_completeness())
        
        print()
        
        # Generate summary
        summary = generate_summary_report()
        print("📊 Project Structure Summary:")
        print(f"   Root files: {summary['file_counts']['root_files']} (target: ≤15)")
        print(f"   Documentation files: {summary['file_counts']['docs_files']}")
        print(f"   Script files: {summary['file_counts']['script_files']}")
        print(f"   Test files: {summary['file_counts']['test_files']}")
        print(f"   Virtual environments: {summary['file_counts']['virtual_envs']} (target: 1)")
        print(f"   Health score: {summary['health_score']}/100")
        print()
        
        # Report results
        if all_issues:
            print("❌ Issues found that need attention:")
            for issue in all_issues:
                print(f"   {issue}")
            print()
            print("📋 Recommended actions:")
            print("   1. Move misplaced files to appropriate directories")
            print("   2. Clean up build artifacts: rm -rf build/ dist/ *.egg-info/")
            print("   3. Remove extra virtual environments")
            print("   4. Update .gitignore with missing patterns")
            print("   5. Follow cleanup guide: scripts/build/project-cleanup-instructions.md")
            print()
            sys.exit(1)
        else:
            print("🎉 Excellent! Project structure follows all best practices.")
            print()
            if summary['health_score'] == 100:
                print("💯 Perfect health score!")
            print("✅ Ready for professional development")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🔧 If this is a Python setup issue:")
        provide_setup_guidance()
        sys.exit(1)


if __name__ == "__main__":
    main()
