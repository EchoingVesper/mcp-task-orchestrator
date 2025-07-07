

# PyPI Publishing Guide for MCP Task Orchestrator

#

# Prerequisites

- PyPI account (https://pypi.org/account/register/)

- 2FA enabled on your PyPI account

- API token from PyPI

#

# Setup Publishing Tools

```bash
pip install --upgrade pip setuptools wheel twine

```text

#

# Build the Package

```text
bash

# Clean previous builds

rm -rf dist/ build/ *.egg-info/

# Build distribution packages

python setup.py sdist bdist_wheel

```text

#

# Test with TestPyPI (Optional but Recommended)

```text
bash

# Upload to test repository

twine upload --repository testpypi dist/*

# Test installation from TestPyPI

pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-task-orchestrator

```text

#

# Publish to PyPI

```text
bash

# Upload to PyPI (will prompt for API token)

twine upload dist/*

# Or use token directly

twine upload -u __token__ -p <your-api-token> dist/*

```text

#

# Verify Installation

```text
bash

# Install from PyPI

pip install mcp-task-orchestrator

# For development install with extras

pip install mcp-task-orchestrator[dev]
```text

#

# Updating the Package

1. Update version in `setup.py`

2. Update version in documentation

3. Create git tag: `git tag v1.5.2`

4. Rebuild and upload as above

#

# Important Notes

- Package name `mcp-task-orchestrator` appears to be available on PyPI

- First upload establishes ownership

- Use semantic versioning (MAJOR.MINOR.PATCH)

- Always test with TestPyPI first for new releases
