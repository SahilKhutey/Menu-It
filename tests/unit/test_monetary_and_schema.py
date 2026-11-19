"""
Unit tests for Monetary, Schema, and Identifier Standards (ARC-02 §12.3 TC-ARC02-11, TC-ARC02-12, TC-ARC02-15).
"""
import re
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from app.modules.menus.schemas import MenuItemCreate, MenuItemBase, ItemVariantCreate
from app.main import app


def test_monetary_precision_decimal_representation():
    """
    TC-ARC02-11 / CON-05:
    Monetary values must be stored and computed with exact decimal precision,
    preventing floating-point rounding inaccuracies.
    """
    # Verify Decimal arithmetic preserves cents/paise accurately
    price_a = Decimal("425.25")
    price_b = Decimal("74.75")
    total = price_a + price_b
    assert total == Decimal("500.00")

    # Verify Pydantic schema parses decimal correctly
    item = MenuItemCreate(
        name="Artisanal Cold Brew",
        base_price=Decimal("280.50"),
        currency_code="INR",
        dietary_type="vegan"
    )
    assert isinstance(item.base_price, Decimal)
    assert item.base_price == Decimal("280.50")


def test_slug_format_validation():
    """
    ARC-02 §4.1:
    Restaurant, category, and menu slugs must follow lowercase kebab-case regex:
    ^[a-z0-9]+(?:-[a-z0-9]+)*$
    """
    slug_regex = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    valid_slugs = ["bombay-canteen", "subko-coffee", "menu-2026", "dinner", "cocktails-and-bites"]
    invalid_slugs = ["Bombay-Canteen", "subko_coffee", "menu--2026", "-invalid", "invalid-", "spaces in slug", "emoji🍔"]

    for s in valid_slugs:
        assert slug_regex.match(s) is not None, f"Expected valid slug: {s}"

    for s in invalid_slugs:
        assert slug_regex.match(s) is None, f"Expected invalid slug: {s}"


def test_openapi_schema_generation_and_validity():
    """
    TC-ARC02-15 / WP-ARC02-04:
    OpenAPI 3.1 specification must generate cleanly without serialization errors
    and contain all declared API v1 route definitions.
    """
    openapi_schema = app.openapi()
    assert openapi_schema is not None
    assert "openapi" in openapi_schema
    assert openapi_schema["info"]["title"] == "ModularMenu"
    assert "/api/v1/public/restaurants/{slug}/menu" in openapi_schema["paths"]
    assert "/api/v1/auth/login" in openapi_schema["paths"]
    assert "/health" in openapi_schema["paths"]
