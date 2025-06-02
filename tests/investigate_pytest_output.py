#!/usr/bin/env python3
"""
Test script to investigate pytest output truncation issues.

This script will:
1. Run a simple test with extensive output using pytest
2. Run the same test directly without pytest
3. Compare the outputs to identify truncation patterns
4. Test various pytest configuration options
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path("E:/My Work/Programming/MCP Servers/mcp-task-orchestrator").resolve()
sys.path.insert(0, str(project_root))


def create_test_with_extensive_output():
    """Create a test function that generates extensive output."""
    test_content = '''
import sys
sys.path.insert(0, r"E:\\My Work\\Programming\\MCP Servers\\mcp-task-orchestrator")

def test_extensive_output():
    """Test function that generates extensive output to check for truncation."""
    print("\\n=== Starting extensive output test ===")
    
    # Generate substantial output
    for i in range(100):
        print(f"Line {i:03d}: This is a test line with some content to check truncation - " + "x" * 50)
    
    print("\\n=== Section 1: Database Information ===")
    for i in range(50):
        print(f"Database record {i:03d}: Some database information and details here")
    
    print("\\n=== Section 2: Processing Results ===")
    for i in range(50):
        print(f"Processing item {i:03d}: Result data and status information")
        
    print("\\n=== Section 3: Final Summary ===")
    print("Summary line 1: All tests completed successfully")
    print("Summary line 2: Total items processed: 200") 
    print("Summary line 3: No errors encountered")
    print("Summary line 4: Test execution finished")
    print("\\n=== End of extensive output test ===")
    
    # This should always pass
    assert True

if __name__ == "__main__":
    # Run directly without pytest
    print("Running test directly (no pytest)...")
    test_extensive_output()
    print("Direct execution completed.")
'''
    
    return test_content


def run_pytest_with_different_configs():
    """Test pytest with different output configurations."""
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_pytest_output_test.py', delete=False) as f:
        f.write(create_test_with_extensive_output())
        test_file = f.name
    
    try:
        pytest_exe = project_root / "venv_test" / "Scripts" / "pytest.exe"
        if not pytest_exe.exists():
            pytest_exe = project_root / "venv_test" / "Scripts" / "python.exe"
            pytest_cmd = [str(pytest_exe), "-m", "pytest"]
        else:
            pytest_cmd = [str(pytest_exe)]
        
        # Test configurations to try
        configs = [
            {
                "name": "Default pytest",
                "args": [test_file]
            },
            {
                "name": "Pytest with -s (no capture)",
                "args": ["-s", test_file]
            },
            {
                "name": "Pytest with -v (verbose)",
                "args": ["-v", test_file]
            },
            {
                "name": "Pytest with -s -v",
                "args": ["-s", "-v", test_file]
            },
            {
                "name": "Pytest with --tb=short",
                "args": ["--tb=short", "-s", test_file]
            },
            {
                "name": "Pytest with --capture=no",
                "args": ["--capture=no", test_file]
            },
            {
                "name": "Pytest with --show-capture=all",
                "args": ["--show-capture=all", test_file]
            }
        ]
        
        results = {}
        
        for config in configs:
            print(f"\\n{'='*60}")
            print(f"Testing: {config['name']}")
            print(f"Command: {pytest_cmd + config['args']}")
            print('='*60)
            
            try:
                # Change to project directory for the test
                result = subprocess.run(
                    pytest_cmd + config['args'],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output_lines = len(result.stdout.split('\\n'))
                error_lines = len(result.stderr.split('\\n'))
                
                results[config['name']] = {
                    'stdout_lines': output_lines,
                    'stderr_lines': error_lines,
                    'return_code': result.returncode,
                    'stdout_preview': result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                    'stderr_preview': result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr
                }
                
                print(f"Return code: {result.returncode}")
                print(f"Stdout lines: {output_lines}")
                print(f"Stderr lines: {error_lines}")
                print(f"\\nStdout preview (first 500 chars):")
                print(result.stdout[:500])
                if result.stderr:
                    print(f"\\nStderr preview (first 500 chars):")
                    print(result.stderr[:500])
                
            except subprocess.TimeoutExpired:
                print("❌ Test timed out")
                results[config['name']] = {'error': 'timeout'}
            except Exception as e:
                print(f"❌ Error running test: {str(e)}")
                results[config['name']] = {'error': str(e)}
        
        return results
    
    finally:
        # Clean up temp file
        try:
            os.unlink(test_file)
        except:
            pass


def run_direct_execution():
    """Run the test directly without pytest."""
    print("\\n" + "="*60)
    print("Testing: Direct execution (no pytest)")
    print("="*60)
    
    # Create and run the test directly
    test_code = create_test_with_extensive_output()
    
    # Extract just the test function and run it
    test_func_code = '''
def test_extensive_output():
    """Test function that generates extensive output to check for truncation."""
    print("\\n=== Starting extensive output test ===")
    
    # Generate substantial output
    for i in range(100):
        print(f"Line {i:03d}: This is a test line with some content to check truncation - " + "x" * 50)
    
    print("\\n=== Section 1: Database Information ===")
    for i in range(50):
        print(f"Database record {i:03d}: Some database information and details here")
    
    print("\\n=== Section 2: Processing Results ===")
    for i in range(50):
        print(f"Processing item {i:03d}: Result data and status information")
        
    print("\\n=== Section 3: Final Summary ===")
    print("Summary line 1: All tests completed successfully")
    print("Summary line 2: Total items processed: 200") 
    print("Summary line 3: No errors encountered")
    print("Summary line 4: Test execution finished")
    print("\\n=== End of extensive output test ===")

# Run the test
print("Starting direct execution...")
test_extensive_output()
print("Direct execution completed.")
'''
    
    # Execute the code and capture output
    import io
    from contextlib import redirect_stdout
    
    output_buffer = io.StringIO()
    
    try:
        with redirect_stdout(output_buffer):
            exec(test_func_code)
        
        output = output_buffer.getvalue()
        output_lines = len(output.split('\\n'))
        
        print(f"Direct execution completed successfully")
        print(f"Output lines: {output_lines}")
        print(f"\\nOutput preview (first 500 chars):")
        print(output[:500])
        
        return {
            'output_lines': output_lines,
            'output_preview': output[:500] + "..." if len(output) > 500 else output
        }
        
    except Exception as e:
        print(f"❌ Error in direct execution: {str(e)}")
        return {'error': str(e)}


def analyze_results(pytest_results, direct_result):
    """Analyze the results to identify truncation patterns."""
    print("\\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    if 'error' not in direct_result:
        print(f"Direct execution baseline: {direct_result['output_lines']} lines")
    
    print("\\nPytest configuration comparison:")
    print("-" * 40)
    
    for config_name, result in pytest_results.items():
        if 'error' in result:
            print(f"{config_name}: ERROR - {result['error']}")
        else:
            lines = result['stdout_lines'] + result['stderr_lines']
            print(f"{config_name}: {lines} total lines (stdout: {result['stdout_lines']}, stderr: {result['stderr_lines']})")
    
    # Find the best performing configuration
    best_config = None
    max_lines = 0
    
    for config_name, result in pytest_results.items():
        if 'error' not in result:
            total_lines = result['stdout_lines'] + result['stderr_lines']
            if total_lines > max_lines:
                max_lines = total_lines
                best_config = config_name
    
    if best_config:
        print(f"\\n✅ Best pytest configuration: {best_config} ({max_lines} lines)")
    else:
        print("\\n❌ No pytest configuration worked properly")
    
    # Check for truncation
    if 'error' not in direct_result and best_config:
        baseline_lines = direct_result['output_lines']
        pytest_lines = max_lines
        
        if pytest_lines < baseline_lines * 0.8:  # If pytest has <80% of direct output
            print(f"\\n⚠️ TRUNCATION DETECTED: Pytest output ({pytest_lines} lines) is significantly less than direct execution ({baseline_lines} lines)")
        else:
            print(f"\\n✅ No significant truncation detected")


def main():
    """Main function to run the investigation."""
    print("=== Pytest Output Truncation Investigation ===")
    print(f"Project root: {project_root}")
    
    # Test direct execution first
    direct_result = run_direct_execution()
    
    # Test pytest with different configurations
    pytest_results = run_pytest_with_different_configs()
    
    # Analyze results
    analyze_results(pytest_results, direct_result)
    
    return pytest_results, direct_result


if __name__ == "__main__":
    pytest_results, direct_result = main()
