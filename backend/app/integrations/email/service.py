"""
ModularMenu — Email Integration Contracts & Services (ARC-07 §11.1, §11.3).
"""
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class EmailMessage:
    recipient: str
    subject: str
    html_body: str
    text_body: str
    reply_to: Optional[str] = None


class EmailProvider(Protocol):
    async def send(self, message: EmailMessage) -> str:
        """Sends an email message and returns provider dispatch identifier."""
        ...


class ConsoleEmailProvider:
    """Development and test provider logging emails to memory."""
    def __init__(self):
        self.sent_messages: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> str:
        self.sent_messages.append(message)
        return f"mock-msg-{len(self.sent_messages)}"


class EmailService:
    def __init__(self, provider: Optional[EmailProvider] = None):
        self.provider = provider or ConsoleEmailProvider()

    async def send_verification(self, recipient: str, token: str) -> str:
        msg = EmailMessage(
            recipient=recipient,
            subject="Verify your ModularMenu account",
            html_body=f"<p>Your verification token is <b>{token}</b></p>",
            text_body=f"Your verification token is {token}",
        )
        return await self.provider.send(msg)

    async def send_password_reset(self, recipient: str, token: str) -> str:
        msg = EmailMessage(
            recipient=recipient,
            subject="Reset your ModularMenu password",
            html_body=f"<p>Reset link: https://app.modularmenu.com/reset?token={token}</p>",
            text_body=f"Reset token: {token}",
        )
        return await self.provider.send(msg)
