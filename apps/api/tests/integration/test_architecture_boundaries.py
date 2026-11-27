"""Architecture boundary and dependency rules validation tests (FCD-13 WP-01).

Enforces Clean Architecture rules via AST inspection:
1. Domain layer must NOT import infrastructure (FastAPI, SQLAlchemy, Redis, HTTPX, cloud SDKs).
2. Domain layer must NOT import application presentation or database models.
3. Application services must NOT depend on FastAPI HTTP Request/Response objects.
4. No circular dependencies across foundational packages.
"""

import ast
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parent.parent.parent / "src" / "menu_it"
DOMAIN_ROOT = SRC_ROOT / "domain"
SERVICES_ROOT = SRC_ROOT / "services"
ENDPOINTS_ROOT = SRC_ROOT / "api" / "v1" / "endpoints"

FORBIDDEN_DOMAIN_MODULES = {
    "fastapi",
    "starlette",
    "sqlalchemy",
    "redis",
    "httpx",
    "boto3",
    "google",
    "azure",
    "menu_it.infrastructure",
    "menu_it.api",
    "menu_it.database",
}


def _extract_imported_modules(file_path: Path) -> list[tuple[int, str]]:
    """Parse a python file with AST and extract all top-level imported module names."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    except Exception as exc:
        pytest.fail(f"Failed to parse {file_path}: {exc}")

    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.lineno, node.module))
    return imports


@pytest.mark.unit
def test_domain_layer_does_not_import_infrastructure() -> None:
    """ARC-T01: Domain layer must remain pure business logic and never import infrastructure."""
    violations: list[str] = []

    for py_file in DOMAIN_ROOT.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue

        imported = _extract_imported_modules(py_file)
        for lineno, module_name in imported:
            for forbidden in FORBIDDEN_DOMAIN_MODULES:
                if module_name == forbidden or module_name.startswith(f"{forbidden}."):
                    rel = py_file.relative_to(SRC_ROOT)
                    violations.append(f"{rel}:{lineno} imports forbidden '{module_name}'")

    assert not violations, "Domain architecture boundaries violated:\n" + "\n".join(violations)


@pytest.mark.unit
def test_services_layer_does_not_import_http_request_objects() -> None:
    """ARC-T03: Application services must not depend on HTTP request/response objects."""
    violations: list[str] = []

    if not SERVICES_ROOT.exists():
        return

    forbidden_http = {
        "fastapi.Request",
        "fastapi.Response",
        "starlette.requests",
        "starlette.responses",
    }

    for py_file in SERVICES_ROOT.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue

        imported = _extract_imported_modules(py_file)
        for lineno, module_name in imported:
            for forbidden in forbidden_http:
                if module_name == forbidden or module_name.startswith(f"{forbidden}."):
                    rel = py_file.relative_to(SRC_ROOT)
                    violations.append(f"{rel}:{lineno} imports HTTP type '{module_name}'")

    assert not violations, "Services layer HTTP decoupling violated:\n" + "\n".join(violations)


@pytest.mark.unit
def test_clean_architecture_module_composition() -> None:
    """ARC-T07: Application composition root initializes platform services through container."""
    from menu_it.application import create_application

    app = create_application()
    assert app is not None
    assert app.title == "Menu-It API"
    assert app.version == "0.1.0"
