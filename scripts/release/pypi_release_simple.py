#!/usr/bin/env python3
"""
Simple PyPI Release Script (No Interactive Input)
Automated version for CI/CD environments

Usage:
    python scripts/release/pypi_release_simple.py [--version TYPE] [--test]
"""

import os
import sys
import subprocess
import re
import shutil
from pathlib import Path
from dotenv import load_dotenv

def run_cmd(cmd, capture_output=True):
    """Run command and return result"""
    return subprocess.run(cmd, capture_output=capture_output, text=True)

def validate_branch():
    """Ensure we're on main branch"""
    try:
        result = run_cmd(['git', 'branch', '--show-current'])
        current_branch = result.stdout.strip()
        
        if current_branch != 'main':
            print(f"ERROR: Must be on main branch (current: {current_branch})")
            return False
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to check git branch")
        return False

def check_uncommitted_changes():
    """Check for uncommitted changes"""
    try:
        result = run_cmd(['git', 'status', '--porcelain'])
        if result.stdout.strip():
            print("ERROR: Uncommitted changes detected!")
            return False
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to check git status")
        return False

def get_current_version():
    """Get current version from setup.py"""
    setup_path = Path("setup.py")
    content = setup_path.read_text()
    version_match = re.search(r'version=[\'"](.*?)[\'"]', content)
    if not version_match:
        print("ERROR: Version not found in setup.py")
        sys.exit(1)
    return version_match.group(1)

def increment_version(current_version, increment_type):
    """Increment version number"""
    major, minor, patch = map(int, current_version.split('.'))
    
    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    elif increment_type == "patch":
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_version_files(new_version):
    """Update version in all relevant files"""
    files_to_update = [
        ("setup.py", r'version=[\'"](.*?)[\'"]', f'version="{new_version}"'),
        ("pyproject.toml", r'version\s*=\s*[\'"](.*?)[\'"]', f'version = "{new_version}"'),
        ("mcp_task_orchestrator/__init__.py", r'__version__\s*=\s*[\'"](.*?)[\'"]', f'__version__ = "{new_version}"'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            new_content = re.sub(pattern, replacement, content)
            path.write_text(new_content)
            print(f"Updated {file_path}")

def build_package():
    """Build the package"""
    print("Building package...")
    
    # Clean old builds
    for path in ["dist", "build"]:
        if Path(path).exists():
            shutil.rmtree(path)
    
    # Build package
    result = run_cmd([sys.executable, "setup.py", "sdist", "bdist_wheel"])
    
    if result.returncode != 0:
        print(f"ERROR: Build failed:\n{result.stderr}")
        return False
    
    # Verify build artifacts
    dist_path = Path("dist")
    if not dist_path.exists() or len(list(dist_path.glob("*"))) == 0:
        print("ERROR: No build artifacts found")
        return False
    
    print("Package built successfully")
    return True

def upload_to_pypi(test_upload=False):
    """Upload package to PyPI"""
    load_dotenv()
    
    if test_upload:
        print("Uploading to TestPyPI...")
        token = os.getenv("PYPI_TEST_TOKEN")
        repository_url = "https://test.pypi.org/legacy/"
    else:
        print("Uploading to PyPI...")
        token = os.getenv("PYPI_API_TOKEN")
        repository_url = "https://upload.pypi.org/legacy/"
    
    if not token:
        print("ERROR: PyPI token not found in .env file")
        return False
    
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--repository-url", repository_url,
        "--username", "__token__",
        "--password", token,
        "dist/*"
    ]
    
    result = run_cmd(cmd)
    
    if result.returncode != 0:
        print(f"ERROR: Upload failed:\n{result.stderr}")
        return False
    
    print("Upload successful!")
    return True

def create_git_tag_and_push(version):
    """Create git tag and push changes"""
    try:
        # Add and commit version changes
        run_cmd(["git", "add", "."], capture_output=False)
        run_cmd([
            "git", "commit", "-m", 
            f"release: v{version}\n\nAutomated PyPI release with comprehensive automation features"
        ], capture_output=False)
        
        # Create and push tag
        tag_name = f"v{version}"
        run_cmd(["git", "tag", tag_name], capture_output=False)
        run_cmd(["git", "push", "origin", "main"], capture_output=False)
        run_cmd(["git", "push", "origin", tag_name], capture_output=False)
        
        print(f"Created and pushed tag {tag_name}")
        return True
        
    except subprocess.CalledProcessError:
        print("ERROR: Git operations failed")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple PyPI Release Automation")
    parser.add_argument("--version", choices=["major", "minor", "patch"], 
                       default="patch", help="Version increment type")
    parser.add_argument("--test", action="store_true", 
                       help="Upload to TestPyPI instead of PyPI")
    
    args = parser.parse_args()
    
    print("=== PyPI Release Automation ===")
    
    # Safety checks
    print("Running safety checks...")
    if not (validate_branch() and check_uncommitted_changes()):
        print("Safety checks failed!")
        sys.exit(1)
    print("Safety checks passed!")
    
    # Version management
    current_version = get_current_version()
    new_version = increment_version(current_version, args.version)
    
    print(f"Version: {current_version} -> {new_version}")
    print(f"Target: {'TestPyPI' if args.test else 'PyPI'}")
    
    # Execute release
    try:
        update_version_files(new_version)
        
        if not build_package():
            sys.exit(1)
        
        if not upload_to_pypi(test_upload=args.test):
            sys.exit(1)
        
        # Git operations (only for production releases)
        if not args.test and not create_git_tag_and_push(new_version):
            print("WARNING: Git operations failed, but package was uploaded")
        
        print(f"\n=== Release {new_version} COMPLETED ===")
        print(f"Package: {'TestPyPI' if args.test else 'PyPI'}")
        if not args.test:
            print(f"Tag: v{new_version}")
        print(f"Install: pip install mcp-task-orchestrator=={new_version}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()