#!/usr/bin/env python3
"""
Setup script for MCP Task Orchestrator
"""

import os
from setuptools import setup, find_packages

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

setup(
    name="mcp-task-orchestrator",
    version="2.0.0",
    author="Echoing Vesper",
    author_email="noreply@github.com",
    description="A Model Context Protocol server for task orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EchoingVesper/mcp-task-orchestrator",
    project_urls={
        "Homepage": "https://github.com/EchoingVesper/mcp-task-orchestrator",
        "Documentation": "https://github.com/EchoingVesper/mcp-task-orchestrator/blob/main/README.md",
        "Issues": "https://github.com/EchoingVesper/mcp-task-orchestrator/issues",
        "Releases": "https://github.com/EchoingVesper/mcp-task-orchestrator/releases",
        "Repository": "https://github.com/EchoingVesper/mcp-task-orchestrator",
    },
    keywords=["mcp", "ai", "task-orchestration", "claude", "automation", "llm", "workflow"],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "mcp_task_orchestrator": ["config/*.yaml"],
        "mcp_task_orchestrator_cli": ["config/*.yaml"],
        "": ["config/*.yaml"],  # Include config files from root
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[req for req in requirements if not req.startswith("pytest") and not req.startswith("#")],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0"],
        "cli": ["typer>=0.9.0", "rich>=13.0.0"],
    },
    entry_points={
        "console_scripts": [
            "mcp-task-orchestrator=mcp_task_orchestrator.__main__:main_sync",
            "mcp-task-orchestrator-cli=mcp_task_orchestrator_cli.__main__:main",
        ],
    },
)