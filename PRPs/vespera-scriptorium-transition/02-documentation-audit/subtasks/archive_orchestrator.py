#!/usr/bin/env python3
"""
Vespera Scriptorium Documentation Archive Orchestrator

Systematically archives existing documentation while preserving valuable content
for migration to the new Vespera Scriptorium structure.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class DocumentationArchiver:
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_root = self.docs_root / "archives" / f"pre-vespera-legacy-{self.timestamp}"
        
        # Load inventory if available
        inventory_file = Path("/home/aya/dev/mcp-servers/mcp-task-orchestrator/PRPs/vespera-scriptorium-transition/02-documentation-audit/tracking/complete_documentation_inventory.json")
        if inventory_file.exists():
            with open(inventory_file) as f:
                self.inventory_data = json.load(f)
                self.inventory = {item['file_path']: item for item in self.inventory_data['inventory']}
        else:
            self.inventory = {}
    
    def create_archive_structure(self):
        """Create the archive directory structure."""
        print(f"Creating archive structure at: {self.archive_root}")
        
        # Create main archive directories
        directories = [
            "by-category/developer-docs",
            "by-category/user-docs", 
            "by-category/reference",
            "by-category/templates",
            "by-category/claude-docs",
            "by-category/miscellaneous",
            "by-action/archive-only",
            "by-action/high-priority",
            "by-action/corrupted",
            "content-extraction"
        ]
        
        for directory in directories:
            (self.archive_root / directory).mkdir(parents=True, exist_ok=True)
    
    def extract_valuable_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract valuable content from high-priority files for migration."""
        if not file_path.exists() or file_path.suffix.lower() != '.md':
            return {}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract key sections that should be preserved
            extracted = {
                "original_file": str(file_path.relative_to(self.docs_root)),
                "extraction_date": datetime.now().isoformat(),
                "valuable_sections": []
            }
            
            lines = content.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                # Detect headers
                if line.strip().startswith('#'):
                    # Save previous section if it has valuable content
                    if current_section and self.is_valuable_section(current_section, current_content):
                        extracted["valuable_sections"].append({
                            "header": current_section,
                            "content": '\n'.join(current_content).strip(),
                            "type": self.classify_section_type(current_section, current_content)
                        })
                    
                    current_section = line.strip()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Don't forget the last section
            if current_section and self.is_valuable_section(current_section, current_content):
                extracted["valuable_sections"].append({
                    "header": current_section,
                    "content": '\n'.join(current_content).strip(),
                    "type": self.classify_section_type(current_section, current_content)
                })
            
            return extracted
            
        except Exception as e:
            return {"error": str(e)}
    
    def is_valuable_section(self, header: str, content: List[str]) -> bool:
        """Determine if a section contains valuable content worth preserving."""
        header_lower = header.lower()
        content_text = '\n'.join(content).lower()
        
        # High-value indicators
        valuable_indicators = [
            'quick start', 'getting started', 'installation', 'setup',
            'architecture', 'design', 'pattern', 'workflow',
            'example', 'tutorial', 'guide', 'reference',
            'configuration', 'integration', 'troubleshooting'
        ]
        
        # Check if header indicates valuable content
        if any(indicator in header_lower for indicator in valuable_indicators):
            return len(content_text.strip()) > 50  # Has substantial content
        
        # Check content for valuable patterns
        if any(indicator in content_text for indicator in valuable_indicators):
            return len(content_text.strip()) > 100
        
        # Code blocks and structured content
        if '```' in content_text or ('|' in content_text and '---' in content_text):
            return True
        
        return False
    
    def classify_section_type(self, header: str, content: List[str]) -> str:
        """Classify the type of section for migration planning."""
        header_lower = header.lower()
        content_text = '\n'.join(content).lower()
        
        if any(word in header_lower for word in ['install', 'setup', 'configuration']):
            return 'installation'
        elif any(word in header_lower for word in ['quick', 'start', 'getting started']):
            return 'quickstart'
        elif any(word in header_lower for word in ['architecture', 'design']):
            return 'architecture'
        elif any(word in header_lower for word in ['example', 'usage', 'workflow']):
            return 'examples'
        elif any(word in header_lower for word in ['reference', 'api', 'command']):
            return 'reference'
        elif any(word in header_lower for word in ['troubleshoot', 'debug', 'error']):
            return 'troubleshooting'
        elif '```' in content_text:
            return 'code-examples'
        else:
            return 'general'
    
    def archive_file(self, file_path: Path) -> Dict[str, str]:
        """Archive a single file to appropriate locations."""
        relative_path = file_path.relative_to(self.docs_root)
        file_info = self.inventory.get(str(file_path), {})
        
        category = file_info.get('category', 'miscellaneous')
        relevance_score = file_info.get('relevance_score', 0)
        
        # Determine archive locations
        archive_paths = []
        
        # Archive by category
        category_archive = self.archive_root / "by-category" / category / relative_path
        category_archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, category_archive)
        archive_paths.append(str(category_archive))
        
        # Archive by action (high priority files also go to special location)
        if relevance_score >= 80:
            priority_archive = self.archive_root / "by-action" / "high-priority" / relative_path
            priority_archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, priority_archive)
            archive_paths.append(str(priority_archive))
            
            # Extract valuable content
            extracted = self.extract_valuable_content(file_path)
            if extracted and extracted.get('valuable_sections'):
                extraction_file = self.archive_root / "content-extraction" / f"{relative_path.stem}_content.json"
                extraction_file.parent.mkdir(parents=True, exist_ok=True)
                with open(extraction_file, 'w') as f:
                    json.dump(extracted, f, indent=2)
        
        return {
            "original_path": str(relative_path),
            "archive_paths": archive_paths,
            "category": category,
            "relevance_score": relevance_score
        }
    
    def generate_manifest(self, archived_files: List[Dict[str, Any]]):
        """Generate comprehensive manifest of archived files."""
        manifest = {
            "archive_metadata": {
                "timestamp": self.timestamp,
                "archive_root": str(self.archive_root.relative_to(self.docs_root)),
                "total_files_archived": len(archived_files),
                "archive_date": datetime.now().isoformat(),
                "purpose": "Pre-Vespera Scriptorium transition archive"
            },
            "statistics": {
                "files_by_category": {},
                "files_by_relevance": {"high": 0, "medium": 0, "low": 0},
                "content_extractions": 0
            },
            "archived_files": archived_files,
            "high_priority_files": [
                f for f in archived_files if f.get('relevance_score', 0) >= 80
            ]
        }
        
        # Calculate statistics
        for file_info in archived_files:
            category = file_info.get('category', 'unknown')
            manifest["statistics"]["files_by_category"][category] = \
                manifest["statistics"]["files_by_category"].get(category, 0) + 1
            
            score = file_info.get('relevance_score', 0)
            if score >= 80:
                manifest["statistics"]["files_by_relevance"]["high"] += 1
            elif score >= 60:
                manifest["statistics"]["files_by_relevance"]["medium"] += 1
            else:
                manifest["statistics"]["files_by_relevance"]["low"] += 1
        
        # Count content extractions
        extraction_dir = self.archive_root / "content-extraction"
        if extraction_dir.exists():
            manifest["statistics"]["content_extractions"] = len(list(extraction_dir.glob("*.json")))
        
        # Save manifest
        manifest_file = self.archive_root / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Also create readable summary
        self.generate_archive_summary(manifest)
        
        return manifest
    
    def generate_archive_summary(self, manifest: Dict[str, Any]):
        """Generate human-readable archive summary."""
        summary_content = f"""# Documentation Archive Summary

**Archive Date**: {manifest['archive_metadata']['archive_date']}  
**Archive Location**: `{manifest['archive_metadata']['archive_root']}`  
**Total Files Archived**: {manifest['archive_metadata']['total_files_archived']}

## Purpose

This archive contains all pre-Vespera Scriptorium documentation as part of the comprehensive transition to the new Vespera Scriptorium documentation system. All files have been systematically archived while preserving valuable content for migration.

## Archive Structure

```
{manifest['archive_metadata']['archive_root']}/
├── by-category/           # Files organized by type
│   ├── developer-docs/    # {manifest['statistics']['files_by_category'].get('developer-docs', 0)} files
│   ├── user-docs/         # {manifest['statistics']['files_by_category'].get('user-docs', 0)} files
│   ├── reference/         # {manifest['statistics']['files_by_category'].get('reference', 0)} files
│   ├── templates/         # {manifest['statistics']['files_by_category'].get('templates', 0)} files
│   └── miscellaneous/     # {manifest['statistics']['files_by_category'].get('miscellaneous', 0)} files
├── by-action/
│   └── high-priority/     # {manifest['statistics']['files_by_relevance']['high']} high-relevance files
├── content-extraction/    # {manifest['statistics']['content_extractions']} content extractions
└── manifest.json         # This summary + full metadata
```

## Content Preservation

High-priority files ({manifest['statistics']['files_by_relevance']['high']} files with relevance score 80+) have had their valuable content extracted to JSON format for easy migration to the new Vespera Scriptorium structure.

### High-Priority Files for Migration

"""
        
        for file_info in manifest['high_priority_files']:
            summary_content += f"- **{file_info['original_path']}** (Score: {file_info['relevance_score']})\n"
            summary_content += f"  - Category: {file_info['category']}\n"
        
        summary_content += f"""

## Statistics

| Metric | Count |
|--------|-------|
| Total Files Archived | {manifest['archive_metadata']['total_files_archived']} |
| High Priority (80+) | {manifest['statistics']['files_by_relevance']['high']} |
| Medium Priority (60-79) | {manifest['statistics']['files_by_relevance']['medium']} |
| Content Extractions | {manifest['statistics']['content_extractions']} |

## Next Steps for Vespera Scriptorium

1. **Review Content Extractions**: Examine `content-extraction/` files for valuable content to migrate
2. **Establish New Structure**: Create fresh Vespera Scriptorium documentation architecture
3. **Selective Migration**: Migrate only essential content from high-priority files
4. **Validation**: Ensure archived content remains accessible for reference

## Recovery

If any content needs to be recovered, all files are preserved in their original structure within the `by-category/` directories. The `manifest.json` file contains complete metadata for all archived files.

---

*Generated by Vespera Scriptorium Documentation Archive Orchestrator*
"""
        
        summary_file = self.archive_root / "ARCHIVE_SUMMARY.md"
        summary_file.write_text(summary_content)
    
    def execute_archive_operation(self) -> Dict[str, Any]:
        """Execute the complete archive operation."""
        print("🗂️  Starting Vespera Scriptorium Documentation Archive Operation")
        print(f"📅 Timestamp: {self.timestamp}")
        
        # Create archive structure
        self.create_archive_structure()
        
        # Find all files to archive (excluding existing archives)
        files_to_archive = []
        for file_path in self.docs_root.rglob('*'):
            if (file_path.is_file() and 
                'archives' not in file_path.parts and
                file_path != self.docs_root / 'archives'):
                files_to_archive.append(file_path)
        
        print(f"📋 Found {len(files_to_archive)} files to archive")
        
        # Archive each file
        archived_files = []
        for i, file_path in enumerate(files_to_archive):
            if i % 50 == 0:
                print(f"📦 Archived {i}/{len(files_to_archive)} files...")
            
            try:
                archive_result = self.archive_file(file_path)
                archived_files.append(archive_result)
            except Exception as e:
                print(f"⚠️  Warning: Failed to archive {file_path}: {e}")
                archived_files.append({
                    "original_path": str(file_path.relative_to(self.docs_root)),
                    "error": str(e),
                    "archive_paths": []
                })
        
        # Generate manifest
        print("📋 Generating archive manifest...")
        manifest = self.generate_manifest(archived_files)
        
        print(f"✅ Archive operation complete!")
        print(f"📊 Statistics:")
        print(f"   Total files archived: {len(archived_files)}")
        print(f"   High priority files: {manifest['statistics']['files_by_relevance']['high']}")
        print(f"   Content extractions: {manifest['statistics']['content_extractions']}")
        print(f"   Archive location: {self.archive_root}")
        
        return manifest

def main():
    """Main execution function."""
    docs_root = "/home/aya/dev/mcp-servers/mcp-task-orchestrator/docs"
    
    # Confirm operation
    print("🚨 DOCUMENTATION ARCHIVE OPERATION")
    print("This will archive ALL existing documentation files.")
    print("Files will be preserved but moved to archives.")
    print()
    
    archiver = DocumentationArchiver(docs_root)
    manifest = archiver.execute_archive_operation()
    
    # Save operation record
    operation_record = {
        "operation": "vespera_scriptorium_documentation_archive",
        "timestamp": archiver.timestamp,
        "archive_location": str(archiver.archive_root),
        "summary": manifest['archive_metadata']
    }
    
    record_file = Path("/home/aya/dev/mcp-servers/mcp-task-orchestrator/PRPs/vespera-scriptorium-transition/02-documentation-audit/tracking/archive_operation_record.json")
    with open(record_file, 'w') as f:
        json.dump(operation_record, f, indent=2)
    
    print(f"📝 Operation record saved to: {record_file}")

if __name__ == "__main__":
    main()