"""Base check interface."""

from __future__ import annotations

from ..models import Finding, Project


class Check:
  """Base class for checks."""

  name: str = ""
  languages: list[str] = ["*"]   # which project languages this applies to

  def run(self, project: Project) -> list[Finding]:
    raise NotImplementedError