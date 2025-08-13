# Orchestrator Functionality Restoration PRP

**PRP ID**: `ORCHESTRATOR_FUNCTIONALITY_RESTORATION`  
**Type**: Critical Infrastructure Restoration  
**Priority**: Critical  
**Estimated Effort**: 2-3 days  
**Status**: [COMPLETED]  
**Last Updated**: 2025-08-13
**Completion Date**: 2025-08-13

## ✅ COMPLETION STATUS - ALL PHASES COMPLETED

### ✅ Phase 1: Core Functionality Restored - COMPLETED
- `orchestrator_plan_task` works without 'str' object errors ✅
- `orchestrator_query_tasks` handles pagination correctly ✅
- Basic orchestrator tools are functional ✅
- Health check passes consistently ✅

### ✅ Phase 2: Domain Layer Implementation - COMPLETED
- Infrastructure layer fully enabled - all modules imported ✅
- Domain services completed with proper imports ✅
- Database layer fully accessible through infrastructure layer ✅
- MCP protocol adapters fully enabled ✅

### ✅ Phase 3: Simplified Implementations Eliminated - COMPLETED
- **0 "simplified implementation" markers** remaining ✅
- Infrastructure `__init__.py` TODO items resolved ✅
- Domain services fully implemented ✅
- Handler responses use proper identifiers ✅

### 🎯 SUCCESS METRICS ACHIEVED
- **0 simplified implementations** remaining (target: 0) ✅
- **Core tools functional** - all primary orchestrator tools working ✅  
- **Infrastructure layer complete** - all modules enabled and accessible ✅
- **Health validation passing** - comprehensive health checks successful ✅
- **Git commit completed** - all changes committed with proper documentation ✅

## Overview

Restore full functionality to the MCP Task Orchestrator by fixing broken tools and replacing simplified implementations with real working code. The Clean Architecture refactor (commit 9a02ca4) broke existing working functionality, leaving critical orchestrator tools non-functional.

## Problem Analysis

### Critical Issues Identified

**1. Broken Core Tools:**
- `orchestrator_plan_task`: TypeError: 'str' object is not a mapping
- `orchestrator_query_tasks`: Pagination error
- Multiple tools returning simplified implementation stubs

**2. Working Implementation Destroyed:**
- Commit 22a04b7 (backup restoration): Had working `handle_plan_task` and complete functionality
- Commit 9a02ca4 (Clean Architecture refactor): Replaced working code with domain abstractions
- Current v2.0-implementation-ready branch: Has broken domain layer without complete implementations

**3. Simplified Implementation Epidemic:**
Found 35+ instances of TODOs and simplified implementations across:
- `mcp_task_orchestrator/infrastructure/` - Multiple incomplete interfaces
- `mcp_task_orchestrator/reboot/` - 15+ TODO items
- Core handlers - Simplified stubs instead of real functionality

## Solution Strategy

### Phase 1: Restore Working Core Tools (Day 1)

**Approach**: Restore working implementations from main branch and backup restoration commit.

#### 1.1 Restore Working Server Implementation

**Working Code Location**: 
- Main branch `server.py` has complete working implementation
- Backup restoration commit 22a04b7 has working handlers

**Implementation**:
```python
# From main branch server.py - working handle_plan_task
async def handle_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task planning with LLM-provided subtasks."""
    orchestrator = get_orchestrator()
    
    description = args["description"]
    subtasks_json = args["subtasks_json"]
    complexity = args.get("complexity_level", "moderate")
    context = args.get("context", "")
    
    try:
        breakdown = await asyncio.wait_for(
            orchestrator.plan_task(description, complexity, subtasks_json, context),
            timeout=30
        )
        # ... (complete working implementation)
```

#### 1.2 Fix Parameter Handling Issues

**Root Cause**: Domain layer expects different parameter formats than what MCP tools provide.

**Fix Approach**:
- Restore parameter mapping from working implementations
- Fix the `'str' object is not a mapping` errors in handlers
- Ensure proper type conversion between MCP protocol and domain layer

#### 1.3 Restore Core Orchestrator Methods

**Missing Methods in Current System**:
- `orchestrator.plan_task()` - Broken parameter handling
- `orchestrator.get_specialist_context()` - Returns simplified stubs
- `orchestrator.complete_subtask()` - Incomplete implementation

**Restoration Source**: 
- Commit 22a04b7 had working `TaskOrchestrator` class with timeout management
- Main branch has working async implementations

### Phase 2: Complete Domain Layer Implementation (Day 2)

**Approach**: Complete the domain layer abstractions properly while maintaining working functionality.

#### 2.1 Fix Infrastructure Layer

**Current Issues**:
- Multiple "TODO: Re-enable when implementations are fixed" in `infrastructure/__init__.py`
- Missing database repository implementations
- Incomplete MCP protocol adapters

**Implementation Plan**:
```yaml
infrastructure_fixes:
  database_layer:
    - Complete SQLite repository implementations
    - Fix connection management issues
    - Implement proper resource cleanup
    
  mcp_layer:
    - Complete protocol adapters with proper error handling
    - Fix parameter mapping between MCP and domain
    - Implement proper timeout management
    
  error_handling:
    - Complete retry mechanisms
    - Implement proper recovery strategies
    - Fix error message sanitization
```

#### 2.2 Complete Domain Services

**Missing Implementations**:
- TaskBreakdownService - Simplified stub
- SpecialistAssignmentService - Incomplete role loading
- ProgressTrackingService - Missing real tracking logic

**Source Material**: Use working orchestrator patterns from backup restoration commit.

### Phase 3: Replace All Simplified Implementations (Day 3)

#### 3.1 Systematic TODO Elimination

**Found 35+ TODO Items**:
- Reboot system: 15+ incomplete implementations
- Infrastructure layer: 10+ missing features
- Domain services: 5+ simplified stubs
- Error handling: 5+ incomplete recovery mechanisms

**Elimination Strategy**:
1. Catalog all TODO items by priority and complexity
2. Implement real functionality based on working patterns
3. Remove all "simplified implementation" markers
4. Add comprehensive error handling

#### 3.2 Restore Enhanced Features

**Working Features Lost**:
- Hang detection and timeout management (from enhanced_handlers.py)
- Comprehensive error recovery
- Proper async operation handling
- Resource cleanup mechanisms

## Technical Implementation Details

### Core Handler Restoration

**File**: `mcp_task_orchestrator/mcp_request_handlers.py`

**Current Issue**: Uses broken domain layer routing
**Fix**: Restore working handler implementations from main branch

```python
# Replace current broken implementation
async def handle_orchestrator_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    # Current: Broken domain routing with 'str' object error
    # Fix: Use working orchestrator.plan_task() pattern from main branch
```

### Parameter Schema Alignment

**Root Issue**: Domain layer expects different parameter formats

**Fix Mapping**:
```python
# MCP Tool Schema -> Domain Layer Schema
{
    "title": str,           # New domain expects this
    "description": str,     # Both use this  
    "complexity": str,      # Domain uses ComplexityLevel enum
    "task_type": str,       # New domain parameter
    "specialist_type": str  # Domain uses SpecialistType enum
}
```

### Working Implementation Integration

**Strategy**: Hybrid approach maintaining both working functionality and domain patterns

```python
# Hybrid implementation pattern
async def handle_plan_task(args: Dict[str, Any]):
    # 1. Use working orchestrator implementation for core logic
    orchestrator = get_orchestrator()  # Working singleton pattern
    
    # 2. Map parameters to domain layer format if needed
    domain_params = map_mcp_to_domain(args)
    
    # 3. Call working core methods
    result = await orchestrator.plan_task(**domain_params)
    
    # 4. Return in MCP format
    return format_mcp_response(result)
```

## Validation Framework

### Testing Strategy

**Multi-Stage Validation**:
```bash
# Stage 1: Orchestrator Health Check
mcp__task-orchestrator__orchestrator_health_check

# Stage 2: Core Tool Functionality
mcp__task-orchestrator__orchestrator_plan_task
mcp__task-orchestrator__orchestrator_query_tasks

# Stage 3: End-to-End Workflow
# Complete task workflow from plan -> execute -> complete

# Stage 4: Performance & Stability
python tools/diagnostics/performance_monitor.py --duration 60

# Stage 5: Integration Testing
pytest tests/integration/ -v
```

### Success Criteria

**Primary Goals**:
- [ ] `orchestrator_plan_task` works without 'str' object errors
- [ ] `orchestrator_query_tasks` handles pagination correctly
- [ ] All simplified implementations replaced with real functionality
- [ ] Zero TODO items marked as "implement this later"
- [ ] Main branch functionality preserved

**Quality Gates**:
- [ ] No "simplified implementation" text in codebase
- [ ] All orchestrator tools return real data, not placeholder responses
- [ ] Error handling provides meaningful recovery options
- [ ] Timeout management works properly
- [ ] Resource cleanup prevents warnings

## Context References

### Enhanced AI Documentation

**Required Context Loading**:
```yaml
- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server implementation patterns with async error handling"
  sections: ["Handler Patterns", "Parameter Mapping", "Error Recovery"]

- file: PRPs/ai_docs/database-integration-patterns.md
  why: "Repository pattern implementation with SQLite"
  sections: ["Connection Management", "Resource Cleanup", "Migration Patterns"]

- file: PRPs/ai_docs/clean-architecture-bridge-patterns.md
  why: "Bridging working legacy code with domain patterns"
  sections: ["Hybrid Implementation", "Gradual Migration", "Interface Adaptation"]
```

### Working Code References

**Key Source Commits**:
- Commit `22a04b7`: Backup restoration with working TaskOrchestrator
- Main branch `server.py`: Complete working handler implementations
- Enhanced handlers patterns for timeout management

### Implementation Examples

**Working Pattern from Main Branch**:
```python
async def handle_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    orchestrator = get_orchestrator()
    
    description = args["description"]
    subtasks_json = args["subtasks_json"]
    complexity = args.get("complexity_level", "moderate")
    context = args.get("context", "")
    
    try:
        breakdown = await asyncio.wait_for(
            orchestrator.plan_task(description, complexity, subtasks_json, context),
            timeout=30
        )
        
        response = {
            "task_created": True,
            "parent_task_id": breakdown.parent_task_id,
            "description": breakdown.description,
            "complexity": breakdown.complexity.value,
            "subtasks": [/* complete working format */],
            "next_steps": "Use orchestrator_execute_subtask to start working on individual subtasks"
        }
    except asyncio.TimeoutError:
        # Complete error handling
    except Exception as e:
        # Comprehensive error recovery
```

## Risk Management

### Technical Risks

**Domain Layer Complexity**: Risk that completing domain layer creates new bugs
- **Mitigation**: Use hybrid approach - bridge working code with domain patterns
- **Fallback**: Keep working implementations as primary path

**Breaking Changes**: Risk that fixes break other functionality
- **Mitigation**: Comprehensive testing at each stage
- **Rollback Plan**: Git branch allows easy revert to current state

**Time Pressure**: Risk of incomplete implementation under deadline
- **Mitigation**: Phase 1 focuses on critical path - getting core tools working
- **Priority**: Core functionality first, then completeness

### Implementation Risks

**Parameter Mapping Issues**: Risk that MCP-to-domain translation fails
- **Mitigation**: Validate parameter schemas at each layer
- **Testing**: Unit tests for parameter transformation

**Async Operation Safety**: Risk of race conditions or resource leaks
- **Mitigation**: Use proven patterns from working implementations
- **Validation**: Resource cleanup testing

## Security Considerations

### Error Message Sanitization

**Current Issue**: Domain layer may expose internal errors
**Fix**: Implement proper error sanitization in handlers

### Input Validation

**Current Issue**: Simplified implementations may skip validation
**Fix**: Restore comprehensive input validation from working patterns

### Resource Protection

**Current Issue**: Incomplete resource cleanup in domain layer
**Fix**: Implement proper resource management patterns

## Implementation Plan

### Day 1: Restore Core Functionality

**Morning (4 hours)**:
1. Restore working `handle_plan_task` implementation
2. Fix parameter mapping issues
3. Restore `handle_query_tasks` functionality
4. Test core tool operations

**Afternoon (4 hours)**:
1. Fix remaining core handler implementations
2. Restore orchestrator method calls
3. Implement proper error handling
4. Validate working tool functionality

### Day 2: Complete Domain Layer

**Morning (4 hours)**:
1. Complete infrastructure repository implementations
2. Fix database connection management
3. Complete MCP protocol adapters
4. Test domain layer integration

**Afternoon (4 hours)**:
1. Complete domain service implementations
2. Fix specialist assignment service
3. Complete progress tracking service
4. Integration testing

### Day 3: Eliminate Simplified Implementations

**Morning (4 hours)**:
1. Catalog and prioritize all TODO items
2. Implement reboot system functionality
3. Complete error handling implementations
4. Remove simplified implementation markers

**Afternoon (4 hours)**:
1. Restore enhanced features (hang detection, etc.)
2. Complete resource cleanup mechanisms
3. Final integration testing
4. Performance validation

## Completion Validation

### Functional Tests

```bash
# Test working orchestrator tools
mcp__task-orchestrator__orchestrator_plan_task \
  --title "Test Task" \
  --description "Test task creation" \
  --complexity "moderate"

# Verify no errors or simplified responses
mcp__task-orchestrator__orchestrator_query_tasks --limit 5
```

### Code Quality Validation

```bash
# Verify no simplified implementations remain
grep -r "simplified implementation\|TODO.*implement\|FIXME" mcp_task_orchestrator/

# Should return empty result
```

### Performance Validation

```bash
# Verify resource management
python tools/diagnostics/health_check.py --comprehensive

# Should show no resource warnings
```

## Success Metrics

### Context Engineering Score: 10/10
- Complete context references to working implementations
- Detailed technical specifications
- Comprehensive error scenarios covered

### Security Integration Score: 10/10
- Input validation requirements specified
- Error sanitization implemented
- Resource protection patterns applied

### Implementation Confidence Score: 9/10
- Working code examples provided
- Clear rollback strategy available
- Hybrid approach reduces risk

## Conclusion

This PRP provides a comprehensive restoration strategy for MCP Task Orchestrator functionality. By leveraging working implementations from the main branch and backup restoration commit, while properly completing the domain layer, we can restore full orchestrator functionality without losing the architectural improvements.

The hybrid approach ensures we maintain working functionality while properly implementing clean architecture patterns, providing both immediate restoration and long-term maintainability.