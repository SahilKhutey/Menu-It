"""
Render Input Validator Service (ARC-09 §11, WP-ARC09-11).
Validates structural, semantic, and business rules for menu rendering payloads.
"""

from decimal import Decimal
from typing import Any

from app.modules.rendering.domain.exceptions import (
    RenderComponentNotFoundError,
    RenderInputValidationError,
    RenderPriceInvalidError,
)
from app.modules.rendering.schemas.render_input import (
    RenderValidationIssue,
    RenderValidationResponse,
)

# Standard registered components in ModularMenu catalogue (ARC-08, ARC-09)
REGISTERED_RENDER_COMPONENTS = {
    "RestaurantHeroHeader",
    "RestaurantMinimalHeader",
    "RestaurantProfileHeader",
    "MenuTitleHeader",
    "MenuDescriptionHeader",
    "CategoryPillNav",
    "CategoryDropdownNav",
    "CategorySidebarNav",
    "CategorySection",
    "CategoryTabSection",
    "FoodItemCard",
    "FoodItemListRow",
    "FoodItemCompactRow",
    "DietaryBadgeList",
    "PriceDisplay",
    "MenuFooter",
    "MenuLegalFooter",
}

# Required theme tokens for baseline rendering (ARC-08 §3)
REQUIRED_THEME_TOKENS = {
    "color.primary",
    "color.background",
    "color.surface",
    "color.text.primary",
    "font.family.heading",
    "font.family.body",
}


class RenderInputValidator:
    """Validates render input readiness, detecting errors and warnings."""

    @classmethod
    def validate_payload(cls, data: dict[str, Any]) -> RenderValidationResponse:
        issues: list[RenderValidationIssue] = []

        # 1. Validate Restaurant
        restaurant = data.get("restaurant")
        if not restaurant or not isinstance(restaurant, dict):
            issues.append(
                RenderValidationIssue(
                    severity="error",
                    code="MISSING_RESTAURANT",
                    message="Restaurant object is required",
                    path="restaurant",
                )
            )
        else:
            if not restaurant.get("name"):
                issues.append(
                    RenderValidationIssue(
                        severity="error",
                        code="MISSING_RESTAURANT_NAME",
                        message="Restaurant name is required",
                        path="restaurant.name",
                    )
                )

        # 2. Validate Menu
        menu = data.get("menu")
        if not menu or not isinstance(menu, dict):
            issues.append(
                RenderValidationIssue(
                    severity="error",
                    code="MISSING_MENU",
                    message="Menu object is required",
                    path="menu",
                )
            )

        # 3. Validate Categories & Items
        categories = data.get("categories", [])
        if not isinstance(categories, list):
            issues.append(
                RenderValidationIssue(
                    severity="error",
                    code="INVALID_CATEGORIES",
                    message="Categories must be a list",
                    path="categories",
                )
            )
        else:
            for c_idx, cat in enumerate(categories):
                if not isinstance(cat, dict):
                    continue
                if not cat.get("name"):
                    issues.append(
                        RenderValidationIssue(
                            severity="error",
                            code="MISSING_CATEGORY_NAME",
                            message=f"Category at index {c_idx} missing name",
                            path=f"categories[{c_idx}].name",
                        )
                    )

                items = cat.get("items", [])
                for i_idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue
                    item_name = item.get("name", f"Item #{i_idx}")
                    price = item.get("base_price", item.get("price"))
                    if price is None:
                        issues.append(
                            RenderValidationIssue(
                                severity="error",
                                code="MISSING_PRICE",
                                message=f"Item '{item_name}' is missing a price",
                                path=f"categories[{c_idx}].items[{i_idx}].price",
                            )
                        )
                    else:
                        try:
                            dec_price = Decimal(str(price))
                            if dec_price < Decimal("0.00"):
                                issues.append(
                                    RenderValidationIssue(
                                        severity="error",
                                        code="NEGATIVE_PRICE",
                                        message=f"Item '{item_name}' has negative price: {price}",
                                        path=f"categories[{c_idx}].items[{i_idx}].price",
                                    )
                                )
                        except Exception:
                            issues.append(
                                RenderValidationIssue(
                                    severity="error",
                                    code="INVALID_PRICE_FORMAT",
                                    message=f"Item '{item_name}' has invalid price format: {price}",
                                    path=f"categories[{c_idx}].items[{i_idx}].price",
                                )
                            )

                    # Warnings: missing description or image
                    if not item.get("description"):
                        issues.append(
                            RenderValidationIssue(
                                severity="warning",
                                code="MISSING_DESCRIPTION",
                                message=f"Item '{item_name}' has no description",
                                path=f"categories[{c_idx}].items[{i_idx}].description",
                            )
                        )

        # 4. Validate Layout & Slots
        layout = data.get("layout", {})
        if isinstance(layout, dict):
            slots = layout.get("slots", {})
            for slot, comp_name in slots.items():
                if comp_name not in REGISTERED_RENDER_COMPONENTS:
                    issues.append(
                        RenderValidationIssue(
                            severity="error",
                            code="UNREGISTERED_COMPONENT",
                            message=f"Component '{comp_name}' in slot '{slot}' is not registered",
                            path=f"layout.slots.{slot}",
                        )
                    )

        # 5. Validate Theme
        theme = data.get("theme", {})
        tokens = theme.get("tokens", theme) if isinstance(theme, dict) else {}
        if isinstance(tokens, dict):
            missing_tokens = [tok for tok in REQUIRED_THEME_TOKENS if tok not in tokens]
            if missing_tokens:
                issues.append(
                    RenderValidationIssue(
                        severity="warning",
                        code="MISSING_RECOMMENDED_TOKENS",
                        message=f"Theme is missing recommended tokens: {', '.join(missing_tokens)}",
                        path="theme.tokens",
                    )
                )

        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        is_valid = len(errors) == 0

        readiness = "ready"
        if len(errors) > 0:
            readiness = "blocked"
        elif len(warnings) > 0:
            readiness = "warnings"

        return RenderValidationResponse(
            is_valid=is_valid,
            total_issues=len(issues),
            errors=errors,
            warnings=warnings,
            render_readiness=readiness,
        )

    @classmethod
    def assert_valid(cls, data: dict[str, Any]) -> None:
        """Raises domain exceptions if any fatal error is detected in data."""
        res = cls.validate_payload(data)
        if not res.is_valid:
            first_err = res.errors[0]
            if first_err.code == "NEGATIVE_PRICE":
                raise RenderPriceInvalidError(
                    "item", first_err.message, "Negative price prohibited"
                )
            if first_err.code == "UNREGISTERED_COMPONENT":
                raise RenderComponentNotFoundError(first_err.message)
            raise RenderInputValidationError(
                first_err.message, {"errors": [e.model_dump() for e in res.errors]}
            )
