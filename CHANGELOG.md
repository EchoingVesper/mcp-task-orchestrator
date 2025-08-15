
# Changelog

All notable changes to the MCP Task Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

#

# [1.8.1] - 2025-08-15

#

## 🐛 Critical Bug Fixes

- **GitHub Issue #46**: Fixed MockTask JSON serialization error
  - Removed legacy `MockTaskResult` class from `db_integration.py`
  - Implemented unified `ResponseFormatter` for consistent JSON serialization
  - Added `SerializationValidator` to ensure all responses are JSON-compatible
  - **Impact**: Eliminates confusing error messages during task operations

- **GitHub Issue #47**: Fixed `orchestrator_update_task` response formatting
  - Implemented `format_update_response` method in `ResponseFormatter`
  - Enhanced error handling in task handlers for dict vs object responses
  - Added comprehensive response structure validation
  - **Impact**: Resolves "'str' object is not a mapping" errors in task updates

- **GitHub Issue #50**: Fixed `orchestrator_query_tasks` format mismatch
  - Implemented `format_query_response` method returning structured dict instead of raw list
  - Added comprehensive pagination and metadata to query responses
  - Enhanced compatibility between use case and handler response expectations
  - **Impact**: Resolves "list indices must be integers or slices, not str" errors

#

## 🚀 New Features

- **GitHub Issue #48**: Implemented missing `delete_task` functionality
  - Added `delete_task` method to `CleanArchTaskUseCase` with full parameter support
  - Implemented repository-level `delete_task` with dependency checking and archival
  - Added comprehensive error handling for deletion edge cases
  - **Parameters**: `task_id`, `force` (default: false), `archive_instead` (default: true)
  - **Impact**: Restores complete task lifecycle management capabilities

- **GitHub Issue #49**: Implemented missing `cancel_task` functionality (PARTIAL)
  - Added `cancel_task` method to `CleanArchTaskUseCase` with work preservation
  - Implemented task cancellation with artifact preservation and state management
  - Added proper reason tracking and dependent task updating
  - **Parameters**: `task_id`, `reason` (optional), `preserve_work` (default: true)
  - **Status**: Use case implemented, repository interface completion pending
  - **Impact**: Enables graceful task cancellation with work preservation

#

## 🔧 Infrastructure

- **Unified Compatibility Layer**: New architecture for consistent response formatting
  - Introduced `ResponseFormatter` class with standardized formatting methods
  - Implemented `SerializationValidator` for JSON compatibility validation
  - Created unified error handling patterns across all operations
  - Established interface contracts for all use case methods

- **Enhanced Testing Coverage**: Comprehensive test suite for all fixes
  - Added integration tests for Issues #46, #47, #50 (compatibility-layer worktree)
  - Added unit tests for Issues #48, #49 (missing-methods worktree)
  - Validation scores: 4 of 5 issues fully implemented, 1 partial (91.6% average)
  - Comprehensive regression testing to ensure no existing functionality broken

#

## 📊 Migration Notes

### Breaking Changes
- `MockTaskResult` class removed - all responses now return `Dict[str, Any]`
- `orchestrator_query_tasks` now returns structured dict instead of raw list
- Response format standardized across all use case methods

### API Enhancements
- New `orchestrator_delete_task` tool available
- New `orchestrator_cancel_task` tool available (repository interface completion pending)
- Enhanced error messages with structured error information
- Improved response metadata for better debugging and monitoring

#

# [1.8.0] - 2025-06-08

#

## 🚀 Major Features

- **Workspace Paradigm Implementation**: Complete transition from session-based to workspace-based architecture
  - Smart working directory detection with PROJECT_MARKERS (package.json, pyproject.toml, Cargo.toml, go.mod, etc.)
  - Automatic workspace root detection for improved artifact and task organization
  - Enhanced DirectoryDetector class with comprehensive project marker recognition
  - Database schema migration to support workspace_id columns across all tables

#

## Fixed

- **CRITICAL**: Database migration system SQLAlchemy 2.0+ compatibility issues
  - Fixed `'RootTransaction' object has no attribute 'execute'` errors in migration execution
  - Corrected transaction handling using `engine.connect()` with `conn.begin()` pattern
  - Added proper `text()` wrapper for all raw SQL executions
  - Resolved migration manager connection passing in auto-migration system

- **Server Import Conflicts**: Resolved server.py vs server/ package naming conflicts
  - Renamed mcp_task_orchestrator/server/ to mcp_task_orchestrator/reboot/
  - Updated all imports to use new package structure
  - Eliminated Python module import ambiguity issues

- **Logging Configuration**: Fixed Claude Code MCP client error display issues
  - Configured logging to send INFO messages to stdout and WARNING+ to stderr
  - Eliminated false "ERROR" labels on informational startup messages
  - Improved MCP client compatibility with proper stream separation

#

## Enhanced

- **Database Migration System**: Improved reliability and error handling
  - Enhanced automatic schema detection and migration execution
  - Better backup creation and rollback capabilities  
  - Comprehensive migration history tracking with batch operations
  - Conservative timeout settings with detailed operation logging

#

## Infrastructure

- **Production Readiness**: Completed workspace paradigm with full backward compatibility

- **Enhanced Testing**: All migration and workspace detection systems thoroughly validated

- **Improved Documentation**: Updated installation and configuration guides for workspace paradigm

#

# [1.6.1] - 2025-06-07

#

## Added

- Health monitoring system with real-time scoring and trend analysis

- Automated maintenance scheduler for build cleanup and cache management

- Professional Claude Code session templates and development guides

- Comprehensive project structure validation tools

- Main entry point fix for package installation (`main_sync()` in server/\_\_init\_\_.py)

#

## Changed

- Complete repository reorganization achieving 100/100 health score

- Scripts moved to purpose-based directories (build/, testing/, diagnostics/, deployment/)

- Documentation restructured with professional information architecture

- Virtual environments consolidated from 6 to 1 (venv_mcp)

- Root files reduced from 61 to 11 (-82%)

#

## Fixed

- **CRITICAL**: Task orchestrator package loading issue preventing MCP client connections

- Console script entry point now works correctly when installed via pip

- Import issues resolved with dynamic code loading for package context

#

## Infrastructure

- well-structured repository organization following industry standards

- CI/CD ready structure with automated quality assurance

- Enhanced testing infrastructure with reliable runners

- Complete backward compatibility maintained

#

# [1.6.0] - 2025-06-06

#

## 🚀 Major Features

- **Automatic Database Migration System**: Complete automatic schema detection, migration execution, and rollback capabilities
  - AutoMigrationSystem with comprehensive safety mechanisms and backup creation
  - Schema comparison and migration complexity analysis
  - Migration history tracking and failure recovery
  - Server startup integration with conservative timeout settings
  - Comprehensive testing suite with 95/100 quality score

- **In-Context Server Reboot**: well-tested server restart functionality with state preservation
  - Graceful shutdown coordination with task suspension and resource cleanup
  - Client connection preservation and request buffering during restart
  - Complete state serialization and restoration across reboots
  - MCP tools for restart operations: `orchestrator_restart_server`, `orchestrator_health_check`, `orchestrator_shutdown_prepare`
  - Comprehensive test coverage with 50+ test methods across all scenarios

#

## 🔧 Infrastructure  

- Enhanced testing infrastructure with file-based output system

- Improved error handling and recovery mechanisms

- Performance optimizations for large-scale operations

- Comprehensive documentation for operational procedures

#

## 📊 Quality & Testing

- Database migration system: 95% test success rate with well-tested deployment approval

- Server reboot system: Comprehensive test coverage ready for staging deployment

- Enhanced test runners preventing output truncation and hang detection

- Resource management validation preventing memory leaks

#

# [1.5.1] - 2025-06-06

#

## 🐛 Critical Bug Fixes

- **CRITICAL**: Fixed artifact path resolution issue where artifacts were written to MCP server directory instead of user's current working directory
  - Artifacts are now correctly stored in `.task_orchestrator/artifacts/` within the user's project directory
  - Restores accessibility to all generated artifacts for 100% of users
  - Enables proper artifact retrieval and prevents accumulation in wrong locations
  - **Impact**: This bug rendered the artifact system non-functional for practical use

#

## 🔧 Infrastructure

- Resolved version inconsistency between setup.py (1.5.0) and package \_\_init\_\_.py (1.4.0)

- Both version declarations now synchronized at 1.5.1

#

# [1.4.0] - 2025-05-30

> **Editor's Note**: Massive documentation reorganization and enhancement inspired by constructive feedback from KECG, who correctly identified the need for clearer input-to-output examples, human-authored documentation, and concrete use cases. Sometimes the harshest critics provide the most valuable direction.

#

## 🎉 Major Features

- **Claude Code MCP Integration**: Complete integration guides and coordination patterns

- **Visual Documentation System**: ASCII diagrams and flowcharts for universal compatibility  

- **Dual-Audience Architecture**: Parallel documentation for humans and LLM agents

#

## 📚 Documentation

- Complete documentation restructure with user-guide/ and llm-agents/ directories

- Character-optimized documentation for LLM tool compatibility (1200-2000 chars)

- Real-world examples across data processing, modernization, and enterprise coordination

- Comprehensive visual guides with setup flows and troubleshooting trees

- Master documentation index (INDEX.md) with multi-audience navigation

- Cross-referencing system linking all documentation components

#

## 🔗 Integration Patterns

- Sequential Coordination Pattern (core pattern for MCP integration)

- Parallel execution and graceful degradation strategies

- Multi-server coordination patterns

- Aggregator integration patterns

#

## ✨ Visual Assets

- Architecture overview diagrams with ASCII art

- Sequential coordination workflow flowcharts

- Setup and installation visual guides

- Troubleshooting decision trees

- Integration patterns visual documentation

#

# [1.3.3] - 2025-05-30

#

## 📚 Documentation

- Documentation architecture redesign and foundation restructure

- New dual-audience structure (user-guide/ + llm-agents/)

- Integration patterns documentation with real coordination examples

- Real-world examples and workflows across 5 major categories

- LLM agent workflow guides with character optimization

- Core sequential coordination pattern establishment

#

# [1.3.2] - 2025-05-30

#

## 🔧 Installation

- Installation script fixes and improvements

- Enhanced installation documentation and error handling

- Cross-documentation consistency verification

- Backward compatibility and migration notes

- Installation instructions testing and validation

#

# [1.3.1] - Previous Release

#

## Initial Features

- Core MCP task orchestration functionality

- Specialist role system

- Basic documentation framework
