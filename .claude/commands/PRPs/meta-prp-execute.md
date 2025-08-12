# Execute META-PRP with Orchestrator Multi-Agent Coordination

Execute comprehensive meta-PRPs using the task orchestrator's full orchestration capabilities to coordinate sub-agents through systematic multi-phase workflows.

## Meta-PRP File: $ARGUMENTS

## Immediate Orchestrator Session Activation

**MANDATORY FIRST STEPS - Execute in Order:**

```bash
# 1. Verify orchestrator connection and full functionality
claude mcp list | grep task-orchestrator || (echo "ORCHESTRATOR NOT CONNECTED - Fixing..." && claude mcp restart task-orchestrator)

# 2. Test critical orchestrator tools for meta-coordination
# orchestrator_health_check must be available and functioning
```

**CRITICAL**: If orchestrator fails, STOP and follow CLAUDE.md protocol. Meta-PRPs require full orchestrator functionality.

**IMMEDIATE SESSION TAKEOVER:**
```yaml
# 3. Initialize orchestrator session for meta-PRP execution coordination
orchestrator_initialize_session:
  working_directory: "/current/project/path"
  session_name: "meta-prp-execution-{concept}-{timestamp}"
  
# 4. Orchestrator becomes the primary coordinator for all sub-agent spawning
orchestrator_role: "primary_execution_coordinator"
coordination_mode: "multi_agent_meta_prp_execution"
```

## Enhanced Context Loading

**MANDATORY**: Load and understand all context before execution:

```yaml
required_context_loading:
  - file: $ARGUMENTS  # The meta-PRP file to execute
    why: "Complete meta-PRP specification with orchestrator integration"
    sections: ["ALL - complete understanding required"]

  - file: PRPs/v2.0-release-meta-prp/meta-coordination-orchestrator.md
    why: "Reference implementation patterns for meta-coordination"
    sections: ["Orchestrator Tools Integration", "Workflow Patterns", "Testing Matrix"]

  - file: PRPs/ai_docs/context-engineering-guide.md
    why: "Multi-agent context engineering principles"
    sections: ["Multi-Agent Coordination", "Context Sharing Patterns"]

  - file: PRPs/ai_docs/systematic-testing-framework.md
    why: "Multi-agent testing and validation"
    sections: ["Complex Workflow Testing", "Orchestrator Validation"]

  - file: CLAUDE.md
    why: "Critical orchestrator failure protocols and requirements"
    sections: ["Task Orchestrator Failure Protocol", "Critical Directives"]
```

## Meta-PRP Execution Framework

### Phase 1: Orchestrator Session Initialization

**Main Agent Responsibilities:**

```yaml
orchestrator_session_setup:
  action: orchestrator_initialize_session
  parameters:
    working_directory: "/current/project/path"
    session_name: "meta-prp-{concept}-execution"
    
orchestrator_health_validation:
  action: orchestrator_health_check
  purpose: "Ensure orchestrator ready for multi-agent coordination"
  
meta_task_creation:
  action: orchestrator_plan_task
  parameters:
    title: "Meta-PRP Execution: {concept}"
    description: "Multi-agent coordination for {concept} from meta-PRP"
    complexity: "very_complex"
    task_type: "breakdown"
    specialist_type: "coordinator"
    
initial_status_check:
  action: orchestrator_get_status
  purpose: "Baseline status before sub-agent spawning"
```

### Phase 2: Sub-Agent Coordination and Task Breakdown

**Main Agent Task Breakdown:**

```yaml
sub_task_creation_workflow:
  # Create all sub-tasks from meta-PRP specification
  research_task:
    action: orchestrator_plan_task
    parameters:
      title: "{concept} Research Coordination"
      description: "Research phase from meta-PRP with specialist context"
      complexity: "complex"
      task_type: "research"
      specialist_type: "researcher"
      parent_task_id: "[meta_task_id]"
      
  architecture_task:
    action: orchestrator_plan_task
    parameters:
      title: "{concept} Architecture Design"
      description: "Architecture phase from meta-PRP with specialist context"
      complexity: "complex"
      task_type: "implementation"
      specialist_type: "architect"
      parent_task_id: "[meta_task_id]"
      dependencies: ["research_task_id"]
      
  implementation_task:
    action: orchestrator_plan_task
    parameters:
      title: "{concept} Implementation Coordination"
      description: "Implementation phase from meta-PRP with specialist context"
      complexity: "very_complex"
      task_type: "implementation"
      specialist_type: "coder"
      parent_task_id: "[meta_task_id]"
      dependencies: ["architecture_task_id"]
      
  testing_task:
    action: orchestrator_plan_task
    parameters:
      title: "{concept} Testing Strategy"
      description: "Testing phase from meta-PRP with specialist context"
      complexity: "complex"
      task_type: "testing"
      specialist_type: "tester"
      parent_task_id: "[meta_task_id]"
      dependencies: ["implementation_task_id"]
      
  security_task:
    action: orchestrator_plan_task
    parameters:
      title: "{concept} Security Validation"
      description: "Security phase from meta-PRP with specialist context"
      complexity: "complex"
      task_type: "review"
      specialist_type: "reviewer"
      parent_task_id: "[meta_task_id]"
      dependencies: ["testing_task_id"]

progress_monitoring:
  action: orchestrator_get_status
  purpose: "Monitor task creation and dependencies"
```

### Phase 3: Intelligent Sub-Agent Spawning and Execution

**Execution Context Detection and Agent Spawning:**

```yaml
intelligent_agent_spawning:
  execution_context_detection:
    if_claude_code_context:
      agent_spawning_method: "Claude Code Task tool"
      coordination_backbone: "Orchestrator maintains all coordination state"
      hot_reload_support: "Use /mcp reconnect when orchestrator updated"
      artifact_storage: "All work stored in orchestrator artifacts"
      
    if_orchestrator_native_context:
      agent_spawning_method: "Orchestrator native agent-to-agent capabilities"
      coordination_backbone: "Full orchestrator session context passing"
      history_retention: "Orchestrator maintains execution history for 'undo' features"
      artifact_storage: "Native orchestrator artifact management"
      
sub_agent_spawning_claude_code_mode:
  research_agent:
    spawning_method: "Task tool with general-purpose agent"
    specialist_context_retrieval:
      action: orchestrator_execute_task
      task_id: "[research_task_id]"
      
    sub_agent_instructions: |
      You are a RESEARCH SPECIALIST executing orchestrator task: [research_task_id]
      
      CRITICAL ORCHESTRATOR INTEGRATION: 
      - FIRST: Use orchestrator_execute_task to get your specialist context and instructions
      - Work ONLY on the specific task assigned to you by the orchestrator
      - Use orchestrator_complete_task when finished - ALL work goes into artifacts
      - Reference meta-PRP file for complete context: $ARGUMENTS
      - Load relevant PRPs/ai_docs/ for specialized context
      - The orchestrator is your coordination backbone - maintain session throughout
      
      LESSONS LEARNED INTEGRATION:
      - Apply hook-style automated validation to your work
      - Consider what automated checks would prevent problems in your domain
      - Design your work to be artifact-centric, not summary-centric
      - All deliverables stored in orchestrator for future 'undo' capabilities
      
      Your task: Execute the research phase as specified in the meta-PRP
      Expected deliverable: Complete research artifacts via orchestrator_complete_task
      
sub_agent_spawning_orchestrator_native_mode:
  # This mode will be available when agent-to-agent is fully implemented
  research_agent:
    spawning_method: "orchestrator_spawn_specialist_agent"
    session_context_passing: "Full orchestrator session state shared"
    history_tracking: "All work tracked for automated undo capabilities"
    
    specialist_instructions: |
      You are spawned by the orchestrator as a RESEARCH SPECIALIST
      - Full orchestrator session context automatically provided
      - Work integrated into orchestrator's history system
      - Automated documentation retention and 'undo' capabilities available
      - Session management handled automatically by orchestrator
      
  architecture_agent:
    specialist_context_retrieval:
      action: orchestrator_execute_task
      task_id: "[architecture_task_id]"
      
    sub_agent_instructions: |
      You are an ARCHITECTURE SPECIALIST working on task: [architecture_task_id]
      
      CRITICAL:
      - Use orchestrator_execute_task to get your specialist context
      - Work ONLY on the specific task assigned to you
      - Use orchestrator_complete_task when finished with detailed artifacts
      - Reference meta-PRP file for complete context: $ARGUMENTS
      - Wait for research task completion (dependency management)
      
      Your task: Execute the architecture phase as specified in the meta-PRP
      Expected deliverable: Complete architecture artifacts stored via orchestrator_complete_task

  # Pattern continues for implementation_agent, testing_agent, security_agent...
```

### Phase 4: Progress Monitoring and Coordination

**Main Agent Monitoring Loop:**

```yaml
coordination_monitoring:
  continuous_status_monitoring:
    action: orchestrator_get_status
    frequency: "regular intervals"
    purpose: "Track sub-agent progress and identify blockers"
    
  task_query_management:
    action: orchestrator_query_tasks
    parameters:
      status: ["in_progress", "blocked"]
      parent_task_id: "[meta_task_id]"
    purpose: "Detailed progress tracking of all sub-tasks"
    
  dependency_management:
    purpose: "Ensure sub-agents can proceed when dependencies complete"
    monitoring: "Task completion triggers for dependent tasks"
    
  health_monitoring:
    action: orchestrator_health_check
    purpose: "Ensure orchestrator stability during multi-agent execution"
```

### Phase 5: Result Synthesis and Completion

**Main Agent Result Aggregation:**

```yaml
result_synthesis_workflow:
  wait_for_completion:
    condition: "All sub-tasks completed"
    monitoring: orchestrator_query_tasks
    
  artifact_aggregation:
    action: orchestrator_synthesize_results
    parameters:
      parent_task_id: "[meta_task_id]"
    purpose: "Aggregate all sub-agent artifacts into cohesive result"
    
  final_validation:
    action: orchestrator_health_check
    purpose: "System health after complex multi-agent workflow"
    
  meta_task_completion:
    action: orchestrator_complete_task
    parameters:
      task_id: "[meta_task_id]"
      summary: "Meta-PRP execution completed with multi-agent coordination"
      detailed_work: "[synthesized_results_from_orchestrator]"
      artifact_type: "general"
      next_action: "complete"
    
  maintenance_cleanup:
    action: orchestrator_maintenance_coordinator
    parameters:
      action: "scan_cleanup"
      scope: "current_session"
    purpose: "Clean up completed multi-agent workflow"
    
  hot_reload_validation:
    condition: "If orchestrator code was modified during execution"
    action: "/mcp reconnect"
    purpose: "Ensure orchestrator changes picked up without Claude Code restart"
    
  hook_integration_validation:
    action: "Run git hooks for automated quality validation"
    purpose: "Apply lessons learned - let hooks catch problems automatically"
    
  session_accumulation_prevention:
    action: "orchestrator_list_sessions + cleanup old sessions"
    purpose: "Prevent infinite session file accumulation discovered in lessons learned"
```

## Enhanced Multi-Agent Execution Pattern

### Sub-Agent Execution Template

Each sub-agent follows this pattern:

```yaml
sub_agent_execution_pattern:
  context_loading:
    - "Load meta-PRP file: $ARGUMENTS"
    - "Load relevant PRPs/ai_docs/ for specialist context"
    - "Understand specific task assignment and dependencies"
    
  specialist_context_retrieval:
    action: orchestrator_execute_task
    task_id: "[assigned_task_id]"
    purpose: "Get specialist-specific context and instructions"
    
  task_execution:
    - "Execute assigned phase from meta-PRP specification"
    - "Apply specialist expertise (researcher/architect/coder/tester/reviewer)"
    - "Generate detailed work artifacts"
    - "Ensure security and quality standards"
    
  task_completion:
    action: orchestrator_complete_task
    parameters:
      task_id: "[assigned_task_id]"
      summary: "Brief summary of specialist work completed"
      detailed_work: "Complete detailed artifacts and deliverables"
      artifact_type: "[code/documentation/analysis/design/test]"
      next_action: "continue"  # or "complete" if final task
    
  return_to_main_agent:
    message: "Task [assigned_task_id] completed. Artifacts stored in orchestrator."
    artifact_reference: "orchestrator_task_[assigned_task_id]_artifacts"
```

## Orchestrator Tool Integration Matrix

### Main Agent Tool Usage

| Phase | Tool | Purpose | Critical |
|-------|------|---------|----------|
| Initialization | orchestrator_initialize_session | Session setup | ✓ |
| Initialization | orchestrator_health_check | Health validation | ✓ |
| Planning | orchestrator_plan_task | Meta-task and sub-task creation | ✓ |
| Monitoring | orchestrator_get_status | Progress tracking | ✓ |
| Monitoring | orchestrator_query_tasks | Detailed task management | ✓ |
| Coordination | orchestrator_execute_task | Sub-agent context | ✓ |
| Completion | orchestrator_synthesize_results | Result aggregation | ✓ |
| Completion | orchestrator_complete_task | Final artifact storage | ✓ |
| Cleanup | orchestrator_maintenance_coordinator | Workflow cleanup | ○ |

### Sub-Agent Tool Usage

| Tool | Purpose | Required |
|------|---------|----------|
| orchestrator_execute_task | Get specialist context | ✓ |
| orchestrator_complete_task | Store detailed artifacts | ✓ |
| orchestrator_get_status | Check dependencies (optional) | ○ |

## Error Handling and Recovery

### Orchestrator Failure Recovery

```yaml
failure_recovery_protocol:
  orchestrator_health_failure:
    immediate_action: "STOP execution"
    recovery_steps:
      - "Follow CLAUDE.md orchestrator failure protocol"
      - "Spawn fix agent per critical directives"
      - "DO NOT continue without working orchestrator"
      
  sub_agent_failure:
    detection: "orchestrator_get_status monitoring"
    recovery_steps:
      - "Query failed task details with orchestrator_query_tasks"
      - "Cancel failed task with orchestrator_cancel_task"
      - "Re-plan task with orchestrator_plan_task"
      - "Spawn replacement sub-agent"
      
  dependency_blocking:
    detection: "orchestrator_query_tasks shows blocked tasks"
    resolution: "Identify and resolve dependency issues"
    escalation: "Update task dependencies with orchestrator_update_task"
```

## Validation and Quality Assurance

### Meta-PRP Execution Validation

```bash
# Pre-execution validation
python scripts/validate_meta_prp_execution_readiness.py $ARGUMENTS

# Orchestrator health validation
python scripts/validate_orchestrator_health.py --comprehensive

# Multi-agent coordination validation
python scripts/validate_multi_agent_coordination_setup.py $ARGUMENTS
```

### During Execution Monitoring

```bash
# Real-time orchestrator monitoring
python scripts/monitor_orchestrator_health.py --duration 3600 --alert-on-failure

# Multi-agent progress tracking
python scripts/track_multi_agent_progress.py --meta-prp $ARGUMENTS

# Artifact validation as tasks complete
python scripts/validate_task_artifacts.py --continuous
```

### Post-Execution Validation

```bash
# Complete meta-PRP execution validation
python scripts/validate_meta_prp_completion.py $ARGUMENTS

# Artifact synthesis validation
python scripts/validate_artifact_synthesis.py $ARGUMENTS

# Multi-agent coordination success validation
python scripts/validate_multi_agent_success.py $ARGUMENTS
```

## Enhanced Success Criteria with Lessons Learned Integration

### Core Execution Requirements

- [ ] **Orchestrator session** successfully initialized and maintained as primary coordinator
- [ ] **Meta-task breakdown** completed with all sub-tasks created via orchestrator
- [ ] **Sub-agents spawned** via intelligent context detection (Claude Code vs native)
- [ ] **All sub-tasks completed** with detailed artifacts stored in orchestrator
- [ ] **Results synthesized** via orchestrator_synthesize_results (no manual summaries)
- [ ] **Meta-task completed** with comprehensive final artifacts in orchestrator storage

### Lessons Learned Integration Success

- [ ] **Hook integration** applied for automated problem detection and prevention
- [ ] **Session lifecycle management** properly handled to prevent accumulation
- [ ] **Artifact-centric workflow** maintained throughout (no scattered summaries)
- [ ] **Hot-reload capability** tested if orchestrator changes were made
- [ ] **Multi-database architecture** properly utilized (SQLite, Vector, Graph)
- [ ] **Automated validation** applied at each phase via hook-inspired patterns

### Multi-Agent Coordination Success

- [ ] **Dependency management** properly handled between sub-agents
- [ ] **No sub-agent conflicts** or resource contention
- [ ] **All specialist contexts** properly retrieved and utilized
- [ ] **Artifact storage consistency** across all sub-agents
- [ ] **Progress monitoring** maintained throughout execution

### Quality and Security Validation

- [ ] **Security validation** completed by dedicated security sub-agent
- [ ] **Quality assurance** maintained across all phases
- [ ] **Context engineering** properly applied to all sub-agent work
- [ ] **Enhanced documentation** integrated from PRPs/ai_docs/
- [ ] **Clean architecture** principles followed throughout

### Orchestrator Integration Success

- [ ] **All orchestrator tools** functioned correctly throughout execution
- [ ] **No orchestrator failures** or degraded functionality
- [ ] **Health monitoring** maintained system stability
- [ ] **Maintenance coordination** completed successfully
- [ ] **Session preservation** maintained throughout complex workflow

## Completion Protocol

**After Meta-PRP Execution:**

1. **Verify all sub-agents completed** their assigned tasks
2. **Validate artifact storage** via orchestrator_complete_task
3. **Run synthesis validation** on orchestrator_synthesize_results
4. **Execute maintenance cleanup** via orchestrator_maintenance_coordinator
5. **COMMIT CHANGES**: Always commit completed meta-PRP execution results
6. **Context Engineering Score Target**: 10/10 (multi-agent coordination)
7. **Security Integration Score Target**: 10/10 (dedicated security validation)
8. **Orchestrator Integration Score Target**: 10/10 (full tool suite utilized)
9. **Multi-Agent Coordination Score Target**: 10/10 (seamless collaboration)
10. **Lessons Learned Integration Score Target**: 10/10 (hook patterns, session management, artifact-centric)
11. **Future 'Undo' Readiness Score Target**: 10/10 (all work stored in orchestrator for automation)

**Mad Scientist Achievement Unlocked**: *"Eventually I WILL have my automated 'oops! undo that!' feature!"* 
- All work stored in orchestrator artifacts enables future automated undo capabilities
- Session management prevents infinite accumulation discovered in lessons learned  
- Hook patterns provide the automated problem detection foundation
- Agent-to-agent architecture will complete the automation vision

## No Manual Summary Required

**CRITICAL**: Meta-PRP execution does NOT require manual result summaries. The orchestrator's 
`orchestrator_synthesize_results` and `orchestrator_complete_task` tools automatically handle:

- **Artifact aggregation** from all sub-agents
- **Result synthesis** into cohesive deliverables  
- **Detailed work storage** with proper categorization
- **Progress tracking** and completion status

**Return only**: Reference to the orchestrator task artifacts for the main agent to read.

Remember: Meta-PRP execution with orchestrator multi-agent coordination enables systematic execution of complex, multi-phase projects with professional quality, comprehensive validation, and seamless collaboration between specialized sub-agents working in orchestrated harmony.