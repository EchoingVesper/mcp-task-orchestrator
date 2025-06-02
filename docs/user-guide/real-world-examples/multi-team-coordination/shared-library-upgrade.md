# Shared Library Migration Coordination
*Coordinated dependency upgrades across 15+ microservices*

## 🎯 Project Overview
**Scenario**: Upgrade shared authentication library across 15 microservices owned by 6 different teams
**Challenge**: Breaking changes, team coordination, rollback safety, dependency conflicts
**Tools**: Task Orchestrator MCP + Claude Code MCP + CI/CD pipelines

## 🔄 Workflow Coordination
```bash
orchestrator_plan_task({
  "description": "Coordinate auth library v3 upgrade across all microservices",
  "complexity_level": "complex",
  "subtasks_json": "[{
    \"title\": \"Breaking Changes Impact Analysis\",
    \"specialist_type\": \"analyzer\"
  }, {
    \"title\": \"Team Migration Planning and Scheduling\",
    \"specialist_type\": \"coordinator\"
  }, {
    \"title\": \"Automated Migration Tool Development\",
    \"specialist_type\": \"implementer\"
  }]"
})
```

## 🔄 Multi-Team Coordination Patterns
**Orchestrator Role**: Manages team dependencies and migration scheduling
**Claude Code Role**: Code analysis, automated transformations, validation

```bash
# Impact analysis across all services
search_code: "AuthLibrary|auth-lib" --include="*.java,*.kt,*.scala"
read_multiple_files: [service-*/pom.xml, service-*/build.gradle]

# Automated migration tool
write_file: migration-tools/auth-lib-migrator.py
execute_command: python migration-tools/auth-lib-migrator.py --service=user-service --dry-run

# Team-specific validation
execute_command: mvn test -Dtest=AuthIntegrationTest
```

## 🏆 Coordination Success Patterns
- **Impact Analysis**: Automated dependency scanning and breaking change detection
- **Phased Rollout**: Team-by-team migration with validation gates
- **Rollback Safety**: Automated reversion capabilities at each checkpoint

---
*📦 Shows coordinated dependency management across organizational boundaries*