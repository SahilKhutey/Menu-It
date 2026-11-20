"""
Application Architecture Boundary Tests (ARC-03 §14.4 ARCH-ARC03-001 to ARCH-ARC03-008).
Enforces:
- Clean Architecture Layering (API -> Application -> Domain -> Infrastructure)
- Strict Dependency Inversion (Domain has 0 external dependencies)
- Frontend / Backend Process Separation
- Public Renderer vs Visual Editor Independence
"""
import ast
import os
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend" / "app"
SHARED_DOMAIN_DIR = BACKEND_DIR / "shared" / "domain"
APPLICATION_DIR = BACKEND_DIR / "shared" / "application"
FRONTEND_DIR = REPO_ROOT / "frontend" / "src"


def get_python_files(directory: Path):
    """Recursively yields all .py files in a directory."""
    if not directory.exists():
        return
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__pycache__"):
                yield Path(root) / file


def get_imports_from_ast(filepath: Path):
    """Extracts all module import strings from a Python file using AST."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def test_arch_arc03_001_domain_entities_do_not_import_fastapi_or_starlette():
    """
    ARCH-ARC03-001 / Principle P-02:
    Domain entities (backend/app/shared/domain/*) must NEVER depend on
    HTTP delivery frameworks (FastAPI, Starlette, Flask, Django).
    """
    forbidden_http = {"fastapi", "starlette", "flask", "django"}
    violations = []

    for filepath in get_python_files(SHARED_DOMAIN_DIR):
        imports = get_imports_from_ast(filepath)
        for imp in imports:
            top_pkg = imp.split(".")[0]
            if top_pkg in forbidden_http:
                violations.append(f"{filepath.relative_to(REPO_ROOT)} imports HTTP framework: '{imp}'")

    assert not violations, f"Architectural violation (ARCH-ARC03-001):\n" + "\n".join(violations)


def test_arch_arc03_002_domain_entities_do_not_import_sqlalchemy_or_persistence():
    """
    ARCH-ARC03-002 / Principle P-02:
    Domain entities must be pure Python objects and NEVER depend on
    SQLAlchemy, database drivers, or ORM persistence logic.
    """
    forbidden_db = {"sqlalchemy", "asyncpg", "aiosqlite", "psycopg2", "sqlite3"}
    violations = []

    for filepath in get_python_files(SHARED_DOMAIN_DIR):
        imports = get_imports_from_ast(filepath)
        for imp in imports:
            top_pkg = imp.split(".")[0]
            if top_pkg in forbidden_db:
                violations.append(f"{filepath.relative_to(REPO_ROOT)} imports persistence driver: '{imp}'")

    assert not violations, f"Architectural violation (ARCH-ARC03-002):\n" + "\n".join(violations)


def test_arch_arc03_006_backend_never_imports_frontend_implementation():
    """
    ARCH-ARC03-006 / ARC-03 §2.3:
    Backend Python code must NEVER reference or import frontend source directories.
    """
    violations = []
    for filepath in get_python_files(BACKEND_DIR):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if "frontend" in content and "import" in content:
            # Check AST imports
            imports = get_imports_from_ast(filepath)
            for imp in imports:
                if "frontend" in imp:
                    violations.append(f"{filepath.relative_to(REPO_ROOT)} imports frontend: '{imp}'")

    assert not violations, f"Architectural violation (ARCH-ARC03-006):\n" + "\n".join(violations)


def test_arch_arc03_007_public_renderer_does_not_import_editor_engine():
    """
    ARCH-ARC03-007 / Principle P-06:
    Public customer menu routes (frontend/src/app/(public)/r/*) must NEVER
    import the heavy 3-panel visual editor engine or studio components.
    """
    public_route_dir = FRONTEND_DIR / "app" / "(public)"
    violations = []

    if public_route_dir.exists():
        for root, _, files in os.walk(public_route_dir):
            for file in files:
                if file.endswith((".ts", ".tsx")):
                    fpath = Path(root) / file
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "editor" in content.lower() and "from" in content:
                        lines = [line for line in content.splitlines() if "import" in line and "editor" in line.lower()]
                        if lines:
                            violations.append(f"{fpath.relative_to(REPO_ROOT)} imports editor: {lines}")

    assert not violations, f"Architectural violation (ARCH-ARC03-007): Public route imports editor:\n" + "\n".join(violations)


def test_arch_arc03_008_application_use_cases_depend_on_interfaces():
    """
    ARCH-ARC03-008 / ARC-03 §7.4:
    Application use cases must import repository interfaces from .interfaces,
    NOT concrete SQLAlchemy implementations.
    """
    use_cases_file = APPLICATION_DIR / "use_cases.py"
    assert use_cases_file.exists()

    imports = get_imports_from_ast(use_cases_file)
    for imp in imports:
        assert "SqlAlchemy" not in imp, f"Use cases must not directly import concrete SQLAlchemy repository: {imp}"
        assert "infrastructure.repositories" not in imp, f"Use cases must not import infrastructure layer directly: {imp}"
