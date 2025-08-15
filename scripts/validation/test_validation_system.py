#!/usr/bin/env python3
"""
Test Validation System

This script tests the validation system to ensure all components work correctly.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

def create_test_files():
    """Create test files for validation."""
    test_dir = Path(tempfile.mkdtemp(prefix="validation_test_"))
    
    # Create a valid feature documentation file
    valid_file = test_dir / "valid_feature.md"
    valid_content = """---
title: "Test Feature Documentation"
status: "DRAFT"
priority: "MEDIUM"
category: "ENHANCEMENT"
version: "1.0.0"
description: "This is a test feature documentation file with proper metadata and structure."
author: "Test Author"
created: "2025-01-08"
tags: ["test", "validation"]
---

# Test Feature Documentation

## Overview

This is a test feature documentation file used to validate the documentation validation system.

## Requirements

### Functional Requirements

1. The system should validate metadata
2. The system should check file structure
3. The system should detect issues

### Non-Functional Requirements

- Performance should be acceptable
- Memory usage should be reasonable

## Implementation

### Architecture

The validation system consists of multiple components:

- Template compliance validator
- Cross-reference validator
- File size monitor
- Metadata validator

### Code Structure

```python
def validate_file(file_path):
    # Validation logic here
    pass
```

## Testing

### Unit Tests

- Test metadata validation
- Test template compliance
- Test cross-reference checking

### Integration Tests

- Test full validation pipeline
- Test error handling
- Test performance

## Dependencies

- Python 3.7+
- PyYAML library
- Requests library

## Related Files

- @/scripts/validation/README.md
- @/docs/developers/architecture/overview.md
"""
    
    with open(valid_file, 'w') as f:
        f.write(valid_content)
    
    # Create an invalid feature documentation file
    invalid_file = test_dir / "invalid_feature.md"
    invalid_content = """---
title: "Bad File"
status: "INVALID_STATUS"
priority: "WRONG"
# Missing required fields
---

# This file has issues

This file is missing required metadata and has invalid values.

TODO: Fix this file
FIXME: Many issues here

This file is intentionally large to test size limits.
""" + "\\n" * 600  # Make it oversized
    
    with open(invalid_file, 'w') as f:
        f.write(invalid_content)
    
    # Create a file without metadata
    no_metadata_file = test_dir / "no_metadata.md"
    no_metadata_content = """# File Without Metadata

This file has no YAML frontmatter metadata.

It should fail metadata validation.
"""
    
    with open(no_metadata_file, 'w') as f:
        f.write(no_metadata_content)
    
    # Create a file with broken references
    broken_refs_file = test_dir / "broken_refs.md"
    broken_refs_content = """---
title: "File with Broken References"
status: "DRAFT"
priority: "LOW"
category: "TESTING"
version: "1.0.0"
description: "File with broken cross-references for testing."
---

# File with Broken References

This file contains broken references:

- Link to non-existent file: [Missing File](missing_file.md)
- Broken file reference: @/non/existent/path.md
- Invalid URL: http://this-domain-does-not-exist-12345.invalid
- Relative path to nowhere: ./missing/directory/file.txt

These should be detected by the cross-reference validator.
"""
    
    with open(broken_refs_file, 'w') as f:
        f.write(broken_refs_content)
    
    return test_dir

def test_individual_validators(test_dir):
    """Test individual validation scripts."""
    script_dir = Path(__file__).parent
    results = {}
    
    validators = [
        ("Template Compliance", "validate_feature_template_compliance.py"),
        ("Metadata Validation", "validate_metadata.py"),
        ("File Size Monitor", "monitor_file_sizes.py"),
        ("Cross References", "validate_cross_references.py"),
        ("Outdated References", "check_outdated_references.py"),
        ("Modularization Analysis", "analyze_modularization_opportunities.py")
    ]
    
    for name, script in validators:
        script_path = script_dir / script
        if script_path.exists():
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, str(script_path), str(test_dir),
                    "--format", "json", "--quiet"
                ], capture_output=True, text=True, timeout=60)
                
                results[name] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "exit_code": result.returncode,
                    "output_length": len(result.stdout),
                    "has_json_output": result.stdout.strip().startswith('{'),
                    "error": result.stderr if result.stderr else None
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            results[name] = {
                "status": "error",
                "error": f"Script not found: {script_path}"
            }
    
    return results

def test_comprehensive_runner(test_dir):
    """Test the comprehensive validation runner."""
    script_dir = Path(__file__).parent
    runner_script = script_dir / "run_all_validations.py"
    
    if not runner_script.exists():
        return {"status": "error", "error": "Comprehensive runner not found"}
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, str(runner_script), str(test_dir),
            "--format", "json", "--timeout", "30"
        ], capture_output=True, text=True, timeout=120)
        
        # Try to parse JSON output
        try:
            output_data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            output_data = {}
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "has_json_output": bool(output_data),
            "summary": output_data.get("summary", {}),
            "error": result.stderr if result.stderr else None
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def run_validation_tests():
    """Run comprehensive validation system tests."""
    print("Testing Documentation Validation System")
    print("=" * 50)
    
    # Create test files
    print("Creating test files...")
    test_dir = create_test_files()
    print(f"Test directory: {test_dir}")
    
    # Test individual validators
    print("\\nTesting individual validators...")
    individual_results = test_individual_validators(test_dir)
    
    for name, result in individual_results.items():
        status_icon = {"passed": "✅", "failed": "❌", "error": "⚠️"}.get(result["status"], "❓")
        print(f"{status_icon} {name}: {result['status']}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
        elif result["status"] == "passed":
            print(f"   JSON output: {'Yes' if result.get('has_json_output') else 'No'}")
    
    # Test comprehensive runner
    print("\\nTesting comprehensive runner...")
    runner_result = test_comprehensive_runner(test_dir)
    
    status_icon = {"passed": "✅", "failed": "❌", "error": "⚠️"}.get(runner_result["status"], "❓")
    print(f"{status_icon} Comprehensive Runner: {runner_result['status']}")
    if runner_result.get("error"):
        print(f"   Error: {runner_result['error']}")
    elif runner_result.get("summary"):
        summary = runner_result["summary"]
        print(f"   Validators run: {summary.get('total_validators', 0)}")
        print(f"   Success rate: {summary.get('passed_validators', 0)}/{summary.get('total_validators', 0)}")
    
    # Calculate overall results
    passed_individual = sum(1 for r in individual_results.values() if r["status"] == "passed")
    total_individual = len(individual_results)
    runner_passed = runner_result["status"] == "passed"
    
    print("\\nTest Summary:")
    print("-" * 20)
    print(f"Individual validators: {passed_individual}/{total_individual} passed")
    print(f"Comprehensive runner: {'Passed' if runner_passed else 'Failed'}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print(f"\\nCleaned up test directory: {test_dir}")
    
    # Overall assessment
    if passed_individual == total_individual and runner_passed:
        print("\\n✅ All tests passed! Validation system is working correctly.")
        return 0
    elif passed_individual > 0 or runner_passed:
        print("\\n⚠️ Some tests passed. Validation system is partially working.")
        return 1
    else:
        print("\\n❌ All tests failed. Validation system needs fixing.")
        return 2

def main():
    """Main test execution."""
    try:
        return run_validation_tests()
    except KeyboardInterrupt:
        print("\\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\\n❌ Test execution failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())