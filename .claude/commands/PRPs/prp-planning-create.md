# Create PLANNING PRP with Context Engineering

Transform rough ideas into comprehensive PRDs with rich visual documentation using enhanced context engineering principles and security-first design.

## Idea: $ARGUMENTS

## Pre-Execution Orchestrator Check

**MANDATORY FIRST STEP:**
```bash
# Verify orchestrator connection
claude mcp list | grep task-orchestrator || (echo "ORCHESTRATOR NOT CONNECTED - Fixing..." && claude mcp restart task-orchestrator)

# Initialize orchestrator session for planning PRP development
# Use orchestrator_initialize_session with working_directory
```

If orchestrator fails, STOP and spawn fix agent per CLAUDE.md protocol.

## Enhanced Context References

**CRITICAL**: Load and reference these enhanced AI documentation files:

```yaml
required_context:
  - file: PRPs/ai_docs/context-engineering-guide.md
    why: "Systematic context engineering principles for production-ready PRDs"
    sections: ["Context Engineering Framework", "Research Methodology"]

  - file: PRPs/ai_docs/mcp-protocol-patterns.md
    why: "MCP server implementation patterns for planning phase"
    sections: ["Core Principles", "Planning Integration"]

  - file: PRPs/ai_docs/security-patterns.md
    why: "Security-first design principles for feature planning"
    sections: ["Threat Modeling", "Security Requirements"]

  - file: CLAUDE.md
    why: "Project-specific guidance and architecture constraints"
    sections: ["Architecture Overview", "Clean Architecture"]
```

## Security Considerations

All planning PRDs must include:
- **Threat modeling** during design phase
- **Input validation** requirements specification
- **Authentication/authorization** integration points
- **Data privacy** and compliance considerations
- **Error handling** that doesn't leak sensitive information

## Enhanced Discovery Process with Orchestrator Integration

**Use Orchestrator for Research Coordination:**
```yaml
orchestrator_tasks:
  - orchestrator_plan_task: "Concept expansion and goal mapping for {idea}"
  - orchestrator_plan_task: "Market analysis and competitor research" 
  - orchestrator_plan_task: "Technical feasibility and architecture analysis"
  - orchestrator_plan_task: "Security requirements and threat modeling"
  - orchestrator_get_status: Track all research progress
```

1. **Enhanced Concept Expansion**
   - Break down the core idea with context engineering principles
   - Define SMART success criteria
   - Map to business goals and user value
   - **Security**: Identify initial threat vectors
   - **Architecture**: Map to existing system components

2. **Market & Technical Research at Scale**
   - **Use orchestrator_execute_task** for parallel research:
     - Market analysis with security considerations
     - Competitor analysis including security practices
     - Technical feasibility with MCP integration patterns
     - Best practice examples from similar systems
     - Integration possibilities with existing architecture
   - **Context Engineering**: Reference enhanced documentation patterns

3. **User Research & Security Validation**
     - Ask user for comprehensive requirements:
     - Target user personas and security roles?
     - Key pain points and security concerns?
     - Success metrics including security KPIs?
     - Constraints/requirements including compliance needs?
     - **Threat Model**: What are the security assumptions?

## PRD Generation

Using /PRPs/templates/prp_planning_base.md:

### Visual Documentation Plan

```yaml
diagrams_needed:
  user_flows:
    - Happy path journey
    - Error scenarios
    - Edge cases
  
  architecture:
    - System components
    - Data flow
    - Integration points
  
  sequences:
    - API interactions
    - Event flows
    - State changes
  
  data_models:
    - Entity relationships
    - Schema design
    - State machines
```

### Research Integration

- **Market Analysis**: Include findings in PRD
- **Technical Options**: Compare approaches
- **Risk Assessment**: With mitigation strategies
- **Success Metrics**: Specific, measurable

### User Story Development

```markdown
## Epic: [High-level feature]

### Story 1: [User need]
**As a** [user type]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Specific behavior
- [ ] Edge case handling
- [ ] Performance requirement

**Technical Notes:**
- Implementation approach
- API implications
- Data requirements
```

### Implementation Strategy

- Phases with dependencies (no dates)
- Priority ordering
- MVP vs enhanced features
- Technical prerequisites

## User Interaction Points

1. **Idea Validation**
   - Confirm understanding
   - Clarify ambiguities
   - Set boundaries

2. **Research Review**
   - Share findings
   - Validate assumptions
   - Adjust direction

3. **PRD Draft Review**
   - Architecture approval
   - Risk acknowledgment
   - Success metric agreement

## Diagram Guidelines

- Use Mermaid for all diagrams
- Include legends where needed
- Show error paths
- Annotate complex flows

## Output Structure

```markdown
1. Executive Summary
2. Problem & Solution
3. User Stories (with diagrams)
4. Technical Architecture (with diagrams)
5. API Specifications
6. Data Models
7. Implementation Phases
8. Risks & Mitigations
9. Success Metrics
10. Appendices
```

Save as: `PRPs/{feature-name}-prd.md`

## Enhanced Multi-Stage Validation

### Stage 1: Planning & Design Validation
```bash
# Validate PRD structure and completeness
python scripts/validate_prd_structure.py PRPs/{feature-name}-prd.md

# Security design review
python scripts/security_design_review.py PRPs/{feature-name}-prd.md

# Architecture alignment check
python scripts/validate_architecture_alignment.py PRPs/{feature-name}-prd.md
```

### Stage 2: Context Engineering Validation
```bash
# Verify context engineering integration
python scripts/validate_context_engineering.py PRPs/{feature-name}-prd.md

# Check enhanced documentation references
grep -r "PRPs/ai_docs/" PRPs/{feature-name}-prd.md || echo "Missing enhanced context references"

# Orchestrator integration verification
grep -r "orchestrator_" PRPs/{feature-name}-prd.md || echo "Missing orchestrator integration"
```

### Stage 3: Security & Compliance Validation
```bash
# Threat model completeness check
python scripts/validate_threat_model.py PRPs/{feature-name}-prd.md

# Compliance requirements verification
python scripts/validate_compliance.py PRPs/{feature-name}-prd.md

# Input validation requirements check
python scripts/validate_input_requirements.py PRPs/{feature-name}-prd.md
```

### Stage 4: Technical Feasibility Validation
```bash
# Architecture compatibility check
python scripts/validate_technical_feasibility.py PRPs/{feature-name}-prd.md

# MCP integration patterns verification
python scripts/validate_mcp_patterns.py PRPs/{feature-name}-prd.md

# Database schema validation
python scripts/validate_data_models.py PRPs/{feature-name}-prd.md
```

### Stage 5: Implementation Readiness
```bash
# User story completeness
python scripts/validate_user_stories.py PRPs/{feature-name}-prd.md

# API specification validation
python scripts/validate_api_specs.py PRPs/{feature-name}-prd.md

# Success metrics verification
python scripts/validate_success_metrics.py PRPs/{feature-name}-prd.md
```

## Enhanced Quality Checklist

### Core Planning Requirements

- [ ] Problem clearly articulated with user impact
- [ ] Solution addresses problem with measurable value
- [ ] All user flows diagrammed with error paths
- [ ] Wireframes included if needed
- [ ] Architecture visualized with component relationships
- [ ] APIs fully specified with examples and error codes
- [ ] Data models included with validation rules
- [ ] Dependencies identified with mitigation strategies

### Context Engineering Integration

- [ ] **Enhanced context references** included from PRPs/ai_docs/
- [ ] **Context engineering guide** principles applied
- [ ] **MCP protocol patterns** referenced appropriately
- [ ] **Orchestrator integration** planned for complex tasks
- [ ] **Multi-stage validation** framework defined

### Security-First Design

- [ ] **Threat model** completed with attack vectors
- [ ] **Security requirements** specified for each component
- [ ] **Input validation** requirements documented
- [ ] **Authentication/authorization** integration points defined
- [ ] **Error handling** that doesn't leak sensitive information
- [ ] **Data privacy** and compliance considerations addressed

### Implementation Readiness

- [ ] Success metrics measurable with security KPIs
- [ ] Implementation phases logical with security checkpoints
- [ ] Technical prerequisites identified including security tools
- [ ] **All 5 validation stages** can be executed
- [ ] Ready for enhanced implementation PRP with security focus

### Git Integration Requirements

- [ ] **COMMIT ENFORCEMENT**: Changes must be committed after completion
- [ ] **Status tracking**: Use orchestrator_get_status for progress
- [ ] **Failure protocol**: CLAUDE.md orchestrator protocol if issues arise

## Completion Protocol

**After completing the PRP:**
1. Run all 5 validation stages
2. **COMMIT CHANGES**: Always commit the completed PRD
3. Use descriptive commit message following project conventions
4. **Context Engineering Score Target**: 9/10
5. **Security Integration Score Target**: 9/10

Remember: Enhanced PRDs with context engineering and security-first design prevent implementation
confusion and security vulnerabilities.
