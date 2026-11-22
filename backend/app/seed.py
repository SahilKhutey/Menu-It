import asyncio
import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.modules.identity.models import Organization, Restaurant, RestaurantMember, User
from app.modules.menus.models import Category, ItemVariant, Menu, MenuItem, MenuVersion, Publication
from app.modules.themes.models import RestaurantDesignConfig, Theme
from app.modules.themes.presets import THEME_PRESETS


async def seed_data():
    print("🌱 Initializing and seeding database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        check = await db.execute(select(User).where(User.email == "admin@modularmenu.in"))
        if check.scalars().first():
            print("Database already seeded. Skipping.")
            return

        print("1. Seeding Platform Admin & Users...")
        admin_user = User(
            email="admin@modularmenu.in",
            password_hash=hash_password("AdminPass123!"),
            full_name="Platform Administrator",
            is_platform_admin=True,
            status="active",
        )
        chef_user = User(
            email="chef@bombaycanteen.com",
            password_hash=hash_password("Password123!"),
            full_name="Chef Floyd Cardoz",
            is_platform_admin=False,
            status="active",
        )
        subko_user = User(
            email="manager@subko.coffee",
            password_hash=hash_password("Password123!"),
            full_name="Rahul Reddy",
            is_platform_admin=False,
            status="active",
        )
        db.add_all([admin_user, chef_user, subko_user])
        await db.flush()

        print("2. Seeding Organizations & Restaurants...")
        # Restaurant 1: The Bombay Canteen
        hunger_inc = Organization(name="Hunger Inc Hospitality", slug="hunger-inc", status="active")
        db.add(hunger_inc)
        await db.flush()

        tbc_rest = Restaurant(
            organization_id=hunger_inc.id,
            name="The Bombay Canteen",
            slug="the-bombay-canteen",
            description="Modern Indian dining celebrating regional cultures and indigenous seasonal produce.",
            logo_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=200&h=200&fit=crop",
            cover_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200&h=400&fit=crop",
            status="active",
        )
        db.add(tbc_rest)
        await db.flush()

        db.add(
            RestaurantMember(
                organization_id=hunger_inc.id,
                restaurant_id=tbc_rest.id,
                user_id=chef_user.id,
                role="owner",
            )
        )

        # Restaurant 2: Subko Specialty Coffee
        subko_org = Organization(name="Subko India", slug="subko-india", status="active")
        db.add(subko_org)
        await db.flush()

        subko_rest = Restaurant(
            organization_id=subko_org.id,
            name="Subko Specialty Coffee & Bakehouse",
            slug="subko-coffee",
            description="Specialty coffee roastery and craft bakehouse focusing on subcontinent-origin beans.",
            logo_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=200&h=200&fit=crop",
            cover_url="https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1200&h=400&fit=crop",
            status="active",
        )
        db.add(subko_rest)
        await db.flush()

        db.add(
            RestaurantMember(
                organization_id=subko_org.id,
                restaurant_id=subko_rest.id,
                user_id=subko_user.id,
                role="owner",
            )
        )

        print("3. Seeding Theme Presets into Database...")
        theme_map = {}
        for preset in THEME_PRESETS:
            theme_obj = Theme(
                name=preset["name"],
                theme_key=preset["theme_key"],
                tokens=preset["tokens"],
                is_system_preset=True,
            )
            db.add(theme_obj)
            await db.flush()
            theme_map[preset["theme_key"]] = theme_obj

        # Design Config for The Bombay Canteen (Luxury Theme)
        luxury_theme = theme_map["luxury"]
        db.add(
            RestaurantDesignConfig(
                restaurant_id=tbc_rest.id,
                theme_id=luxury_theme.id,
                layout_config={"type": "category_first", "card_style": "elevated"},
                custom_tokens={},
                config_version=1,
            )
        )

        # Design Config for Subko (Minimal Theme)
        minimal_theme = theme_map["minimal"]
        db.add(
            RestaurantDesignConfig(
                restaurant_id=subko_rest.id,
                theme_id=minimal_theme.id,
                layout_config={"type": "category_first", "card_style": "bordered"},
                custom_tokens={},
                config_version=1,
            )
        )
        await db.flush()

        print("4. Seeding Menus, Categories and Food Items...")
        # Menu for The Bombay Canteen
        tbc_menu = Menu(
            restaurant_id=tbc_rest.id,
            name="Dinner Tasting & A La Carte",
            slug="dinner",
            description="Our evening showcase of regional Indian specialties.",
            menu_type="dinner",
            status="active",
            sort_order=1,
        )
        db.add(tbc_menu)
        await db.flush()

        # Categories for TBC
        cat_small = Category(
            restaurant_id=tbc_rest.id,
            menu_id=tbc_menu.id,
            name="Small Plates & Chintu",
            description="Quick, flavorful bites inspired by Indian street food culture.",
            sort_order=1,
            is_visible=True,
        )
        cat_big = Category(
            restaurant_id=tbc_rest.id,
            menu_id=tbc_menu.id,
            name="Big Plates & Curries",
            description="Hearty heritage curries cooked with stone-ground regional spice blends.",
            sort_order=2,
            is_visible=True,
        )
        cat_breads = Category(
            restaurant_id=tbc_rest.id,
            menu_id=tbc_menu.id,
            name="Breads & Heirloom Rice",
            description="Clay tandoor fired breads and indigenous grain preparations.",
            sort_order=3,
            is_visible=True,
        )
        cat_desserts = Category(
            restaurant_id=tbc_rest.id,
            menu_id=tbc_menu.id,
            name="Desserts & Mithai",
            description="Modern nostalgic desserts reimagined with local dairy and fruits.",
            sort_order=4,
            is_visible=True,
        )
        db.add_all([cat_small, cat_big, cat_breads, cat_desserts])
        await db.flush()

        # Food Items for TBC
        item1 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_small.id,
            name="Barley & Jowar Salad",
            description="Pomegranate seeds, spiced hung curd dressing, crispy sev, puffed amaranth.",
            base_price=425.00,
            currency_code="INR",
            dietary_type="vegetarian",
            spice_level="mild",
            ingredients=["Barley", "Jowar", "Pomegranate", "Hung Curd", "Crispy Sev"],
            allergens=["Dairy"],
            is_available=True,
            is_featured=True,
            sort_order=1,
        )
        item2 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_small.id,
            name="Chettinad Fried Chicken",
            description="Curry leaf crisp, shallot chutney dip, buttermilk batter, crushed tellicherry pepper.",
            base_price=525.00,
            currency_code="INR",
            dietary_type="non_veg",
            spice_level="hot",
            ingredients=["Farm Chicken", "Tellicherry Pepper", "Shallots", "Curry Leaves"],
            allergens=["Gluten", "Dairy"],
            is_available=True,
            is_featured=True,
            sort_order=2,
        )
        item3 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_small.id,
            name="Eggs Kejriwal Toast",
            description="Sunny side up organic egg, toasted sourdough, melted sharp white cheddar, green chilli tadka.",
            base_price=450.00,
            currency_code="INR",
            dietary_type="egg",
            spice_level="medium",
            ingredients=["Organic Egg", "Sourdough", "Aged Cheddar", "Green Chillies"],
            allergens=["Gluten", "Dairy", "Egg"],
            is_available=True,
            is_featured=False,
            sort_order=3,
        )
        item4 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_big.id,
            name="Paneer & Fig Kofta",
            description="Almond yogurt gravy, fenugreek cream, served with flaky malabar parotta.",
            base_price=650.00,
            currency_code="INR",
            dietary_type="vegetarian",
            spice_level="mild",
            ingredients=["Cottage Cheese", "Dried Figs", "Almonds", "Fenugreek"],
            allergens=["Dairy", "Nuts"],
            is_available=True,
            is_featured=True,
            sort_order=1,
        )
        item5 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_big.id,
            name="Kerala Roast Duck",
            description="Slow-roasted duck leg, tellicherry black pepper, shallots, cold-pressed coconut oil drizzle.",
            base_price=895.00,
            currency_code="INR",
            dietary_type="non_veg",
            spice_level="hot",
            ingredients=["Duck Leg", "Black Pepper", "Shallots", "Curry Leaf"],
            allergens=[],
            is_available=True,
            is_featured=True,
            sort_order=2,
        )
        item6 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_breads.id,
            name="Truffle & Wild Mushroom Kulcha",
            description="Smoked scamorza cheese, fresh coriander butter, black truffle glaze.",
            base_price=375.00,
            currency_code="INR",
            dietary_type="vegetarian",
            spice_level="none",
            ingredients=["Wild Mushrooms", "Scamorza", "Flour", "Truffle Oil"],
            allergens=["Gluten", "Dairy"],
            is_available=True,
            is_featured=True,
            sort_order=1,
        )
        item7 = MenuItem(
            restaurant_id=tbc_rest.id,
            category_id=cat_desserts.id,
            name="Filter Coffee Tres Leches",
            description="Chikmagalur espresso soaked sponge cake, condensed milk foam, candied cocoa nibs.",
            base_price=420.00,
            currency_code="INR",
            dietary_type="vegetarian",
            spice_level="none",
            ingredients=["Espresso", "Milk", "Flour", "Cocoa Nibs"],
            allergens=["Gluten", "Dairy"],
            is_available=True,
            is_featured=True,
            sort_order=1,
        )
        db.add_all([item1, item2, item3, item4, item5, item6, item7])
        await db.flush()

        # Add Variants to item2 (Half / Full)
        db.add(
            ItemVariant(
                restaurant_id=tbc_rest.id,
                menu_item_id=item2.id,
                name="Regular Portion",
                price_delta=0.00,
                is_available=True,
                sort_order=1,
            )
        )
        db.add(
            ItemVariant(
                restaurant_id=tbc_rest.id,
                menu_item_id=item2.id,
                name="Large Sharing Bowl",
                price_delta=250.00,
                is_available=True,
                sort_order=2,
            )
        )
        await db.flush()

        print("5. Publishing Initial Version Snapshot for The Bombay Canteen...")
        # Compile snapshot
        snapshot_payload = {
            "restaurant": {
                "id": str(tbc_rest.id),
                "name": tbc_rest.name,
                "slug": tbc_rest.slug,
                "description": tbc_rest.description,
                "logo_url": tbc_rest.logo_url,
                "cover_url": tbc_rest.cover_url,
            },
            "menu": {
                "id": str(tbc_menu.id),
                "name": tbc_menu.name,
                "slug": tbc_menu.slug,
                "description": tbc_menu.description,
                "menu_type": tbc_menu.menu_type,
            },
            "categories": [
                {
                    "id": str(cat_small.id),
                    "name": cat_small.name,
                    "description": cat_small.description,
                    "sort_order": cat_small.sort_order,
                    "items": [
                        {
                            "id": str(item1.id),
                            "name": item1.name,
                            "description": item1.description,
                            "base_price": float(item1.base_price),
                            "currency_code": item1.currency_code,
                            "dietary_type": item1.dietary_type,
                            "spice_level": item1.spice_level,
                            "allergens": item1.allergens,
                            "is_available": item1.is_available,
                            "is_featured": item1.is_featured,
                            "sort_order": item1.sort_order,
                            "variants": [],
                        },
                        {
                            "id": str(item2.id),
                            "name": item2.name,
                            "description": item2.description,
                            "base_price": float(item2.base_price),
                            "currency_code": item2.currency_code,
                            "dietary_type": item2.dietary_type,
                            "spice_level": item2.spice_level,
                            "allergens": item2.allergens,
                            "is_available": item2.is_available,
                            "is_featured": item2.is_featured,
                            "sort_order": item2.sort_order,
                            "variants": [
                                {
                                    "name": "Regular Portion",
                                    "price_delta": 0.00,
                                    "is_available": True,
                                },
                                {
                                    "name": "Large Sharing Bowl",
                                    "price_delta": 250.00,
                                    "is_available": True,
                                },
                            ],
                        },
                        {
                            "id": str(item3.id),
                            "name": item3.name,
                            "description": item3.description,
                            "base_price": float(item3.base_price),
                            "currency_code": item3.currency_code,
                            "dietary_type": item3.dietary_type,
                            "spice_level": item3.spice_level,
                            "allergens": item3.allergens,
                            "is_available": item3.is_available,
                            "is_featured": item3.is_featured,
                            "sort_order": item3.sort_order,
                            "variants": [],
                        },
                    ],
                },
                {
                    "id": str(cat_big.id),
                    "name": cat_big.name,
                    "description": cat_big.description,
                    "sort_order": cat_big.sort_order,
                    "items": [
                        {
                            "id": str(item4.id),
                            "name": item4.name,
                            "description": item4.description,
                            "base_price": float(item4.base_price),
                            "currency_code": item4.currency_code,
                            "dietary_type": item4.dietary_type,
                            "spice_level": item4.spice_level,
                            "allergens": item4.allergens,
                            "is_available": item4.is_available,
                            "is_featured": item4.is_featured,
                            "sort_order": item4.sort_order,
                            "variants": [],
                        },
                        {
                            "id": str(item5.id),
                            "name": item5.name,
                            "description": item5.description,
                            "base_price": float(item5.base_price),
                            "currency_code": item5.currency_code,
                            "dietary_type": item5.dietary_type,
                            "spice_level": item5.spice_level,
                            "allergens": item5.allergens,
                            "is_available": item5.is_available,
                            "is_featured": item5.is_featured,
                            "sort_order": item5.sort_order,
                            "variants": [],
                        },
                    ],
                },
                {
                    "id": str(cat_breads.id),
                    "name": cat_breads.name,
                    "description": cat_breads.description,
                    "sort_order": cat_breads.sort_order,
                    "items": [
                        {
                            "id": str(item6.id),
                            "name": item6.name,
                            "description": item6.description,
                            "base_price": float(item6.base_price),
                            "currency_code": item6.currency_code,
                            "dietary_type": item6.dietary_type,
                            "spice_level": item6.spice_level,
                            "allergens": item6.allergens,
                            "is_available": item6.is_available,
                            "is_featured": item6.is_featured,
                            "sort_order": item6.sort_order,
                            "variants": [],
                        }
                    ],
                },
                {
                    "id": str(cat_desserts.id),
                    "name": cat_desserts.name,
                    "description": cat_desserts.description,
                    "sort_order": cat_desserts.sort_order,
                    "items": [
                        {
                            "id": str(item7.id),
                            "name": item7.name,
                            "description": item7.description,
                            "base_price": float(item7.base_price),
                            "currency_code": item7.currency_code,
                            "dietary_type": item7.dietary_type,
                            "spice_level": item7.spice_level,
                            "allergens": item7.allergens,
                            "is_available": item7.is_available,
                            "is_featured": item7.is_featured,
                            "sort_order": item7.sort_order,
                            "variants": [],
                        }
                    ],
                },
            ],
            "theme": luxury_theme.tokens,
            "layout": {"type": "category_first", "card_style": "elevated"},
            "published_at": datetime.now(UTC).isoformat(),
        }

        checksum = hashlib.sha256(
            json.dumps(snapshot_payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        version_1 = MenuVersion(
            restaurant_id=tbc_rest.id,
            menu_id=tbc_menu.id,
            version_number=1,
            snapshot_data=snapshot_payload,
            checksum=checksum,
            published_by=chef_user.id,
        )
        db.add(version_1)
        await db.flush()

        db.add(
            Publication(
                restaurant_id=tbc_rest.id,
                menu_id=tbc_menu.id,
                active_version_id=version_1.id,
                status="published",
            )
        )

        await db.commit()
        print("✅ Database seeding completed successfully!")
        print("Created Admin: admin@modularmenu.in / AdminPass123!")
        print("Created Chef:  chef@bombaycanteen.com / Password123!")
        print("Published URL: /r/the-bombay-canteen")


if __name__ == "__main__":
    asyncio.run(seed_data())
