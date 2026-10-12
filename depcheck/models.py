"""Core data types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Dependency:
  """A single declared dependency."""

  name: str          # normalized lowercase name
  raw: str           # original string as written
  constraint: str        # e.g. "==1.2.3", ">=1.0,<2.0", "" if unpinned
  source: str          # filename it came from
  line: int          # line number in that file
  kind: str = "runtime"    # "runtime" | "dev"


@dataclass
class Project:
  """A scanned project."""

  root: str
  dependencies: list[Dependency] = field(default_factory=list)
  imported: set[str] = field(default_factory=set)   # normalized module names
  languages: set[str] = field(default_factory=set)   # "python" | "javascript"


@dataclass(frozen=True)
class Finding:
  """A problem found by a check."""

  check: str
  severity: str        # "error" | "warning" | "info"
  message: str
  source: str = ""
  line: int = 0