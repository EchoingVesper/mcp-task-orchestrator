# Architecture Documentation - Claude Code Guide

Architectural documentation guidance for the MCP Task Orchestrator's design decisions and technical records.

## Architecture Documentation

**Design Records**: System architecture, design decisions, and technical documentation.

### Architecture Areas
- System design and component relationships
- Database schema and persistence architecture
- MCP protocol integration patterns
- Enhanced feature architecture (artifacts, maintenance, testing)
- Decision records and rationale

## Architecture Context Commands

### Design Documentation
```bash
# Review current architecture
find . -name "*.md" -exec echo "=== {} ===" \; -exec head -10 {} \;

# Check decision records
grep -r "Decision:" . --include="*.md"

# Validate architecture consistency
grep -r "Architecture" ../docs/ --include="*.md"
```

### Integration Analysis
```bash
# Component relationship analysis
tree -I "__pycache__|*.pyc" -L 2

# Cross-reference architecture decisions
grep -r "$(basename $PWD)" ../docs/ ../README.md
```

## Architecture Documentation Patterns

### Decision Records
- **Context**: Problem statement and constraints
- **Decision**: What was decided and why
- **Consequences**: Trade-offs and implications
- **Alternatives**: Options considered but not chosen

---

**Architecture Records**: This directory contains system design decisions and technical architecture documentation.
