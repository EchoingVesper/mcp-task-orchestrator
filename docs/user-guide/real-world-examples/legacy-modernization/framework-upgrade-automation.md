# Framework Migration Automation
*Large-scale dependency upgrades with automated testing validation*

## 🎯 Project Overview
**Scenario**: Upgrade a React 16 application to React 18 across 150+ components
**Challenge**: Breaking changes detection, automated code transformation, comprehensive testing
**Tools**: Task Orchestrator MCP + Claude Code MCP + AST transformation tools

## 🔄 Workflow Coordination
```bash
orchestrator_plan_task({
  "description": "Migrate React 16 to React 18 with comprehensive validation",
  "subtasks_json": "[{
    \"title\": \"Breaking Changes Analysis\",
    \"specialist_type\": \"analyzer\"
  }, {
    \"title\": \"Automated Code Transformation\",
    \"specialist_type\": \"implementer\"
  }, {
    \"title\": \"Test Suite Migration and Validation\",
    \"specialist_type\": \"tester\"
  }]"
})
```

## 🔄 Key Coordination Patterns
**Orchestrator Role**: Migration strategy and validation checkpoints
**Claude Code Role**: File analysis, code transformation, test execution

```bash
# Breaking changes detection
search_code: "componentWillMount|componentWillReceiveProps" --include="*.jsx"
read_multiple_files: [package.json, jest.config.js, webpack.config.js]

# Automated transformation
execute_command: npx react-codemod update-react-imports src/
execute_command: npx @typescript-eslint/eslint-plugin --fix src/

# Validation pipeline
execute_command: npm test -- --coverage --watchAll=false
execute_command: npm run build
```

## 🏆 Success Metrics
- **Automation Rate**: 87% of changes automated, 13% manual review
- **Test Coverage**: Maintained 95%+ coverage throughout migration
- **Migration Time**: 2-week timeline vs. 6-week manual estimate

---
*⚡ Shows how orchestration accelerates complex technical migrations*