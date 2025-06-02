# Maintenance and Streaming System Test Suite

This directory contains comprehensive tests for the maintenance features and streaming system of the MCP Task Orchestrator.

## Test Structure

### Unit Tests

1. **`test_maintenance_coordinator.py`**
   - Tests all maintenance actions (scan_cleanup, validate_structure, update_documentation, prepare_handover)
   - Tests different scopes (current_session, full_project, specific_subtask)
   - Tests validation levels (basic, comprehensive, full_audit)
   - Error handling and edge cases
   - Concurrent operation handling

2. **`test_task_lifecycle_manager.py`**
   - Stale task detection with different specialist thresholds
   - Task archival functionality (single and bulk)
   - Cleanup recommendation generation
   - Lifecycle state transitions
   - Retention policy enforcement

3. **`test_streaming_artifacts.py`**
   - Large content storage without truncation (up to 10MB tested)
   - Cross-context accessibility (simulates context resets)
   - File mirroring functionality
   - Metadata preservation
   - Partial session resumption
   - Concurrent session handling
   - Atomic operations and corruption detection

### Integration Tests

**`test_maintenance_integration.py`**
- Complete task lifecycle workflow (creation → execution → archival)
- Real database operations
- Maintenance operations with actual file system
- Streaming system preservation across context resets
- Bulk operation performance
- Error recovery and system resilience

## Running the Tests

### Quick Start

Run all maintenance and streaming tests:
```bash
python tests/run_maintenance_tests.py
```

### Individual Test Suites

Run only unit tests:
```bash
pytest tests/unit/test_maintenance_coordinator.py -v
pytest tests/unit/test_task_lifecycle_manager.py -v
pytest tests/unit/test_streaming_artifacts.py -v
```

Run integration tests:
```bash
pytest tests/integration/test_maintenance_integration.py -v
```

### With Coverage

Run with coverage analysis:
```bash
pytest tests/unit/test_*.py --cov=mcp_task_orchestrator --cov-report=html
```

### Filtering Tests

Run specific test categories:
```bash
# Only maintenance tests
pytest -m maintenance

# Only streaming tests  
pytest -m streaming

# Skip slow tests
pytest -m "not slow"
```

## Test Scenarios Covered

### MaintenanceCoordinator
- ✅ Basic scan and cleanup for all scopes
- ✅ Comprehensive validation with issue detection
- ✅ Documentation generation with cross-references
- ✅ Handover package preparation
- ✅ Database error handling
- ✅ Concurrent operation management
- ✅ Empty project handling
- ✅ Large-scale cleanup with batching

### TaskLifecycleManager
- ✅ Specialist-specific stale thresholds
- ✅ Advanced stale detection heuristics
- ✅ Task archival with artifact preservation
- ✅ Subtask archival cascading
- ✅ Cleanup recommendations based on retention
- ✅ Bulk archival operations
- ✅ Error handling for missing tasks

### StreamingArtifactManager
- ✅ Large file handling (10MB+)
- ✅ Progress tracking with percentages
- ✅ Session interruption and resumption
- ✅ File mirroring for multiple files
- ✅ Metadata storage and retrieval
- ✅ Artifact search and filtering
- ✅ Atomic operations preventing corruption
- ✅ Incomplete session cleanup
- ✅ Concurrent session isolation
- ✅ Disk space monitoring
- ✅ Corruption detection and recovery

### Integration Scenarios
- ✅ Full workflow from task planning to archival
- ✅ Stale task detection → recommendation → cleanup
- ✅ Context preservation across resets
- ✅ File mirroring with maintenance operations
- ✅ Performance with 50+ tasks
- ✅ System resilience to corrupted state

## Performance Benchmarks

The test suite includes performance benchmarks for:
- Streaming throughput (MB/s)
- Maintenance scan time for large projects
- Bulk archive operations (tasks/second)
- Memory usage monitoring

## Test Output

After running the full test suite, you'll find:
- `test_results/maintenance_test_report.md` - Comprehensive test report
- `test_results/unit_tests.html` - Detailed unit test results
- `test_results/integration_tests.html` - Integration test results
- `test_results/coverage_html/index.html` - Code coverage report
- `test_results/test_results.json` - Machine-readable results

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in PYTHONPATH
2. **Database Errors**: Tests create temporary databases; ensure write permissions
3. **Timeout Errors**: Increase timeout in pytest.ini for slower systems
4. **File System Errors**: Tests need temp directory access

### Debug Mode

Run with full output for debugging:
```bash
pytest -vvs --tb=long tests/unit/test_maintenance_coordinator.py::test_name
```

## Contributing

When adding new maintenance or streaming features:
1. Add corresponding unit tests
2. Update integration tests if needed
3. Run the full test suite
4. Ensure coverage remains above 80%
5. Update this README with new test scenarios