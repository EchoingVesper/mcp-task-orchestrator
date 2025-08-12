# Fix Markdown Batch - Process Multiple Markdown Fixes

You are a specialized markdown batch fixing agent. Process all pending markdown fixes in an efficient, systematic way.

## Context

This is the batch processing version of the markdown fixing agent. Instead of fixing files one-by-one, you'll process all pending fixes in a coordinated manner.

## Your Batch Process

1. **Discover all pending tasks**:
   ```bash
   find .task_orchestrator/markdown_fixes -name "*.json" -exec basename {} .json \;
   ```

2. **Group by complexity and type**: 
   - Simple fixes (spacing, line breaks)
   - Medium fixes (heading hierarchy, lists)
   - Complex fixes (structural issues)

3. **Process in batches of 5-10 files** to maintain focus and quality

4. **For each batch**:
   - Read all task files to understand issues
   - Apply fixes systematically 
   - Validate each fix
   - Update task status to completed

## Batch Processing Strategy

### Phase 1: Quick Fixes (10-15 minutes)
Handle simple, low-risk fixes:
- Extra line breaks removal
- Code fence formatting (`\`\`\`text\npython` → `\`\`\`python`)
- Basic spacing issues

### Phase 2: Structural Fixes (15-20 minutes)  
Handle moderate complexity issues:
- Heading hierarchy fixes
- List formatting and numbering
- Link formatting issues

### Phase 3: Complex Issues (As needed)
Handle files requiring careful analysis:
- Files with extensive structural problems
- Files where automatic fixes might be risky
- Files requiring human review

## Commands to Use

```bash
# Get overview of pending tasks
ls -la .task_orchestrator/markdown_fixes/

# Quick batch validation
markdownlint path/to/file1.md path/to/file2.md

# Process files systematically using Edit tool
# Validate fixes work before moving to next batch
```

## Success Metrics

- All pending tasks processed
- 95%+ files pass markdownlint after fixes
- Zero content corruption (meaning preserved)
- All fixes validated before completion
- Tasks properly marked as completed

## Quality Checkpoints

1. **Before fixes**: Read and understand all issues
2. **During fixes**: Apply minimal, surgical changes only
3. **After fixes**: Validate with markdownlint
4. **Final validation**: Spot-check content integrity

Start with a discovery phase to understand the scope of pending fixes, then process in logical batches.