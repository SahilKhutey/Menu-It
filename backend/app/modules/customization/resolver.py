"""
ModularMenu — Python Theme & Customization Resolution Engine (ARC-08 §11).
Authoritative, deterministic server-side merge of theme presets, restaurant overrides,
layout settings, and component default properties.
"""
from typing import Any, Dict, List
from app.modules.customization.registries import component_registry, layout_registry, theme_registry


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically merges override dict into base dict without mutating inputs."""
    result = dict(base)
    for key, value in (override or {}).items():
        if value is None:
            # Null reset if key exists
            result.pop(key, None)
            continue
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def resolve_menu_customization(config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolves raw customization document into normalized, fully-populated presentation configuration."""
    theme_sel = config.get("theme", {})
    theme_id = theme_sel.get("id", "theme-minimal")
    theme_ver = theme_sel.get("version", "1.0.0")
    theme_def = theme_registry.get(theme_id, theme_ver) or theme_registry.get("theme-minimal")

    base_tokens = theme_def.get("tokens", {}) if theme_def else {}
    overrides = theme_sel.get("overrides", {})
    resolved_tokens = deep_merge(base_tokens, overrides)

    layout_sel = config.get("layout", {})
    layout_id = layout_sel.get("id", "layout-grid")
    layout_ver = layout_sel.get("version", "1.0.0")
    layout_def = layout_registry.get(layout_id, layout_ver) or layout_registry.get("layout-grid")

    default_settings = layout_def.get("default_settings", {}) if layout_def else {}
    layout_settings = deep_merge(default_settings, layout_sel.get("settings", {}))

    default_responsive = layout_def.get("responsive", {}) if layout_def else {}
    layout_responsive = deep_merge(default_responsive, layout_sel.get("responsive", {}))

    resolved_components: List[Dict[str, Any]] = []
    for comp in config.get("components", []):
        c_id = comp.get("component_id")
        c_ver = comp.get("component_version", "1.0.0")
        c_def = component_registry.get(c_id, c_ver)
        c_defaults = c_def.get("default_props", {}) if c_def else {}
        c_merged_props = deep_merge(c_defaults, comp.get("props", {}))

        resolved_components.append({
            "instanceId": comp.get("instance_id"),
            "componentId": c_id,
            "componentVersion": c_ver,
            "slot": comp.get("slot"),
            "position": comp.get("position", 0),
            "visible": comp.get("visible", True),
            "props": c_merged_props,
        })

    resolved_components.sort(key=lambda x: x["position"])

    return {
        "configurationVersion": "1.0.0",
        "theme": {
            "themeId": theme_id,
            "themeVersion": theme_ver,
            "tokens": resolved_tokens,
        },
        "layout": {
            "id": layout_id,
            "version": layout_ver,
            "settings": layout_settings,
            "responsive": layout_responsive,
        },
        "components": resolved_components,
    }
