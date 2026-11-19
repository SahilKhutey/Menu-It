import io
from fastapi import APIRouter, Depends, HTTPException, Response, status
import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from app.core.config import settings
from app.modules.identity.models import Restaurant
from app.modules.menus.models import Menu, MenuVersion, Publication

router = APIRouter(prefix="/public", tags=["Public Customer Menu"])


@router.get("/restaurants/{slug}/menu")
async def get_public_menu(slug: str, db: AsyncSession = Depends(get_db)):
    # 1. Resolve Restaurant by slug
    rest_stmt = select(Restaurant).where(Restaurant.slug == slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # 2. Find active published menu
    pub_stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(Publication.restaurant_id == restaurant.id, Publication.status == "published")
        .order_by(Publication.published_at.desc())
    )
    result = await db.execute(pub_stmt)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="No published menu found for this restaurant")

    publication, menu_version = row
    return {
        "status": "success",
        "version_number": menu_version.version_number,
        "checksum": menu_version.checksum,
        "published_at": menu_version.published_at.isoformat(),
        "data": menu_version.snapshot_data
    }


@router.get("/restaurants/{slug}/qr")
async def get_restaurant_qr_code(slug: str, db: AsyncSession = Depends(get_db)):
    # 1. Verify restaurant exists
    rest_stmt = select(Restaurant).where(Restaurant.slug == slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    public_menu_url = f"{settings.PUBLIC_BASE_URL}/r/{slug}"
    
    # 2. Generate QR code in memory
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(public_menu_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")
