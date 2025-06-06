# Changelog

All notable changes to the MCP Task Orchestrator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
