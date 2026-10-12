"""Flag declared dependencies that are never imported."""

from __future__ import annotations

from ..models import Finding, Project
from .base import Check

IGNORE_UNUSED = {
    "pytest", "black", "ruff", "mypy", "flake8", "isort",
    "tox", "coverage", "pre-commit", "setuptools", "wheel",
    "build", "twine", "pip", "virtualenv",
}


class UnusedCheck(Check):
    name = "unused"

    def run(self, project: Project) -> list[Finding]:
        imported = project.imported_modules
        findings: list[Finding] = []
        for dep in project.dependencies:
            if dep.kind == "dev":
                continue
            if dep.name in IGNORE_UNUSED:
                continue
            if dep.name in imported:
                continue
            findings.append(
                Finding(
                    check=self.name,
                    severity="warning",
                    message=f"`{dep.name}` is declared but never imported",
                    source=dep.source,
                    line=dep.line,
                )
            )
        return findings