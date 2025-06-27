# MCP Server Configuration Documentation Index

This directory contains comprehensive documentation on MCP (Model Context Protocol) server configuration best practices, focusing on PyPI package-based servers and cross-tool compatibility.

## Documentation Structure

### Core Documentation

1. **[MCP_PROTOCOL_OVERVIEW.md](./MCP_PROTOCOL_OVERVIEW.md)**
   - Introduction to Model Context Protocol
   - Core concepts and architecture
   - Protocol standards and specifications
   - Security considerations

2. **[CONFIGURATION_BEST_PRACTICES.md](./CONFIGURATION_BEST_PRACTICES.md)**
   - Official configuration schema
   - Python package-based server configuration
   - PATH and environment variable handling
   - Development vs production configurations
   - Common pitfalls and solutions

3. **[TOOL_SPECIFIC_CONFIGURATIONS.md](./TOOL_SPECIFIC_CONFIGURATIONS.md)**
   - Claude Desktop configuration
   - Claude Code configuration (WSL and native Linux)
   - Cursor IDE configuration
   - Windsurf IDE configuration
   - Roo Code configuration
   - Cline configuration
   - GitHub Copilot MCP support
   - Other AI coding tools

4. **[PYPI_PACKAGE_SERVERS.md](./PYPI_PACKAGE_SERVERS.md)**
   - Installing PyPI-based MCP servers
   - Virtual environment considerations
   - Python interpreter path handling
   - Module execution patterns
   - Dependency management

5. **[UNIVERSAL_INSTALLATION.md](./UNIVERSAL_INSTALLATION.md)**
   - Cross-platform installation strategies
   - Universal installer approaches
   - Registry-based configuration systems
   - Automated detection and setup
   - Troubleshooting multi-tool setups

6. **[CONFIGURATION_EXAMPLES.md](./CONFIGURATION_EXAMPLES.md)**
   - Real-world configuration examples
   - Working configurations for popular servers
   - Platform-specific examples
   - Debugging configuration issues

## Quick Reference

### Key Findings Summary

- **Use absolute paths** in all configurations
- **Python module execution** pattern: `python -m package.module`
- **Minimal environment variables** - only add what's necessary
- **Tool-specific paths** vary by platform and installation method
- **Validation with MCP Inspector** is recommended

### Tool Support Matrix

| Tool | MCP Support | Configuration Location | PyPI Package Support |
|------|-------------|----------------------|---------------------|
| Claude Desktop | Full | Platform-specific config.json | Yes |
| Claude Code | Full | Uses Claude Desktop config | Yes |
| Cursor | Full | Settings → MCP | Yes |
| Windsurf | Full | Settings → MCP | Yes |
| Roo Code | Limited | TBD | TBD |
| Cline | Limited | TBD | TBD |
| GitHub Copilot | Preview (v1.99+) | VS Code settings | Yes |

### Common Issues

1. **Server not appearing in tools**
   - Check absolute paths
   - Verify Python installation
   - Validate with MCP Inspector

2. **Import errors**
   - Ensure package installed in correct Python environment
   - Check PYTHONPATH if needed

3. **Permission errors**
   - File system permissions
   - Environment variable access

## Related Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Community MCP Servers](https://github.com/modelcontextprotocol/servers)