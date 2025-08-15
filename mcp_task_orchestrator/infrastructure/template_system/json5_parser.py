"""
JSON5 Parser for Template System

Provides robust JSON5 parsing and validation with security controls.
JSON5 extends JSON with comments, trailing commas, and more flexible syntax.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class JSON5ValidationError(Exception):
    """Raised when JSON5 content fails validation."""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(message)
        self.line = line
        self.column = column
        
    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"JSON5 validation error at line {self.line}, column {self.column}: {super().__str__()}"
        return f"JSON5 validation error: {super().__str__()}"


class JSON5Parser:
    """
    Secure JSON5 parser with validation and sanitization.
    
    Features:
    - Comments (single-line // and multi-line /* */)
    - Trailing commas in objects and arrays
    - Unquoted object keys (when they are valid identifiers)
    - Single-quoted strings
    - Multi-line strings
    - Security validation and limits
    """
    
    def __init__(self, max_depth: int = 32, max_size: int = 1024 * 1024):  # 1MB default
        self.max_depth = max_depth
        self.max_size = max_size
        
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON5 content to Python dictionary.
        
        Args:
            content: JSON5 string content
            
        Returns:
            Parsed dictionary
            
        Raises:
            JSON5ValidationError: If parsing fails or content is invalid
        """
        if not content or not content.strip():
            raise JSON5ValidationError("Empty content provided")
            
        if len(content) > self.max_size:
            raise JSON5ValidationError(f"Content exceeds maximum size of {self.max_size} bytes")
            
        try:
            # Step 1: Remove comments
            cleaned_content = self._remove_comments(content)
            
            # Step 2: Process JSON5 extensions
            json_content = self._convert_json5_to_json(cleaned_content)
            
            # Step 3: Parse as JSON
            parsed = json.loads(json_content)
            
            # Step 4: Validate structure and depth
            self._validate_structure(parsed)
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise JSON5ValidationError(f"JSON parsing failed: {e}", e.lineno, e.colno)
        except Exception as e:
            raise JSON5ValidationError(f"Parsing failed: {str(e)}")
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse JSON5 content from a file.
        
        Args:
            file_path: Path to JSON5 file
            
        Returns:
            Parsed dictionary
            
        Raises:
            JSON5ValidationError: If file cannot be read or parsed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise JSON5ValidationError(f"File not found: {file_path}")
                
            if path.stat().st_size > self.max_size:
                raise JSON5ValidationError(f"File exceeds maximum size of {self.max_size} bytes")
                
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return self.parse(content)
            
        except IOError as e:
            raise JSON5ValidationError(f"Failed to read file {file_path}: {e}")
    
    def validate(self, content: str) -> List[str]:
        """
        Validate JSON5 content and return list of errors.
        
        Args:
            content: JSON5 string content
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            self.parse(content)
        except JSON5ValidationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            
        return errors
    
    def _remove_comments(self, content: str) -> str:
        """Remove single-line and multi-line comments from JSON5 content."""
        # Track if we're inside a string to avoid removing comment-like patterns in strings
        result = []
        i = 0
        in_string = False
        string_delimiter = None
        
        while i < len(content):
            char = content[i]
            
            # Handle string delimiters
            if not in_string and char in ('"', "'"):
                in_string = True
                string_delimiter = char
                result.append(char)
                i += 1
                continue
            elif in_string and char == string_delimiter:
                # Check if it's escaped
                if i > 0 and content[i-1] == '\\':
                    result.append(char)
                    i += 1
                    continue
                else:
                    in_string = False
                    string_delimiter = None
                    result.append(char)
                    i += 1
                    continue
            
            # Skip comments if not in string
            if not in_string:
                # Single-line comment
                if i < len(content) - 1 and content[i:i+2] == '//':
                    # Skip to end of line
                    while i < len(content) and content[i] != '\n':
                        i += 1
                    continue
                    
                # Multi-line comment
                elif i < len(content) - 1 and content[i:i+2] == '/*':
                    i += 2
                    # Skip to end of comment
                    while i < len(content) - 1:
                        if content[i:i+2] == '*/':
                            i += 2
                            break
                        i += 1
                    continue
            
            result.append(char)
            i += 1
            
        return ''.join(result)
    
    def _convert_json5_to_json(self, content: str) -> str:
        """Convert JSON5 syntax to valid JSON."""
        # Remove trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Convert unquoted object keys to quoted keys (string-aware)
        content = self._quote_unquoted_keys(content)
        
        # Convert single quotes to double quotes (outside of strings)
        content = self._convert_single_quotes(content)
        
        return content
    
    def _quote_unquoted_keys(self, content: str) -> str:
        """Convert unquoted object keys to quoted keys (string-aware)."""
        result = []
        i = 0
        in_string = False
        string_delimiter = None
        
        while i < len(content):
            char = content[i]
            
            # Handle string delimiters
            if not in_string and char in ('"', "'"):
                in_string = True
                string_delimiter = char
                result.append(char)
                i += 1
                continue
            elif in_string and char == string_delimiter:
                # Check if it's escaped
                if i > 0 and content[i-1] == '\\':
                    result.append(char)
                    i += 1
                    continue
                else:
                    in_string = False
                    string_delimiter = None
                    result.append(char)
                    i += 1
                    continue
            
            # If we're inside a string, just copy the character
            if in_string:
                result.append(char)
                i += 1
                continue
            
            # Look for unquoted keys outside of strings
            if char.isalpha() or char == '_':
                # Start of potential unquoted key
                key_start = i
                while i < len(content) and (content[i].isalnum() or content[i] == '_'):
                    i += 1
                
                # Skip whitespace after potential key
                while i < len(content) and content[i].isspace():
                    i += 1
                
                # Check if followed by colon (indicating it's a key)
                if i < len(content) and content[i] == ':':
                    # This is an unquoted key - add quotes
                    key = content[key_start:i].rstrip()
                    result.append(f'"{key}"')
                    # Don't increment i here as we need to process the colon
                else:
                    # Not a key, add the content as-is
                    result.append(content[key_start:i])
                    # Don't increment i here as we're already at the right position
            else:
                result.append(char)
                i += 1
        
        return ''.join(result)
    
    def _convert_single_quotes(self, content: str) -> str:
        """Convert single-quoted strings to double-quoted strings."""
        result = []
        i = 0
        
        while i < len(content):
            char = content[i]
            
            if char == "'":
                # Start of single-quoted string
                result.append('"')
                i += 1
                
                # Process string content
                while i < len(content):
                    char = content[i]
                    
                    if char == "'":
                        # End of string
                        result.append('"')
                        i += 1
                        break
                    elif char == '\\':
                        # Escape sequence
                        result.append(char)
                        i += 1
                        if i < len(content):
                            result.append(content[i])
                            i += 1
                    elif char == '"':
                        # Escape double quotes inside single-quoted string
                        result.append('\\"')
                        i += 1
                    else:
                        result.append(char)
                        i += 1
            else:
                result.append(char)
                i += 1
                
        return ''.join(result)
    
    def _validate_structure(self, data: Any, depth: int = 0) -> None:
        """Validate the structure for security and limits."""
        if depth > self.max_depth:
            raise JSON5ValidationError(f"Structure exceeds maximum depth of {self.max_depth}")
            
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, str):
                    raise JSON5ValidationError(f"Object keys must be strings, got {type(key)}")
                if len(key) > 1000:  # Reasonable key length limit
                    raise JSON5ValidationError(f"Object key too long: {len(key)} characters")
                self._validate_structure(value, depth + 1)
                
        elif isinstance(data, list):
            if len(data) > 10000:  # Reasonable array size limit
                raise JSON5ValidationError(f"Array too large: {len(data)} elements")
            for item in data:
                self._validate_structure(item, depth + 1)
                
        elif isinstance(data, str):
            if len(data) > 100000:  # Reasonable string length limit
                raise JSON5ValidationError(f"String too long: {len(data)} characters")


def parse_json5(content: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to parse JSON5 content.
    
    Args:
        content: JSON5 string content
        **kwargs: Additional arguments for JSON5Parser
        
    Returns:
        Parsed dictionary
    """
    parser = JSON5Parser(**kwargs)
    return parser.parse(content)


def parse_json5_file(file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
    """
    Convenience function to parse JSON5 file.
    
    Args:
        file_path: Path to JSON5 file
        **kwargs: Additional arguments for JSON5Parser
        
    Returns:
        Parsed dictionary
    """
    parser = JSON5Parser(**kwargs)
    return parser.parse_file(file_path)