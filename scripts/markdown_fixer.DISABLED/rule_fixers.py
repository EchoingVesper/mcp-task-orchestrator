"""
Rule Fixers for specific markdownlint violations.

Implements fixes for common markdownlint rules while preserving content integrity.
"""

import re
from typing import List, Tuple, Dict, Set
from .parser import MarkdownParser, BlockType


class RuleFixer:
    """Fixes markdownlint rule violations."""
    
    def __init__(self):
        self.parser = MarkdownParser()
    
    def fix_md025_multiple_h1s(self, content: str) -> str:
        """
        Fix MD025: Multiple top-level headings in the same document.
        
        Converts standalone '#' lines to '##' and additional H1s to H2s.
        """
        lines = content.split('\n')
        
        # Convert standalone '#' to '##'
        for i, line in enumerate(lines):
            if line.strip() == '#':
                lines[i] = '##'
        
        # Convert additional H1s to H2s (keep first real H1)
        h1_count = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('# ') and len(stripped) > 2:
                h1_count += 1
                if h1_count > 1:
                    # Convert to H2
                    lines[i] = '#' + line
        
        return '\n'.join(lines)
    
    def fix_md022_heading_blanks(self, content: str) -> str:
        """
        Fix MD022: Headings should be surrounded by blank lines.
        
        Ensures proper blank lines above and below headings.
        """
        lines = content.split('\n')
        result = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if current line is a heading
            if line.strip().startswith('#') and (' ' in line.strip() or line.strip() == '#'):
                # Check if we need blank line before
                if (i > 0 and 
                    result and 
                    result[-1].strip() != '' and
                    not result[-1].strip().startswith('#')):
                    result.append('')  # Add blank line before
                
                result.append(line)
                
                # Check if we need blank line after
                if (i < len(lines) - 1 and 
                    i + 1 < len(lines) and
                    lines[i + 1].strip() != '' and
                    not lines[i + 1].strip().startswith('#')):
                    result.append('')  # Add blank line after
            else:
                result.append(line)
            
            i += 1
        
        return '\n'.join(result)
    
    def fix_md024_duplicate_headings(self, content: str) -> str:
        """
        Fix MD024: Multiple headings with the same content.
        
        Renames duplicate headings by adding context or numbering.
        """
        lines = content.split('\n')
        seen_headings = {}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                # Extract heading text
                level = len(stripped) - len(stripped.lstrip('#'))
                text = stripped.lstrip('#').strip()
                
                if text in seen_headings:
                    # This is a duplicate, rename it
                    seen_headings[text] += 1
                    if text == '':
                        new_text = f"Section {seen_headings[text]}"
                    else:
                        new_text = f"{text} {seen_headings[text]}"
                    prefix = '#' * level
                    lines[i] = f"{prefix} {new_text}"
                else:
                    seen_headings[text] = 1
        
        return '\n'.join(lines)
    
    def fix_md013_line_length(self, content: str, max_length: int = 120) -> str:
        """
        Fix MD013: Line length violations.
        
        Wraps long lines while preserving code blocks and tables.
        """
        lines = content.split('\n')
        result = []
        in_code_block = False
        
        for line in lines:
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                result.append(line)
                continue
            
            # Skip if inside code block
            if in_code_block:
                result.append(line)
                continue
            
            # Skip tables (they're excluded in config)
            if '|' in line:
                result.append(line)
                continue
            
            # Skip headings (they're excluded in config)  
            if line.strip().startswith('#'):
                result.append(line)
                continue
            
            # Wrap long lines
            if len(line) > max_length:
                wrapped = self._wrap_line(line, max_length)
                result.extend(wrapped)
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def fix_md009_trailing_spaces(self, content: str) -> str:
        """
        Fix MD009: No trailing spaces.
        
        Removes trailing whitespace from all lines.
        """
        lines = content.split('\n')
        return '\n'.join(line.rstrip() for line in lines)
    
    def fix_md032_list_blanks(self, content: str) -> str:
        """
        Fix MD032: Lists should be surrounded by blank lines.
        
        Ensures proper blank lines around lists.
        """
        lines = content.split('\n')
        result = []
        in_list = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            is_list_item = (stripped.startswith('- ') or 
                           stripped.startswith('* ') or 
                           stripped.startswith('+ ') or
                           bool(re.match(r'^\d+\.\s+', stripped)))
            
            if is_list_item and not in_list:
                # Starting a list
                if result and result[-1].strip() != '':
                    result.append('')  # Add blank line before
                in_list = True
            elif not is_list_item and not stripped.startswith('  ') and stripped != '' and in_list:
                # Ending a list
                if result and result[-1].strip() != '':
                    result.append('')  # Add blank line after
                in_list = False
            
            result.append(line)
        
        return '\n'.join(result)
    
    def fix_md031_code_block_blanks(self, content: str) -> str:
        """
        Fix MD031: Fenced code blocks should be surrounded by blank lines.
        
        Ensures proper blank lines around code blocks.
        """
        lines = content.split('\n')
        result = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                # Check if we need blank line before code block
                if (i > 0 and result and result[-1].strip() != ''):
                    result.append('')
                
                result.append(line)
                
                # For closing code fence, check if we need blank line after
                # Simple heuristic: if this looks like a closing fence and next line exists
                if (line.strip() == '```' and 
                    i < len(lines) - 1 and 
                    lines[i + 1].strip() != ''):
                    result.append('')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def fix_md029_ordered_lists(self, content: str) -> str:
        """
        Fix MD029: Ordered list item prefix.
        
        According to config, style is "ordered" which means 1. 2. 3. etc.
        """
        lines = content.split('\n')
        result = []
        
        for line in lines:
            # Skip if inside code block
            if self.parser.is_inside_code_block(len(result)):
                result.append(line)
                continue
            
            # Fix ordered list numbering
            stripped = line.strip()
            if re.match(r'^\d+\.\s+', stripped):
                # Extract indentation and content
                indent = line[:len(line) - len(line.lstrip())]
                content_part = stripped[stripped.find('.') + 1:].strip()
                
                # Count current list position
                list_num = self._count_list_position(result)
                result.append(f"{indent}{list_num}. {content_part}")
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def fix_md040_code_language(self, content: str) -> str:
        """
        Fix MD040: Fenced code blocks should have a language specified.
        
        Adds 'text' language to unlabeled code blocks.
        """
        lines = content.split('\n')
        result = []
        
        for line in lines:
            if line.strip() == '```':
                result.append('```text')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def fix_md047_single_trailing_newline(self, content: str) -> str:
        """
        Fix MD047: Files should end with a single newline character.
        """
        return content.rstrip() + '\n'
    
    def _wrap_line(self, line: str, max_length: int) -> List[str]:
        """
        Wrap a long line at word boundaries.
        
        Args:
            line: Line to wrap
            max_length: Maximum line length
            
        Returns:
            List of wrapped lines
        """
        if len(line) <= max_length:
            return [line]
        
        # Preserve indentation
        indent = line[:len(line) - len(line.lstrip())]
        content = line.strip()
        
        wrapped = []
        current_line = indent
        
        for word in content.split():
            # Check if adding word would exceed limit
            test_line = current_line + (' ' if current_line.strip() else '') + word
            
            if len(test_line) <= max_length:
                current_line = test_line
            else:
                # Start new line
                if current_line.strip():
                    wrapped.append(current_line)
                current_line = indent + word
        
        if current_line.strip():
            wrapped.append(current_line)
        
        return wrapped
    
    def _count_list_position(self, previous_lines: List[str]) -> int:
        """
        Count the position in current ordered list.
        
        Args:
            previous_lines: Lines processed so far
            
        Returns:
            Next list number
        """
        count = 0
        for line in reversed(previous_lines):
            stripped = line.strip()
            if re.match(r'^\d+\.\s+', stripped):
                count += 1
            elif stripped == '' or line.startswith('  '):
                # Continue counting through blank lines and indented content
                continue
            else:
                # Hit non-list content, stop counting
                break
        
        return count + 1
    
    def apply_all_fixes(self, content: str) -> str:
        """
        Apply all markdown fixes to content.
        
        Args:
            content: Original markdown content
            
        Returns:
            Fixed markdown content
        """
        # Apply fixes in order of importance
        content = self.fix_md047_single_trailing_newline(content)
        content = self.fix_md009_trailing_spaces(content)
        content = self.fix_md025_multiple_h1s(content)
        content = self.fix_md024_duplicate_headings(content)
        content = self.fix_md022_heading_blanks(content)
        content = self.fix_md032_list_blanks(content)
        content = self.fix_md031_code_block_blanks(content)
        content = self.fix_md029_ordered_lists(content)
        content = self.fix_md040_code_language(content)
        content = self.fix_md013_line_length(content)
        
        return content