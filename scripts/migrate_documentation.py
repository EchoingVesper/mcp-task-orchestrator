#!/usr/bin/env python3
"""
Documentation migration script for Excellence Architecture.
Migrates existing documentation to the new modular structure while preserving content.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class DocumentationMigrator:
    """Handles migration of documentation to new modular structure."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.docs_root = self.project_root / "docs"
        self.migration_plan = self._create_migration_plan()
        self.migration_log = []
    
    def _create_migration_plan(self) -> Dict[str, str]:
        """Create mapping from current paths to new structure."""
        return {
            # User-focused content -> users/
            "user-guide/": "users/guides/",
            "examples/": "users/guides/intermediate/",
            "troubleshooting/": "users/troubleshooting/",
            "installation.md": "users/quick-start/installation.md",
            
            # Developer-focused content -> developers/
            "architecture/": "developers/architecture/",
            "development/": "developers/contributing/",
            "planning/": "developers/planning/",
            "testing/": "developers/contributing/standards/",
            "reference/": "users/reference/",
            
            # API and integration -> developers/integration/
            "api/": "developers/integration/",
            
            # Operations -> developers/
            "operations/": "developers/architecture/",
            
            # LLM agents guides -> users/guides/advanced/
            "llm-agents/": "users/guides/advanced/",
            
            # Releases -> archives/by-version/
            "releases/": "archives/by-version/current/",
            
            # Temp files -> archives/historical/
            "temp/": "archives/historical/temp/"
        }
    
    def analyze_file_sizes(self) -> List[Tuple[str, int]]:
        """Analyze markdown file sizes to identify large files."""
        large_files = []
        
        for md_file in self.docs_root.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                
                if lines > 200:  # Files that might need breaking down
                    relative_path = md_file.relative_to(self.docs_root)
                    large_files.append((str(relative_path), lines))
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return sorted(large_files, key=lambda x: x[1], reverse=True)
    
    def break_down_large_file(self, file_path: Path, max_lines: int = 200) -> List[Path]:
        """Break down a large file into smaller modules."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by major sections (h1 and h2 headings)
        sections = re.split(r'\n(?=# [^#]|\n## [^#])', content)
        
        if len(sections) <= 1:
            # Can't break down meaningfully
            return [file_path]
        
        modules = []
        base_name = file_path.stem
        parent_dir = file_path.parent
        
        # Create a directory for the broken down modules
        module_dir = parent_dir / base_name
        module_dir.mkdir(exist_ok=True)
        
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            
            lines = section.count('\n') + 1
            
            # Try to extract meaningful name from heading
            first_line = section.split('\n')[0]
            if first_line.startswith('#'):
                # Extract heading text for filename
                heading_text = re.sub(r'^#+\s*', '', first_line)
                heading_text = re.sub(r'[^\w\s-]', '', heading_text)
                heading_text = re.sub(r'\s+', '-', heading_text.strip()).lower()
                module_name = f"{heading_text}.md"
            else:
                module_name = f"section_{i+1}.md"
            
            module_path = module_dir / module_name
            
            # Add proper markdown structure
            if not section.startswith('#'):
                section = f"# {base_name.replace('-', ' ').title()}\n\n{section}"
            
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(section + '\n')
            
            modules.append(module_path)
            self.migration_log.append(f"Created module: {module_path}")
        
        # Create index file
        index_path = module_dir / "README.md"
        index_content = f"# {base_name.replace('-', ' ').title()}\n\n"
        index_content += "This documentation has been broken down into focused modules:\n\n"
        
        for module in modules:
            module_name = module.stem.replace('-', ' ').title()
            index_content += f"- [{module_name}]({module.name})\n"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        self.migration_log.append(f"Created index: {index_path}")
        return modules
    
    def migrate_file(self, source_path: Path, target_path: Path) -> bool:
        """Migrate a single file to the new structure."""
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file is large and should be broken down
            with open(source_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines > 300:  # Break down very large files
                self.migration_log.append(f"Breaking down large file: {source_path} ({lines} lines)")
                modules = self.break_down_large_file(source_path, max_lines=200)
                
                # Move modules to target directory
                for module in modules:
                    module_target = target_path.parent / module.name
                    shutil.move(str(module), str(module_target))
                
                # Remove original large file
                os.remove(source_path)
                return True
            else:
                # Simple move for smaller files
                shutil.move(str(source_path), str(target_path))
                self.migration_log.append(f"Moved: {source_path} -> {target_path}")
                return True
                
        except Exception as e:
            self.migration_log.append(f"Error migrating {source_path}: {e}")
            return False
    
    def update_cross_references(self):
        """Update cross-references and links after migration."""
        # This is a complex operation that would need to scan all files
        # and update relative links based on the new structure
        print("🔗 Updating cross-references (placeholder implementation)")
        
        # For now, just log that this needs to be done
        self.migration_log.append("TODO: Update cross-references after migration")
    
    def run_migration(self, dry_run: bool = True) -> bool:
        """Run the complete migration process."""
        print(f"🚀 Starting documentation migration (dry_run={dry_run})...")
        
        # Analyze current structure
        large_files = self.analyze_file_sizes()
        print(f"📊 Found {len(large_files)} files >200 lines")
        
        if large_files:
            print("📋 Top 10 largest files:")
            for file_path, lines in large_files[:10]:
                print(f"  - {file_path}: {lines} lines")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be moved")
            print("\nMigration plan:")
            for source_pattern, target_pattern in self.migration_plan.items():
                print(f"  {source_pattern} -> {target_pattern}")
            return True
        
        # Perform actual migration
        total_migrated = 0
        total_errors = 0
        
        for source_pattern, target_pattern in self.migration_plan.items():
            source_path = self.docs_root / source_pattern
            
            if source_path.exists():
                if source_path.is_file():
                    target_path = self.docs_root / target_pattern
                    if self.migrate_file(source_path, target_path):
                        total_migrated += 1
                    else:
                        total_errors += 1
                elif source_path.is_dir():
                    # Migrate directory contents
                    target_dir = self.docs_root / target_pattern
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    for item in source_path.rglob("*"):
                        if item.is_file() and item.suffix == '.md':
                            relative_path = item.relative_to(source_path)
                            target_path = target_dir / relative_path
                            
                            if self.migrate_file(item, target_path):
                                total_migrated += 1
                            else:
                                total_errors += 1
        
        # Update cross-references
        self.update_cross_references()
        
        # Generate migration report
        self.generate_report()
        
        print("\n✅ Migration completed!")
        print(f"📈 Files migrated: {total_migrated}")
        print(f"❌ Errors: {total_errors}")
        
        return total_errors == 0
    
    def generate_report(self):
        """Generate a migration report."""
        report = {
            "timestamp": __import__('time').time(),
            "migration_log": self.migration_log,
            "summary": {
                "total_operations": len(self.migration_log),
                "errors": len([log for log in self.migration_log if "Error" in log])
            }
        }
        
        report_path = self.project_root / "migration_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Migration report saved: {report_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate documentation to modular structure")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be migrated without making changes")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze file sizes and show large files")
    parser.add_argument("--project-root", default=".", 
                       help="Project root directory")
    
    args = parser.parse_args()
    
    migrator = DocumentationMigrator(args.project_root)
    
    if args.analyze_only:
        large_files = migrator.analyze_file_sizes()
        print(f"📊 Analysis Results: {len(large_files)} files >200 lines")
        print("\nFiles that need breaking down:")
        for file_path, lines in large_files:
            if lines > 300:
                status = "🔴 CRITICAL (>300 lines)"
            elif lines > 200:
                status = "🟡 MODERATE (>200 lines)"
            else:
                status = "🟢 OK"
            print(f"  {status} {file_path}: {lines} lines")
        return
    
    success = migrator.run_migration(dry_run=args.dry_run)
    
    if not success:
        print("❌ Migration completed with errors")
        exit(1)
    else:
        print("✅ Migration completed successfully")


if __name__ == "__main__":
    main()