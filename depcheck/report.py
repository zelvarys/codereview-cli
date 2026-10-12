"""Output formatting: human and JSON."""

from __future__ import annotations

import json
from collections import defaultdict

from .models import Finding

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"

SEVERITY_COLOR = {"error": RED, "warning": YELLOW, "info": CYAN}
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _c(text: str, code: str, color: bool) -> str:
  return f"{code}{text}{RESET}" if color else text


def human_report(
  findings: list[Finding],
  files_scanned: int,
  deps_count: int,
  color: bool = True,
) -> str:
  if not findings:
    return (
      f"Scanned {files_scanned} file(s), {deps_count} dependency(ies).\n"
      "No issues found."
    )

  findings = sorted(
    findings,
    key=lambda f: (f.source, f.line, SEVERITY_ORDER.get(f.severity, 9)),
  )

  by_source: dict[str, list[Finding]] = defaultdict(list)
  for f in findings:
    by_source[f.source or "<project>"].append(f)

  lines: list[str] = []
  for source, group in sorted(by_source.items()):
    lines.append(_c(source, BOLD, color))
    for f in group:
      sev = _c(f.severity.ljust(7), SEVERITY_COLOR[f.severity], color)
      loc = f":{f.line}" if f.line else ""
      lines.append(f"  {sev}  {f.check}{loc} — {f.message}")
    lines.append("")

  lines.append(f"Scanned {files_scanned} file(s), {deps_count} dependency(ies).")
  lines.append(f"Found {len(findings)} issue(s).")
  return "\n".join(lines)


def json_report(findings: list[Finding]) -> str:
  return json.dumps(
    [
      {
        "check": f.check,
        "severity": f.severity,
        "message": f.message,
        "source": f.source,
        "line": f.line,
      }
      for f in findings
    ],
    indent=2,
  )