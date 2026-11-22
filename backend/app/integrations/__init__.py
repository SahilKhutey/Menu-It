"""
ModularMenu — External Integrations Package (ARC-07 §11.1).
"""

from app.integrations.billing.service import BillingService
from app.integrations.email.service import EmailMessage, EmailService
from app.integrations.monitoring.service import MonitoringService
from app.integrations.storage.service import StorageService, UploadIntentResult
from app.integrations.webhooks.delivery import WebhookDeliveryService, WebhookEvent
from app.integrations.webhooks.signing import sign_payload, verify_signature

__all__ = [
    "EmailService",
    "EmailMessage",
    "StorageService",
    "UploadIntentResult",
    "WebhookDeliveryService",
    "WebhookEvent",
    "sign_payload",
    "verify_signature",
    "BillingService",
    "MonitoringService",
]
