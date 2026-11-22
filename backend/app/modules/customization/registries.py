"""
ModularMenu — Customization Platform Registries (ARC-08 §6, §7, §8).
Authoritative catalog of platform themes, layouts, and registered components.
"""

import copy
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MANIFESTS_DIR = REPO_ROOT / "packages" / "contracts" / "manifests"


class PlatformThemeRegistry:
    """Registry of platform-approved theme presets."""

    def __init__(self):
        self._themes: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self):
        manifest_file = MANIFESTS_DIR / "theme-catalogue.json"
        if manifest_file.exists():
            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)
                for t in data.get("themes", []):
                    self._themes[t["id"]] = t
                    self._themes[f"{t['id']}@{t['version']}"] = t

    def get(self, theme_id: str, version: str | None = None) -> dict[str, Any] | None:
        if version:
            v_key = f"{theme_id}@{version}"
            if v_key in self._themes:
                return copy.deepcopy(self._themes[v_key])
            base = self._themes.get(theme_id)
            if base and base.get("version") == version:
                return copy.deepcopy(base)
            return None
        res = self._themes.get(theme_id)
        return copy.deepcopy(res) if res else None

    def list_all(self) -> list[dict[str, Any]]:
        unique = {}
        for k, v in self._themes.items():
            if "@" not in k:
                unique[k] = v
        return copy.deepcopy(list(unique.values()))


class PlatformLayoutRegistry:
    """Registry of platform-approved layout structures."""

    def __init__(self):
        self._layouts: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self):
        manifest_file = MANIFESTS_DIR / "layout-catalogue.json"
        if manifest_file.exists():
            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)
                for layout_def in data.get("layouts", []):
                    self._layouts[layout_def["id"]] = layout_def
                    self._layouts[f"{layout_def['id']}@{layout_def['version']}"] = layout_def

    def get(self, layout_id: str, version: str | None = None) -> dict[str, Any] | None:
        if version:
            v_key = f"{layout_id}@{version}"
            if v_key in self._layouts:
                return copy.deepcopy(self._layouts[v_key])
            base = self._layouts.get(layout_id)
            if base and base.get("version") == version:
                return copy.deepcopy(base)
            return None
        res = self._layouts.get(layout_id)
        return copy.deepcopy(res) if res else None

    def list_all(self) -> list[dict[str, Any]]:
        unique = {}
        for k, v in self._layouts.items():
            if "@" not in k:
                unique[k] = v
        return copy.deepcopy(list(unique.values()))


class PlatformComponentRegistry:
    """Registry of platform-approved components."""

    def __init__(self):
        self._components: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self):
        manifest_file = MANIFESTS_DIR / "component-catalogue.json"
        if manifest_file.exists():
            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)
                for c in data.get("components", []):
                    self._components[c["id"]] = c
                    self._components[f"{c['id']}@{c['version']}"] = c

    def get(self, component_id: str, version: str | None = None) -> dict[str, Any] | None:
        if version:
            v_key = f"{component_id}@{version}"
            if v_key in self._components:
                return copy.deepcopy(self._components[v_key])
            base = self._components.get(component_id)
            if base and base.get("version") == version:
                return copy.deepcopy(base)
            return None
        res = self._components.get(component_id)
        return copy.deepcopy(res) if res else None

    def list_all(self) -> list[dict[str, Any]]:
        unique = {}
        for k, v in self._components.items():
            if "@" not in k:
                unique[k] = v
        return copy.deepcopy(list(unique.values()))


# Shared platform singletons
theme_registry = PlatformThemeRegistry()
layout_registry = PlatformLayoutRegistry()
component_registry = PlatformComponentRegistry()


def get_default_customization_document(
    theme_id: str = "theme-minimal",
    layout_id: str = "layout-grid",
) -> dict[str, Any]:
    """Generates a valid, canonical default customization document."""
    theme = theme_registry.get(theme_id) or theme_registry.get("theme-minimal")
    layout = layout_registry.get(layout_id) or layout_registry.get("layout-grid")

    theme_id_val = theme["id"] if theme else "theme-minimal"
    theme_ver_val = theme["version"] if theme else "1.0.0"
    layout_id_val = layout["id"] if layout else "layout-grid"
    layout_ver_val = layout["version"] if layout else "1.0.0"

    layout_settings = layout.get("default_settings", {}) if layout else {}
    layout_responsive = (
        layout.get(
            "responsive",
            {
                "mobile": {"columns": 1, "navigation": "horizontal-scroll"},
                "tablet": {"columns": 2, "navigation": "horizontal-scroll"},
                "desktop": {"columns": 3, "navigation": "inline"},
            },
        )
        if layout
        else {}
    )

    default_components = [
        {
            "instance_id": "header-1",
            "component_id": "restaurant-header",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "header",
            "position": 1,
            "visible": True,
            "props": {
                "show_logo": True,
                "show_cover": True,
                "logo_alignment": "center",
                "logo_size": "medium",
            },
        },
        {
            "instance_id": "title-1",
            "component_id": "menu-title",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "header",
            "position": 2,
            "visible": True,
            "props": {
                "alignment": "center",
                "show_description": True,
                "typography_style": "display",
            },
        },
        {
            "instance_id": "nav-1",
            "component_id": "category-navigation",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "navigation",
            "position": 3,
            "visible": True,
            "props": {"style": "pills", "position": "sticky", "show_icons": False},
        },
        {
            "instance_id": "cat-head-1",
            "component_id": "category-heading",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "category.header",
            "position": 4,
            "visible": True,
            "props": {"alignment": "left", "show_description": True, "divider": True},
        },
        {
            "instance_id": "item-card-1",
            "component_id": "menu-item-card",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "category.items",
            "position": 5,
            "visible": True,
            "props": {
                "card_style": "elevated",
                "image_visible": True,
                "image_ratio": "4:3",
                "alignment": "left",
                "dense": False,
            },
        },
        {
            "instance_id": "footer-1",
            "component_id": "menu-footer",
            "component_version": "1.0.0",
            "schema_version": "1.0.0",
            "slot": "footer",
            "position": 6,
            "visible": True,
            "props": {"show_fssai": True, "show_tax_notice": True, "alignment": "center"},
        },
    ]

    return copy.deepcopy(
        {
            "configuration_version": "1.0.0",
            "schema_version": "1.0.0",
            "theme": {"id": theme_id_val, "version": theme_ver_val, "overrides": {}},
            "layout": {
                "id": layout_id_val,
                "version": layout_ver_val,
                "settings": layout_settings,
                "responsive": layout_responsive,
            },
            "components": default_components,
            "metadata": {"revision": 1, "updated_at": None},
        }
    )
