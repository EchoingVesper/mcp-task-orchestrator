"""
Application layer interfaces.

These interfaces define contracts for external services
that the application layer depends on.
"""

from .notification_service import NotificationService
from .external_api_client import ExternalApiClient

__all__ = [
    'NotificationService',
    'ExternalApiClient'
]