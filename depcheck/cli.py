"""depcheck CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .checks.base import Check
from .checks.duplicate import DuplicateCheck
from .checks.missing import MissingCheck
from .checks.stdlib_shadow import StdlibShadowCheck
from .checks.unpinned import UnpinnedCheck
from .checks.unused import UnusedCheck
from .models import Project
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

DEP_FILENAMES = {"requirements.txt", "pyproject.toml", "package.json"}

ALL_CHECKS: list[Check] = [
    UnpinnedCheck(),
    UnusedCheck(),
    MissingCheck(),
    StdlibShadowCheck(),
    DuplicateCheck(),
]


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


def _scan_imports(root: Path) -> tuple[set[str], set[str]]:
    py = PyImportsScanner().scan(root)
    js = JsImportsScanner().scan(root)
    return py, js


def run(path: str, as_json: bool, color: bool) -> int:
    root = Path(path).resolve()
    if not root.exists():
        print(f"error: path not found: {path}", file=sys.stderr)
        return 2

    files_scanned = sum(1 for _ in _iter_candidate_files(root))
    deps = _parse_deps(root)
    py_imports, js_imports = _scan_imports(root)

    languages: set[str] = set()
    if py_imports or any(d.source.endswith(".txt") or d.source.endswith(".toml")
                         for d in deps):
        languages.add("python")
    if js_imports or any(d.source.endswith("package.json") for d in deps):
        languages.add("javascript")

    project = Project(
        root=str(root),
        dependencies=deps,
        imported=py_imports | js_imports,
        languages=languages,
    )

    findings = []
    for check in ALL_CHECKS:
        if "*" in check.languages or (set(check.languages) & languages):
            try:
                findings.extend(check.run(project))
            except Exception as e:  # noqa: BLE001
                print(f"warning: check {check.name} failed: {e}", file=sys.stderr)

    if as_json:
        print(json_report(findings))
    else:
        print(human_report(findings, files_scanned, len(deps), color=color))

    return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="depcheck", description="Audit dependencies.")
    p.add_argument("--version", action="version", version=f"depcheck {__version__}")
    p.add_argument("path", nargs="?", default=".", help="Project directory")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args(argv)

    return run(args.path, as_json=args.json, color=not args.no_color)


if __name__ == "__main__":
    raise SystemExit(main())