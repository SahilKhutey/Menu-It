from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, require_platform_admin
from app.modules.identity.models import Organization, Restaurant, User

router = APIRouter(prefix="/platform", tags=["Platform Administration"])


@router.get("/overview")
async def get_platform_overview(
    admin_user: User = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Returns platform-wide metrics. Requires platform admin privileges."""
    orgs_count = (await db.execute(select(func.count(Organization.id)))).scalar_one()
    rests_count = (await db.execute(select(func.count(Restaurant.id)))).scalar_one()
    users_count = (await db.execute(select(func.count(User.id)))).scalar_one()

    return {
        "status": "operational",
        "total_organizations": orgs_count,
        "total_restaurants": rests_count,
        "total_users": users_count,
    }
