#!/usr/bin/env python3
"""
Session Context Manager Hook for Claude Code

Manages session context restoration and tracking for development workflows.
Helps maintain continuity across Claude Code sessions.
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

def get_git_info():
    """Get current git information"""
    try:
        branch = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, timeout=5).stdout.strip()
        
        modified_count = len(subprocess.run(['git', 'status', '--porcelain'], 
                                          capture_output=True, text=True, timeout=5).stdout.strip().split('\n'))
        if modified_count == 1 and not subprocess.run(['git', 'status', '--porcelain'], 
                                                     capture_output=True, text=True, timeout=5).stdout.strip():
            modified_count = 0
            
        last_commit = subprocess.run(['git', 'log', '-1', '--format=%s'], 
                                   capture_output=True, text=True, timeout=5).stdout.strip()
        
        return {
            'branch': branch or 'none',
            'modified_files': modified_count,
            'last_commit': last_commit or 'none'
        }
    except:
        return {'branch': 'none', 'modified_files': 0, 'last_commit': 'none'}

def find_current_prp():
    """Find current in-progress PRP"""
    try:
        prps_dir = Path('PRPs')
        if prps_dir.exists():
            for prp_file in prps_dir.glob('[IN-PROGRESS]*.md'):
                return prp_file.name
    except:
        pass
    return 'none'

def load_session_context():
    """Load existing session context"""
    context_file = Path('.task_orchestrator/.session_context.json')
    
    if context_file.exists():
        try:
            with open(context_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_session_context():
    """Save current session context"""
    context_dir = Path('.task_orchestrator')
    context_dir.mkdir(exist_ok=True)
    
    context_file = context_dir / '.session_context.json'
    
    git_info = get_git_info()
    current_prp = find_current_prp()
    
    context_data = {
        'last_active': datetime.now().isoformat(),
        'current_branch': git_info['branch'],
        'modified_files': git_info['modified_files'],
        'current_task': current_prp,
        'last_commit': git_info['last_commit'],
        'project_root': os.getcwd()
    }
    
    with open(context_file, 'w') as f:
        json.dump(context_data, f, indent=2)
    
    return context_data

def show_session_context(context_data):
    """Display session context to user"""
    if not context_data:
        return
        
    print("🧭 Session Context:", file=sys.stderr)
    print(f"   Last Active: {context_data.get('last_active', 'Unknown')}", file=sys.stderr)
    print(f"   Current Task: {context_data.get('current_task', 'None')}", file=sys.stderr)
    print(f"   Branch: {context_data.get('current_branch', 'none')}", file=sys.stderr)
    print(f"   Modified Files: {context_data.get('modified_files', 0)} files", file=sys.stderr)
    
    last_commit = context_data.get('last_commit', 'none')
    if last_commit and last_commit != 'none':
        print(f"   Last Commit: {last_commit}", file=sys.stderr)
    
    print("", file=sys.stderr)

def main():
    """Main hook execution"""
    try:
        # Always update context
        current_context = save_session_context()
        
        # For SessionStart, show context
        input_data = {}
        try:
            input_data = json.loads(sys.stdin.read())
        except:
            pass
            
        hook_type = os.environ.get('CLAUDE_HOOK_TYPE', '')
        
        if hook_type == 'SessionStart' or not hook_type:
            # Load previous context to show
            previous_context = load_session_context()
            show_session_context(previous_context)
        
    except Exception as e:
        # Log error but don't fail the hook
        print(f"Session context error: {e}", file=sys.stderr)
    
    # Always succeed
    sys.exit(0)

if __name__ == "__main__":
    main()