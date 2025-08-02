# Create PLANNING PRP with Parallel Research (Vespera Enhanced)

Transform rough ideas into comprehensive PRDs using Claude Code's headless mode for parallel research agents, maximizing efficiency and depth.

## Idea: $ARGUMENTS

## Enhanced Parallel Research Discovery

**IMPLEMENTATION**: Execute the following 4 research agents simultaneously using Claude Code's headless mode patterns from Anthropic's best practices for maximum research efficiency and real-time coordination.

### Technical Implementation: Concurrent Execution Framework

Based on [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) and parallel execution patterns:

#### Coordination Infrastructure

```bash
# Create research coordination workspace
mkdir -p .planning_research_coordination
touch .planning_research_coordination/market_intelligence.md
touch .planning_research_coordination/technical_feasibility.md
touch .planning_research_coordination/ux_patterns.md
touch .planning_research_coordination/best_practices.md
touch .planning_research_coordination/synthesis_workspace.md
touch .planning_research_coordination/progress.log

# Initialize planning research
echo "$(date): Planning research coordination initialized for: $ARGUMENTS" > .planning_research_coordination/progress.log
```

#### Parallel Research Agent Execution

```bash
# Agent 1: Market Intelligence Research
claude -p "Research the market landscape for '$ARGUMENTS'. Conduct deep analysis of:
- Competitor landscape and positioning
- Market size, growth trends, and opportunities
- Pricing models and revenue strategies
- Existing solutions and their limitations
- Market gaps and unmet needs
- Target audience and user segments

Focus purely on research - do not write any code. Use web search extensively.
Write comprehensive market analysis report with specific data points and insights to .planning_research_coordination/market_intelligence.md.
Update progress in .planning_research_coordination/progress.log with timestamp and findings summary." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "WebSearch,WebFetch,Write" \
  --append-system-prompt "MARKET RESEARCH AGENT - Focus on market intelligence and competitive analysis. Write findings to .planning_research_coordination/market_intelligence.md" \
  > market_agent_output.json &

# Agent 2: Technical Feasibility Research
claude -p "Analyze technical feasibility for '$ARGUMENTS'. Research and evaluate:
- Recommended technology stacks and frameworks
- System architecture patterns and best practices
- Integration possibilities with existing systems
- Scalability and performance considerations
- Technical challenges and solutions
- Development effort estimation

Focus on research only - no code implementation. Use web search for current best practices.
Write technical recommendations with pros/cons analysis to .planning_research_coordination/technical_feasibility.md.
Update progress in .planning_research_coordination/progress.log with timestamp and technical insights." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "WebSearch,WebFetch,Write" \
  --append-system-prompt "TECHNICAL RESEARCH AGENT - Focus on architecture and feasibility analysis. Write findings to .planning_research_coordination/technical_feasibility.md" \
  > technical_agent_output.json &

# Agent 3: User Experience Pattern Research
claude -p "Research user experience patterns for '$ARGUMENTS'. Investigate:
- User journey mapping and flow examples
- Pain points in existing solutions
- UX best practices and design patterns
- Accessibility standards and requirements
- User interface trends and innovations
- Usability testing insights from similar products

Research only - no design creation. Use web search for UX case studies.
Write UX analysis with actionable recommendations to .planning_research_coordination/ux_patterns.md.
Update progress in .planning_research_coordination/progress.log with timestamp and UX insights." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "WebSearch,WebFetch,Write" \
  --append-system-prompt "UX RESEARCH AGENT - Focus on user experience patterns and design analysis. Write findings to .planning_research_coordination/ux_patterns.md" \
  > ux_agent_output.json &

# Agent 4: Industry Standards & Compliance Research
claude -p "Research industry best practices for '$ARGUMENTS'. Cover:
- Security standards and compliance requirements
- Data privacy and protection regulations
- Performance benchmarks and KPIs
- Quality assurance methodologies
- Risk management practices
- Legal and regulatory considerations

Research focus only. Use web search for compliance guides.
Write comprehensive best practices guide with specific standards to .planning_research_coordination/best_practices.md.
Update progress in .planning_research_coordination/progress.log with timestamp and compliance insights." \
  --output-format stream-json \
  --max-turns 15 \
  --allowedTools "WebSearch,WebFetch,Write" \
  --append-system-prompt "COMPLIANCE RESEARCH AGENT - Focus on industry standards and best practices. Write findings to .planning_research_coordination/best_practices.md" \
  > compliance_agent_output.json &

echo "$(date): All 4 planning research agents launched in parallel" >> .planning_research_coordination/progress.log
```

### Advanced Progress Monitoring

```bash
# Enhanced progress monitoring with agent status tracking
monitor_planning_research() {
  while jobs | grep -q Running; do
    running_count=$(jobs | grep Running | wc -l)
    echo "$(date '+%H:%M:%S'): $running_count planning research agents active"
    
    # Show agent-specific progress
    echo "Agent Status:"
    for agent_type in market technical ux compliance; do
      if [[ -f .planning_research_coordination/${agent_type}_*.md ]]; then
        word_count=$(wc -w < .planning_research_coordination/${agent_type}_*.md 2>/dev/null || echo "0")
        echo "  ${agent_type}: ${word_count} words researched"
      fi
    done
    
    # Show latest progress updates
    if [[ -f .planning_research_coordination/progress.log ]]; then
      echo "Latest research updates:"
      tail -n 4 .planning_research_coordination/progress.log | sed 's/^/  /'
    fi
    
    sleep 30
  done
  
  echo "$(date '+%H:%M:%S'): All planning research agents completed"
}

# Launch monitoring with real-time updates
monitor_planning_research &
monitor_pid=$!

# Wait for all research agents
wait

# Stop monitoring
kill $monitor_pid 2>/dev/null
```

### Research Synthesis & Quality Validation

```bash
# Process and validate all research outputs
echo "=== PROCESSING PLANNING RESEARCH OUTPUTS ===" >> .planning_research_coordination/synthesis_workspace.md

# Validate JSON outputs and extract content
for agent_type in market technical ux compliance; do
  output_file="${agent_type}_agent_output.json"
  if jq -e . "$output_file" >/dev/null 2>&1; then
    echo "## ${agent_type^} Research Results" >> .planning_research_coordination/synthesis_workspace.md
    jq -r 'select(.type == "assistant") | .content // empty' "$output_file" >> .planning_research_coordination/synthesis_workspace.md
    echo "" >> .planning_research_coordination/synthesis_workspace.md
  else
    echo "ERROR: Invalid JSON output from ${agent_type} agent" >> .planning_research_coordination/synthesis_workspace.md
  fi
done

# Advanced synthesis with cross-research integration
claude -p "Synthesize comprehensive planning research from .planning_research_coordination/ directory.
Integrate findings from:
- market_intelligence.md (competitive landscape, opportunities)
- technical_feasibility.md (architecture recommendations, challenges)
- ux_patterns.md (user experience best practices, design patterns)
- best_practices.md (industry standards, compliance requirements)

Create integrated analysis covering:
1. Market Opportunity Assessment with competitive positioning
2. Technical Architecture Framework with feasibility analysis
3. User Experience Blueprint with journey mapping
4. Implementation Readiness with risk assessment

Write comprehensive synthesis to .planning_research_coordination/synthesis_workspace.md" \
  --allowedTools "Read,Write" \
  --append-system-prompt "PLANNING SYNTHESIS AGENT - Integrate all research into comprehensive planning foundation" \
  --output-format stream-json > planning_synthesis.json
```

## User Validation & Requirements Gathering

### Critical Clarification Framework

```bash
# Generate user validation questions based on research findings
claude -p "Based on the synthesized research in .planning_research_coordination/synthesis_workspace.md, 
generate critical questions to ask the user about '$ARGUMENTS' covering:

1. **Scope & Constraints**
   - Target timeline and resource constraints
   - Must-have vs nice-to-have features
   - Integration requirements with existing systems

2. **Success Definition**  
   - Primary success metrics and KPIs
   - User adoption goals and business objectives
   - Performance and quality targets

3. **Technical Context**
   - Technology preferences or restrictions
   - Team expertise and capabilities
   - Infrastructure and deployment constraints

4. **User Context**
   - Primary user personas and use cases
   - Current user pain points and workflows
   - Competitive differentiation requirements

Generate structured questions with context from research findings.
Save questions to .planning_research_coordination/user_validation_questions.md" \
  --allowedTools "Read,Write" \
  --max-turns 8 > user_questions.json

# Present questions to user (manual step)
echo "=== USER VALIDATION REQUIRED ==="
echo "Please review and answer questions in: .planning_research_coordination/user_validation_questions.md"
echo "This input is critical for generating an accurate and actionable PRD."
```

## PRD Generation Framework

### Comprehensive PRD Creation

```bash
# Generate comprehensive PRD using all research and user input
claude -p "Using the synthesized research findings and user validation responses, create a comprehensive Planning PRD for '$ARGUMENTS' following this enhanced structure:

# Product Requirements Document: $ARGUMENTS

## 1. Executive Summary
- Problem statement with market context
- Proposed solution with unique value proposition
- Success criteria with measurable outcomes
- Resource requirements and timeline estimate

## 2. Market Analysis & Opportunity
[Market Intelligence findings with competitive landscape]
- Market size and growth potential
- Competitive positioning and differentiation
- Target user segments and personas
- Value proposition and pricing strategy

## 3. User Experience Design
[UX Research findings with design patterns]
- User personas and journey mapping
- Key user flows with Mermaid diagrams
- Wireframe requirements and design system needs
- Accessibility and usability considerations

## 4. Technical Architecture & Feasibility
[Technical Research findings with recommendations]
- System architecture with Mermaid diagrams
- Technology stack recommendations
- Integration points and dependencies
- Scalability and performance requirements

## 5. Security, Compliance & Standards
[Best Practices findings with requirements]
- Security architecture and requirements
- Compliance standards and regulations
- Quality assurance methodology
- Risk assessment and mitigation strategies

## 6. Implementation Strategy
- Development phases with dependencies
- Resource allocation and team requirements
- Timeline estimates with milestones
- Success metrics and validation gates

## 7. Success Metrics & KPIs
- Key Performance Indicators with targets
- User adoption and engagement metrics
- Business impact measurements
- Technical performance benchmarks

## 8. Risk Assessment & Mitigation
- Technical risks with mitigation strategies
- Market risks with contingency plans
- Resource risks with alternatives
- Timeline risks with buffer strategies

Save the comprehensive PRD as PRPs/$ARGUMENTS-planning-prd.md

Include required Mermaid diagrams:
1. User Flow Diagram showing primary user journeys
2. System Architecture Diagram showing components and data flow
3. Implementation Timeline Gantt chart showing development phases" \
  --allowedTools "Read,Write" \
  --max-turns 20 \
  --append-system-prompt "PRD GENERATOR - Create comprehensive planning PRD from integrated research and user validation" \
  --output-format stream-json > prd_generation.json
```

### Visual Documentation Generation

```bash
# Generate required Mermaid diagrams
claude -p "Create comprehensive Mermaid diagrams for the PRD based on research findings:

1. **User Flow Diagram**:
\`\`\`mermaid
flowchart TD
    A[User Entry Point] --> B{Decision/Action}
    B -->|Primary Path| C[Core Functionality]
    B -->|Alternative| D[Secondary Path]
    C --> E[Success Outcome]
    D --> F[Alternative Outcome]
\`\`\`

2. **System Architecture Diagram**:
\`\`\`mermaid
graph TB
    Frontend[User Interface] --> API[API Gateway]
    API --> Auth[Authentication Service]
    API --> Core[Core Business Logic]
    Core --> DB[(Database)]
    Core --> External[External Services]
\`\`\`

3. **Implementation Timeline**:
\`\`\`mermaid
gantt
    title Implementation Phases
    section Research & Design
    Market Research: 2024-01-01, 2w
    Technical Design: 2w
    section Development
    Core Features: 4w
    Integration: 2w
    section Testing & Launch
    QA Testing: 2w
    Launch Prep: 1w
\`\`\`

Customize diagrams based on specific requirements from research findings.
Append diagrams to PRPs/$ARGUMENTS-planning-prd.md" \
  --allowedTools "Read,Write,Edit" \
  --max-turns 10 > diagram_generation.json
```

## Quality Assurance & Validation

### Multi-Level PRD Validation

```bash
# Comprehensive PRD quality assessment
claude -p "Review and validate the generated PRD at PRPs/$ARGUMENTS-planning-prd.md against industry standards:

1. **Research Integration Score** (1-10):
   - Market analysis comprehensiveness
   - Technical feasibility depth
   - UX research integration
   - Industry standards coverage

2. **Strategic Clarity Score** (1-10):
   - Problem/solution alignment
   - Success metrics definition
   - Implementation feasibility
   - Risk mitigation completeness

3. **User-Centric Design Score** (1-10):
   - User journey mapping quality
   - Persona definition clarity
   - Accessibility considerations
   - Usability validation approach

4. **Technical Viability Score** (1-10):
   - Architecture design soundness
   - Technology stack appropriateness
   - Scalability considerations
   - Integration complexity assessment

5. **Implementation Readiness Score** (1-10):
   - Phase breakdown clarity
   - Resource requirement accuracy
   - Timeline realism
   - Success measurement definition

Generate detailed quality scorecard with specific recommendations for improvement.
Target: 8+ on all metrics through enhanced parallel research methodology.
Save assessment to .planning_research_coordination/quality_scorecard.md" \
  --allowedTools "Read,Write" \
  --max-turns 12 > quality_assessment.json
```

### Stakeholder Review Preparation

```bash
# Generate stakeholder review package
claude -p "Create stakeholder review package for the PRD including:

1. **Executive Briefing** (1-page summary)
   - Key findings and recommendations
   - Resource requirements and timeline
   - Risk assessment and mitigation
   - Success metrics and ROI projection

2. **Technical Review Checklist**
   - Architecture validation points
   - Technology stack approval items
   - Integration complexity assessment
   - Performance requirement verification

3. **Implementation Action Plan**
   - Immediate next steps
   - Resource allocation requirements
   - Key decision points and timelines
   - Success milestone definitions

Save review package to .planning_research_coordination/stakeholder_review_package.md" \
  --allowedTools "Read,Write" \
  --max-turns 10 > stakeholder_package.json
```

## Alternative Execution Strategies

### Git Worktrees for Deep Research

```bash
# For complex planning requiring isolated research environments
git worktree add ../planning-market-research main
git worktree add ../planning-technical-research main  
git worktree add ../planning-ux-research main
git worktree add ../planning-compliance-research main

echo "For deep research isolation, launch agents in separate terminals:"
echo "Terminal 1: cd ../planning-market-research && claude # Market intelligence"
echo "Terminal 2: cd ../planning-technical-research && claude # Technical feasibility"
echo "Terminal 3: cd ../planning-ux-research && claude # UX patterns"
echo "Terminal 4: cd ../planning-compliance-research && claude # Standards & compliance"

# Cleanup script
cat > cleanup_planning_worktrees.sh << 'EOF'
#!/bin/bash
git worktree remove ../planning-market-research
git worktree remove ../planning-technical-research
git worktree remove ../planning-ux-research
git worktree remove ../planning-compliance-research
echo "Planning research worktrees cleaned up"
EOF
chmod +x cleanup_planning_worktrees.sh
```

### Error Recovery & Resilience

```bash
# Health check and agent recovery
for agent_type in market technical ux compliance; do
  output_file="${agent_type}_agent_output.json"
  if ! jq -e . "$output_file" >/dev/null 2>&1; then
    echo "Agent $agent_type failed - initiating recovery..."
    claude -p "Resume planning research for $agent_type aspects of '$ARGUMENTS' - continue where previous attempt left off.
    Focus on comprehensive research and write findings to .planning_research_coordination/${agent_type}_*.md" \
      --output-format stream-json \
      --max-turns 12 \
      --allowedTools "WebSearch,WebFetch,Write" \
      > "${agent_type}_agent_recovery.json" &
  fi
done
```

## Deliverable Package & Cleanup

### Comprehensive Output Organization

```bash
# Create planning deliverable package
mkdir -p "PRPs/planning-research-$(date +%Y%m%d)-$ARGUMENTS"
cp .planning_research_coordination/* "PRPs/planning-research-$(date +%Y%m%d)-$ARGUMENTS/"
cp *_agent_output.json "PRPs/planning-research-$(date +%Y%m%d)-$ARGUMENTS/" 2>/dev/null

# Generate delivery summary
cat > "PRPs/planning-research-$(date +%Y%m%d)-$ARGUMENTS/delivery_summary.md" << EOF
# Planning Research Delivery Summary

**Project**: $ARGUMENTS
**Generated**: $(date)
**Method**: Enhanced parallel research with Claude Code headless mode

## Deliverables

1. **Primary PRD**: PRPs/$ARGUMENTS-planning-prd.md
2. **Research Findings**: 4 parallel research streams
3. **Quality Assessment**: Comprehensive validation scorecard
4. **Stakeholder Package**: Review materials and action plan

## Research Quality Metrics

- **Parallel Execution**: 4 concurrent research agents
- **Time Efficiency**: ~4x faster than sequential research
- **Depth**: Multi-angle comprehensive analysis
- **Integration**: Cross-research synthesis and validation

## Next Steps

1. Stakeholder review of PRD
2. User validation and feedback incorporation
3. Implementation PRP creation using /prp command
4. Development planning and sprint creation
EOF
```

### Cleanup & Archive

```bash
# Clean up temporary files
rm -f *_agent_output.json *_agent_recovery.json
rm -f planning_synthesis.json prd_generation.json quality_assessment.json
rm -f user_questions.json diagram_generation.json stakeholder_package.json
rm -rf .planning_research_coordination

echo "$(date): Enhanced parallel planning PRP creation completed for: $ARGUMENTS"
echo "Primary deliverable: PRPs/$ARGUMENTS-planning-prd.md"
echo "Research package: PRPs/planning-research-$(date +%Y%m%d)-$ARGUMENTS/"
echo "Ready for stakeholder review and implementation planning"
```

## Success Metrics & Quality Gates

### Target Performance Indicators

- **Research Comprehensiveness**: 4 specialized research streams
- **Time Efficiency**: 4x faster through parallel execution
- **Quality Scores**: 8+ across all validation metrics
- **Implementation Readiness**: Complete PRD with actionable plans
- **Stakeholder Preparation**: Review package and action plan ready

### Quality Validation Checklist

- [ ] All 4 research agents completed successfully
- [ ] Market intelligence comprehensive with competitive analysis
- [ ] Technical feasibility thoroughly assessed with recommendations
- [ ] UX patterns researched with actionable design guidance
- [ ] Industry standards and compliance requirements documented
- [ ] Research synthesis completed and validated
- [ ] PRD generated with all required sections and diagrams
- [ ] Quality scores 8+ across all assessment categories
- [ ] Stakeholder review package prepared
- [ ] Implementation readiness confirmed

---

**Remember**: This enhanced planning command leverages Claude Code's headless mode for true parallel research execution, comprehensive synthesis, and quality validation. The goal is creating actionable, well-researched PRDs that enable successful implementation planning and execution.
