"""
ModularMenu — OpenAPI Specification Exporter (ARC-07 §18.2, §25.1).
Generates canonical openapi.json and openapi.yaml artifacts.
"""
import json
import os
import sys
from pathlib import Path
import yaml

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

OUTPUT_DIR = backend_dir / "openapi"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_openapi() -> None:
    openapi_schema = app.openapi()

    json_path = OUTPUT_DIR / "openapi.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported: {json_path}")

    yaml_path = OUTPUT_DIR / "openapi.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, sort_keys=False, allow_unicode=True)
    print(f"Exported: {yaml_path}")


if __name__ == "__main__":
    export_openapi()
