"""Flag dependencies without a version constraint."""

from __future__ import annotations

from ..models import Finding, Project
from .base import Check


class UnpinnedCheck(Check):
  name = "unpinned"

  def run(self, project: Project) -> list[Finding]:
    findings: list[Finding] = []
    for dep in project.dependencies:
      if not dep.constraint:
        findings.append(
          Finding(
            check=self.name,
            severity="warning",
            message=f"`{dep.name}` has no version constraint",
            source=dep.source,
            line=dep.line,
          )
        )
    return findings