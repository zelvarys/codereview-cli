"""Scan Python files for imports (top-level names only)."""

from __future__ import annotations

import ast
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "target", "vendor",
    ".tox", ".eggs",
}


def _normalize(name: str) -> str:
    return name.split(".", 1)[0].replace("_", "-").lower()


class PyImportsScanner:
    language = "python"

    def scan(self, root: Path) -> set[str]:
        imported: set[str] = set()
        for path in root.rglob("*.py"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(_normalize(alias.name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        imported.add(_normalize(node.module))
        return imported