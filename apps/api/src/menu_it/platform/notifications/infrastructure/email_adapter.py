"""Email provider protocol and channel adapter (FCD-09 WP-03)."""

from dataclasses import dataclass
import logging
from typing import Protocol, runtime_checkable
from uuid import uuid4

from menu_it.platform.notifications.application.renderer import TemplateRenderer
from menu_it.platform.notifications.domain.contracts import (
    NotificationChannelAdapter,
    NotificationMessage,
    NotificationResult,
    NotificationStatus,
)

logger = logging.getLogger("menu_it.platform.notifications.email")


@runtime_checkable
class EmailProvider(Protocol):
    """Protocol for sending raw emails through an underlying transport."""

    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str,
        idempotency_key: str,
    ) -> str | None:
        """Deliver email and return provider message reference ID."""
        ...


@dataclass(frozen=True)
class SentEmailRecord:
    recipient: str
    subject: str
    html_body: str
    text_body: str
    idempotency_key: str
    reference_id: str


class InMemoryEmailProvider:
    """Test double recording sent emails in memory."""

    def __init__(self) -> None:
        self.sent: list[SentEmailRecord] = []
        self.should_fail: bool = False
        self.fail_error: str = "Simulated email provider failure"

    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str,
        idempotency_key: str,
    ) -> str | None:
        if self.should_fail:
            raise RuntimeError(self.fail_error)
        ref = f"mem-{uuid4().hex[:12]}"
        self.sent.append(
            SentEmailRecord(
                recipient=recipient,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                idempotency_key=idempotency_key,
                reference_id=ref,
            )
        )
        return ref


class ConsoleEmailProvider:
    """Development provider logging emails to console."""

    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str,
        idempotency_key: str,
    ) -> str | None:
        ref = f"console-{uuid4().hex[:12]}"
        logger.info(
            "EMAIL_DISPATCH [idempotency=%s, ref=%s] -> To: %s | Subject: %s\nText:\n%s",
            idempotency_key,
            ref,
            recipient,
            subject,
            text_body,
        )
        return ref


class EmailNotificationAdapter:
    """Renders approved email templates and dispatches via configured EmailProvider."""

    def __init__(self, provider: EmailProvider, renderer: TemplateRenderer | None = None) -> None:
        self.provider = provider
        self.renderer = renderer or TemplateRenderer()

    async def send(self, message: NotificationMessage) -> NotificationResult:
        try:
            subject, html_body, text_body = self.renderer.render_email(
                template_id=message.template_id,
                variables=message.variables,
                locale=message.locale,
            )
            ref = await self.provider.send_email(
                recipient=message.recipient,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                idempotency_key=message.idempotency_key,
            )
            return NotificationResult(
                provider_reference=ref,
                accepted=True,
                status=NotificationStatus.SENT,
            )
        except Exception as exc:
            logger.error("Failed to send email notification %s: %s", message.notification_id, exc)
            return NotificationResult(
                provider_reference=None,
                accepted=False,
                status=NotificationStatus.FAILED,
                error=str(exc),
            )
