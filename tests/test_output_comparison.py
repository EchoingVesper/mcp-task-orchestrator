#!/usr/bin/env python3
"""
Manual test runner to compare pytest vs direct execution output.

Usage:
1. Run this script directly: python test_output_comparison.py
2. Run with pytest: pytest test_output_comparison.py -s -v
3. Compare the outputs
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def generate_test_output():
    """Generate test output to check for truncation."""
    print("\n" + "="*60)
    print("PYTEST OUTPUT TRUNCATION TEST")
    print("="*60)
    
    print("\n=== Section 1: Basic Information ===")
    for i in range(10):
        print(f"Info line {i:02d}: Basic test information and details")
    
    print("\n=== Section 2: Detailed Data ===")
    for i in range(25):
        print(f"Data line {i:02d}: {'*' * 50} Detailed information row {i}")
    
    print("\n=== Section 3: Processing Results ===")
    for i in range(15):
        print(f"Result {i:02d}: Processing complete for item {i} - Status: OK")
    
    print("\n=== Section 4: Critical Messages ===")
    critical_messages = [
        "🔴 CRITICAL: This message must not be truncated",
        "🟡 WARNING: Check for output truncation in pytest",
        "🟢 SUCCESS: If you see this, output is working",
        "📝 NOTE: Compare pytest vs direct execution",
        "🔍 DEBUG: Line count and content verification"
    ]
    
    for msg in critical_messages:
        print(msg)
    
    print("\n=== Section 5: Large Content Block ===")
    large_content = """
This is a large block of text that contains important information.
It includes multiple lines and should be fully visible in both
pytest and direct execution modes. If this content is truncated
or missing, it indicates an output capture issue.

The content includes:
- Multiple paragraphs
- Technical details about the test
- Important debugging information
- Expected behavior descriptions
- Error indicators and success markers

This block serves as a comprehensive test for output capture
systems to ensure that lengthy content is properly displayed
and not cut off or hidden from view.
"""
    print(large_content)
    
    print("\n=== Section 6: Final Verification ===")
    print("✅ Test execution completed")
    print("✅ All sections processed")
    print("✅ Output capture test finished")
    print("🔍 If you can read this, output is NOT truncated")
    print("❌ If this line is missing, output WAS truncated")
    
    print("\n" + "="*60)
    print("END OF OUTPUT TEST")
    print("="*60)
    
    return True


def test_output_truncation():
    """Pytest test function."""
    result = generate_test_output()
    assert result is True


if __name__ == "__main__":
    print("Running output test directly (without pytest)...")
    generate_test_output()
    print("\nDirect execution completed successfully.")
