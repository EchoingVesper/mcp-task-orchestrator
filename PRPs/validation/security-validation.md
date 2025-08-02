
# Security Validation Framework

**Purpose**: Comprehensive security validation procedures and testing frameworks specifically designed for MCP Task Orchestrator implementations, ensuring robust security posture and compliance with security best practices.

#
# Security Validation Philosophy

#
## Defense in Depth Validation

**"Security validation at every layer, every stage, every component"**

Security validation must be comprehensive, systematic, and integrated throughout the development lifecycle. Each validation layer addresses different attack vectors and security concerns.

#
## Security Validation Architecture

```yaml
SECURITY_VALIDATION_LAYERS:
  input_validation:
    focus: "All user inputs, API parameters, file paths"
    techniques: ["XSS prevention", "SQL injection prevention", "Path traversal prevention"]
    
  authentication_authorization:
    focus: "Identity verification and access control"
    techniques: ["Authentication bypass testing", "Authorization escalation testing", "Session management"]
    
  data_protection:
    focus: "Sensitive data handling and storage"
    techniques: ["Encryption validation", "Data leakage prevention", "Privacy compliance"]
    
  error_handling:
    focus: "Secure error responses and logging"
    techniques: ["Information disclosure prevention", "Error message sanitization", "Audit logging"]
    
  infrastructure_security:
    focus: "System-level security controls"
    techniques: ["Dependency scanning", "Configuration validation", "Network security"]

```text

#
# Input Validation Security Testing

#
## XSS Prevention Validation

```text
python

# PATTERN: Comprehensive XSS prevention testing

class XSSValidationSuite:
    """Comprehensive XSS prevention validation."""
    
    XSS_PAYLOADS = [
        
# Basic XSS
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        
        
# JavaScript protocol
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>",
        "vbscript:alert('xss')",
        
        
# Event handlers
        "onload=alert('xss')",
        "onerror=alert('xss')",
        "onclick=alert('xss')",
        "onmouseover=alert('xss')",
        
        
# Advanced evasion
        "<ScRiPt>alert('xss')</ScRiPt>",
        "<script>eval(String.fromCharCode(97,108,101,114,116,40,39,120,115,115,39,41))</script>",
        "';alert('xss');//",
        "\"><script>alert('xss')</script>",
        
        
# HTML5 vectors
        "<video><source onerror=\"alert('xss')\">",
        "<audio src=x onerror=alert('xss')>",
        "<iframe src='javascript:alert(1)'>",
        "<object data='javascript:alert(1)'>",
        "<embed src='javascript:alert(1)'>"
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_xss_prevention_in_text_fields(self):
        """Test XSS prevention in all text input fields."""
        for payload in self.XSS_PAYLOADS:
            
# Test task title field
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                await create_task_handler({
                    "title": payload,
                    "description": "Valid description"
                })
            
            
# Verify specific validation message
            assert "dangerous content" in str(exc_info.value).lower() or \
                   "invalid" in str(exc_info.value).lower()
            
            
# Test task description field
            with pytest.raises((ValidationError, ValueError)):
                await create_task_handler({
                    "title": "Valid title",
                    "description": payload
                })
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_xss_prevention_in_search_fields(self):
        """Test XSS prevention in search and filter fields."""
        for payload in self.XSS_PAYLOADS:
            
# Test search functionality
            with pytest.raises((ValidationError, ValueError)):
                await search_tasks_handler({
                    "search_term": payload
                })
            
            
# Test filter functionality
            with pytest.raises((ValidationError, ValueError)):
                await filter_tasks_handler({
                    "filter": payload
                })
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_stored_xss_prevention(self):
        """Test stored XSS prevention in database storage."""
        
# Create task with sanitized content
        task_data = {
            "title": "Test <script>alert('xss')</script> Task",
            "description": "Description with <img src=x onerror=alert('xss')> content"
        }
        
        
# Should be blocked at validation layer
        with pytest.raises((ValidationError, ValueError)):
            await create_task_handler(task_data)

```text

#
## SQL Injection Prevention Validation

```text
python

# PATTERN: SQL injection prevention testing

class SQLInjectionValidationSuite:
    """Comprehensive SQL injection prevention validation."""
    
    SQL_INJECTION_PAYLOADS = [
        
# Basic SQL injection
        "'; DROP TABLE tasks; --",
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DELETE FROM tasks WHERE 1=1; --",
        
        
# Union-based injection
        "' UNION SELECT password FROM users --",
        "' UNION ALL SELECT NULL,username,password FROM users --",
        
        
# Time-based blind injection
        "'; WAITFOR DELAY '00:00:05'; --",
        "'; SELECT SLEEP(5); --",
        
        
# Boolean-based blind injection
        "' AND (SELECT COUNT(*) FROM users) > 0 --",
        "' AND SUBSTRING(version(),1,1) = '5' --",
        
        
# Error-based injection
        "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e)) --",
        "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --"
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_sql_injection_prevention_in_search(self):
        """Test SQL injection prevention in search operations."""
        repository = get_test_repository()
        
        for payload in self.SQL_INJECTION_PAYLOADS:
            try:
                
# Should complete safely without database errors
                results = await repository.search_tasks(search_term=payload)
                
                
# Verify search completed safely (no exception)
                assert isinstance(results, list)
                
                
# Verify no unauthorized data was returned
                for result in results:
                    assert hasattr(result, 'title')  
# Verify expected structure
                    assert not any(sensitive in str(result).lower() 
                                 for sensitive in ['password', 'secret', 'token'])
                
            except Exception as e:
                
# Should not raise database-specific errors
                assert "sql" not in str(e).lower()
                assert "database" not in str(e).lower()
                assert "syntax" not in str(e).lower()
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_parameterized_queries_usage(self):
        """Verify that parameterized queries are used correctly."""
        repository = get_test_repository()
        
        
# Test with potential injection payload
        malicious_id = "test'; DROP TABLE tasks; --"
        
        
# Should handle safely with parameterized queries
        result = await repository.get_task(malicious_id)
        
        
# Should return None (task not found) rather than raising SQL error
        assert result is None
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_database_error_sanitization(self):
        """Test that database errors are properly sanitized."""
        repository = get_test_repository()
        
        
# Simulate database connection error
        with patch.object(repository, 'get_session') as mock_session:
            mock_session.side_effect = Exception("Database connection failed: host='internal-db' user='admin' password='secret123'")
            
            try:
                await repository.get_task("test-id")
                assert False, "Expected exception was not raised"
            except Exception as e:
                error_message = str(e).lower()
                
                
# Verify sensitive information is not in error message
                assert "password" not in error_message
                assert "secret123" not in error_message
                assert "admin" not in error_message
                assert "internal-db" not in error_message
                
                
# Should be generic database error message
                assert "database" in error_message or "operation failed" in error_message

```text

#
## Path Traversal Prevention Validation

```text
python

# PATTERN: Path traversal prevention testing

class PathTraversalValidationSuite:
    """Path traversal attack prevention validation."""
    
    PATH_TRAVERSAL_PAYLOADS = [
        
# Basic traversal
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        
        
# URL encoded
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows%5csystem32%5cconfig%5csam",
        
        
# Double encoding
        "%252e%252e%252fetc%252fpasswd",
        "%252e%252e%255cetc%255cpasswd",
        
        
# Absolute paths
        "/etc/passwd",
        "/etc/shadow",
        "/root/.ssh/id_rsa",
        "C:\\windows\\system32\\config\\sam",
        "C:\\windows\\system32\\drivers\\etc\\hosts",
        
        
# Home directory access
        "~/.ssh/id_rsa",
        "~/.bashrc",
        "~/../../etc/passwd",
        
        
# File protocol
        "file:///etc/passwd",
        "file:///../etc/passwd",
        "file://../../etc/passwd"
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_file_path_validation(self):
        """Test file path validation prevents traversal attacks."""
        for payload in self.PATH_TRAVERSAL_PAYLOADS:
            with pytest.raises((ValueError, SecurityError, FileNotFoundError)):
                await validate_file_path(payload, allowed_base_dirs=["/tmp", "/workspace"])
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_file_upload_path_validation(self):
        """Test file upload path validation."""
        
# If file uploads are supported
        for payload in self.PATH_TRAVERSAL_PAYLOADS:
            with pytest.raises((ValueError, SecurityError)):
                await handle_file_upload({
                    "file_path": payload,
                    "content": "test content"
                })
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_configuration_file_access(self):
        """Test that configuration files cannot be accessed via path traversal."""
        sensitive_files = [
            "../../../config/database.yml",
            "../../../.env",
            "../../../config/secrets.json",
            "../../../mcp_task_orchestrator/config/settings.py"
        ]
        
        for sensitive_file in sensitive_files:
            with pytest.raises((ValueError, SecurityError, FileNotFoundError)):
                await read_configuration_file(sensitive_file)

```text

#
# Authentication and Authorization Validation

#
## Authentication Security Testing

```text
python

# PATTERN: Authentication security validation

class AuthenticationValidationSuite:
    """Comprehensive authentication security testing."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_authentication_bypass_attempts(self):
        """Test various authentication bypass techniques."""
        bypass_attempts = [
            
# Missing authentication
            {},
            {"api_key": ""},
            {"api_key": None},
            
            
# Invalid authentication
            {"api_key": "invalid_key"},
            {"api_key": "expired_key"},
            {"api_key": "malformed_key"},
            
            
# Authentication manipulation
            {"api_key": "valid_key'; DROP TABLE api_keys; --"},
            {"api_key": "<script>alert('xss')</script>"},
            {"api_key": "../../../secrets/api_key.txt"},
        ]
        
        for attempt in bypass_attempts:
            with pytest.raises(McpError) as exc_info:
                await protected_handler_function(attempt)
            
            
# Verify proper error code and message
            assert exc_info.value.code in [-32602, -32603]  
# Invalid params or access denied
            assert "denied" in exc_info.value.message.lower() or \
                   "required" in exc_info.value.message.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_session_security(self):
        """Test session management security."""
        
# Test session fixation prevention
        session_id_1 = await create_session("user1")
        await authenticate_user("user1", session_id_1)
        
        
# Session ID should change after authentication
        session_id_2 = await get_current_session("user1")
        assert session_id_1 != session_id_2
        
        
# Test session timeout
        with patch('time.time', return_value=time.time() + 3600):  
# 1 hour later
            with pytest.raises(SecurityError):
                await validate_session(session_id_2)
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_brute_force_protection(self):
        """Test protection against brute force attacks."""
        
# Attempt multiple failed authentications
        for i in range(10):
            try:
                await authenticate_user("testuser", f"wrong_password_{i}")
            except AuthenticationError:
                pass  
# Expected
        
        
# Account should be locked after multiple failures
        with pytest.raises(SecurityError) as exc_info:
            await authenticate_user("testuser", "correct_password")
        
        assert "locked" in str(exc_info.value).lower() or \
               "rate" in str(exc_info.value).lower()

```text

#
## Authorization Security Testing

```text
python

# PATTERN: Authorization security validation

class AuthorizationValidationSuite:
    """Comprehensive authorization security testing."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_role_based_access_control(self):
        """Test role-based access control enforcement."""
        
# Test with different user roles
        test_scenarios = [
            ("readonly_user", "create_task", False),
            ("readonly_user", "view_task", True),
            ("user", "create_task", True),
            ("user", "delete_task", False),
            ("admin", "delete_task", True),
            ("admin", "manage_users", True),
        ]
        
        for user_role, action, should_succeed in test_scenarios:
            user_context = {"user_id": "test_user", "role": user_role}
            
            if should_succeed:
                
# Should succeed without exception
                result = await authorize_action(user_context, action)
                assert result is True
            else:
                
# Should raise authorization error
                with pytest.raises((SecurityError, McpError)):
                    await authorize_action(user_context, action)
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_horizontal_privilege_escalation(self):
        """Test prevention of horizontal privilege escalation."""
        
# User should only access their own resources
        user1_context = {"user_id": "user1", "role": "user"}
        user2_context = {"user_id": "user2", "role": "user"}
        
        
# Create task as user1
        task_id = await create_task_as_user(user1_context, {
            "title": "User1 Task",
            "description": "Task owned by user1"
        })
        
        
# User2 should not be able to access user1's task
        with pytest.raises((SecurityError, McpError)):
            await get_task_as_user(user2_context, task_id)
        
        
# User2 should not be able to modify user1's task
        with pytest.raises((SecurityError, McpError)):
            await update_task_as_user(user2_context, task_id, {
                "title": "Modified by user2"
            })
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_vertical_privilege_escalation(self):
        """Test prevention of vertical privilege escalation."""
        user_context = {"user_id": "regular_user", "role": "user"}
        
        
# Regular user should not be able to perform admin actions
        admin_actions = [
            ("create_user", {"username": "new_user", "role": "admin"}),
            ("delete_user", {"user_id": "another_user"}),
            ("modify_system_config", {"setting": "debug", "value": True}),
            ("access_audit_logs", {}),
        ]
        
        for action, params in admin_actions:
            with pytest.raises((SecurityError, McpError)):
                await perform_admin_action(user_context, action, params)

```text

#
# Data Protection Validation

#
## Sensitive Data Handling Testing

```text
python

# PATTERN: Sensitive data protection validation

class DataProtectionValidationSuite:
    """Comprehensive data protection validation."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_sensitive_data_encryption(self):
        """Test that sensitive data is properly encrypted."""
        sensitive_data = {
            "api_key": "secret_api_key_12345",
            "password": "user_password_secret",
            "personal_note": "This contains sensitive information"
        }
        
        
# Store sensitive data
        record_id = await store_sensitive_record(sensitive_data)
        
        
# Retrieve raw database record
        raw_record = await get_raw_database_record(record_id)
        
        
# Verify sensitive fields are encrypted
        for field_name, original_value in sensitive_data.items():
            if field_name in ["api_key", "password", "personal_note"]:
                stored_value = raw_record.get(field_name)
                assert stored_value != original_value  
# Should be encrypted
                assert len(stored_value) > len(original_value)  
# Encrypted data is longer
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_data_leakage_in_logs(self):
        """Test that sensitive data doesn't leak into logs."""
        sensitive_inputs = {
            "password": "secret_password_123",
            "api_key": "sk_live_abc123def456",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789"
        }
        
        with LogCapture() as log_capture:
            try:
                
# Perform operation that might log sensitive data
                await process_user_data(sensitive_inputs)
            except Exception:
                pass  
# We're testing logging, not functionality
            
            
# Check all log messages
            for log_record in log_capture.records:
                log_message = log_record.getMessage().lower()
                
                
# Verify no sensitive data in logs
                assert "secret_password_123" not in log_message
                assert "sk_live_abc123def456" not in log_message
                assert "4111-1111-1111-1111" not in log_message
                assert "123-45-6789" not in log_message
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_data_masking_in_responses(self):
        """Test that sensitive data is properly masked in API responses."""
        
# Create user with sensitive data
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "api_key": "secret_key_123456",
            "phone": "+1-555-123-4567"
        }
        
        user_id = await create_user(user_data)
        
        
# Retrieve user via API
        response = await get_user_handler({"user_id": user_id})
        response_data = json.loads(response[0].text)
        
        
# Verify sensitive data is masked
        assert response_data["api_key"].startswith("sk_****")  
# Masked
        assert response_data["phone"] == "+1-555-***-****"     
# Masked
        assert response_data["email"] == "test@example.com"    
# Not sensitive, not masked

```text

#
## Privacy Compliance Validation

```text
python

# PATTERN: Privacy compliance validation

class PrivacyComplianceValidationSuite:
    """Privacy regulation compliance validation."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_data_retention_compliance(self):
        """Test data retention policy compliance."""
        
# Create user data with timestamp
        user_data = {
            "user_id": "retention_test_user",
            "personal_data": "sensitive personal information",
            "created_at": datetime.utcnow() - timedelta(days=400)  
# Old data
        }
        
        await store_user_data(user_data)
        
        
# Run data retention cleanup
        await run_data_retention_cleanup()
        
        
# Verify old data was removed
        retrieved_data = await get_user_data("retention_test_user")
        assert retrieved_data is None or \
               retrieved_data.get("personal_data") is None
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_data_deletion_compliance(self):
        """Test right to deletion compliance."""
        
# Create user data
        user_id = "deletion_test_user"
        await create_user_with_data(user_id, {
            "profile": "user profile data",
            "activity_log": ["action1", "action2", "action3"],
            "preferences": {"theme": "dark", "notifications": True}
        })
        
        
# Request data deletion
        deletion_request_id = await request_data_deletion(user_id)
        
        
# Process deletion request
        await process_deletion_request(deletion_request_id)
        
        
# Verify all user data is deleted
        user_profile = await get_user_profile(user_id)
        user_activity = await get_user_activity(user_id)
        user_preferences = await get_user_preferences(user_id)
        
        assert user_profile is None
        assert user_activity == []
        assert user_preferences is None
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_data_portability_compliance(self):
        """Test data portability compliance."""
        user_id = "portability_test_user"
        
        
# Request data export
        export_request_id = await request_data_export(user_id)
        export_data = await get_export_data(export_request_id)
        
        
# Verify export data format
        assert isinstance(export_data, dict)
        assert "user_profile" in export_data
        assert "activity_history" in export_data
        assert "created_content" in export_data
        
        
# Verify data completeness
        assert export_data["user_profile"]["user_id"] == user_id
        assert isinstance(export_data["activity_history"], list)
        assert isinstance(export_data["created_content"], list)

```text

#
# Error Handling Security Validation

#
## Information Disclosure Prevention

```text
python

# PATTERN: Information disclosure prevention validation

class InformationDisclosureValidationSuite:
    """Information disclosure prevention validation."""
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_database_error_sanitization(self):
        """Test that database errors don't leak sensitive information."""
        error_scenarios = [
            
# Connection errors
            ("Database connection failed: host='internal-db.company.com' user='admin' password='secret123'", 
             "Database connection failed"),
            
            
# SQL errors
            ("Syntax error at line 45: SELECT * FROM secret_table WHERE password = 'leaked_password'",
             "Database query failed"),
            
            
# Constraint violations
            ("UNIQUE constraint failed: users.email (email: 'admin@company.com' already exists)",
             "Data validation failed"),
            
            
# File system errors
            ("Permission denied accessing '/etc/shadow' (uid=0 required)",
             "File access denied")
        ]
        
        for internal_error, expected_message in error_scenarios:
            with patch('database.execute') as mock_db:
                mock_db.side_effect = Exception(internal_error)
                
                try:
                    await database_operation_handler({"param": "test"})
                    assert False, "Expected exception was not raised"
                except McpError as e:
                    
# Verify error message is sanitized
                    assert "password" not in e.message.lower()
                    assert "secret" not in e.message
                    assert "admin" not in e.message
                    assert "internal-db" not in e.message
                    assert "/etc/shadow" not in e.message
                    
                    
# Verify expected generic message
                    assert any(expected in e.message.lower() 
                             for expected in ["failed", "error", "denied"])
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_stack_trace_prevention(self):
        """Test that stack traces are not exposed to clients."""
        with patch('some_internal_function') as mock_func:
            
# Simulate internal error with detailed stack trace
            mock_func.side_effect = Exception("Internal error in sensitive_function at line 123")
            
            try:
                await public_api_handler({"input": "test"})
                assert False, "Expected exception was not raised"
            except McpError as e:
                
# Verify no stack trace information in client response
                assert "line 123" not in e.message
                assert "sensitive_function" not in e.message
                assert "traceback" not in e.message.lower()
                assert e.message in ["Internal server error", "Operation failed"]
    
    @pytest.mark.asyncio
    @pytest.mark.security
    async def test_configuration_leak_prevention(self):
        """Test that configuration details don't leak in errors."""
        config_sensitive_errors = [
            "Failed to connect to Redis at redis://admin:password123@internal-redis:6379",
            "SMTP server error: smtp.company.com:587 (user: notifications@company.com, pass: smtp_secret)",
            "API key validation failed: sk_live_abc123def456ghi789 is invalid",
            "Database URL parse error: postgresql://dbuser:dbpass@db.internal:5432/production_db"
        ]
        
        for sensitive_error in config_sensitive_errors:
            with patch('external_service.connect') as mock_connect:
                mock_connect.side_effect = Exception(sensitive_error)
                
                try:
                    await service_integration_handler({"action": "test"})
                    assert False, "Expected exception was not raised"
                except McpError as e:
                    
# Verify no configuration details in error message
                    assert "password123" not in e.message
                    assert "smtp_secret" not in e.message
                    assert "sk_live_abc123def456ghi789" not in e.message
                    assert "dbpass" not in e.message
                    assert "internal" not in e.message.lower()

```text

#
# Security Audit Automation

#
## Automated Security Scanning

```text
python

# PATTERN: Automated security scanning framework

class AutomatedSecurityScanner:
    """Automated security scanning and validation."""
    
    def __init__(self):
        self.scan_results = {}
        self.security_score = 0
        self.critical_issues = []
    
    async def run_comprehensive_security_scan(self) -> Dict[str, Any]:
        """Run comprehensive automated security scan."""
        scan_results = {
            "dependency_scan": await self._scan_dependencies(),
            "code_scan": await self._scan_code_vulnerabilities(),
            "configuration_scan": await self._scan_configuration(),
            "authentication_scan": await self._scan_authentication(),
            "input_validation_scan": await self._scan_input_validation(),
            "data_protection_scan": await self._scan_data_protection(),
        }
        
        
# Calculate overall security score
        self.security_score = self._calculate_security_score(scan_results)
        
        return {
            "security_score": self.security_score,
            "scan_results": scan_results,
            "critical_issues": self.critical_issues,
            "recommendations": self._generate_security_recommendations(),
            "compliance_status": self._check_compliance_status()
        }
    
    async def _scan_dependencies(self) -> Dict[str, Any]:
        """Scan dependencies for known vulnerabilities."""
        try:
            
# Run safety check
            result = await self._run_command("safety check --json")
            
            if result.returncode == 0:
                return {"status": "passed", "vulnerabilities": []}
            else:
                vulnerabilities = json.loads(result.stdout)
                critical_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]
                
                if critical_vulns:
                    self.critical_issues.extend(critical_vulns)
                
                return {
                    "status": "failed" if critical_vulns else "warning",
                    "vulnerabilities": vulnerabilities,
                    "critical_count": len(critical_vulns)
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _scan_code_vulnerabilities(self) -> Dict[str, Any]:
        """Scan code for security vulnerabilities using bandit."""
        try:
            result = await self._run_command("bandit -r src/ -f json")
            
            if result.returncode == 0:
                return {"status": "passed", "issues": []}
            else:
                issues = json.loads(result.stdout)
                high_severity = [i for i in issues.get("results", []) 
                               if i.get("issue_severity") == "HIGH"]
                
                if high_severity:
                    self.critical_issues.extend(high_severity)
                
                return {
                    "status": "failed" if high_severity else "warning",
                    "issues": issues.get("results", []),
                    "high_severity_count": len(high_severity)
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _calculate_security_score(self, scan_results: Dict[str, Any]) -> int:
        """Calculate overall security score (0-100)."""
        base_score = 100
        
        
# Deduct points for critical issues
        critical_count = len(self.critical_issues)
        base_score -= critical_count * 20  
# 20 points per critical issue
        
        
# Deduct points for failed scans
        failed_scans = sum(1 for result in scan_results.values() 
                          if result.get("status") == "failed")
        base_score -= failed_scans * 10  
# 10 points per failed scan
        
        
# Deduct points for warnings
        warning_scans = sum(1 for result in scan_results.values() 
                           if result.get("status") == "warning")
        base_score -= warning_scans * 5  
# 5 points per warning
        
        return max(0, base_score)

```text

#
# Security Validation Reporting

#
## Comprehensive Security Reports

```text
python

# PATTERN: Security validation reporting

class SecurityValidationReporter:
    """Comprehensive security validation reporting."""
    
    def generate_security_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security validation report."""
        return {
            "executive_summary": self._generate_executive_summary(validation_results),
            "detailed_findings": self._generate_detailed_findings(validation_results),
            "risk_assessment": self._generate_risk_assessment(validation_results),
            "remediation_plan": self._generate_remediation_plan(validation_results),
            "compliance_status": self._generate_compliance_status(validation_results),
            "security_metrics": self._generate_security_metrics(validation_results)
        }
    
    def _generate_executive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of security validation."""
        total_tests = sum(len(category.get("tests", [])) for category in results.values())
        passed_tests = sum(len([t for t in category.get("tests", []) if t.get("passed", False)]) 
                          for category in results.values())
        
        critical_issues = sum(len(category.get("critical_issues", [])) for category in results.values())
        
        return {
            "overall_status": "PASS" if critical_issues == 0 else "FAIL",
            "security_score": results.get("security_score", 0),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "critical_issues": critical_issues,
            "recommendation": "DEPLOY" if critical_issues == 0 else "DO NOT DEPLOY"
        }
```text

#
# Best Practices Summary

#
## Security Validation Best Practices

1. **Comprehensive Coverage**: Test all attack vectors including XSS, SQL injection, path traversal, and authentication bypass

2. **Automated Scanning**: Integrate automated security scanning tools (bandit, safety, custom scanners)

3. **Layered Testing**: Validate security at input, processing, storage, and output layers

4. **Realistic Payloads**: Use real-world attack payloads, not just basic test cases

5. **Error Sanitization**: Verify that all error messages are sanitized and don't leak sensitive information

6. **Regular Updates**: Keep security test suites updated with latest attack techniques and payloads

#
## Security Anti-Patterns to Avoid

- ❌ **Test Bypassing**: Don't skip security tests "to save time" - security issues are critical

- ❌ **Mock Overuse**: Don't over-mock security tests - test with real security controls

- ❌ **Generic Testing**: Don't use only basic security test cases - include advanced evasion techniques

- ❌ **Information Leakage**: Don't ignore information disclosure - test all error scenarios

- ❌ **Incomplete Coverage**: Don't test only happy paths - focus on edge cases and attack scenarios

#
# Related Documentation

- [Security Patterns](../ai_docs/security-patterns.md) - Security implementation patterns

- [Validation Framework](./validation-framework.md) - Multi-stage validation system

- [MCP Protocol Patterns](../ai_docs/mcp-protocol-patterns.md) - MCP security considerations

- [Database Integration Patterns](../ai_docs/database-integration-patterns.md) - Database security patterns

- [Context Engineering Guide](../ai_docs/context-engineering-guide.md) - Security context engineering
