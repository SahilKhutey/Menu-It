"""
ModularMenu — Customization Validation Engine (ARC-08 §10).
Authoritative server-side schema, policy, and security validation pipeline.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import jsonschema

from app.modules.customization.registries import component_registry, layout_registry, theme_registry

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SCHEMAS_DIR = REPO_ROOT / "packages" / "contracts" / "schemas"

# Security constraints (ARC-08 §19.1)
MAX_DOCUMENT_BYTES = 256 * 1024  # 256 KB
MAX_COMPONENTS = 100
MAX_JSON_DEPTH = 10

DANGEROUS_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"data\s*:\s*text/html", re.IGNORECASE),
    re.compile(r"on[a-z]+\s*=", re.IGNORECASE),
    re.compile(r"expression\s*\(", re.IGNORECASE),
    re.compile(r"@import", re.IGNORECASE),
]


class CustomizationValidationError(Exception):
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__(f"Customization validation failed with {len(errors)} error(s).")


def get_json_depth(obj: Any, current_depth: int = 1) -> int:
    if isinstance(obj, dict) and obj:
        return max(get_json_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list) and obj:
        return max(get_json_depth(v, current_depth + 1) for v in obj)
    return current_depth


class CustomizationValidator:
    """Full-pipeline customization validator."""

    def __init__(self):
        self._load_schemas()

    def _load_schemas(self):
        doc_schema_path = SCHEMAS_DIR / "menu-customization.schema.json"
        with open(doc_schema_path, "r", encoding="utf-8") as f:
            self._doc_schema = json.load(f)
        self._doc_validator = jsonschema.Draft202012Validator(self._doc_schema)

    def validate(self, config: Dict[str, Any]) -> None:
        errors: List[Dict[str, Any]] = []

        # 1. Bounded Payload & Complexity Checks
        raw_json = json.dumps(config)
        if len(raw_json.encode("utf-8")) > MAX_DOCUMENT_BYTES:
            raise CustomizationValidationError([{
                "path": "$",
                "code": "PAYLOAD_TOO_LARGE",
                "message": f"Customization payload exceeds maximum size of {MAX_DOCUMENT_BYTES} bytes."
            }])

        if get_json_depth(config) > MAX_JSON_DEPTH:
            raise CustomizationValidationError([{
                "path": "$",
                "code": "EXCESSIVE_NESTING",
                "message": f"JSON nesting depth exceeds maximum limit of {MAX_JSON_DEPTH}."
            }])

        # 2. Dangerous executable code scans (XSS, script, inline handlers)
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(raw_json):
                raise CustomizationValidationError([{
                    "path": "$",
                    "code": "EXECUTABLE_CONTENT_PROHIBITED",
                    "message": "Customization payload contains prohibited executable code or script expressions."
                }])

        # 3. Structural JSON Schema validation
        schema_errors = list(self._doc_validator.iter_errors(config))
        if schema_errors:
            for err in schema_errors:
                path = ".".join(str(p) for p in err.absolute_path) or "$"
                errors.append({
                    "path": path,
                    "code": "SCHEMA_VIOLATION",
                    "message": err.message
                })
            raise CustomizationValidationError(errors)

        # 4. Component Count Limit
        components = config.get("components", [])
        if len(components) > MAX_COMPONENTS:
            errors.append({
                "path": "components",
                "code": "MAX_COMPONENTS_EXCEEDED",
                "message": f"Component count ({len(components)}) exceeds maximum allowed ({MAX_COMPONENTS})."
            })

        # 5. Semantic Validation — Theme Registry
        theme_sel = config.get("theme", {})
        theme_id = theme_sel.get("id")
        theme_ver = theme_sel.get("version")
        theme_def = theme_registry.get(theme_id, theme_ver)
        if not theme_def:
            errors.append({
                "path": "theme.id",
                "code": "UNKNOWN_THEME",
                "message": f"Theme '{theme_id}' (version '{theme_ver}') is not registered in platform catalogue."
            })
        elif theme_def.get("status") == "retired":
            errors.append({
                "path": "theme.id",
                "code": "THEME_RETIRED",
                "message": f"Theme '{theme_id}' has been retired and cannot be newly selected."
            })

        # 6. Semantic Validation — Layout Registry
        layout_sel = config.get("layout", {})
        layout_id = layout_sel.get("id")
        layout_ver = layout_sel.get("version")
        layout_def = layout_registry.get(layout_id, layout_ver)
        if not layout_def:
            errors.append({
                "path": "layout.id",
                "code": "UNKNOWN_LAYOUT",
                "message": f"Layout '{layout_id}' is not registered in platform catalogue."
            })
        else:
            # Check theme/layout compatibility if theme exists
            if theme_def and layout_id not in theme_def.get("supported_layouts", []):
                errors.append({
                    "path": "layout.id",
                    "code": "INCOMPATIBLE_THEME_LAYOUT",
                    "message": f"Layout '{layout_id}' is not supported by theme '{theme_id}'."
                })

            # Check responsive columns
            resp = layout_sel.get("responsive", {})
            for vp in ("mobile", "tablet", "desktop"):
                if vp in resp:
                    cols = resp[vp].get("columns")
                    if cols is not None and (cols < 1 or cols > 4):
                        errors.append({
                            "path": f"layout.responsive.{vp}.columns",
                            "code": "INVALID_COLUMN_COUNT",
                            "message": f"Column count '{cols}' for viewport '{vp}' is outside allowed range (1-4)."
                        })

        # 7. Semantic Validation — Component Registry & Slots
        seen_instances = set()
        for idx, comp in enumerate(components):
            inst_id = comp.get("instance_id")
            if inst_id in seen_instances:
                errors.append({
                    "path": f"components.{idx}.instance_id",
                    "code": "DUPLICATE_INSTANCE_ID",
                    "message": f"Duplicate component instance ID '{inst_id}'."
                })
            seen_instances.add(inst_id)

            comp_id = comp.get("component_id")
            comp_ver = comp.get("component_version")
            comp_def = component_registry.get(comp_id, comp_ver)
            if not comp_def:
                errors.append({
                    "path": f"components.{idx}.component_id",
                    "code": "UNKNOWN_COMPONENT",
                    "message": f"Component '{comp_id}' is not registered in platform catalogue."
                })
                continue

            if comp_def.get("status") == "retired":
                errors.append({
                    "path": f"components.{idx}.component_id",
                    "code": "COMPONENT_RETIRED",
                    "message": f"Component '{comp_id}' is retired and cannot be newly selected."
                })

            slot = comp.get("slot")
            if slot not in comp_def.get("supported_slots", []):
                errors.append({
                    "path": f"components.{idx}.slot",
                    "code": "UNSUPPORTED_COMPONENT_SLOT",
                    "message": f"Component '{comp_id}' does not support slot '{slot}'."
                })

            if layout_def and comp_id not in layout_def.get("allowed_components", []):
                errors.append({
                    "path": f"components.{idx}.component_id",
                    "code": "COMPONENT_NOT_ALLOWED_BY_LAYOUT",
                    "message": f"Component '{comp_id}' is not permitted by layout '{layout_id}'."
                })

            # Validate component props against props_schema
            props = comp.get("props", {})
            props_schema = comp_def.get("props_schema", {})
            for prop_key, prop_val in props.items():
                if prop_key not in props_schema:
                    errors.append({
                        "path": f"components.{idx}.props.{prop_key}",
                        "code": "UNKNOWN_PROPERTY",
                        "message": f"Property '{prop_key}' is not allowed on component '{comp_id}'."
                    })
                else:
                    # Check enum restriction
                    spec = props_schema[prop_key]
                    if "enum" in spec and prop_val not in spec["enum"]:
                        errors.append({
                            "path": f"components.{idx}.props.{prop_key}",
                            "code": "UNSUPPORTED_VALUE",
                            "message": f"Value '{prop_val}' for property '{prop_key}' is not in allowed choices: {spec['enum']}."
                        })

        if errors:
            raise CustomizationValidationError(errors)


validator = CustomizationValidator()
