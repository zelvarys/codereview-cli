"""Parse package.json (dependencies + devDependencies)."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Dependency
from .requirements import normalize


class PackageJsonParser:
    filename = "package.json"

    def parse(self, path: Path) -> list[Dependency]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        source = str(path)
        deps: list[Dependency] = []

        for section, kind in (
            ("dependencies", "runtime"),
            ("devDependencies", "dev"),
        ):
            for name, constraint in (data.get(section) or {}).items():
                deps.append(
                    Dependency(
                        name=normalize(name),
                        raw=f"{name}@{constraint}",
                        constraint=str(constraint),
                        source=source,
                        line=0,
                        kind=kind,
                    )
                )
        return deps