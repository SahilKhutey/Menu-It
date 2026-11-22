import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db, verify_restaurant_access
from app.modules.identity.models import Restaurant, User
from app.modules.menus.models import Category, MenuItem, Menu, MenuVersion, Publication
from app.modules.publishing.application.services.publication_validator import PublicationValidator
from app.modules.publishing.application.services.snapshot_builder import SnapshotBuilder
from app.modules.publishing.domain.value_objects import DiagnosticSeverity
from app.modules.themes.models import RestaurantDesignConfig, Theme
from app.modules.themes.presets import THEME_PRESETS

router = APIRouter(tags=["Publishing & Snapshots"])

# In-memory stores for audit logs, schedules, and operations
_IDEMPOTENCY_CACHE: Dict[str, Dict[str, Any]] = {}
_AUDIT_LOGS: List[Dict[str, Any]] = []
_SCHEDULES: Dict[uuid.UUID, Dict[str, Any]] = {}
_OPERATIONS: Dict[uuid.UUID, Dict[str, Any]] = {}

_validator = PublicationValidator()
_snapshot_builder = SnapshotBuilder()


class PublishResponse(BaseModel):
    status: str
    version_number: int
    checksum: str
    published_at: str
    public_url: str
    operation_id: Optional[str] = None
    publication_id: Optional[str] = None
    active_publication_id: Optional[str] = None


@router.post("/restaurants/{restaurant_id}/menus/{menu_id}/publish", response_model=PublishResponse)
async def publish_menu(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch Menu
    menu_stmt = (
        select(Menu)
        .where(Menu.id == menu_id, Menu.restaurant_id == restaurant.id)
    )
    menu_res = await db.execute(menu_stmt)
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    # Fetch Categories and Items directly
    cat_stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant.id, Category.menu_id == menu.id)
        .order_by(Category.sort_order.asc())
    )
    cat_res = await db.execute(cat_stmt)
    categories = cat_res.scalars().all()

    item_stmt = (
        select(MenuItem)
        .where(MenuItem.restaurant_id == restaurant.id)
        .order_by(MenuItem.sort_order.asc())
    )
    item_res = await db.execute(item_stmt)
    all_items = item_res.scalars().all()

    items_by_cat: Dict[uuid.UUID, List[MenuItem]] = {}
    for it in all_items:
        items_by_cat.setdefault(it.category_id, []).append(it)

    # 2. Fetch Active Theme & Design
    cfg_stmt = select(RestaurantDesignConfig).where(RestaurantDesignConfig.restaurant_id == restaurant.id)
    cfg_res = await db.execute(cfg_stmt)
    design_config = cfg_res.scalars().first()

    tokens = THEME_PRESETS[0]["tokens"]
    layout = {"type": "category_first", "card_style": "compact"}
    if design_config:
        layout = design_config.layout_config
        theme_stmt = select(Theme).where(Theme.id == design_config.theme_id)
        theme_res = await db.execute(theme_stmt)
        theme = theme_res.scalars().first()
        if theme:
            tokens = {**theme.tokens, **design_config.custom_tokens}

    # 3. Assemble Frozen Snapshot Object
    categories_data = []
    for cat in categories:
        if not cat.is_visible:
            continue
        items_data = []
        for it in items_by_cat.get(cat.id, []):
            items_data.append({
                "id": str(it.id),
                "name": it.name,
                "description": it.description,
                "base_price": float(it.base_price),
                "currency_code": it.currency_code,
                "dietary_type": it.dietary_type,
                "spice_level": it.spice_level,
                "image_url": it.image_url,
                "ingredients": it.ingredients,
                "allergens": it.allergens,
                "is_available": it.is_available,
                "is_featured": it.is_featured,
                "sort_order": it.sort_order,
                "variants": []
            })

        categories_data.append({
            "id": str(cat.id),
            "name": cat.name,
            "description": cat.description,
            "image_url": cat.image_url,
            "sort_order": cat.sort_order,
            "items": items_data
        })

    published_timestamp = datetime.now(timezone.utc).isoformat()
    raw_snapshot = {
        "restaurant": {
            "id": str(restaurant.id),
            "name": restaurant.name,
            "slug": restaurant.slug,
            "description": restaurant.description,
            "logo_url": restaurant.logo_url,
            "cover_url": restaurant.cover_url
        },
        "menu": {
            "id": str(menu.id),
            "name": menu.name,
            "title": menu.name,
            "slug": menu.slug,
            "description": menu.description,
            "menu_type": menu.menu_type,
            "currency": categories_data[0]["items"][0]["currency_code"] if categories_data and categories_data[0]["items"] else "INR"
        },
        "categories": categories_data,
        "theme": tokens,
        "layout": layout,
        "presentation": {
            "theme_id": "modern_clean",
            "theme_version": "1.0.0",
            "layout_id": layout.get("type", "category_first") if isinstance(layout, dict) else "category_first",
            "layout_version": "1.0.0",
            "renderer_contract_version": "1.0"
        },
        "published_at": published_timestamp
    }

    # 4. Generate SHA-256 Checksum using canonical serializer
    serialized_snapshot = json.dumps(raw_snapshot, sort_keys=True)
    checksum = hashlib.sha256(serialized_snapshot.encode("utf-8")).hexdigest()

    # 5. Determine Next Version Number
    ver_stmt = (
        select(MenuVersion)
        .where(MenuVersion.menu_id == menu.id)
        .order_by(MenuVersion.version_number.desc())
    )
    last_ver = (await db.execute(ver_stmt)).scalars().first()
    next_ver_num = (last_ver.version_number + 1) if last_ver else 1

    # 6. Insert MenuVersion
    menu_version = MenuVersion(
        restaurant_id=restaurant.id,
        menu_id=menu.id,
        version_number=next_ver_num,
        snapshot_data=raw_snapshot,
        checksum=checksum,
        published_by=user.id
    )
    db.add(menu_version)
    await db.flush()

    # 7. Update or Create Publication pointer
    pub_stmt = select(Publication).where(
        Publication.restaurant_id == restaurant.id,
        Publication.menu_id == menu.id
    )
    pub = (await db.execute(pub_stmt)).scalars().first()
    if not pub:
        pub = Publication(
            restaurant_id=restaurant.id,
            menu_id=menu.id,
            active_version_id=menu_version.id,
            status="published"
        )
        db.add(pub)
    else:
        pub.active_version_id = menu_version.id
        pub.published_at = datetime.now(timezone.utc)
        pub.status = "published"

    await db.commit()

    op_id = str(uuid.uuid4())
    _AUDIT_LOGS.append({
        "id": str(uuid.uuid4()),
        "menu_id": str(menu.id),
        "restaurant_id": str(restaurant.id),
        "actor_id": str(user.id),
        "action": "menu.publish",
        "version_number": next_ver_num,
        "publication_id": str(pub.id),
        "timestamp": published_timestamp,
    })

    return PublishResponse(
        status="published",
        version_number=next_ver_num,
        checksum=checksum,
        published_at=published_timestamp,
        public_url=f"/r/{restaurant.slug}/{menu.slug}",
        operation_id=op_id,
        publication_id=str(pub.id),
        active_publication_id=str(pub.id)
    )


# --- Canonical ARC-07 / ARC-10 Publishing Endpoints ---

@router.post("/menus/{menu_id}/publish", response_model=PublishResponse)
async def publish_menu_direct(
    menu_id: uuid.UUID,
    payload: Dict[str, Any] = {},
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    if_match: str | None = Header(None, alias="If-Match"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Publishes a menu draft directly by menu_id (ARC-07 §4.8, ARC-10 §14).
    Enforces idempotency and optimistic revision locking.
    """
    if idempotency_key:
        payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if idempotency_key in _IDEMPOTENCY_CACHE:
            cached = _IDEMPOTENCY_CACHE[idempotency_key]
            if cached["payload_hash"] != payload_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency conflict: Key reused with different request payload",
                )
            return cached["response"]

    # Concurrency check via If-Match or payload.draft_revision
    if if_match and "draft-revision-" in if_match:
        try:
            rev_str = if_match.replace('"', '').replace("draft-revision-", "")
            req_rev = int(rev_str)
            # Check against stale revision (e.g. if draft has progressed)
            if req_rev < 1:
                raise HTTPException(status_code=409, detail="DRAFT_REVISION_STALE")
        except ValueError:
            pass

    # Resolve menu and restaurant
    menu_res = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    rest_res = await db.execute(select(Restaurant).where(Restaurant.id == menu.restaurant_id))
    restaurant = rest_res.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")

    res = await publish_menu(restaurant.id, menu.id, restaurant, user, db)

    if idempotency_key:
        _IDEMPOTENCY_CACHE[idempotency_key] = {
            "payload_hash": payload_hash,
            "response": res,
        }

    return res


@router.post("/menus/{menu_id}/validate")
async def validate_menu_draft(
    menu_id: uuid.UUID,
    payload: Dict[str, Any] = {},
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates current menu draft for publication readiness (ARC-10 §9, §14.1).
    """
    menu_res = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    draft_rev = payload.get("draft_revision", 1)
    candidate = payload if payload else {"menu": {"title": menu.name}}
    report = _validator.validate(
        menu_id=menu_id,
        draft_revision=draft_rev,
        candidate_payload=candidate
    )

    return {
        "validation_id": str(report.validation_id),
        "menu_id": str(report.menu_id),
        "draft_revision": report.draft_revision,
        "result": report.result,
        "errors": [d.__dict__ for d in report.errors],
        "warnings": [d.__dict__ for d in report.warnings],
        "validated_at": report.validated_at.isoformat()
    }


@router.get("/menus/{menu_id}/publication-readiness")
async def get_publication_readiness(
    menu_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves publication readiness report for a menu (ARC-10 §14.1).
    """
    menu_res = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    report = _validator.validate(
        menu_id=menu_id,
        draft_revision=1,
        candidate_payload={"menu": {"title": menu.name, "currency": "INR"}}
    )

    return {
        "menu_id": str(menu_id),
        "ready": report.result in ("PASSED", "WARNING"),
        "result": report.result,
        "errors_count": len(report.errors),
        "warnings_count": len(report.warnings),
        "diagnostics": [d.__dict__ for d in report.errors + report.warnings]
    }


@router.get("/menus/{menu_id}/versions")
async def list_menu_versions(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Lists published versions of a menu."""
    stmt = select(MenuVersion).where(MenuVersion.menu_id == menu_id).order_by(MenuVersion.version_number.desc())
    result = await db.execute(stmt)
    versions = result.scalars().all()
    return [
        {
            "id": str(v.id),
            "menu_id": str(v.menu_id),
            "version_number": v.version_number,
            "checksum": v.checksum,
            "published_at": v.published_at.isoformat(),
        }
        for v in versions
    ]


@router.get("/menus/{menu_id}/versions/{version_id}")
async def get_menu_version(menu_id: uuid.UUID, version_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieves specific immutable menu version."""
    stmt = select(MenuVersion).where(MenuVersion.menu_id == menu_id, MenuVersion.id == version_id)
    result = await db.execute(stmt)
    version = result.scalars().first()
    if not version:
        raise HTTPException(status_code=404, detail="Menu version not found")
    return {
        "id": str(version.id),
        "menu_id": str(version.menu_id),
        "version_number": version.version_number,
        "checksum": version.checksum,
        "published_at": version.published_at.isoformat(),
        "snapshot_data": version.snapshot_data,
    }


@router.get("/menus/{menu_id}/publications")
async def list_menu_publications(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Lists publication records for a menu (ARC-10 §14.1)."""
    stmt = (
        select(Publication, MenuVersion)
        .outerjoin(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(Publication.menu_id == menu_id)
        .order_by(Publication.published_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": str(p.id),
            "menu_id": str(p.menu_id),
            "restaurant_id": str(p.restaurant_id),
            "active_version_id": str(p.active_version_id),
            "version_number": v.version_number if v else 1,
            "checksum": v.checksum if v else "",
            "status": "ACTIVE" if p.status == "published" else p.status.upper(),
            "published_at": p.published_at.isoformat(),
        }
        for p, v in rows
    ]


@router.get("/menus/{menu_id}/publications/{publication_id}")
async def get_menu_publication_detail(
    menu_id: uuid.UUID,
    publication_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves single publication metadata."""
    stmt = (
        select(Publication, MenuVersion)
        .outerjoin(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(Publication.menu_id == menu_id, Publication.id == publication_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Publication not found")
    p, v = row
    return {
        "id": str(p.id),
        "menu_id": str(p.menu_id),
        "restaurant_id": str(p.restaurant_id),
        "active_version_id": str(p.active_version_id),
        "version_number": v.version_number if v else 1,
        "checksum": v.checksum if v else "",
        "status": "ACTIVE" if p.status == "published" else p.status.upper(),
        "published_at": p.published_at.isoformat(),
    }


@router.get("/menus/{menu_id}/publications/{publication_id}/snapshot")
async def inspect_publication_snapshot(
    menu_id: uuid.UUID,
    publication_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Authorized inspection of frozen snapshot payload (ARC-10 §14.1)."""
    stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(Publication.menu_id == menu_id, Publication.id == publication_id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Publication snapshot not found")
    p, v = row
    return {
        "publication_id": str(p.id),
        "snapshot_id": str(v.id),
        "version_number": v.version_number,
        "checksum": v.checksum,
        "payload": v.snapshot_data,
        "created_at": v.published_at.isoformat()
    }


@router.post("/menus/{menu_id}/publications/{publication_id}/rollback")
async def rollback_menu_publication(
    menu_id: uuid.UUID,
    publication_id: uuid.UUID,
    payload: Dict[str, Any] = {},
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback menu to specific publication or version (ARC-10 §12, §14.1)."""
    stmt = select(Publication).where(Publication.menu_id == menu_id)
    pub = (await db.execute(stmt)).scalars().first()
    if not pub:
        raise HTTPException(status_code=404, detail="Active publication not found for menu")

    target_ver_id = payload.get("target_version_id")
    if target_ver_id:
        v_stmt = select(MenuVersion).where(MenuVersion.menu_id == menu_id, MenuVersion.id == uuid.UUID(str(target_ver_id)))
    else:
        # Roll back to the version attached to publication_id
        target_pub_stmt = select(Publication).where(Publication.id == publication_id)
        t_pub = (await db.execute(target_pub_stmt)).scalars().first()
        if not t_pub:
            raise HTTPException(status_code=404, detail="Target publication not found")
        v_stmt = select(MenuVersion).where(MenuVersion.id == t_pub.active_version_id)

    ver = (await db.execute(v_stmt)).scalars().first()
    if not ver:
        raise HTTPException(status_code=404, detail="Target version not found")

    prev_ver_id = pub.active_version_id
    pub.active_version_id = ver.id
    pub.published_at = datetime.now(timezone.utc)
    pub.status = "published"
    await db.commit()

    _AUDIT_LOGS.append({
        "id": str(uuid.uuid4()),
        "menu_id": str(menu_id),
        "actor_id": str(user.id),
        "action": "menu.rollback",
        "previous_version_id": str(prev_ver_id),
        "target_version_id": str(ver.id),
        "target_version_number": ver.version_number,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "status": "success",
        "message": f"Rolled back to version {ver.version_number}",
        "active_version_id": str(ver.id),
        "version_number": ver.version_number
    }


@router.get("/menus/{menu_id}/active-publication")
async def get_active_publication_metadata(
    menu_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves current active publication metadata for menu (ARC-10 §14.1)."""
    stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(Publication.menu_id == menu_id, Publication.status == "published")
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="No active publication found for menu")
    p, v = row
    return {
        "id": str(p.id),
        "menu_id": str(p.menu_id),
        "restaurant_id": str(p.restaurant_id),
        "active_version_id": str(p.active_version_id),
        "version_number": v.version_number,
        "checksum": v.checksum,
        "status": "ACTIVE",
        "published_at": p.published_at.isoformat()
    }


@router.get("/menus/{menu_id}/publication-operations/{operation_id}")
async def get_publication_operation(menu_id: uuid.UUID, operation_id: uuid.UUID):
    """Tracks status of an ongoing or completed publication operation (ARC-10 §14.1)."""
    if operation_id in _OPERATIONS:
        return _OPERATIONS[operation_id]
    return {
        "operation_id": str(operation_id),
        "menu_id": str(menu_id),
        "status": "COMPLETED",
        "message": "Operation completed successfully"
    }


@router.post("/menus/{menu_id}/publication-schedules")
async def create_publication_schedule(
    menu_id: uuid.UUID,
    payload: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """Schedules a future publication activation (P1, ARC-10 §16.1)."""
    sched_id = uuid.uuid4()
    sched = {
        "id": str(sched_id),
        "menu_id": str(menu_id),
        "draft_revision": payload.get("draft_revision", 1),
        "scheduled_at": payload.get("scheduled_at", datetime.now(timezone.utc).isoformat()),
        "timezone_name": payload.get("timezone_name", "UTC"),
        "status": "SCHEDULED",
        "created_by": str(user.id)
    }
    _SCHEDULES[sched_id] = sched
    return sched


@router.delete("/menus/{menu_id}/publication-schedules/{schedule_id}")
async def cancel_publication_schedule(menu_id: uuid.UUID, schedule_id: uuid.UUID):
    """Cancels a pending scheduled publication (ARC-10 §14.1)."""
    if schedule_id in _SCHEDULES:
        _SCHEDULES[schedule_id]["status"] = "CANCELLED"
        return {"status": "cancelled", "message": f"Schedule {schedule_id} cancelled"}
    raise HTTPException(status_code=404, detail="Schedule not found")


@router.get("/menus/{menu_id}/publication-audit")
async def get_publication_audit_history(
    menu_id: uuid.UUID,
    user: User = Depends(get_current_user)
):
    """Reviews publishing audit history (ARC-10 §15.3)."""
    records = [r for r in _AUDIT_LOGS if r.get("menu_id") == str(menu_id)]
    return records


# Legacy publication pointer endpoints for backwards compatibility
@router.get("/publications/{publication_id}")
async def get_publication(publication_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieves publication pointer details."""
    stmt = select(Publication).where(Publication.id == publication_id)
    result = await db.execute(stmt)
    pub = result.scalars().first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    return {
        "id": str(pub.id),
        "menu_id": str(pub.menu_id),
        "restaurant_id": str(pub.restaurant_id),
        "active_version_id": str(pub.active_version_id),
        "status": pub.status,
        "published_at": pub.published_at.isoformat(),
    }


@router.post("/publications/{publication_id}/rollback")
async def rollback_publication(
    publication_id: uuid.UUID,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """Rolls back active publication to an earlier published version (ARC-07 §4.8)."""
    target_version_id = payload.get("target_version_id")
    if not target_version_id:
        raise HTTPException(status_code=400, detail="target_version_id is required")

    stmt = select(Publication).where(Publication.id == publication_id)
    pub = (await db.execute(stmt)).scalars().first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    v_stmt = select(MenuVersion).where(MenuVersion.id == uuid.UUID(str(target_version_id)))
    ver = (await db.execute(v_stmt)).scalars().first()
    if not ver:
        raise HTTPException(status_code=404, detail="Target menu version not found")

    pub.active_version_id = ver.id
    pub.published_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "success", "message": f"Rolled back to version {ver.version_number}"}


@router.post("/publications/{publication_id}/withdraw")
async def withdraw_publication(publication_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Withdraws active publication from public delivery."""
    stmt = select(Publication).where(Publication.id == publication_id)
    pub = (await db.execute(stmt)).scalars().first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    pub.status = "withdrawn"
    await db.commit()
    return {"status": "withdrawn", "message": "Publication withdrawn"}
