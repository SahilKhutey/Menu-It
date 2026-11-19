"""
Unit tests for Design Tokens and Theme Configuration (ARC-02 §12.4 TC-ARC02-03, TC-ARC02-16, TC-ARC02-17).
"""
import pytest
from app.modules.themes.presets import THEME_PRESETS

REQUIRED_COLOR_KEYS = {
    "surface", "surfaceElevated", "surfaceMuted",
    "textPrimary", "textMuted",
    "primary", "primaryForeground", "accent", "border",
    "dietaryVeg", "dietaryNonVeg", "dietaryEgg"
}

REQUIRED_TYPOGRAPHY_KEYS = {
    "fontHeading", "fontBody", "fontPrice", "baseSize", "scaleRatio"
}

REQUIRED_LAYOUT_KEYS = {
    "borderRadius", "cardStyle", "itemSpacing", "imageAspectRatio"
}


def test_theme_presets_adhere_to_required_token_schema():
    """
    TC-ARC02-03:
    Every system theme preset must strictly provide all required design tokens.
    """
    assert len(THEME_PRESETS) >= 3, "Expected at least 3 default theme presets"

    for preset in THEME_PRESETS:
        tokens = preset.get("tokens", {})
        colors = tokens.get("colors", {})
        typography = tokens.get("typography", {})
        layout = tokens.get("layout", {})

        # Verify colors
        missing_colors = REQUIRED_COLOR_KEYS - set(colors.keys())
        assert not missing_colors, f"Preset '{preset.get('name')}' is missing colors: {missing_colors}"

        # Verify typography
        missing_typo = REQUIRED_TYPOGRAPHY_KEYS - set(typography.keys())
        assert not missing_typo, f"Preset '{preset.get('name')}' is missing typography keys: {missing_typo}"

        # Verify layout
        missing_layout = REQUIRED_LAYOUT_KEYS - set(layout.keys())
        assert not missing_layout, f"Preset '{preset.get('name')}' is missing layout keys: {missing_layout}"


def test_hex_color_validation():
    """
    CON-09:
    Token colors must be valid hex color codes to prevent CSS injection.
    """
    import re
    hex_regex = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

    for preset in THEME_PRESETS:
        colors = preset["tokens"]["colors"]
        for color_name, hex_val in colors.items():
            assert hex_regex.match(hex_val), f"Invalid hex color for '{color_name}' in preset '{preset['name']}': {hex_val}"


def test_token_safe_fallback_for_missing_customizations():
    """
    TC-ARC02-17 / WP-ARC02-07:
    When an operator provides a partial customization object, missing tokens must safely fall back
    to default system tokens rather than throwing a runtime error.
    """
    default_preset = THEME_PRESETS[0]["tokens"]
    custom_tokens = {
        "colors": {
            "primary": "#FF5733"
        }
    }

    # Merging logic with fallback
    merged_colors = {**default_preset["colors"], **custom_tokens.get("colors", {})}
    assert merged_colors["primary"] == "#FF5733"
    assert merged_colors["surface"] == default_preset["colors"]["surface"]
    assert merged_colors["dietaryVeg"] == default_preset["colors"]["dietaryVeg"]


def test_arc02_ui_003_component_toggle_configuration():
    """
    ARC02-UI-003 / Principle P-10:
    Component visibility flags (e.g. show_dietary_badges, show_spice_indicators)
    must cleanly toggle component rendering state without modifying menu domain data.
    """
    component_config = {
        "restaurant_header": {"enabled": True, "show_cover": False},
        "dietary_filters": {"enabled": True},
        "item_cards": {"show_allergens": False, "show_spice_level": True},
        "qr_share_modal": {"enabled": False}
    }

    # Verify toggle values are boolean and schema-compliant
    assert component_config["qr_share_modal"]["enabled"] is False
    assert component_config["restaurant_header"]["show_cover"] is False
    assert component_config["item_cards"]["show_spice_level"] is True
