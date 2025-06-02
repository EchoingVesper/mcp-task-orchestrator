#!/usr/bin/env python3
"""
Validation script for pytest configuration improvements.

This script tests different pytest configurations to verify that output
truncation issues have been resolved.
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

def create_test_with_known_output():
    """Create a test file with known output patterns."""
    test_content = '''
def test_known_output():
    """Test with predictable output to check for truncation."""
    print("\\n=== PYTEST OUTPUT VALIDATION TEST ===")
    
    # Print exactly 50 numbered lines
    for i in range(50):
        print(f"Line {i:02d}: This is test line {i} for truncation validation")
    
    print("\\n=== CRITICAL MARKERS ===")
    print("MARKER_START: Beginning of critical section")
    print("MARKER_MIDDLE: Middle of test output") 
    print("MARKER_END: End of test - if you see this, NO TRUNCATION occurred")
    
    # Return success
    assert True
'''
    return test_content

def test_configuration(config_name, pytest_args, project_root):
    """Test a specific pytest configuration."""
    print(f"\n{'='*60}")
    print(f"Testing Configuration: {config_name}")
    print(f"Args: {pytest_args}")
    print('='*60)
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_validation_test.py', 
                                    dir=project_root / "tests", delete=False) as f:
        f.write(create_test_with_known_output())
        test_file = Path(f.name)
    
    try:
        # Run pytest with the configuration
        cmd = [
            sys.executable, "-m", "pytest", 
            str(test_file.relative_to(project_root))
        ] + pytest_args
        
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Analyze output
        stdout_lines = result.stdout.split('\n')
        stderr_lines = result.stderr.split('\n')
        
        # Check for critical markers
        markers_found = {
            'MARKER_START': any('MARKER_START' in line for line in stdout_lines),
            'MARKER_MIDDLE': any('MARKER_MIDDLE' in line for line in stdout_lines), 
            'MARKER_END': any('MARKER_END' in line for line in stdout_lines)
        }
        
        # Count expected test output lines
        test_lines = [line for line in stdout_lines if 'Line ' in line and 'test line' in line]
        
        # Results
        print(f"Return code: {result.returncode}")
        print(f"Total stdout lines: {len(stdout_lines)}")
        print(f"Total stderr lines: {len(stderr_lines)}")
        print(f"Test output lines found: {len(test_lines)}/50 expected")
        
        print(f"Critical markers found:")
        for marker, found in markers_found.items():
            status = "✅" if found else "❌"
            print(f"  {status} {marker}: {found}")
        
        # Determine if truncation occurred
        all_markers_found = all(markers_found.values())
        sufficient_test_lines = len(test_lines) >= 45  # Allow some flexibility
        
        if all_markers_found and sufficient_test_lines:
            print("✅ NO TRUNCATION DETECTED")
            truncation_status = "PASS"
        else:
            print("❌ TRUNCATION DETECTED")
            truncation_status = "FAIL"
        
        return {
            'config_name': config_name,
            'return_code': result.returncode,
            'stdout_lines': len(stdout_lines),
            'stderr_lines': len(stderr_lines),
            'test_lines_found': len(test_lines),
            'markers_found': markers_found,
            'truncation_status': truncation_status,
            'stdout_preview': result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
        }
        
    except subprocess.TimeoutExpired:
        print("❌ TEST TIMED OUT")
        return {'config_name': config_name, 'error': 'timeout'}
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {'config_name': config_name, 'error': str(e)}
    finally:
        # Clean up test file
        try:
            test_file.unlink()
        except:
            pass

def main():
    """Run pytest configuration validation."""
    project_root = Path("E:/My Work/Programming/MCP Servers/mcp-task-orchestrator")
    
    print("PYTEST CONFIGURATION VALIDATION")
    print("="*60)
    print(f"Project root: {project_root}")
    
    # Test configurations
    configurations = [
        ("Default", []),
        ("No Capture (-s)", ["-s"]),
        ("Verbose + No Capture", ["-s", "-v"]), 
        ("Capture Disabled", ["--capture=no"]),
        ("Show All Captured", ["--show-capture=all"]),
        ("No Capture + Short TB", ["-s", "-v", "--tb=short"]),
        ("Recommended Config", ["-s", "-v", "--tb=short", "--maxfail=1"])
    ]
    
    results = []
    
    for config_name, args in configurations:
        try:
            result = test_configuration(config_name, args, project_root)
            results.append(result)
        except KeyboardInterrupt:
            print("\\n❌ Testing interrupted by user")
            break
        except Exception as e:
            print(f"\\n❌ Unexpected error testing {config_name}: {str(e)}")
            results.append({'config_name': config_name, 'error': str(e)})
    
    # Summary
    print("\\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed_configs = []
    failed_configs = []
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['config_name']}: ERROR - {result['error']}")
            failed_configs.append(result['config_name'])
        elif result.get('truncation_status') == 'PASS':
            print(f"✅ {result['config_name']}: PASSED - No truncation detected")
            passed_configs.append(result['config_name'])
        else:
            print(f"❌ {result['config_name']}: FAILED - Truncation detected")
            failed_configs.append(result['config_name'])
    
    print(f"\\nResults: {len(passed_configs)} passed, {len(failed_configs)} failed")
    
    if passed_configs:
        print(f"\\n✅ RECOMMENDED CONFIGURATIONS:")
        for config in passed_configs:
            print(f"  - {config}")
    
    if failed_configs:
        print(f"\\n❌ AVOID THESE CONFIGURATIONS:")
        for config in failed_configs:
            print(f"  - {config}")
    
    return len(passed_configs) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
