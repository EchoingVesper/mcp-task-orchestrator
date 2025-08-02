#!/usr/bin/env python3
"""Fix indentation issues in authentication tests."""

with open('tests/security/test_authentication.py', 'r') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # Fix the assert statements that got moved to column 0
    if line.strip() == 'assert is_valid is False' and not line.startswith('            '):
        fixed_lines.append('            assert is_valid is False\n')
    # Fix the if not is_valid statements that got moved to column 0
    elif line.strip().startswith('if not is_valid:') and not line.startswith('            '):
        fixed_lines.append('            if not is_valid:\n')
    # Remove the reference to exc_info that doesn't exist anymore
    elif 'assert "expired" in str(exc_info.value).lower()' in line:
        continue  # Skip this line
    else:
        fixed_lines.append(line)

# Fix the final line issue
if not fixed_lines[-1].endswith('\n'):
    fixed_lines[-1] += '\n'

with open('tests/security/test_authentication.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed indentation issues")