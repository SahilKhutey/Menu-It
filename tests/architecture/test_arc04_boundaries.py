"""
ARC-04 Module Boundary and Architecture Enforcement Tests (ARC-04 §14.2 & §14.4).
Verifies:
- ARC04-T046: Prohibited cross-module imports fail boundary analysis
- ARC04-T047: Direct cross-module internal writes are forbidden
- Enforces YAML dependency matrix in backend/architecture/module_dependencies.yaml
"""
import ast
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend" / "app"
MODULES_DIR = BACKEND_DIR / "modules"
CONFIG_PATH = REPO_ROOT / "backend" / "architecture" / "module_dependencies.yaml"


def load_dependency_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_imports_from_file(filepath: Path):
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


def test_arc04_t046_prohibited_cross_module_imports():
    """
    ARC04-T046:
    Enforces that modules do not import forbidden modules as defined in module_dependencies.yaml.
    """
    config = load_dependency_config()
    modules_cfg = config.get("modules", {})
    violations = []

    for mod_key, mod_info in modules_cfg.items():
        mod_name = mod_info["name"]
        prohibited = set(mod_info.get("prohibited", []))
        mod_dir = MODULES_DIR / mod_name
        if not mod_dir.exists():
            continue

        for py_file in mod_dir.rglob("*.py"):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("app.modules."):
                    target_mod = imp.split(".")[2]
                    if target_mod in prohibited:
                        violations.append(
                            f"Module '{mod_name}' ({py_file.name}) illegally imports prohibited module '{target_mod}' ({imp})"
                        )

    assert not violations, "Prohibited cross-module import violations found:\n" + "\n".join(violations)


def test_arc04_t047_no_direct_cross_module_orm_access():
    """
    ARC04-T047:
    Modules must not import internal ORM models from another module.
    Cross-module communication must use public protocols/contracts or entities.
    """
    violations = []
    for mod_dir in MODULES_DIR.iterdir():
        if not mod_dir.is_dir() or mod_dir.name.startswith("__"):
            continue
        mod_name = mod_dir.name
        for py_file in mod_dir.rglob("*.py"):
            if py_file.name == "models.py":
                continue  # self models
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("app.modules.") and ".models" in imp:
                    target_mod = imp.split(".")[2]
                    if target_mod != mod_name:
                        violations.append(
                            f"Module '{mod_name}' ({py_file.name}) directly accesses external ORM models '{imp}'"
                        )

    assert not violations, "Direct cross-module ORM access violations found:\n" + "\n".join(violations)


def test_arc04_all_16_module_manifests_exist_and_validate():
    """
    WP-ARC04-02:
    Validates that all 16 modules have a valid module.yaml manifest.
    """
    expected_modules = [
        "identity", "organizations", "restaurants", "menus",
        "categories", "food_items", "pricing", "themes",
        "layouts", "components", "rendering", "editor",
        "publishing", "media", "licensing", "analytics"
    ]
    for mod in expected_modules:
        manifest_path = MODULES_DIR / mod / "module.yaml"
        assert manifest_path.exists(), f"Module manifest missing: {manifest_path}"
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            assert "module" in data
            assert "id" in data["module"]
            assert "name" in data["module"]
            assert "status" in data["module"]
            assert "ownership" in data["module"]
            assert "contracts" in data["module"]
            assert "dependencies" in data["module"]
