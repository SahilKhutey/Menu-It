import uuid
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.dependencies import get_db, verify_restaurant_access
from app.modules.identity.models import Restaurant
from app.modules.menus.models import Category, MenuItem, Menu
from app.modules.menus.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    MenuCreate,
    MenuItemCreate,
    MenuItemOut,
    MenuItemUpdate,
    MenuOut,
    MenuUpdate,
)

router = APIRouter(tags=["Menus & Items"])


# --- Menus Endpoints ---
@router.get("/restaurants/{restaurant_id}/menus", response_model=List[MenuOut])
async def list_menus(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Menu)
        .where(Menu.restaurant_id == restaurant.id)
        .order_by(Menu.sort_order.asc(), Menu.created_at.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/restaurants/{restaurant_id}/menus", response_model=MenuOut, status_code=status.HTTP_201_CREATED)
async def create_menu(
    restaurant_id: uuid.UUID,
    req: MenuCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(Menu).where(Menu.restaurant_id == restaurant.id, Menu.slug == req.slug)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="A menu with this slug already exists for this restaurant.")

    menu = Menu(
        restaurant_id=restaurant.id,
        name=req.name,
        slug=req.slug,
        description=req.description,
        menu_type=req.menu_type,
        status=req.status,
        sort_order=req.sort_order
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
    db: AsyncSession = Depends(get_db)
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
@router.get("/restaurants/{restaurant_id}/menus/{menu_id}/categories", response_model=List[CategoryOut])
async def list_categories(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
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
    items_by_cat: Dict[uuid.UUID, List[MenuItem]] = {}
    for it in items:
        it.variants = []
        items_by_cat.setdefault(it.category_id, []).append(it)

    result_cats: List[CategoryOut] = []
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
                variants=[]
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
                items=cat_items
            )
        )

    return result_cats


@router.post("/restaurants/{restaurant_id}/menus/{menu_id}/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    req: CategoryCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    # Verify menu belongs to restaurant
    menu_check = await db.execute(select(Menu).where(Menu.id == menu_id, Menu.restaurant_id == restaurant.id))
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
        parent_id=req.parent_id
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
        items=[]
    )


# --- Food Items Endpoints ---
@router.post("/restaurants/{restaurant_id}/categories/{category_id}/items", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    restaurant_id: uuid.UUID,
    category_id: uuid.UUID,
    req: MenuItemCreate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
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
        sort_order=req.sort_order
    )
    db.add(item)
    await db.commit()
    return MenuItemOut(
        id=item.id,
        category_id=item.category_id,
        name=item.name,
        description=item.description,
        base_price=float(item.base_price),
        currency_code=item.currency_code,
        dietary_type=item.dietary_type,
        spice_level=item.spice_level,
        image_url=item.image_url,
        ingredients=item.ingredients,
        allergens=item.allergens,
        is_available=item.is_available,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        variants=[]
    )


@router.patch("/restaurants/{restaurant_id}/items/{item_id}", response_model=MenuItemOut)
async def update_item(
    restaurant_id: uuid.UUID,
    item_id: uuid.UUID,
    req: MenuItemUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
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
        base_price=float(item.base_price),
        currency_code=item.currency_code,
        dietary_type=item.dietary_type,
        spice_level=item.spice_level,
        image_url=item.image_url,
        ingredients=item.ingredients,
        allergens=item.allergens,
        is_available=item.is_available,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        variants=[]
    )
