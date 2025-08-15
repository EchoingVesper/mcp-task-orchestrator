

# 🔧 Feature Specification: Modular Repository Architecture

**Feature ID**: `MODULAR_REPOSITORY_ARCH`  
**Priority**: High  
**Category**: Core Infrastructure  
**Estimated Effort**: 1-2 weeks  
**Created**: 2025-01-06  
**Status**: Proposed  

#

# 📋 Overview

Split the large 1,180-line generic repository into focused, modular components to prevent Claude Code memory crashes and improve maintainability. This addresses the JavaScript heap memory exhaustion that occurred during repository pattern development.

#

# 🎯 Objectives

1. **Memory Optimization**: Reduce individual file sizes to prevent Claude Code heap overflow

2. **Maintainability**: Create focused modules with single responsibilities  

3. **Developer Experience**: Enable targeted edits without loading massive context

4. **Code Organization**: Establish clear separation of concerns in repository layer

5. **Performance**: Improve loading times and reduce memory footprint

#

# 🛠️ Proposed Implementation

#

#

# New Module Structure

```text
mcp_task_orchestrator/db/
├── repositories/
│   ├── __init__.py              

# Repository factory and exports

│   ├── base_repository.py       

# Abstract base class (~200 lines)

│   ├── crud_operations.py       

# Task CRUD operations (~300 lines)

│   ├── hierarchy_manager.py     

# Hierarchy operations (~250 lines)

│   ├── dependency_manager.py    

# Dependency operations (~200 lines)

│   ├── query_builder.py         

# Search and query operations (~200 lines)

│   └── template_manager.py      

# Template operations (~150 lines)

├── generic_repository.py        

# Legacy compatibility wrapper

└── generic_task_migration.py    

# Migration scripts

```text

#

#

# Database Changes

- No schema changes required

- Maintain backward compatibility through wrapper class

- Repository factory pattern for dependency injection

#

#

# Integration Points

- Drop-in replacement for existing `GenericTaskRepository`

- Maintains same async interface and error handling

- Compatible with existing orchestrator components

#

# 🔄 Implementation Approach

#

#

# Phase 1: Module Extraction (Week 1)

- Create base repository with common patterns

- Extract CRUD operations module

- Extract hierarchy management module

- Extract dependency management module

#

#

# Phase 2: Refinement & Testing (Week 2)

- Extract query operations module

- Extract template management module

- Create repository factory

- Comprehensive testing and validation

#

# 📊 Benefits

#

#

# Immediate Benefits

- **Memory Safety**: Prevent Claude Code crashes from large files

- **Focused Development**: Work on specific repository concerns in isolation

- **Reduced Context**: Each module ~150-300 lines vs 1,180 lines

- **Faster Loading**: Targeted imports reduce memory usage

#

#

# Long-term Benefits

- **Easier Maintenance**: Modular updates without affecting entire repository

- **Team Development**: Multiple developers can work on different modules

- **Testing Isolation**: Unit test specific concerns independently

- **Code Reuse**: Individual modules can be reused in other contexts

#

# 🔍 Success Metrics

- **File Size Reduction**: No individual module exceeds 300 lines

- **Memory Usage**: Claude Code successfully processes all modules without crashes

- **API Compatibility**: 100% backward compatibility with existing code

- **Test Coverage**: Maintain existing test coverage across all modules

- **Performance**: No degradation in database operation performance

#

# 🎯 Migration Strategy

#

#

# Backward Compatibility Approach

1. Keep original `generic_repository.py` as compatibility wrapper

2. Implement modular architecture in `repositories/` directory  

3. Gradual migration of consumers to new modular imports

4. Deprecation notice in original file with migration guidance

#

#

# Migration Steps

```text
python

# Old usage (still supported)

from mcp_task_orchestrator.db.generic_repository import GenericTaskRepository

# New modular usage (recommended)

from mcp_task_orchestrator.db.repositories import RepositoryFactory
repository = RepositoryFactory.create_generic_repository(db_url)
```text

#

# 📝 Additional Considerations

#

#

# Risks and Mitigation

- **Risk**: Breaking existing imports
  - **Mitigation**: Maintain wrapper class for backward compatibility

- **Risk**: Performance overhead from module splits
  - **Mitigation**: Optimize imports and use lazy loading where appropriate

- **Risk**: Increased complexity
  - **Mitigation**: Clear documentation and factory pattern for simple usage

#

#

# Dependencies

- Existing database models and schema

- Current async session management patterns

- SQLAlchemy async infrastructure

- Existing test infrastructure

#

#

# Technical Implementation Details

#

#

#
# Memory Impact Analysis

- **Current**: Single 1,180-line file (~48KB, ~2.3MB context load)

- **Target**: 6 modules of 150-300 lines each (~8KB per module)

- **Benefit**: ~70% reduction in per-module context load

#

#

#
# Module Responsibilities

- **BaseRepository**: Common patterns, session management, error handling

- **CrudOperations**: Create, read, update, delete operations

- **HierarchyManager**: Parent/child relationships, tree operations

- **DependencyManager**: Task dependencies, cycle detection

- **QueryBuilder**: Search, filtering, complex queries

- **TemplateManager**: Template CRUD and instantiation

---

**Next Steps**: 

1. Create module structure and base repository class

2. Extract CRUD operations to dedicated module

3. Test backward compatibility with existing code

4. Document migration path for future development

**Related Features/Tasks**:

- Generic Task Implementation Roadmap

- Database persistence layer enhancements

- Memory optimization initiatives
