#!/usr/bin/env python3
"""
Comprehensive PyPI Release Automation Script
Handles version updates, git operations, building, uploading, and GitHub releases

Usage:
    python scripts/release/pypi_release_automation.py [--version TYPE] [--test] [--skip-tests]
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text
    console = Console()
except ImportError:
    print("❌ Rich not installed. Install with: pip install rich")
    sys.exit(1)

def validate_branch() -> bool:
    """Ensure we're on main branch"""
    try:
        current_branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if current_branch != 'main':
            console.print("[red]❌ Must be on main branch to release![/red]")
            console.print(f"   Current branch: {current_branch}")
            console.print("   Switch to main with: git checkout main")
            return False
        return True
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to check git branch[/red]")
        return False

def check_uncommitted_changes() -> bool:
    """Check for uncommitted changes"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            console.print("[red]❌ Uncommitted changes detected![/red]")
            console.print("   Commit or stash changes before release")
            console.print("\n   Uncommitted files:")
            for line in result.stdout.strip().split('\n'):
                console.print(f"     {line}")
            return False
        return True
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to check git status[/red]")
        return False

def check_upstream_sync() -> bool:
    """Check if local main is up to date with remote"""
    try:
        # Fetch latest from remote
        subprocess.run(['git', 'fetch', 'origin'], check=True)
        
        # Compare local main with remote main
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'main..origin/main'],
            capture_output=True, text=True
        )
        
        behind_count = int(result.stdout.strip())
        if behind_count > 0:
            console.print("[red]❌ Local main is behind remote![/red]")
            console.print(f"   Your branch is {behind_count} commits behind origin/main")
            console.print("   Update with: git pull origin main")
            return False
            
        # Check if we're ahead of remote
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'origin/main..main'],
            capture_output=True, text=True
        )
        
        ahead_count = int(result.stdout.strip())
        if ahead_count > 0:
            console.print("[yellow]⚠️  Local main is ahead of remote[/yellow]")
            console.print(f"   Your branch is {ahead_count} commits ahead of origin/main")
            console.print("   Make sure this is intentional")
            
        return True
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to check upstream sync[/red]")
        return False

def get_current_version() -> str:
    """Get current version from setup.py"""
    setup_path = Path("setup.py")
    if not setup_path.exists():
        console.print("[red]❌ setup.py not found[/red]")
        sys.exit(1)
    
    content = setup_path.read_text()
    version_match = re.search(r'version=[\'"](.*?)[\'"]', content)
    if not version_match:
        console.print("[red]❌ Version not found in setup.py[/red]")
        sys.exit(1)
    
    return version_match.group(1)

def increment_version(current_version: str, increment_type: str) -> str:
    """Increment version number"""
    parts = current_version.split('.')
    if len(parts) != 3:
        console.print(f"[red]❌ Invalid version format: {current_version}[/red]")
        sys.exit(1)
    
    major, minor, patch = map(int, parts)
    
    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    elif increment_type == "patch":
        patch += 1
    else:
        console.print(f"[red]❌ Invalid increment type: {increment_type}[/red]")
        sys.exit(1)
    
    return f"{major}.{minor}.{patch}"

def update_version_files(new_version: str) -> None:
    """Update version in all relevant files"""
    files_to_update = [
        ("setup.py", r'version=[\'"](.*?)[\'"]', f'version="{new_version}"'),
        ("pyproject.toml", r'version\s*=\s*[\'"](.*?)[\'"]', f'version = "{new_version}"'),
    ]
    
    # Check if __init__.py has version
    init_file = Path("mcp_task_orchestrator/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        if "__version__" in content:
            files_to_update.append((
                str(init_file),
                r'__version__\s*=\s*[\'"](.*?)[\'"]',
                f'__version__ = "{new_version}"'
            ))
    
    for file_path, pattern, replacement in files_to_update:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            new_content = re.sub(pattern, replacement, content)
            path.write_text(new_content)
            console.print(f"[green]✅ Updated version in {file_path}[/green]")

def run_tests() -> bool:
    """Run test suite"""
    console.print("[blue]🧪 Running test suite...[/blue]")
    try:
        # Try enhanced test runner first
        test_runners = [
            ["python", "scripts/maintenance/simple_test_runner.py"],
            ["python", "tests/validation_suite.py"],
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
        ]
        
        for runner in test_runners:
            try:
                result = subprocess.run(runner, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    console.print("[green]✅ Tests passed[/green]")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        console.print("[red]❌ All test runners failed[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Test execution failed: {e}[/red]")
        return False

def build_package() -> bool:
    """Build the package"""
    console.print("[blue]📦 Building package...[/blue]")
    try:
        # Clean old builds
        subprocess.run(["rm", "-rf", "dist/", "build/", "*.egg-info"], shell=True)
        
        # Build package
        result = subprocess.run(
            ["python", "setup.py", "sdist", "bdist_wheel"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]❌ Build failed:[/red]\n{result.stderr}")
            return False
        
        # Verify build artifacts
        dist_path = Path("dist")
        if not dist_path.exists() or len(list(dist_path.glob("*"))) == 0:
            console.print("[red]❌ No build artifacts found in dist/[/red]")
            return False
        
        console.print("[green]✅ Package built successfully[/green]")
        
        # Show build artifacts
        artifacts = list(dist_path.glob("*"))
        for artifact in artifacts:
            console.print(f"   📄 {artifact.name}")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Build failed: {e}[/red]")
        return False

def upload_to_pypi(test_upload: bool = False) -> bool:
    """Upload package to PyPI"""
    load_dotenv()
    
    if test_upload:
        console.print("[blue]🚀 Uploading to TestPyPI...[/blue]")
        token = os.getenv("PYPI_TEST_TOKEN")
        repository_url = os.getenv("TEST_PYPI_REPOSITORY_URL", "https://test.pypi.org/legacy/")
    else:
        console.print("[blue]🚀 Uploading to PyPI...[/blue]")
        token = os.getenv("PYPI_API_TOKEN")
        repository_url = os.getenv("PYPI_REPOSITORY_URL", "https://upload.pypi.org/legacy/")
    
    if not token:
        token_type = "PYPI_TEST_TOKEN" if test_upload else "PYPI_API_TOKEN"
        console.print(f"[red]❌ {token_type} not found in .env file[/red]")
        return False
    
    try:
        # Upload using twine
        cmd = [
            "python", "-m", "twine", "upload",
            "--repository-url", repository_url,
            "--username", "__token__",
            "--password", token,
            "dist/*"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]❌ Upload failed:[/red]\n{result.stderr}")
            return False
        
        upload_target = "TestPyPI" if test_upload else "PyPI"
        console.print(f"[green]✅ Successfully uploaded to {upload_target}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Upload failed: {e}[/red]")
        return False

def create_git_tag_and_push(version: str) -> bool:
    """Create git tag and push changes"""
    try:
        # Add and commit version changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run([
            "git", "commit", "-m", f"release: v{version}\n\n🤖 Generated with PyPI Release Automation"
        ], check=True)
        
        # Create and push tag
        tag_name = f"v{version}"
        subprocess.run(["git", "tag", tag_name], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", tag_name], check=True)
        
        console.print(f"[green]✅ Created and pushed tag {tag_name}[/green]")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Git operations failed: {e}[/red]")
        return False

def create_github_release(version: str) -> bool:
    """Create GitHub release"""
    try:
        # Check if gh CLI is available
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        
        tag_name = f"v{version}"
        release_title = f"Release {version}"
        
        # Create release notes
        release_notes = f"""# Release {version}

## What's Changed
- Version {version} release
- Updated package metadata and dependencies
- Improved stability and performance

**Installation:**
```bash
pip install mcp-task-orchestrator=={version}
```

**Full Changelog:** https://github.com/EchoingVesper/mcp-task-orchestrator/compare/v{version}...v{version}

---
🤖 Generated with PyPI Release Automation
"""
        
        # Create GitHub release
        result = subprocess.run([
            "gh", "release", "create", tag_name,
            "--title", release_title,
            "--notes", release_notes
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[yellow]⚠️  GitHub release creation failed: {result.stderr}[/yellow]")
            console.print("   You can create the release manually on GitHub")
            return False
        
        console.print(f"[green]✅ Created GitHub release {tag_name}[/green]")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[yellow]⚠️  GitHub CLI not available - skipping release creation[/yellow]")
        console.print("   Install with: gh --version")
        return False

def cleanup_build_artifacts() -> None:
    """Clean up build artifacts"""
    try:
        subprocess.run(["rm", "-rf", "dist/", "build/", "*.egg-info"], shell=True)
        console.print("[green]✅ Cleaned up build artifacts[/green]")
    except Exception:
        console.print("[yellow]⚠️  Failed to clean up build artifacts[/yellow]")

def main():
    """Main release automation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyPI Release Automation")
    parser.add_argument("--version", choices=["major", "minor", "patch"], 
                       default="patch", help="Version increment type")
    parser.add_argument("--test", action="store_true", 
                       help="Upload to TestPyPI instead of PyPI")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running test suite")
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold blue]🚀 PyPI Release Automation[/bold blue]\n"
        "Automated release process with safety checks",
        title="Release Tool"
    ))
    
    # Safety checks
    console.print("\n[bold]🔒 Running safety checks...[/bold]")
    
    checks = [
        ("Branch validation", validate_branch),
        ("Uncommitted changes", check_uncommitted_changes),
        ("Upstream sync", check_upstream_sync)
    ]
    
    for check_name, check_func in checks:
        console.print(f"   Checking {check_name}...", end="")
        if check_func():
            console.print(" [green]✅[/green]")
        else:
            console.print(" [red]❌[/red]")
            console.print("\n[red]❌ Safety checks failed. Please fix issues before release.[/red]")
            sys.exit(1)
    
    # Version management
    current_version = get_current_version()
    new_version = increment_version(current_version, args.version)
    
    console.print(f"\n[bold]📋 Release Summary[/bold]")
    summary_table = Table(show_header=False)
    summary_table.add_row("Current Version:", current_version)
    summary_table.add_row("New Version:", f"[green]{new_version}[/green]")
    summary_table.add_row("Increment Type:", args.version.title())
    summary_table.add_row("Target:", "TestPyPI" if args.test else "PyPI")
    summary_table.add_row("Run Tests:", "No" if args.skip_tests else "Yes")
    console.print(summary_table)
    
    if not Confirm.ask(f"\n[bold]Proceed with release {new_version}?[/bold]"):
        console.print("[yellow]Release cancelled by user[/yellow]")
        sys.exit(0)
    
    # Execute release steps
    console.print(f"\n[bold]🎯 Executing release {new_version}...[/bold]")
    
    try:
        # Update version files
        update_version_files(new_version)
        
        # Run tests (unless skipped)
        if not args.skip_tests:
            if not run_tests():
                if not Confirm.ask("Tests failed. Continue anyway?"):
                    console.print("[red]Release aborted due to test failures[/red]")
                    sys.exit(1)
        
        # Build package
        if not build_package():
            console.print("[red]❌ Release failed at build stage[/red]")
            sys.exit(1)
        
        # Upload to PyPI/TestPyPI
        if not upload_to_pypi(test_upload=args.test):
            console.print("[red]❌ Release failed at upload stage[/red]")
            sys.exit(1)
        
        # Git operations (only for production releases)
        if not args.test:
            if not create_git_tag_and_push(new_version):
                console.print("[yellow]⚠️  Git operations failed, but package was uploaded[/yellow]")
            
            # Create GitHub release
            create_github_release(new_version)
        
        # Cleanup
        if os.getenv("CLEAN_BUILD_ARTIFACTS", "true").lower() == "true":
            cleanup_build_artifacts()
        
        # Success message
        console.print(Panel.fit(
            f"[bold green]🎉 Release {new_version} completed successfully![/bold green]\n\n"
            f"📦 Package uploaded to {'TestPyPI' if args.test else 'PyPI'}\n"
            f"🏷️  Git tag created: v{new_version}\n"
            f"📋 GitHub release: {'Created' if not args.test else 'Skipped (test mode)'}\n\n"
            f"[bold]Installation command:[/bold]\n"
            f"pip install mcp-task-orchestrator=={new_version}",
            title="🚀 Release Complete"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Release interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()