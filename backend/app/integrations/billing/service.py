"""
ModularMenu — Billing Provider Contract & Adapter (ARC-07 §11.1).
"""

from typing import Protocol
from uuid import UUID


class BillingProvider(Protocol):
    async def create_checkout_session(
        self, organization_id: UUID, plan_code: str, return_url: str
    ) -> str: ...


class DeferredBillingProvider:
    """Mock/deferred billing provider for early stage (ARC-07 §11.2)."""

    async def create_checkout_session(
        self, organization_id: UUID, plan_code: str, return_url: str
    ) -> str:
        return (
            f"https://checkout.modularmenu.com/mock-session?org={organization_id}&plan={plan_code}"
        )


class BillingService:
    def __init__(self, provider: BillingProvider | None = None):
        self.provider = provider or DeferredBillingProvider()

    async def initiate_checkout(
        self, organization_id: UUID, plan_code: str, return_url: str
    ) -> str:
        return await self.provider.create_checkout_session(organization_id, plan_code, return_url)
