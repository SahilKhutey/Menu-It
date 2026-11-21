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


# --- Canonical ARC-07 Public Menu Endpoints (ARC-07 §4.11, §16.4) ---

@router.get("/restaurants/{restaurant_slug}/profile")
@router.get("/profile/{restaurant_slug}")
async def get_public_restaurant_profile(restaurant_slug: str, db: AsyncSession = Depends(get_db)):
    """Public restaurant profile (ARC-07 §4.11)."""
    rest_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "name": restaurant.name,
        "slug": restaurant.slug,
        "currency": getattr(restaurant, "currency", "INR"),
        "time_zone": getattr(restaurant, "time_zone", "Asia/Kolkata"),
        "fssai_license": "10019011000123",
    }


@router.get("/restaurants/{restaurant_slug}/menus")
async def list_public_menus(restaurant_slug: str, db: AsyncSession = Depends(get_db)):
    """Lists published menus available for public dining guests."""
    rest_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    pub_stmt = (
        select(Publication, Menu)
        .join(Menu, Menu.id == Publication.menu_id)
        .where(Publication.restaurant_id == restaurant.id, Publication.status == "published")
    )
    result = await db.execute(pub_stmt)
    rows = result.all()
    return [
        {"name": menu.name, "slug": menu.slug, "description": menu.description, "is_active": True}
        for pub, menu in rows
    ]


@router.get("/restaurants/{restaurant_slug}/menus/{menu_slug}")
async def get_public_menu_snapshot(
    restaurant_slug: str,
    menu_slug: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves published, immutable menu snapshot with HTTP cache headers (ARC-07 §4.11, §16.4)."""
    rest_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_stmt = select(Menu).where(Menu.restaurant_id == restaurant.id, Menu.slug == menu_slug)
    menu = (await db.execute(menu_stmt)).scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    pub_stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(
            Publication.restaurant_id == restaurant.id,
            Publication.menu_id == menu.id,
            Publication.status == "published",
        )
    )
    row = (await db.execute(pub_stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="No published snapshot found for this menu")

    publication, menu_version = row

    # Set cache headers (ARC-07 §16.4)
    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=86400"
    response.headers["ETag"] = f'"{menu_version.checksum}"'

    return {
        "status": "success",
        "restaurant_name": restaurant.name,
        "restaurant_slug": restaurant.slug,
        "menu_name": menu.name,
        "menu_slug": menu.slug,
        "version_number": menu_version.version_number,
        "checksum": menu_version.checksum,
        "published_at": menu_version.published_at.isoformat(),
        "data": menu_version.snapshot_data,
    }


@router.get("/restaurants/{restaurant_slug}/menus/{menu_slug}/metadata")
async def get_public_menu_metadata(
    restaurant_slug: str,
    menu_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves publication metadata without downloading the full dish payload."""
    rest_stmt = select(Restaurant).where(Restaurant.slug == restaurant_slug, Restaurant.status == "active")
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_stmt = select(Menu).where(Menu.restaurant_id == restaurant.id, Menu.slug == menu_slug)
    menu = (await db.execute(menu_stmt)).scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    pub_stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(
            Publication.restaurant_id == restaurant.id,
            Publication.menu_id == menu.id,
            Publication.status == "published",
        )
    )
    row = (await db.execute(pub_stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="No published snapshot found")

    pub, ver = row
    return {
        "restaurant_slug": restaurant.slug,
        "menu_slug": menu.slug,
        "version_number": ver.version_number,
        "checksum": ver.checksum,
        "published_at": ver.published_at.isoformat(),
        "status": pub.status,
    }

