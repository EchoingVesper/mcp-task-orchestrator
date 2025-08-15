# Test Failure Analysis

**Task ID**: `cicd-analysis-01`  
**Type**: Analysis  
**Local LLM Ready**: ✅ High  
**Estimated Duration**: 20 minutes  
**Priority**: 🔴 Critical

## Objective

Analyze current test failures to categorize root causes and create fix strategy.

## Inputs

- Current pytest output: `pytest --tb=short -v`
- Test collection errors from recent runs
- Import error patterns identified

## Expected Outputs

1. **Failure Categories JSON**:
   ```json
   {
     "import_errors": {
       "count": 28,
       "patterns": ["relative import errors", "missing parent package"],
       "affected_files": ["list of files"]
     },
     "pydantic_warnings": {
       "count": 54,
       "type": "V1 to V2 migration warnings",
       "affected_modules": ["list of modules"]
     }
   }
   ```

2. **Fix Priority Matrix**:
   - High: Import errors (blocking test execution)
   - Medium: Pydantic warnings (deprecation warnings)
   - Low: Style/formatting issues

## Success Criteria

- [ ] Complete categorization of all 28 test collection errors
- [ ] Root cause identified for import failures
- [ ] Priority ranking established for fixes
- [ ] JSON output file created for downstream tasks

## Local LLM Prompt Template

```
Analyze the pytest output below and categorize failures:

PYTEST_OUTPUT:
{pytest_output}

Create a JSON categorization with:
1. Import error patterns and affected files
2. Warning types and counts
3. Priority ranking for fixes
4. Recommended fix strategy for each category

Focus on actionable, specific categorization.
```

## Agent Instructions

Execute this command and analyze output:
```bash
pytest --tb=short -v 2>&1 | tee test_failure_analysis.log
```

Create categorization JSON and priority matrix based on patterns observed.