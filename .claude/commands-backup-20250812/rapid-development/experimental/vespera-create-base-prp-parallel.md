# Create BASE PRP with Parallel Research (Vespera Enhanced)

## Feature: $ARGUMENTS

Generate a comprehensive PRP using Claude Code's headless mode for parallel research agents, maximizing context gathering efficiency and depth. This enhanced command leverages concurrent execution patterns from Anthropic's best practices to enable self-validation and iterative refinement.

## Enhanced Parallel Research Phase

**IMPLEMENTATION**: Execute the following 4 research agents simultaneously using Claude Code's headless mode for maximum research efficiency and real-time coordination.

### Technical Implementation: Headless Mode Execution

Based on [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) and concurrent execution patterns:

#### Coordination Setup

```bash
# Create research coordination workspace
mkdir -p .research_coordination
touch .research_coordination/agent_{1..4}_findings.md
touch .research_coordination/synthesis_workspace.md
touch .research_coordination/progress.log

# Initialize progress tracking
echo "$(date): Research coordination initialized for: $ARGUMENTS" > .research_coordination/progress.log
```

#### Parallel Agent Execution

```bash
# Agent 1: Codebase Pattern Analysis
claude -p "Analyze the codebase for patterns relevant to '$ARGUMENTS'. Research and identify:
- Similar features/patterns already implemented in the codebase
- Files that contain relevant examples or patterns to reference
- Existing conventions, architectural patterns, and code styles to follow
- Test patterns and validation approaches used in similar features
- Integration points and dependencies to consider
- File structure and organization patterns to mirror

Focus on codebase exploration only - do not write code. Use Glob, Grep, and Read tools extensively.
Write comprehensive analysis with specific file paths and code examples to .research_coordination/agent_1_findings.md.
Update progress in .research_coordination/progress.log with timestamp and status." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "Read,Glob,Grep,LS,Write" \
  --append-system-prompt "RESEARCH AGENT 1 - Codebase analysis focus. Write findings to .research_coordination/agent_1_findings.md" \
  > research_agent_1_output.json &

# Agent 2: External Technical Research
claude -p "Research external technical resources for '$ARGUMENTS'. Investigate:
- Library documentation and API references (include specific URLs)
- Implementation examples from GitHub, StackOverflow, and technical blogs
- Best practices and architectural patterns for similar features
- Common pitfalls, gotchas, and solutions
- Performance considerations and optimization techniques
- Security considerations and vulnerability patterns

Focus purely on research - do not write code. Use web search extensively.
Write comprehensive technical research with specific URLs, code examples, and implementation guidance to .research_coordination/agent_2_findings.md.
Update progress in .research_coordination/progress.log with timestamp and status." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "WebSearch,WebFetch,Write" \
  --append-system-prompt "RESEARCH AGENT 2 - External research focus. Write findings to .research_coordination/agent_2_findings.md" \
  > research_agent_2_output.json &

# Agent 3: Testing & Validation Strategy
claude -p "Research testing and validation approaches for '$ARGUMENTS'. Analyze:
- Test patterns used in the current codebase
- Unit testing strategies and frameworks
- Integration testing approaches
- Validation gates and quality checks
- Error handling and edge case patterns
- Performance testing considerations

Research only - no test implementation. Use codebase analysis and web search.
Write detailed testing strategy with specific patterns to follow and validation commands to .research_coordination/agent_3_findings.md.
Update progress in .research_coordination/progress.log with timestamp and status." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "Read,Grep,WebSearch,Write" \
  --append-system-prompt "RESEARCH AGENT 3 - Testing strategy focus. Write findings to .research_coordination/agent_3_findings.md" \
  > research_agent_3_output.json &

# Agent 4: Documentation & Context Research
claude -p "Research documentation and context resources for '$ARGUMENTS'. Gather:
- Check PRPs/ai_docs/ for relevant documentation files
- Configuration examples and setup patterns
- Environment and dependency requirements
- Known issues and workarounds documented
- Related feature documentation and examples
- User guides and implementation notes

Research focus only. Use Read tool to examine ai_docs directory.
Write documentation context with specific file references and configuration examples to .research_coordination/agent_4_findings.md.
Update progress in .research_coordination/progress.log with timestamp and status." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "Read,Glob,Grep,Write" \
  --append-system-prompt "RESEARCH AGENT 4 - Documentation context focus. Write findings to .research_coordination/agent_4_findings.md" \
  > research_agent_4_output.json &

echo "$(date): All 4 research agents launched in parallel" >> .research_coordination/progress.log
```

### Progress Monitoring & Coordination

```bash
# Real-time progress monitoring
monitor_research_progress() {
  while jobs | grep -q Running; do
    running_count=$(jobs | grep Running | wc -l)
    echo "$(date '+%H:%M:%S'): $running_count research agents active"
    
    # Show latest progress updates
    if [[ -f .research_coordination/progress.log ]]; then
      echo "Latest updates:"
      tail -n 4 .research_coordination/progress.log | sed 's/^/  /'
    fi
    
    sleep 30
  done
  
  echo "$(date '+%H:%M:%S'): All research agents completed"
}

# Launch monitoring in background
monitor_research_progress &
monitor_pid=$!

# Wait for all research agents to complete
wait

# Stop monitoring
kill $monitor_pid 2>/dev/null
```

### Output Processing & Synthesis

```bash
# Process streaming JSON outputs
echo "=== PROCESSING RESEARCH OUTPUTS ===" >> .research_coordination/synthesis_workspace.md
for agent in {1..4}; do
  echo "## Agent $agent Results" >> .research_coordination/synthesis_workspace.md
  if jq -e . research_agent_${agent}_output.json >/dev/null 2>&1; then
    jq -r 'select(.type == "assistant") | .content // empty' research_agent_${agent}_output.json >> .research_coordination/synthesis_workspace.md
  else
    echo "ERROR: Invalid JSON output from Agent $agent" >> .research_coordination/synthesis_workspace.md
  fi
  echo "" >> .research_coordination/synthesis_workspace.md
done

# Launch synthesis agent
claude -p "Synthesize the research findings from all 4 agents in .research_coordination/ directory. 
Combine findings from:
- agent_1_findings.md (codebase patterns)
- agent_2_findings.md (external research)
- agent_3_findings.md (testing strategies)
- agent_4_findings.md (documentation context)

Create comprehensive analysis and implementation roadmap.
Write synthesis to .research_coordination/synthesis_workspace.md" \
  --allowedTools "Read,Write" \
  --append-system-prompt "SYNTHESIS AGENT - Combine all research findings into actionable PRP foundation" \
  --output-format stream-json > synthesis_output.json
```

## Research Synthesis & PRP Generation

Using the synthesized research findings, generate a comprehensive PRP following the base template structure:

### PRP Template Integration

```bash
# Generate comprehensive PRP using synthesized research
claude -p "Using the synthesized research findings in .research_coordination/, create a comprehensive BASE PRP for '$ARGUMENTS' following the template structure:

## Goal
[Specific, measurable outcome based on research]

## Why
- Business value and user impact
- Integration with existing features (from codebase analysis)
- Problems this solves and for whom

## What
[User-visible behavior and technical requirements]

## All Needed Context
### Documentation & References
- url: [Specific URLs from external research]
- file: [Specific file paths from codebase analysis]
- docfile: [Relevant PRPs/ai_docs/ files]

### Current Codebase Context
[Tree structure and relevant files from Agent 1]

### Implementation Patterns
[Specific patterns to follow from codebase analysis]

### Known Gotchas
[Library quirks and caveats from research]

## Implementation Blueprint
### Data Models and Structure
[Type-safe models following existing patterns]

### Task List
[Ordered tasks based on dependency analysis]

### Pseudocode
[Implementation approach with critical details]

### Integration Points
[Database, config, routes based on existing patterns]

## Validation Loop
### Level 1: Syntax & Style
[Commands specific to this codebase from Agent 3]

### Level 2: Unit Tests
[Test patterns from codebase analysis]

### Level 3: Integration Tests
[End-to-end validation approach]

## Final Validation Checklist
[Comprehensive quality gates]

Save the comprehensive PRP as PRPs/$ARGUMENTS-parallel.md" \
  --allowedTools "Read,Write" \
  --append-system-prompt "PRP GENERATOR - Create comprehensive implementation PRP from research synthesis" \
  --output-format stream-json > prp_generation.json
```

### Quality Assurance Framework

```bash
# Validate PRP quality using automated checks
claude -p "Review the generated PRP at PRPs/$ARGUMENTS-parallel.md and validate:

1. **Research Quality Score** (1-10):
   - Comprehensiveness of context gathering
   - Quality of external research and references
   - Depth of codebase pattern analysis
   - Testing strategy completeness

2. **Implementation Clarity Score** (1-10):
   - Clear implementation path with dependencies
   - Specific file references and patterns
   - Actionable task breakdown
   - Integration points defined

3. **Validation Completeness Score** (1-10):
   - Executable validation commands
   - Comprehensive quality gates
   - Error handling approaches
   - Success criteria defined

4. **One-Pass Success Probability** (1-10):
   - Confidence level for successful implementation
   - Context sufficiency assessment
   - Risk mitigation coverage

Generate quality scorecard and save to .research_coordination/quality_assessment.md
Target: 8+ on all metrics through enhanced parallel research depth" \
  --allowedTools "Read,Write" \
  --max-turns 8 > quality_validation.json
```

## Alternative Execution Methods

### Git Worktrees for Complex Analysis

```bash
# For deeper analysis requiring isolated working spaces
git worktree add ../prp-research-agent-1 main
git worktree add ../prp-research-agent-2 main  
git worktree add ../prp-research-agent-3 main
git worktree add ../prp-research-agent-4 main

# Launch Claude in each worktree (separate terminal tabs)
echo "Launch agents in separate terminals:"
echo "Terminal 1: cd ../prp-research-agent-1 && claude"
echo "Terminal 2: cd ../prp-research-agent-2 && claude"
echo "Terminal 3: cd ../prp-research-agent-3 && claude"
echo "Terminal 4: cd ../prp-research-agent-4 && claude"

# Cleanup when complete
# git worktree remove ../prp-research-agent-{1..4}
```

### Error Recovery & Resilience

```bash
# Health check and recovery
for agent in {1..4}; do
  if ! jq -e . research_agent_${agent}_output.json >/dev/null 2>&1; then
    echo "Agent $agent failed - restarting with recovery prompt..."
    claude -p "Resume research task $agent for '$ARGUMENTS' - continue where previous attempt left off" \
      --output-format stream-json \
      --max-turns 10 \
      > research_agent_${agent}_recovery.json &
  fi
done
```

## Output & Cleanup

### Deliverable Package

```bash
# Create final deliverable package
mkdir -p "PRPs/research-artifacts-$(date +%Y%m%d)"
cp .research_coordination/* "PRPs/research-artifacts-$(date +%Y%m%d)/"
cp research_agent_*.json "PRPs/research-artifacts-$(date +%Y%m%d)/"

# Generate summary report
echo "# PRP Research Summary: $ARGUMENTS" > "PRPs/research-artifacts-$(date +%Y%m%d)/summary.md"
echo "Generated: $(date)" >> "PRPs/research-artifacts-$(date +%Y%m%d)/summary.md"
echo "Research agents: 4 parallel instances" >> "PRPs/research-artifacts-$(date +%Y%m%d)/summary.md"
echo "Primary deliverable: PRPs/$ARGUMENTS-parallel.md" >> "PRPs/research-artifacts-$(date +%Y%m%d)/summary.md"
```

### Cleanup

```bash
# Clean up temporary files
rm -f research_agent_*.json synthesis_output.json prp_generation.json quality_validation.json
rm -rf .research_coordination

echo "$(date): Enhanced parallel PRP creation completed for: $ARGUMENTS"
echo "Deliverable: PRPs/$ARGUMENTS-parallel.md"
echo "Research artifacts archived: PRPs/research-artifacts-$(date +%Y%m%d)/"
```

## Quality Checklist

Before marking complete, verify:

- [ ] All 4 research agents executed successfully with headless mode
- [ ] Comprehensive context gathered from codebase, external sources, testing, and documentation
- [ ] Research synthesis completed and quality-assessed
- [ ] PRP generated following template structure with all required sections
- [ ] Validation gates defined and executable
- [ ] Quality scores 8+ across all metrics
- [ ] Implementation path clear with specific file references and patterns
- [ ] Error handling and recovery strategies included
- [ ] Research artifacts properly archived

## Success Metrics

- **Research Depth**: 4x faster research through parallel execution
- **Context Richness**: Comprehensive multi-angle analysis
- **Implementation Clarity**: Clear path with specific patterns and examples
- **Quality Assurance**: Automated validation and scoring
- **Time Efficiency**: Parallel approach reduces PRP creation time significantly
- **Success Probability**: 8+ confidence score for one-pass implementation

---

**Remember**: This enhanced command leverages Claude Code's headless mode for true parallel execution, real-time monitoring, and comprehensive error handling. The goal is one-pass implementation success through enhanced parallel research and context gathering.
