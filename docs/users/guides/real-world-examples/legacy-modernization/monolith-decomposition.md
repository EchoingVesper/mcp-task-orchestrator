

# Monolith to Microservices Decomposition

*⭐ Featured Example: Safe extraction of user service from e-commerce monolith*

#

# 🎯 Project Overview

**Scenario**: Extract user management functionality from 200,000+ line e-commerce monolith
**Challenge**: Zero-downtime migration, data consistency, API compatibility, rollback safety
**Tools**: Task Orchestrator MCP + Claude Code MCP + Database tools + Deployment automation

#

# 🔄 Sequential Coordination Pattern

```bash
orchestrator_plan_task({
  "description": "Extract user service from e-commerce monolith with zero downtime",
  "complexity_level": "very_complex",
  "subtasks_json": "[{
    \"title\": \"Codebase Analysis and Dependency Mapping\",
    \"specialist_type\": \"architect\"
  }, {
    \"title\": \"Service Boundary Definition and API Design\",
    \"specialist_type\": \"architect\"
  }, {
    \"title\": \"Database Schema Extraction Planning\",
    \"specialist_type\": \"database_specialist\"
  }]"
})

```text

#

# 🔄 Key Coordination Patterns

**Orchestrator Role**: Provides architectural analysis specialist context
**Claude Code Role**: File analysis, dependency discovery, impact assessment

```text
bash

# Comprehensive codebase analysis

search_code: "User" --include="*.java" --context-lines=3
read_multiple_files: [UserController.java, UserService.java, UserRepository.java]
execute_command: java-dependency-analyzer --target=User --output=dependencies.json

# Create new service structure (Strangler Fig pattern)

create_directory: user-service/
write_file: user-service/src/main/java/UserServiceApplication.java
execute_command: mvn clean test
```text
text

#

# 🏆 Success Patterns

- **Strangler Fig**: Gradual replacement without breaking existing functionality

- **Feature Toggles**: Safe rollout with instant rollback capability

- **Database Per Service**: Clean data separation with migration safety

- **API Versioning**: Backward compatibility during transition

---
*🔧 Demonstrates Large-scale modernization with orchestrated safety*
