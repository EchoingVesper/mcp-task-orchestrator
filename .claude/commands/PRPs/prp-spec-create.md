# Create SPEC PRP with Context Engineering

Generate a comprehensive specification-driven PRP with clear transformation goals using enhanced
context engineering principles and security-first design.

## Specification: $ARGUMENTS

## Pre-Execution Orchestrator Check

**MANDATORY FIRST STEP:**

```bash
# Verify orchestrator connection
claude mcp list | grep task-orchestrator || (echo "ORCHESTRATOR NOT CONNECTED - Fixing..." && claude mcp restart task-orchestrator)

# Initialize orchestrator session for specification PRP development
# Use orchestrator_initialize_session with working_directory
```

If orchestrator fails, STOP and spawn fix agent per CLAUDE.md protocol.

## Enhanced Context References

**CRITICAL**: Load and reference these enhanced AI documentation files:

```yaml
required_context:
  - file: PRPs/ai_docs/context-engineering-guide.md
    why: "Systematic context engineering for specification-driven development"
    sections: ["Context Engineering Framework", "Specification Patterns"]

  - file: PRPs/ai_docs/mcp-protocol-patterns.md
    why: "MCP server implementation patterns for specification compliance"
    sections: ["Core Principles", "State Management"]

  - file: PRPs/ai_docs/systematic-testing-framework.md
    why: "Testing framework for specification validation"
    sections: ["Specification Testing", "Validation Patterns"]

  - file: PRPs/ai_docs/security-patterns.md
    why: "Security-first design for specification changes"
    sections: ["Secure Refactoring", "State Security"]

  - file: CLAUDE.md
    why: "Project-specific architecture and specification constraints"
    sections: ["Clean Architecture", "Architecture Layers"]
```

## Security Considerations

All specification PRPs must include:
- **Security impact assessment** of proposed changes
- **Data flow security** validation
- **State transition security** analysis
- **Backward compatibility** security implications
- **Migration security** considerations

## Enhanced Analysis Process with Orchestrator Integration

**Use Orchestrator for Specification Analysis:**

```yaml
orchestrator_tasks:
  - orchestrator_plan_task: "Current state mapping and technical debt analysis for {specification}"
  - orchestrator_plan_task: "Desired state research with security implications" 
  - orchestrator_plan_task: "Migration strategy and risk assessment"
  - orchestrator_plan_task: "Integration point analysis and compatibility"
  - orchestrator_get_status: Track all analysis progress
```

1. **Enhanced Current State Assessment**
   - **Deep codebase analysis**: Use orchestrator_execute_task for parallel analysis
   - Map existing implementation with security considerations
   - Identify pain points and security vulnerabilities
   - Document technical debt and security debt
   - Note integration points and their security implications
   - **Context Engineering**: Reference similar patterns in ai_docs/

2. **Desired State Research with Security Focus**
   - **Use orchestrator_execute_task** for comprehensive research:
     - Best practices for target state with security patterns
     - Implementation examples from enhanced documentation
     - Migration strategies with security checkpoints
     - Risk assessment including security risks
     - Dependency mapping with security implications
   - **Security Validation**: Threat model changes

3. **User Clarification & Security Validation**
   - Confirm transformation goals and security requirements
   - Priority of objectives including security priorities
   - Acceptable trade-offs with security implications
   - **Security Review**: Validate security assumptions

## PRP Generation

Using /PRPs/templates/prp_spec.md:

### State Documentation

```yaml
current_state:
  files: [list affected files]
  behavior: [how it works now]
  issues: [specific problems]

desired_state:
  files: [expected structure]
  behavior: [target functionality]
  benefits: [improvements gained]
```

### Hierarchical Objectives

1. **High-Level**: Overall transformation goal
2. **Mid-Level**: Major milestones
3. **Low-Level**: Specific tasks with validation

### Task Specification with information dense keywords

#### Information dense keywords:

- MIRROR: Mirror the state of existing code to be mirrored to another use case
- COPY: Copy the state of existing code to be copied to another use case
- ADD: Add new code to the codebase
- MODIFY: Modify existing code
- DELETE: Delete existing code
- RENAME: Rename existing code
- MOVE: Move existing code
- REPLACE: Replace existing code
- CREATE: Create new code

#### Example:

```yaml
task_name:
  action: MODIFY/CREATE
  file: path/to/file
  changes: |
    - Specific modifications
    - Implementation details
    - With clear markers
  validation:
    - command: "test command"
    - expect: "success criteria"
```

### Implementation Strategy

- Identify dependencies
- Order tasks by priority and implementation order and dependencies logic
- Include rollback plans
- Progressive enhancement

## User Interaction Points

1. **Objective Validation**
   - Review hierarchical breakdown
   - Confirm priorities
   - Identify missing pieces

2. **Risk Review**
   - Document identified risks
   - Find mitigations
   - Set go/no-go criteria

## Context Requirements

- Current implementation details
- Target architecture examples
- Migration best practices
- Testing strategies

## Output

Save as: `SPEC_PRP/PRPs/{spec-name}.md`

## Enhanced Multi-Stage Validation

### Stage 1: Specification & Design Validation
```bash
# Validate specification structure and completeness
python scripts/validate_spec_structure.py PRPs/{spec-name}.md

# Security impact assessment
python scripts/security_impact_analysis.py PRPs/{spec-name}.md

# Architecture compliance check
python scripts/validate_architecture_compliance.py PRPs/{spec-name}.md
```

### Stage 2: Context Engineering Validation
```bash
# Verify context engineering integration
python scripts/validate_context_engineering.py PRPs/{spec-name}.md

# Check enhanced documentation references
grep -r "PRPs/ai_docs/" PRPs/{spec-name}.md || echo "Missing enhanced context references"

# Orchestrator integration verification
grep -r "orchestrator_" PRPs/{spec-name}.md || echo "Missing orchestrator integration"
```

### Stage 3: Security & Migration Validation
```bash
# Migration security assessment
python scripts/validate_migration_security.py PRPs/{spec-name}.md

# State transition security validation
python scripts/validate_state_security.py PRPs/{spec-name}.md

# Backward compatibility security check
python scripts/validate_compatibility_security.py PRPs/{spec-name}.md
```

### Stage 4: Technical Feasibility & Dependencies
```bash
# Dependency chain validation
python scripts/validate_dependency_chain.py PRPs/{spec-name}.md

# Implementation order verification
python scripts/validate_implementation_order.py PRPs/{spec-name}.md

# Rollback strategy validation
python scripts/validate_rollback_strategy.py PRPs/{spec-name}.md
```

### Stage 5: Implementation Readiness
```bash
# Task specification completeness
python scripts/validate_task_specs.py PRPs/{spec-name}.md

# Validation command verification
python scripts/validate_test_commands.py PRPs/{spec-name}.md

# Integration point validation
python scripts/validate_integration_points.py PRPs/{spec-name}.md
```

## Enhanced Quality Checklist

### Core Specification Requirements
- [ ] Current state fully documented with security analysis
- [ ] Desired state clearly defined with security implications
- [ ] All objectives measurable with security KPIs
- [ ] Tasks ordered by dependency and security priority
- [ ] Each task has validation that AI can run
- [ ] Integration points noted with security implications

### Context Engineering Integration
- [ ] **Enhanced context references** included from PRPs/ai_docs/
- [ ] **Context engineering guide** principles applied
- [ ] **Systematic testing framework** referenced
- [ ] **Security patterns** applied to specification changes
- [ ] **Orchestrator integration** planned for complex transformations

### Security-First Specification
- [ ] **Security impact assessment** completed for all changes
- [ ] **Data flow security** validated for state transitions
- [ ] **Migration security** strategy defined
- [ ] **Backward compatibility security** implications addressed
- [ ] **State transition security** analysis completed

### Implementation Readiness
- [ ] Risks identified with mitigations including security risks
- [ ] Rollback strategy included with security considerations
- [ ] **All 5 validation stages** can be executed
- [ ] Transformation journey security-validated
- [ ] Ready for enhanced implementation with security focus

### Git Integration Requirements
- [ ] **COMMIT ENFORCEMENT**: Changes must be committed after completion
- [ ] **Status tracking**: Use orchestrator_get_status for progress
- [ ] **Failure protocol**: CLAUDE.md orchestrator protocol if issues arise

## Completion Protocol

**After completing the specification PRP:**
1. Run all 5 validation stages
2. **COMMIT CHANGES**: Always commit the completed specification
3. Use descriptive commit message following project conventions
4. **Context Engineering Score Target**: 9/10
5. **Security Integration Score Target**: 9/10

Remember: Focus on the secure transformation journey with enhanced context engineering, not just the destination.
