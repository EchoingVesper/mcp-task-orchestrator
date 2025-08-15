#!/usr/bin/env python3
"""
Comprehensive markdown fixer for v2.0-release-meta-prp files.
Fixes common patterns from the 287 detected errors.
"""

import re
from pathlib import Path

def fix_comprehensive_markdown(content):
    """Apply comprehensive markdown fixes."""
    
    # 1. Fix code blocks without language specifiers
    # Find ``` followed by immediate newline, add appropriate language
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if line.strip() == '```':
            # Look at next few lines to guess language
            next_lines = lines[i+1:i+5] if i+1 < len(lines) else []
            
            # Check for YAML patterns
            if any(re.match(r'^\s*\w+:', nl) for nl in next_lines[:3]):
                fixed_lines.append('```yaml')
            # Check for Python patterns  
            elif any(('def ' in nl or 'class ' in nl or 'import ' in nl) for nl in next_lines):
                fixed_lines.append('```python')
            # Check for bash patterns
            elif any(nl.strip().startswith(('$', '#', 'cd ', 'ls ', 'mkdir')) for nl in next_lines):
                fixed_lines.append('```bash')
            # Check for mermaid patterns
            elif any(('graph' in nl or 'flowchart' in nl) for nl in next_lines):
                fixed_lines.append('```mermaid')
            # Default to text for safety
            else:
                fixed_lines.append('```text')
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 2. Add blank lines around code blocks (MD031)
    content = re.sub(r'([^\n])\n```', r'\1\n\n```', content)  # Before fences
    content = re.sub(r'```\n([^\n])', r'```\n\n\1', content)  # After fences
    
    # 3. Fix multiple consecutive blank lines (MD012)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 4. Break long lines (MD013) - split at logical points
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 120 and not line.startswith('```'):
            # Try to split at logical points
            if ', ' in line and len(line) > 120:
                # Split at commas
                parts = line.split(', ')
                current_line = parts[0]
                
                for part in parts[1:]:
                    if len(current_line + ', ' + part) > 120:
                        fixed_lines.append(current_line + ',')
                        current_line = part
                    else:
                        current_line += ', ' + part
                
                fixed_lines.append(current_line)
            else:
                # Split at spaces near middle
                words = line.split(' ')
                current_line = words[0]
                
                for word in words[1:]:
                    if len(current_line + ' ' + word) > 120:
                        fixed_lines.append(current_line)
                        current_line = word
                    else:
                        current_line += ' ' + word
                
                fixed_lines.append(current_line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 5. Fix multiple H1 headings (MD025) - convert to H2
    lines = content.split('\n')
    h1_count = 0
    fixed_lines = []
    
    for line in lines:
        if re.match(r'^# [^#]', line):
            h1_count += 1
            if h1_count > 1:
                # Convert additional H1s to H2s
                fixed_lines.append('##' + line[1:])
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 6. Ensure single trailing newline (MD047)
    content = content.rstrip() + '\n'
    
    return content

def process_file(file_path):
    """Process a single file."""
    print(f"Processing: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_comprehensive_markdown(content)
        
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed: {file_path.name}")
            return True
        else:
            print(f"  ℹ️ No changes: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main execution."""
    base_dir = Path("PRPs/v2.0-release-meta-prp")
    
    # Get all markdown files excluding legacy
    md_files = [f for f in base_dir.glob("*.md") if "legacy" not in str(f)]
    
    print(f"Found {len(md_files)} markdown files to process\n")
    
    fixed_count = 0
    for file_path in sorted(md_files):
        if process_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Fixed {fixed_count} of {len(md_files)} files")
    
    # Verify fixes
    print("\nRunning markdownlint to verify fixes...")
    import subprocess
    try:
        result = subprocess.run(
            ['markdownlint'] + [str(f) for f in md_files],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ All markdown issues fixed!")
        else:
            remaining = len(result.stderr.split('\n')) - 1
            print(f"⚠️ {remaining} issues remaining")
            print("First few remaining issues:")
            print(result.stderr[:500])
    except:
        print("Manual verification needed")

if __name__ == "__main__":
    main()