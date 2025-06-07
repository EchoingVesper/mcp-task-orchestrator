# Changelog

All notable changes to the MCP Task Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.1] - 2025-06-07

### Added
- Health monitoring system with real-time scoring and trend analysis
- Automated maintenance scheduler for build cleanup and cache management
- Professional Claude Code session templates and development guides
- Comprehensive project structure validation tools
- Main entry point fix for package installation (`main_sync()` in server/__init__.py)

### Changed
- Complete repository reorganization achieving 100/100 health score
- Scripts moved to purpose-based directories (build/, testing/, diagnostics/, deployment/)
- Documentation restructured with professional information architecture
- Virtual environments consolidated from 6 to 1 (venv_mcp)
- Root files reduced from 61 to 11 (-82%)

### Fixed
- **CRITICAL**: Task orchestrator package loading issue preventing MCP client connections
- Console script entry point now works correctly when installed via pip
- Import issues resolved with dynamic code loading for package context

### Infrastructure
- Professional-grade repository organization following industry standards
- CI/CD ready structure with automated quality assurance
- Enhanced testing infrastructure with reliable runners
- Complete backward compatibility maintained

## [1.6.0] - 2025-06-06

### 🚀 Major Features
- **Automatic Database Migration System**: Complete automatic schema detection, migration execution, and rollback capabilities
  - AutoMigrationSystem with comprehensive safety mechanisms and backup creation
  - Schema comparison and migration complexity analysis
  - Migration history tracking and failure recovery
  - Server startup integration with conservative timeout settings
  - Comprehensive testing suite with 95/100 quality score
  
- **In-Context Server Reboot**: Production-ready server restart functionality with state preservation
  - Graceful shutdown coordination with task suspension and resource cleanup
  - Client connection preservation and request buffering during restart
  - Complete state serialization and restoration across reboots
  - MCP tools for restart operations: `orchestrator_restart_server`, `orchestrator_health_check`, `orchestrator_shutdown_prepare`
  - Comprehensive test coverage with 50+ test methods across all scenarios

### 🔧 Infrastructure  
- Enhanced testing infrastructure with file-based output system
- Improved error handling and recovery mechanisms
- Performance optimizations for large-scale operations
- Comprehensive documentation for operational procedures

### 📊 Quality & Testing
- Database migration system: 95% test success rate with production-ready deployment approval
- Server reboot system: Comprehensive test coverage ready for staging deployment
- Enhanced test runners preventing output truncation and hang detection
- Resource management validation preventing memory leaks

## [1.5.1] - 2025-06-06

### 🐛 Critical Bug Fixes
- **CRITICAL**: Fixed artifact path resolution issue where artifacts were written to MCP server directory instead of user's current working directory
  - Artifacts are now correctly stored in `.task_orchestrator/artifacts/` within the user's project directory
  - Restores accessibility to all generated artifacts for 100% of users
  - Enables proper artifact retrieval and prevents accumulation in wrong locations
  - **Impact**: This bug rendered the artifact system non-functional for practical use

### 🔧 Infrastructure
- Resolved version inconsistency between setup.py (1.5.0) and package __init__.py (1.4.0)
- Both version declarations now synchronized at 1.5.1

## [1.4.0] - 2025-05-30

> **Editor's Note**: Massive documentation reorganization and enhancement inspired by constructive feedback from KECG, who correctly identified the need for clearer input-to-output examples, human-authored documentation, and concrete use cases. Sometimes the harshest critics provide the most valuable direction.

### 🎉 Major Features
- **Claude Code MCP Integration**: Complete integration guides and coordination patterns
- **Visual Documentation System**: ASCII diagrams and flowcharts for universal compatibility  
- **Dual-Audience Architecture**: Parallel documentation for humans and LLM agents

### 📚 Documentation
- Complete documentation restructure with user-guide/ and llm-agents/ directories
- Character-optimized documentation for LLM tool compatibility (1200-2000 chars)
- Real-world examples across data processing, modernization, and enterprise coordination
- Comprehensive visual guides with setup flows and troubleshooting trees
- Master documentation index (INDEX.md) with multi-audience navigation
- Cross-referencing system linking all documentation components

### 🔗 Integration Patterns
- Sequential Coordination Pattern (core pattern for MCP integration)
- Parallel execution and graceful degradation strategies
- Multi-server coordination patterns
- Aggregator integration patterns

### ✨ Visual Assets
- Architecture overview diagrams with ASCII art
- Sequential coordination workflow flowcharts
- Setup and installation visual guides
- Troubleshooting decision trees
- Integration patterns visual documentation

## [1.3.3] - 2025-05-30

### 📚 Documentation
- Documentation architecture redesign and foundation restructure
- New dual-audience structure (user-guide/ + llm-agents/)
- Integration patterns documentation with real coordination examples
- Real-world examples and workflows across 5 major categories
- LLM agent workflow guides with character optimization
- Core sequential coordination pattern establishment

## [1.3.2] - 2025-05-30

### 🔧 Installation
- Installation script fixes and improvements
- Enhanced installation documentation and error handling
- Cross-documentation consistency verification
- Backward compatibility and migration notes
- Installation instructions testing and validation

## [1.3.1] - Previous Release

### Initial Features
- Core MCP task orchestration functionality
- Specialist role system
- Basic documentation framework
