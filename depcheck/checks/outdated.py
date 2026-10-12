"""Flag dependencies that are behind the latest release."""

from __future__ import annotations

import re

from ..models import Finding, Project
from .base import Check


def _extract_pinned(constraint: str) -> str | None:
    """Return the version this constraint pins to, if any.

    Handles: ==1.2.3, ===1.2.3, 1.2.3 (bare), >=1.0 (returns None — not a pin)
    """
    c = constraint.strip()
    if not c:
        return None
    m = re.match(r"^===?\s*([0-9][^\s,;]*)", c)
    if m:
        return m.group(1)
    # bare version like "1.2.3" or "^1.2.3" (npm)
    m = re.match(r"^[\^~]?\s*v?([0-9][^\s,;]*)", c)
    if m:
        return m.group(1)
    return None


def _version_tuple(v: str) -> tuple[int, ...] | None:
    """Parse '1.2.3' or '1.2.3rc1' into a comparable tuple. Best-effort."""
    v = v.strip().lstrip("v")
    parts = re.split(r"[.\-+]", v)
    out = []
    for p in parts:
        m = re.match(r"^(\d+)", p)
        if not m:
            break
        out.append(int(m.group(1)))
    return tuple(out) if out else None


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
            cur = _version_tuple(pinned)
            new = _version_tuple(latest)
            if not cur or not new:
                continue
            if new > cur:
                findings.append(
                    Finding(
                        check=self.name,
                        severity="info",
                        message=(
                            f"`{dep.name}` is {pinned}, latest is {latest}"
                        ),
                        source=dep.source,
                        line=dep.line,
                    )
                )
        return findings