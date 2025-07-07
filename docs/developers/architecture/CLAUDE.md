

# Architecture Documentation - Claude Code Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Architecture Files in THIS Directory Exceeding Limits**:

- `database-schema-enhancements.md` (694 lines) - HIGH RISK

- `nested-task-architecture.md` (554 lines) - MEDIUM RISK

**Architecture Documentation Best Practices**:

1. Split large architecture docs by component or layer

2. Use separate files for diagrams and detailed specs

3. Create overview files that link to detailed docs

4. Keep decision records concise (under 300 lines)

5. Use appendices for lengthy technical details
</critical_file_size_warning>

<architecture_context_analysis>
You are working with architectural documentation and design decisions. Before proceeding:

1. **Understand Documentation Type**: System design, decision records, or technical specifications?

2. **Identify Stakeholders**: Who will read and use this architectural documentation?

3. **Assess Decision Impact**: Does this affect system design, component relationships, or future development?

4. **Check Consistency**: How does this align with existing architectural decisions?

5. **Consider Long-term Implications**: What are the maintenance and evolution impacts?
</architecture_context_analysis>

Architectural documentation guidance for the MCP Task Orchestrator's design decisions and technical records.

#

# Architecture Decision Framework

<architecture_decision_reasoning>
**Structured Approach to Architecture Decisions**:

**Decision Record Components**:

1. **Context**: What is the problem or situation requiring a decision?

2. **Decision**: What specific choice was made and why?

3. **Alternatives**: What other options were considered but not chosen?

4. **Consequences**: What are the trade-offs, benefits, and implications?

5. **Status**: Proposed, accepted, deprecated, or superseded?

**Documentation Strategy**:

- **Problem-First**: Start with clear problem statement and constraints

- **Solution-Focused**: Explain what was decided, not just what was implemented

- **Future-Aware**: Consider how decisions affect system evolution

- **Stakeholder-Oriented**: Write for future developers and maintainers

**Decision Process**:

1. **Analyze Problem**: What architectural challenge needs resolution?

2. **Research Options**: What are the viable approaches and trade-offs?

3. **Evaluate Impact**: How does each option affect system qualities?

4. **Make Decision**: Choose approach based on requirements and constraints

5. **Document Rationale**: Record decision with full context and reasoning

6. **Monitor Outcomes**: Track how decision performs in practice

**Integration with Development**:

- Link architectural decisions to implementation choices

- Update documentation when decisions are revisited

- Cross-reference related decisions and dependencies

- Maintain decision history and evolution
</architecture_decision_reasoning>

#

# Architecture Documentation

**Design Records**: System architecture, design decisions, and technical documentation.

#

## Architecture Areas

- System design and component relationships

- Database schema and persistence architecture

- MCP protocol integration patterns

- Enhanced feature architecture (artifacts, maintenance, testing)

- Decision records and rationale

#

# Architecture Context Commands

#

## Design Documentation

```bash

# Review current architecture

find . -name "*.md" -exec echo "=== {} ===" \; -exec head -10 {} \;

# Check decision records

grep -r "Decision:" . --include="*.md"

# Validate architecture consistency

grep -r "Architecture" ../docs/ --include="*.md"

```text

#

## Integration Analysis

```text
bash

# Component relationship analysis

tree -I "__pycache__|*.pyc" -L 2

# Cross-reference architecture decisions

grep -r "$(basename $PWD)" ../docs/ ../README.md
```text

#

# Architecture Documentation Patterns

#

## Decision Records

- **Context**: Problem statement and constraints

- **Decision**: What was decided and why

- **Consequences**: Trade-offs and implications

- **Alternatives**: Options considered but not chosen

---

**Architecture Records**: This directory contains system design decisions and technical architecture documentation.
