"""depcheck CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .checks.base import Check
from .checks.duplicate import DuplicateCheck
from .checks.missing import MissingCheck
from .checks.outdated import OutdatedCheck
from .checks.stdlib_shadow import StdlibShadowCheck
from .checks.unpinned import UnpinnedCheck
from .checks.unused import UnusedCheck
from .models import Project
from .online import latest_npm, latest_pypi
from .parsers.package_json import PackageJsonParser
from .parsers.pyproject import PyprojectParser
from .parsers.requirements import RequirementsParser
from .report import human_report, json_report
from .scanners.js_imports import JsImportsScanner
from .scanners.py_imports import PyImportsScanner

SKIP_DIRS = {
  ".git", ".hg", ".svn", "node_modules", "venv", ".venv",
  "__pycache__", "dist", "build", ".pytest_cache",
  ".mypy_cache", ".ruff_cache", "target", "vendor",
  ".tox", ".eggs",
}


def _iter_candidate_files(root: Path):
  for path in root.rglob("*"):
    if not path.is_file():
      continue
    if any(part in SKIP_DIRS for part in path.parts):
      continue
    yield path


def _parse_deps(root: Path) -> list:
  deps = []
  parsers = {
    "requirements.txt": RequirementsParser(),
    "pyproject.toml": PyprojectParser(),
    "package.json": PackageJsonParser(),
  }
  for path in _iter_candidate_files(root):
    if path.name in parsers:
      deps.extend(parsers[path.name].parse(path))
  return deps


def _scan_imports(root: Path) -> tuple[list, list]:
  return PyImportsScanner().scan(root), JsImportsScanner().scan(root)


def _lookup_latest(dep):
  """Dispatch to PyPI or npm based on which file declared the dep."""
  if dep.source.endswith("package.json"):
    return latest_npm(dep.name)
  return latest_pypi(dep.name)


def run(path: str, as_json: bool, online: bool) -> int:
  root = Path(path).resolve()
  if not root.exists():
    print(f"error: path not found: {path}", file=sys.stderr)
    return 2

  files_scanned = sum(1 for _ in _iter_candidate_files(root))
  deps = _parse_deps(root)
  py_imports, js_imports = _scan_imports(root)
  all_imports = py_imports + js_imports

  languages: set[str] = set()
  if py_imports or any(d.source.endswith((".txt", ".toml")) for d in deps):
    languages.add("python")
  if js_imports or any(d.source.endswith("package.json") for d in deps):
    languages.add("javascript")

  project = Project(
    root=str(root),
    dependencies=deps,
    imports=all_imports,
    languages=languages,
  )

  checks: list[Check] = [
    UnpinnedCheck(),
    UnusedCheck(),
    MissingCheck(),
    StdlibShadowCheck(),
    DuplicateCheck(),
  ]
  if online:
    checks.append(OutdatedCheck(_lookup_latest))

  findings = []
  for check in checks:
    if "*" in check.languages or (set(check.languages) & languages):
      try:
        findings.extend(check.run(project))
      except Exception as e:  # noqa: BLE001
        print(f"warning: check {check.name} failed: {e}", file=sys.stderr)

  color = sys.stdout.isatty()
  if as_json:
    print(json_report(findings))
  else:
    print(human_report(findings, files_scanned, len(deps), color=color))

  return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
  p = argparse.ArgumentParser(prog="depcheck", description="Audit dependencies.")
  p.add_argument("-v", "--version", action="version",
           version=f"depcheck {__version__}")
  p.add_argument("path", nargs="?", default=".", help="Project directory")
  p.add_argument("--json", action="store_true", help="JSON output")
  p.add_argument("--online", action="store_true",
           help="Also check for outdated versions (network)")
  args = p.parse_args(argv)

  return run(args.path, as_json=args.json, online=args.online)


if __name__ == "__main__":
  raise SystemExit(main())