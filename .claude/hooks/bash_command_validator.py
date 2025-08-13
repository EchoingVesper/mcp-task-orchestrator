#!/usr/bin/env python3
"""
Bash Command Validator Hook for Claude Code

Validates bash commands and suggests improvements for better practices.

Attribution: Based on official Claude Code example
https://github.com/anthropics/claude-code/blob/main/examples/hooks/bash_command_validator_example.py
"""

import json
import sys
import re

def validate_command(command):
    """Validate bash command and return warnings/suggestions"""
    warnings = []
    suggestions = []
    
    # Check for grep usage and suggest ripgrep
    if re.search(r'\bgrep\b', command):
        warnings.append("Consider using 'rg' (ripgrep) instead of 'grep' for better performance")
        suggestions.append(f"rg equivalent: {command.replace('grep', 'rg')}")
    
    # Check for find -name and suggest ripgrep alternative
    find_name_match = re.search(r'find\s+\S+\s+-name\s+["\']([^"\']+)["\']', command)
    if find_name_match:
        pattern = find_name_match.group(1)
        warnings.append("Consider using 'rg --files -g' instead of 'find -name' for pattern matching")
        suggestions.append(f"rg equivalent: rg --files -g '{pattern}'")
    
    # Check for dangerous patterns
    dangerous_patterns = [
        (r'\brm\s+-rf\s+/', "Dangerous: recursive delete from root"),
        (r'\bchmod\s+777\b', "Security risk: chmod 777 gives full permissions to everyone"),
        (r'\bsudo\s+rm\b', "Potentially dangerous: sudo rm command"),
    ]
    
    for pattern, warning in dangerous_patterns:
        if re.search(pattern, command):
            warnings.append(warning)
    
    # Check for performance improvements
    if re.search(r'\bfind\s+.*-exec.*rm.*\{\}.*\+', command):
        suggestions.append("Good: Using find with -exec and + for efficiency")
    elif re.search(r'\bfind\s+.*-exec.*rm.*\{\}.*;', command):
        warnings.append("Consider using + instead of ; with find -exec for better performance")
    
    return warnings, suggestions

def main():
    """Main hook execution"""
    try:
        # Read the tool call data from stdin
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get('tool')
        if tool_name != 'Bash':
            sys.exit(0)
        
        tool_params = input_data.get('tool_input', {})
        command = tool_params.get('command', '')
        
        if not command:
            sys.exit(0)
        
        # Validate the command
        warnings, suggestions = validate_command(command)
        
        # Print warnings and suggestions
        if warnings:
            print("⚠️  Command warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"   • {warning}", file=sys.stderr)
        
        if suggestions:
            print("💡 Suggestions:", file=sys.stderr)
            for suggestion in suggestions:
                print(f"   • {suggestion}", file=sys.stderr)
        
        if warnings or suggestions:
            print("", file=sys.stderr)  # Add blank line for readability
        
    except json.JSONDecodeError:
        # Invalid JSON input, ignore
        pass
    except Exception as e:
        # Log error but don't fail the hook
        print(f"Hook error: {e}", file=sys.stderr)
    
    # Always allow the command to proceed (exit 0)
    # Use exit 1 to show error to user but allow command
    # Use exit 2 to block command and show error to Claude
    sys.exit(0)

if __name__ == "__main__":
    main()