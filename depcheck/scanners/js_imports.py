"""Scan JS/TS files for imports (regex-based, good enough for v1)."""

from __future__ import annotations

import re
from pathlib import Path

from .base import Scanner

SKIP_DIRS = {
  ".git", "node_modules", "dist", "build", "coverage",
  ".next", ".nuxt", ".cache", "out", "target",
}

EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}

# import X from 'pkg' / import 'pkg' / import('pkg')
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
  # skip relative and absolute paths
  if spec.startswith(".") or spec.startswith("/"):
    return None
  # skip node builtins (bare like "fs")
  # handle scoped packages: @scope/name/subpath -> @scope/name
  if spec.startswith("@"):
    parts = spec.split("/")
    if len(parts) >= 2:
      return f"{parts[0]}/{parts[1]}".lower()
    return spec.lower()
  # unscoped: name/sub -> name
  return spec.split("/", 1)[0].lower()


class JsImportsScanner(Scanner):
  language = "javascript"

  def scan(self, root: Path) -> set[str]:
    imported: set[str] = set()
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
        if norm:
          imported.add(norm)
    return imported