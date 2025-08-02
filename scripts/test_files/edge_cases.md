---
title: "Test Document with YAML Frontmatter"
date: 2024-01-07
author: "Test Author"
---

# Test Document

This file tests various edge cases.

#

# Duplicate Headings

#

#

# Configuration

Some content about configuration.

#

#

# Configuration

More content with the same heading (should trigger MD024).

#

# Trailing Spaces   

This line has trailing spaces that should be removed.

#

# Code Blocks Without Language

```text
This code block has no language specified
Should get 'text' added automatically
```text

#

# Empty Headings

#

#

#

This should be handled properly.

#

# Lists

- Item without proper spacing above

- Another item

Final content without proper spacing below list.
