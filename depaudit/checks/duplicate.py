"""Flag dependencies declared more than once."""

from __future__ import annotations

from collections import defaultdict

from ..models import Finding, Project
from .base import Check


class DuplicateCheck(Check):
  name = "duplicate"

  def run(self, project: Project) -> list[Finding]:
    by_name: dict[str, list] = defaultdict(list)
    for dep in project.dependencies:
      by_name[dep.name].append(dep)

    findings: list[Finding] = []
    for name, deps in by_name.items():
      if len(deps) < 2:
        continue
      constraints = {d.constraint for d in deps}
      if len(constraints) > 1:
        where = ", ".join(f"{d.source}:{d.line}" for d in deps if d.line)
        findings.append(
          Finding(
            check=self.name,
            severity="warning",
            message=(
              f"`{name}` declared {len(deps)}x with different "
              f"constraints ({where or 'multiple files'})"
            ),
            source=deps[0].source,
            line=deps[0].line,
          )
        )
    return findings