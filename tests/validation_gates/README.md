
# MCP Task Orchestrator Validation Gates

#
# Overview

This directory contains a comprehensive validation framework for systematic testing of all 16 MCP Task Orchestrator tools. The framework provides automated testing with 3x validation levels per tool, immediate issue resolution, and progress tracking.

#
# Components

#
## 1. Testing Framework (`validation_framework.py`)

- **ValidationFramework**: Main framework class for running validation gates

- **TestLevel**: Enum for test levels (BASIC, EDGE_CASES, INTEGRATION, ALL)

- **TestResult**: Data structure for individual test results

- **ToolSpec**: Specifications for each tool with validation gates

#
## 2. Tool-Specific Test Cases (`tool_test_cases.py`)

- **CoreToolTests**: Tests for core orchestration tools

- **TaskToolTests**: Tests for task management tools

- **RebootToolTests**: Tests for server reboot tools

- **TestCaseRegistry**: Registry for organizing and executing test cases

#
## 3. Automated Test Runner (`test_runner.py`)

- **TestRunner**: Main test runner with retry logic and issue resolution

- Continuous testing capabilities

- Priority-based test execution

- Progress tracking and reporting

#
## 4. Issue Resolution Workflows (`issue_resolution_workflows.py`)

- **IssueResolutionManager**: Coordinates issue resolution across resolvers

- **DatabaseIssueResolver**: Handles database-related issues

- **ServerIssueResolver**: Handles server-related issues

- **PermissionIssueResolver**: Handles permission-related issues

#
## 5. Progress Tracking (`MCP_TOOLS_TESTING_TRACKER.md`)

- Comprehensive checkbox tracking for all 16 tools

- 3x validation levels per tool (Basic, Edge Cases, Integration)

- Real-time progress updates

- Issue tracking and resolution notes

#
# Quick Start

#
## 1. Run Tests for a Single Tool

```bash

# Basic functionality tests

python validation_framework.py --tool orchestrator_get_status --level basic

# All validation levels

python validation_framework.py --tool orchestrator_get_status --level all

```text

#
## 2. Run Tests for All Tools

```text
bash

# Run all tools with basic validation

python validation_framework.py --all --level basic

# Run all tools with comprehensive validation

python validation_framework.py --all --level all

```text

#
## 3. Use the Automated Test Runner

```text
bash

# Run single tool with retry logic

python test_runner.py --tool orchestrator_get_status --level basic

# Run all tools with stop-on-failure

python test_runner.py --run-all --stop-on-failure

# Continuous testing (every 5 minutes)

python test_runner.py --continuous --interval 300

# Priority-based testing

python test_runner.py --priority-based --level all

```text

#
## 4. Generate Reports

```text
bash

# Generate test report

python validation_framework.py --report

# Generate progress report

python test_runner.py --progress-report

```text

#
# Tool Categories

#
## Core Orchestration Tools (3 tools)

1. **orchestrator_initialize_session** - Session initialization

2. **orchestrator_get_status** - Status retrieval

3. **orchestrator_synthesize_results** - Result synthesis

#
## Task Management Tools (8 tools)

4. **orchestrator_plan_task** - Task creation

5. **orchestrator_update_task** - Task updates

6. **orchestrator_delete_task** - Task deletion

7. **orchestrator_cancel_task** - Task cancellation

8. **orchestrator_query_tasks** - Task querying

9. **orchestrator_execute_task** - Task execution

10. **orchestrator_complete_task** - Task completion

11. **orchestrator_maintenance_coordinator** - Maintenance coordination

#
## Server Reboot Tools (5 tools)

12. **orchestrator_restart_server** - Server restart

13. **orchestrator_health_check** - Health checking

14. **orchestrator_shutdown_prepare** - Shutdown preparation

15. **orchestrator_reconnect_test** - Reconnection testing

16. **orchestrator_restart_status** - Restart status

#
# Validation Levels

#
## Basic Functionality

- Core feature validation

- Default parameter testing

- Response format validation

- Basic error handling

#
## Edge Cases

- Boundary condition testing

- Invalid parameter handling

- Error scenario validation

- Performance edge cases

#
## Integration

- Cross-tool interaction testing

- System integration validation

- Performance under load

- End-to-end workflow testing

#
# Issue Resolution

The framework includes automated issue resolution for common problems:

#
## Database Issues

- Connection failures

- Database locks

- Schema mismatches

- Data corruption

#
## Server Issues

- Server not running

- Server crashes

- Timeout problems

- Overload conditions

#
## Permission Issues

- File access denied

- Directory access denied

- General permission problems

#
# Configuration

#
## Environment Variables

- `MCP_TASK_ORCHESTRATOR_USE_DI`: Enable dependency injection mode

- `TEST_DATABASE_PATH`: Custom test database path

- `TEST_OUTPUT_DIR`: Custom output directory for test results

#
## Test Configuration

```text
python

# Test environment configuration

env = TestEnvironment(
    database_path="tests/test_orchestrator.db",
    working_directory="/tmp/test_workspace",
    mock_mode=True,
    performance_timeout=5.0
)

```text

#
# Output Files

#
## Test Results

- `validation_results/validation_report_YYYYMMDD_HHMMSS.json`

- `validation_results/progress_report_YYYYMMDD_HHMMSS.json`

- `validation_results/continuous_results_YYYYMMDD_HHMMSS.json`

#
## Progress Tracking

- `MCP_TOOLS_TESTING_TRACKER.md` - Updated with current progress

- Individual tool status and issue tracking

#
# Best Practices

#
## 1. One Tool at a Time

- Test tools systematically, one at a time

- Complete all 3 validation levels before moving to next tool

- Resolve issues immediately before proceeding

#
## 2. Issue Resolution

- Use automated issue resolution workflows

- Document manual resolution steps

- Track resolution success rates

#
## 3. Continuous Validation

- Run continuous testing for critical tools

- Monitor for regressions

- Maintain test environment health

#
## 4. Progress Tracking

- Update tracking file regularly

- Document issues and resolutions

- Maintain completion statistics

#
# Advanced Usage

#
## Custom Test Cases

```text
python
from tool_test_cases import BaseToolTest, TestResult, TestStatus

class CustomToolTest(BaseToolTest):
    async def test_custom_functionality(self) -> TestResult:
        
# Custom test implementation
        return TestResult(
            name="test_custom_functionality",
            status=TestStatus.PASS,
            duration=0.1,
            output="Custom test passed"
        )

```text

#
## Custom Issue Resolvers

```text
python
from issue_resolution_workflows import IssueResolver, ResolutionResult

class CustomIssueResolver(IssueResolver):
    async def can_resolve(self, issue_type: str, context: Dict[str, Any]) -> bool:
        return issue_type == "custom_issue"
    
    async def resolve(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        
# Custom resolution logic
        return ResolutionResult(
            issue_type=issue_type,
            resolution_applied=True,
            success=True,
            steps_taken=["Custom resolution step"]
        )

```text

#
# Troubleshooting

#
## Common Issues

1. **Test Database Issues**
- Delete test database file and recreate
- Check database permissions
- Verify database schema version

2. **Server Connection Issues**
- Ensure MCP server is running
- Check server port availability
- Verify server configuration

3. **Permission Problems**
- Check file/directory permissions
- Verify user access rights
- Run with appropriate privileges

4. **Performance Issues**
- Increase timeout values
- Run tests individually
- Check system resources

#
## Debug Mode

```text
bash

# Enable debug logging

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m logging.basicConfig --level=DEBUG validation_framework.py --tool orchestrator_get_status

```text

#
# Integration with CI/CD

#
## GitHub Actions Example

```text
yaml
name: MCP Tool Validation
on: [push, pull_request]

jobs:
  validate-tools:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run validation tests
        run: |
          cd tests/validation_gates
          python test_runner.py --run-all --level all --stop-on-failure
```text

#
# Contributing

1. Add new test cases to appropriate test class

2. Implement issue resolvers for new problem types

3. Update tracking file with new tools or test categories

4. Document new features and configuration options

5. Test changes thoroughly before submitting

#
# License

This validation framework is part of the MCP Task Orchestrator project and follows the same license terms.
