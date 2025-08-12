#!/usr/bin/env python3
"""
Markdown Lint Agent Dispatcher Hook for Claude Code

Detects markdown linting issues and creates tasks for specialized markdown agents.
Integrates with the async agent architecture for automated fixing.

Attribution: Inspired by Claude Code bash_command_validator example
https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py
"""

import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime
import uuid

def create_markdown_fix_task(file_path, lint_issues, severity="medium"):
    """Create a task for the markdown fixing agent"""
    
    # Create task directory if it doesn't exist
    task_dir = Path(".task_orchestrator/markdown_fixes")
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique task ID
    task_id = f"markdown_fix_{uuid.uuid4().hex[:8]}"
    task_file = task_dir / f"{task_id}.json"
    
    # Count issues by type
    issue_count = len(lint_issues.split('\n')) if lint_issues else 0
    
    # Determine complexity based on issue count and types
    complexity = "low"
    if issue_count > 10 or "MD025" in lint_issues:  # Many issues or multiple h1
        complexity = "medium"
    if issue_count > 20 or "MD033" in lint_issues:  # Very many or inline HTML
        complexity = "high"
    
    task_data = {
        "task_id": task_id,
        "type": "markdown_fix",
        "status": "pending",
        "priority": severity,
        "agent_type": "markdown_specialist", 
        "created_at": datetime.now().isoformat(),
        "file_path": str(file_path),
        "issues": lint_issues.split('\n') if lint_issues else [],
        "issue_count": issue_count,
        "estimated_complexity": complexity,
        "auto_fixable": complexity in ["low", "medium"],
        "context": {
            "trigger": "claude_hook",
            "tool_source": "markdownlint",
            "batch_eligible": True,
            "hook_version": "1.0"
        }
    }
    
    # Write task file
    with open(task_file, 'w') as f:
        json.dump(task_data, f, indent=2)
    
    # Also maintain a simple pending list
    pending_file = task_dir / "pending_files.txt"
    with open(pending_file, 'a') as f:
        f.write(f"{file_path}\n")
    
    return task_id, issue_count

def check_markdown_file(file_path):
    """Check a markdown file for linting issues"""
    if not file_path.endswith('.md'):
        return None
    
    if not os.path.exists(file_path):
        return None
    
    try:
        # Run markdownlint on the file
        result = subprocess.run(
            ['markdownlint', file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0 and result.stdout:
            return result.stdout.strip()
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # markdownlint not available or timed out
        pass
    
    return None

def main():
    """Main hook execution"""
    try:
        # Read the tool call data from stdin
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get('tool')
        tool_params = input_data.get('tool_input', {})
        
        # Only process Read, Write, Edit, MultiEdit operations
        if tool_name not in ['Read', 'Write', 'Edit', 'MultiEdit']:
            sys.exit(0)
        
        # Extract file path based on tool type
        file_path = None
        
        if tool_name == 'Read':
            file_path = tool_params.get('file_path')
        elif tool_name in ['Write', 'Edit']:
            file_path = tool_params.get('file_path')
        elif tool_name == 'MultiEdit':
            file_path = tool_params.get('file_path')
        
        if not file_path or not file_path.endswith('.md'):
            sys.exit(0)
        
        # Check the markdown file for issues
        lint_issues = check_markdown_file(file_path)
        
        if lint_issues:
            # Create task for fixing
            task_id, issue_count = create_markdown_fix_task(file_path, lint_issues)
            
            # Print notification to user
            print(f"📝 Markdown issues detected in {file_path}: {issue_count} issues", file=sys.stderr)
            print(f"   └─ Task created: {task_id}", file=sys.stderr)
            print(f"   └─ Run 'claude fix-markdown' or 'claude fix-markdown-batch' to fix", file=sys.stderr)
            
    except json.JSONDecodeError:
        # Invalid JSON input, ignore
        pass
    except Exception as e:
        # Log error but don't fail the hook
        print(f"Hook error: {e}", file=sys.stderr)
    
    # Always allow the original tool to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()