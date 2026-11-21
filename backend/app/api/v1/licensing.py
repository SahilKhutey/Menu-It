"""
ModularMenu — Licensing & Subscription API Endpoints (ARC-07 §4.10).
"""
import datetime
from decimal import Decimal
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.api.schemas.licensing import (
    LicenseResponse,
    SubscriptionPlanResponse,
    SubscriptionResponse,
)
from app.core.database import get_db
from app.shared.application.tenant_context import TenantContext

router = APIRouter(tags=["Licensing & Subscriptions"])


@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def list_subscription_plans(db: AsyncSession = Depends(get_db)):
    """Lists publicly available subscription plans."""
    return [
        SubscriptionPlanResponse(
            id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
            code="starter",
            name="Starter Plan",
            price=Decimal("1999.00"),
            currency="INR",
            billing_interval="monthly",
            max_restaurants=1,
            features=["1 Restaurant", "Standard Themes", "QR Code Generation", "Unlimited Scans"],
        ),
        SubscriptionPlanResponse(
            id=uuid.UUID("11111111-0000-0000-0000-000000000002"),
            code="pro",
            name="Professional Hospitality",
            price=Decimal("4999.00"),
            currency="INR",
            billing_interval="monthly",
            max_restaurants=5,
            features=["5 Branches", "Custom Themes", "Analytics", "Priority Support"],
        ),
        SubscriptionPlanResponse(
            id=uuid.UUID("11111111-0000-0000-0000-000000000003"),
            code="enterprise",
            name="Enterprise Multi-Branch",
            price=Decimal("12999.00"),
            currency="INR",
            billing_interval="monthly",
            max_restaurants=25,
            features=["Unlimited Branches", "Dedicated Account Manager", "Custom Domain", "SLA"],
        ),
    ]


@router.get("/organizations/{organization_id}/subscription", response_model=SubscriptionResponse)
async def get_organization_subscription(
    organization_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("subscription.read")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves active subscription entitlement for an organization."""
    if tenant.organization_id != organization_id and not tenant.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    now = datetime.datetime.now(datetime.timezone.utc)
    return SubscriptionResponse(
        id=uuid.uuid4(),
        organization_id=organization_id,
        plan_code="starter",
        status="active",
        current_period_end=now + datetime.timedelta(days=30),
    )


@router.get("/organizations/{organization_id}/license", response_model=LicenseResponse)
async def get_organization_license(
    organization_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("license.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves deployment license entitlement for self-hosted customer appliances."""
    if tenant.organization_id != organization_id and not tenant.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    now = datetime.datetime.now(datetime.timezone.utc)
    return LicenseResponse(
        id=uuid.uuid4(),
        organization_id=organization_id,
        license_type="commercial_saas",
        status="valid",
        max_branches=5,
        expires_at=now + datetime.timedelta(days=365),
    )
