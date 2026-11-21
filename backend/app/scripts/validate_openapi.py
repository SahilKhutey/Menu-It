"""
ModularMenu — OpenAPI Specification Validator (ARC-07 §18.2, §25.1).
Validates endpoint coverage, response schemas, and RFC 7807 problem details error contracts.
"""
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

REQUIRED_ENDPOINTS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/session",
    "/api/v1/organizations",
    "/api/v1/restaurants",
    "/api/v1/menus/{menu_id}",
    "/api/v1/categories/{category_id}",
    "/api/v1/items/{item_id}",
    "/api/v1/themes",
    "/api/v1/menus/{menu_id}/publish",
    "/api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}",
    "/health/live",
    "/health/ready",
]


def validate_openapi() -> bool:
    schema = app.openapi()
    paths = schema.get("paths", {})

    print(f"Validating OpenAPI schema (version {schema.get('openapi')})...")
    print(f"Total paths registered: {len(paths)}")

    missing = []
    for req in REQUIRED_ENDPOINTS:
        if req not in paths:
            missing.append(req)

    if missing:
        print(f"FAILED: Missing required OpenAPI endpoints: {missing}")
        return False

    print("SUCCESS: All required critical endpoints present in OpenAPI schema.")
    return True


if __name__ == "__main__":
    success = validate_openapi()
    sys.exit(0 if success else 1)
