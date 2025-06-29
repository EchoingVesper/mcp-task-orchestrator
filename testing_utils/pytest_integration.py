#!/usr/bin/env python3
"""
Pytest Integration for File-Based Test Output System

This module provides decorators and fixtures for seamlessly integrating
the file-based test output system with pytest tests, ensuring complete
output capture and safe reading by external systems.
"""

import pytest
import functools
import logging
from pathlib import Path
from typing import Any, Callable, Optional, Union

from .file_output_system import TestOutputWriter, TestOutputReader

logger = logging.getLogger("test_output_pytest")


class PytestOutputCapture:
    """Pytest integration for the file-based output system."""
    
    def __init__(self, base_output_dir: Optional[Union[str, Path]] = None):
        if base_output_dir is None:
            base_output_dir = Path.cwd() / "test_outputs" / "pytest"
        
        self.writer = TestOutputWriter(base_output_dir)
        self.reader = TestOutputReader(base_output_dir)
        self.current_session = None
    
    def capture_test_output(self, test_name: str, output_format: str = "text"):
        """Decorator for capturing test output to files."""
        def decorator(test_func: Callable) -> Callable:
            @functools.wraps(test_func)
            def wrapper(*args, **kwargs):
                # Start output capture
                with self.writer.write_test_output(test_name, output_format) as session:
                    self.current_session = session
                    
                    try:
                        # Capture print statements during test execution
                        original_print = __builtins__['print']
                        
                        def captured_print(*print_args, **print_kwargs):
                            # Call original print
                            original_print(*print_args, **print_kwargs)
                            
                            # Also write to our output file
                            output_line = ' '.join(str(arg) for arg in print_args)
                            session.write_line(output_line)
                        
                        # Replace print function temporarily
                        __builtins__['print'] = captured_print
                        
                        # Execute the test
                        result = test_func(*args, **kwargs)
                        
                        # Write test completion marker
                        session.write_line("\\n=== TEST COMPLETED SUCCESSFULLY ===")
                        session.write_line(f"Test: {test_name}")
                        session.write_line(f"Result: PASSED")
                        
                        return result
                        
                    except Exception as e:
                        # Write test failure information
                        session.write_line("\\n=== TEST FAILED ===")
                        session.write_line(f"Test: {test_name}")
                        session.write_line(f"Error: {str(e)}")
                        session.write_line(f"Result: FAILED")
                        raise
                        
                    finally:
                        # Restore original print function
                        __builtins__['print'] = original_print
                        self.current_session = None
            
            return wrapper
        return decorator


# Global pytest output capture instance
_pytest_capture = PytestOutputCapture()


def file_output_test(test_name: str = None, output_format: str = "text"):
    """
    Decorator for pytest tests to enable file-based output capture.
    
    Usage:
        @file_output_test("my_test_name")
        def test_example():
            print("This will be captured to a file")
            assert True
    """
    def decorator(test_func: Callable) -> Callable:
        nonlocal test_name
        if test_name is None:
            test_name = test_func.__name__
        
        return _pytest_capture.capture_test_output(test_name, output_format)(test_func)
    
    return decorator


@pytest.fixture
def file_output_session():
    """
    Pytest fixture that provides a file output session for manual output writing.
    
    Usage:
        def test_example(file_output_session):
            file_output_session.write_line("Manual output line")
            file_output_session.write_json({"key": "value"})
    """
    test_name = f"fixture_test_{int(time.time())}"
    
    with _pytest_capture.writer.write_test_output(test_name, "text") as session:
        yield session


@pytest.fixture
def output_file_reader():
    """
    Pytest fixture that provides access to the output file reader.
    
    Usage:
        def test_reader(output_file_reader):
            # Wait for a specific test output to complete
            completed = output_file_reader.wait_for_completion("test_output.txt")
            if completed:
                content = output_file_reader.read_completed_output("test_output.txt")
    """
    return _pytest_capture.reader


def wait_for_test_completion(test_name: str, timeout: float = 30.0) -> bool:
    """
    Wait for a specific test to complete its output writing.
    
    Args:
        test_name: Name of the test to wait for
        timeout: Maximum time to wait in seconds
        
    Returns:
        bool: True if test completed, False if timeout
    """
    # Find the output file for the test
    output_files = _pytest_capture.reader.base_output_dir.glob(f"{test_name}_*.txt")
    
    for output_file in output_files:
        if _pytest_capture.reader.wait_for_completion(output_file, timeout):
            return True
    
    return False


def read_test_output_safely(test_name: str) -> Optional[str]:
    """
    Safely read test output after ensuring it's completed.
    
    Args:
        test_name: Name of the test to read output for
        
    Returns:
        str: Test output content if available and complete, None otherwise
    """
    # Find the most recent output file for the test
    output_files = list(_pytest_capture.reader.base_output_dir.glob(f"{test_name}_*.txt"))
    
    if not output_files:
        return None
    
    # Sort by modification time and get the most recent
    latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
    
    return _pytest_capture.reader.read_completed_output(latest_file)


# Example usage and integration functions
def integrate_with_migration_test():
    """
    Example of how to integrate with the existing migration test.
    
    This shows how to wrap the existing test_migration function.
    """
    
    @file_output_test("migration_test_enhanced")
    def test_migration_with_file_output(tmp_path, capsys):
        """Enhanced migration test with file-based output."""
        
        # Import the original test
        from tests.unit.test_migration import test_migration
        
        # Run the original test - output will be captured to file
        print("=== Starting Enhanced Migration Test ===")
        print(f"Output will be written to file for safe reading")
        print(f"Temporary path: {tmp_path}")
        
        try:
            # Execute the original test
            result = test_migration(tmp_path, capsys)
            
            print("=== Migration Test Results ===")
            print("✅ Migration test completed successfully")
            print("All artifacts migrated correctly")
            
            return result
            
        except Exception as e:
            print("=== Migration Test Failed ===")
            print(f"❌ Error: {str(e)}")
            raise
    
    return test_migration_with_file_output


# Configuration and setup
def configure_pytest_integration(output_dir: Union[str, Path] = None):
    """
    Configure the pytest integration with custom settings.
    
    Args:
        output_dir: Custom output directory for test files
    """
    global _pytest_capture
    _pytest_capture = PytestOutputCapture(output_dir)
    
    logger.info(f"Configured pytest file output integration with directory: {output_dir}")


def get_pytest_output_statistics():
    """Get statistics about pytest file output usage."""
    return {
        "active_sessions": len(_pytest_capture.writer.get_active_sessions()),
        "output_directory": str(_pytest_capture.writer.base_output_dir),
        "completed_files": len(_pytest_capture.writer.list_completed_outputs())
    }
