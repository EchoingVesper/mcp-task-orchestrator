# MCP Task Orchestrator Release Notes

## Version 1.5.1 - Critical Artifact Path Fix (2025-06-06)

### 🚨 IMMEDIATE ACTION REQUIRED
- **Upgrade Immediately**: This release fixes a critical bug that prevents access to generated artifacts
- **All Users Affected**: Previous versions store artifacts in inaccessible server directories

### 🐛 Critical Bug Fixes
- **FIXED**: Artifact path resolution issue causing artifacts to be written to MCP server directory
  - **Problem**: Artifacts were stored in server's working directory instead of user's project directory
  - **Solution**: Artifacts now correctly stored in `.task_orchestrator/artifacts/` within user's current working directory
  - **Impact**: Resolves functionality issues for users experiencing artifact access problems
  - **User Experience**: Users can now access all generated documentation, analysis, and code artifacts

### 🔧 Infrastructure Improvements
- Synchronized version numbers across all package files (resolved 1.5.0/1.4.0 mismatch)
- Enhanced artifact storage system reliability

### 🎯 Who Should Upgrade
- **All Users**: This bug affects every user attempting to use artifact generation features
- **Development Teams**: Critical for teams relying on task orchestrator for documentation and analysis
- **Production Deployments**: Essential update for any production usage

### 📋 Migration Notes
- No breaking changes to API or configuration
- Existing artifacts may remain in old server locations (can be safely deleted)
- New artifacts will be correctly placed in project directories after upgrade

---

## Version 1.3.1 - Critical Bug Fix Release (2025-05-30)

### 🐛 Critical Bug Fixes
- **CRITICAL**: Fixed `orchestrator_initialize_session` failure preventing tool entry
  - Corrected method name mismatch: `_get_parent_task_id_from_persistence` → `_get_parent_task_id`
  - Resolves initialization issues for new users attempting to use the orchestrator
  - Enables parent task progress tracking and interrupted task detection

### 📚 Documentation Improvements
- **NEW**: `QUICK_START.md` - Streamlined 5-minute setup guide
- **NEW**: `TROUBLESHOOTING.md` - Comprehensive error resolution guide  
- **NEW**: `README_STREAMLINED.md` - Simplified project overview
- Addresses major UX pain point of information overload in documentation

### 🎯 Impact
- Restores orchestrator entry point functionality
- Eliminates critical barrier preventing new user adoption
- Provides clear troubleshooting path for common setup issues
- Reduces cognitive load for first-time users

---

## Version 1.3.0 - Database Persistence Complete (2025-05-29)

### 🎯 Major Features
- **Database Persistence**: Full SQLite-based task and subtask persistence
- **Professional Directory Structure**: Comprehensive project reorganization
- **Enhanced Testing Suite**: Organized test categories (unit/integration/performance)
- **Diagnostic Tools**: Comprehensive system health and maintenance utilities

### ✨ New Features
- SQLite database backend for all task data
- Lock tracking and cleanup mechanisms
- Comprehensive diagnostic and maintenance scripts
- Professional directory organization following Python best practices
- Enhanced documentation structure

### 🔧 Improvements  
- Organized test suite with clear categories
- Better script organization (diagnostics/maintenance/deployment)
- Comprehensive documentation restructure
- Enhanced configuration management
- Better cross-platform compatibility

### 🐛 Bug Fixes
- Fixed critical StateManager `get_parent_task_id` method issue
- Improved Unicode compatibility for console output
- Enhanced error handling and recovery
- Better database connection management

### 📁 Directory Structure
```
MCP Task Orchestrator/
├── tests/
│   ├── integration/     # End-to-end workflow tests
│   ├── unit/           # Component-level tests  
│   ├── performance/    # Performance benchmarks
│   └── fixtures/       # Test utilities
├── scripts/
│   ├── diagnostics/    # System diagnostic tools
│   ├── maintenance/    # Maintenance utilities
│   ├── migrations/     # Data migration scripts
│   └── deployment/     # Installation scripts
├── docs/
│   ├── development/    # Technical implementation guides
│   ├── testing/        # Test procedures and reports
│   └── troubleshooting/ # Diagnostic guides
├── data/              # Database and backup files
└── logs/              # Log files
```

### 🛠️ New Utilities
- `scripts/maintenance/run_tests.py` - Comprehensive test runner
- `scripts/maintenance/cleanup_database.py` - Database cleanup and maintenance
- `scripts/diagnostics/simple_health_check.py` - System health validation
- `scripts/maintenance/setup_project.py` - Project setup and validation

### 📚 Enhanced Documentation
- Complete testing guides and procedures
- Troubleshooting and diagnostic documentation  
- Development implementation guides
- Comprehensive API and usage documentation

### ⚠️ Breaking Changes
None - Fully backward compatible

### 🔄 Migration Notes
- Database files automatically created on first use
- Old task data preserved during upgrade
- New directory structure is optional but recommended
- All existing functionality maintained

### 📋 Known Issues
- None - All critical issues resolved in this release

### 🚀 Next Steps
- Implement parallel task execution capabilities
- Enhanced progress visualization
- Advanced orchestration features

## Version 1.1 (May 27, 2025)

### Major Enhancements

#### LLM-Powered Task Orchestration

- Introduced a new approach that leverages the calling LLM's intelligence for task breakdown
- Added `initialize_session` method to provide guidance to the LLM
- Modified `plan_task` method to accept JSON-formatted subtasks directly from the LLM
- Removed pattern-matching approach in favor of more flexible LLM-driven task analysis

#### Documentation Updates

- Updated README.md to reflect the new LLM-powered approach
- Enhanced usage.md with comprehensive instructions for the new workflow
- Updated DEVELOPER.md with architecture documentation for the new system
- Updated usage_examples.md with examples of the new workflow
- Fixed markdown linting issues across documentation files

### API Changes

- Added new tool: `orchestrator_initialize_session` - Provides context and guidance to the LLM
- Modified `orchestrator_plan_task` tool to accept JSON-formatted subtasks

### Compatibility

- Maintains backward compatibility with existing task orchestration features
- All existing specialist types and state management remain functional

## Version 1.0 (Initial Release)

### Features

- Unified installation system for all supported MCP clients
- Auto-detection of installed clients
- Task decomposition with pattern matching
- Specialist modes (Architect, Implementer, Debugger, Documenter)
- State management for tracking task progress
- Support for Claude Desktop, Cursor IDE, Windsurf, and VS Code with Cline
