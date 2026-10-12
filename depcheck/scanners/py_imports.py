"""Scan Python files for imports (with location)."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "target", "vendor",
    ".tox", ".eggs",
}

# Special forms that aren't real modules
SKIP_MODULES = {"__future__"}


def _normalize(name: str) -> str:
    return name.split(".", 1)[0].replace("_", "-").lower()


@dataclass(frozen=True)
class Import:
    module: str
    source: str
    line: int


class PyImportsScanner:
    language = "python"

    def scan(self, root: Path) -> list[Import]:
        imports: list[Import] = []
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
                        top = alias.name.split(".", 1)[0]
                        if top in SKIP_MODULES:
                            continue
                        imports.append(
                            Import(_normalize(alias.name), str(path), node.lineno)
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.level != 0 or not node.module:
                        continue
                    top = node.module.split(".", 1)[0]
                    if top in SKIP_MODULES:
                        continue
                    imports.append(
                        Import(_normalize(node.module), str(path), node.lineno)
                    )
        return imports