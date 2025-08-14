# Subtask: Complete Documentation Inventory Creation

**Task ID**: `doc-audit-01`  
**Parent**: Documentation Audit & Remediation  
**Type**: Discovery & Analysis  
**Priority**: CRITICAL - Must complete first  
**Estimated Duration**: 4 hours

## Objective

Generate a comprehensive inventory of ALL documentation files in the project, identifying corruption patterns, organizational issues, and priority fixes.

## Deliverables

1. `inventory/complete_documentation_inventory.json` - Full file listing
2. `inventory/problematic_files_priority_list.json` - Prioritized fix list
3. `inventory/organization_analysis.json` - Structural issues report

## Implementation Steps

### Step 1: Recursive Documentation Scan

```python
# Script: scripts/generate_doc_inventory.py
import os
import json
from pathlib import Path
from datetime import datetime

def scan_documentation():
    inventory = []
    for root, dirs, files in os.walk('docs/'):
        for file in files:
            if file.endswith('.md'):
                path = Path(root) / file
                inventory.append({
                    'path': str(path),
                    'size': path.stat().st_size,
                    'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    'corruption_check': check_corruption(path),
                    'location_analysis': analyze_location(path)
                })
    return inventory
```

### Step 2: Corruption Pattern Detection

Identify these specific patterns:
- Extra line breaks at document start
- Heading corruption (`#\n# Heading`)
- Code block corruption (` ```text\npython`)
- Systematic `text\n` insertions

### Step 3: Organization Analysis

Detect:
- Nested identical folder names (`contributing/contributing/`)
- Task-tracking documents in permanent locations
- Misplaced temporary files
- Missing categorization

## Success Criteria

- [ ] 100+ documentation files cataloged
- [ ] All .md files in docs/ scanned
- [ ] Corruption patterns identified and quantified
- [ ] Priority ranking generated
- [ ] JSON outputs validated

## Agent Instructions

```yaml
agent: inventory_specialist
context: 
  - Full filesystem access to docs/
  - Markdown parsing capabilities
  - JSON generation tools
priority: Execute before any other documentation tasks
```