from pathlib import Path

from depaudit.parsers.pyproject import PyprojectParser


def test_pep621_dependencies(tmp_path: Path):
  (tmp_path / "pyproject.toml").write_text(
    """
[project]
name = "x"
version = "0.1.0"
dependencies = ["requests>=2.0", "click==8.1.7"]

[project.optional-dependencies]
dev = ["pytest>=7"]
"""
  )
  deps = PyprojectParser().parse(tmp_path / "pyproject.toml")
  names = sorted(d.name for d in deps)
  assert names == ["click", "pytest", "requests"]
  kinds = {d.name: d.kind for d in deps}
  assert kinds["pytest"] == "dev"
  assert kinds["requests"] == "runtime"


def test_missing_project_section(tmp_path: Path):
  (tmp_path / "pyproject.toml").write_text("[build-system]\nrequires = []\n")
  assert PyprojectParser().parse(tmp_path / "pyproject.toml") == []