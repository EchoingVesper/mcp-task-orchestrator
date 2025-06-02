"""
Enhanced server implementation with streaming artifact support and partial response recovery.

This module enhances the MCP server to detect potential partial responses and provide
recovery mechanisms using the streaming artifact system.
"""

import asyncio
import json
import os
import logging
import hashlib
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from mcp import types
from mcp.server import Server

from .streaming_artifacts import StreamingArtifactManager, StreamingSession
from .artifacts import ArtifactManager

logger = logging.getLogger("mcp_task_orchestrator.enhanced_server")


class EnhancedArtifactServer:
    """Enhanced server with streaming artifact support and partial response recovery."""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.getcwd()
        self.streaming_manager = StreamingArtifactManager(self.base_dir)
        self.legacy_manager = ArtifactManager(self.base_dir)
        
        # Response analysis patterns for detecting truncation
        self.truncation_indicators = [
            r'(?:\.\.\.|…)$',  # Ending with ellipsis
            r'[A-Za-z0-9][^.!?]*$',  # Ending mid-sentence (no punctuation)
            r'```\s*$',  # Unclosed code blocks
            r'[-*+]\s*$',  # Unfinished list items
            r'\s+$',  # Ending with just whitespace
            r'[,;:]\s*$',  # Ending with incomplete punctuation
        ]
        
        # Content analysis patterns for completion detection
        self.completion_indicators = [
            r'.*[.!?]\s*$',  # Ends with proper punctuation
            r'.*```\s*$',  # Closed code block
            r'.*\*\*Summary\*\*.*$',  # Contains summary section
            r'.*\*\*Conclusion\*\*.*$',  # Contains conclusion
            r'.*---\s*$',  # Ends with horizontal rule
        ]
    
    async def enhanced_complete_subtask(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced subtask completion with streaming artifact support and partial response detection.
        
        This method:
        1. Analyzes the response for potential truncation
        2. Creates streaming artifacts for robust storage
        3. Provides recovery mechanisms for partial responses
        4. Falls back to legacy method if needed
        """
        task_id = args["task_id"]
        summary = args["summary"]
        detailed_work = args["detailed_work"]
        file_paths = args.get("file_paths", [])
        artifact_type = args.get("artifact_type", "general")
        next_action = args["next_action"]
        
        # Analyze response for potential issues
        response_analysis = await self._analyze_response_quality(detailed_work, task_id)
        
        try:
            if response_analysis["is_likely_complete"]:
                # Response appears complete - use streaming storage for robustness
                result = await self._store_complete_response(
                    task_id, summary, detailed_work, file_paths, artifact_type, next_action
                )
                result.update({
                    "response_analysis": response_analysis,
                    "storage_method": "streaming_complete"
                })
                return result
            else:
                # Response appears incomplete - create partial artifact and prepare for resumption
                result = await self._handle_partial_response(
                    task_id, summary, detailed_work, file_paths, artifact_type, next_action, response_analysis
                )
                result.update({
                    "response_analysis": response_analysis,
                    "storage_method": "partial_with_resumption"
                })
                return result
                
        except Exception as e:
            logger.error(f"Error in enhanced completion for task {task_id}: {str(e)}")
            
            # Fallback to legacy method
            try:
                logger.info(f"Falling back to legacy method for task {task_id}")
                legacy_result = self.legacy_manager.store_artifact(
                    task_id=task_id,
                    summary=summary,
                    detailed_work=detailed_work,
                    file_paths=file_paths,
                    artifact_type=artifact_type
                )
                
                return {
                    "task_id": task_id,
                    "status": "completed_with_fallback",
                    "artifact_created": True,
                    "artifact_info": legacy_result,
                    "storage_method": "legacy_fallback",
                    "warning": f"Enhanced storage failed: {str(e)}",
                    "response_analysis": response_analysis
                }
            except Exception as fallback_error:
                logger.error(f"Both enhanced and legacy methods failed for task {task_id}: {str(fallback_error)}")
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": f"Enhanced error: {str(e)}, Legacy error: {str(fallback_error)}",
                    "results_recorded": False,
                    "response_analysis": response_analysis
                }
    
    async def _analyze_response_quality(self, content: str, task_id: str) -> Dict[str, Any]:
        """Analyze response content to detect potential truncation or incompleteness.
        
        Args:
            content: Response content to analyze
            task_id: Task ID for context
            
        Returns:
            Analysis results with recommendations
        """
        analysis = {
            "is_likely_complete": True,
            "confidence_score": 1.0,
            "detected_issues": [],
            "content_statistics": {},
            "recommendations": []
        }
        
        # Basic content statistics
        analysis["content_statistics"] = {
            "character_count": len(content),
            "word_count": len(content.split()),
            "line_count": len(content.splitlines()),
            "code_block_count": content.count("```"),
            "list_item_count": len(re.findall(r'^[-*+]\s', content, re.MULTILINE))
        }
        
        # Check for truncation indicators
        for pattern in self.truncation_indicators:
            if re.search(pattern, content.strip(), re.MULTILINE | re.DOTALL):
                analysis["detected_issues"].append({
                    "type": "truncation_indicator",
                    "pattern": pattern,
                    "description": "Content appears to end abruptly"
                })
                analysis["confidence_score"] -= 0.3
        
        # Check for completion indicators
        completion_found = False
        for pattern in self.completion_indicators:
            if re.search(pattern, content.strip(), re.MULTILINE | re.DOTALL):
                completion_found = True
                break
        
        if not completion_found:
            analysis["detected_issues"].append({
                "type": "missing_completion_indicators",
                "description": "Content lacks typical completion patterns"
            })
            analysis["confidence_score"] -= 0.2
        
        # Check for unbalanced elements
        unbalanced_issues = self._check_unbalanced_elements(content)
        if unbalanced_issues:
            analysis["detected_issues"].extend(unbalanced_issues)
            analysis["confidence_score"] -= 0.2 * len(unbalanced_issues)
        
        # Check content length expectations
        if analysis["content_statistics"]["character_count"] < 100:
            analysis["detected_issues"].append({
                "type": "suspiciously_short",
                "description": "Content is very short for a detailed work artifact"
            })
            analysis["confidence_score"] -= 0.4
        
        # Final determination
        analysis["is_likely_complete"] = analysis["confidence_score"] > 0.6
        
        # Generate recommendations
        if not analysis["is_likely_complete"]:
            analysis["recommendations"] = [
                "Consider this a partial response",
                "Store as temporary artifact with resumption capability",
                "Prompt user to continue or confirm completion",
                "Check for network interruption or token limits"
            ]
        else:
            analysis["recommendations"] = [
                "Content appears complete",
                "Safe to store as final artifact",
                "Proceed with normal completion workflow"
            ]
        
        logger.info(f"Response analysis for task {task_id}: confidence={analysis['confidence_score']:.2f}, complete={analysis['is_likely_complete']}")
        return analysis
    
    def _check_unbalanced_elements(self, content: str) -> List[Dict[str, str]]:
        """Check for unbalanced elements that might indicate truncation."""
        issues = []
        
        # Check for unbalanced code blocks
        code_block_count = content.count("```")
        if code_block_count % 2 != 0:
            issues.append({
                "type": "unbalanced_code_blocks",
                "description": f"Found {code_block_count} code block markers (should be even)"
            })
        
        # Check for unbalanced parentheses, brackets, braces
        balancing_chars = {
            '(': ')', '[': ']', '{': '}'
        }
        
        for open_char, close_char in balancing_chars.items():
            open_count = content.count(open_char)
            close_count = content.count(close_char)
            if open_count != close_count:
                issues.append({
                    "type": "unbalanced_delimiters",
                    "description": f"Unbalanced {open_char}{close_char}: {open_count} open, {close_count} close"
                })
        
        # Check for unfinished markdown elements
        if content.count('**') % 2 != 0:
            issues.append({
                "type": "unbalanced_bold_markers",
                "description": "Unbalanced bold (**) markers"
            })
        
        if content.count('*') % 2 != 0:
            issues.append({
                "type": "unbalanced_italic_markers",
                "description": "Unbalanced italic (*) markers"
            })
        
        return issues
    
    async def _store_complete_response(self, 
                                     task_id: str,
                                     summary: str,
                                     detailed_work: str,
                                     file_paths: List[str],
                                     artifact_type: str,
                                     next_action: str) -> Dict[str, Any]:
        """Store a complete response using streaming artifacts for robustness."""
        # Create streaming session
        session = await self.streaming_manager.create_streaming_session(
            task_id=task_id,
            summary=summary,
            file_paths=file_paths,
            artifact_type=artifact_type,
            expected_size_hint=len(detailed_work.encode('utf-8'))
        )
        
        # Write content in chunks (simulating streaming)
        chunk_size = 1024  # 1KB chunks
        async with session.write_stream():
            for i in range(0, len(detailed_work), chunk_size):
                chunk = detailed_work[i:i + chunk_size]
                is_final = (i + chunk_size) >= len(detailed_work)
                await session.write_chunk(chunk, is_final=is_final)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "artifact_created": True,
            "artifact_info": {
                "artifact_id": session.artifact_id,
                "summary": session.summary,
                "artifact_type": session.artifact_type,
                "final_size": session.bytes_written,
                "content_hash": session.content_hash.hexdigest(),
                "accessible_via": f".task_orchestrator/artifacts/{task_id}/{session.artifact_id}.md"
            },
            "context_saving": {
                "detailed_work_length": len(detailed_work),
                "stored_in_filesystem": True,
                "prevents_context_limit": True,
                "streaming_enabled": True
            }
        }
    
    async def _handle_partial_response(self,
                                     task_id: str,
                                     summary: str,
                                     detailed_work: str,
                                     file_paths: List[str],
                                     artifact_type: str,
                                     next_action: str,
                                     analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a partial response by creating a resumable streaming session."""
        # Create streaming session for partial content
        session = await self.streaming_manager.create_streaming_session(
            task_id=task_id,
            summary=f"PARTIAL: {summary}",
            file_paths=file_paths,
            artifact_type=artifact_type,
            expected_size_hint=None  # Unknown size for partial content
        )
        
        # Store partial content without finalizing
        async with session.write_stream():
            await session.write_chunk(detailed_work, is_final=False)
            
            # Add truncation notice
            truncation_notice = [
                "",
                "<!-- RESPONSE APPEARS TRUNCATED -->",
                "",
                "⚠️ **PARTIAL RESPONSE DETECTED**",
                "",
                "This response appears to be incomplete based on content analysis:",
                ""
            ]
            
            for issue in analysis["detected_issues"]:
                truncation_notice.append(f"- {issue['description']}")
            
            truncation_notice.extend([
                "",
                f"**Confidence Score:** {analysis['confidence_score']:.2f}/1.0",
                f"**Content Statistics:** {analysis['content_statistics']['character_count']} chars, {analysis['content_statistics']['word_count']} words",
                "",
                "**Next Steps:**",
                "1. This partial content has been saved to a temporary location",
                "2. Use the resumption tools to continue from where this left off",
                "3. The content can be completed and then moved to permanent storage",
                "",
                "**Resumption Information:**",
                f"- Task ID: `{task_id}`",
                f"- Artifact ID: `{session.artifact_id}`",
                f"- Partial file: `.task_orchestrator/temp/{task_id}/{session.artifact_id}/{session.artifact_id}_partial.md`",
                "",
                "<!-- END TRUNCATION NOTICE -->",
                ""
            ])
            
            await session.write_chunk("\n".join(truncation_notice), is_final=False)
        
        # Don't finalize - leave as partial for resumption
        progress_info = session.get_progress_info()
        
        return {
            "task_id": task_id,
            "status": "partial_response_detected",
            "artifact_created": False,
            "partial_artifact_created": True,
            "resumption_info": {
                "artifact_id": session.artifact_id,
                "partial_file_location": str(session.temp_file),
                "progress_file_location": str(session.progress_file),
                "bytes_written": session.bytes_written,
                "content_hash": session.content_hash.hexdigest()
            },
            "recovery_options": {
                "continue_response": "Continue writing from where the response was cut off",
                "confirm_complete": "Mark this partial response as complete and finalize",
                "restart_task": "Restart the task from the beginning"
            },
            "context_saving": {
                "partial_work_preserved": True,
                "resumption_available": True,
                "no_work_lost": True
            }
        }
    
    async def resume_partial_artifact(self, task_id: str, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Resume work on a partial artifact.
        
        Args:
            task_id: Task ID
            artifact_id: Artifact ID to resume
            
        Returns:
            Resumption information or None if not found
        """
        session = await self.streaming_manager.resume_partial_session(task_id, artifact_id)
        
        if not session:
            return None
        
        return {
            "resumed": True,
            "task_id": task_id,
            "artifact_id": artifact_id,
            "progress_info": session.get_progress_info(),
            "session_available": True,
            "instructions": [
                "The partial session has been resumed",
                "Continue providing content to complete the artifact",
                "Use the write_chunk method to add more content",
                "Call finalize when the content is complete"
            ]
        }
    
    async def list_partial_artifacts(self) -> List[Dict[str, Any]]:
        """List all partial artifacts that can be resumed."""
        return await self.streaming_manager.list_partial_sessions()
    
    async def continue_partial_artifact(self, 
                                      task_id: str, 
                                      artifact_id: str, 
                                      additional_content: str,
                                      is_final: bool = False) -> Dict[str, Any]:
        """Continue writing to a partial artifact.
        
        Args:
            task_id: Task ID
            artifact_id: Artifact ID
            additional_content: Content to add
            is_final: Whether this completes the artifact
            
        Returns:
            Continuation result
        """
        session = await self.streaming_manager.resume_partial_session(task_id, artifact_id)
        
        if not session:
            return {
                "error": f"No partial session found for {task_id}/{artifact_id}",
                "success": False
            }
        
        try:
            async with session.write_stream():
                await session.write_chunk(additional_content, is_final=is_final)
            
            if is_final:
                return {
                    "success": True,
                    "status": "completed",
                    "artifact_finalized": True,
                    "final_info": {
                        "artifact_id": session.artifact_id,
                        "final_size": session.bytes_written,
                        "content_hash": session.content_hash.hexdigest()
                    }
                }
            else:
                return {
                    "success": True,
                    "status": "continued",
                    "progress_info": session.get_progress_info(),
                    "ready_for_more": True
                }
        
        except Exception as e:
            logger.error(f"Error continuing partial artifact {task_id}/{artifact_id}: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def cleanup_old_partials(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up old partial artifacts.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Cleanup results
        """
        cleaned_count = await self.streaming_manager.cleanup_old_temp_files(max_age_hours)
        
        return {
            "cleaned_count": cleaned_count,
            "max_age_hours": max_age_hours,
            "cleanup_completed": True
        }


# Integration helper functions
def create_enhanced_artifact_tools() -> List[types.Tool]:
    """Create enhanced MCP tools with partial response support."""
    return [
        types.Tool(
            name="orchestrator_complete_subtask_enhanced",
            description="Enhanced subtask completion with streaming artifacts and partial response detection",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the completed subtask"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of what was accomplished"
                    },
                    "detailed_work": {
                        "type": "string",
                        "description": "Full detailed work content to store as artifacts"
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of original file paths being referenced or created (optional)"
                    },
                    "artifact_type": {
                        "type": "string",
                        "enum": ["code", "documentation", "analysis", "design", "test", "config", "general"],
                        "description": "Type of artifact being created",
                        "default": "general"
                    },
                    "next_action": {
                        "type": "string",
                        "enum": ["continue", "needs_revision", "blocked", "complete"],
                        "description": "What should happen next"
                    }
                },
                "required": ["task_id", "summary", "detailed_work", "next_action"]
            }
        ),
        types.Tool(
            name="orchestrator_resume_partial_artifact",
            description="Resume work on a partial artifact that was interrupted",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID to resume"
                    }
                },
                "required": ["task_id", "artifact_id"]
            }
        ),
        types.Tool(
            name="orchestrator_continue_partial_artifact",
            description="Continue writing to a partial artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    },
                    "additional_content": {
                        "type": "string",
                        "description": "Content to add to the artifact"
                    },
                    "is_final": {
                        "type": "boolean",
                        "description": "Whether this completes the artifact",
                        "default": False
                    }
                },
                "required": ["task_id", "artifact_id", "additional_content"]
            }
        ),
        types.Tool(
            name="orchestrator_list_partial_artifacts",
            description="List all partial artifacts that can be resumed",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="orchestrator_cleanup_partial_artifacts",
            description="Clean up old partial artifacts",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_age_hours": {
                        "type": "number",
                        "description": "Maximum age of partial artifacts in hours",
                        "default": 24
                    }
                }
            }
        )
    ]


# Usage example
async def example_streaming_usage():
    """Example of how to use the streaming artifact system."""
    
    # Initialize enhanced server
    enhanced_server = EnhancedArtifactServer("/path/to/project")
    
    # Simulate a partial response scenario
    partial_response_args = {
        "task_id": "implementer_123",
        "summary": "User authentication system implementation",
        "detailed_work": "# User Authentication System\n\nThis implementation provides...",  # Truncated
        "file_paths": ["auth/models.py", "auth/views.py"],
        "artifact_type": "code",
        "next_action": "continue"
    }
    
    # Handle the partial response
    result = await enhanced_server.enhanced_complete_subtask(partial_response_args)
    
    if result["status"] == "partial_response_detected":
        print(f"Partial response detected for task {result['task_id']}")
        print(f"Artifact ID: {result['resumption_info']['artifact_id']}")
        
        # Later, resume the partial artifact
        task_id = result["task_id"]
        artifact_id = result["resumption_info"]["artifact_id"]
        
        # Continue with more content
        continuation_result = await enhanced_server.continue_partial_artifact(
            task_id=task_id,
            artifact_id=artifact_id,
            additional_content="\n\n## Additional Implementation Details\n\nHere's the rest of the implementation...",
            is_final=True
        )
        
        if continuation_result["success"]:
            print(f"Artifact completed successfully: {continuation_result['final_info']}")
        
    # List all partial artifacts
    partial_list = await enhanced_server.list_partial_artifacts()
    print(f"Found {len(partial_list)} partial artifacts")
    
    # Clean up old partials
    cleanup_result = await enhanced_server.cleanup_old_partials(max_age_hours=48)
    print(f"Cleaned up {cleanup_result['cleaned_count']} old partial artifacts")


if __name__ == "__main__":
    asyncio.run(example_streaming_usage())
