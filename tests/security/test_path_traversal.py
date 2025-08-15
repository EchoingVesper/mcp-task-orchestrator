"""
Path Traversal Security Tests

Comprehensive test suite for validating path traversal protection, directory
traversal prevention, file system security, and safe path resolution.
"""

import pytest
import os
import tempfile
import platform
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# from mcp_task_orchestrator.infrastructure.security import  # TODO: Complete this import


class TestBasicPathTraversal:
    """Test basic path traversal attack prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.critical
    async def test_basic_directory_traversal_prevention(self, path_traversal_payloads):
        """Test basic directory traversal payload rejection."""
        safe_base_path = "/safe/base/directory"
        
        for payload in path_traversal_payloads:
            with pytest.raises(ValidationError) as exc_info:
                validate_file_path(payload, safe_base_path, "file_path")
            
            # Error should mention path traversal or invalid path
            error_msg = str(exc_info.value).lower()
            assert any(term in error_msg for term in ["path", "invalid", "traversal", "unsafe"])
            
            # Should not leak the actual payload in error message
            assert payload not in str(exc_info.value)
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.critical
    async def test_relative_path_traversal(self):
        """Test relative path traversal prevention."""
        base_path = "/safe/workspace"
        
        traversal_attempts = [
            "../secret.txt",
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "../../../../windows/system32/config/sam",
            "docs/../../../etc/hosts",
            "folder/../../etc/shadow",
            "a/b/c/../../../etc/passwd",
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "relative_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.critical
    async def test_absolute_path_injection(self):
        """Test absolute path injection prevention."""
        base_path = "/safe/workspace"
        
        absolute_path_attempts = [
            "/etc/passwd",
            "/root/.ssh/id_rsa", 
            "/proc/self/environ",
            "/dev/null",
            "/sys/kernel/debug",
            "C:\\windows\\system32\\config\\sam",
            "C:\\Users\\Administrator\\Desktop\\secrets.txt",
            "\\\\server\\share\\sensitive.txt",
        ]
        
        for attempt in absolute_path_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "absolute_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_mixed_separator_traversal(self):
        """Test mixed path separator traversal attempts."""
        base_path = "/safe/workspace"
        
        mixed_separator_attempts = [
            "..\\../etc/passwd",
            "../..\\etc\\passwd",
            "..\\..\\etc/passwd",
            "..\\/..\\/../etc/passwd",
            "folder\\../../../etc/passwd",
            "docs/..\\../etc/hosts",
        ]
        
        for attempt in mixed_separator_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "mixed_path")


class TestEncodedPathTraversal:
    """Test encoded path traversal attack prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_url_encoded_traversal(self):
        """Test URL encoded path traversal prevention."""
        base_path = "/safe/workspace"
        
        url_encoded_attempts = [
            # Single encoding
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows%5csystem32",
            
            # Double encoding
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            
            # Mixed encoding
            "..%2f..%2f..%2fetc%2fpasswd",
            "%2e%2e/..%2f../etc/passwd",
        ]
        
        for attempt in url_encoded_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "url_encoded_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_unicode_encoded_traversal(self):
        """Test Unicode encoded path traversal prevention."""
        base_path = "/safe/workspace"
        
        unicode_encoded_attempts = [
            # Unicode dot and slash
            "\u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002fetc\u002fpasswd",
            "\u002e\u002e\u005c\u002e\u002e\u005c\u002e\u002e\u005cwindows",
            
            # Full-width characters
            "．．／．．／．．／etc／passwd",
            "．．＼．．＼．．＼windows",
            
            # Combining characters
            "..\u0301/.\u0301./.\u0301./etc/passwd",
        ]
        
        for attempt in unicode_encoded_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "unicode_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_overlong_utf8_encoding(self):
        """Test overlong UTF-8 encoding path traversal prevention."""
        base_path = "/safe/workspace"
        
        # Overlong UTF-8 sequences (invalid but sometimes processed)
        overlong_attempts = [
            # Overlong '/' (0x2F)
            "..\xc0\xaf..\xc0\xaf..\xc0\xafetc\xc0\xafpasswd",
            
            # Overlong '\' (0x5C)  
            "..\xc1\x9c..\xc1\x9c..\xc1\x9cwindows",
            
            # Overlong '.' (0x2E)
            "\xc0\xae\xc0\xae\x2f\xc0\xae\xc0\xae\x2fetc\x2fpasswd",
        ]
        
        for attempt in overlong_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "overlong_utf8_path")


class TestNullByteInjection:
    """Test null byte injection prevention in paths."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_null_byte_path_injection(self):
        """Test null byte injection in file paths."""
        base_path = "/safe/workspace"
        
        null_byte_attempts = [
            # Basic null byte injection
            "../../../etc/passwd\x00.txt",
            "../../../etc/passwd\0.jpg",
            "safe_file.txt\x00/../../../etc/passwd",
            
            # URL encoded null bytes
            "../../../etc/passwd%00.txt",
            "safe_file.txt%00/../../../etc/passwd",
            
            # Unicode null bytes
            "../../../etc/passwd\u0000.txt",
            "safe_file.txt\u0000/../../../etc/passwd",
            
            # Multiple null bytes
            "../../../etc/passwd\x00\x00.txt",
            "safe\x00file\x00.txt\x00/../../../etc/passwd",
        ]
        
        for attempt in null_byte_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "null_byte_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_control_character_injection(self):
        """Test control character injection in paths."""
        base_path = "/safe/workspace"
        
        control_char_attempts = [
            # Various control characters
            "../../../etc/passwd\x01.txt",
            "../../../etc/passwd\x08.txt",  # Backspace
            "../../../etc/passwd\x0B.txt",  # Vertical tab
            "../../../etc/passwd\x0C.txt",  # Form feed
            "../../../etc/passwd\x1F.txt",  # Unit separator
            "../../../etc/passwd\x7F.txt",  # DEL
            
            # Line endings that might be interpreted
            "../../../etc/passwd\r\n.txt",
            "../../../etc/passwd\n.txt",
            "../../../etc/passwd\r.txt",
        ]
        
        for attempt in control_char_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "control_char_path")


class TestSymbolicLinkAttacks:
    """Test symbolic link and junction point attack prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_symbolic_link_traversal(self):
        """Test symbolic link traversal prevention."""
        base_path = "/safe/workspace"
        
        # Simulate symbolic link attacks
        symlink_attempts = [
            "/tmp/symlink_to_etc_passwd",
            "../symlink_to_sensitive_file",
            "safe_dir/symlink_to_root",
            "docs/symlink_to_etc_shadow",
            "uploads/symlink_to_private_keys",
        ]
        
        for attempt in symlink_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "symlink_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_junction_point_attacks(self):
        """Test Windows junction point attack prevention."""
        if platform.system() != "Windows":
            pytest.skip("Junction point tests only relevant on Windows")
        
        base_path = "C:\\safe\\workspace"
        
        junction_attempts = [
            "C:\\safe\\workspace\\junction_to_system32",
            "junction_to_windows\\system32\\config\\sam",
            "docs\\junction_to_users\\administrator",
        ]
        
        for attempt in junction_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "junction_path")


class TestSpecialFileAndDevice:
    """Test access to special files and devices."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_special_file_access_prevention(self):
        """Test prevention of access to special files."""
        base_path = "/safe/workspace"
        
        special_file_attempts = [
            # Linux/Unix special files
            "/dev/null",
            "/dev/zero", 
            "/dev/random",
            "/dev/urandom",
            "/dev/mem",
            "/dev/kmem",
            "/proc/version",
            "/proc/cpuinfo",
            "/proc/meminfo",
            "/proc/self/environ",
            "/proc/self/cmdline",
            "/sys/kernel/debug",
            
            # Windows special files
            "CON",
            "PRN", 
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "LPT1",
            "LPT2",
            "con.txt",  # Windows ignores extension for device names
            "prn.log",
            "aux.dat",
        ]
        
        for attempt in special_file_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "special_file_path")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_reserved_name_prevention(self):
        """Test prevention of reserved file names."""
        base_path = "/safe/workspace"
        
        reserved_names = [
            # Windows reserved names
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
            
            # With extensions (still reserved on Windows)
            "CON.txt", "PRN.log", "AUX.dat", "NUL.tmp",
            
            # Case variations
            "con", "prn", "aux", "nul",
            "Con", "Prn", "Aux", "Nul",
        ]
        
        for name in reserved_names:
            with pytest.raises(ValidationError):
                validate_file_path(name, base_path, "reserved_name")


class TestPathNormalization:
    """Test path normalization and canonicalization."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_path_normalization_bypass(self):
        """Test path normalization bypass attempts."""
        base_path = "/safe/workspace"
        
        normalization_bypass_attempts = [
            # Redundant slashes
            ".///..////..///..///etc//passwd",
            ".\\\\..\\\\..\\\\..\\\\windows\\\\system32",
            
            # Current directory references
            "./././../././../././../etc/passwd",
            ".\\.\\.\\..\\.\\.\\..\\.\\.\\..\\windows",
            
            # Complex combinations
            "./folder/../../../etc/passwd",
            ".\\folder\\..\\..\\..\\windows\\system32",
            "folder/.././..///../etc/passwd",
            
            # Trailing dots and spaces (Windows)
            "../../../etc/passwd.",
            "../../../etc/passwd ",
            "../../../etc/passwd...",
            "../../../etc/passwd   ",
        ]
        
        for attempt in normalization_bypass_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "normalization_bypass")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_case_sensitivity_attacks(self):
        """Test case sensitivity bypass attempts."""
        base_path = "/safe/workspace"
        
        case_bypass_attempts = [
            # Mixed case (might bypass simple string matching)
            "../../../ETC/PASSWD",
            "../../../Etc/Passwd",
            "../../../etc/PASSWD",
            "..\\..\\..\\WINDOWS\\SYSTEM32",
            "..\\..\\..\\Windows\\System32",
            "..\\..\\..\\windows\\SYSTEM32",
        ]
        
        for attempt in case_bypass_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attempt, base_path, "case_bypass")


class TestSafePathValidation:
    """Test that safe paths are correctly allowed."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_safe_relative_paths(self):
        """Test that safe relative paths are allowed."""
        base_path = "/safe/workspace"
        
        safe_paths = [
            "file.txt",
            "documents/report.pdf",
            "images/photo.jpg",
            "data/logs/app.log",
            "src/main.py",
            "docs/readme.md",
            "config/settings.json",
            "a/b/c/deep/file.dat",
        ]
        
        for safe_path in safe_paths:
            try:
                result = validate_file_path(safe_path, base_path, "safe_path")
                assert isinstance(result, str)
                assert len(result) > 0
                # Should not contain traversal sequences
                assert ".." not in result
            except ValidationError as e:
                pytest.fail(f"Safe path '{safe_path}' was incorrectly rejected: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_safe_filenames(self):
        """Test that safe filenames are allowed."""
        base_path = "/safe/workspace"
        
        safe_filenames = [
            "document.txt",
            "file_with_underscores.dat",
            "file-with-dashes.log",
            "file.with.dots.txt",
            "FILE_UPPERCASE.TXT",
            "123numeric456.dat",
            "file (with spaces).txt",
            "файл.txt",  # Unicode filename
            "文件.txt",   # Chinese characters
        ]
        
        for filename in safe_filenames:
            try:
                result = validate_file_path(filename, base_path, "safe_filename")
                assert isinstance(result, str)
            except ValidationError as e:
                pytest.fail(f"Safe filename '{filename}' was incorrectly rejected: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_edge_case_safe_paths(self):
        """Test edge case paths that should be safe."""
        base_path = "/safe/workspace"
        
        edge_case_safe_paths = [
            # Files with dots (but not traversal)
            "file.name.txt",
            ".hidden_file",
            "folder/.hidden_file",
            
            # Files with similar patterns to traversal
            "not_a_traversal.txt",  # Contains dots but not ..
            "dotdot.txt",           # Contains "dot" but not actual dots
            "parent_folder/child.txt",  # Contains "parent" but no traversal
        ]
        
        for safe_path in edge_case_safe_paths:
            try:
                result = validate_file_path(safe_path, base_path, "edge_case_safe")
                assert isinstance(result, str)
            except ValidationError as e:
                pytest.fail(f"Edge case safe path '{safe_path}' was incorrectly rejected: {e}")


class TestPathValidationPerformance:
    """Test path validation performance."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.performance
    async def test_path_validation_performance(self, performance_monitor, path_traversal_payloads):
        """Test path validation performance under load."""
        performance_monitor.start_monitoring()
        
        base_path = "/safe/workspace"
        
        # Test many path validations
        for i in range(100):
            # Test safe path
            safe_path = f"folder_{i}/file_{i}.txt"
            result = validate_file_path(safe_path, base_path, "performance_test")
            assert isinstance(result, str)
            
            # Test malicious path (should be fast to reject)
            if i < len(path_traversal_payloads):
                with pytest.raises(ValidationError):
                    validate_file_path(path_traversal_payloads[i], base_path, "performance_test")
        
        # Validation should be fast
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=10.0,
            max_cpu_percent=30.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.performance
    async def test_deep_path_performance(self, performance_monitor):
        """Test performance with very deep paths."""
        performance_monitor.start_monitoring()
        
        base_path = "/safe/workspace"
        
        # Generate very deep paths
        deep_paths = []
        for depth in [10, 50, 100]:
            path_components = [f"level_{i}" for i in range(depth)]
            deep_path = "/".join(path_components) + "/file.txt"
            deep_paths.append(deep_path)
        
        for deep_path in deep_paths:
            try:
                result = validate_file_path(deep_path, base_path, "deep_path")
                assert isinstance(result, str)
            except ValidationError:
                # Might be rejected for being too deep, which is fine
                pass
        
        # Should handle deep paths efficiently
        performance_monitor.assert_performance_limits(
            max_execution_time=2.0,
            max_memory_mb=5.0,
            max_cpu_percent=20.0
        )


class TestPathValidationLogging:
    """Test security logging for path validation events."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_path_traversal_attempt_logging(self, clean_security_state):
        """Test logging of path traversal attempts."""
        base_path = "/safe/workspace"
        malicious_path = "../../../etc/passwd"
        
        # Attempt path traversal
        with pytest.raises(ValidationError):
            validate_file_path(malicious_path, base_path, "logged_path")
        
        # Check if event was logged
        if hasattr(security_audit_logger, 'get_recent_events'):
            events = security_audit_logger.get_recent_events(limit=5)
            path_traversal_events = [
                e for e in events 
                if "PATH_TRAVERSAL" in e.get("event_type", "") or 
                   "path" in e.get("event_type", "").lower()
            ]
            assert len(path_traversal_events) > 0, "Path traversal attempt should be logged"
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_multiple_traversal_attempts_logging(self, clean_security_state):
        """Test logging of multiple path traversal attempts."""
        base_path = "/safe/workspace"
        
        malicious_paths = [
            "../../../etc/passwd",
            "../../../etc/shadow", 
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/hosts",
            "/proc/self/environ"
        ]
        
        # Attempt multiple traversals
        for malicious_path in malicious_paths:
            with pytest.raises(ValidationError):
                validate_file_path(malicious_path, base_path, "multiple_attempts")
        
        # Should log multiple events
        if hasattr(security_audit_logger, 'get_recent_events'):
            events = security_audit_logger.get_recent_events(limit=10)
            assert len(events) >= len(malicious_paths), "All traversal attempts should be logged"


class TestRealWorldPathAttacks:
    """Test real-world path attack scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_web_application_attacks(self):
        """Test common web application path traversal attacks."""
        base_path = "/var/www/html"
        
        web_attack_paths = [
            # Classic web attacks
            "../../../etc/passwd",
            "../../../etc/shadow",
            "../../../root/.ssh/id_rsa",
            "../../../home/user/.bash_history",
            
            # Apache/Nginx attacks
            "../../../etc/apache2/apache2.conf",
            "../../../etc/nginx/nginx.conf",
            "../../../var/log/apache2/access.log",
            "../../../var/log/nginx/access.log",
            
            # Database attacks
            "../../../var/lib/mysql",
            "../../../var/lib/postgresql",
            
            # Application attacks
            "../../../opt/app/config/database.yml",
            "../../../home/app/.env",
            "../../../var/www/.env",
        ]
        
        for attack_path in web_attack_paths:
            with pytest.raises(ValidationError):
                validate_file_path(attack_path, base_path, "web_attack")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_container_escape_attacks(self):
        """Test container escape path attacks."""
        base_path = "/app/workspace"
        
        container_escape_paths = [
            # Host filesystem access
            "../../../host/etc/passwd",
            "../../../host/root/.ssh/id_rsa",
            
            # Docker specific
            "../../../proc/1/root/etc/passwd",
            "../../../proc/self/root/etc/shadow",
            
            # Kubernetes specific
            "../../../var/run/secrets/kubernetes.io/serviceaccount/token",
            "../../../etc/kubernetes/admin.conf",
            
            # Container runtime
            "../../../var/run/docker.sock",
            "../../../var/lib/docker",
        ]
        
        for escape_path in container_escape_paths:
            with pytest.raises(ValidationError):
                validate_file_path(escape_path, base_path, "container_escape")
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    async def test_cloud_metadata_attacks(self):
        """Test cloud metadata service attacks via path traversal."""
        base_path = "/app/data"
        
        # While these aren't file paths, they might be used in similar contexts
        metadata_attack_attempts = [
            # AWS metadata
            "../../../proc/net/fib_trie",  # Network info
            "../../../proc/self/environ",  # Environment variables
            
            # Configuration files that might contain cloud credentials
            "../../../root/.aws/credentials",
            "../../../home/ubuntu/.aws/credentials",
            "../../../etc/kubernetes/kubelet/config.yaml",
        ]
        
        for attack_path in metadata_attack_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(attack_path, base_path, "cloud_metadata_attack")


# Integration tests
class TestPathTraversalIntegration:
    """Integration tests combining multiple path security measures."""
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.integration
    async def test_comprehensive_path_security(self, performance_monitor):
        """Test comprehensive path security across all attack vectors."""
        performance_monitor.start_monitoring()
        
        base_path = "/safe/workspace"
        
        # Combine multiple attack techniques
        complex_attacks = [
            # Multiple encoding + traversal
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            
            # Unicode + null byte + traversal
            "\u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002fetc\u002fpasswd\u0000.txt",
            
            # Mixed separators + encoding + control chars
            "..\\../../../etc/passwd\x00\r\n.txt",
            
            # Normalization bypass + special files
            ".//././..//././..//././dev//null",
            
            # Case manipulation + reserved names
            "../../../CON.txt",
            "../../../com1.dat",
        ]
        
        attack_count = 0
        for attack in complex_attacks:
            with pytest.raises(ValidationError):
                validate_file_path(attack, base_path, "comprehensive_test")
            attack_count += 1
        
        # Also test that safe paths still work
        safe_paths = [
            "documents/file.txt",
            "data/reports/summary.pdf",
            "images/logo.png"
        ]
        
        for safe_path in safe_paths:
            result = validate_file_path(safe_path, base_path, "safe_test")
            assert isinstance(result, str)
        
        # Should handle all validations efficiently
        assert attack_count == len(complex_attacks)
        performance_monitor.assert_performance_limits(
            max_execution_time=3.0,
            max_memory_mb=8.0,
            max_cpu_percent=25.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.path_traversal
    @pytest.mark.integration
    async def test_cross_platform_path_security(self):
        """Test path security across different platforms."""
        base_paths = {
            "linux": "/safe/workspace",
            "windows": "C:\\safe\\workspace",
            "macos": "/safe/workspace"
        }
        
        # Cross-platform attack attempts
        cross_platform_attacks = [
            # Linux/Unix style on Windows
            ("windows", "../../../etc/passwd"),
            
            # Windows style on Linux  
            ("linux", "..\\..\\..\\windows\\system32\\config\\sam"),
            
            # Mixed styles
            ("linux", "../../../C:\\windows\\system32"),
            ("windows", "..\\..\\../etc/passwd"),
            
            # UNC paths on Linux
            ("linux", "\\\\server\\share\\file.txt"),
            
            # Unix paths on Windows
            ("windows", "/tmp/test")
        ]
        
        for platform, attack_path in cross_platform_attacks:
            base_path = base_paths[platform]
            with pytest.raises(ValidationError):
                validate_file_path(attack_path, base_path, f"{platform}_attack")