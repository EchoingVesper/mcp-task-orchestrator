# Execute Enhanced BASE PRP with Context Engineering

Implement a feature using the enhanced PRP file with security-first design and multi-stage validation.

## PRP File: $ARGUMENTS

## Pre-Execution Orchestrator Check

**MANDATORY:**

```bash
# Verify orchestrator connection
claude mcp list | grep task-orchestrator || (echo "FIXING ORCHESTRATOR..." && claude mcp restart task-orchestrator)

# If orchestrator fails, STOP and follow CLAUDE.md protocol
# DO NOT PROCEED without working orchestrator
```

## Execution Process

1. **Load Enhanced PRP**
   - Read the specified PRP file
   - **CRITICAL**: Load referenced enhanced AI documentation from PRPs/ai_docs/
   - Understand all context, requirements, and security considerations
   - Follow all instructions including security-first design principles
   - Ensure you have all context from ai_docs/, validation/, and patterns/
   - Do additional research if needed, referencing context engineering guide

2. **ULTRATHINK**
   - Ultrathink before you execute the plan. Create a comprehensive plan addressing all requirements.
   - Break down the PRP into clear todos using the TodoWrite tool.
   - Use agents subagents and batchtool to enhance the process.
   - **Important** ENSURE CLEAR TASKS FOR SUBAGENTS WITH CONTEXT
   - Each subagent MUST read the PRP and understand its context
   - Identify implementation patterns from existing code to follow.
   - Never guess about imports, file names funtion names etc, ALWAYS be based in reality and real context gathering

3. **Execute the plan**
   - Execute the PRP step by step
   - Implement all the code
   - Use orchestrator_execute_task for complex subtasks
   - Track progress with orchestrator_get_status

4. **Enhanced Multi-Stage Validation**
   - **Stage 1**: Syntax & Security (ruff, mypy, bandit, safety)
   - **Stage 2**: Unit Testing with Security Focus (XSS, injection, authorization tests)
   - **Stage 3**: Integration & Database Testing (real component validation)
   - **Stage 4**: Security & Performance Validation (audit, benchmarks)
   - **Stage 5**: Production Readiness (end-to-end, deployment validation)
   - Fix any failures at each stage before proceeding
   - Reference PRPs/validation/ for detailed validation procedures
   - Always re-read PRP and security requirements to ensure compliance

5. **Complete with Security Validation**
   - Ensure all enhanced checklist items completed
   - Verify security requirements implemented (input validation, error sanitization, etc.)
   - Run complete validation suite with all 5 stages
   - Confirm context engineering scores meet quality thresholds
   - Report completion status with security posture assessment
   - Read PRP again to ensure everything implemented including security

6. **Enhanced Context Reference**
   - Reference PRP and all enhanced documentation (ai_docs/, validation/, patterns/)
   - Use context engineering guide for systematic validation
   - Apply security patterns for any additional requirements

7. **Git Commit on Completion**
   - ALWAYS commit changes after successful implementation
   - Use descriptive commit message from PRP
   - Never leave uncommitted work

**Note**: Enhanced validation includes security-first design. If validation fails:
- Reference PRPs/validation/ for debugging procedures
- If orchestrator fails, STOP and fix per CLAUDE.md protocol
