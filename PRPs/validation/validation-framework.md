
# Multi-Stage Validation Framework

**Purpose**: Comprehensive 5-stage validation framework for enhanced PRP implementations, ensuring code quality, security, performance, and production readiness before deployment.

#
# Framework Philosophy

#
## Shift-Left Validation Principle

**"Catch issues early, validate continuously, deploy confidently"**

The multi-stage validation framework implements a "shift-left" approach to quality assurance, catching defects as early as possible in the development cycle. Each stage builds upon the previous, creating a comprehensive quality gate system.

#
## Validation Stage Architecture

```yaml
VALIDATION_STAGES:
  stage_1_syntax_security:
    purpose: "Catch syntax errors and security vulnerabilities immediately"
    blocking: true  
# Must pass before proceeding
    
  stage_2_unit_testing:
    purpose: "Validate individual component functionality and security"
    blocking: true  
# Must pass before proceeding
    
  stage_3_integration:
    purpose: "Validate component interactions and database operations"
    blocking: true  
# Must pass before proceeding
    
  stage_4_security_performance:
    purpose: "Comprehensive security audit and performance validation"
    blocking: true  
# Must pass before proceeding
    
  stage_5_production_readiness:
    purpose: "End-to-end validation and deployment readiness"
    blocking: false  
# Advisory, can proceed with warnings

```text

#
# Stage 1: Syntax & Security Validation

#
## Purpose

Immediate validation of code syntax, type safety, and basic security vulnerabilities.

#
## Commands and Expected Outputs

```text
bash

# SYNTAX VALIDATION

ruff check . --fix                    
# Python code formatting and linting

# Expected: All auto-fixable issues resolved, no remaining linting errors

mypy src/                            
# Static type checking

# Expected: No type errors, all function signatures properly typed

# SECURITY VALIDATION  

bandit -r src/ -f json               
# Security vulnerability scanning

# Expected: No high or medium severity security issues

safety check --json                 
# Dependency vulnerability scanning  

# Expected: No known security vulnerabilities in dependencies

# CONFIGURATION VALIDATION

python scripts/validate_config.py   
# Configuration file validation

# Expected: All configuration files valid, no missing required settings

```text

#
## Failure Handling

```python

# PATTERN: Stage 1 validation with automated fixes

class Stage1Validator:
    """Handles syntax and security validation with automated fixes."""
    
    def __init__(self):
        self.results = {}
        self.auto_fixes_applied = []
    
    async def validate_syntax(self) -> bool:
        """Run syntax validation with auto-fixes."""
        try:
            
# Run ruff with auto-fix
            result = await self._run_command("ruff check . --fix")
            if result.returncode == 0:
                self.results["ruff"] = {"status": "passed", "auto_fixes": True}
                return True
            else:
                self.results["ruff"] = {"status": "failed", "errors": result.stderr}
                return False
                
        except Exception as e:
            self.results["ruff"] = {"status": "error", "message": str(e)}
            return False
    
    async def validate_security(self) -> bool:
        """Run security validation."""
        try:
            
# Run bandit security scan
            result = await self._run_command("bandit -r src/ -f json")
            
            if result.returncode == 0:
                
# Parse results to check severity
                issues = self._parse_bandit_results(result.stdout)
                high_severity = [i for i in issues if i["severity"] == "HIGH"]
                
                if high_severity:
                    self.results["security"] = {
                        "status": "failed", 
                        "high_severity_issues": len(high_severity),
                        "issues": high_severity
                    }
                    return False
                else:
                    self.results["security"] = {"status": "passed"}
                    return True
            else:
                self.results["security"] = {"status": "error", "message": result.stderr}
                return False
                
        except Exception as e:
            self.results["security"] = {"status": "error", "message": str(e)}
            return False

```text

#
# Stage 2: Unit Testing with Security Focus

#
## Purpose

Validate individual component functionality with emphasis on security test cases.

#
## Commands and Expected Outputs

```text
bash

# UNIT TEST EXECUTION

pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80

# Expected: All tests pass, >80% code coverage, no security test failures

pytest tests/unit/ -m "security" -v  
# Security-specific unit tests

# Expected: All security tests pass, input validation works correctly

pytest tests/unit/ -k "test_error_handling" -v  
# Error handling tests

# Expected: All error scenarios handled securely, no information disclosure

```text

#
## Security Test Requirements

```python

# PATTERN: Comprehensive security unit tests

class SecurityTestSuite:
    """Required security tests for all features."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_input_validation_xss_prevention(self):
        """Test XSS attack prevention in user inputs."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "onload=alert('xss')",
            "<object data='javascript:alert(1)'></object>",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises((ValidationError, ValueError)):
                await your_feature_function(title=malicious_input)
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_sql_injection_prevention(self):
        """Test SQL injection prevention in database operations."""
        malicious_queries = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT password FROM users --",
            "'; INSERT INTO users (admin) VALUES (1); --"
        ]
        
        for malicious_query in malicious_queries:
            
# Should not raise database errors, should be safely parameterized
            result = await your_database_function(search_term=malicious_query)
            assert result is not None  
# Function completes safely
            
# Verify no unauthorized data access occurred
    
    @pytest.mark.asyncio
    @pytest.mark.security  
    async def test_path_traversal_prevention(self):
        """Test path traversal prevention in file operations."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "~/.ssh/id_rsa",
            "file://../../sensitive_file"
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises((ValueError, SecurityError)):
                await your_file_function(file_path=malicious_path)
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information."""
        
# Simulate various error conditions
        with patch('database.execute') as mock_db:
            mock_db.side_effect = Exception("Database error: user='admin' password='secret123' host='internal-db'")
            
            try:
                await your_function("valid_input")
            except Exception as e:
                error_message = str(e).lower()
                
                
# SECURITY: Ensure no sensitive information in error
                assert "password" not in error_message
                assert "secret123" not in error_message
                assert "admin" not in error_message
                assert "internal-db" not in error_message
                
# Should be generic message like "Database operation failed"

```text

#
## Coverage Requirements

```text
yaml
COVERAGE_REQUIREMENTS:
  overall_coverage: ">= 80%"
  security_functions: ">= 95%"  
# Security-critical functions need higher coverage
  input_validation: "100%"      
# All validation paths must be tested
  error_handling: ">= 90%"      
# Error scenarios must be thoroughly tested
  
REQUIRED_TEST_CATEGORIES:
  - Happy path functionality tests
  - Input validation security tests  
  - Error handling security tests
  - Authorization and authentication tests
  - Database security tests (if applicable)
  - File operation security tests (if applicable)

```text

#
# Stage 3: Integration & Database Testing

#
## Purpose

Validate component interactions, database operations, and MCP protocol compliance.

#
## Commands and Expected Outputs

```text
bash

# INTEGRATION TEST EXECUTION

pytest tests/integration/ -v                    
# Full integration test suite

# Expected: All integration tests pass, components interact correctly

python scripts/validate_database_schema.py      
# Database schema validation

# Expected: Database schema matches expected structure, migrations applied

python scripts/test_mcp_protocol_compliance.py  
# MCP protocol validation

# Expected: MCP tools registered correctly, protocol compliance verified

# DATABASE INTEGRATION TESTING

pytest tests/integration/test_database.py -v    
# Database-specific integration tests

# Expected: Database connections managed properly, transactions work correctly

```text

#
## Integration Test Patterns

```python

# PATTERN: Integration testing with real components

class IntegrationTestSuite:
    """Integration tests with real database and MCP components."""
    
    @pytest.fixture
    async def test_database(self):
        """Create isolated test database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            db_url = f"sqlite:///{temp_db.name}"
            
            repository = SQLiteTaskRepository(db_url)
            
            
# Initialize test schema
            migration_manager = MigrationManager(db_url)
            await migration_manager.run_migrations()
            
            yield repository
            
            
# Cleanup
            await repository.async_engine.dispose()
            os.unlink(temp_db.name)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_task_creation(self, test_database):
        """Test complete task creation workflow."""
        
# Test the full flow: MCP handler -> Use case -> Repository -> Database
        
        
# 1. Create task through MCP handler
        mcp_arguments = {
            "title": "Integration Test Task",
            "description": "Test task for integration testing",
            "priority": "high"
        }
        
        result = await handle_create_task(mcp_arguments)
        
        
# 2. Verify MCP response format
        assert len(result) == 1
        assert result[0].type == "text"
        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        task_id = response_data["task_id"]
        
        
# 3. Verify task was created in database
        created_task = await test_database.get_task(task_id)
        assert created_task is not None
        assert created_task.title == "Integration Test Task"
        assert created_task.priority == TaskPriority.HIGH
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_transaction_rollback(self, test_database):
        """Test database transaction rollback on errors."""
        
# Test that failed operations don't leave partial data
        
        with pytest.raises(Exception):
            async with test_database.get_session() as session:
                
# Create task
                task_record = TaskModel(
                    task_id="test-rollback",
                    title="Test Task",
                    description="Test Description"
                )
                session.add(task_record)
                await session.flush()
                
                
# Simulate error that should cause rollback
                raise Exception("Simulated error")
        
        
# Verify task was not saved due to rollback
        task = await test_database.get_task("test-rollback")
        assert task is None
    
    @pytest.mark.asyncio
    @pytest.mark.integration  
    async def test_mcp_tool_registration(self):
        """Test MCP tool registration and availability."""
        from src.infrastructure.mcp.tool_definitions import get_all_tools
        
        tools = get_all_tools()
        
        
# Verify our tools are registered
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "orchestrator_initialize_session",
            "orchestrator_plan_task", 
            "orchestrator_execute_task"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        
# Verify tool schemas are valid
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            
# Verify schema is valid JSON Schema
            jsonschema.validate({}, tool.inputSchema)  
# Should not raise

```text

#
# Stage 4: Security & Performance Validation

#
## Purpose

Comprehensive security audit and performance benchmarking.

#
## Commands and Expected Outputs

```text
bash

# SECURITY VALIDATION

python scripts/security_audit.py               
# Custom security audit

# Expected: No high-severity security issues found

pytest tests/security/ -v                      
# Security integration tests

# Expected: All security integration tests pass

python scripts/penetration_test.py             
# Basic penetration testing

# Expected: No successful penetration attempts

# PERFORMANCE VALIDATION

python scripts/performance_benchmark.py        
# Performance benchmarks

# Expected: All performance metrics within acceptable ranges

locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 60s

# Expected: System handles expected load without degradation

python scripts/memory_leak_test.py             
# Memory leak detection

# Expected: No memory leaks detected during extended operation

```text

#
## Security Audit Framework

```python

# PATTERN: Comprehensive security audit framework

class SecurityAuditor:
    """Comprehensive security audit for PRP implementations."""
    
    def __init__(self):
        self.findings = []
        self.severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    
    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run complete security audit."""
        audit_results = {
            "input_validation": await self._audit_input_validation(),
            "authentication": await self._audit_authentication(),
            "authorization": await self._audit_authorization(), 
            "data_protection": await self._audit_data_protection(),
            "error_handling": await self._audit_error_handling(),
            "logging_security": await self._audit_logging_security(),
            "dependency_security": await self._audit_dependencies(),
            "configuration_security": await self._audit_configuration()
        }
        
        
# Calculate overall security score
        total_findings = sum(self.severity_counts.values())
        high_severity = self.severity_counts["HIGH"]
        medium_severity = self.severity_counts["MEDIUM"]
        
        
# Security score calculation (0-100)
        security_score = max(0, 100 - (high_severity * 20) - (medium_severity * 5))
        
        return {
            "security_score": security_score,
            "severity_counts": self.severity_counts,
            "audit_results": audit_results,
            "findings": self.findings,
            "passed": high_severity == 0 and security_score >= 80
        }
    
    async def _audit_input_validation(self) -> Dict[str, Any]:
        """Audit input validation implementation."""
        findings = []
        
        
# Check for Pydantic validation in all MCP handlers
        handler_files = glob.glob("src/infrastructure/mcp/handlers/*.py")
        
        for handler_file in handler_files:
            with open(handler_file, 'r') as f:
                content = f.read()
                
                
# Check for proper validation patterns
                if "BaseModel" not in content and "validate" not in content:
                    findings.append({
                        "severity": "HIGH",
                        "file": handler_file,
                        "issue": "Missing input validation",
                        "description": "MCP handler does not implement Pydantic validation"
                    })
                
                
# Check for XSS prevention
                if "validator" not in content and "Field" not in content:
                    findings.append({
                        "severity": "MEDIUM", 
                        "file": handler_file,
                        "issue": "Limited validation",
                        "description": "Handler may not have comprehensive field validation"
                    })
        
        return {"findings": findings, "files_checked": len(handler_files)}

```text

#
## Performance Benchmarking

```text
python

# PATTERN: Performance benchmarking framework

class PerformanceBenchmarker:
    """Performance benchmarking for PRP implementations."""
    
    def __init__(self):
        self.benchmarks = {}
        self.thresholds = {
            "response_time_ms": 500,      
# Max 500ms response time
            "memory_usage_mb": 100,       
# Max 100MB memory usage
            "cpu_usage_percent": 80,      
# Max 80% CPU usage
            "database_query_ms": 100      
# Max 100ms database queries
        }
    
    async def benchmark_mcp_tools(self) -> Dict[str, Any]:
        """Benchmark MCP tool performance."""
        tools = get_all_tools()
        tool_benchmarks = {}
        
        for tool in tools:
            
# Skip tools that require special setup
            if tool.name in ["orchestrator_initialize_session"]:
                continue
                
            try:
                start_time = time.time()
                
                
# Execute tool with sample data
                sample_args = self._generate_sample_arguments(tool)
                result = await call_tool(tool.name, sample_args)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  
# Convert to ms
                
                tool_benchmarks[tool.name] = {
                    "response_time_ms": response_time,
                    "success": True,
                    "meets_threshold": response_time <= self.thresholds["response_time_ms"]
                }
                
            except Exception as e:
                tool_benchmarks[tool.name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return tool_benchmarks
    
    async def benchmark_database_operations(self) -> Dict[str, Any]:
        """Benchmark database operation performance."""
        repository = get_test_repository()
        db_benchmarks = {}
        
        
# Benchmark task creation
        start_time = time.time()
        test_task = Task(task_id="perf-test", title="Performance Test", description="Test")
        await repository.create_task(test_task)
        end_time = time.time()
        
        db_benchmarks["create_task_ms"] = (end_time - start_time) * 1000
        
        
# Benchmark task retrieval
        start_time = time.time()
        retrieved_task = await repository.get_task("perf-test")
        end_time = time.time()
        
        db_benchmarks["get_task_ms"] = (end_time - start_time) * 1000
        
        
# Cleanup
        await repository.delete_task("perf-test", hard_delete=True)
        
        return db_benchmarks

```text

#
# Stage 5: Production Readiness Validation

#
## Purpose

End-to-end validation and deployment readiness assessment.

#
## Commands and Expected Outputs

```text
bash

# END-TO-END VALIDATION

python scripts/e2e_validation.py               
# Complete workflow testing

# Expected: All user workflows complete successfully

python scripts/production_readiness_check.py   
# Production environment validation

# Expected: System ready for production deployment

# DEPLOYMENT VALIDATION

docker-compose -f docker-compose.test.yml up   
# Container testing (if applicable)

# Expected: Application starts correctly in containerized environment

python scripts/health_check_validation.py      
# Health check endpoint testing

# Expected: Health checks respond correctly, system monitoring functional

# DOCUMENTATION VALIDATION

python scripts/validate_documentation.py       
# Documentation completeness check

# Expected: All required documentation present and up to date

```text

#
## End-to-End Test Framework

```python

# PATTERN: End-to-end validation framework

class E2EValidator:
    """End-to-end validation for complete workflows."""
    
    def __init__(self):
        self.scenarios = []
        self.results = {}
    
    async def validate_complete_workflows(self) -> Dict[str, Any]:
        """Validate complete user workflows."""
        workflow_results = {}
        
        
# Test complete task management workflow
        workflow_results["task_management"] = await self._test_task_management_workflow()
        
        
# Test MCP client integration workflow
        workflow_results["mcp_integration"] = await self._test_mcp_integration_workflow()
        
        
# Test error recovery workflow
        workflow_results["error_recovery"] = await self._test_error_recovery_workflow()
        
        return workflow_results
    
    async def _test_task_management_workflow(self) -> Dict[str, Any]:
        """Test complete task management workflow."""
        try:
            
# 1. Initialize session
            init_result = await call_tool("orchestrator_initialize_session", {
                "working_directory": "/tmp/test_workspace"
            })
            
            
# 2. Create task
            create_result = await call_tool("orchestrator_plan_task", {
                "title": "E2E Test Task",
                "description": "End-to-end test task",
                "task_type": "standard"
            })
            
            
# Extract task ID from result
            task_data = json.loads(create_result[0].text)
            task_id = task_data["task_id"]
            
            
# 3. Execute task
            execute_result = await call_tool("orchestrator_execute_task", {
                "task_id": task_id
            })
            
            
# 4. Complete task
            complete_result = await call_tool("orchestrator_complete_task", {
                "task_id": task_id,
                "summary": "E2E test completed",
                "detailed_work": "Test workflow executed successfully",
                "next_action": "complete"
            })
            
            return {
                "success": True,
                "steps_completed": 4,
                "task_id": task_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "steps_completed": "unknown"
            }

```text

#
# Failure Recovery and Debugging

#
## Validation Failure Handling

```text
python

# PATTERN: Comprehensive failure recovery system

class ValidationFailureHandler:
    """Handles validation failures with automated recovery."""
    
    def __init__(self):
        self.failure_history = []
        self.recovery_strategies = {
            "syntax_error": self._recover_syntax_error,
            "security_issue": self._recover_security_issue,
            "test_failure": self._recover_test_failure,
            "performance_issue": self._recover_performance_issue
        }
    
    async def handle_validation_failure(self, stage: str, failure_type: str, 
                                      failure_details: Dict[str, Any]) -> bool:
        """Handle validation failure with automated recovery."""
        failure_record = {
            "stage": stage,
            "type": failure_type,
            "details": failure_details,
            "timestamp": datetime.utcnow()
        }
        
        self.failure_history.append(failure_record)
        
        
# Attempt automated recovery
        recovery_strategy = self.recovery_strategies.get(failure_type)
        
        if recovery_strategy:
            try:
                recovery_success = await recovery_strategy(failure_details)
                failure_record["recovery_attempted"] = True
                failure_record["recovery_success"] = recovery_success
                return recovery_success
            except Exception as e:
                failure_record["recovery_error"] = str(e)
                return False
        else:
            failure_record["recovery_attempted"] = False
            return False
    
    async def _recover_security_issue(self, details: Dict[str, Any]) -> bool:
        """Attempt to recover from security issues."""
        
# Example: Auto-fix common security issues
        if "XSS" in details.get("issue_type", ""):
            
# Apply XSS prevention templates
            return await self._apply_xss_prevention_template()
        elif "SQL_INJECTION" in details.get("issue_type", ""):
            
# Apply parameterized query templates
            return await self._apply_sql_injection_prevention()
        
        return False
    
    def generate_recovery_report(self) -> Dict[str, Any]:
        """Generate comprehensive recovery report."""
        total_failures = len(self.failure_history)
        recovered_failures = len([f for f in self.failure_history 
                                if f.get("recovery_success", False)])
        
        return {
            "total_failures": total_failures,
            "recovered_failures": recovered_failures,
            "recovery_rate": recovered_failures / total_failures if total_failures > 0 else 0,
            "failure_breakdown": self._analyze_failure_patterns(),
            "recommendations": self._generate_recommendations()
        }

```text

#
# Framework Integration

#
## Continuous Validation Pipeline

```text
yaml

# PATTERN: Continuous validation pipeline configuration

VALIDATION_PIPELINE:
  trigger_events:
    - code_commit
    - pull_request  
    - deployment_request
    - scheduled_daily
  
  pipeline_stages:
    - name: "syntax_security"
      blocking: true
      timeout_minutes: 5
      
    - name: "unit_testing"
      blocking: true  
      timeout_minutes: 15
      
    - name: "integration"
      blocking: true
      timeout_minutes: 30
      
    - name: "security_performance"
      blocking: true
      timeout_minutes: 45
      
    - name: "production_readiness"
      blocking: false  
# Can proceed with warnings
      timeout_minutes: 60

  notification_settings:
    failure_notifications:
      - email
      - slack
      - github_status
    
    success_notifications:
      - github_status
      - deployment_webhook
```text

#
# Best Practices Summary

#
## Validation Framework Best Practices

1. **Early Detection**: Run syntax and security validation first to catch issues immediately

2. **Comprehensive Coverage**: Include unit, integration, security, and performance tests

3. **Automated Recovery**: Implement automated fixes for common issues where possible

4. **Clear Reporting**: Provide detailed, actionable feedback on all validation failures

5. **Continuous Improvement**: Analyze failure patterns to improve validation coverage

#
## Anti-Patterns to Avoid

- ❌ **Skipping Stages**: Don't skip validation stages "to save time" - each stage catches different issues

- ❌ **Ignoring Security**: Don't treat security validation as optional - security issues are blocking

- ❌ **Mock-Heavy Testing**: Don't over-mock in integration tests - test with real components when possible

- ❌ **Performance Afterthought**: Don't leave performance testing until the end - benchmark continuously

- ❌ **Manual Processes**: Don't rely on manual validation - automate everything possible

#
# Related Documentation

- [Security Patterns](../ai_docs/security-patterns.md) - Security validation patterns

- [MCP Protocol Patterns](../ai_docs/mcp-protocol-patterns.md) - MCP compliance validation  

- [Database Integration Patterns](../ai_docs/database-integration-patterns.md) - Database testing patterns

- [Context Engineering Guide](../ai_docs/context-engineering-guide.md) - Context quality validation

- [Security Validation](./security-validation.md) - Detailed security validation procedures
