"""Parse requirements.txt (with -r includes, extras, markers, comments)."""

from __future__ import annotations

import re
from pathlib import Path

from ..models import Dependency
from .base import Parser

# Matches: name[extras]  operator  version  ; marker  # comment
NAME_RE = re.compile(r"^([A-Za-z0-9_.\-]+)")
EXTRAS_RE = re.compile(r"\[([^\]]*)\]")
CONSTRAINT_RE = re.compile(r"([<>=!~]=?|===)\s*([^\s;,#]+)")


def normalize(name: str) -> str:
  """PEP 503 normalized name."""
  return re.sub(r"[-_.]+", "-", name).lower()


def _strip_comment(line: str) -> str:
  # strip unquoted '#' comments
  out = []
  in_quote = False
  for ch in line:
    if ch in "'\"":
      in_quote = not in_quote
    if ch == "#" and not in_quote:
      break
    out.append(ch)
  return "".join(out)


def _parse_line(line: str, source: str, lineno: int, kind: str) -> Dependency | None:
  stripped = line.strip()
  if not stripped:
    return None
  # skip options like --index-url, --extra-index-url, --find-links
  if stripped.startswith("-") and not stripped.startswith("-r"):
    return None

  # remove env marker
  if ";" in stripped:
    stripped = stripped.split(";", 1)[0].strip()

  # remove trailing comment
  stripped = _strip_comment(stripped).strip()
  if not stripped:
    return None

  m = NAME_RE.match(stripped)
  if not m:
    return None
  raw_name = m.group(1)

  # remove extras for matching, but keep for raw
  name = EXTRAS_RE.sub("", raw_name).strip()

  # everything after name and extras is the constraint
  rest = stripped[len(raw_name):].strip()
  rest = EXTRAS_RE.sub("", rest).strip()

  return Dependency(
    name=normalize(name),
    raw=stripped,
    constraint=rest,
    source=source,
    line=lineno,
    kind=kind,
  )


class RequirementsParser(Parser):
  filename = "requirements.txt"

  def parse(self, path: Path) -> list[Dependency]:
    return self._parse_file(path, kind="runtime", seen=None)

  def _parse_file(
    self,
    path: Path,
    kind: str,
    seen: set[Path] | None,
  ) -> list[Dependency]:
    if seen is None:
      seen = set()
    path = path.resolve()
    if path in seen:
      return []
    seen.add(path)

    try:
      text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
      return []

    deps: list[Dependency] = []
    for i, line in enumerate(text.splitlines(), start=1):
      stripped = line.strip()
      if not stripped or stripped.startswith("#"):
        continue

      # handle -r includes
      if stripped.startswith("-r "):
        included = stripped[3:].strip()
        inc_path = (path.parent / included).resolve()
        deps.extend(self._parse_file(inc_path, kind=kind, seen=seen))
        continue

      dep = _parse_line(line, str(path), i, kind)
      if dep:
        deps.append(dep)
    return deps