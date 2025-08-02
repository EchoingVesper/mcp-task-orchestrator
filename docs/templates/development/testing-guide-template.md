
# CLAUDE.md

**[CURRENT]** Claude Code guidance for Testing Infrastructure in MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 400 lines for Claude Code stability

#
# Status Header

- **Status**: [CURRENT]

- **Context**: Testing and Quality Assurance Infrastructure

- **Architecture Layer**: Cross-cutting (tests all layers)

#
# Context Analysis

#
## Directory Purpose

Comprehensive testing infrastructure for validating Clean Architecture implementation across all layers.

#
## Scope

- Unit tests for individual components and services

- Integration tests for cross-layer workflows

- Performance tests for system resource usage

- Test utilities and fixtures for consistent testing

#
## Architectural Role

Validates the Clean Architecture implementation by:

- Testing domain logic in isolation

- Verifying use case orchestration

- Validating infrastructure implementations

- Ensuring presentation layer integration

#
# Core Commands

#
## Essential Testing Operations

```bash

# Run all tests

pytest

# Run specific test categories

pytest -m unit           
# Unit tests only
pytest -m integration    
# Integration tests
pytest -m performance    
# Performance tests
pytest -m "not slow"     
# Skip slow tests

# Run tests for specific layers

pytest tests/unit/domain/
pytest tests/unit/application/
pytest tests/integration/

```text

#
## Alternative Test Runners

```text
bash

# More reliable output for complex tests

python tests/test_resource_cleanup.py
python tests/test_hang_detection.py
python tests/enhanced_migration_test.py

# File-based output system (prevents truncation)

python tests/test_real_implementations_comprehensive.py

```text

#
## Coverage and Quality

```text
bash

# Run tests with coverage

pytest --cov=mcp_task_orchestrator

# Generate coverage report

pytest --cov=mcp_task_orchestrator --cov-report=html

# Run linting on test files

black tests/
isort tests/

```text

#
# Directory Structure

```text
bash
tests/
├── unit/                    
# Component-level tests
│   ├── domain/             
# Domain layer tests
│   ├── application/        
# Application layer tests
│   └── infrastructure/     
# Infrastructure tests
├── integration/            
# Cross-component workflow tests
│   ├── test_task_execution.py
│   ├── test_complete_task.py
│   └── test_real_implementations_*.py
├── performance/            
# System performance tests
│   └── test_error_handling_performance.py
├── fixtures/               
# Test utilities and sample data
├── error_handling/         
# Error scenario tests
└── CLAUDE.md              
# This file

```text

#
# Development Patterns

#
## Writing Unit Tests

- Test domain entities in isolation without external dependencies

- Mock infrastructure dependencies for application layer tests

- Focus on business logic validation and invariant checking

- Use file-based output for tests that produce long results

#
## Writing Integration Tests

- Test complete workflows from presentation to infrastructure

- Validate clean architecture dependency flow

- Use real database connections with proper cleanup

- Test error handling and recovery scenarios

#
## Performance Testing

- Monitor resource usage and cleanup

- Detect memory leaks and connection issues

- Validate system performance under load

- Track metrics over time for regression detection

#
# Integration Points

#
## MCP Tool Integration

- Test all MCP tools through complete request/response cycles

- Validate tool registration and handler implementation

- Test error scenarios and recovery mechanisms

- Ensure proper resource cleanup after tool execution

#
## Clean Architecture Integration

- **Domain Tests**: Validate business logic without external dependencies

- **Application Tests**: Test use case orchestration with mocked infrastructure

- **Infrastructure Tests**: Test repository implementations and external adapters

- **Integration Tests**: Validate complete layer interaction

#
## Database Integration

- Use test databases with automatic cleanup

- Test migration scenarios and rollback capabilities

- Validate workspace-aware database organization

- Monitor connection management and resource cleanup

#
# Troubleshooting

#
## Common Issues

- **Resource Warnings**: Indicate database connection leaks - check context manager usage

- **Test Timeouts**: Use alternative test runners or file-based output

- **Hanging Tests**: Use hang detection utilities to identify problematic tests

- **Flaky Tests**: Isolate tests and ensure proper cleanup between runs

#
## Debugging Tests

```text
bash

# Run single test with verbose output

pytest tests/test_specific.py -v -s

# Debug hanging tests

python tests/test_hang_detection.py

# Check resource cleanup

python tests/test_resource_cleanup.py

# Performance analysis

python tests/performance/test_error_handling_performance.py
```text

#
## Performance Considerations

- Use file-based output system to prevent truncation

- Implement proper resource cleanup in test fixtures

- Monitor test execution time and resource usage

- Use alternative test runners for reliability

#
# Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../docs/CLAUDE.md) - Complete documentation system

- **Core Package**: [mcp_task_orchestrator/CLAUDE.md](../mcp_task_orchestrator/CLAUDE.md) - Implementation details

- **Scripts Reference**: [scripts/CLAUDE.md](../scripts/CLAUDE.md) - Testing utilities

#
## Related Documentation

- [Testing Best Practices](../docs/developers/contributing/testing/TESTING_BEST_PRACTICES.md)

- [Testing Guidelines](../docs/developers/contributing/testing/TESTING_GUIDELINES.md)

- [Comprehensive Test Reports](../docs/developers/contributing/testing/)

#
# Quality Checklist

- [ ] File size under 400 lines for Claude Code stability

- [ ] Status header current and reflects testing scope

- [ ] All test categories properly documented

- [ ] Directory structure reflects current test organization

- [ ] Commands tested and functional across all test types

- [ ] Cross-references accurate and up-to-date

- [ ] Development patterns reflect current testing best practices

- [ ] Test organization categories clearly defined

- [ ] Integration points completely documented

- [ ] Troubleshooting addresses real testing issues

- [ ] Accessibility guidelines followed (proper heading hierarchy)

- [ ] Code blocks specify language (bash, python, yaml, etc.)

- [ ] Related documentation links verified

#
# Maintenance Notes

#
## Update Procedures

- Add tests when implementing new features or fixing bugs

- Maintain test coverage across all architecture layers

- Update test fixtures when domain models change

- Ensure proper cleanup in all test scenarios

#
## Validation Requirements

- All domain entities must have comprehensive unit tests

- All use cases must have integration tests

- All MCP tools must have end-to-end tests

- Performance tests must validate resource cleanup

- **Template Compliance**: Must pass `python scripts/validation/validate_template_compliance.py`

- **Cross-Reference Accuracy**: Must pass `python scripts/validation/validate_cross_references.py`

- **Style Guide Compliance**: Must follow [Style Guide](../style-guide.md) standards

- **Testing Standards**: Follow established testing patterns and conventions

#
## Dependencies

- pytest framework for test execution and fixtures

- Coverage tools for test coverage measurement

- File-based output system for reliable test results

- Resource monitoring utilities for leak detection

#
# Accessibility Notes

- **Heading Hierarchy**: Always follow proper H1 → H2 → H3 structure

- **Screen Reader Compatibility**: Use descriptive link text and alt text

- **Language Specification**: All code blocks must specify language

- **Consistent Navigation**: Cross-references enable logical navigation paths

- **Test Documentation**: Clear test descriptions and coverage explanations

---

📋 **This testing infrastructure validates the complete Clean Architecture. See [CLAUDE.md](../CLAUDE.md) for essential commands, [Style Guide](../style-guide.md) for writing standards, and [CLAUDE-detailed.md](../CLAUDE-detailed.md) for comprehensive testing strategies.**
