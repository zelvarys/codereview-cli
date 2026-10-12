"""Flag dependencies that are a major version behind the latest release."""

from __future__ import annotations

import re

from ..models import Finding, Project
from .base import Check


def _extract_pinned(constraint: str) -> str | None:
  """Return the version this constraint pins to, if any.

  Handles: ==1.2.3, ===1.2.3, 1.2.3 (bare), ^1.2.3, ~1.2.3 (npm).
  Returns None for ranges like >=1.0 or empty.
  """
  c = constraint.strip()
  if not c:
    return None
  m = re.match(r"^===?\s*v?([0-9][^\s,;]*)", c)
  if m:
    return m.group(1)
  m = re.match(r"^[\^~]?\s*v?([0-9][^\s,;]*)", c)
  if m:
    return m.group(1)
  return None


def _major(v: str) -> int | None:
  """Return the major version number, or None if unparseable."""
  v = v.strip().lstrip("v")
  m = re.match(r"^(\d+)", v)
  return int(m.group(1)) if m else None


class OutdatedCheck(Check):
  name = "outdated"

  def __init__(self, latest_lookup):
    """latest_lookup(dep) -> latest version string or None."""
    self.latest_lookup = latest_lookup

  def run(self, project: Project) -> list[Finding]:
    findings: list[Finding] = []
    for dep in project.dependencies:
      pinned = _extract_pinned(dep.constraint)
      if pinned is None:
        continue
      latest = self.latest_lookup(dep)
      if not latest:
        continue
      cur_major = _major(pinned)
      new_major = _major(latest)
      if cur_major is None or new_major is None:
        continue
      if new_major <= cur_major:
        continue
      behind = new_major - cur_major
      label = "1 major" if behind == 1 else f"{behind} majors"
      findings.append(
        Finding(
          check=self.name,
          severity="warning",
          message=(
            f"`{dep.name}` is on {cur_major}.x "
            f"(latest is {new_major}.x, {label} behind)"
          ),
          source=dep.source,
          line=dep.line,
        )
      )
    return findings