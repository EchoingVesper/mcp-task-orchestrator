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
    version="1.2.0",
    author="Echoing Vesper",
    author_email="example@example.com",
    description="A Model Context Protocol server for task orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EchoingVesper/mcp-task-orchestrator",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "mcp_task_orchestrator": ["config/*.yaml"],
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-task-orchestrator=mcp_task_orchestrator.server:main",
            "mcp-task-orchestrator-cli=mcp_task_orchestrator_cli.cli:main",
        ],
    },
)