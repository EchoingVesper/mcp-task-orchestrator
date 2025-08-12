# MCP Task Orchestrator Commands Guide

Quick reference for all available commands in this project.

## PRP (Project Requirement Planning) Commands

### `/PRPs:prp-base-create [feature description]`
**Purpose**: Create comprehensive feature implementation PRPs with context engineering  
**When to use**: Starting new feature development with full planning  
**Example**: `/PRPs:prp-base-create user authentication system with OAuth2`

### `/PRPs:prp-base-execute @PRP-file.md`
**Purpose**: Execute a PRP with enhanced validation and orchestrator integration  
**When to use**: Implementing features from completed PRPs  
**Example**: `/PRPs:prp-base-execute @PRPs/user-auth-implementation.md`

### `/PRPs:prp-planning-create [rough idea]`
**Purpose**: Transform rough ideas into comprehensive PRDs with visual documentation  
**When to use**: Early ideation phase, need market research and user story development  
**Example**: `/PRPs:prp-planning-create real-time collaboration features`

### `/PRPs:prp-spec-create [transformation goal]`
**Purpose**: Create specification-driven PRPs for refactoring/transformation projects  
**When to use**: Modernizing existing code, architectural changes, migration projects  
**Example**: `/PRPs:prp-spec-create migrate database layer to async SQLAlchemy`

### `/PRPs:prp-spec-execute @SPEC-file.md`
**Purpose**: Execute specification-driven transformations with security validation  
**When to use**: Implementing architecture changes, refactoring projects  
**Example**: `/PRPs:prp-spec-execute @PRPs/async-db-migration-spec.md`

### `/PRPs:prp-task-create [specific task]`
**Purpose**: Create focused task PRPs for smaller implementations  
**When to use**: Bug fixes, small features, specific technical tasks  
**Example**: `/PRPs:prp-task-create add rate limiting to API endpoints`

### `/PRPs:prp-task-execute @task-file.md`
**Purpose**: Execute focused task implementations  
**When to use**: Implementing specific technical tasks or bug fixes  
**Example**: `/PRPs:prp-task-execute @PRPs/add-rate-limiting-task.md`

## Development Commands

### `/development:create-pr [PR title]`
**Purpose**: Create enhanced pull requests with security validation and comprehensive testing  
**When to use**: After completing feature implementation, ready to submit for review  
**Features**: 
- Project-specific code formatting (black, isort)
- Security scanning (bandit, safety) 
- Enhanced PR template with security sections
- Orchestrator integration checks
**Example**: `/development:create-pr feat: add user authentication system`

### `/development:debug-RCA [issue description]`
**Purpose**: Root cause analysis for debugging issues  
**When to use**: Investigating bugs, performance issues, or system failures  
**Example**: `/development:debug-RCA API response times increased after latest deployment`

### `/development:new-dev-branch [feature name]`
**Purpose**: Create and setup new development branch with proper naming  
**When to use**: Starting work on new features or bug fixes  
**Example**: `/development:new-dev-branch user-auth-oauth2`

### `/development:smart-commit [commit message]`
**Purpose**: Create intelligent commits with proper formatting and validation  
**When to use**: Committing code changes with enhanced commit messages  
**Example**: `/development:smart-commit fix rate limiting bug in API middleware`

## Git Operations Commands

### `/git-operations:conflict-resolver-general`
**Purpose**: General git merge conflict resolution assistance  
**When to use**: Resolving merge conflicts during branch merges or rebases  

### `/git-operations:conflict-resolver-specific [conflict description]`
**Purpose**: Specific conflict resolution with targeted guidance  
**When to use**: Complex merge conflicts requiring detailed analysis  
**Example**: `/git-operations:conflict-resolver-specific database schema conflicts in migration files`

### `/git-operations:smart-resolver [merge situation]`
**Purpose**: Intelligent merge conflict resolution with context awareness  
**When to use**: Complex merges requiring understanding of code context  
**Example**: `/git-operations:smart-resolver merging feature branch with updated main`

## Code Quality Commands

### `/code-quality:refactor-simple [code description]`
**Purpose**: Quick refactoring checks for Python code  
**When to use**: Improving code quality, readability, or performance  
**Example**: `/code-quality:refactor-simple database query optimization in user service`

### `/code-quality:review-general`
**Purpose**: General code review with best practices focus  
**When to use**: Pre-commit code quality checks  

### `/code-quality:review-staged-unstaged`
**Purpose**: Review both staged and unstaged changes  
**When to use**: Comprehensive review before committing changes  

## Usage Patterns

### 🚀 **New Feature Workflow**
1. `/PRPs:prp-planning-create [idea]` - Start with planning
2. `/PRPs:prp-base-create [refined feature]` - Create implementation PRP
3. `/PRPs:prp-base-execute @PRP-file.md` - Implement the feature
4. `/code-quality:review-staged-unstaged` - Quality check
5. `/development:create-pr [PR title]` - Submit for review

### 🔧 **Refactoring Workflow**  
1. `/PRPs:prp-spec-create [transformation goal]` - Plan the refactoring
2. `/PRPs:prp-spec-execute @SPEC-file.md` - Execute transformation
3. `/development:create-pr [PR title]` - Submit changes

### 🐛 **Bug Fix Workflow**
1. `/development:debug-RCA [issue]` - Understand the problem
2. `/PRPs:prp-task-create [fix description]` - Plan the fix
3. `/PRPs:prp-task-execute @task-file.md` - Implement fix
4. `/development:smart-commit [commit message]` - Commit fix

### 🚦 **Git Conflict Resolution**
1. `/git-operations:conflict-resolver-general` - General guidance
2. `/git-operations:conflict-resolver-specific [details]` - Specific help
3. `/git-operations:smart-resolver [situation]` - Intelligent resolution

## Project-Specific Features

All commands include:
- **Orchestrator Integration**: Automatic health checks and task coordination
- **Context Engineering**: References to PRPs/ai_docs/ enhanced documentation
- **Security-First Design**: Built-in security validation and scanning
- **Clean Architecture**: Follows project's layered architecture principles
- **Enhanced Validation**: Multi-stage validation frameworks
- **Commit Enforcement**: Automatic git integration following CLAUDE.md

## Quick Tips

- 📝 **Arguments**: Use descriptive arguments for better results
- 📁 **File References**: Use `@` prefix to reference specific files
- 🔒 **Security**: All commands include security considerations
- 🎯 **Context**: Commands automatically load relevant project context
- ⚡ **Orchestrator**: Commands verify orchestrator health before proceeding
- 🏗️ **Architecture**: All implementations follow Clean Architecture patterns

**Pro Tip**: Start with planning commands (prp-planning-create, prp-spec-create) for better implementation outcomes!