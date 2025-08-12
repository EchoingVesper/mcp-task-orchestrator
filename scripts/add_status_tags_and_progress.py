#!/usr/bin/env python3
"""
Add status tags to v2.0-release-meta-prp filenames and add progress tracking sections.
"""

import re
from pathlib import Path
import shutil
from datetime import datetime

# Progress tracking template to add to each file
PROGRESS_TEMPLATE = """

## Progress Tracking

**Status**: [PENDING]
**Last Updated**: {timestamp}
**Agent ID**: [Will be assigned by orchestrator]

### Completion Checklist

- [ ] Task planned via orchestrator_plan_task
- [ ] Specialist context created via orchestrator_execute_task  
- [ ] Implementation started
- [ ] Core functionality complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Integration verified
- [ ] Task completed via orchestrator_complete_task
- [ ] Results synthesized

### Implementation Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Core Implementation | ⏳ Pending | |
| Unit Tests | ⏳ Pending | |
| Integration Tests | ⏳ Pending | |
| Documentation | ⏳ Pending | |
| Code Review | ⏳ Pending | |

### Agent Activity Log

```yaml
# Auto-updated by orchestrator agents
agent_activities:
  - timestamp: 
    agent_id: 
    action: "initialized"
    details: "PRP ready for orchestrator assignment"
```

### Blockers & Issues

- None currently identified

### Next Steps

1. Awaiting orchestrator assignment
2. Pending specialist context creation
"""

def add_status_tag_to_filename(file_path, status="PENDING"):
    """Add status tag to filename after the number."""
    file_name = file_path.name
    
    # Skip files that already have status tags
    if "[" in file_name and "]" in file_name:
        print(f"  ℹ️ Already has status tag: {file_name}")
        return file_path
    
    # Match pattern like "01-documentation-..."
    match = re.match(r'^(\d{2})-(.+)$', file_name)
    if match:
        number = match.group(1)
        rest = match.group(2)
        new_name = f"{number}-[{status}]-{rest}"
        new_path = file_path.parent / new_name
        
        # Rename the file
        file_path.rename(new_path)
        print(f"  ✅ Renamed: {file_name} → {new_name}")
        return new_path
    else:
        print(f"  ⚠️ Skipping (no number prefix): {file_name}")
        return file_path

def add_progress_tracking_section(file_path):
    """Add progress tracking section to the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if progress tracking already exists
    if "## Progress Tracking" in content:
        print(f"  ℹ️ Progress tracking already exists")
        return False
    
    # Add progress tracking before the final separator (if exists) or at the end
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    progress_section = PROGRESS_TEMPLATE.format(timestamp=timestamp)
    
    # Look for final separator pattern (---)
    if '\n---\n' in content:
        # Insert before the final separator
        parts = content.rsplit('\n---\n', 1)
        content = parts[0] + progress_section + '\n---\n' + parts[1]
    else:
        # Just append at the end
        content = content.rstrip() + progress_section
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Added progress tracking section")
    return True

def process_prp_files():
    """Process all PRP files in the v2.0-release-meta-prp directory."""
    base_dir = Path("PRPs/v2.0-release-meta-prp")
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} not found")
        return
    
    # Files to process (numbered PRPs)
    prp_files = sorted(base_dir.glob("[0-9][0-9]-*.md"))
    
    print(f"Found {len(prp_files)} PRP files to process\n")
    
    for file_path in prp_files:
        print(f"Processing: {file_path.name}")
        
        # Add status tag to filename
        new_path = add_status_tag_to_filename(file_path, "PENDING")
        
        # Add progress tracking section
        add_progress_tracking_section(new_path)
        
        print()
    
    # Also update the meta-coordinator with IN-PROGRESS status
    meta_coord = base_dir / "meta-coordination-orchestrator.md"
    if meta_coord.exists():
        print("Processing meta-coordinator:")
        # Don't rename meta-coordinator, just add progress tracking
        add_progress_tracking_section(meta_coord)
        
        # Update its status line to IN-PROGRESS
        with open(meta_coord, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('**Status**: Active', '**Status**: [IN-PROGRESS]')
        
        with open(meta_coord, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  ✅ Updated meta-coordinator status to [IN-PROGRESS]")

def main():
    """Main execution."""
    print("=" * 60)
    print("Adding Status Tags and Progress Tracking to v2.0 PRPs")
    print("=" * 60 + "\n")
    
    process_prp_files()
    
    print("\n" + "=" * 60)
    print("✅ Processing complete!")
    print("\nNext steps:")
    print("1. Meta-coordinator can now track progress via status tags")
    print("2. Agents should update progress sections when working on PRPs")
    print("3. Status tags in filenames provide at-a-glance progress view")
    print("=" * 60)

if __name__ == "__main__":
    main()