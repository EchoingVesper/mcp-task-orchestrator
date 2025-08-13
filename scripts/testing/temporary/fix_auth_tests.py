#!/usr/bin/env python3
"""
Script to systematically fix authentication test API mismatches.

This script updates authentication tests to match the new API where:
- API key is passed in kwargs instead of context
- Proper mocking is used for API key validation
"""

import re
import sys
from pathlib import Path


def fix_auth_decorator_tests(file_path):
    """Fix authentication decorator tests in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Fix test_require_auth_decorator_failure
    pattern1 = r'''(@pytest.mark.asyncio\s+@pytest.mark.authentication\s+@pytest.mark.critical\s+async def test_require_auth_decorator_failure.*?)(\n\s+# Should fail without auth\s+with pytest.raises\(AuthenticationError\):\s+await protected_handler\(context, {}\))'''
    
    replacement1 = r'''\1
        
        # Should fail without auth - no api_key provided
        with pytest.raises(AuthenticationError):
            await protected_handler(context, {})'''
    
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
    
    # Pattern 2: Fix test_nested_authentication_decorators
    pattern2 = r'''(async def test_nested_authentication_decorators.*?)(\n\s+result = await double_protected_handler\(context, {}\))(.*?assert result\["inner"\] is True)'''
    
    replacement2 = r'''\1
        
        # Mock the API key validation
        with patch('mcp_task_orchestrator.infrastructure.security.authentication.auth_validator.api_key_manager.validate_api_key') as mock_validate:
            mock_validate.return_value = (True, {"user_id": test_user_admin["user_id"], "role": "admin"})
            
            # Pass api_key in kwargs
            result = await double_protected_handler(context, {}, api_key=valid_api_key)\3'''
    
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    
    # Pattern 3: Fix security audit logging tests
    # These tests use SecurityAuditLogger methods that need updating
    
    # Fix test_successful_authentication_logging
    pattern3 = r'''(async def test_successful_authentication_logging.*?)(\n\s+# Verify audit log entry\s+events = security_audit_logger\.get_recent_events\(limit=1\))'''
    
    replacement3 = r'''\1
        
        # Verify audit log entry
        # Note: get_recent_events doesn't take limit parameter
        events = security_audit_logger.get_recent_events()
        if events:
            events = events[:1]  # Get first event only'''
    
    content = re.sub(pattern3, replacement3, content, flags=re.DOTALL)
    
    # Similar fix for other logging tests
    content = re.sub(
        r'security_audit_logger\.get_recent_events\(limit=(\d+)\)',
        r'security_audit_logger.get_recent_events()[::\1]',
        content
    )
    
    # Fix the handler definitions to accept **kwargs
    content = re.sub(
        r'async def protected_handler\(context, args\):',
        r'async def protected_handler(context, args, **kwargs):',
        content
    )
    
    content = re.sub(
        r'async def outer_handler\(context, args\):',
        r'async def outer_handler(context, args, **kwargs):',
        content
    )
    
    content = re.sub(
        r'async def inner_handler\(context, args\):',
        r'async def inner_handler(context, args, **kwargs):',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Fixed {file_path}")
        return True
    
    return False


def main():
    """Fix authentication test files."""
    test_dir = Path("tests/security")
    
    files_to_fix = [
        "test_authentication.py",
        "test_authorization.py",
        "test_attack_vectors.py"
    ]
    
    fixed_count = 0
    for file_name in files_to_fix:
        file_path = test_dir / file_name
        if file_path.exists():
            if fix_auth_decorator_tests(file_path):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")
    return fixed_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)