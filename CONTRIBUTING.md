# Contributing to MCP Task Orchestrator

Thank you for your interest in contributing to the MCP Task Orchestrator! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

There are many ways to contribute to the MCP Task Orchestrator:

1. **Reporting Bugs**: If you find a bug, please create an issue with detailed information about how to reproduce it.
2. **Suggesting Enhancements**: Have an idea for a new feature? Create an issue to suggest it.
3. **Code Contributions**: Submit pull requests with bug fixes or new features.
4. **Documentation**: Help improve the documentation by fixing errors or adding examples.
5. **Testing**: Help test the software on different platforms and configurations.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate.
2. Add or update tests for any new or modified functionality.
3. Ensure all tests pass before submitting your pull request.
4. Update the CHANGELOG.md with details of your changes.
5. Submit your pull request against the `main` branch.

## Coding Standards

- Follow PEP 8 style guidelines for Python code.
- Write docstrings for all functions, classes, and modules.
- Include type hints where appropriate.
- Write unit tests for new functionality.
- Keep functions small and focused on a single responsibility.
- Use meaningful variable and function names.

## Testing

- Run tests with pytest:
  ```bash
  pytest
  ```
- Ensure your changes work on all supported platforms (Windows, macOS, Linux).
- Test with different MCP clients if possible.

## Documentation

- Keep documentation up-to-date with code changes.
- Use clear, concise language.
- Include examples where appropriate.
- Document any new configuration options or features.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.

Thank you for contributing to the MCP Task Orchestrator!