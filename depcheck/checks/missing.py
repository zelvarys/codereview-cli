"""Flag imports that aren't declared as dependencies."""

from __future__ import annotations

import sys

from ..models import Finding, Project
from .base import Check

# top-level stdlib module names
STDLIB = set(getattr(sys, "stdlib_module_names", set()))

# common import names that map to different package names
IMPORT_TO_PACKAGE = {
  "pil": "pillow",
  "cv2": "opencv-python",
  "sklearn": "scikit-learn",
  "yaml": "pyyaml",
  "bs4": "beautifulsoup4",
  "dotenv": "python-dotenv",
  "jwt": "pyjwt",
  "dateutil": "python-dateutil",
  "serial": "pyserial",
  "git": "gitpython",
  "attr": "attrs",
}

# project-local modules to ignore
IGNORE_MISSING = {"tests", "test"}


class MissingCheck(Check):
  name = "missing"

  def run(self, project: Project) -> list[Finding]:
    declared = {d.name for d in project.dependencies}
    findings: list[Finding] = []

    for mod in sorted(project.imported):
      if mod in STDLIB:
        continue
      if mod in IGNORE_MISSING:
        continue
      if mod.startswith("_"):
        continue
      # try mapping
      pkg = IMPORT_TO_PACKAGE.get(mod, mod)
      if pkg in declared or mod in declared:
        continue
      findings.append(
        Finding(
          check=self.name,
          severity="error",
          message=f"`{mod}` is imported but not declared as a dependency",
        )
      )
    return findings