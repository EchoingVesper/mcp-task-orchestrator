"""
Markdown Parser for understanding document structure.

Provides proper markdown parsing to understand context and structure
instead of relying on simple regex replacements.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Set


class BlockType(Enum):
    """Types of markdown blocks."""
    TEXT = "text"
    HEADING = "heading"
    CODE_BLOCK = "code_block"
    LIST = "list"
    QUOTE = "quote"
    HTML = "html"
    YAML_FRONTMATTER = "yaml_frontmatter"
    HORIZONTAL_RULE = "horizontal_rule"


@dataclass
class MarkdownBlock:
    """Represents a block of markdown content."""
    type: BlockType
    content: str
    start_line: int
    end_line: int
    level: Optional[int] = None  # For headings and lists
    language: Optional[str] = None  # For code blocks
    
    
class MarkdownParser:
    """Parses markdown content and understands document structure."""
    
    def __init__(self):
        self.blocks: List[MarkdownBlock] = []
        self.lines: List[str] = []
        self.code_block_ranges: List[Tuple[int, int]] = []
        
    def parse(self, content: str) -> List[MarkdownBlock]:
        """
        Parse markdown content into structured blocks.
        
        Args:
            content: Markdown content as string
            
        Returns:
            List of MarkdownBlock objects
        """
        self.lines = content.split('\n')
        self.blocks = []
        self.code_block_ranges = []
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            
            # Check for YAML frontmatter
            if i == 0 and line.strip() == '---':
                i = self._parse_yaml_frontmatter(i)
                continue
                
            # Check for fenced code blocks
            if line.strip().startswith('```'):
                i = self._parse_code_block(i)
                continue
                
            # Check for headings
            if line.strip().startswith('#'):
                self._parse_heading(i)
                i += 1
                continue
                
            # Check for lists
            if self._is_list_item(line):
                i = self._parse_list(i)
                continue
                
            # Check for quotes
            if line.strip().startswith('>'):
                i = self._parse_quote(i)
                continue
                
            # Check for horizontal rules
            if re.match(r'^[ \t]*[-*_][ \t]*[-*_][ \t]*[-*_][ \t]*$', line):
                self._parse_horizontal_rule(i)
                i += 1
                continue
                
            # Check for HTML blocks
            if line.strip().startswith('<'):
                i = self._parse_html_block(i)
                continue
                
            # Default to text block
            i = self._parse_text_block(i)
            
        return self.blocks
    
    def _parse_yaml_frontmatter(self, start_line: int) -> int:
        """Parse YAML frontmatter block."""
        i = start_line + 1
        while i < len(self.lines):
            if self.lines[i].strip() == '---':
                content = '\n'.join(self.lines[start_line:i+1])
                self.blocks.append(MarkdownBlock(
                    type=BlockType.YAML_FRONTMATTER,
                    content=content,
                    start_line=start_line,
                    end_line=i
                ))
                return i + 1
            i += 1
        return i
    
    def _parse_code_block(self, start_line: int) -> int:
        """Parse fenced code block."""
        start_line_content = self.lines[start_line]
        fence_char = start_line_content.strip()[0]  # ` or ~
        fence_length = len(start_line_content) - len(start_line_content.lstrip(fence_char))
        
        # Extract language
        language = start_line_content.strip()[3:].strip()
        
        i = start_line + 1
        while i < len(self.lines):
            line = self.lines[i]
            if line.strip().startswith(fence_char * fence_length):
                content = '\n'.join(self.lines[start_line:i+1])
                self.blocks.append(MarkdownBlock(
                    type=BlockType.CODE_BLOCK,
                    content=content,
                    start_line=start_line,
                    end_line=i,
                    language=language or None
                ))
                self.code_block_ranges.append((start_line, i))
                return i + 1
            i += 1
        return i
    
    def _parse_heading(self, line_num: int):
        """Parse heading line."""
        line = self.lines[line_num]
        level = len(line) - len(line.lstrip('#'))
        
        self.blocks.append(MarkdownBlock(
            type=BlockType.HEADING,
            content=line,
            start_line=line_num,
            end_line=line_num,
            level=level
        ))
    
    def _parse_list(self, start_line: int) -> int:
        """Parse list block."""
        i = start_line
        while i < len(self.lines) and (self._is_list_item(self.lines[i]) or self._is_list_continuation(self.lines[i])):
            i += 1
        
        content = '\n'.join(self.lines[start_line:i])
        self.blocks.append(MarkdownBlock(
            type=BlockType.LIST,
            content=content,
            start_line=start_line,
            end_line=i-1
        ))
        return i
    
    def _parse_quote(self, start_line: int) -> int:
        """Parse quote block."""
        i = start_line
        while i < len(self.lines) and self.lines[i].strip().startswith('>'):
            i += 1
        
        content = '\n'.join(self.lines[start_line:i])
        self.blocks.append(MarkdownBlock(
            type=BlockType.QUOTE,
            content=content,
            start_line=start_line,
            end_line=i-1
        ))
        return i
    
    def _parse_horizontal_rule(self, line_num: int):
        """Parse horizontal rule."""
        self.blocks.append(MarkdownBlock(
            type=BlockType.HORIZONTAL_RULE,
            content=self.lines[line_num],
            start_line=line_num,
            end_line=line_num
        ))
    
    def _parse_html_block(self, start_line: int) -> int:
        """Parse HTML block."""
        # Simple HTML block detection
        i = start_line + 1
        content = '\n'.join(self.lines[start_line:i])
        self.blocks.append(MarkdownBlock(
            type=BlockType.HTML,
            content=content,
            start_line=start_line,
            end_line=i-1
        ))
        return i
    
    def _parse_text_block(self, start_line: int) -> int:
        """Parse text block."""
        i = start_line
        while i < len(self.lines):
            line = self.lines[i]
            if (line.strip().startswith('#') or 
                line.strip().startswith('```') or
                self._is_list_item(line) or
                line.strip().startswith('>') or
                line.strip().startswith('<')):
                break
            i += 1
        
        if i > start_line:
            content = '\n'.join(self.lines[start_line:i])
            self.blocks.append(MarkdownBlock(
                type=BlockType.TEXT,
                content=content,
                start_line=start_line,
                end_line=i-1
            ))
        return i
    
    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item."""
        stripped = line.strip()
        # Unordered list
        if re.match(r'^[-*+]\s+', stripped):
            return True
        # Ordered list
        if re.match(r'^\d+\.\s+', stripped):
            return True
        return False
    
    def _is_list_continuation(self, line: str) -> bool:
        """Check if line is a list continuation."""
        return line.startswith('  ') or line.startswith('\t') or line.strip() == ''
    
    def is_inside_code_block(self, line_num: int) -> bool:
        """
        Check if a line is inside a code block.
        
        Args:
            line_num: Line number to check
            
        Returns:
            True if line is inside a code block
        """
        for start, end in self.code_block_ranges:
            if start <= line_num <= end:
                return True
        return False
    
    def get_headings(self) -> List[MarkdownBlock]:
        """Get all heading blocks."""
        return [block for block in self.blocks if block.type == BlockType.HEADING]
    
    def get_code_blocks(self) -> List[MarkdownBlock]:
        """Get all code blocks."""
        return [block for block in self.blocks if block.type == BlockType.CODE_BLOCK]
    
    def find_duplicate_headings(self) -> Dict[str, List[MarkdownBlock]]:
        """Find duplicate heading content."""
        headings = self.get_headings()
        heading_map: Dict[str, List[MarkdownBlock]] = {}
        
        for heading in headings:
            # Extract heading text without # symbols
            text = heading.content.strip().lstrip('#').strip()
            if text in heading_map:
                heading_map[text].append(heading)
            else:
                heading_map[text] = [heading]
        
        # Return only duplicates
        return {text: blocks for text, blocks in heading_map.items() if len(blocks) > 1}
    
    def get_h1_headings(self) -> List[MarkdownBlock]:
        """Get all H1 headings."""
        return [block for block in self.blocks if block.type == BlockType.HEADING and block.level == 1]