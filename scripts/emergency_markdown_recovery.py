#!/usr/bin/env python3
"""
Emergency Markdown Recovery Script

Restores clean markdown files from backup to fix damage caused by broken
markdown fixing scripts.
"""

import os
import json
import shutil
from pathlib import Path

def main():
    """Restore clean markdown files from backup."""
    
    # Backup directory with clean files
    backup_dir = Path("backups/recovery_points/20250707_034444")
    docs_dir = Path("docs")
    
    if not backup_dir.exists():
        print(f"❌ Backup directory not found: {backup_dir}")
        return 1
    
    # Load metadata to see what files are available
    metadata_file = backup_dir / "metadata.json"
    if not metadata_file.exists():
        print(f"❌ Metadata file not found: {metadata_file}")
        return 1
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    restored_count = 0
    failed_count = 0
    
    print(f"🔄 Starting recovery of {len(metadata['files'])} markdown files...")
    print(f"📁 Backup from: {metadata['description']} ({metadata['timestamp']})")
    
    for file_path in metadata['files']:
        backup_file = backup_dir / file_path
        target_file = docs_dir / file_path
        
        try:
            if backup_file.exists():
                # Ensure target directory exists
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the clean file
                shutil.copy2(backup_file, target_file)
                restored_count += 1
                print(f"✅ Restored: {file_path}")
            else:
                print(f"⚠️  Backup not found: {file_path}")
                failed_count += 1
        except Exception as e:
            print(f"❌ Failed to restore {file_path}: {e}")
            failed_count += 1
    
    print("\n📊 Recovery Summary:")
    print(f"   ✅ Restored: {restored_count} files")
    print(f"   ❌ Failed: {failed_count} files")
    
    if failed_count == 0:
        print("\n🎉 Recovery completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check a few restored files to verify they look correct")
        print("   2. Run 'markdownlint docs/' to check for any remaining issues")
        print("   3. The broken scripts have been disabled (.DISABLED extension)")
    else:
        print("\n⚠️  Recovery completed with some failures")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())