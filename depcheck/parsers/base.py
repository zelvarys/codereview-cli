"""Base parser interface."""

from __future__ import annotations

from pathlib import Path

from ..models import Dependency


class Parser:
  """Base class for dependency-file parsers."""

  #: filename this parser handles (matched case-sensitively)
  filename: str = ""

  def parse(self, path: Path) -> list[Dependency]:
    """Parse `path` and return a list of dependencies."""
    raise NotImplementedError