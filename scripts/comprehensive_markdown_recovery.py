#!/usr/bin/env python3
"""
Comprehensive Markdown Recovery Script

Restores ALL markdown files damaged by broken markdown fixing scripts.
Uses git to identify modified files and restores them from git history.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to {description}: {e}")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return None

def main():
    """Restore all damaged markdown files."""
    
    print("🔄 Comprehensive Markdown Recovery")
    print("=" * 50)
    
    # First, get list of all modified markdown files
    print("📋 Finding modified markdown files...")
    modified_files = run_command("git status --porcelain | grep '\\.md$' | cut -c4-", "get modified files")
    
    if not modified_files:
        print("✅ No modified markdown files found!")
        return 0
    
    modified_file_list = [f.strip() for f in modified_files.split('\n') if f.strip()]
    print(f"📝 Found {len(modified_file_list)} modified markdown files")
    
    # Show what will be restored
    print("\n📁 Files to be restored:")
    for file_path in modified_file_list:
        print(f"   • {file_path}")
    
    # Auto-proceed with recovery since this is an emergency repair
    print(f"\n⚠️  Proceeding with restoration of {len(modified_file_list)} markdown files from git history.")
    
    # Restore files using git checkout
    restored_count = 0
    failed_count = 0
    
    print("\n🔄 Restoring files...")
    
    for file_path in modified_file_list:
        # Use git checkout to restore from HEAD
        result = run_command(f"git checkout HEAD -- '{file_path}'", f"restore {file_path}")
        
        if result is not None:
            print(f"✅ Restored: {file_path}")
            restored_count += 1
        else:
            print(f"❌ Failed to restore: {file_path}")
            failed_count += 1
    
    print("\n📊 Recovery Summary:")
    print(f"   ✅ Restored: {restored_count} files")
    print(f"   ❌ Failed: {failed_count} files")
    
    if failed_count == 0:
        print("\n🎉 Comprehensive recovery completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check a few restored files to verify they look correct")
        print("   2. The broken scripts remain disabled (.DISABLED extension)")
        print("   3. All markdown files should now be clean and properly formatted")
    else:
        print("\n⚠️  Recovery completed with some failures")
        print("   Check failed files manually if needed")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())