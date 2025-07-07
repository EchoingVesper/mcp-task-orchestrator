# Tests - Validation and Quality Assurance

## Testing Architecture

**Multi-Level Testing**: Unit, integration, and performance tests for Clean Architecture validation.

## Structure

### Core Test Categories
- **`unit/`** - Component-level tests for individual classes
- **`integration/`** - Cross-component workflow validation
- **`performance/`** - System performance and resource usage
- **`fixtures/`** - Test utilities and sample data

### Enhanced Testing Infrastructure
- **Alternative test runners** - Prevent output truncation and hanging
- **File-based output** - Complete test result capture
- **Resource cleanup** - Automatic database connection management
- **Hang detection** - Timeout mechanisms for reliability

## Test Execution

### Enhanced Runners (Recommended)
```bash
# Alternative runner (prevents truncation)
python enhanced_migration_test.py

# Resource cleanup validation
python test_resource_cleanup.py

# Hang detection testing
python test_hang_detection.py
```

### Traditional Testing
```bash
# Standard pytest
pytest

# Category-specific
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Skip slow tests
```

## Clean Architecture Testing

### Layer Testing Strategy
- **Domain**: Test entities and value objects in isolation
- **Application**: Test use cases with mocked repositories
- **Infrastructure**: Test repository implementations with real databases
- **Presentation**: Test MCP request/response handling

## File Size Warnings
Critical test files needing refactoring:
- `validation_suite.py` (837 lines)
- `unit/test_generic_repository.py` (676 lines)