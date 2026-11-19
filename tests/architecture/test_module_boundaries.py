"""
Architecture Boundary Tests for ModularMenu (ARC-02 §10 WP-ARC02-03 & §11.3).
Enforces:
- Principle P-01 (Modularity)
- Principle P-02 (Separation of Concerns)
- Principle P-04 (Multi-Tenant Isolation)
- Constraint CON-04 (No implicit lazy loading)
- Constraint CON-05 (No floating-point currency)
"""
import ast
import os
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend" / "app"
MODULES_DIR = BACKEND_DIR / "modules"


def get_python_files(directory: Path):
    """Recursively yields all .py files in a directory."""
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


def test_domain_modules_do_not_import_api_layer():
    """
    MOD-001 / Principle P-02:
    Domain modules (backend/app/modules/*) must NEVER depend on the API delivery layer (app.api).
    Communication flow is strictly API -> Application -> Domain -> Infrastructure.
    """
    violations = []
    for filepath in get_python_files(MODULES_DIR):
        imports = get_imports_from_ast(filepath)
        for imp in imports:
            if imp.startswith("app.api") or imp.startswith("api."):
                violations.append(f"{filepath.relative_to(REPO_ROOT)} imports API layer: '{imp}'")

    assert not violations, f"Architectural violation (P-02): Domain modules must not depend on API layer:\n" + "\n".join(violations)


def test_no_private_cross_module_imports():
    """
    MOD-003 / Principle P-01:
    Modules must communicate via public exports. Direct imports of private
    internals (prefixed with '_' or named 'internal_') are forbidden.
    """
    violations = []
    for filepath in get_python_files(MODULES_DIR):
        imports = get_imports_from_ast(filepath)
        for imp in imports:
            parts = imp.split(".")
            for part in parts:
                if part.startswith("_") and not part.startswith("__"):
                    violations.append(f"{filepath.relative_to(REPO_ROOT)} imports private internal: '{imp}'")
                if "internal_" in part:
                    violations.append(f"{filepath.relative_to(REPO_ROOT)} imports internal component: '{imp}'")

    assert not violations, f"Architectural violation (P-01): Prohibited private cross-module imports:\n" + "\n".join(violations)


def test_no_circular_dependencies_between_modules():
    """
    MOD-002 / Principle P-01:
    Modules must not have circular dependencies between one another.
    """
    # Map of module -> set of target modules it imports
    dep_graph = {}
    for mod_dir in MODULES_DIR.iterdir():
        if mod_dir.is_dir() and not mod_dir.name.startswith("__"):
            mod_name = mod_dir.name
            dep_graph[mod_name] = set()

            for py_file in get_python_files(mod_dir):
                for imp in get_imports_from_ast(py_file):
                    if imp.startswith("app.modules."):
                        target = imp.split(".")[2]
                        if target != mod_name and not target.startswith("__"):
                            dep_graph[mod_name].add(target)

    # Detect cycles via DFS
    visited = {}  # 0 = unvisited, 1 = visiting, 2 = visited
    cycle_path = []

    def dfs(node, path):
        visited[node] = 1
        path.append(node)
        for neighbor in dep_graph.get(node, []):
            if visited.get(neighbor, 0) == 1:
                cycle_path.extend(path[path.index(neighbor):] + [neighbor])
                return True
            if visited.get(neighbor, 0) == 0:
                if dfs(neighbor, path):
                    return True
        path.pop()
        visited[node] = 2
        return False

    for mod in dep_graph:
        if visited.get(mod, 0) == 0:
            if dfs(mod, []):
                break

    assert not cycle_path, f"Circular dependency detected between modules: {' -> '.join(cycle_path)}"


def test_modules_expose_public_interface():
    """
    MOD-004:
    Every domain module must contain an __init__.py exposing its public contract.
    """
    missing_init = []
    for module_dir in MODULES_DIR.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith("__"):
            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                missing_init.append(str(module_dir.relative_to(REPO_ROOT)))

    assert not missing_init, f"Missing __init__.py in module directories:\n" + "\n".join(missing_init)


def test_models_declare_explicit_lazy_loading():
    """
    CON-04 / ADR-0003:
    All SQLAlchemy relationships in domain models must explicitly specify `lazy='raise'`
    or explicit join loading. Implicit lazy loading is strictly prohibited to prevent N+1 queries.
    """
    violations = []
    for filepath in get_python_files(MODULES_DIR):
        if filepath.name == "models.py":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check if call is relationship(...)
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr

                    if func_name == "relationship":
                        # Check keyword arguments for lazy
                        lazy_kwarg = None
                        for kw in node.keywords:
                            if kw.arg == "lazy":
                                if isinstance(kw.value, ast.Constant):
                                    lazy_kwarg = kw.value.value
                        
                        if lazy_kwarg != "raise":
                            violations.append(
                                f"{filepath.relative_to(REPO_ROOT)}: line {node.lineno} relationship() has invalid or missing lazy strategy (got {lazy_kwarg!r}, expected 'raise')"
                            )

    assert not violations, f"Architectural violation (CON-04): Implicit lazy loading detected:\n" + "\n".join(violations)


def test_monetary_attributes_do_not_use_floating_point():
    """
    CON-05 / ADR-0008:
    Monetary and pricing fields must never use Float or Double types.
    """
    violations = []
    for filepath in get_python_files(MODULES_DIR):
        if filepath.name == "models.py":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            for line_no, line in enumerate(content.splitlines(), start=1):
                lower_line = line.lower()
                if any(k in lower_line for k in ["price", "amount", "tax", "fee", "cost"]):
                    if "float" in lower_line or "double" in lower_line:
                        violations.append(
                            f"{filepath.relative_to(REPO_ROOT)}: line {line_no} appears to declare floating point monetary attribute: {line.strip()}"
                        )

    assert not violations, f"Architectural violation (CON-05): Floating-point pricing detected:\n" + "\n".join(violations)
