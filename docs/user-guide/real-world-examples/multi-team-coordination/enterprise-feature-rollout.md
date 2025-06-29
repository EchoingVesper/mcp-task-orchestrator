# Enterprise Feature Release Coordination
*⭐ Featured Example: Multi-team payment system integration across 5 services*

## 🎯 Project Overview
**Scenario**: Implement new payment processing across Frontend, API Gateway, Payment Service, User Service, and Analytics teams
**Challenge**: Shared API contracts, database migrations, security compliance, staged rollout
**Tools**: Task Orchestrator MCP + Claude Code MCP + Team-specific toolchains

## 🔄 Sequential Coordination Pattern
```bash
orchestrator_plan_task({
  "description": "Deploy payment system v2 across 5 teams with zero downtime",
  "complexity_level": "very_complex",
  "subtasks_json": "[{
    \"title\": \"API Contract Definition and Validation\",
    \"specialist_type\": \"architect\"
  }, {
    \"title\": \"Parallel Development Coordination\",
    \"specialist_type\": \"implementer\"
  }]"
})
```

## 🔄 Multi-Team Coordination Patterns
**Orchestrator Role**: Facilitates cross-team API contract negotiation
**Claude Code Role**: API schema validation, documentation generation
```bash
# Contract definition and validation
read_file: api-contracts/payment-v2.openapi.yml
execute_command: swagger-codegen validate api-contracts/payment-v2.openapi.yml
write_file: team-contracts/frontend-requirements.md

# Frontend Team (React/TypeScript)
create_directory: frontend/src/payment-v2/
write_file: frontend/src/payment-v2/PaymentForm.tsx

# Backend Teams (Java/Spring)
create_directory: payment-service/src/main/java/v2/
write_file: payment-service/src/main/java/v2/PaymentController.java

# Database Migration Coordination
execute_command: liquibase --context=payment-v2 update
```

## 🏆 Success Patterns
- **Contract-First Development**: API contracts established before implementation
- **Parallel Execution**: Teams work independently with orchestrated checkpoints

---
*👥 Demonstrates Large-scale team coordination with minimal conflicts*