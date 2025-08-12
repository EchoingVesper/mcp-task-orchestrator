#!/usr/bin/env python3
"""
Fix markdown formatting issues in v2.0-release-meta-prp files.
Applies surgical fixes while preserving content.
"""

import re
from pathlib import Path
import sys

def fix_markdown_formatting(content):
    """Apply markdown formatting fixes while preserving content."""
    
    # Fix heading splits (#\n# -> ##)
    content = re.sub(r'^#\n#', '##', content, flags=re.MULTILINE)
    
    # Fix code block endings (```text -> ```)
    content = re.sub(r'```text\n', '```\n', content)
    content = re.sub(r'```bash\n', '```\n', content)
    
    # Fix malformed code blocks
    content = re.sub(r'```text\nyaml', '```yaml', content)
    content = re.sub(r'```text\nmermaid', '```mermaid', content)
    
    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Ensure single blank line before headings (but not at start of file)
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip the very first line
        if i == 0:
            fixed_lines.append(line)
            continue
            
        # If this line starts with # and previous line is not empty
        if line.startswith('#') and i > 0 and fixed_lines[-1].strip() != '':
            # Add blank line before heading
            fixed_lines.append('')
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Ensure single blank line after headings
    content = re.sub(r'^(#+[^\n]+)\n([^\n#])', r'\1\n\n\2', content, flags=re.MULTILINE)
    
    return content

def process_file(file_path):
    """Process a single markdown file."""
    print(f"Processing: {file_path.name}")
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        fixed_content = fix_markdown_formatting(content)
        
        # Only write if changes were made
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed: {file_path.name}")
            return True
        else:
            print(f"  ℹ️ No changes needed: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main execution."""
    base_dir = Path("PRPs/v2.0-release-meta-prp")
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} not found")
        sys.exit(1)
    
    # Files to process (excluding legacy folder and newly created files)
    files_to_process = [
        "meta-coordination-orchestrator.md",
        "01-documentation-automation-spec-orchestrator.md",
        "02-git-integration-task-orchestrator.md",
        "03-health-monitoring-spec-orchestrator.md",
        "04-smart-routing-task-orchestrator.md",
        "05-template-library-spec-orchestrator.md",
        "06-testing-automation-spec-orchestrator.md",
        "07-integration-testing-task-orchestrator.md",
        "09-documentation-update-task-orchestrator.md",
        "10-repository-cleanup-task-orchestrator.md",
        "11-git-commit-organization-task-orchestrator.md",
        "12-release-preparation-task-orchestrator.md",
        "orchestrator-integration-template.md"
    ]
    
    fixed_count = 0
    
    for file_name in files_to_process:
        file_path = base_dir / file_name
        if file_path.exists():
            if process_file(file_path):
                fixed_count += 1
        else:
            print(f"  ⚠️ File not found: {file_name}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} of {len(files_to_process)} files")
    
    # Now handle README situation
    readme_path = base_dir / "README.md"
    readme_original = base_dir / "README-original.md"
    
    print("\n📚 README cleanup:")
    if readme_original.exists():
        print("  Removing README-original.md (duplicate)")
        readme_original.unlink()
        print("  ✅ Removed README-original.md")

if __name__ == "__main__":
    main()