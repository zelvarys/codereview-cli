"""Parse pyproject.toml (PEP 621 dependencies only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomllib

from ..models import Dependency
from .requirements import normalize, _strip_comment


def _parse_spec(spec: str, source: str, line: int, kind: str) -> Dependency | None:
  spec = spec.strip()
  if not spec:
    return None
  if ";" in spec:
    spec = spec.split(";", 1)[0].strip()
  spec = _strip_comment(spec).strip()
  if not spec:
    return None

  name_chars = []
  for ch in spec:
    if ch in "[<>=!~; ":
      break
    name_chars.append(ch)
  name = "".join(name_chars).strip()
  if not name:
    return None

  rest = spec[len(name):].strip()
  if rest.startswith("["):
    end = rest.find("]")
    if end != -1:
      rest = rest[end + 1:].strip()

  return Dependency(
    name=normalize(name),
    raw=spec,
    constraint=rest,
    source=source,
    line=line,
    kind=kind,
  )


class PyprojectParser:
  filename = "pyproject.toml"

  def parse(self, path: Path) -> list[Dependency]:
    try:
      data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
      return []

    project = data.get("project") or {}
    deps: list[Dependency] = []
    source = str(path)

    for spec in project.get("dependencies", []) or []:
      d = _parse_spec(spec, source, 0, "runtime")
      if d:
        deps.append(d)

    for _group, specs in (project.get("optional-dependencies") or {}).items():
      for spec in specs or []:
        d = _parse_spec(spec, source, 0, "dev")
        if d:
          deps.append(d)

    return deps