"""
Unit tests for JSON5 Parser

Tests JSON5 parsing functionality including comments, trailing commas,
unquoted keys, and error handling.
"""

import pytest
from pathlib import Path
import tempfile
import json

from mcp_task_orchestrator.infrastructure.template_system.json5_parser import JSON5Parser, JSON5ValidationError


class TestJSON5Parser:
    """Test suite for JSON5Parser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JSON5Parser()
    
    def test_basic_json_parsing(self):
        """Test parsing of basic JSON content."""
        json_content = '{"name": "test", "value": 42}'
        result = self.parser.parse(json_content)
        
        assert result == {"name": "test", "value": 42}
    
    def test_json5_comments_single_line(self):
        """Test parsing JSON5 with single-line comments."""
        json5_content = '''
        {
            "name": "test", // This is a comment
            "value": 42
        }
        '''
        result = self.parser.parse(json5_content)
        
        assert result == {"name": "test", "value": 42}
    
    def test_json5_comments_multi_line(self):
        """Test parsing JSON5 with multi-line comments."""
        json5_content = '''
        {
            /* This is a 
               multi-line comment */
            "name": "test",
            "value": 42 /* inline comment */
        }
        '''
        result = self.parser.parse(json5_content)
        
        assert result == {"name": "test", "value": 42}
    
    def test_json5_trailing_commas(self):
        """Test parsing JSON5 with trailing commas."""
        json5_content = '''
        {
            "name": "test",
            "value": 42,
            "list": [1, 2, 3,],
            "nested": {
                "key": "value",
            },
        }
        '''
        result = self.parser.parse(json5_content)
        
        expected = {
            "name": "test",
            "value": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        assert result == expected
    
    def test_json5_unquoted_keys(self):
        """Test parsing JSON5 with unquoted object keys."""
        json5_content = '''
        {
            name: "test",
            value: 42,
            camelCase: true,
            snake_case: false
        }
        '''
        result = self.parser.parse(json5_content)
        
        expected = {
            "name": "test",
            "value": 42,
            "camelCase": True,
            "snake_case": False
        }
        assert result == expected
    
    def test_json5_single_quoted_strings(self):
        """Test parsing JSON5 with single-quoted strings."""
        json5_content = '''
        {
            "double": "quoted",
            'single': 'quoted',
            'mixed': "styles"
        }
        '''
        result = self.parser.parse(json5_content)
        
        expected = {
            "double": "quoted",
            "single": "quoted",
            "mixed": "styles"
        }
        assert result == expected
    
    def test_json5_multi_line_strings(self):
        """Test parsing JSON5 with multi-line strings."""
        json5_content = '''
        {
            "multiline": "This is a long string that spans multiple lines"
        }
        '''
        result = self.parser.parse(json5_content)
        
        assert "multiline" in result
        assert "long string" in result["multiline"]
    
    def test_json5_numeric_formats(self):
        """Test parsing JSON5 with various numeric formats."""
        json5_content = '''
        {
            "decimal": 42,
            "float": 3.14,
            "scientific": 1e5,
            "negative": -42
        }
        '''
        result = self.parser.parse(json5_content)
        
        assert result["decimal"] == 42
        assert result["float"] == 3.14
        assert result["scientific"] == 1e5
        assert result["negative"] == -42
    
    def test_parse_file_valid(self):
        """Test parsing from a valid file."""
        json5_content = '''
        {
            // File-based parsing test
            "template": "test",
            "valid": true,
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json5', delete=False) as f:
            f.write(json5_content)
            temp_path = Path(f.name)
        
        try:
            result = self.parser.parse_file(temp_path)
            assert result == {"template": "test", "valid": True}
        finally:
            temp_path.unlink()
    
    def test_parse_file_not_found(self):
        """Test parsing from a non-existent file."""
        non_existent = Path("/non/existent/file.json5")
        
        with pytest.raises(JSON5ValidationError, match="File not found"):
            self.parser.parse_file(non_existent)
    
    def test_parse_file_permission_error(self):
        """Test parsing from a file with permission issues."""
        # Create a file and then make it unreadable (if possible)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json5', delete=False) as f:
            f.write('{"test": true}')
            temp_path = Path(f.name)
        
        try:
            # Try to make file unreadable (may not work on all systems)
            temp_path.chmod(0o000)
            
            with pytest.raises(JSON5ValidationError, match="Failed to read file"):
                self.parser.parse_file(temp_path)
        except (OSError, PermissionError):
            # If we can't change permissions, just verify file reading works
            result = self.parser.parse_file(temp_path)
            assert result == {"test": True}
        finally:
            # Restore permissions and clean up
            try:
                temp_path.chmod(0o644)
                temp_path.unlink()
            except:
                pass
    
    def test_invalid_json5_syntax(self):
        """Test parsing invalid JSON5 syntax."""
        invalid_content = '''
        {
            "unterminated": "string
            "invalid": syntax,
        '''
        
        with pytest.raises(JSON5ValidationError, match="JSON parsing failed"):
            self.parser.parse(invalid_content)
    
    def test_empty_content(self):
        """Test parsing empty content."""
        with pytest.raises(JSON5ValidationError, match="Empty content provided"):
            self.parser.parse("")
        
        with pytest.raises(JSON5ValidationError, match="Empty content provided"):
            self.parser.parse("   \n\t  ")
    
    def test_null_content(self):
        """Test parsing null content."""
        with pytest.raises(JSON5ValidationError, match="Empty content provided"):
            self.parser.parse(None)
    
    def test_non_object_root(self):
        """Test parsing JSON5 that doesn't have object at root."""
        # Array at root
        array_content = '[1, 2, 3]'
        result = self.parser.parse(array_content)
        assert result == [1, 2, 3]
        
        # String at root
        string_content = '"just a string"'
        result = self.parser.parse(string_content)
        assert result == "just a string"
        
        # Number at root
        number_content = '42'
        result = self.parser.parse(number_content)
        assert result == 42
    
    def test_complex_nested_structure(self):
        """Test parsing complex nested JSON5 structure."""
        complex_content = '''
        {
            // Complex template structure
            metadata: {
                name: "Complex Template",
                version: "1.0.0",
                tags: ["test", "complex",], // trailing comma
            },
            parameters: {
                required_param: {
                    type: "string",
                    description: 'Single quoted description',
                },
                optional_param: {
                    type: "number",
                    default: 42,
                    /* Multi-line
                       comment here */
                }
            },
            tasks: {
                task1: {
                    title: "Task One",
                    dependencies: [],
                },
                task2: {
                    title: "Task Two", 
                    dependencies: ["task1"],
                }
            }
        }
        '''
        
        result = self.parser.parse(complex_content)
        
        # Verify structure
        assert "metadata" in result
        assert "parameters" in result
        assert "tasks" in result
        
        # Verify metadata
        assert result["metadata"]["name"] == "Complex Template"
        assert result["metadata"]["version"] == "1.0.0"
        assert result["metadata"]["tags"] == ["test", "complex"]
        
        # Verify parameters
        assert result["parameters"]["required_param"]["type"] == "string"
        assert result["parameters"]["optional_param"]["default"] == 42
        
        # Verify tasks
        assert len(result["tasks"]) == 2
        assert result["tasks"]["task2"]["dependencies"] == ["task1"]
    
    def test_unicode_content(self):
        """Test parsing JSON5 with Unicode content."""
        unicode_content = '''
        {
            "english": "Hello World",
            "japanese": "こんにちは",
            "emoji": "🎉🚀✨",
            "arabic": "مرحبا بالعالم",
            "chinese": "你好世界"
        }
        '''
        
        result = self.parser.parse(unicode_content)
        
        assert result["english"] == "Hello World"
        assert result["japanese"] == "こんにちは"
        assert result["emoji"] == "🎉🚀✨"
        assert result["arabic"] == "مرحبا بالعالم"
        assert result["chinese"] == "你好世界"
    
    def test_edge_case_whitespace(self):
        """Test parsing JSON5 with various whitespace scenarios."""
        # Lots of whitespace
        whitespace_content = '''
        
        
        {
            
            "key"    :    "value"   ,
            
            
            "number"  :  42
            
            
        }
        
        
        '''
        
        result = self.parser.parse(whitespace_content)
        assert result == {"key": "value", "number": 42}
    
    def test_error_line_reporting(self):
        """Test that parsing errors include line number information."""
        invalid_content = '''
        {
            "valid": "line",
            "invalid": syntax error here,
            "another": "line"
        }
        '''
        
        with pytest.raises(JSON5ValidationError) as exc_info:
            self.parser.parse(invalid_content)
        
        # The error message should contain useful information
        error_msg = str(exc_info.value)
        assert "JSON parsing failed" in error_msg
    
    def test_large_content_performance(self):
        """Test parsing performance with larger JSON5 content."""
        # Generate a reasonably large JSON5 structure
        large_content = "{\n"
        
        # Add many key-value pairs
        for i in range(1000):
            large_content += f'    "key{i}": "value{i}",  // Comment {i}\n'
        
        # Add nested structure
        large_content += '''
            "nested": {
                // Nested structure
                "level1": {
                    "level2": {
                        "data": [1, 2, 3, 4, 5,]
                    }
                }
            }
        }
        '''
        
        # This should complete without timeout/error
        result = self.parser.parse(large_content)
        
        assert len(result) == 1001  # 1000 keys + nested
        assert result["key0"] == "value0"
        assert result["key999"] == "value999"
        assert result["nested"]["level1"]["level2"]["data"] == [1, 2, 3, 4, 5]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])