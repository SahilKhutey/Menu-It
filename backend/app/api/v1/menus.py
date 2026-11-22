import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db, verify_restaurant_access
from app.modules.identity.models import Restaurant
from app.modules.menus.models import Category, Menu, MenuItem
from app.modules.menus.schemas import (
    CategoryCreate,
    CategoryOut,
    MenuCreate,
    MenuItemCreate,
    MenuItemOut,
    MenuItemUpdate,
    MenuOut,
    MenuUpdate,
)

router = APIRouter(tags=["Menus & Items"])


# --- Menus Endpoints ---
@router.get("/restaurants/{restaurant_id}/menus", response_model=list[MenuOut])
async def list_menus(
    restaurant_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Menu)
        .where(Menu.restaurant_id == restaurant.id)
        .order_by(Menu.sort_order.asc(), Menu.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/restaurants/{restaurant_id}/menus",
    response_model=MenuOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_menu(
    restaurant_id: uuid.UUID,
    req: MenuCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Menu).where(Menu.restaurant_id == restaurant.id, Menu.slug == req.slug)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=400, detail="A menu with this slug already exists for this restaurant."
        )

    menu = Menu(
        restaurant_id=restaurant.id,
        name=req.name,
        slug=req.slug,
        description=req.description,
        menu_type=req.menu_type,
        status=req.status,
        sort_order=req.sort_order,
    )
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu


@router.patch("/restaurants/{restaurant_id}/menus/{menu_id}", response_model=MenuOut)
async def update_menu(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    req: MenuUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Menu).where(Menu.id == menu_id, Menu.restaurant_id == restaurant.id)
    result = await db.execute(stmt)
    menu = result.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(menu, field, val)

    await db.commit()
    await db.refresh(menu)
    return menu


# --- Categories Endpoints ---
@router.get(
    "/restaurants/{restaurant_id}/menus/{menu_id}/categories", response_model=list[CategoryOut]
)
async def list_categories(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant.id, Category.menu_id == menu_id)
        .order_by(Category.sort_order.asc())
    )
    result = await db.execute(stmt)
    categories = result.scalars().all()

    item_stmt = (
        select(MenuItem)
        .where(MenuItem.restaurant_id == restaurant.id)
        .order_by(MenuItem.sort_order.asc())
    )
    items = (await db.execute(item_stmt)).scalars().all()
    items_by_cat: dict[uuid.UUID, list[MenuItem]] = {}
    for it in items:
        it.variants = []
        items_by_cat.setdefault(it.category_id, []).append(it)

    result_cats: list[CategoryOut] = []
    for cat in categories:
        cat_items = [
            MenuItemOut(
                id=it.id,
                category_id=it.category_id,
                name=it.name,
                description=it.description,
                base_price=float(it.base_price),
                currency_code=it.currency_code,
                dietary_type=it.dietary_type,
                spice_level=it.spice_level,
                image_url=it.image_url,
                ingredients=it.ingredients,
                allergens=it.allergens,
                is_available=it.is_available,
                is_featured=it.is_featured,
                sort_order=it.sort_order,
                variants=[],
            )
            for it in items_by_cat.get(cat.id, [])
        ]
        result_cats.append(
            CategoryOut(
                id=cat.id,
                menu_id=cat.menu_id,
                name=cat.name,
                description=cat.description,
                image_url=cat.image_url,
                sort_order=cat.sort_order,
                is_visible=cat.is_visible,
                parent_id=cat.parent_id,
                items=cat_items,
            )
        )

    return result_cats


@router.post(
    "/restaurants/{restaurant_id}/menus/{menu_id}/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    req: CategoryCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    # Verify menu belongs to restaurant
    menu_check = await db.execute(
        select(Menu).where(Menu.id == menu_id, Menu.restaurant_id == restaurant.id)
    )
    if not menu_check.scalars().first():
        raise HTTPException(status_code=404, detail="Menu not found for this restaurant.")

    cat = Category(
        restaurant_id=restaurant.id,
        menu_id=menu_id,
        name=req.name,
        description=req.description,
        image_url=req.image_url,
        sort_order=req.sort_order,
        is_visible=req.is_visible,
        parent_id=req.parent_id,
    )
    db.add(cat)
    await db.commit()
    return CategoryOut(
        id=cat.id,
        menu_id=cat.menu_id,
        name=cat.name,
        description=cat.description,
        image_url=cat.image_url,
        sort_order=cat.sort_order,
        is_visible=cat.is_visible,
        parent_id=cat.parent_id,
        items=[],
    )


# --- Food Items Endpoints ---
@router.post(
    "/restaurants/{restaurant_id}/categories/{category_id}/items",
    response_model=MenuItemOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    restaurant_id: uuid.UUID,
    category_id: uuid.UUID,
    req: MenuItemCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    cat_check = await db.execute(
        select(Category).where(Category.id == category_id, Category.restaurant_id == restaurant.id)
    )
    if not cat_check.scalars().first():
        raise HTTPException(status_code=404, detail="Category not found for this restaurant.")

    item = MenuItem(
        restaurant_id=restaurant.id,
        category_id=category_id,
        name=req.name,
        description=req.description,
        base_price=req.base_price,
        currency_code=req.currency_code,
        dietary_type=req.dietary_type,
        spice_level=req.spice_level,
        image_url=req.image_url,
        ingredients=req.ingredients,
        allergens=req.allergens,
        is_available=req.is_available,
        is_featured=req.is_featured,
        sort_order=req.sort_order,
    )
    db.add(item)
    await db.commit()
    return MenuItemOut(
        id=item.id,
        category_id=item.category_id,
        name=item.name,
        description=item.description,
        base_price=item.base_price,
        currency_code=item.currency_code,
        dietary_type=item.dietary_type,
        spice_level=item.spice_level,
        image_url=item.image_url,
        ingredients=item.ingredients,
        allergens=item.allergens,
        is_available=item.is_available,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        variants=[],
    )


@router.get("/restaurants/{restaurant_id}/items/{item_id}", response_model=MenuItemOut)
async def get_item(
    restaurant_id: uuid.UUID,
    item_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(MenuItem)
        .options(selectinload(MenuItem.variants))
        .where(MenuItem.id == item_id, MenuItem.restaurant_id == restaurant.id)
    )
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found for this restaurant.")

    return MenuItemOut(
        id=item.id,
        category_id=item.category_id,
        name=item.name,
        description=item.description,
        base_price=item.base_price,
        currency_code=item.currency_code,
        dietary_type=item.dietary_type,
        spice_level=item.spice_level,
        image_url=item.image_url,
        ingredients=item.ingredients,
        allergens=item.allergens,
        is_available=item.is_available,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        variants=[],
    )


@router.patch("/restaurants/{restaurant_id}/items/{item_id}", response_model=MenuItemOut)
async def update_item(
    restaurant_id: uuid.UUID,
    item_id: uuid.UUID,
    req: MenuItemUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(MenuItem)
        .options(selectinload(MenuItem.variants))
        .where(MenuItem.id == item_id, MenuItem.restaurant_id == restaurant.id)
    )
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found for this restaurant.")

    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(item, field, val)

    await db.commit()
    return MenuItemOut(
        id=item.id,
        category_id=item.category_id,
        name=item.name,
        description=item.description,
        base_price=item.base_price,
        currency_code=item.currency_code,
        dietary_type=item.dietary_type,
        spice_level=item.spice_level,
        image_url=item.image_url,
        ingredients=item.ingredients,
        allergens=item.allergens,
        is_available=item.is_available,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        variants=[],
    )


# --- Canonical ARC-07 Menu Endpoints (ARC-07 §3.1, §4.4) ---


@router.get("/menus/{menu_id}", response_model=MenuOut)
async def get_menu_by_id(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieves menu details directly by menu_id (ARC-07 §4.4)."""
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")
    return menu


@router.patch("/menus/{menu_id}", response_model=MenuOut)
async def update_menu_by_id(
    menu_id: uuid.UUID, req: MenuUpdate, db: AsyncSession = Depends(get_db)
):
    """Updates menu metadata directly by menu_id (ARC-07 §4.4)."""
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(menu, field, val)

    await db.commit()
    await db.refresh(menu)
    return menu


@router.delete("/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_by_id(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Archives or deletes menu directly by menu_id (ARC-07 §4.4)."""
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().first()
    if menu:
        await db.delete(menu)
        await db.commit()
    return None


@router.get("/menus/{menu_id}/categories", response_model=list[CategoryOut])
async def list_menu_categories_by_id(menu_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Lists categories under a menu (ARC-07 §4.4)."""
    stmt = (
        select(Category)
        .options(selectinload(Category.items))
        .where(Category.menu_id == menu_id)
        .order_by(Category.sort_order.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/menus/{menu_id}/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED
)
async def create_menu_category_by_id(
    menu_id: uuid.UUID, req: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    """Creates category under a menu (ARC-07 §4.4)."""
    res = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    category = Category(
        restaurant_id=menu.restaurant_id,
        menu_id=menu.id,
        name=req.name,
        description=req.description,
        sort_order=req.display_order if req.display_order is not None else req.sort_order,
        is_visible=req.is_visible,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryOut(
        id=category.id,
        menu_id=category.menu_id,
        name=category.name,
        slug=req.slug,
        description=category.description,
        image_url=category.image_url,
        sort_order=category.sort_order,
        display_order=category.sort_order,
        is_visible=category.is_visible,
        parent_id=category.parent_id,
        items=[],
    )


@router.post("/menus/{menu_id}/categories/reorder")
async def reorder_menu_categories(
    menu_id: uuid.UUID, payload: dict[str, Any], db: AsyncSession = Depends(get_db)
):
    """Reorders categories within a menu (ARC-07 §4.4)."""
    items = payload.get("items") or payload.get("category_orders") or []
    for it in items:
        cat_id = it.get("id")
        sort_order = it.get("sort_order") if "sort_order" in it else it.get("display_order", 0)
        if cat_id:
            res = await db.execute(select(Category).where(Category.id == uuid.UUID(str(cat_id))))
            cat = res.scalars().first()
            if cat:
                cat.sort_order = sort_order
    await db.commit()
    return {"status": "success", "success": True, "reordered_count": len(items)}
