"""
Notification service implementations.
"""

from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime

from ...application.interfaces import NotificationService

logger = logging.getLogger(__name__)


class WebhookNotificationService(NotificationService):
    """
    Notification service that sends notifications via webhooks.
    """
    
    def __init__(self, webhook_url: str, timeout: int = 30):
        self.webhook_url = webhook_url
        self.timeout = timeout
    
    async def notify_task_started(self, task_id: str, metadata: Dict[str, Any]) -> None:
        """Send notification when a task starts."""
        payload = {
            "event": "task_started",
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        await self._send_webhook(payload)
    
    async def notify_task_completed(
        self,
        task_id: str,
        result: str,
        artifacts: list[str],
        metadata: Dict[str, Any]
    ) -> None:
        """Send notification when a task completes."""
        payload = {
            "event": "task_completed",
            "task_id": task_id,
            "result": result,
            "artifacts": artifacts,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        await self._send_webhook(payload)
    
    async def notify_task_failed(
        self,
        task_id: str,
        error: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Send notification when a task fails."""
        payload = {
            "event": "task_failed",
            "task_id": task_id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        await self._send_webhook(payload)
    
    async def notify_session_completed(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """Send notification when an orchestration session completes."""
        payload = {
            "event": "session_completed",
            "session_id": session_id,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_webhook(payload)
    
    async def _send_webhook(self, payload: Dict[str, Any]) -> None:
        """Send webhook HTTP request."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status >= 400:
                        logger.warning(f"Webhook notification failed with status {response.status}")
                    else:
                        logger.debug(f"Webhook notification sent successfully: {payload['event']}")
        
        except ImportError:
            logger.error("aiohttp not available, cannot send webhook notifications")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")


class EmailNotificationService(NotificationService):
    """
    Notification service that sends email notifications.
    """
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: list[str]
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
    
    async def notify_task_started(self, task_id: str, metadata: Dict[str, Any]) -> None:
        """Send email notification when a task starts."""
        subject = f"Task Started: {task_id}"
        body = f"""
Task {task_id} has started.

Metadata:
{json.dumps(metadata, indent=2)}

Timestamp: {datetime.utcnow().isoformat()}
        """
        
        await self._send_email(subject, body)
    
    async def notify_task_completed(
        self,
        task_id: str,
        result: str,
        artifacts: list[str],
        metadata: Dict[str, Any]
    ) -> None:
        """Send email notification when a task completes."""
        subject = f"Task Completed: {task_id}"
        body = f"""
Task {task_id} has completed successfully.

Result:
{result}

Artifacts: {', '.join(artifacts) if artifacts else 'None'}

Metadata:
{json.dumps(metadata, indent=2)}

Timestamp: {datetime.utcnow().isoformat()}
        """
        
        await self._send_email(subject, body)
    
    async def notify_task_failed(
        self,
        task_id: str,
        error: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Send email notification when a task fails."""
        subject = f"Task Failed: {task_id}"
        body = f"""
Task {task_id} has failed.

Error:
{error}

Metadata:
{json.dumps(metadata, indent=2)}

Timestamp: {datetime.utcnow().isoformat()}
        """
        
        await self._send_email(subject, body)
    
    async def notify_session_completed(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """Send email notification when an orchestration session completes."""
        subject = f"Orchestration Session Completed: {session_id}"
        body = f"""
Orchestration session {session_id} has completed.

Summary:
{json.dumps(summary, indent=2)}

Timestamp: {datetime.utcnow().isoformat()}
        """
        
        await self._send_email(subject, body)
    
    async def _send_email(self, subject: str, body: str) -> None:
        """Send email using SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import asyncio
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Run SMTP in thread to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._send_smtp,
                msg
            )
            
            logger.debug(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_smtp(self, msg) -> None:
        """Send email via SMTP (blocking operation)."""
        import smtplib
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class LoggingNotificationService(NotificationService):
    """
    Simple notification service that logs notifications instead of sending them.
    Useful for development and testing.
    """
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger(f"{__name__}.notifications")
        self.log_level = getattr(logging, log_level.upper())
    
    async def notify_task_started(self, task_id: str, metadata: Dict[str, Any]) -> None:
        """Log task started notification."""
        self.logger.log(self.log_level, f"NOTIFICATION: Task {task_id} started - {metadata}")
    
    async def notify_task_completed(
        self,
        task_id: str,
        result: str,
        artifacts: list[str],
        metadata: Dict[str, Any]
    ) -> None:
        """Log task completed notification."""
        self.logger.log(
            self.log_level,
            f"NOTIFICATION: Task {task_id} completed - Result: {result[:100]}... - Artifacts: {artifacts}"
        )
    
    async def notify_task_failed(
        self,
        task_id: str,
        error: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Log task failed notification."""
        self.logger.log(self.log_level, f"NOTIFICATION: Task {task_id} failed - Error: {error}")
    
    async def notify_session_completed(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> None:
        """Log session completed notification."""
        self.logger.log(
            self.log_level,
            f"NOTIFICATION: Session {session_id} completed - Summary: {summary}"
        )