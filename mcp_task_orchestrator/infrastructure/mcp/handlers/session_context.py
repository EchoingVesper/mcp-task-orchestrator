"""
Session Context Management for Agent-to-Agent Orchestration

This module provides functionality for passing session context between agents,
enabling multi-agent collaboration on the same orchestration session.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class SessionContextManager:
    """
    Manages session context for cross-agent orchestration.
    
    This allows spawned agents to inherit and work with the same
    orchestration session as their parent agent.
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        """Initialize session context manager."""
        self.working_dir = working_dir or Path.cwd()
        self.task_orchestrator_dir = self.working_dir / ".task_orchestrator"
        self.active_session_file = self.task_orchestrator_dir / ".active_session"
        
    def set_active_session(self, session_id: str) -> bool:
        """
        Mark a session as the active session for this workspace.
        
        Args:
            session_id: Session ID to mark as active
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.task_orchestrator_dir.mkdir(parents=True, exist_ok=True)
            
            # Verify session file exists
            session_file = self.task_orchestrator_dir / f"{session_id}.json"
            if not session_file.exists():
                logger.error(f"Session file not found: {session_id}")
                return False
            
            # Write active session marker
            active_session_data = {
                "session_id": session_id,
                "activated_at": datetime.now(timezone.utc).isoformat(),
                "working_directory": str(self.working_dir)
            }
            
            with open(self.active_session_file, 'w') as f:
                json.dump(active_session_data, f, indent=2)
            
            logger.info(f"Set active session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set active session: {e}")
            return False
    
    def get_active_session(self) -> Optional[str]:
        """
        Get the currently active session ID.
        
        Returns:
            Session ID if an active session exists, None otherwise
        """
        try:
            if not self.active_session_file.exists():
                return None
                
            with open(self.active_session_file, 'r') as f:
                data = json.load(f)
                
            session_id = data.get("session_id")
            
            # Verify session still exists
            if session_id:
                session_file = self.task_orchestrator_dir / f"{session_id}.json"
                if session_file.exists():
                    return session_id
                else:
                    logger.warning(f"Active session file missing: {session_id}")
                    
        except Exception as e:
            logger.error(f"Failed to get active session: {e}")
            
        return None
    
    def get_session_context_for_agent(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get session context formatted for passing to a spawned agent.
        
        This creates a context object that can be passed to the Task tool
        to ensure the spawned agent works within the same orchestration session.
        
        Args:
            session_id: Specific session ID to use (defaults to active session)
            
        Returns:
            Context dictionary for agent spawning
        """
        # Use provided session_id or get active session
        if not session_id:
            session_id = self.get_active_session()
            
        if not session_id:
            return {
                "orchestrator_session": None,
                "message": "No active orchestration session"
            }
        
        # Load session data
        session_file = self.task_orchestrator_dir / f"{session_id}.json"
        if not session_file.exists():
            return {
                "orchestrator_session": None,
                "message": f"Session not found: {session_id}"
            }
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Build context for agent
            context = {
                "orchestrator_session": session_id,
                "working_directory": session_data.get("working_directory", str(self.working_dir)),
                "capabilities": session_data.get("capabilities", {}),
                "database_status": session_data.get("database_status", "unknown"),
                "instructions": (
                    f"You are working within orchestration session '{session_id}'. "
                    "Use the following tools to interact with the orchestrator:\n"
                    "- orchestrator_resume_session: Resume the session if needed\n"
                    "- orchestrator_query_tasks: Find tasks to work on\n"
                    "- orchestrator_execute_task: Execute specific tasks\n"
                    "- orchestrator_complete_task: Mark tasks as complete\n"
                    "- orchestrator_get_status: Check overall progress"
                ),
                "session_file": str(session_file)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to load session context: {e}")
            return {
                "orchestrator_session": None,
                "message": f"Failed to load session: {str(e)}"
            }
    
    def create_agent_prompt_with_session(self, 
                                        base_prompt: str,
                                        session_id: Optional[str] = None) -> str:
        """
        Create an agent prompt that includes session context.
        
        Args:
            base_prompt: The base task prompt for the agent
            session_id: Optional session ID (defaults to active session)
            
        Returns:
            Enhanced prompt with session context
        """
        context = self.get_session_context_for_agent(session_id)
        
        if context.get("orchestrator_session"):
            session_prompt = f"""
## Orchestration Session Context

You are working within an active orchestration session: {context['orchestrator_session']}

### Session Details:
- Working Directory: {context['working_directory']}
- Database Status: {context['database_status']}

### Available Orchestrator Tools:
First, resume the session if needed:
```
orchestrator_resume_session(session_id="{context['orchestrator_session']}")
```

Then use these tools to work with tasks:
- `orchestrator_query_tasks()` - Find tasks assigned to you or available
- `orchestrator_execute_task(task_id)` - Get execution context for a task
- `orchestrator_complete_task(task_id, summary, detailed_work)` - Complete tasks
- `orchestrator_get_status()` - Check overall session progress

### Your Task:
{base_prompt}

Remember to coordinate with the orchestrator throughout your work.
"""
            return session_prompt
        else:
            # No active session, return base prompt with note
            return f"""
{base_prompt}

Note: No active orchestration session found. Working independently.
"""


def get_session_context_manager(working_dir: Optional[Path] = None) -> SessionContextManager:
    """Get or create a session context manager instance."""
    return SessionContextManager(working_dir)


# Environment variable support for session passing
def export_session_to_env(session_id: str) -> bool:
    """
    Export session ID to environment variable for child processes.
    
    Args:
        session_id: Session ID to export
        
    Returns:
        True if successful
    """
    try:
        os.environ["MCP_ORCHESTRATOR_SESSION"] = session_id
        os.environ["MCP_ORCHESTRATOR_WORKSPACE"] = str(Path.cwd())
        return True
    except Exception as e:
        logger.error(f"Failed to export session to environment: {e}")
        return False


def get_session_from_env() -> Optional[str]:
    """
    Get session ID from environment variable.
    
    Returns:
        Session ID if set in environment, None otherwise
    """
    return os.environ.get("MCP_ORCHESTRATOR_SESSION")