#!/usr/bin/env python3
"""
Comprehensive Documentation Inventory and Analysis Tool

Generates complete inventory of documentation files for Vespera Scriptorium transition.
This tool analyzes all non-archived documentation files and creates detailed reports.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import re

def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single file and return comprehensive metadata."""
    try:
        stat = file_path.stat()
        
        # Basic file information
        analysis = {
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to("/home/aya/dev/mcp-servers/mcp-task-orchestrator")),
            "filename": file_path.name,
            "file_size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_type": file_path.suffix.lower(),
            "directory": str(file_path.parent.relative_to("/home/aya/dev/mcp-servers/mcp-task-orchestrator"))
        }
        
        # Content analysis for markdown files
        if file_path.suffix.lower() == '.md':
            try:
                content = file_path.read_text(encoding='utf-8')
                analysis.update(analyze_markdown_content(content))
            except Exception as e:
                analysis.update({
                    "content_error": str(e),
                    "line_count": 0,
                    "word_count": 0,
                    "corruption_level": "high"
                })
        else:
            # For non-markdown files
            analysis.update({
                "line_count": 0,
                "word_count": 0,
                "corruption_level": "unknown"
            })
        
        # Categorize and score
        analysis.update({
            "category": categorize_file(file_path),
            "relevance_score": calculate_relevance_score(file_path, analysis),
            "recommended_action": recommend_action(file_path, analysis)
        })
        
        return analysis
        
    except Exception as e:
        return {
            "file_path": str(file_path),
            "error": str(e),
            "corruption_level": "critical"
        }

def analyze_markdown_content(content: str) -> Dict[str, Any]:
    """Analyze markdown content for quality and structure."""
    lines = content.split('\n')
    
    # Basic metrics
    line_count = len(lines)
    word_count = len(content.split())
    
    # Quality indicators
    has_h1 = bool(re.search(r'^# ', content, re.MULTILINE))
    has_structure = bool(re.search(r'^#{1,6} ', content, re.MULTILINE))
    has_code_blocks = bool(re.search(r'```', content))
    has_links = bool(re.search(r'\[.*?\]\(.*?\)', content))
    
    # Corruption indicators
    has_broken_links = bool(re.search(r'\[.*?\]\(\s*\)', content))
    has_malformed_headers = bool(re.search(r'#{7,}', content))
    has_duplicate_content = check_duplicate_sections(content)
    
    # Vespera relevance
    vespera_mentions = len(re.findall(r'vespera|scriptorium', content, re.IGNORECASE))
    orchestrator_mentions = len(re.findall(r'orchestrator|task.*orchestrat', content, re.IGNORECASE))
    
    # Determine corruption level
    corruption_indicators = sum([
        has_broken_links,
        has_malformed_headers,
        has_duplicate_content,
        line_count > 1000,  # Very long files may be accumulations
        word_count < 10 and line_count > 5  # Very sparse files
    ])
    
    if corruption_indicators >= 3:
        corruption_level = "high"
    elif corruption_indicators >= 2:
        corruption_level = "medium"
    elif corruption_indicators >= 1:
        corruption_level = "low"
    else:
        corruption_level = "none"
    
    return {
        "line_count": line_count,
        "word_count": word_count,
        "has_h1": has_h1,
        "has_structure": has_structure,
        "has_code_blocks": has_code_blocks,
        "has_links": has_links,
        "has_broken_links": has_broken_links,
        "has_malformed_headers": has_malformed_headers,
        "has_duplicate_content": has_duplicate_content,
        "vespera_mentions": vespera_mentions,
        "orchestrator_mentions": orchestrator_mentions,
        "corruption_level": corruption_level
    }

def check_duplicate_sections(content: str) -> bool:
    """Check for duplicate sections or repetitive content."""
    lines = content.split('\n')
    headers = [line for line in lines if re.match(r'^#{1,6} ', line)]
    
    # Check for duplicate headers
    header_counts = {}
    for header in headers:
        clean_header = header.strip()
        header_counts[clean_header] = header_counts.get(clean_header, 0) + 1
    
    return any(count > 1 for count in header_counts.values())

def categorize_file(file_path: Path) -> str:
    """Categorize the file based on its path and name."""
    path_parts = file_path.parts
    filename = file_path.name.lower()
    
    # Category mapping based on path
    if 'developers' in path_parts:
        return 'developer-docs'
    elif 'users' in path_parts:
        return 'user-docs'
    elif 'reference' in path_parts:
        return 'reference'
    elif 'templates' in path_parts:
        return 'templates'
    elif 'installation' in path_parts:
        return 'installation'
    elif 'quick-start' in path_parts:
        return 'quick-start'
    elif 'journey' in path_parts:
        return 'meta-docs'
    elif 'development' in path_parts:
        return 'development'
    
    # Category based on filename
    if filename in ['readme.md', 'index.md']:
        return 'index'
    elif 'claude' in filename:
        return 'claude-docs'
    elif any(word in filename for word in ['api', 'reference']):
        return 'reference'
    elif any(word in filename for word in ['guide', 'tutorial']):
        return 'guides'
    elif any(word in filename for word in ['architecture', 'design']):
        return 'architecture'
    elif any(word in filename for word in ['test', 'validation']):
        return 'testing'
    
    return 'miscellaneous'

def calculate_relevance_score(file_path: Path, analysis: Dict[str, Any]) -> int:
    """Calculate relevance score for Vespera Scriptorium transition (0-100)."""
    score = 50  # Base score
    
    # Path-based scoring
    if 'quick-start' in str(file_path):
        score += 20
    elif 'users' in str(file_path) and 'guides' in str(file_path):
        score += 15
    elif 'developers' in str(file_path) and 'architecture' in str(file_path):
        score += 15
    elif 'reference' in str(file_path):
        score += 10
    elif 'templates' in str(file_path):
        score += 10
    
    # Content-based scoring
    if analysis.get('vespera_mentions', 0) > 0:
        score += 20
    if analysis.get('orchestrator_mentions', 0) > 5:
        score += 10
    if analysis.get('has_structure', False):
        score += 5
    if analysis.get('has_code_blocks', False):
        score += 5
    
    # Negative scoring for corruption
    corruption_level = analysis.get('corruption_level', 'none')
    if corruption_level == 'high':
        score -= 30
    elif corruption_level == 'medium':
        score -= 15
    elif corruption_level == 'low':
        score -= 5
    
    # File size penalties
    file_size = analysis.get('file_size', 0)
    if file_size > 50000:  # Very large files
        score -= 10
    elif file_size < 100:  # Very small files
        score -= 10
    
    return max(0, min(100, score))

def recommend_action(file_path: Path, analysis: Dict[str, Any]) -> str:
    """Recommend action for the file in Vespera transition."""
    relevance = analysis.get('relevance_score', 0)
    corruption = analysis.get('corruption_level', 'none')
    category = analysis.get('category', 'miscellaneous')
    
    # High priority preservation
    if relevance >= 80 and corruption in ['none', 'low']:
        return 'preserve-and-update'
    
    # Medium priority - may need updates
    elif relevance >= 60 and corruption in ['none', 'low', 'medium']:
        return 'review-and-migrate'
    
    # Template files - special handling
    elif category == 'templates' and corruption in ['none', 'low']:
        return 'preserve-as-template'
    
    # Reference docs - preserve but may update
    elif category == 'reference' and corruption != 'high':
        return 'preserve-reference'
    
    # Everything else - archive
    else:
        return 'archive-only'

def generate_inventory_report(docs_root: str) -> Dict[str, Any]:
    """Generate comprehensive inventory report."""
    docs_path = Path(docs_root)
    
    # Find all non-archived files
    all_files = []
    for file_path in docs_path.rglob('*'):
        if file_path.is_file() and 'archives' not in file_path.parts:
            all_files.append(file_path)
    
    print(f"Found {len(all_files)} files to analyze...")
    
    # Analyze each file
    inventory = []
    for i, file_path in enumerate(all_files):
        if i % 50 == 0:
            print(f"Analyzed {i}/{len(all_files)} files...")
        
        analysis = analyze_file(file_path)
        inventory.append(analysis)
    
    # Generate summary statistics
    categories = {}
    actions = {}
    corruption_levels = {}
    
    for item in inventory:
        category = item.get('category', 'unknown')
        action = item.get('recommended_action', 'unknown')
        corruption = item.get('corruption_level', 'unknown')
        
        categories[category] = categories.get(category, 0) + 1
        actions[action] = actions.get(action, 0) + 1
        corruption_levels[corruption] = corruption_levels.get(corruption, 0) + 1
    
    summary = {
        "total_files": len(inventory),
        "analysis_timestamp": datetime.now().isoformat(),
        "categories": categories,
        "recommended_actions": actions,
        "corruption_levels": corruption_levels,
        "high_relevance_files": len([item for item in inventory if item.get('relevance_score', 0) >= 80]),
        "files_to_preserve": len([item for item in inventory if item.get('recommended_action', '') in ['preserve-and-update', 'preserve-as-template', 'preserve-reference']]),
        "files_to_archive": len([item for item in inventory if item.get('recommended_action', '') == 'archive-only'])
    }
    
    return {
        "summary": summary,
        "inventory": inventory
    }

def main():
    """Main execution function."""
    docs_root = "/home/aya/dev/mcp-servers/mcp-task-orchestrator/docs"
    output_dir = Path("/home/aya/dev/mcp-servers/mcp-task-orchestrator/PRPs/vespera-scriptorium-transition/02-documentation-audit/tracking")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Starting comprehensive documentation inventory...")
    
    # Generate inventory
    report = generate_inventory_report(docs_root)
    
    # Save detailed inventory
    inventory_file = output_dir / "complete_documentation_inventory.json"
    with open(inventory_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Inventory complete!")
    print(f"📊 Summary:")
    print(f"   Total files: {report['summary']['total_files']}")
    print(f"   High relevance: {report['summary']['high_relevance_files']}")
    print(f"   To preserve: {report['summary']['files_to_preserve']}")
    print(f"   To archive: {report['summary']['files_to_archive']}")
    print(f"\n📄 Full report saved to: {inventory_file}")
    
    # Generate summary markdown
    summary_file = output_dir / "inventory_summary.md"
    generate_summary_markdown(report, summary_file)
    print(f"📝 Summary report saved to: {summary_file}")

def generate_summary_markdown(report: Dict[str, Any], output_file: Path):
    """Generate human-readable summary markdown."""
    summary = report['summary']
    inventory = report['inventory']
    
    content = f"""# Documentation Inventory Summary

**Analysis Date**: {summary['analysis_timestamp']}  
**Total Files Analyzed**: {summary['total_files']}

## Overview

This comprehensive analysis examined all non-archived documentation files in preparation for the Vespera Scriptorium transition.

## Summary Statistics

### Files by Category
{format_dict_as_table(summary['categories'])}

### Recommended Actions
{format_dict_as_table(summary['recommended_actions'])}

### Corruption Levels
{format_dict_as_table(summary['corruption_levels'])}

## Key Findings

- **High Priority Files**: {summary['high_relevance_files']} files scored 80+ relevance
- **Files to Preserve**: {summary['files_to_preserve']} files should be migrated to new structure
- **Files to Archive**: {summary['files_to_archive']} files should be archived only

## High Priority Files (Relevance Score 80+)

"""
    
    # Add high priority files
    high_priority = [item for item in inventory if item.get('relevance_score', 0) >= 80]
    high_priority.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    for item in high_priority:
        content += f"- **{item.get('relative_path', 'Unknown')}** (Score: {item.get('relevance_score', 0)})\n"
        content += f"  - Category: {item.get('category', 'Unknown')}\n"
        content += f"  - Action: {item.get('recommended_action', 'Unknown')}\n"
        content += f"  - Size: {item.get('file_size', 0)} bytes\n\n"
    
    content += """## Next Steps

1. **Archive Operation**: Move all files marked as 'archive-only' to archives/pre-vespera-legacy/
2. **Preserve Files**: Migrate high-priority files to new Vespera Scriptorium structure
3. **Review Files**: Manually review files marked as 'review-and-migrate'
4. **Template Preservation**: Special handling for template files

## Archive Directory Structure

```
docs/archives/pre-vespera-legacy-TIMESTAMP/
├── by-category/
│   ├── developer-docs/
│   ├── user-docs/
│   ├── reference/
│   └── miscellaneous/
├── by-action/
│   ├── archive-only/
│   ├── review-and-migrate/
│   └── corrupted/
└── manifest.json
```

---

*Generated by Vespera Scriptorium Documentation Audit Tool*
"""
    
    output_file.write_text(content)

def format_dict_as_table(data: Dict[str, int]) -> str:
    """Format dictionary as markdown table."""
    if not data:
        return "No data available"
    
    lines = ["| Category | Count |", "|----------|-------|"]
    for key, value in sorted(data.items()):
        lines.append(f"| {key} | {value} |")
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()