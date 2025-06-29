"""
External service integrations infrastructure.

This package contains implementations for external services
like notifications, webhooks, and API integrations.
"""

from .notification_service import EmailNotificationService, WebhookNotificationService
from .api_client import HTTPApiClient
from .artifact_storage import FileSystemArtifactStorage

__all__ = [
    'EmailNotificationService',
    'WebhookNotificationService',
    'HTTPApiClient',
    'FileSystemArtifactStorage'
]