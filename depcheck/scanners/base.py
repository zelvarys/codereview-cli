"""Base scanner interface."""

from __future__ import annotations

from pathlib import Path


class Scanner:
  """Base class for source-code import scanners."""

  language: str = ""

  def scan(self, root: Path) -> set[str]:
    """Return a set of normalized module/package names imported under root."""
    raise NotImplementedError