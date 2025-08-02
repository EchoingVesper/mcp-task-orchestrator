

# Main Title

This file contains various markdown structures to test edge cases.

#

# Code Blocks

```python
def example():
    

# This is inside a code block

    

# Should not be modified

    return "Hello 

# World"

```text

#

# Lists Without Proper Spacing

- Item 1

- Item 2

1. Ordered item

1. Another ordered item

#

# Long Lines

This is a very long line that exceeds the 120 character limit and should be wrapped by the line length fixer to ensure it meets the markdown linting requirements for maximum line length.

#

# Nested Markdown

```text
markdown

# This is markdown inside markdown

#

# Subsection

- List item

- Another item

```mermaid
graph TD
    A --> B
```text

#

# Tables

| Column 1 | Column 2 with a very long header that might exceed line limits |
|----------|----------------------------------------------------------------|
| Data     | More data that could also be quite long and potentially problematic |

#

# HTML Elements

<details>
<summary>Click to expand</summary>

This content should be preserved as HTML is allowed.

</details>
