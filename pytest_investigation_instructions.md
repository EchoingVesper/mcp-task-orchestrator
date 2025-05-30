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

## Recommended Solutions

Based on initial analysis, the most likely solutions are:

### Solution 1: Use -s flag (No Capture)
```
pytest tests/ -s
```

### Solution 2: Update pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-s -v"  # Disable capture, enable verbose
```

### Solution 3: Use --capture=no
```
pytest tests/ --capture=no
```

### Solution 4: Disable problematic plugins
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-p no:anyio -p no:asyncio -s -v"
```
