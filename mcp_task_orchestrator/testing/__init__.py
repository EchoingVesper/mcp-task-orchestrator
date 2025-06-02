"""
Testing utilities for the MCP Task Orchestrator.

This package provides comprehensive testing tools including:
- File-based test output system with atomic writes
- Pytest integration for seamless test output capture  
- Safe reading mechanisms to prevent timing issues
- Enhanced test runners for existing tests
- Alternative test runners that bypass pytest entirely

The file-based output system solves the critical issue where LLM calls
check test results before tests have finished writing output, causing
truncated or incomplete data to be read.

The alternative test runners provide pytest-free execution with superior
output handling and no truncation issues.
"""

from .file_output_system import (
    TestOutputWriter,
    TestOutputReader, 
    TestOutputMetadata,
    AtomicFileWriter,
    TestOutputSession
)

from .pytest_integration import (
    file_output_test,
    wait_for_test_completion,
    read_test_output_safely,
    configure_pytest_integration,
    get_pytest_output_statistics
)

from .base_test_runner import (
    BaseTestRunner,
    TestResult,
    TestSuite
)

from .direct_runner import (
    DirectFunctionRunner,
    MigrationTestRunner,
    run_tests_directly
)

from .integration_runner import (
    IntegrationTestRunner,
    AsyncTestRunner
)

from .comprehensive_runner import (
    ComprehensiveTestRunner,
    TestRunnerConfig
)

__all__ = [
    # Core file output system
    'TestOutputWriter',
    'TestOutputReader', 
    'TestOutputMetadata',
    'AtomicFileWriter',
    'TestOutputSession',
    
    # Pytest integration
    'file_output_test',
    'wait_for_test_completion', 
    'read_test_output_safely',
    'configure_pytest_integration',
    'get_pytest_output_statistics',
    
    # Alternative test runners
    'BaseTestRunner',
    'TestResult',
    'TestSuite',
    'DirectFunctionRunner',
    'MigrationTestRunner', 
    'IntegrationTestRunner',
    'AsyncTestRunner',
    'ComprehensiveTestRunner',
    'TestRunnerConfig',
    'run_tests_directly'
]

# Version info
__version__ = "1.0.0"
__author__ = "MCP Task Orchestrator Team"
__description__ = "File-based test output system preventing timing issues"
