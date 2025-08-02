# Create Enhanced BASE PRP with Context Engineering

## Feature: $ARGUMENTS

Generate a complete PRP using **enhanced context engineering principles** for feature implementation with security-first design and comprehensive validation. Ensure rich, systematic context is passed to enable production-ready code generation on the first pass.

The AI agent only gets the context you are appending to the PRP and its own training data. Assume the AI agent has
access to the codebase and the same knowledge cutoff as you, so its important that your research findings are included
or referenced in the PRP. The Agent has Websearch capabilities, so pass urls to documentation and examples.

## Research Process

> During the research process, create clear tasks and spawn as many agents and subagents as needed using the batch
tools. The deeper research we do here the better the PRP will be. we optminize for chance of success and not for speed.

1. **Codebase Analysis in depth**
   - Create clear todos and spawn subagents to search the codebase for similar features/patterns Think hard and plan
     your approach
   - Identify all the necessary files to reference in the PRP
   - Note all existing conventions to follow
   - Check existing test patterns for validation approach
   - Use the batch tools to spawn subagents to search the codebase for similar features/patterns

2. **External Research at scale**
   - Create clear todos and spawn with instructions subagents to do deep research for similar features/patterns online
     and include urls to documentation and examples
   - Library documentation (include specific URLs)
   - For critical pieces of documentation add a .md file to PRPs/ai_docs and reference it in the PRP with clear
     reasoning and instructions
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls found during research
   - Use the batch tools to spawn subagents to search for similar features/patterns online and include urls to
     documentation and examples

3. **User Clarification**
   - Ask for clarification if you need it

## Enhanced PRP Generation

**Choose Enhanced Template Based on Complexity:**

- **Standard Features**: Use `PRPs/templates/prp_base.md` (enhanced with security-first design)
- **Complex Features**: Use `PRPs/templates/prp_base_enhanced.md` (prescriptive with context engineering)

**CRITICAL: Reference Enhanced AI Documentation System:**

### Enhanced Context Engineering Requirements

**MANDATORY: Include Enhanced AI Documentation References:**
```yaml
- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server implementation patterns with Python/async"
  sections: ["Core Principles", "Error Handling", "Security Patterns"]

- file: PRPs/ai_docs/database-integration-patterns.md
  why: "Async database patterns with SQLite/aiosqlite" 
  sections: ["Connection Management", "Security Patterns", "Error Handling"]

- file: PRPs/ai_docs/security-patterns.md
  why: "Security validation and protection patterns"
  sections: ["Input Validation", "Error Sanitization", "Authentication"]

- file: PRPs/ai_docs/context-engineering-guide.md
  why: "Context engineering methodology and best practices"
  sections: ["Context Engineering Principle", "Validation Framework"]
```

**Additional Critical Context:**
- **Security Requirements**: Authentication, authorization, input validation, error sanitization
- **Code Examples**: Real snippets from codebase with security considerations
- **Gotchas & Security**: Library quirks, version issues, security pitfalls
- **Patterns**: Existing approaches with security integration
- **Validation Patterns**: Reference PRPs/validation/ for comprehensive testing

### Implementation Blueprint

- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- List tasks to be completed to fulfill the PRP in the order they should be completed, use the pattern in the PRP with
  information dense keywords

### Enhanced Multi-Stage Validation Framework (Must be Executable by AI agent)

**CRITICAL: Implement 5-Stage Validation (reference PRPs/validation/validation-framework.md):**

```bash
# Stage 1: Syntax & Security Validation
ruff check . --fix && mypy src/ && bandit -r src/ && safety check

# Stage 2: Unit Testing with Security Focus
pytest tests/unit/ -v --cov=src --cov-fail-under=80 -m security

# Stage 3: Integration & Database Testing
pytest tests/integration/ -v && python scripts/validate_database_schema.py

# Stage 4: Security & Performance Validation  
python scripts/security_audit.py && python scripts/performance_benchmark.py

# Stage 5: Production Readiness Validation
python scripts/e2e_validation.py && python scripts/production_readiness_check.py
```

**Security-Specific Validation Requirements:**
- XSS prevention testing in all text inputs
- SQL injection prevention in database operations
- Path traversal prevention in file operations
- Error message sanitization verification
- Authentication/authorization testing

**_ CRITICAL AFTER YOU ARE DONE RESEARCHING AND EXPLORING THE CODEBASE BEFORE YOU START WRITING THE PRP _**

**_ ULTRATHINK ABOUT THE PRP AND PLAN YOUR APPROACH IN DETAILED TODOS THEN START WRITING THE PRP _**

## Output

Save as: `PRPs/{feature-name}.md`

## Enhanced Quality Checklist

### Context Engineering Validation
- [ ] All enhanced AI documentation referenced (ai_docs/)
- [ ] Security-first design integrated throughout
- [ ] Prescriptive implementation with file paths and line numbers
- [ ] Context completeness verified using PRPs/ai_docs/context-engineering-guide.md

### Security Integration
- [ ] Input validation requirements specified
- [ ] Authentication/authorization requirements defined
- [ ] Error sanitization requirements documented
- [ ] Security testing requirements included

### Multi-Stage Validation
- [ ] All 5 validation stages implemented and executable
- [ ] Security validation gates included
- [ ] Performance benchmarks specified
- [ ] Production readiness criteria defined

### Pattern Integration
- [ ] References existing patterns from PRPs/patterns/
- [ ] Clear implementation path with security considerations
- [ ] Error handling with security-safe messages documented

**Context Engineering Score**: Rate 1-10 for context completeness and engineering quality
**Security Integration Score**: Rate 1-10 for security-first design integration  
**Overall Confidence Score**: Rate 1-10 for one-pass implementation success

Remember: The goal is one-pass implementation success through comprehensive context.
