"""Scan JS/TS files for imports (with location)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "coverage",
    ".next", ".nuxt", ".cache", "out", "target",
}

EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}

IMPORT_RE = re.compile(
    r"""(?x)
    (?:
        import \s+ (?:[\w*\s{},]+ \s+ from \s+)? ['"]([^'"]+)['"]
      |
        require \s* \( \s* ['"]([^'"]+)['"] \s* \)
      |
        import \s* \( \s* ['"]([^'"]+)['"] \s* \)
    )
    """
)


def _normalize(spec: str) -> str | None:
    if spec.startswith(".") or spec.startswith("/"):
        return None
    if spec.startswith("@"):
        parts = spec.split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}".lower()
        return spec.lower()
    return spec.split("/", 1)[0].lower()


@dataclass(frozen=True)
class Import:
    module: str
    source: str
    line: int


class JsImportsScanner:
    language = "javascript"

    def scan(self, root: Path) -> list[Import]:
        imports: list[Import] = []
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in EXTENSIONS:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in IMPORT_RE.finditer(text):
                spec = m.group(1) or m.group(2) or m.group(3)
                if not spec:
                    continue
                norm = _normalize(spec)
                if not norm:
                    continue
                line = text.count("\n", 0, m.start()) + 1
                imports.append(Import(norm, str(path), line))
        return imports