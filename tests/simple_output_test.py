#!/usr/bin/env python3
"""
Simple test to reproduce pytest output truncation.
"""

def test_simple_output():
    """Test with moderate output to check for truncation."""
    print("\n=== Starting output test ===")
    
    for i in range(20):
        print(f"Line {i:02d}: This is a test line to check for output truncation issues")
    
    print("\n=== Middle section ===")
    print("This is important output that should not be truncated")
    print("Testing if all content appears in pytest output")
    
    print("\n=== End section ===")
    print("Test completed successfully")
    
    assert True


def test_verbose_output():
    """Test with extensive output to trigger potential truncation."""
    print("\n=== Verbose Output Test ===")
    
    # Generate 100 lines of output
    for i in range(100):
        print(f"Verbose line {i:03d}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. " +
              f"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Line {i}")
    
    print("\n=== Critical Information ===")
    print("This is critical information that must not be truncated")
    print("If you can see this, output capture is working correctly")
    
    # Generate more output
    for i in range(50):
        print(f"Additional line {i:03d}: More content to test output limits")
    
    print("\n=== Test Summary ===")
    print("✅ Test completed")
    print("✅ All output should be visible")
    print("✅ No truncation should occur")
    
    assert True


if __name__ == "__main__":
    print("Running tests directly...")
    test_simple_output()
    test_verbose_output()
    print("Direct execution completed.")
