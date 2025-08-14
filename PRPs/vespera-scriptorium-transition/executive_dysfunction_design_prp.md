# Meta-PRP: Universal Accessibility Design Philosophy Integration

## Meta-PRP Concept: UNIVERSAL_ACCESSIBILITY_DESIGN_PHILOSOPHY

Systematically integrate universal accessibility design principles throughout Vespera Scriptorium's architecture, documentation, and user experience, creating tools that work effectively across a wide range of cognitive styles and energy levels, with particular attention to reducing barriers during challenging periods.

**Legal Note**: This PRP focuses on design philosophy and user experience considerations. It does not make medical claims or constitute advice for any health conditions.

## Pre-Execution Orchestrator Health Check

**MANDATORY FIRST STEP:**

```bash
# Verify orchestrator connection and full functionality
claude mcp list | grep task-orchestrator || (echo "ORCHESTRATOR NOT CONNECTED - Fixing..." && claude mcp restart task-orchestrator)

# Test orchestrator health before meta-coordination
# This is critical for multi-agent workflows
```

If orchestrator fails, STOP and spawn fix agent per CLAUDE.md protocol.

## Enhanced Context References

**CRITICAL**: Load and reference these enhanced AI documentation files:

```yaml
required_context:
  - file: docs/philosophy/Executive-Dysfunction-Pressure-Lid-Metaphor-Extended.md
    why: "Core design philosophy and theoretical foundation"
    sections: ["Pressure-Lid Mechanics", "Vents and Bandwidth Theory", "Design Implications"]

  - file: PRPs/ai_docs/context-engineering-guide.md
    why: "Context engineering for accessibility-focused design"
    sections: ["Cognitive Load Patterns", "User Experience Design"]

  - file: PRPs/ai_docs/systematic-testing-framework.md
    why: "Testing accessibility and executive function support"
    sections: ["User Experience Testing", "Cognitive Load Validation"]

  - file: CLAUDE.md
    why: "Project-specific integration requirements"
    sections: ["Clean Architecture", "User Experience Guidelines"]

  - file: docs/architecture/clean-architecture-guide.md
    why: "Understanding current architecture for philosophy integration"
    sections: ["Domain Layer", "Application Layer", "User Interface Patterns"]
```

## Meta-PRP Design Principles

**Key Integration Targets:**
- **Documentation Strategy**: Momentum preservation across cognitive interruptions (sleep, illness, overwhelm)
- **User Interface Design**: Ultra-low cognitive load interfaces for "barely functional" days
- **Agent Coordination**: Pressure delegation when personal capacity is compromised
- **Session Management**: Damage prevention and recovery for cognitive accessibility
- **Template Systems**: Pre-reduced complexity for low-energy engagement
- **Error Handling**: Graceful degradation that preserves dignity and progress
- **Assistive Features**: Explicit support for migraine days, brain fog, chronic conditions

## Enhanced Discovery Process with Multi-Agent Coordination

**Use Orchestrator for Meta-Coordination:**

```yaml
orchestrator_meta_session:
  session_name: "executive-dysfunction-philosophy-integration"
  working_directory: "/vespera-scriptorium"
  expected_duration: "5-7 days"
  
orchestrator_meta_task:
  title: "Meta-PRP: Executive Dysfunction Design Philosophy Integration"
  description: "Systematically integrate pressure-lid design philosophy throughout platform"
  complexity: "very_complex"
  task_type: "architecture_philosophy"
  specialist_type: "accessibility_architect"
  
sub_task_coordination:
  - orchestrator_plan_task: "Philosophy documentation and guidelines creation"
  - orchestrator_plan_task: "Architecture pattern identification and integration"
  - orchestrator_plan_task: "User experience audit and redesign coordination"
  - orchestrator_plan_task: "Developer guidelines and template creation"
  - orchestrator_plan_task: "Testing framework for executive function support"
```

### Phase Structure with Sub-Agent Coordination

```yaml
phase_structure:
  phase_1_philosophy_documentation:
    duration: "1-2 days"
    orchestrator_session: "Philosophy Documentation Coordination"
    sub_agents:
      - philosophy_writer: "specialist_type: documenter"
      - accessibility_researcher: "specialist_type: researcher" 
      - user_experience_analyst: "specialist_type: reviewer"
    deliverables: 
      - "Extended pressure-lid metaphor with vents theory"
      - "Design philosophy integration guidelines"
      - "Accessibility principles documentation"
    
  phase_2_architecture_integration:
    duration: "2-3 days"
    orchestrator_session: "Architecture Integration Coordination"
    sub_agents:
      - architecture_analyst: "specialist_type: architect"
      - pattern_identifier: "specialist_type: coder"
      - integration_specialist: "specialist_type: architect"
    deliverables:
      - "Architecture patterns audit with executive dysfunction lens"
      - "Clean Architecture integration points for accessibility"
      - "Code patterns and conventions for lid weight reduction"
      
  phase_3_user_experience_audit:
    duration: "1-2 days"
    orchestrator_session: "User Experience Coordination"
    sub_agents:
      - ux_auditor: "specialist_type: reviewer"
      - friction_analyst: "specialist_type: tester"
      - workflow_optimizer: "specialist_type: coder"
    deliverables:
      - "Current UX audit through pressure-lid lens"
      - "Friction point identification and remediation plan"
      - "Workflow optimization recommendations"
      
  phase_4_developer_guidelines:
    duration: "1 day"
    orchestrator_session: "Developer Guidelines Coordination"
    sub_agents:
      - guideline_writer: "specialist_type: documenter"
      - template_creator: "specialist_type: coder"
      - example_generator: "specialist_type: coder"
    deliverables:
      - "Developer guidelines for executive dysfunction-aware design"
      - "Code review checklist with accessibility considerations"
      - "Template examples demonstrating philosophy integration"
      
  phase_5_validation_framework:
    duration: "1 day"
    orchestrator_session: "Validation Framework Coordination"
    sub_agents:
      - testing_strategist: "specialist_type: tester"
      - accessibility_validator: "specialist_type: reviewer"
      - metrics_designer: "specialist_type: analyst"
    deliverables:
      - "Testing framework for executive function support"
      - "Accessibility validation procedures"
      - "Success metrics and monitoring systems"
```

## Core Integration Areas

### 1. Documentation Strategy (Momentum Preservation)

**Problem**: Sleep resets close all lids - documentation must enable momentum preservation

**Integration Points:**
- Session state documentation that captures cognitive context
- Quick-start guides that minimize cognitive load on restart
- Progress tracking that maintains psychological momentum
- Context recovery systems for interrupted workflows

**Design Patterns:**
```yaml
documentation_patterns:
  quick_resume:
    purpose: "Minimize lid weight for continuation"
    requirements: ["Last state capture", "Next steps clarity", "Context preservation"]
    
  cognitive_breadcrumbs:
    purpose: "Reduce mental overhead for navigation"
    requirements: ["Clear hierarchy", "Progress indicators", "Return paths"]
    
  context_packaging:
    purpose: "Bundle related information to reduce switching costs"
    requirements: ["Coherent chunks", "Minimal dependencies", "Self-contained units"]
```

### 2. User Interface Design (Lid Weight Reduction)

**Problem**: Interface friction increases lid weights and causes task abandonment

**Integration Points:**
- Minimize clicks and navigation overhead
- Provide clear entry points for all major workflows
- Reduce cognitive load through intelligent defaults
- Enable graceful degradation when overwhelm occurs

**Design Patterns:**
```yaml
ui_patterns:
  friction_elimination:
    purpose: "Reduce lid weights for task initiation"
    requirements: ["One-click access", "Minimal configuration", "Intelligent defaults"]
    
  progressive_disclosure:
    purpose: "Prevent cognitive overwhelm"
    requirements: ["Layered complexity", "Optional details", "Core workflow clarity"]
    
  escape_hatches:
    purpose: "Prevent pressure damage when overwhelm occurs"
    requirements: ["Easy exits", "State preservation", "Graceful recovery"]
```

### 3. Agent Coordination (Pressure Delegation)

**Problem**: Task switching requires pressure redirection - agent spawning should reduce this cost

**Integration Points:**
- Agent spawning reduces switching overhead by maintaining context
- Specialist agents handle heavy lids that would overwhelm main context
- Context passing reduces re-explanation overhead
- Result synthesis minimizes manual aggregation work

**Design Patterns:**
```yaml
agent_patterns:
  pressure_offloading:
    purpose: "Delegate heavy lids to fresh contexts"
    requirements: ["Context packaging", "Specialist assignment", "Result integration"]
    
  momentum_preservation:
    purpose: "Maintain progress across agent switches"
    requirements: ["State tracking", "Artifact persistence", "Session continuity"]
    
  cognitive_load_distribution:
    purpose: "Spread complexity across multiple contexts"
    requirements: ["Task decomposition", "Clear boundaries", "Minimal coordination overhead"]
```

### 4. Session Management (Damage Prevention)

**Problem**: Frustration accumulation damages tasks - system should prevent and recover from this

**Integration Points:**
- Automatic session state preservation before overwhelm
- Recovery procedures that don't increase lid weights
- Graceful degradation that maintains partial progress
- Error handling that prevents frustration accumulation

**Design Patterns:**
```yaml
session_patterns:
  damage_prevention:
    purpose: "Prevent frustration from increasing lid weights"
    requirements: ["Early warning systems", "Automatic state preservation", "Graceful exits"]
    
  recovery_optimization:
    purpose: "Minimize lid weights for resumption"
    requirements: ["Context reconstruction", "Progress validation", "Clear next steps"]
    
  momentum_protection:
    purpose: "Preserve psychological momentum across interruptions"
    requirements: ["Achievement tracking", "Partial progress recognition", "Continuation cues"]
```

### 6. Low-Energy Mode Design (Accessibility Focus)

**Problem**: During periods of reduced cognitive capacity (fatigue, stress, health challenges), many productivity tools become difficult or impossible to use effectively

**Integration Points:**
- Simplified interfaces that work with minimal cognitive resources
- Reduced-input interaction modes (voice, gesture, or single-action workflows)
- Automatic context preservation when capacity changes suddenly
- Progress validation that recognizes partial efforts as meaningful achievements

**Design Patterns:**
```yaml
accessibility_patterns:
  low_energy_mode:
    purpose: "Enable meaningful engagement during challenging periods"
    requirements: ["Simplified workflows", "Minimal decisions", "Automatic saving", "Clear guidance"]
    
  cognitive_scaffolding:
    purpose: "Provide external structure to reduce mental overhead"
    requirements: ["Visual cues", "Predictable patterns", "Error tolerance", "Gentle feedback"]
    
  adaptive_complexity:
    purpose: "Automatically adjust interface complexity to user capacity"
    requirements: ["Load detection", "Progressive simplification", "Graceful degradation", "Easy recovery"]
```

**Problem**: Complex tasks have heavy lids - templates should reduce initial weights

**Integration Points:**
- Common workflows pre-packaged to reduce setup overhead
- Intelligent defaults that eliminate decision fatigue
- Progressive complexity that allows incremental engagement
- Customization that doesn't sacrifice simplicity

**Design Patterns:**
```yaml
template_patterns:
  complexity_reduction:
    purpose: "Pre-reduce lid weights for common tasks"
    requirements: ["Intelligent defaults", "Minimal configuration", "Clear starting points"]
    
  progressive_enhancement:
    purpose: "Allow complexity growth without overwhelming"
    requirements: ["Layered options", "Optional features", "Core workflow preservation"]
    
  cognitive_scaffolding:
    purpose: "Provide structure that reduces mental overhead"
    requirements: ["Clear patterns", "Consistent interfaces", "Predictable behaviors"]
```

## Success Criteria for Executive Dysfunction Integration

### Philosophy Documentation

- [ ] **Extended pressure-lid metaphor** documented with vents theory
- [ ] **Design philosophy guidelines** created for all development decisions
- [ ] **Accessibility principles** integrated into project documentation
- [ ] **User journey mapping** through executive dysfunction lens

### Architecture Integration

- [ ] **Clean Architecture layers** evaluated for lid weight impact
- [ ] **Code patterns identified** that reduce cognitive overhead
- [ ] **Integration points documented** for accessibility features
- [ ] **Refactoring roadmap** created for high-friction areas

### User Experience Audit

- [ ] **Current workflows audited** for executive dysfunction barriers
- [ ] **Friction points catalogued** with severity assessment
- [ ] **Optimization plan created** with priority ranking
- [ ] **Success metrics defined** for accessibility improvements

### Developer Guidelines

- [ ] **Coding standards updated** with executive dysfunction considerations
- [ ] **Code review checklist** includes accessibility validation
- [ ] **Template examples** demonstrate philosophy integration
- [ ] **Onboarding materials** explain design philosophy

### Validation Framework

- [ ] **Testing procedures** validate executive function support
- [ ] **Accessibility validation** integrated into CI/CD pipeline
- [ ] **User feedback systems** capture executive dysfunction impacts
- [ ] **Metrics dashboards** monitor accessibility improvements

## Enhanced Multi-Stage Validation

### Stage 1: Philosophy Integration Validation

```bash
# Validate philosophy documentation completeness
python scripts/validate_philosophy_integration.py docs/philosophy/

# Check design guideline coverage
python scripts/validate_design_guidelines.py docs/developers/

# Verify accessibility principle integration
python scripts/validate_accessibility_principles.py
```

### Stage 2: Architecture Pattern Validation

```bash
# Audit architecture for executive dysfunction considerations
python scripts/audit_architecture_accessibility.py

# Validate clean architecture integration points
python scripts/validate_accessibility_integration.py

# Check code patterns for cognitive load reduction
python scripts/validate_cognitive_patterns.py
```

### Stage 3: User Experience Validation

```bash
# Audit current UX for friction points
python scripts/audit_ux_friction.py

# Validate workflow accessibility
python scripts/validate_workflow_accessibility.py

# Check progressive disclosure implementation
python scripts/validate_progressive_disclosure.py
```

### Stage 4: Developer Experience Validation

```bash
# Validate developer guidelines comprehensiveness
python scripts/validate_developer_guidelines.py

# Check code review checklist integration
python scripts/validate_code_review_accessibility.py

# Validate template accessibility examples
python scripts/validate_template_accessibility.py
```

### Stage 5: Testing Framework Validation

```bash
# Validate accessibility testing procedures
python scripts/validate_accessibility_testing.py

# Check CI/CD pipeline integration
python scripts/validate_cicd_accessibility.py

# Validate metrics and monitoring systems
python scripts/validate_accessibility_metrics.py
```

## Implementation Success Metrics

### Quantitative Metrics

- **Task Initiation Time**: Reduce average time from intention to action by 40%
- **Session Recovery Time**: Reduce restart overhead to under 2 minutes
- **Context Switch Penalty**: Minimize cognitive load for agent coordination
- **Error Recovery Rate**: Improve graceful degradation and recovery by 60%
- **Documentation Effectiveness**: Measure momentum preservation across interruptions

### Qualitative Metrics

- **User Experience Feedback**: Regular validation from users with executive dysfunction
- **Developer Adoption**: Track integration of accessibility patterns in new features
- **Philosophy Consistency**: Audit new developments for design philosophy adherence
- **Community Impact**: Monitor template contributions focused on accessibility

## Security-First Accessibility Design

### Accessibility Security Considerations

- **Input Validation**: Ensure accessibility features don't create security vulnerabilities
- **Context Preservation**: Secure storage of cognitive state and session data
- **Agent Communication**: Secure context passing between agents
- **Template Security**: Validate user-submitted accessibility templates

### Threat Modeling for Accessibility

- **Cognitive Overwhelm Attacks**: Prevent deliberate complexity injection
- **Context Poisoning**: Protect session state from malicious modification
- **Template Injection**: Secure template system against malicious templates
- **Resource Exhaustion**: Prevent accessibility features from being exploited

## Completion Protocol

**After completing the Meta-PRP:**

1. **Initialize orchestrator session** for philosophy integration coordination
2. **Run all 5 validation stages** for comprehensive accessibility validation
3. **Test integration points** across all architecture layers
4. **Verify philosophy consistency** in existing and new components
5. **COMMIT CHANGES**: Always commit completed integration work
6. **Context Engineering Score Target**: 10/10 (accessibility-focused engineering)
7. **Security Integration Score Target**: 10/10 (secure accessibility implementation)
8. **Accessibility Integration Score Target**: 10/10 (comprehensive philosophy integration)

Save as: `PRPs/executive-dysfunction-design-philosophy-integration-meta-prp.md`

## Philosophy Integration Requirements

- [ ] **COMMIT ENFORCEMENT**: All philosophy integration changes committed
- [ ] **Documentation Updates**: All relevant docs updated with accessibility focus
- [ ] **Architecture Validation**: Clean Architecture layers validated for accessibility
- [ ] **User Experience Audit**: Complete UX review through executive dysfunction lens
- [ ] **Developer Guidelines**: Comprehensive accessibility development standards
- [ ] **Testing Framework**: Robust accessibility validation and monitoring

Remember: This meta-PRP transforms unconscious accessibility wisdom into systematic design philosophy, ensuring that Vespera Scriptorium's executive dysfunction-aware design becomes a deliberate, documented, and replicable approach to building tools that work with human cognitive limitations rather than against them.