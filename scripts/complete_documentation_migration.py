#!/usr/bin/env python3
"""
Complete documentation migration from old structure to new modular excellence architecture.
Safely migrates all existing content while preserving history and updating cross-references.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Set
import json
import time


class CompleteDocumentationMigrator:
    """Complete migration from old docs structure to new modular architecture."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.docs_root = self.project_root / "docs"
        self.migration_log = []
        self.link_mappings = {}  # Track old -> new path mappings
        
        # Define the complete migration mapping
        self.migration_plan = {
            # User-focused content
            "user-guide/": "users/guides/",
            "examples/": "users/guides/intermediate/examples/",
            "troubleshooting/": "users/troubleshooting/",
            "llm-agents/": "users/guides/advanced/llm-agents/",
            "installation.md": "users/quick-start/installation-legacy.md",  # Keep existing + new
            
            # Developer-focused content  
            "architecture/": "developers/architecture/",
            "development/": "developers/contributing/",
            "planning/": "developers/planning/",
            "testing/": "developers/contributing/testing/",
            "api/": "developers/integration/api/",
            "operations/": "developers/architecture/operations/",
            "reference/": "users/reference/",
            
            # Archive content
            "releases/": "archives/by-version/releases/",
            "temp/": "archives/historical/temp/",
            
            # Root docs that need special handling
            "README.md": "README.md",  # Stay at root
            "INDEX.md": "archives/historical/legacy-index.md",
            "QUICK_COMMANDS.md": "users/quick-start/quick-commands.md",
            "CLEAN_ARCHITECTURE_GUIDE.md": "developers/architecture/clean-architecture-guide.md",
            "CLAUDE.md": "CLAUDE.md"  # Stay at root
        }
    
    def analyze_current_structure(self) -> Dict[str, List[str]]:
        """Analyze what needs to be migrated."""
        analysis = {
            "old_folders": [],
            "new_folders": [],
            "root_files": [],
            "conflicts": []
        }
        
        for item in self.docs_root.iterdir():
            if item.is_dir():
                if item.name in ["users", "developers", "archives"]:
                    analysis["new_folders"].append(item.name)
                else:
                    analysis["old_folders"].append(item.name)
            elif item.suffix == '.md':
                analysis["root_files"].append(item.name)
        
        # Check for conflicts
        for old_path, new_path in self.migration_plan.items():
            new_full_path = self.docs_root / new_path
            if new_full_path.exists() and (self.docs_root / old_path).exists():
                analysis["conflicts"].append(f"{old_path} -> {new_path}")
        
        return analysis
    
    def backup_current_state(self) -> Path:
        """Create backup of current documentation state."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"docs_backup_{timestamp}"
        
        try:
            shutil.copytree(self.docs_root, backup_dir)
            self.migration_log.append(f"Created backup: {backup_dir}")
            return backup_dir
        except Exception as e:
            self.migration_log.append(f"Backup failed: {e}")
            raise
    
    def migrate_content(self, dry_run: bool = True) -> bool:
        """Migrate all old content to new structure."""
        print(f"🚀 Starting complete migration (dry_run={dry_run})...")
        
        if not dry_run:
            # Create backup first
            backup_path = self.backup_current_state()
            print(f"📦 Backup created: {backup_path}")
        
        total_moved = 0
        total_errors = 0
        
        for old_pattern, new_pattern in self.migration_plan.items():
            old_path = self.docs_root / old_pattern
            
            if not old_path.exists():
                continue
                
            new_path = self.docs_root / new_pattern
            
            if dry_run:
                print(f"  📝 Would migrate: {old_pattern} -> {new_pattern}")
                continue
            
            try:
                # Create target directory
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                if old_path.is_file():
                    if new_path.exists():
                        # Handle conflict - rename old file
                        conflict_path = new_path.with_suffix('.legacy' + new_path.suffix)
                        shutil.move(str(old_path), str(conflict_path))
                        self.migration_log.append(f"Conflict resolved: {old_path} -> {conflict_path}")
                    else:
                        shutil.move(str(old_path), str(new_path))
                        self.migration_log.append(f"Moved file: {old_path} -> {new_path}")
                    
                    # Track mapping for link updates
                    self.link_mappings[old_pattern] = new_pattern
                    total_moved += 1
                
                elif old_path.is_dir():
                    if new_path.exists():
                        # Merge directories
                        for item in old_path.rglob("*"):
                            if item.is_file():
                                relative_path = item.relative_to(old_path)
                                target_file = new_path / relative_path
                                target_file.parent.mkdir(parents=True, exist_ok=True)
                                
                                if target_file.exists():
                                    # Rename to avoid overwrite
                                    target_file = target_file.with_suffix('.legacy' + target_file.suffix)
                                
                                shutil.move(str(item), str(target_file))
                                total_moved += 1
                        
                        # Remove empty directory structure
                        shutil.rmtree(old_path)
                    else:
                        shutil.move(str(old_path), str(new_path))
                        self.migration_log.append(f"Moved directory: {old_path} -> {new_path}")
                        total_moved += 1
                    
                    # Track mapping
                    self.link_mappings[old_pattern] = new_pattern
                    
            except Exception as e:
                self.migration_log.append(f"Error migrating {old_path}: {e}")
                total_errors += 1
        
        print(f"✅ Migration completed: {total_moved} items moved, {total_errors} errors")
        return total_errors == 0
    
    def update_cross_references(self, dry_run: bool = True) -> int:
        """Update all cross-references to use new paths."""
        print("🔗 Updating cross-references...")
        
        if not self.link_mappings:
            print("⚠️  No link mappings available - run migration first")
            return 0
        
        updates_made = 0
        
        # Find all markdown files in new structure
        for md_file in self.docs_root.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Update relative links based on mappings
                for old_path, new_path in self.link_mappings.items():
                    # Handle various link formats
                    patterns = [
                        f"]({old_path}",  # ]( format
                        f"](./{old_path}",  # ](./  format  
                        f"](../{old_path}",  # ](../  format
                        f"]({old_path.rstrip('/')}/",  # Directory links
                    ]
                    
                    for pattern in patterns:
                        if pattern in content:
                            # Calculate relative path from current file to new location
                            current_dir = md_file.parent
                            target_path = self.docs_root / new_path
                            
                            try:
                                relative_new_path = os.path.relpath(target_path, current_dir)
                                replacement = pattern.replace(old_path, relative_new_path)
                                content = content.replace(pattern, replacement)
                            except ValueError:
                                # Fallback to absolute path from docs root
                                replacement = pattern.replace(old_path, new_path)
                                content = content.replace(pattern, replacement)
                
                # Write updated content
                if content != original_content:
                    if not dry_run:
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                    
                    updates_made += 1
                    self.migration_log.append(f"Updated links in: {md_file.relative_to(self.docs_root)}")
                    
            except Exception as e:
                self.migration_log.append(f"Error updating links in {md_file}: {e}")
        
        print(f"🔗 Link updates: {updates_made} files {'would be ' if dry_run else ''}updated")
        return updates_made
    
    def create_legacy_redirects(self) -> None:
        """Create redirect files for major legacy paths."""
        redirects = {
            "user-guide/README.md": "users/README.md",
            "architecture/README.md": "developers/architecture/README.md", 
            "development/README.md": "developers/contributing/README.md",
            "planning/README.md": "developers/planning/README.md"
        }
        
        for old_path, new_path in redirects.items():
            redirect_file = self.docs_root / old_path
            redirect_file.parent.mkdir(parents=True, exist_ok=True)
            
            redirect_content = f"""# MOVED

This content has been moved to: [{new_path}](../{new_path})

## New Documentation Structure

The documentation has been reorganized for better user experience:

- **User Documentation**: `docs/users/` - End-user guides and tutorials
- **Developer Documentation**: `docs/developers/` - Technical architecture and contribution guides  
- **Historical Archive**: `docs/archives/` - Previous versions and historical content

Please update your bookmarks and links to use the new structure.
"""
            
            with open(redirect_file, 'w', encoding='utf-8') as f:
                f.write(redirect_content)
            
            self.migration_log.append(f"Created redirect: {old_path}")
    
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories left after migration."""
        removed_count = 0
        
        # Walk directory tree bottom-up to catch nested empty dirs
        for root, dirs, files in os.walk(self.docs_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):  # Empty directory
                        dir_path.rmdir()
                        removed_count += 1
                        self.migration_log.append(f"Removed empty directory: {dir_path.relative_to(self.docs_root)}")
                except OSError:
                    pass  # Directory not empty or permission issue
        
        return removed_count
    
    def generate_migration_report(self) -> Dict:
        """Generate comprehensive migration report."""
        report = {
            "migration_timestamp": time.time(),
            "migration_log": self.migration_log,
            "link_mappings": self.link_mappings,
            "summary": {
                "total_operations": len(self.migration_log),
                "link_mappings_created": len(self.link_mappings),
                "errors": len([log for log in self.migration_log if "Error" in log])
            }
        }
        
        report_path = self.project_root / "complete_migration_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Complete migration report: {report_path}")
        return report
    
    def run_complete_migration(self, dry_run: bool = True, update_links: bool = True) -> bool:
        """Execute the complete migration process."""
        print("🎯 Starting Complete Documentation Migration")
        print("=" * 50)
        
        # 1. Analyze current state
        analysis = self.analyze_current_structure()
        print(f"📊 Analysis:")
        print(f"  - Old folders to migrate: {len(analysis['old_folders'])}")
        print(f"  - New folders existing: {len(analysis['new_folders'])}")
        print(f"  - Root files: {len(analysis['root_files'])}")
        print(f"  - Potential conflicts: {len(analysis['conflicts'])}")
        
        if analysis['conflicts']:
            print("⚠️  Conflicts detected:")
            for conflict in analysis['conflicts']:
                print(f"    - {conflict}")
        
        # 2. Migrate content
        migration_success = self.migrate_content(dry_run=dry_run)
        if not migration_success:
            print("❌ Migration failed")
            return False
        
        # 3. Update cross-references
        if update_links and not dry_run:
            self.update_cross_references(dry_run=False)
        
        # 4. Create redirects for major paths
        if not dry_run:
            self.create_legacy_redirects()
        
        # 5. Cleanup
        if not dry_run:
            removed_dirs = self.cleanup_empty_directories()
            print(f"🧹 Cleaned up {removed_dirs} empty directories")
        
        # 6. Generate report
        if not dry_run:
            self.generate_migration_report()
        
        print(f"\n{'🔍 DRY RUN COMPLETED' if dry_run else '✅ MIGRATION COMPLETED'}")
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete documentation migration")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be migrated without making changes")
    parser.add_argument("--no-link-updates", action="store_true",
                       help="Skip updating cross-references")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze current structure")
    
    args = parser.parse_args()
    
    migrator = CompleteDocumentationMigrator()
    
    if args.analyze_only:
        analysis = migrator.analyze_current_structure()
        print("📊 Current Documentation Structure Analysis")
        print("=" * 50)
        print(f"Old folders to migrate: {analysis['old_folders']}")
        print(f"New modular folders: {analysis['new_folders']}")
        print(f"Root markdown files: {analysis['root_files']}")
        if analysis['conflicts']:
            print(f"Conflicts: {analysis['conflicts']}")
        return
    
    success = migrator.run_complete_migration(
        dry_run=args.dry_run,
        update_links=not args.no_link_updates
    )
    
    if not success:
        print("❌ Migration failed")
        exit(1)
    else:
        print("✅ Migration completed successfully")


if __name__ == "__main__":
    main()