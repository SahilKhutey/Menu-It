"""
ModularMenu — Licensing & Subscription Schemas (ARC-07 §4.10).
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    price: Decimal
    currency: str
    billing_interval: str
    max_restaurants: int
    features: List[str]


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    plan_code: str
    status: str
    current_period_end: datetime


class LicenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    license_type: str
    status: str
    max_branches: int
    expires_at: Optional[datetime] = None
