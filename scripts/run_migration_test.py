#!/usr/bin/env python3
"""
Simple script to run the migration test directly.
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import the test function
from tests.unit.test_migration import test_migration

# Mock the pytest fixtures
class MockTmpPath:
    def __init__(self):
        self.path = Path(project_root) / "test_artifacts_temp"
        os.makedirs(self.path, exist_ok=True)
    
    def __truediv__(self, other):
        return self.path / other

class MockCapsys:
    def __init__(self):
        pass
    
    def readouterr(self):
        class Output:
            def __init__(self):
                self.out = ""
                self.err = ""
        return Output()

if __name__ == "__main__":
    print("=== Running Migration Test ===")
    try:
        # Run the test function with mocked fixtures
        test_migration(MockTmpPath(), MockCapsys())
        print("\n=== Test completed successfully ===")
    except Exception as e:
        print(f"\n=== Test failed with error: {e} ===")
    finally:
        # Clean up the temporary test directory
        temp_dir = Path(project_root) / "test_artifacts_temp"
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                if file.is_file():
                    try:
                        file.unlink()
                    except:
                        pass
            try:
                temp_dir.rmdir()
            except:
                pass
