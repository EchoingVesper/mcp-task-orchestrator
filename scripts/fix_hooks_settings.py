#!/usr/bin/env python3
"""Fix the settings.json to move Read hook to PostToolUse"""

import json
from pathlib import Path

def fix_settings():
    settings_path = Path(".claude/settings.json")
    
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    # Remove Read hook from PreToolUse
    if 'PreToolUse' in settings['hooks']:
        settings['hooks']['PreToolUse'] = [
            hook for hook in settings['hooks']['PreToolUse']
            if hook.get('matcher') != 'Read'
        ]
    
    # Add Read hook to PostToolUse  
    read_hook = {
        "matcher": "Read",
        "hooks": [
            {
                "type": "command",
                "command": "if [[ \"$CLAUDE_TOOL_RESULT_FILE\" ]]; then python3 $CLAUDE_PROJECT_DIR/.claude/hooks/post_read_linter.py \"$CLAUDE_TOOL_RESULT_FILE\"; fi"
            }
        ]
    }
    
    if 'PostToolUse' not in settings['hooks']:
        settings['hooks']['PostToolUse'] = []
    
    settings['hooks']['PostToolUse'].append(read_hook)
    
    # Write back
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("✅ Fixed settings.json - moved Read hook to PostToolUse")

if __name__ == "__main__":
    fix_settings()