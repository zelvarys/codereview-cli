"""Flag imports that aren't declared as dependencies."""

from __future__ import annotations

import sys

from ..models import Finding, Project
from .base import Check

STDLIB = set(getattr(sys, "stdlib_module_names", set()))

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

IGNORE_MISSING = {"tests", "test"}


class MissingCheck(Check):
    name = "missing"

    def run(self, project: Project) -> list[Finding]:
        declared = {d.name for d in project.dependencies}
        findings: list[Finding] = []
        reported: set[tuple[str, str]] = set()

        for imp in project.imports:
            mod = imp.module
            if mod in STDLIB or mod in IGNORE_MISSING or mod.startswith("_"):
                continue
            pkg = IMPORT_TO_PACKAGE.get(mod, mod)
            if pkg in declared or mod in declared:
                continue
            # dedupe: one finding per (module, file)
            key = (mod, imp.source)
            if key in reported:
                continue
            reported.add(key)
            findings.append(
                Finding(
                    check=self.name,
                    severity="error",
                    message=f"`{mod}` is imported but not declared",
                    source=imp.source,
                    line=imp.line,
                )
            )
        return findings