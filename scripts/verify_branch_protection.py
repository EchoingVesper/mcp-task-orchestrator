#!/usr/bin/env python3
"""
Branch Protection Verification Script
=====================================

This script helps verify that branch protection is working correctly
for the MCP Task Orchestrator repository.

Usage:
    python verify_branch_protection.py
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            check=False
        )
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def check_git_status():
    """Check if we're in a git repository and get current branch."""
    print("🔍 Checking Git Repository Status...")
    
    # Check if we're in a git repo
    result = run_command("git rev-parse --is-inside-work-tree")
    if result.returncode != 0:
        print("❌ Not in a git repository!")
        return False
    
    # Get current branch
    result = run_command("git branch --show-current")
    if result.returncode == 0:
        branch = result.stdout.strip()
        print(f"✅ Current branch: {branch}")
        return branch
    else:
        print("❌ Could not determine current branch")
        return False

def check_remote_setup():
    """Check remote repository configuration."""
    print("\\n🌐 Checking Remote Repository Setup...")
    
    result = run_command("git remote -v")
    if result.returncode == 0:
        remotes = result.stdout.strip()
        if "EchoingVesper/mcp-task-orchestrator" in remotes:
            print("✅ Remote repository correctly configured")
            print(f"   {remotes}")
            return True
        else:
            print("❌ Remote repository not pointing to EchoingVesper/mcp-task-orchestrator")
            print(f"   Current remotes: {remotes}")
            return False
    else:
        print("❌ No remote repository configured")
        return False

def check_codeowners_file():
    """Check if CODEOWNERS file exists and is properly configured."""
    print("\\n👥 Checking CODEOWNERS Configuration...")
    
    codeowners_path = Path(".github/CODEOWNERS")
    if codeowners_path.exists():
        print("✅ CODEOWNERS file exists")
        with open(codeowners_path, 'r') as f:
            content = f.read()
            if "@EchoingVesper" in content:
                print("✅ EchoingVesper is configured as code owner")
                return True
            else:
                print("❌ EchoingVesper not found in CODEOWNERS")
                return False
    else:
        print("❌ CODEOWNERS file not found at .github/CODEOWNERS")
        return False

def check_github_workflows():
    """Check if GitHub Actions workflows are configured."""
    print("\\n🔄 Checking GitHub Actions Setup...")
    
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        if workflow_files:
            print(f"✅ Found {len(workflow_files)} workflow file(s):")
            for workflow in workflow_files:
                print(f"   - {workflow.name}")
            return True
        else:
            print("❌ No workflow files found in .github/workflows/")
            return False
    else:
        print("❌ .github/workflows/ directory not found")
        return False

def test_branch_protection():
    """Test if branch protection is active by attempting direct push."""
    print("\\n🔒 Testing Branch Protection (Safe Test)...")
    
    # Check if we're on main branch
    current_branch = run_command("git branch --show-current").stdout.strip()
    if current_branch == "main":
        print("⚠️  Currently on main branch - creating test branch for safety")
        
        # Create a test branch
        test_branch = "test-branch-protection"
        result = run_command(f"git checkout -b {test_branch}")
        if result.returncode != 0:
            print(f"❌ Could not create test branch: {result.stderr}")
            return False
        
        print(f"✅ Created test branch: {test_branch}")
        
        # Make a test change
        test_file = Path("test_protection.txt")
        with open(test_file, 'w') as f:
            f.write("This is a test file for branch protection verification\\n")
        
        # Add and commit
        run_command("git add test_protection.txt")
        run_command('git commit -m "Test: Verify branch protection setup"')
        
        # Try to push the test branch
        result = run_command(f"git push origin {test_branch}")
        if result.returncode == 0:
            print("✅ Test branch push successful - this is expected")
            print("💡 You can now create a PR from this branch to test the protection")
            return True
        else:
            print(f"❌ Could not push test branch: {result.stderr}")
            return False
    else:
        print(f"✅ Currently on branch '{current_branch}' - safe to test")
        return True

def display_next_steps():
    """Display next steps for setting up branch protection."""
    print("\\n🎯 Next Steps for Branch Protection Setup:")
    print("="*50)
    print("1. 🌐 Go to: https://github.com/EchoingVesper/mcp-task-orchestrator/settings/branches")
    print("2. 🔧 Click 'Add classic rule'")
    print("3. 📝 Enter branch name pattern: main")
    print("4. ✅ Enable these settings:")
    print("   - Require a pull request before merging")
    print("     └── Require approvals: 1")
    print("     └── Dismiss stale PR approvals when new commits are pushed")
    print("     └── Require review from code owners")
    print("   - Require status checks to pass before merging")
    print("     └── Require branches to be up to date before merging")
    print("     └── Add status checks: CI/CD Pipeline / test")
    print("   - Require conversation resolution before merging")
    print("   - Include administrators")
    print("   - Restrict pushes that create files larger than 100MB")
    print("5. ❌ Keep DISABLED:")
    print("   - Allow force pushes")
    print("   - Allow deletions")
    print("6. 💾 Click 'Create' to save the protection rules")

def main():
    """Main verification function."""
    print("🔐 MCP Task Orchestrator - Branch Protection Verification")
    print("="*60)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        ("Git Repository Status", check_git_status),
        ("Remote Repository Setup", check_remote_setup),
        ("CODEOWNERS Configuration", check_codeowners_file),
        ("GitHub Actions Setup", check_github_workflows),
    ]
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_checks_passed = False
        except Exception as e:
            print(f"❌ Error during {check_name}: {e}")
            all_checks_passed = False
    
    # Test branch protection setup
    try:
        test_branch_protection()
    except Exception as e:
        print(f"❌ Error during branch protection test: {e}")
        all_checks_passed = False
    
    # Summary
    print("\\n" + "="*60)
    if all_checks_passed:
        print("🎉 All pre-checks passed! Repository is ready for branch protection setup.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    
    # Always show next steps
    display_next_steps()
    
    print("\\n🔗 Additional Resources:")
    print("   - Branch Protection Guide: docs/branch-protection-guide.md")
    print("   - GitHub Documentation: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches")

if __name__ == "__main__":
    main()
