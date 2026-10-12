"""Flag dependencies whose names shadow Python stdlib modules."""

from __future__ import annotations

import sys

from ..models import Finding, Project
from .base import Check

STDLIB = set(getattr(sys, "stdlib_module_names", set()))


class StdlibShadowCheck(Check):
  name = "stdlib-shadow"
  languages = ["python"]

  def run(self, project: Project) -> list[Finding]:
    findings: list[Finding] = []
    for dep in project.dependencies:
      # normalize the dep name the way stdlib would
      mod = dep.name.replace("-", "_")
      if mod in STDLIB:
        findings.append(
          Finding(
            check=self.name,
            severity="error",
            message=(
              f"`{dep.name}` shadows a Python stdlib module "
              f"(`{mod}`)"
            ),
            source=dep.source,
            line=dep.line,
          )
        )
    return findings