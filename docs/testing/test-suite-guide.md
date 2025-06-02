# Test Suite Guide - MCP Task Orchestrator

## Overview

This guide explains how to run and maintain the test suite for the MCP Task Orchestrator. The tests are organized into categories for different testing purposes and deployment scenarios.

## Test Directory Structure

```
tests/
├── integration/          # Full pipeline tests
├── unit/                 # Isolated component tests  
├── performance/          # Performance benchmarks
├── fixtures/             # Test utilities and helpers
├── test_db_persistence.py # Database persistence tests
└── test_server.py        # Server functionality tests
```

## Test Categories

### Integration Tests (`tests/integration/`)
Full end-to-end tests that verify complete workflows:

- `test_complete_subtask.py` - Complete task execution pipeline
- `test_orchestrator.py` - Full orchestrator functionality  
- `test_subtask_execution.py` - Subtask workflow validation
- `test_synchronization_fix.py` - Complex synchronization scenarios

**How to run:**
```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific integration test
python -m pytest tests/integration/test_orchestrator.py -v
```

### Unit Tests (`tests/unit/`)
Isolated tests for individual components:

- Database operations: `test_persistence.py`, `test_main_db.py`
- Fix validations: `test_artifacts_fix.py`, `test_cleanup_locks.py`
- Core functionality: `test_detection.py`, `test_validation.py`
- Protocol tests: `test_mcp_protocol.py`

**How to run:**
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific component tests
python -m pytest tests/unit/test_persistence.py -v
```

### Performance Tests (`tests/performance/`)
Performance benchmarks and load testing:

- `performance_benchmark.py` - Comprehensive performance metrics
- `simple_sync_test.py`, `quick_sync_test.py` - Basic performance validation
- `test_performance_fix.py` - Verification of performance improvements

**How to run:**
```bash
# Run performance benchmarks  
python -m pytest tests/performance/ -v

# Run specific performance test
python tests/performance/performance_benchmark.py
```

### Test Fixtures (`tests/fixtures/`)
Test utilities and helper scripts:

- `run_test.py`, `run_startup_test.py` - Test execution utilities
- `detailed_test.py` - Comprehensive test scenarios
- `test_db_persistence_script.py` - Database testing script

## Running Tests

### Prerequisites
```bash
# Ensure virtual environment is activated
source venv_mcp/bin/activate  # Linux/Mac
# or
venv_mcp\Scripts\activate     # Windows

# Install test dependencies
pip install pytest pytest-asyncio
```

### Quick Test Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests by category
python -m pytest tests/unit/ -v          # Unit tests only
python -m pytest tests/integration/ -v   # Integration tests only  
python -m pytest tests/performance/ -v   # Performance tests only

# Run with coverage
python -m pytest tests/ --cov=mcp_task_orchestrator --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_persistence.py -v

# Run with detailed output
python -m pytest tests/ -v -s
```

### Test Environment Setup

#### Database Setup
Tests use either in-memory databases or isolated test databases:

```bash
# For tests requiring persistent database
export TEST_DB_PATH="test_orchestrator.db"

# For integration tests with real database
export INTEGRATION_DB_PATH="integration_test.db"
```

#### Configuration
Test configuration is handled automatically, but you can override:

```bash
# Override test timeout (in seconds)
export TEST_TIMEOUT=30

# Enable debug output
export DEBUG_TESTS=true

# Skip slow tests
export SKIP_SLOW_TESTS=true
```

## Performance Benchmarks

### Expected Performance Metrics

**Unit Tests:**
- Test execution time: <5 seconds per file
- Database operations: <100ms per operation
- Memory usage: <50MB during test execution

**Integration Tests:**
- Complete workflow: <15 seconds
- Concurrent operations: <30 seconds
- Database persistence: <10 seconds

**Performance Tests:**
- Baseline operations: >100 ops/second
- Concurrent tasks: >10 simultaneous tasks
- Memory efficiency: <500MB peak usage

### Benchmark Commands

```bash
# Run performance benchmarks
python tests/performance/performance_benchmark.py

# Generate performance report
python -m pytest tests/performance/ --benchmark-only --benchmark-sort=mean
```

## Troubleshooting Test Failures

### Common Issues

#### Database Lock Errors
```bash
# Clear test databases
rm -f test_*.db integration_*.db

# Run tests with fresh database
python -m pytest tests/ --fresh-db
```

#### Import Errors
```bash
# Verify package installation
pip install -e .

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Timeout Issues
```bash
# Increase test timeout
export TEST_TIMEOUT=60

# Run with timeout debugging
python -m pytest tests/ -v --timeout=60 --timeout-method=thread
```

### Test Debugging

```bash
# Run with maximum verbosity
python -m pytest tests/ -vvv -s

# Run specific failing test with debug
python -m pytest tests/unit/test_persistence.py::test_specific_function -vvv -s

# Enable logging during tests
python -m pytest tests/ --log-level=DEBUG
```

## Continuous Integration

### Pre-commit Checks
```bash
# Run full test suite before commit
python -m pytest tests/ -v

# Quick validation
python -m pytest tests/unit/ -v
```

### Test Data Management
- Test databases are automatically cleaned up
- Temporary files are removed after test completion
- No persistent test data should remain after test runs

## Contributing Test Cases

### Writing New Tests
1. Follow existing test structure and naming conventions
2. Include both positive and negative test cases  
3. Add appropriate setup and teardown
4. Document test purpose and expected behavior
5. Ensure tests are isolated and don't depend on external state

### Test Coverage Goals
- Unit tests: >90% code coverage
- Integration tests: All major workflows covered
- Performance tests: All critical operations benchmarked
- Error scenarios: Common failure modes tested
