#!/usr/bin/env python3
"""
Create test pytest configurations to identify output truncation issues.
"""

import os
from pathlib import Path

def create_pytest_configs():
    """Create different pytest configuration files to test."""
    
    project_root = Path("E:/My Work/Programming/MCP Servers/mcp-task-orchestrator")
    
    # Configuration 1: Minimal pytest settings
    config1 = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v"
"""
    
    # Configuration 2: Disable output capture
    config2 = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-s -v"
"""
    
    # Configuration 3: Full output capture disabled
    config3 = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--capture=no -v"
"""
    
    # Configuration 4: Show all captured output
    config4 = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py" 
addopts = "--show-capture=all -v"
"""
    
    # Configuration 5: Disable plugins that might interfere
    config5 = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-p no:anyio -p no:asyncio -s -v"
"""
    
    configs = {
        "config1_minimal": config1,
        "config2_no_capture": config2,
        "config3_capture_disabled": config3,
        "config4_show_all": config4,
        "config5_no_plugins": config5
    }
    
    return configs


def create_test_instructions():
    """Create instructions for manually testing different configurations."""
    
    instructions = """
# Pytest Output Truncation Investigation Instructions

## Problem Summary
Tests run with pytest show truncated output compared to direct execution.
The working run_migration_test.py bypasses pytest and shows full output.

## Test Procedure

1. **Baseline Test (Direct Execution)**
   ```
   cd "E:/My Work/Programming/MCP Servers/mcp-task-orchestrator"
   python tests/test_output_comparison.py
   ```
   
2. **Current Pytest Configuration**
   ```
   pytest tests/test_output_comparison.py
   ```

3. **Test with No Capture**
   ```
   pytest tests/test_output_comparison.py -s
   ```

4. **Test with Verbose and No Capture**
   ```
   pytest tests/test_output_comparison.py -s -v
   ```

5. **Test with Capture Disabled**
   ```
   pytest tests/test_output_comparison.py --capture=no
   ```

6. **Test with Show All Capture**
   ```
   pytest tests/test_output_comparison.py --show-capture=all
   ```

7. **Test without asyncio plugin**
   ```
   pytest tests/test_output_comparison.py -p no:asyncio -s -v
   ```

8. **Test without anyio plugin**
   ```
   pytest tests/test_output_comparison.py -p no:anyio -s -v
   ```

9. **Test the actual migration test**
   ```
   pytest tests/unit/test_migration.py::test_migration -s -v
   ```

10. **Compare with working script**
    ```
    python scripts/run_migration_test.py
    ```

## Expected Findings

- Direct execution should show full output
- Some pytest configurations may truncate output
- Identify which configuration preserves full output
- Determine if plugins (asyncio, anyio) are causing issues

## Analysis Points

1. **Line Count Comparison**: Count output lines between methods
2. **Content Completeness**: Check if final messages appear
3. **Plugin Impact**: See if disabling plugins helps
4. **Configuration Impact**: Test different capture settings

## Root Cause Hypotheses

1. **Default Output Capture**: Pytest captures stdout/stderr by default
2. **Plugin Interference**: asyncio/anyio plugins may affect output
3. **Buffer Limits**: Output buffer size limitations
4. **Timing Issues**: Async operations completing after capture ends
5. **Logging Configuration**: Conflict between print() and logging
"""
    
    return instructions


def create_analysis_script():
    """Create a script to analyze pytest behavior."""
    
    analysis_script = '''#!/usr/bin/env python3
"""
Analyze pytest output capture behavior.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and capture output."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=cwd,
            timeout=60
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'stdout_lines': len(result.stdout.splitlines()),
            'stderr_lines': len(result.stderr.splitlines())
        }
    except subprocess.TimeoutExpired:
        return {'error': 'timeout'}
    except Exception as e:
        return {'error': str(e)}

def main():
    project_root = "E:/My Work/Programming/MCP Servers/mcp-task-orchestrator"
    
    # Test commands
    commands = [
        ("Direct execution", "python tests/test_output_comparison.py"),
        ("Pytest default", "pytest tests/test_output_comparison.py"),
        ("Pytest -s", "pytest tests/test_output_comparison.py -s"),
        ("Pytest -s -v", "pytest tests/test_output_comparison.py -s -v"),
        ("Pytest --capture=no", "pytest tests/test_output_comparison.py --capture=no"),
        ("Pytest --show-capture=all", "pytest tests/test_output_comparison.py --show-capture=all"),
    ]
    
    results = {}
    
    for name, cmd in commands:
        print(f"Running: {name}")
        print(f"Command: {cmd}")
        result = run_command(cmd, cwd=project_root)
        results[name] = result
        
        if 'error' in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Return code: {result['returncode']}")
            print(f"Stdout lines: {result['stdout_lines']}")
            print(f"Stderr lines: {result['stderr_lines']}")
        print("-" * 40)
    
    # Analysis
    print("\\nANALYSIS:")
    print("=" * 50)
    
    baseline = results.get("Direct execution")
    if baseline and 'error' not in baseline:
        baseline_lines = baseline['stdout_lines']
        print(f"Baseline (direct execution): {baseline_lines} lines")
        
        for name, result in results.items():
            if name != "Direct execution" and 'error' not in result:
                total_lines = result['stdout_lines'] + result['stderr_lines']
                percentage = (total_lines / baseline_lines) * 100 if baseline_lines > 0 else 0
                print(f"{name}: {total_lines} lines ({percentage:.1f}% of baseline)")
                
                if percentage < 80:
                    print(f"  ⚠️ SIGNIFICANT TRUNCATION DETECTED")
                elif percentage < 95:
                    print(f"  ⚠️ MINOR TRUNCATION DETECTED")
                else:
                    print(f"  ✅ NO TRUNCATION")

if __name__ == "__main__":
    main()
'''
    
    return analysis_script


def main():
    """Generate investigation files."""
    project_root = Path("E:/My Work/Programming/MCP Servers/mcp-task-orchestrator")
    
    # Create configs
    configs = create_pytest_configs()
    print("Created pytest configuration variants:")
    for name, config in configs.items():
        print(f"- {name}")
    
    # Create instructions
    instructions = create_test_instructions()
    with open(project_root / "pytest_investigation_instructions.md", "w") as f:
        f.write(instructions)
    print("\\nCreated: pytest_investigation_instructions.md")
    
    # Create analysis script
    analysis_script = create_analysis_script()
    with open(project_root / "analyze_pytest_output.py", "w") as f:
        f.write(analysis_script)
    print("Created: analyze_pytest_output.py")
    
    print("\\nInvestigation files created. Follow the instructions to identify truncation causes.")


if __name__ == "__main__":
    main()
